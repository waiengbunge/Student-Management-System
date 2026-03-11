from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet, AssessmentItemViewSet, StudentAssessmentViewSet

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet)
router.register(r'items', AssessmentItemViewSet)
router.register(r'student-assessments', StudentAssessmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    GradingSchemeViewSet,
    GradingSchemeItemViewSet,
    AssessmentComponentViewSet,
    AssessmentItemViewSet,
    StudentAssessmentViewSet,
    AssessmentAdjustmentViewSet,
    AssessmentFeedbackViewSet,
    PassFailRuleViewSet,
    GradePublicationBatchViewSet,
)

router = DefaultRouter()
router.register(r"grading-schemes", GradingSchemeViewSet)
router.register(r"grading-scheme-items", GradingSchemeItemViewSet)
router.register(r"components", AssessmentComponentViewSet)
router.register(r"items", AssessmentItemViewSet)
router.register(r"student-assessments", StudentAssessmentViewSet)
router.register(r"adjustments", AssessmentAdjustmentViewSet)
router.register(r"feedback", AssessmentFeedbackViewSet)
router.register(r"pass-fail-rules", PassFailRuleViewSet)
router.register(r"publication-batches", GradePublicationBatchViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
