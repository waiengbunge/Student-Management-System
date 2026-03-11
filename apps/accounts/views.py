from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from apps.saas.models import Tenant
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone


@login_required
def dashboard(request):
    user = request.user
    # Use centralized role-name helper (prefers UserRole then groups)
    role_names = _get_user_role_names(user)
    try:
        group_names = set(g.name.lower() for g in user.groups.all())
    except Exception:
        group_names = set()
    if 'student' in role_names:
        template = 'dashboard/student_dashboard.html'
    elif 'instructor' in role_names:
        template = 'dashboard/instructor_dashboard.html'
    elif 'training manager' in role_names:
        template = 'dashboard/training_manager_dashboard.html'
    elif 'registrar' in role_names:
        template = 'dashboard/registrar_dashboard.html'
    elif 'accountant' in role_names or 'cashier' in role_names:
        template = 'dashboard/finance_dashboard.html'
    elif 'marketing manager' in role_names:
        template = 'dashboard/marketing_dashboard.html'
    elif 'receptionist' in role_names:
        template = 'dashboard/receptionist_dashboard.html'
    elif 'managing director' in role_names:
        template = 'dashboard/managing_director_dashboard.html'
    elif 'system administrator' in role_names or user.is_staff or user.is_superuser:
        template = 'dashboard/admin_dashboard.html'
    else:
        template = 'dashboard/admin_dashboard.html'

    # Prepare role-specific context data
    context = {}

    # Admin / staff: collect site-wide metrics for the accounts dashboard
    if user.is_superuser or user.is_staff or 'admin' in group_names:
        import json
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group

        User = get_user_model()
        user_count = User.objects.count()
        staff_count = User.objects.filter(is_staff=True).count()
        group_count = Group.objects.count()

        # Students and programs may live in different apps depending on setup — try common locations
        students_count = 0
        programs_count = 0
        try:
            from apps.blueprint.models import Student as BlueprintStudent
            students_count = BlueprintStudent.objects.count()
        except Exception:
            try:
                from apps.academics.models import Student as AcadStudent
                students_count = AcadStudent.objects.count()
            except Exception:
                students_count = 0

        try:
            from apps.academics.models import Program as AcadProgram
            programs_count = AcadProgram.objects.count()
        except Exception:
            try:
                from apps.blueprint.models import Program as BlueprintProgram
                programs_count = BlueprintProgram.objects.count()
            except Exception:
                programs_count = 0

        # Simple revenue/time series placeholder — try finance model if present
        revenue_series = []
        try:
            from apps.finance.models import PaymentTransaction
            # aggregate monthly revenue for last 6 months
            from django.db.models.functions import TruncMonth
            from django.db.models import Sum
            qs = PaymentTransaction.objects.all().annotate(m=TruncMonth('created_at')).values('m').annotate(total=Sum('amount')).order_by('m')[:6]
            revenue_series = [{'month': x['m'].strftime('%b %Y') if x['m'] else '', 'value': float(x['total'] or 0)} for x in qs]
        except Exception:
            # fallback dummy last-6-months
            import datetime
            today = datetime.date.today()
            revenue_series = []
            for i in range(5, -1, -1):
                m = (today.replace(day=1) - datetime.timedelta(days=30 * i))
                revenue_series.append({'month': m.strftime('%b %Y'), 'value': 0})

        # Program distribution
        program_distribution = []
        try:
            from apps.blueprint.models import Program as BlueprintProgram
            qs = BlueprintProgram.objects.values('name').annotate(cnt=__import__('django').db.models.Count('id')).order_by('-cnt')[:8]
            program_distribution = [{'label': x['name'], 'value': x['cnt']} for x in qs]
        except Exception:
            program_distribution = []

        context = {
            'stats': {
                'user_count': user_count,
                'staff_count': staff_count,
                'group_count': group_count,
                'students_count': students_count,
                'programs_count': programs_count,
            },
            'revenue_series_json': json.dumps(revenue_series),
            'program_distribution_json': json.dumps(program_distribution),
        }

    # Student dashboard context
    if template == 'student/dashboard.html':
        try:
            from apps.blueprint.models import Student as BlueprintStudent
            from apps.blueprint.models import Course as BlueprintCourse
            stud = None
            if user.email:
                stud = BlueprintStudent.objects.filter(email__iexact=user.email).first()
            if not stud:
                stud = BlueprintStudent.objects.filter(student_number__iexact=user.username).first()

            enrolled = 0
            attendance_pct = 0
            outstanding = 0
            upcoming = 0
            if stud:
                # assume relations exist
                try:
                    enrolled = stud.course_set.count()
                except Exception:
                    enrolled = 0
                # placeholders
                attendance_pct = 92
                outstanding = 0
                upcoming = 2
            else:
                enrolled = 0
                attendance_pct = 0
                outstanding = 0
                upcoming = 0

            context.update({'student_summary': {'courses': enrolled, 'attendance': attendance_pct, 'outstanding': outstanding, 'upcoming': upcoming}})
        except Exception:
            context.update({'student_summary': {'courses': 0, 'attendance': 0, 'outstanding': 0, 'upcoming': 0}})

    # Instructor dashboard context
    if template == 'instructor/dashboard.html':
        try:
            # try to compute assigned classes and pending attendance
            from apps.blueprint.models import Course as BlueprintCourse
            assigned = BlueprintCourse.objects.filter(instructor__email__iexact=user.email).count() if hasattr(BlueprintCourse, 'instructor') else 0
            pending_attendance = 0
            spr_drafts = 0
            upcoming_exams = 0
            context.update({'instructor_summary': {'assigned': assigned, 'pending_attendance': pending_attendance, 'spr_drafts': spr_drafts, 'upcoming_exams': upcoming_exams}})
        except Exception:
            context.update({'instructor_summary': {'assigned': 0, 'pending_attendance': 0, 'spr_drafts': 0, 'upcoming_exams': 0}})

    # Registrar / training manager contexts: basic counts + trend placeholders
    if template in ('registrar/dashboard.html', 'training_manager/dashboard.html'):
        try:
            from apps.blueprint.models import Student as BlueprintStudent
            enrollment_count = BlueprintStudent.objects.count()
        except Exception:
            enrollment_count = 0
        trend = []
        try:
            # build last 6 months enrollment trend
            import datetime
            today = datetime.date.today()
            for i in range(5, -1, -1):
                m = (today.replace(day=1) - datetime.timedelta(days=30 * i))
                trend.append({'month': m.strftime('%b %Y'), 'count': 0})
        except Exception:
            trend = []
        context.update({'registrar_summary': {'enrollment_count': enrollment_count, 'trend_json': __import__('json').dumps(trend)}})

    return render(request, template, context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        email = request.POST.get('email')
        if form.is_valid():
            username = form.cleaned_data.get('username') if 'username' in form.cleaned_data else email.split('@')[0]
            raw_password = form.cleaned_data.get('password1')

            # ensure tenant exists
            tenant = Tenant.objects.first()
            if tenant is None:
                tenant = Tenant.objects.create(name='System', slug='system')

            User = get_user_model()
            # create user with required tenant and email
            user = User.objects.create_user(email=email, username=username, password=raw_password, tenant=tenant)

            # create basic profile
            try:
                from apps.accounts.models import UserProfile
                UserProfile.objects.create(user=user, first_name=username, last_name='')
            except Exception:
                pass

            messages.success(request, 'Account created. A System Administrator must assign a role before access is granted.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


@ensure_csrf_cookie
def login_view(request):
    # custom login view supporting username or email and role redirection
    if request.method == 'POST':
        identifier = request.POST.get('username') or request.POST.get('identifier')
        password = request.POST.get('password')
        user = None
        if identifier and password:
            # try authenticate directly (User may use email as USERNAME_FIELD)
            user = authenticate(request, username=identifier, password=password)
            if not user:
                # try lookup by email then authenticate by username if necessary
                try:
                    User = get_user_model()
                    u = User.objects.filter(email__iexact=identifier).first()
                    if u:
                        user = authenticate(request, username=u.email, password=password)
                except Exception:
                    user = None

        if user is not None:
            auth_login(request, user)
            # Central dashboard view will select the correct template based on user's role
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'accounts/login.html', {})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required
@ensure_csrf_cookie
def student_dashboard(request):
    # ensure student role
    group_names = _get_user_role_names(request.user)
    if 'student' not in group_names and not request.user.is_superuser:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('instructor_dashboard')
    # simple placeholders
    context = {}
    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
@ensure_csrf_cookie
def instructor_dashboard(request):
    group_names = _get_user_role_names(request.user)
    if 'instructor' not in group_names and not request.user.is_superuser:
        # redirect to correct dashboard
        if 'student' in group_names:
            return redirect('student_dashboard')
        return redirect('admin_dashboard')
    context = {}
    return render(request, 'dashboard/instructor_dashboard.html', context)


@login_required
@ensure_csrf_cookie
def admin_dashboard(request):
    # allow only staff/admin
    if not _is_admin_user(request.user):
        # redirect to user's role dashboard
        group_names = _get_user_role_names(request.user)
        if 'student' in group_names:
            return redirect('student_dashboard')
        if 'instructor' in group_names:
            return redirect('instructor_dashboard')
        return HttpResponseForbidden('Forbidden')

    # minimal admin context
    import json
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_count = User.objects.count()
    try:
        from apps.blueprint.models import Student as BlueprintStudent
        students_count = BlueprintStudent.objects.count()
    except Exception:
        students_count = 0
    try:
        from apps.blueprint.models import Program as BlueprintProgram
        programs_count = BlueprintProgram.objects.count()
    except Exception:
        programs_count = 0

    context = {'stats': {'user_count': user_count, 'students_count': students_count, 'programs_count': programs_count}}
    return render(request, 'dashboard/admin_dashboard.html', context)


# -------------------------
# Admin module CRUD (Students, Programs, Courses, Classes)
# -------------------------
from django import forms
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from apps.accounts.decorators import permission_required


def _get_blueprint_models():
    # Prefer `apps.academics` if available, fall back to `apps.blueprint` for compatibility
    try:
        from apps.academics.models import Student, Program, Course, Classroom
        return Student, Program, Course, Classroom
    except Exception:
        try:
            from apps.blueprint.models import Student, Program, Course, Classroom
            return Student, Program, Course, Classroom
        except Exception:
            return None, None, None, None


StudentModel, ProgramModel, CourseModel, ClassroomModel = _get_blueprint_models()


# Generic admin module placeholder views
@login_required
@permission_required('enrollment.manage')
def admin_enrollment(request):
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    # Build enrollment dashboard context
    students = StudentModel.objects.all() if StudentModel else []
    q = request.GET.get('q')
    program = request.GET.get('program')
    if q and StudentModel:
        students = students.filter(first_name__icontains=q) | students.filter(last_name__icontains=q) | students.filter(student_number__icontains=q)
    if program and StudentModel:
        try:
            students = students.filter(program__id=program)
        except Exception:
            pass
    total = students.count() if StudentModel else 0
    # recent enrollments (show last 10 by pk ordering as fallback)
    recent = students.order_by('-pk')[:10] if StudentModel else []
    # program and course choices
    programs = ProgramModel.objects.all() if ProgramModel else []
    courses = CourseModel.objects.all() if CourseModel else []

    # Handle enroll/un-enroll POST actions
    msg = None
    if request.method == 'POST':
        action = request.POST.get('action')
        student_pk = request.POST.get('student') or request.POST.get('student_pk')
        course_pk = request.POST.get('course') or request.POST.get('course_pk')
        stud = None
        course = None
        try:
            if StudentModel and student_pk:
                stud = StudentModel.objects.filter(pk=student_pk).first()
        except Exception:
            stud = None
        try:
            if CourseModel and course_pk:
                course = CourseModel.objects.filter(pk=course_pk).first()
        except Exception:
            course = None

        if action == 'enroll' and stud and course:
            # Try common relation patterns
            done = False
            try:
                stud.course_set.add(course)
                done = True
            except Exception:
                pass
            if not done:
                try:
                    stud.courses.add(course)
                    done = True
                except Exception:
                    pass
            if not done:
                try:
                    course.student_set.add(stud)
                    done = True
                except Exception:
                    pass
            msg = 'Enrolled' if done else 'Could not enroll (relation not found)'

        if action == 'remove' and stud and course:
            done = False
            try:
                stud.course_set.remove(course)
                done = True
            except Exception:
                pass
            if not done:
                try:
                    stud.courses.remove(course)
                    done = True
                except Exception:
                    pass
            if not done:
                try:
                    course.student_set.remove(stud)
                    done = True
                except Exception:
                    pass
            msg = 'Removed enrollment' if done else 'Could not remove enrollment (relation not found)'

    context = {'students': recent, 'total_students': total, 'programs': programs, 'courses': courses, 'message': msg}
    return render(request, 'admin/enrollment/index.html', context)


@login_required
@permission_required('enrollment.view')
def admin_enrollment_list(request):
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    q = request.GET.get('q')
    students_qs = StudentModel.objects.all() if StudentModel else []
    if q and StudentModel:
        students_qs = students_qs.filter(first_name__icontains=q) | students_qs.filter(last_name__icontains=q) | students_qs.filter(student_number__icontains=q)
    # pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(students_qs.order_by('last_name', 'first_name'), 25)
    try:
        students_page = paginator.page(page)
    except PageNotAnInteger:
        students_page = paginator.page(1)
    except EmptyPage:
        students_page = paginator.page(paginator.num_pages)
    return render(request, 'admin/enrollment/list.html', {'students_page': students_page, 'paginator': paginator, 'q': q})


@login_required
@permission_required('enrollment.manage')
def admin_enrollment_student(request, pk):
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    student = StudentModel.objects.filter(pk=pk).first() if StudentModel else None
    if not student:
        return redirect('admin_enrollment_list')
    courses = CourseModel.objects.all() if CourseModel else []
    msg = None
    if request.method == 'POST':
        action = request.POST.get('action')
        course_pk = request.POST.get('course')
        course = CourseModel.objects.filter(pk=course_pk).first() if CourseModel and course_pk else None
        if action == 'enroll' and course:
            done = False
            try:
                student.course_set.add(course)
                done = True
            except Exception:
                pass
            if not done:
                try:
                    student.courses.add(course)
                    done = True
                except Exception:
                    pass
            msg = 'Enrolled' if done else 'Could not enroll'
        if action == 'remove' and course:
            done = False
            try:
                student.course_set.remove(course)
                done = True
            except Exception:
                pass
            if not done:
                try:
                    student.courses.remove(course)
                    done = True
                except Exception:
                    pass
            msg = 'Removed enrollment' if done else 'Could not remove enrollment'

    # determine enrolled courses for display
    enrolled = []
    try:
        enrolled = list(student.course_set.all())
    except Exception:
        try:
            enrolled = list(student.courses.all())
        except Exception:
            enrolled = []
    return render(request, 'admin/enrollment/student_detail.html', {'student': student, 'courses': courses, 'enrolled': enrolled, 'message': msg})


@login_required
@permission_required('enrollment.view')
def admin_enrollment_course(request, pk):
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    course = CourseModel.objects.filter(pk=pk).first() if CourseModel else None
    if not course:
        return redirect('admin_enrollment_list')
    # students in course
    students = []
    try:
        students = list(course.student_set.all())
    except Exception:
        try:
            students = list(course.students.all())
        except Exception:
            students = []
    return render(request, 'admin/enrollment/course_detail.html', {'course': course, 'students': students})


@login_required
@permission_required('scheduling.manage')
def admin_scheduling(request):
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    # Scheduling context: show classrooms and courses
    classes_qs = ClassroomModel.objects.all() if ClassroomModel else []
    courses_qs = CourseModel.objects.all() if CourseModel else []
    q = request.GET.get('q')
    if q and ClassroomModel:
        classes_qs = classes_qs.filter(name__icontains=q)
    if q and CourseModel:
        courses_qs = courses_qs.filter(name__icontains=q) | courses_qs.filter(code__icontains=q)
    stats = {'classrooms': classes_qs.count() if ClassroomModel else 0, 'courses': courses_qs.count() if CourseModel else 0}
    # show first 20 upcoming (by pk fallback)
    classrooms = classes_qs.order_by('name')[:20] if ClassroomModel else []
    courses = courses_qs.order_by('name')[:20] if CourseModel else []
    context = {'classrooms': classrooms, 'courses': courses, 'stats': stats}
    return render(request, 'admin/scheduling/index.html', context)


@login_required
def admin_attendance(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/attendance/index.html', {})


@login_required
def admin_assessments(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/assessments/index.html', {})


@login_required
def admin_spr(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/spr/index.html', {})


@login_required
def admin_exams(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/exams/index.html', {})


@login_required
def admin_finance(request):
    # finance modules allowed to finance staff and admins
    if not has_any_role(request.user, FINANCE_ROLES):
        return redirect('dashboard')
    return render(request, 'admin/finance/index.html', {})


@login_required
def admin_requests(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/requests/index.html', {})


@login_required
def admin_transcripts(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/transcripts/index.html', {})


@login_required
def admin_reports(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/reports/index.html', {})


@login_required
def admin_notifications(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/notifications/index.html', {})


@login_required
def admin_permissions(request):
    # Only system admin or managing director can manage permissions
    if not has_any_role(request.user, ADMIN_ROLES):
        return redirect('dashboard')
    # placeholder: list all permissions and roles
    from apps.accounts.models import Permission, Role, RolePermission
    permissions = Permission.objects.all()[:200]
    roles = Role.objects.all()
    role_permissions = RolePermission.objects.all()[:200]
    return render(request, 'users/permissions.html', {'permissions': permissions, 'roles': roles, 'role_permissions': role_permissions})


@login_required
def admin_users(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/users/index.html', {})


class AdminUserCreateForm(forms.Form):
    first_name = forms.CharField(max_length=120, required=True)
    last_name = forms.CharField(max_length=120, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=30, required=False)
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    status = forms.CharField(max_length=50, required=False)


@login_required
def admin_user_list(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    User = get_user_model()
    q = request.GET.get('q')
    users_qs = User.objects.all().order_by('-created_at')
    if q:
        users_qs = users_qs.filter(email__icontains=q) | users_qs.filter(username__icontains=q)

    # pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(users_qs, 25)
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    return render(request, 'users/user_list.html', {'users_page': users_page, 'paginator': paginator, 'q': q})


@login_required
def admin_user_create(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            User = get_user_model()
            tenant = Tenant.objects.first()
            if tenant is None:
                tenant = Tenant.objects.create(name='System', slug='system')
            user = User.objects.create_user(email=data['email'], username=data['username'], password=data['password'], tenant=tenant)
            # create profile if possible
            try:
                from apps.accounts.models import UserProfile
                UserProfile.objects.create(user=user, first_name=data['first_name'], last_name=data['last_name'])
            except Exception:
                pass
            return redirect('admin_user_list')
    else:
        form = AdminUserCreateForm()
    return render(request, 'users/user_form.html', {'form': form})


@login_required
def admin_user_view(request, user_pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    User = get_user_model()
    user = get_object_or_404(User, pk=user_pk)
    return render(request, 'users/user_view.html', {'user_obj': user})


@login_required
def admin_user_edit(request, user_pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    User = get_user_model()
    user = get_object_or_404(User, pk=user_pk)
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.username = request.POST.get('username')
        user.phone = request.POST.get('phone')
        user.is_active = True if request.POST.get('is_active') == 'on' else False
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        user.save()
        # update profile
        try:
            profile = user.profile
            profile.first_name = request.POST.get('first_name')
            profile.last_name = request.POST.get('last_name')
            profile.save()
        except Exception:
            pass
        return redirect('admin_user_list')
    return render(request, 'users/user_form_edit.html', {'user_obj': user})


@login_required
@require_POST
def admin_user_deactivate(request, user_pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    User = get_user_model()
    user = get_object_or_404(User, pk=user_pk)
    # toggle active state
    user.is_active = False
    user.save()
    return redirect('admin_user_list')


class RoleAssignForm(forms.Form):
    role = forms.ChoiceField(choices=[])  # populated in view


@login_required
def admin_user_assign_role(request, user_pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    User = get_user_model()
    user = get_object_or_404(User, pk=user_pk)
    from apps.accounts.models import Role, UserRole
    roles = list(Role.objects.all())
    role_choices = [(r.id, r.name) for r in roles]
    if request.method == 'POST':
        form = RoleAssignForm(request.POST)
        form.fields['role'].choices = role_choices
        if form.is_valid():
            role_id = form.cleaned_data['role']
            role = get_object_or_404(Role, pk=role_id)
            # create assignment if not exists
            ur, created = UserRole.objects.get_or_create(user=user, role=role)
            # if role is student, attempt to link to StudentProfile if blueprint/student exists
            if role.name.lower() == 'student':
                try:
                    from apps.students.models import StudentProfile
                    # create profile only if missing
                    if not hasattr(user, 'student_profile'):
                        student_number = user.username or user.email.split('@')[0]
                        StudentProfile.objects.create(user=user, student_number=student_number, tenant=user.tenant)
                except Exception:
                    pass
            return redirect('admin_user_list')
    else:
        form = RoleAssignForm()
        form.fields['role'].choices = role_choices
    return render(request, 'users/assign_role.html', {'form': form, 'user_obj': user, 'roles': roles})


@login_required
def admin_roles_list(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    from apps.accounts.models import Role
    roles = Role.objects.all()
    return render(request, 'users/roles_list.html', {'roles': roles})


@login_required
def admin_role_create(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    from apps.accounts.models import Role
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        if name and code:
            Role.objects.create(name=name, code=code)
            return redirect('admin_roles_list')
    return render(request, 'users/role_form.html', {})


@login_required
def admin_role_permissions(request, role_pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    from apps.accounts.models import Role, Permission, RolePermission
    role = Role.objects.filter(pk=role_pk).first()
    if not role:
        return redirect('admin_roles_list')
    permissions = Permission.objects.all().order_by('module', 'action')
    assigned = set(RolePermission.objects.filter(role=role).values_list('permission_id', flat=True))
    if request.method == 'POST':
        action = request.POST.get('action')
        perm_id = request.POST.get('permission')
        if action == 'assign' and perm_id:
            p = Permission.objects.filter(pk=perm_id).first()
            if p:
                RolePermission.objects.get_or_create(role=role, permission=p)
        if action == 'remove' and perm_id:
            RolePermission.objects.filter(role=role, permission_id=perm_id).delete()
        return redirect('admin_role_permissions', role_pk=role_pk)

    return render(request, 'users/role_permissions.html', {'role': role, 'permissions': permissions, 'assigned': assigned})


@login_required
def admin_settings(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    return render(request, 'admin/settings/index.html', {})


def _is_admin_user(user):
    try:
        from apps.accounts.utils import get_user_roles
        role_objs = get_user_roles(user)
        role_names = set(r.name.lower() for r in role_objs if r and getattr(r, 'name', None))
    except Exception:
        role_names = set()
    try:
        group_names = set(g.name.lower() for g in user.groups.all())
    except Exception:
        group_names = set()
    return bool(user and (user.is_staff or user.is_superuser or 'admin' in group_names or 'admin' in role_names))


def _get_user_role_names(u):
    names = set()
    try:
        from apps.accounts.utils import get_user_roles
        for r in get_user_roles(u):
            try:
                names.add(r.name.lower())
            except Exception:
                pass
    except Exception:
        pass
    try:
        names.update(g.name.lower() for g in u.groups.all())
    except Exception:
        pass
    return names


ADMIN_ROLES = set(['system administrator', 'managing director'])
ACADEMIC_ROLES = set(['training manager', 'registrar', 'instructor']) | ADMIN_ROLES
FINANCE_ROLES = set(['accountant', 'cashier']) | ADMIN_ROLES
MARKETING_ROLES = set(['marketing manager']) | ADMIN_ROLES
RECEPTION_ROLES = set(['receptionist']) | ADMIN_ROLES


from apps.accounts.utils import has_any_role


class StudentForm(forms.ModelForm):
    class Meta:
        model = StudentModel
        fields = ['student_number', 'first_name', 'last_name', 'email', 'program', 'intake_batch', 'status'] if StudentModel else []


class ProgramForm(forms.ModelForm):
    class Meta:
        model = ProgramModel
        fields = ['code', 'name', 'duration_months'] if ProgramModel else []


class CourseForm(forms.ModelForm):
    class Meta:
        model = CourseModel
        fields = ['code', 'name', 'program'] if CourseModel else []


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = ClassroomModel
        fields = ['name', 'capacity'] if ClassroomModel else []


@login_required
@permission_required('students.view')
def admin_students_list(request):
    # allow academic roles and admins
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    students = StudentModel.objects.all() if StudentModel else []
    q = request.GET.get('q')
    if q and StudentModel:
        students = students.filter(first_name__icontains=q) | students.filter(last_name__icontains=q) | students.filter(student_number__icontains=q)
    stats = {'total': students.count() if StudentModel else 0, 'active': students.filter(status='active').count() if StudentModel else 0}
    return render(request, 'admin/students/student_list.html', {'students': students, 'stats': stats})


@login_required
def admin_student_add(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            obj = form.save()
            return redirect('admin_students_list')
    else:
        form = StudentForm()
    return render(request, 'admin/students/student_form.html', {'form': form})


@login_required
def change_password(request):
    """Allow a logged-in user to change their password from the site."""
    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'accounts/change_password.html', {})
        if not new or new != confirm:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'accounts/change_password.html', {})
        request.user.set_password(new)
        request.user.save()
        messages.success(request, 'Password updated. Please login again.')
        return redirect('login')
    return render(request, 'accounts/change_password.html', {})


@login_required
def admin_student_edit(request, pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    obj = StudentModel.objects.filter(pk=pk).first() if StudentModel else None
    if not obj:
        return redirect('admin_students_list')
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('admin_students_list')
    else:
        form = StudentForm(instance=obj)
    return render(request, 'admin/students/student_form.html', {'form': form, 'student': obj})


@login_required
def admin_student_delete(request, pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    obj = StudentModel.objects.filter(pk=pk).first() if StudentModel else None
    if not obj:
        return redirect('admin_students_list')
    if request.method == 'POST':
        obj.delete()
        return redirect('admin_students_list')
    return render(request, 'admin/students/student_confirm_delete.html', {'student': obj})


@login_required
def admin_student_detail(request, pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    obj = StudentModel.objects.filter(pk=pk).first() if StudentModel else None
    if not obj:
        return redirect('admin_students_list')
    # basic profile context
    context = {'student': obj}
    return render(request, 'admin/students/student_detail.html', context)


@login_required
@permission_required('programs.view')
def admin_programs_list(request):
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    programs = ProgramModel.objects.all() if ProgramModel else []
    q = request.GET.get('q')
    if q and ProgramModel:
        programs = programs.filter(name__icontains=q) | programs.filter(code__icontains=q)
    stats = {'total': programs.count() if ProgramModel else 0}
    return render(request, 'admin/programs/program_list.html', {'programs': programs, 'stats': stats})


@login_required
def admin_program_add(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_programs_list')
    else:
        form = ProgramForm()
    return render(request, 'admin/programs/program_form.html', {'form': form})


@login_required
def admin_program_edit(request, pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    obj = ProgramModel.objects.filter(pk=pk).first() if ProgramModel else None
    if not obj:
        return redirect('admin_programs_list')
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('admin_programs_list')
    else:
        form = ProgramForm(instance=obj)
    return render(request, 'admin/programs/program_form.html', {'form': form, 'program': obj})


@login_required
def admin_program_delete(request, pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    obj = ProgramModel.objects.filter(pk=pk).first() if ProgramModel else None
    if not obj:
        return redirect('admin_programs_list')
    if request.method == 'POST':
        obj.delete()
        return redirect('admin_programs_list')
    return render(request, 'admin/programs/program_confirm_delete.html', {'program': obj})


@login_required
@permission_required('courses.view')
def admin_courses_list(request):
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    courses = CourseModel.objects.all() if CourseModel else []
    stats = {'total': courses.count() if CourseModel else 0}
    return render(request, 'admin/courses/course_list.html', {'courses': courses, 'stats': stats})


@login_required
def admin_course_add(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_courses_list')
    else:
        form = CourseForm()
    return render(request, 'admin/courses/course_form.html', {'form': form})


@login_required
def admin_course_delete(request, pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    obj = CourseModel.objects.filter(pk=pk).first() if CourseModel else None
    if not obj:
        return redirect('admin_courses_list')
    if request.method == 'POST':
        obj.delete()
        return redirect('admin_courses_list')
    return render(request, 'admin/courses/course_confirm_delete.html', {'course': obj})


@login_required
@permission_required('classes.view')
def admin_classes_list(request):
    if not has_any_role(request.user, ACADEMIC_ROLES):
        return redirect('dashboard')
    classes = ClassroomModel.objects.all() if ClassroomModel else []
    stats = {'total': classes.count() if ClassroomModel else 0}
    return render(request, 'admin/classes/class_list.html', {'classes': classes, 'stats': stats})


@login_required
def admin_class_add(request):
    if not _is_admin_user(request.user):
        return redirect('login')
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_classes_list')
    else:
        form = ClassroomForm()
    return render(request, 'admin/classes/class_form.html', {'form': form})


@login_required
def admin_class_edit(request, pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    obj = ClassroomModel.objects.filter(pk=pk).first() if ClassroomModel else None
    if not obj:
        return redirect('admin_classes_list')
    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('admin_classes_list')
    else:
        form = ClassroomForm(instance=obj)
    return render(request, 'admin/classes/class_form.html', {'form': form, 'classroom': obj})


@login_required
def admin_class_delete(request, pk):
    if not _is_admin_user(request.user):
        return redirect('login')
    obj = ClassroomModel.objects.filter(pk=pk).first() if ClassroomModel else None
    if not obj:
        return redirect('admin_classes_list')
    if request.method == 'POST':
        obj.delete()
        return redirect('admin_classes_list')
    return render(request, 'admin/classes/class_confirm_delete.html', {'classroom': obj})


# -------------------------
# Personal Access Token management (web UI)
# -------------------------

@login_required
@ensure_csrf_cookie
def tokens_view(request):
    """Web UI for managing personal access tokens."""
    import secrets as _secrets
    import hashlib as _hashlib
    import datetime
    from apps.accounts.models import ApiKey

    new_token = None
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            name = request.POST.get('name', '').strip()
            days_str = request.POST.get('expires_in_days', '').strip()
            if not name:
                error = 'Token name is required.'
            else:
                token = _secrets.token_urlsafe(32)
                prefix = token[:8]
                key_hash = _hashlib.sha256(token.encode()).hexdigest()
                expires_at = None
                if days_str:
                    try:
                        expires_at = timezone.now() + datetime.timedelta(days=int(days_str))
                    except ValueError:
                        pass
                ApiKey.objects.create(
                    tenant=request.user.tenant,
                    user=request.user,
                    name=name,
                    key_prefix=prefix,
                    key_hash=key_hash,
                    expires_at=expires_at,
                    is_active=True,
                )
                new_token = token

        elif action == 'revoke':
            token_id = request.POST.get('token_id')
            ApiKey.objects.filter(pk=token_id, user=request.user).update(
                is_active=False, key_hash='REVOKED'
            )

    tokens = ApiKey.objects.filter(user=request.user, is_active=True).order_by('-created_at')
    return render(request, 'accounts/tokens.html', {
        'tokens': tokens,
        'new_token': new_token,
        'error': error,
    })
