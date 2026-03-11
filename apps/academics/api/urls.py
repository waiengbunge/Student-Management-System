from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgramViewSet, CourseViewSet, ClassViewSet, ClassLevelViewSet, ClassroomViewSet

router = DefaultRouter()
router.register('programs', ProgramViewSet, basename='program')
router.register('courses', CourseViewSet, basename='course')
router.register('classes', ClassViewSet, basename='class')
router.register('class-levels', ClassLevelViewSet, basename='classlevel')
router.register('classrooms', ClassroomViewSet, basename='classroom')

urlpatterns = [
    path('', include(router.urls)),
]
