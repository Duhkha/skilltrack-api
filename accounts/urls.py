from django.urls import path
from rest_framework.routers import DefaultRouter
from accounts.views import (
    SignUpView,
    SignInView,
    CustomTokenRefreshView,
    CurrentUserView,
    SignOutView,
    PermissionGroupListView,
    PermissionListView,
    PermissionListByGroupView,
    PermissionDetailView,
    RoleViewSet,
    UserViewSet,
    ChangePasswordView,
)

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/sign-up/", SignUpView.as_view(), name="sign-up"),
    path("auth/sign-in/", SignInView.as_view(), name="sign-in"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/current-user/", CurrentUserView.as_view(), name="current-user"),
    path("auth/sign-out/", SignOutView.as_view(), name="sign-out"),
    path(
        "permission-groups/",
        PermissionGroupListView.as_view(),
        name="permission-groups",
    ),
    path("permissions/", PermissionListView.as_view(), name="permissions"),
    path(
        "permission-groups/<int:group_id>/permissions/",
        PermissionListByGroupView.as_view(),
        name="permissions-by-group",
    ),
    path(
        "permissions/<int:permission_id>/",
        PermissionDetailView.as_view(),
        name="permission-detail",
    ),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
]

urlpatterns += router.urls
