from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import CreateUserView

urlpatterns = [
    path("auth/sign-up/", CreateUserView.as_view(), name="sign-up"),
    path("auth/sign-in/", TokenObtainPairView.as_view(), name="sign-in"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
