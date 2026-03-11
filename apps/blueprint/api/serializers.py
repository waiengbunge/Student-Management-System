from rest_framework import serializers
from ..models import Student, Course


class StudentSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = Student
        fields = ["id", "student_number", "first_name", "last_name", "email", "phone", "program", "program_name", "status"]


class CourseSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = Course
        fields = ["id", "code", "name", "program", "program_name", "credit_hours"]
