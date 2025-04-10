from django.urls import path
from accounts.views import (
    SignUpView,
    SignInView,
    CustomTokenRefreshView,
    CurrentUserView,
    SignOutView,
)

urlpatterns = [
    path("auth/sign-up/", SignUpView.as_view(), name="sign-up"),
    path("auth/sign-in/", SignInView.as_view(), name="sign-in"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/current-user/", CurrentUserView.as_view(), name="current-user"),
    path("auth/sign-out/", SignOutView.as_view(), name="sign-out"),
]
