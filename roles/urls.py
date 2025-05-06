from rest_framework.routers import DefaultRouter
from roles.base.views import RoleViewSet

roles_router = DefaultRouter()
roles_router.register(r"", RoleViewSet, basename="roles")

urlpatterns = roles_router.urls
