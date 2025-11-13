from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Course, Lesson, Enrollment, LessonProgress


@login_required
def course_list_view(request):
    """
    Display all available courses
    Shows enrollment status for students
    """
    courses = Course.objects.all()
    enrolled_courses = []
    
    if request.user.profile.role == 'student':
        enrolled_courses = Enrollment.objects.filter(
            student=request.user
        ).values_list('course_id', flat=True)
    
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'enrolled_courses': enrolled_courses
    })


@login_required
def course_detail_view(request, course_id):
    """
    Display detailed course information
    Shows lessons and enrollment status
    """
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    is_enrolled = False
    enrollment = None
    
    if request.user.profile.role == 'student':
        try:
            enrollment = Enrollment.objects.get(
                student=request.user, 
                course=course
            )
            is_enrolled = True
        except Enrollment.DoesNotExist:
            pass
    
    is_instructor = course.instructor == request.user
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
        'enrollment': enrollment
    })


@login_required
def course_create_view(request):
    """
    Create a new course (instructors only)
    """
    if request.user.profile.role != 'instructor':
        messages.error(request, 'Only instructors can create courses')
        return redirect('courses:list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        price = request.POST.get('price')
        thumbnail = request.FILES.get('thumbnail')
        
        course = Course.objects.create(
            instructor=request.user,
            title=title,
            description=description,
            category=category,
            price=price,
            thumbnail=thumbnail
        )
        
        messages.success(request, 'Course created successfully!')
        return redirect('courses:detail', course_id=course.id)
    
    return render(request, 'courses/course_create.html', {
        'categories': Course.CATEGORY_CHOICES
    })


@login_required
def lesson_create_view(request, course_id):
    """
    Add lesson to course (instructors only)
    """
    course = get_object_or_404(Course, id=course_id)
    
    if course.instructor != request.user:
        messages.error(
            request, 
            'You are not authorized to add lessons to this course'
        )
        return redirect('courses:detail', course_id=course_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file = request.FILES.get('video_file')
        pdf_file = request.FILES.get('pdf_file')
        duration = request.POST.get('duration', 0)
        
        lesson = Lesson.objects.create(
            course=course,
            title=title,
            description=description,
            video_file=video_file,
            pdf_file=pdf_file,
            duration=duration,
            order=course.lessons.count() + 1
        )
        
        messages.success(request, 'Lesson added successfully!')
        return redirect('courses:detail', course_id=course_id)
    
    return render(request, 'courses/lesson_create.html', {'course': course})


@login_required
def enroll_course_view(request, course_id):
    """
    Enroll student in course (dummy payment)
    """
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can enroll in courses')
        return redirect('courses:detail', course_id=course_id)
    
    course = get_object_or_404(Course, id=course_id)
    
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )
    
    if created:
        messages.success(
            request, 
            f'Successfully enrolled in {course.title}!'
        )
    else:
        messages.info(request, 'You are already enrolled in this course')
    
    return redirect('courses:detail', course_id=course_id)


@login_required
def lesson_watch_view(request, lesson_id):
    """
    Watch lesson video
    Tracks lesson progress for students
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    # Check if student is enrolled
    if request.user.profile.role == 'student':
        is_enrolled = Enrollment.objects.filter(
            student=request.user, 
            course=course
        ).exists()
        if not is_enrolled:
            messages.error(request, 'You must enroll in this course first')
            return redirect('courses:detail', course_id=course.id)
    
    # Get or create progress
    progress = None
    if request.user.profile.role == 'student':
        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )
    
    all_lessons = course.lessons.all()
    
    return render(request, 'courses/lesson_watch.html', {
        'lesson': lesson,
        'course': course,
        'all_lessons': all_lessons,
        'progress': progress
    })


@login_required
def mark_lesson_complete(request, lesson_id):
    """
    Mark lesson as completed
    """
    if request.user.profile.role != 'student':
        return redirect('courses:lesson_watch', lesson_id=lesson_id)
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )
    
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()
    
    messages.success(request, 'Lesson marked as completed!')
    return redirect('courses:lesson_watch', lesson_id=lesson_id)
