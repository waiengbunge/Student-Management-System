from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentProfileViewSet, GuardianProfileViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register('profiles', StudentProfileViewSet, basename='studentprofile')
router.register('guardians', GuardianProfileViewSet, basename='guardian')
router.register('enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
