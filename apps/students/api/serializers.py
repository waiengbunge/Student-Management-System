from rest_framework import serializers
from apps.students.models import StudentProfile, GuardianProfile, Enrollment
from apps.students.services import generate_student_number


class GuardianProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianProfile
        fields = ["id", "user", "full_name", "phone", "email", "relationship_type", "occupation"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "user_email",
            "current_program",
            "admission_offer",
            "student_number",
            "admitted_on",
            "current_status",
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            # enforce tenant scoping: created student must belong to same tenant
            tenant = getattr(request.user, 'tenant', None)
            if 'tenant' in self.initial_data and self.initial_data.get('tenant') != getattr(tenant, 'id', None):
                raise serializers.ValidationError('Cannot create student for a different tenant')
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        # enforce tenant for non-superusers
        if request and not getattr(request.user, 'is_superuser', False):
            validated_data['tenant'] = getattr(request.user, 'tenant')

        tenant = validated_data.get('tenant')
        # generate student_number if missing
        if not validated_data.get('student_number') and tenant:
            validated_data['student_number'] = generate_student_number(tenant)

        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student_profile",
            "program",
            "academic_year",
            "term",
            "class_obj",
            "payment_plan",
            "enrollment_number",
            "enrolled_on",
            "status",
        ]

    def validate(self, data):
        # ensure a student is not enrolled twice for same program/year/term
        student = data.get('student_profile')
        program = data.get('program')
        academic_year = data.get('academic_year')
        term = data.get('term')
        class_obj = data.get('class_obj')
        if student and program and academic_year and term:
            qs = Enrollment.objects.filter(student_profile=student, program=program, academic_year=academic_year, term=term)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('Student is already enrolled for this program, year and term')

        # capacity check when class is assigned
        if class_obj is not None:
            cap = getattr(class_obj, 'capacity', None)
            if cap is not None:
                current = Enrollment.objects.filter(class_obj=class_obj, status='active').count()
                # if updating, exclude self
                if self.instance and getattr(self.instance, 'class_obj_id', None) == class_obj.id:
                    # updating same class - current count already includes instance
                    pass
                if current >= cap:
                    raise serializers.ValidationError('Selected class is at full capacity')

        return data

    def create(self, validated_data):
        # ensure enrollment_number exists; generate if missing
        if not validated_data.get('enrollment_number'):
            # simple generator: ENR-{tenant_id}-{count+1}
            tenant = getattr(validated_data.get('student_profile'), 'tenant', None)
            from apps.students.models import Enrollment as EnrollmentModel
            count = EnrollmentModel.objects.filter(student_profile__tenant=tenant).count() if tenant else EnrollmentModel.objects.count()
            validated_data['enrollment_number'] = f"ENR-{getattr(tenant, 'id', 0)}-{count+1:06d}"
        return super().create(validated_data)
