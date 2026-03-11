from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, ExamScheduleViewSet, StudentExamResultViewSet

router = DefaultRouter()
router.register(r'exams', ExamViewSet)
router.register(r'schedules', ExamScheduleViewSet)
router.register(r'results', StudentExamResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExamTypeViewSet,
    ExamSessionViewSet,
    ExamPaperViewSet,
    ExamSeatingViewSet,
    ExamAttendanceViewSet,
    ExamResultViewSet,
    ExamResultAdjustmentViewSet,
)

router = DefaultRouter()
router.register(r"types", ExamTypeViewSet)
router.register(r"sessions", ExamSessionViewSet)
router.register(r"papers", ExamPaperViewSet)
router.register(r"seating", ExamSeatingViewSet)
router.register(r"attendance", ExamAttendanceViewSet)
router.register(r"results", ExamResultViewSet)
router.register(r"result-adjustments", ExamResultAdjustmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
