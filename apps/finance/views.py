from rest_framework import viewsets
from apps.accounts.drf_permissions import RolePermissionDRF

from .models import (
    PaymentPlan,
    FeeType,
    FeeStructure,
    FeeStructureItem,
    Invoice,
    InvoiceItem,
    Payment,
    Scholarship,
    StudentScholarship,
)
from .serializers import (
    PaymentPlanSerializer,
    FeeTypeSerializer,
    FeeStructureSerializer,
    FeeStructureItemSerializer,
    InvoiceSerializer,
    InvoiceItemSerializer,
    PaymentSerializer,
    ScholarshipSerializer,
    StudentScholarshipSerializer,
)


class FeeTypeViewSet(viewsets.ModelViewSet):
    queryset = FeeType.objects.all()
    serializer_class = FeeTypeSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'


class PaymentPlanViewSet(viewsets.ModelViewSet):
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'


class FeeStructureItemViewSet(viewsets.ModelViewSet):
    queryset = FeeStructureItem.objects.all()
    serializer_class = FeeStructureItemSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'


class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'


class StudentScholarshipViewSet(viewsets.ModelViewSet):
    queryset = StudentScholarship.objects.all()
    serializer_class = StudentScholarshipSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'finance.manage'
