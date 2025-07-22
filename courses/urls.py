# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('catalog/', views.course_catalog, name='course_catalog'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('lesson/<int:pk>/', views.lesson_page, name='lesson_page'),
    path('assignment/<int:pk>/', views.assignment_page, name='assignment_page'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('admin/panel/', views.admin_panel, name='admin_panel'),
    path('course/create/', views.course_create, name='course_create'),
    path('course/<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('assignment/create/<int:course_id>/', views.assignment_create, name='assignment_create'),
    path('submission/create/<int:assignment_id>/', views.submission_create, name='submission_create'),
    path('faq/', views.faq, name='faq'),
    path('about/', views.about, name='about'),
]