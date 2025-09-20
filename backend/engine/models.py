from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.code

class RuleSet(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="rule_sets")
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50, default="v1")
    technical_rules = models.JSONField(default=dict)
    medical_rules = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "name", "version")

class Claim(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="claims")
    claim_id = models.CharField(max_length=64)
    encounter_type = models.CharField(max_length=64, null=True, blank=True)
    service_date = models.DateField(null=True, blank=True)
    national_id = models.CharField(max_length=64, null=True, blank=True)
    member_id = models.CharField(max_length=64, null=True, blank=True)
    facility_id = models.CharField(max_length=64, null=True, blank=True)
    unique_id = models.CharField(max_length=64, null=True, blank=True)
    diagnosis_codes = models.JSONField(default=list)
    service_code = models.CharField(max_length=64, null=True, blank=True)
    paid_amount_aed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approval_number = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=32, default="Uploaded")
    error_type = models.CharField(max_length=64, default="No error")
    error_explanation = models.TextField(blank=True, default="")
    recommended_action = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "claim_id"]),
            models.Index(fields=["tenant", "status"]),
        ]

class RefinedClaim(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    claim = models.OneToOneField(Claim, on_delete=models.CASCADE, related_name="refined")
    is_valid = models.BooleanField(default=False)
    tech_errors = models.JSONField(default=list)
    med_errors = models.JSONField(default=list)
    llm_findings = models.JSONField(default=list)
    score = models.FloatField(default=0)

class Metric(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    rule_set = models.ForeignKey(RuleSet, on_delete=models.SET_NULL, null=True)
    as_of = models.DateTimeField(auto_now_add=True)
    counts_by_error = models.JSONField(default=dict)
    paid_by_error = models.JSONField(default=dict)

class JobRun(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    rule_set = models.ForeignKey(RuleSet, on_delete=models.SET_NULL, null=True)
    job_type = models.CharField(max_length=64)
    status = models.CharField(max_length=32, default="Pending")
    detail = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
