from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="BloomTrack API",
        default_version="v1",
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path('teams/', include('teams.urls')),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"),
]
