from rest_framework import serializers
from .models import (
    PaymentPlan, FeeType, FeeStructure, FeeStructureItem, Invoice, InvoiceItem, Payment, Scholarship, StudentScholarship
)

class PaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = "__all__"

class FeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeType
        fields = "__all__"

class FeeStructureItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructureItem
        fields = "__all__"

class FeeStructureSerializer(serializers.ModelSerializer):
    items = FeeStructureItemSerializer(many=True, read_only=True)
    class Meta:
        model = FeeStructure
        fields = "__all__"

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = "__all__"

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    class Meta:
        model = Invoice
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = "__all__"

class StudentScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentScholarship
        fields = "__all__"
