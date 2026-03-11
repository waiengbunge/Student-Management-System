from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_number", "first_name", "last_name", "email", "phone", "program", "status"]
        widgets = {
            'status': forms.Select(choices=[('active','Active'),('inactive','Inactive')])
        }
