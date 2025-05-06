from rest_framework.routers import DefaultRouter
from users.base.views import UserViewSet
from users.password.views import UserPasswordViewSet
from users.bulk.ingest.views import UserBulkIngestViewSet

users_router = DefaultRouter()
users_router.register(r"", UserViewSet, basename="users")
users_router.register(r"", UserPasswordViewSet, basename="user-password")
users_router.register(r"bulk/ingest", UserBulkIngestViewSet, basename="bulk-ingest")

urlpatterns = users_router.urls
