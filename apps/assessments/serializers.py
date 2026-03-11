from rest_framework import serializers
from .models import Assessment, AssessmentItem, StudentAssessment


class AssessmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentItem
        fields = '__all__'


class AssessmentSerializer(serializers.ModelSerializer):
    items = AssessmentItemSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = ['id', 'tenant', 'program', 'course', 'name', 'assessment_type', 'scheduled_at', 'items']


class StudentAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAssessment
        fields = ['id', 'assessment', 'student_profile', 'score', 'grade', 'remarks']

    def validate(self, data):
        # basic tenant scoping: student must belong to same tenant
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            tenant = getattr(request.user, 'tenant', None)
            sp = data.get('student_profile')
            if sp and getattr(sp, 'tenant', None) != tenant:
                raise serializers.ValidationError('Student must belong to your tenant')
        return data
from rest_framework import serializers
from .models import (
    GradingScheme, GradingSchemeItem, AssessmentComponent, AssessmentItem, StudentAssessment,
    AssessmentAdjustment, AssessmentFeedback, PassFailRule, GradePublicationBatch
)

class GradingSchemeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingSchemeItem
        fields = "__all__"

class GradingSchemeSerializer(serializers.ModelSerializer):
    items = GradingSchemeItemSerializer(many=True, read_only=True)
    class Meta:
        model = GradingScheme
        fields = "__all__"

class AssessmentComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentComponent
        fields = "__all__"

class AssessmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentItem
        fields = "__all__"

class StudentAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAssessment
        fields = "__all__"

class AssessmentAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentAdjustment
        fields = "__all__"

class AssessmentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentFeedback
        fields = "__all__"

class PassFailRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassFailRule
        fields = "__all__"

class GradePublicationBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradePublicationBatch
        fields = "__all__"
