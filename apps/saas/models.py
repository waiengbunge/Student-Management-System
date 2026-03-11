from django.db import models
from apps.common.models import TimeStampedModel

class SubscriptionPlan(TimeStampedModel):
    name = models.CharField(max_length=120)
    code = models.SlugField(unique=True)
    monthly_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    annual_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_campuses = models.PositiveIntegerField(default=1)
    max_active_students = models.PositiveIntegerField(default=0)
    class Meta:
        db_table = "subscription_plans"

class Tenant(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    legal_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, default="active")
    default_timezone = models.CharField(max_length=100, default="Pacific/Port_Moresby")
    default_currency = models.CharField(max_length=10, default="PGK")
    class Meta:
        db_table = "tenants"
    def __str__(self):
        return self.name

class TenantSubscription(TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, related_name="subscriptions")
    subscription_plan = models.ForeignKey("saas.SubscriptionPlan", on_delete=models.PROTECT, related_name="tenant_subscriptions")
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default="active")
    billing_cycle = models.CharField(max_length=30, default="monthly")
    class Meta:
        db_table = "tenant_subscriptions"

class Campus(TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, related_name="campuses")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    is_main_campus = models.BooleanField(default=False)
    class Meta:
        db_table = "campuses"
        unique_together = [("tenant", "code")]

class TenantSetting(TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, related_name="settings")
    setting_key = models.CharField(max_length=120)
    setting_value_json = models.JSONField(default=dict, blank=True)
    class Meta:
        db_table = "tenant_settings"
        unique_together = [("tenant", "setting_key")]
