from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import TruncMonth
from django.db.models import Count
from .. import models
from datetime import datetime, timedelta


class MetricsView(APIView):
    permission_classes = []  # public for development; change to IsAuthenticated in prod

    def get(self, request):
        students_count = models.Student.objects.count()
        courses_count = models.Course.objects.count()
        staff_count = models.Staff.objects.count()

        # last 6 months enrollments timeseries
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        enroll_qs = models.StudentEnrollment.objects.filter(created_at__gte=six_months_ago)
        enroll_series = (
            enroll_qs.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        series = [{"month": e["month"].strftime("%Y-%m"), "count": e["count"]} for e in enroll_series]

        # simple pass rate sample
        total_assessments = models.StudentAssessment.objects.count()
        passed = models.StudentAssessment.objects.filter(score__gte=50).count() if total_assessments else 0
        pass_rate = (passed / total_assessments * 100) if total_assessments else 0

        return Response({
            "students_count": students_count,
            "courses_count": courses_count,
            "staff_count": staff_count,
            "enrollments_series": series,
            "pass_rate": round(pass_rate, 2),
        })
