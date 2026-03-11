from rest_framework import serializers
from .models import Exam, ExamSchedule, StudentExamResult


class ExamScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSchedule
        fields = '__all__'


class ExamSerializer(serializers.ModelSerializer):
    schedules = ExamScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'tenant', 'program', 'course', 'title', 'description', 'is_published', 'schedules']


class StudentExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamResult
        fields = ['id', 'exam', 'student_profile', 'score', 'grade', 'remarks']

    def validate(self, data):
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            tenant = getattr(request.user, 'tenant', None)
            sp = data.get('student_profile')
            if sp and getattr(sp, 'tenant', None) != tenant:
                raise serializers.ValidationError('Student must belong to your tenant')
        return data
from rest_framework import serializers
from .models import (
    ExamType, ExamSession, ExamPaper, ExamSeating, ExamAttendance, ExamResult, ExamResultAdjustment
)

class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = "__all__"

class ExamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSession
        fields = "__all__"

class ExamPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamPaper
        fields = "__all__"

class ExamSeatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSeating
        fields = "__all__"

class ExamAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttendance
        fields = "__all__"

class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = "__all__"

class ExamResultAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResultAdjustment
        fields = "__all__"
