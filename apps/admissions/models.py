from django.db import models
from apps.common.models import CampusScopedModel, TimeStampedModel

class AdmissionCycle(CampusScopedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50)
    class Meta:
        db_table = "admission_cycles"
        unique_together = [("tenant", "code")]

class Application(CampusScopedModel):
    admission_cycle = models.ForeignKey("admissions.AdmissionCycle", on_delete=models.PROTECT, related_name="applications")
    program = models.ForeignKey("academics.Program", on_delete=models.PROTECT, related_name="applications")
    application_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    current_status = models.CharField(max_length=50)
    class Meta:
        db_table = "applications"
        unique_together = [("tenant", "application_number")]

class ApplicationDocument(TimeStampedModel):
    application = models.ForeignKey("admissions.Application", on_delete=models.CASCADE, related_name="documents")
    file_upload = models.ForeignKey("common.FileUpload", on_delete=models.CASCADE, related_name="application_documents")
    document_type = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        db_table = "application_documents"

class ApplicationStatusHistory(TimeStampedModel):
    application = models.ForeignKey("admissions.Application", on_delete=models.CASCADE, related_name="status_history")
    changed_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)
    changed_at = models.DateTimeField()
    class Meta:
        db_table = "application_status_history"

class AdmissionOffer(TimeStampedModel):
    application = models.ForeignKey("admissions.Application", on_delete=models.CASCADE, related_name="offers")
    offer_number = models.CharField(max_length=50, unique=True)
    offered_on = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)
    class Meta:
        db_table = "admission_offers"

class OfferAcceptance(TimeStampedModel):
    admission_offer = models.OneToOneField("admissions.AdmissionOffer", on_delete=models.CASCADE, related_name="acceptance")
    decision = models.CharField(max_length=30)
    decided_on = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    class Meta:
        db_table = "offer_acceptances"
