from decimal import Decimal
from django.utils import timezone
from .models import Invoice, InvoiceItem, FeeStructure, FeeStructureItem, Payment, Scholarship, StudentScholarship


class FinanceService:
    """Service methods for finance workflows."""
    @staticmethod
    def generate_invoice(student_profile_id, fee_structure_id):
        try:
            fs = FeeStructure.objects.get(pk=fee_structure_id)
        except FeeStructure.DoesNotExist:
            return None

        items = FeeStructureItem.objects.filter(fee_structure=fs)
        total = Decimal('0.00')
        for it in items:
            total += (it.amount or Decimal('0.00'))

        inv = Invoice.objects.create(
            student_profile_id=student_profile_id,
            fee_structure=fs,
            total_amount=total,
            due_date=fs.items.first().due_date if fs.items.exists() else None,
            status='unpaid'
        )

        for it in items:
            InvoiceItem.objects.create(invoice=inv, fee_type=it.fee_type, amount=it.amount)

        return inv

    @staticmethod
    def record_payment(invoice_id, amount, payment_method, reference_number=None, received_by_id=None):
        try:
            inv = Invoice.objects.get(pk=invoice_id)
        except Invoice.DoesNotExist:
            return None

        payment = Payment.objects.create(
            invoice=inv,
            amount=Decimal(amount),
            payment_date=timezone.now().date(),
            payment_method=payment_method,
            reference_number=reference_number or '',
            received_by_id=received_by_id,
            status='completed'
        )

        # compute total paid so far
        paid = Payment.objects.filter(invoice=inv, status='completed').aggregate(total_amount__sum=('amount'))['total_amount__sum']
        if paid is None:
            paid = Decimal('0.00')

        if paid >= inv.total_amount:
            inv.status = 'paid'
            inv.save(update_fields=['status'])

        return payment

    @staticmethod
    def apply_scholarship(student_profile_id, scholarship_id):
        try:
            sch = Scholarship.objects.get(pk=scholarship_id)
        except Scholarship.DoesNotExist:
            return None

        ss = StudentScholarship.objects.create(
            student_profile_id=student_profile_id,
            scholarship=sch,
            amount_awarded=sch.amount
        )
        return ss

    @staticmethod
    def get_student_balance(student_profile_id):
        invoices = Invoice.objects.filter(student_profile_id=student_profile_id)
        total_due = Decimal('0.00')
        for inv in invoices:
            if inv.status != 'paid':
                total_due += inv.total_amount or Decimal('0.00')

        payments = Payment.objects.filter(invoice__student_profile_id=student_profile_id, status='completed')
        total_paid = sum((p.amount or Decimal('0.00')) for p in payments)

        scholarships = StudentScholarship.objects.filter(student_profile_id=student_profile_id)
        total_sch = sum((s.amount_awarded or Decimal('0.00')) for s in scholarships)

        balance = total_due - total_paid - total_sch
        return balance
