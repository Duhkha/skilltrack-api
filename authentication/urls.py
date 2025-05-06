from django.urls import path
from authentication.sign_up.views import SignUpView
from authentication.sign_in.views import SignInView
from authentication.sign_out.views import SignOutView
from authentication.token.views import CustomTokenRefreshView


urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
]
