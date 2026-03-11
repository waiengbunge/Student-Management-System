from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import get_object_or_404
from . import models
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import StudentForm
from django.utils.decorators import method_decorator
from apps.accounts.decorators import permission_required


class CreateStudentView(CreateView):
    model = models.Student
    form_class = StudentForm
    template_name = "students/_form.html"
    @method_decorator(permission_required('students.manage'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save()
        # return a small success fragment that HTMX will swap into the modal
        return self.render_to_response({
            'created': True,
            'student': obj,
        })

    def form_invalid(self, form):
        return self.render_to_response({'form': form})


class DashboardView(TemplateView):
    template_name = "dashboard.html"
    @method_decorator(permission_required('dashboard.view'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "students_count": models.Student.objects.count(),
            "courses_count": models.Course.objects.count(),
            "staff_count": models.Staff.objects.count(),
        })
        return ctx


class StudentListView(ListView):
    model = models.Student
    template_name = "students/list.html"
    context_object_name = "students"
    paginate_by = 25
    @method_decorator(permission_required('students.view'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class StudentDetailView(DetailView):
    model = models.Student
    template_name = "students/detail.html"
    context_object_name = "student"
    @method_decorator(permission_required('students.view'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CourseListView(ListView):
    model = models.Course
    template_name = "courses/list.html"
    context_object_name = "courses"
    paginate_by = 25
    @method_decorator(permission_required('courses.view'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
