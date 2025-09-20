from django.contrib import admin
from .models import Tenant, RuleSet, Claim, RefinedClaim, Metric, JobRun


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")


@admin.register(RuleSet)
class RuleSetAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "name", "version", "is_active", "created_at")
    list_filter = ("tenant", "is_active")


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "claim_id", "status", "error_type", "updated_at")
    list_filter = ("tenant", "status", "error_type")
    search_fields = ("claim_id", "member_id", "facility_id")


@admin.register(RefinedClaim)
class RefinedClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "claim", "is_valid", "score")
    list_filter = ("tenant", "is_valid")


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "as_of")
    list_filter = ("tenant",)


@admin.register(JobRun)
class JobRunAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "job_type", "status", "created_at", "finished_at")
    list_filter = ("tenant", "job_type", "status")
 
