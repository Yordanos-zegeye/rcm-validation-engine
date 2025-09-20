from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import HealthView, ClaimIngestView, ValidateView, ResultsView, RuleSetViewSet, TenantViewSet, AuditView, MeView

router = DefaultRouter()
router.register(r"tenants", TenantViewSet, basename="tenant")
router.register(r"rulesets", RuleSetViewSet, basename="ruleset")

urlpatterns = [
    path("health/", HealthView.as_view()),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view()),
    path("upload/claims/", ClaimIngestView.as_view()),
    path("validate/", ValidateView.as_view()),
    path("results/", ResultsView.as_view()),
    path("audit/", AuditView.as_view()),
    path("", include(router.urls)),
]
