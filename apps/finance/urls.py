from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentPlanViewSet,
    FeeTypeViewSet,
    FeeStructureViewSet,
    FeeStructureItemViewSet,
    InvoiceViewSet,
    InvoiceItemViewSet,
    PaymentViewSet,
    ScholarshipViewSet,
    StudentScholarshipViewSet,
)

router = DefaultRouter()
router.register(r"payment-plans", PaymentPlanViewSet)
router.register(r"fee-types", FeeTypeViewSet)
router.register(r"fee-structures", FeeStructureViewSet)
router.register(r"fee-structure-items", FeeStructureItemViewSet)
router.register(r"invoices", InvoiceViewSet)
router.register(r"invoice-items", InvoiceItemViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"scholarships", ScholarshipViewSet)
router.register(r"student-scholarships", StudentScholarshipViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
