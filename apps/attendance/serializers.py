from rest_framework import serializers
from .models import (
	AttendancePolicy,
	AttendanceSession,
	StudentAttendanceRecord,
	AttendanceAdjustment,
	AttendanceSummary,
	AttendanceWarning,
)


class AttendancePolicySerializer(serializers.ModelSerializer):
	class Meta:
		model = AttendancePolicy
		fields = "__all__"


class AttendanceSessionSerializer(serializers.ModelSerializer):
	class Meta:
		model = AttendanceSession
		fields = "__all__"


class StudentAttendanceRecordSerializer(serializers.ModelSerializer):
	class Meta:
		model = StudentAttendanceRecord
		fields = "__all__"


class AttendanceAdjustmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = AttendanceAdjustment
		fields = "__all__"


class AttendanceSummarySerializer(serializers.ModelSerializer):
	class Meta:
		model = AttendanceSummary
		fields = "__all__"


class AttendanceWarningSerializer(serializers.ModelSerializer):
	class Meta:
		model = AttendanceWarning
		fields = "__all__"
