from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from skills.base.views import SkillViewSet
from skills.levels.views import LevelViewSet
from skills.expectations.views import ExpectationViewSet
from skills.user_skills.views import UserSkillViewSet
from skills.expectation_progress.views import UserExpectationProgressViewSet

# Main router for top-level endpoints
main_router = DefaultRouter()
main_router.register(r'skills', SkillViewSet, basename='skill')
main_router.register(r'user-skills', UserSkillViewSet, basename='user-skill')
main_router.register(r'expectation-progress', UserExpectationProgressViewSet, basename='expectation-progress')

#make user skills and expectations seperate

# Nested router for levels within skills
levels_router = NestedDefaultRouter(main_router, r'skills', lookup='skill')
levels_router.register(r'levels', LevelViewSet, basename='skill-level')

# Nested router for expectations within levels
expectations_router = NestedDefaultRouter(levels_router, r'levels', lookup='level')
expectations_router.register(r'expectations', ExpectationViewSet, basename='level-expectation')

urlpatterns = [
    path('', include(main_router.urls)),
    path('', include(levels_router.urls)),
    path('', include(expectations_router.urls)),
]