# courses/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .models import Course, Lesson, Assignment, Submission, Enrollment
from .forms import CourseForm, AssignmentForm, SubmissionForm, LessonForm

# Create your views here.

def homepage(request):
    courses = Course.objects.all()
    return render(request, 'courses/homepage.html', {'courses': courses})

def course_catalog(request):
    courses = Course.objects.all()
    category = request.GET.get('category')
    if category:
        courses = courses.filter(category=category)
    return render(request, 'courses/course_catalog.html', {'courses': courses})

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrolled = Enrollment.objects.filter(course=course, student=request.user).exists() if request.user.is_authenticated else False
    return render(request, 'courses/course_detail.html', {'course': course, 'enrolled': enrolled})

@login_required
def lesson_page(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    quizzes = lesson.quizzes.all()
    return render(request, 'courses/lesson_page.html', {'lesson': lesson, 'quizzes': quizzes})

@login_required
def assignment_page(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, 'Submission successful!')
            return redirect('assignment_page', pk=pk)
    else:
        form = SubmissionForm(instance=submission)
    return render(request, 'courses/assignment_page.html', {'assignment': assignment, 'submission': submission, 'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        selected_role = request.POST.get('role')
        user = authenticate(request, username=username, password=password)

        if user:
            if selected_role == 'student' and not user.groups.filter(name='Students').exists():
                messages.error(request, 'You are not registered as a student.')
                return redirect('login')
            elif selected_role == 'instructor' and not user.groups.filter(name='Instructors').exists():
                messages.error(request, 'You are not registered as an instructor.')
                return redirect('login')
            login(request, user)
            if user.groups.filter(name='Admins').exists():
                return redirect('admin_panel')
            elif user.groups.filter(name='Instructors').exists():
                return redirect('instructor_dashboard')
            else:
                return redirect('student_dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'courses/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['password1']
        role = request.POST.get('role', 'student') 

        if not password or not confirm_password:
            messages.error(request, 'Both password fields are required.')
            return redirect('register')


        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return render(request, 'courses/register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'courses/register.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return render(request, 'courses/register.html')
        
        user = User.objects.create_user(username=username, password=password)
        group = Group.objects.get(name='Students' if role == 'student' else 'Instructors')
        user.groups.add(group)
        user.save()
        login(request, user)
        return redirect('student_dashboard' if role == 'student' else 'instructor_dashboard')
    return render(request, 'courses/register.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('homepage')

@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user).prefetch_related('course__assignments')
    for enrollment in enrollments:
        for assignment in enrollment.course.assignments.all():
            assignment.is_submitted = Submission.objects.filter(
                assignment=assignment, student=request.user
            ).exists()
    return render(request, 'courses/student_dashboard.html', {'enrollments': enrollments})

@login_required
def instructor_dashboard(request):
    if not request.user.groups.filter(name='Instructors').exists():
        messages.error(request, 'You do not have permission to access the instructor dashboard.')
        return redirect('homepage')
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/instructor_dashboard.html', {'courses': courses})

@login_required
@permission_required('courses.add_course', raise_exception=True)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()
    return render(request, 'courses/course_create.html', {'form': form})

@login_required
@permission_required('courses.manage_admin_panel', raise_exception=True)
def admin_panel(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admins').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('homepage')
    users = User.objects.all()
    courses = Course.objects.all()
    return render(request, 'courses/admin_panel.html', {'users': users, 'courses': courses})

@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.get_or_create(course=course, student=request.user)
    messages.success(request, f'You have successfully enrolled in {course.title}!')
    return redirect('course_detail', pk=pk)

@login_required
def assignment_create(request, course_id):
    if not request.user.groups.filter(name='Instructors').exists():
        messages.error(request, 'You do not have permission to create assignments.')
        return redirect('homepage')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('course_detail', pk=course.id)
    else:
        form = AssignmentForm()
    return render(request, 'courses/assignment_create.html', {'form': form, 'course': course})

@login_required
def submission_create(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not Enrollment.objects.filter(student=request.user, course=assignment.course).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('student_dashboard')
    if Submission.objects.filter(assignment=assignment, student=request.user).exists():
        messages.error(request, 'You have already submitted this assignment.')
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.assignment = assignment
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('student_dashboard')
    else:
        form = SubmissionForm()
    return render(request, 'courses/submission_create.html', {'form': form, 'assignment': assignment})

def faq(request):
    return render(request, 'courses/faq.html')

def about(request):
    return render(request, 'courses/about.html')