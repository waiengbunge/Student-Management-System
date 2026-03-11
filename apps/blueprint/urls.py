from django.urls import path
from . import views

app_name = "blueprint"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("students/", views.StudentListView.as_view(), name="students_list"),
    path("students/add/", views.CreateStudentView.as_view(), name="students_add"),
    path("students/<uuid:pk>/", views.StudentDetailView.as_view(), name="students_detail"),
    path("courses/", views.CourseListView.as_view(), name="courses_list"),
]
