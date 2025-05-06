from rest_framework.routers import DefaultRouter
from permissions.base.views import PermissionsViewSet
from permissions.groups.views import PermissionGroupsViewSet

permission_groups_router = DefaultRouter()
permission_groups_router.register(
    r"", PermissionGroupsViewSet, basename="permission-groups"
)

permissions_router = DefaultRouter()
permissions_router.register(r"", PermissionsViewSet, basename="permissions")

urlpatterns_for_permission_groups = permission_groups_router.urls
urlpatterns_for_permissions = permissions_router.urls
