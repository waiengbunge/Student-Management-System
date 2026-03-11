from django.contrib import admin
from .models import (
    PaymentPlan, FeeType, FeeStructure, FeeStructureItem, Invoice, InvoiceItem, Payment, Scholarship, StudentScholarship
)

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "installments_count", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "academic_year", "program", "class_level", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("academic_year", "program", "class_level", "is_active")

@admin.register(FeeStructureItem)
class FeeStructureItemAdmin(admin.ModelAdmin):
    list_display = ("fee_structure", "fee_type", "amount", "due_date", "is_mandatory")
    search_fields = ("fee_structure__name", "fee_type__name")
    list_filter = ("fee_structure", "fee_type", "is_mandatory")

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("student_profile", "fee_structure", "total_amount", "due_date", "status", "issued_at")
    search_fields = ("student_profile__student_id",)
    list_filter = ("status", "fee_structure")

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "fee_type", "amount")
    search_fields = ("invoice__id", "fee_type__name")
    list_filter = ("fee_type",)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "payment_date", "payment_method", "status", "received_by")
    search_fields = ("invoice__id", "reference_number")
    list_filter = ("payment_method", "status")

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "amount", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

@admin.register(StudentScholarship)
class StudentScholarshipAdmin(admin.ModelAdmin):
    list_display = ("student_profile", "scholarship", "amount_awarded", "awarded_at")
    search_fields = ("student_profile__student_id", "scholarship__name")
    list_filter = ("scholarship",)
