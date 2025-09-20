from django.core.management.base import BaseCommand
from django.utils import timezone
from engine.models import Tenant, RuleSet, Claim
from engine.pipeline import run_validation_pipeline

class Command(BaseCommand):
    help = "Seed a demo tenant, rules, and claims, then run validation."

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.get_or_create(code="demo", defaults={"name": "Demo Tenant"})
        self.stdout.write(self.style.SUCCESS(f"Tenant ID: {tenant.id}"))

        tech = {
            "paid_thresholds": [
                {"id": "paid_gt_10000", "field": "paid_amount_aed", "operator": "<=", "value": 10000, "error_type": "Technical error", "message": "Paid amount exceeds threshold", "recommendation": "Verify pricing and approval number."}
            ]
        }
        med = {
            "dx_svc_mapping": [
                {"id": "svc_dx_mismatch", "field": "service_code", "operator": "in", "value": ["99213", "MRI"], "error_type": "Medical error", "message": "Service code not allowed for diagnosis", "recommendation": "Check medical necessity and documented diagnosis."}
            ]
        }
        ruleset, _ = RuleSet.objects.update_or_create(
            tenant=tenant, name="default", version="v1",
            defaults={"technical_rules": tech, "medical_rules": med, "is_active": True}
        )

        sample_claims = [
            dict(claim_id="C1001", paid_amount_aed=12000, service_code="99213", diagnosis_codes=["J20"], member_id="M1"),
            dict(claim_id="C1002", paid_amount_aed=800, service_code="LAB01", diagnosis_codes=["E11"], member_id="M2"),
        ]
        for c in sample_claims:
            Claim.objects.update_or_create(
                tenant=tenant, claim_id=c["claim_id"],
                defaults={
                    "encounter_type": "OP",
                    "service_date": timezone.now().date(),
                    "national_id": "N/A",
                    "member_id": c.get("member_id", ""),
                    "facility_id": "F001",
                    "unique_id": c["claim_id"],
                    "diagnosis_codes": c.get("diagnosis_codes", []),
                    "service_code": c.get("service_code", ""),
                    "paid_amount_aed": c.get("paid_amount_aed", 0),
                    "approval_number": "APPR-001",
                }
            )

        run_validation_pipeline(tenant.id, ruleset)
        self.stdout.write(self.style.SUCCESS("Seeding complete. Run /api/results/ with X-Tenant-ID header."))
