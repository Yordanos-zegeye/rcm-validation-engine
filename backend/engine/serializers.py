from rest_framework import serializers
from .models import Claim, Metric, Tenant, RuleSet, RefinedClaim

class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = "__all__"

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ("id", "name", "code")

class RuleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleSet
        fields = "__all__"

class RefinedClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefinedClaim
        fields = "__all__"
