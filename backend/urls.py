from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from permissions.urls import (
    urlpatterns_for_permissions,
    urlpatterns_for_permission_groups,
)

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
    path("auth/", include("authentication.urls")),
    path("permissions/", include(urlpatterns_for_permissions)),
    path(
        "permission-groups/",
        include(urlpatterns_for_permission_groups),
    ),
    path("roles/", include("roles.urls")),
    path("users/", include("users.urls")),
    path("teams/", include("teams.urls")),
    path("skills/", include("skills.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"),
    path("swagger.json/", schema_view.without_ui(cache_timeout=0), name="swagger-json"),
]
