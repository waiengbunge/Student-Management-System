"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from apps.accounts import views as accounts_views

urlpatterns = [
    # Generic dashboard route that chooses role-specific dashboard
    path('dashboard/', accounts_views.dashboard, name='dashboard'),
    
    # Role-specific dashboards (place these before the admin site so 'admin/dashboard/' resolves to our view)
    path('admin/dashboard/', accounts_views.admin_dashboard, name='admin_dashboard'),
    path('student/dashboard/', accounts_views.student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', accounts_views.instructor_dashboard, name='instructor_dashboard'),
    # Admin module routes
    path('admin/students/', accounts_views.admin_students_list, name='admin_students_list'),
    path('admin/students/add/', accounts_views.admin_student_add, name='admin_student_add'),
    path('admin/students/<uuid:pk>/', accounts_views.admin_student_detail, name='admin_student_detail'),
    path('admin/students/<uuid:pk>/edit/', accounts_views.admin_student_edit, name='admin_student_edit'),
    path('admin/students/<uuid:pk>/delete/', accounts_views.admin_student_delete, name='admin_student_delete'),

    path('admin/programs/', accounts_views.admin_programs_list, name='admin_programs_list'),
    path('admin/programs/add/', accounts_views.admin_program_add, name='admin_program_add'),
    path('admin/programs/<uuid:pk>/edit/', accounts_views.admin_program_edit, name='admin_program_edit'),
    path('admin/programs/<uuid:pk>/delete/', accounts_views.admin_program_delete, name='admin_program_delete'),

    path('admin/courses/', accounts_views.admin_courses_list, name='admin_courses_list'),
    path('admin/courses/add/', accounts_views.admin_course_add, name='admin_course_add'),
    path('admin/courses/<uuid:pk>/delete/', accounts_views.admin_course_delete, name='admin_course_delete'),

    path('admin/classes/', accounts_views.admin_classes_list, name='admin_classes_list'),
    path('admin/classes/add/', accounts_views.admin_class_add, name='admin_class_add'),
    path('admin/classes/<uuid:pk>/edit/', accounts_views.admin_class_edit, name='admin_class_edit'),
    path('admin/classes/<uuid:pk>/delete/', accounts_views.admin_class_delete, name='admin_class_delete'),

    # Admin module placeholders
    path('admin/enrollment/', accounts_views.admin_enrollment, name='admin_enrollment'),
    path('admin/enrollment/list/', accounts_views.admin_enrollment_list, name='admin_enrollment_list'),
    path('admin/enrollment/student/<uuid:pk>/', accounts_views.admin_enrollment_student, name='admin_enrollment_student'),
    path('admin/enrollment/course/<uuid:pk>/', accounts_views.admin_enrollment_course, name='admin_enrollment_course'),
    path('admin/scheduling/', accounts_views.admin_scheduling, name='admin_scheduling'),
    path('admin/attendance/', accounts_views.admin_attendance, name='admin_attendance'),
    path('admin/assessments/', accounts_views.admin_assessments, name='admin_assessments'),
    path('admin/spr/', accounts_views.admin_spr, name='admin_spr'),
    path('admin/exams/', accounts_views.admin_exams, name='admin_exams'),
    path('admin/finance/', accounts_views.admin_finance, name='admin_finance'),
    path('admin/requests/', accounts_views.admin_requests, name='admin_requests'),
    path('admin/transcripts/', accounts_views.admin_transcripts, name='admin_transcripts'),
    path('admin/reports/', accounts_views.admin_reports, name='admin_reports'),
    path('admin/notifications/', accounts_views.admin_notifications, name='admin_notifications'),
    path('admin/users/', accounts_views.admin_users, name='admin_users'),
    path('admin/permissions/', accounts_views.admin_permissions, name='admin_permissions'),
    path('admin/users/list/', accounts_views.admin_user_list, name='admin_user_list'),
    path('admin/users/add/', accounts_views.admin_user_create, name='admin_user_add'),
    path('admin/users/<int:user_pk>/assign/', accounts_views.admin_user_assign_role, name='admin_user_assign_role'),
    path('admin/users/<int:user_pk>/', accounts_views.admin_user_view, name='admin_user_view'),
    path('admin/users/<int:user_pk>/edit/', accounts_views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_pk>/deactivate/', accounts_views.admin_user_deactivate, name='admin_user_deactivate'),
    path('admin/roles/', accounts_views.admin_roles_list, name='admin_roles_list'),
    path('admin/roles/add/', accounts_views.admin_role_create, name='admin_role_create'),
    path('admin/roles/<int:role_pk>/permissions/', accounts_views.admin_role_permissions, name='admin_role_permissions'),
    path('admin/settings/', accounts_views.admin_settings, name='admin_settings'),

    path('admin/', admin.site.urls),
    # Legacy auth paths redirect to new auth endpoints
    path('accounts/login/', RedirectView.as_view(url='/login/')),
    path('accounts/logout/', RedirectView.as_view(url='/logout/')),
    # Common top-level routes (redirect to role-appropriate dashboards)
    path('students/', RedirectView.as_view(url='/student/dashboard/')),
    path('programs/', RedirectView.as_view(url='/admin/dashboard/')),
    path('courses/', RedirectView.as_view(url='/admin/dashboard/')),
    path('admissions/', RedirectView.as_view(url='/admin/dashboard/')),
    path('classes/', RedirectView.as_view(url='/admin/dashboard/')),
    path('enrollment/', RedirectView.as_view(url='/admin/dashboard/')),
    path('attendance/', RedirectView.as_view(url='/admin/dashboard/')),
    path('assessments/', RedirectView.as_view(url='/admin/dashboard/')),
    path('finance/', RedirectView.as_view(url='/admin/dashboard/')),
    path('requests/', RedirectView.as_view(url='/admin/dashboard/')),
    path('reports/', RedirectView.as_view(url='/admin/dashboard/')),
    path('users/', RedirectView.as_view(url='/admin/dashboard/')),
    path('settings/', RedirectView.as_view(url='/admin/dashboard/')),
    # Redirect root to login page
    path('', RedirectView.as_view(url='/login/')),
    # Authentication: custom login at /login/ and logout at /logout/
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('accounts/signup/', accounts_views.signup, name='signup'),
    path('accounts/change-password/', accounts_views.change_password, name='change_password'),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    path('api/v1/assessments/', include('apps.assessments.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/exams/', include('apps.exams.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/blueprint/', include('apps.blueprint.api.urls')),
    path('api/v1/requests/', include('apps.requests_app.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/accounts/', include('apps.accounts.api.urls')),
    path('api/v1/students/', include('apps.students.api.urls')),
    path('api/v1/academics/', include('apps.academics.api.urls')),
    
]
