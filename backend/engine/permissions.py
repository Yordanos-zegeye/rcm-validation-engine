from rest_framework.permissions import BasePermission

class IsTenantScoped(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            return False
        return str(getattr(obj, "tenant_id", getattr(getattr(obj, "tenant", None), "id", None))) == str(tenant_id)
