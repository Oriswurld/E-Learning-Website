# courses/admin.py
from django.contrib import admin
from .models import Course, Lesson, Quiz, Assignment, Submission, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'created_at']
    list_filter = ['instructor', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['question', 'lesson']
    list_filter = ['lesson']
    search_fields = ['question']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date']
    list_filter = ['course', 'due_date']
    search_fields = ['title']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'grade', 'submitted_at']
    list_filter = ['assignment', 'student', 'submitted_at']
    search_fields = ['student__username']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'progress', 'enrolled_at']
    list_filter = ['course', 'enrolled_at']
    search_fields = ['student__username', 'course__title']

# Register your models here.
