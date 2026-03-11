from django.db import models
from apps.common.models import CampusScopedModel, TenantScopedModel, TimeStampedModel

class Department(CampusScopedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    class Meta:
        db_table = "departments"
        unique_together = [("tenant", "campus", "code")]

class Position(TenantScopedModel):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    class Meta:
        db_table = "positions"
        unique_together = [("tenant", "code")]

class StaffProfile(CampusScopedModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="staff_profile")
    department = models.ForeignKey("hr.Department", on_delete=models.PROTECT, related_name="staff_profiles")
    position = models.ForeignKey("hr.Position", on_delete=models.PROTECT, related_name="staff_profiles")
    staff_number = models.CharField(max_length=50)
    employment_type = models.CharField(max_length=50)
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    class Meta:
        db_table = "staff_profiles"
        unique_together = [("tenant", "staff_number")]

class StaffEmploymentRecord(TimeStampedModel):
    staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.CASCADE, related_name="employment_records")
    department = models.ForeignKey("hr.Department", on_delete=models.PROTECT)
    position = models.ForeignKey("hr.Position", on_delete=models.PROTECT)
    campus = models.ForeignKey("saas.Campus", on_delete=models.PROTECT)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    employment_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    class Meta:
        db_table = "staff_employment_records"

class ReportingLine(TimeStampedModel):
    staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.CASCADE, related_name="manager_links")
    reports_to_staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.CASCADE, related_name="subordinate_links")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    class Meta:
        db_table = "reporting_lines"
        unique_together = [("staff_profile", "reports_to_staff_profile", "effective_from")]

class StaffQualification(TimeStampedModel):
    staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.CASCADE, related_name="qualifications")
    qualification_name = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    year_awarded = models.PositiveIntegerField(null=True, blank=True)
    file_upload = models.ForeignKey("common.FileUpload", on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        db_table = "staff_qualifications"

class StaffCertification(TimeStampedModel):
    staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.CASCADE, related_name="certifications")
    certificate_name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255, blank=True)
    issued_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    file_upload = models.ForeignKey("common.FileUpload", on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        db_table = "staff_certifications"
