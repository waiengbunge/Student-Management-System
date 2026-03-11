from django.db import transaction
from apps.students.models import StudentProfile


def generate_student_number(tenant, campus=None, user=None):
    """Generate a simple tenant-scoped student number.

    Format: ST-{tenant.id}-{sequential:06d}
    This is deterministic and safe for initial use; replace with more
    sophisticated rules as needed.
    """
    tenant_id = getattr(tenant, 'id', None) or '0'
    # Use a DB-backed sequential number per tenant
    with transaction.atomic():
        count = StudentProfile.objects.filter(tenant=tenant).select_for_update().count()
        seq = count + 1
        return f"ST-{tenant_id}-{seq:06d}"
# Business logic for Students app
