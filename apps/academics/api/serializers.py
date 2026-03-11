from rest_framework import serializers
from apps.academics.models import Program, Course, Class, ClassLevel, Classroom


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['id', 'tenant', 'campus', 'name', 'code', 'award_type', 'duration_months', 'status']

    def validate(self, data):
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            data['tenant'] = getattr(request.user, 'tenant', None)
        return data


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'tenant', 'department', 'name', 'code', 'credit_hours', 'status']

    def validate(self, data):
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            data['tenant'] = getattr(request.user, 'tenant', None)
        return data


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ['id', 'tenant', 'name', 'level_order']


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'tenant', 'campus', 'program', 'academic_year', 'class_level', 'name', 'code', 'batch_name', 'capacity', 'status']

    def validate(self, data):
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            data['tenant'] = getattr(request.user, 'tenant', None)
        return data


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'tenant', 'campus', 'name', 'code', 'capacity', 'room_type']
