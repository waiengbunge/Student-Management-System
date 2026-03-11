from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel


class PaymentPlan(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    installments_count = models.PositiveIntegerField(default=1)
    grace_period_days = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "payment_plans"
        unique_together = [("tenant", "code")]

class FeeType(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "fee_types"
        unique_together = [("tenant", "code")]

class FeeStructure(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.CASCADE)
    program = models.ForeignKey("academics.Program", on_delete=models.CASCADE)
    class_level = models.ForeignKey("academics.ClassLevel", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "fee_structures"
        unique_together = [("tenant", "code", "academic_year", "program", "class_level")]

class FeeStructureItem(TimeStampedModel):
    fee_structure = models.ForeignKey("finance.FeeStructure", on_delete=models.CASCADE, related_name="items")
    fee_type = models.ForeignKey("finance.FeeType", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)
    class Meta:
        db_table = "fee_structure_items"
        unique_together = [("fee_structure", "fee_type")]

class Invoice(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE)
    fee_structure = models.ForeignKey("finance.FeeStructure", on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="unpaid")
    issued_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "invoices"

class InvoiceItem(TimeStampedModel):
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.CASCADE, related_name="items")
    fee_type = models.ForeignKey("finance.FeeType", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        db_table = "invoice_items"
        unique_together = [("invoice", "fee_type")]

class Payment(TimeStampedModel):
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30, default="pending")
    class Meta:
        db_table = "payments"

class Scholarship(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "scholarships"
        unique_together = [("tenant", "code")]

class StudentScholarship(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE)
    scholarship = models.ForeignKey("finance.Scholarship", on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    amount_awarded = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        db_table = "student_scholarships"
        unique_together = [("student_profile", "scholarship")]
