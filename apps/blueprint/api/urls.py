from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .viewsets import StudentViewSet, CourseViewSet
from .metrics import MetricsView
from .dtable_views import StudentListAPI, CourseListAPI

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="student")
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    path("", include(router.urls)),
    path("metrics/", MetricsView.as_view(), name="metrics"),
    path("server/students/", StudentListAPI.as_view(), name="server_students"),
    path("server/courses/", CourseListAPI.as_view(), name="server_courses"),
]
