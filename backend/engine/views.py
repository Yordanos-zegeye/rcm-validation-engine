from rest_framework import status, views, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.utils.dateparse import parse_date
import pandas as pd
import json

from .models import Claim, Tenant, RuleSet, Metric, JobRun
from .serializers import ClaimSerializer, MetricSerializer, TenantSerializer, RuleSetSerializer
from .pipeline import run_validation_pipeline
from .utils_rule_parsing import load_rules_from_file


def _tenant_from_request(request):
    tid = request.headers.get("X-Tenant-ID")
    if not tid:
        return None
    try:
        return Tenant.objects.get(id=tid)
    except Tenant.DoesNotExist:
        return None


class HealthView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"})


class MeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": getattr(user, "email", ""),
            "is_staff": getattr(user, "is_staff", False),
            "is_superuser": getattr(user, "is_superuser", False),
        })


class TenantViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class RuleSetViewSet(viewsets.ModelViewSet):
    queryset = RuleSet.objects.all()
    serializer_class = RuleSetSerializer

    def get_queryset(self):
        tenant = _tenant_from_request(self.request)
        if not tenant:
            return RuleSet.objects.none()
        return RuleSet.objects.filter(tenant=tenant)

    @action(detail=False, methods=["post"], url_path="upload")
    def upload_rules(self, request):
        tenant = _tenant_from_request(request)
        if not tenant:
            return Response({"detail": "Missing X-Tenant-ID"}, status=400)
        technical = request.FILES.get("technical")
        medical = request.FILES.get("medical")
        name = request.data.get("name", "default")
        version = request.data.get("version", "v1")
        tech_rules = load_rules_from_file(technical) if technical else {}
        med_rules = load_rules_from_file(medical) if medical else {}
        rs, _ = RuleSet.objects.update_or_create(
            tenant=tenant, name=name, version=version,
            defaults={"technical_rules": tech_rules, "medical_rules": med_rules, "is_active": True}
        )
        return Response(RuleSetSerializer(rs).data)


class ClaimIngestView(views.APIView):
    def post(self, request):
        tenant = _tenant_from_request(request)
        if not tenant:
            return Response({"detail": "Missing X-Tenant-ID"}, status=400)
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "Missing file"}, status=400)
        ext = (file.name.split(".")[-1] or "").lower()
        if ext == "csv":
            df = pd.read_csv(file)
        elif ext in {"xlsx", "xls"}:
            df = pd.read_excel(file)
        else:
            return Response({"detail": "Unsupported format"}, status=400)

        required = [
            "claim_id", "encounter_type", "service_date", "national_id", "member_id",
            "facility_id", "unique_id", "diagnosis_codes", "service_code", "paid_amount_aed",
            "approval_number"
        ]
        for col in required:
            if col not in df.columns:
                return Response({"detail": f"Missing column {col}"}, status=400)

        created = 0
        with transaction.atomic():
            for _, row in df.iterrows():
                # diagnosis_codes can be JSON array, comma string, or single code
                raw_diag = row.get("diagnosis_codes")
                diag_list = []
                if isinstance(raw_diag, str):
                    s = raw_diag.strip()
                    if s.startswith("["):
                        try:
                            diag_list = json.loads(s)
                        except Exception:
                            diag_list = [s]
                    elif "," in s:
                        diag_list = [x.strip() for x in s.split(",") if x.strip()]
                    else:
                        diag_list = [s]
                elif isinstance(raw_diag, (list, tuple)):
                    diag_list = list(raw_diag)
                else:
                    diag_list = [str(raw_diag)] if raw_diag else []

                claim = Claim(
                    tenant=tenant,
                    claim_id=str(row.get("claim_id")),
                    encounter_type=row.get("encounter_type"),
                    service_date=parse_date(str(row.get("service_date"))) if row.get("service_date") else None,
                    national_id=str(row.get("national_id")),
                    member_id=str(row.get("member_id")),
                    facility_id=str(row.get("facility_id")),
                    unique_id=str(row.get("unique_id")),
                    diagnosis_codes=diag_list,
                    service_code=str(row.get("service_code")),
                    paid_amount_aed=row.get("paid_amount_aed") or 0,
                    approval_number=str(row.get("approval_number")),
                )
                claim.save()
                created += 1
        return Response({"ingested": created})


class ValidateView(views.APIView):
    def post(self, request):
        tenant = _tenant_from_request(request)
        if not tenant:
            return Response({"detail": "Missing X-Tenant-ID"}, status=400)
        rule_set = RuleSet.objects.filter(tenant=tenant, is_active=True).order_by("-created_at").first()
        if not rule_set:
            return Response({"detail": "No active rule set"}, status=400)
        run_validation_pipeline(tenant.id, rule_set)
        return Response({"status": "started"})


class ResultsView(views.APIView):
    def get(self, request):
        tenant = _tenant_from_request(request)
        if not tenant:
            return Response({"detail": "Missing X-Tenant-ID"}, status=400)
        claims = Claim.objects.filter(tenant=tenant).order_by("-updated_at")[:1000]
        metrics = Metric.objects.filter(tenant=tenant).order_by("-as_of").first()
        return Response({
            "claims": ClaimSerializer(claims, many=True).data,
            "metrics": MetricSerializer(metrics).data if metrics else None,
        })


class AuditView(views.APIView):
    def get(self, request):
        tenant = _tenant_from_request(request)
        if not tenant:
            return Response({"detail": "Missing X-Tenant-ID"}, status=400)
        jobs = JobRun.objects.filter(tenant=tenant).order_by("-created_at")[:50]
        data = [
            {
                "id": j.id,
                "job_type": j.job_type,
                "status": j.status,
                "detail": j.detail,
                "created_at": j.created_at,
                "finished_at": j.finished_at,
            }
            for j in jobs
        ]
        return Response({"jobs": data})
