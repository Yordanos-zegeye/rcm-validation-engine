from typing import Dict, Any, List
from django.utils import timezone
from .models import Claim, RefinedClaim, RuleSet, Metric, JobRun
from .rule_engine_static import evaluate_static_rules
from .rule_engine_llm import evaluate_with_llm_async
import asyncio


def _aggregate_metrics(tenant_id: int):
    claims = Claim.objects.filter(tenant_id=tenant_id)
    counts = {"No error": 0, "Technical error": 0, "Medical error": 0, "both": 0}
    paid = {k: 0.0 for k in counts.keys()}
    for c in claims:
        et = c.error_type or "No error"
        paid[et] = paid.get(et, 0.0) + float(c.paid_amount_aed or 0)
        counts[et] = counts.get(et, 0) + 1
    Metric.objects.create(tenant_id=tenant_id, rule_set=None, counts_by_error=counts, paid_by_error=paid)


def run_validation_pipeline(tenant_id: int, rule_set: RuleSet):
    job = JobRun.objects.create(tenant_id=tenant_id, rule_set=rule_set, job_type="validation", status="Running")
    try:
        claims = Claim.objects.filter(tenant_id=tenant_id)
        for claim in claims:
            static_findings = evaluate_static_rules(claim, {
                **(rule_set.technical_rules or {}),
                **(rule_set.medical_rules or {}),
            })
            llm_results: List[Dict[str, Any]] = []
            try:
                llm_results = asyncio.run(evaluate_with_llm_async({
                    "claim_id": claim.claim_id,
                    "diagnosis_codes": claim.diagnosis_codes,
                    "service_code": claim.service_code,
                    "paid_amount_aed": float(claim.paid_amount_aed or 0),
                    "approval_number": claim.approval_number,
                }, {
                    "technical": rule_set.technical_rules,
                    "medical": rule_set.medical_rules,
                }))
            except RuntimeError:
                # If already in event loop (e.g. ASGI), fallback
                llm_results = []

            tech = [f for f in static_findings if (f.get("error_type") or "").lower().startswith("tech")]
            med = [f for f in static_findings if (f.get("error_type") or "").lower().startswith("med")]
            all_findings = static_findings + llm_results

            error_type = "No error"
            if tech and med:
                error_type = "both"
            elif tech:
                error_type = "Technical error"
            elif med:
                error_type = "Medical error"

            explanation_lines = [f"- {f.get('explanation')}" for f in all_findings]
            recommendations = [f"- {f.get('recommendation')}" for f in all_findings if f.get('recommendation')]

            claim.status = "Validated" if not all_findings else "Not validated"
            claim.error_type = error_type
            claim.error_explanation = "\n".join(explanation_lines)
            claim.recommended_action = "\n".join(recommendations)
            claim.save(update_fields=["status", "error_type", "error_explanation", "recommended_action", "updated_at"])

            RefinedClaim.objects.update_or_create(
                claim=claim,
                defaults={
                    "tenant_id": tenant_id,
                    "is_valid": claim.status == "Validated",
                    "tech_errors": tech,
                    "med_errors": med,
                    "llm_findings": llm_results,
                    "score": 1.0 if claim.status == "Validated" else 0.0,
                }
            )
        _aggregate_metrics(tenant_id)
        job.status = "Finished"
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "finished_at"])
    except Exception as exc:
        job.status = "Failed"
        job.detail = {"error": str(exc)}
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "detail", "finished_at"])
        raise
