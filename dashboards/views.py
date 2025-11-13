from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from courses.models import Course, Enrollment, LessonProgress
from session_logs.services import get_student_session_logs, get_instructor_session_logs
from .models import (
    TechBlog, CoreSubject, TrendingSkill, LearningPath,
    SuccessStory, DailyQuiz, FreeResource, Webinar, PlacementOpportunity
)


@login_required
def dashboard_redirect(request):
    """
    Redirect to appropriate dashboard based on user role
    Students go to student dashboard
    Instructors go to instructor dashboard
    """
    if request.user.profile.role == 'student':
        return redirect('dashboards:student')
    else:
        return redirect('dashboards:instructor')


@login_required
def student_dashboard(request):
    """
    Student dashboard view
    Shows enrolled courses, progress, and recent sessions
    """
    # Ensure only students can access
    if request.user.profile.role != 'student':
        return redirect('dashboards:instructor')
    
    # Get enrolled courses
    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related('course').order_by('-enrolled_at')
    
    # Calculate progress for each enrollment
    for enrollment in enrollments:
        total_lessons = enrollment.course.lessons.count()
        completed = LessonProgress.objects.filter(
            student=request.user,
            lesson__course=enrollment.course,
            completed=True
        ).count()
        
        if total_lessons > 0:
            enrollment.progress_percentage = int((completed / total_lessons) * 100)
        else:
            enrollment.progress_percentage = 0
    
    # Get lesson progress statistics
    completed_lessons = LessonProgress.objects.filter(
        student=request.user,
        completed=True
    ).count()
    
    total_lessons_enrolled = 0
    for enrollment in enrollments:
        total_lessons_enrolled += enrollment.course.lessons.count()
    
    # Get session logs (last 5)
    try:
        session_logs = get_student_session_logs(request.user.id)[:5]
    except:
        session_logs = []
    
    # Calculate overall progress
    if total_lessons_enrolled > 0:
        overall_progress = int((completed_lessons / total_lessons_enrolled) * 100)
    else:
        overall_progress = 0
    
    context = {
        'enrollments': enrollments,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons_enrolled,
        'overall_progress': overall_progress,
        'session_logs': session_logs,
        'total_enrollments': enrollments.count(),
        # Home page sections
        'blogs': TechBlog.objects.all()[:6],
        'core_subjects': CoreSubject.objects.all()[:6],
        'trending_skills': TrendingSkill.objects.all()[:6],
        'learning_paths': LearningPath.objects.all()[:6],
        'success_stories': SuccessStory.objects.all()[:3],
        'daily_quiz': DailyQuiz.objects.filter(date=timezone.now().date()).first(),
        'free_resources': FreeResource.objects.all()[:6],
        'upcoming_webinars': Webinar.objects.filter(date__gte=timezone.now())[:4],
        'placement_opportunities': PlacementOpportunity.objects.all()[:6],
    }
    
    return render(request, 'dashboards/student_dashboard.html', context)


@login_required
def instructor_dashboard(request):
    """
    Instructor dashboard view
    Shows created courses, students, and session history
    """
    # Ensure only instructors can access
    if request.user.profile.role != 'instructor':
        return redirect('dashboards:student')
    
    # Get instructor's courses
    courses = Course.objects.filter(
        instructor=request.user
    ).order_by('-created_at')
    
    # Get total students across all courses
    total_students = Enrollment.objects.filter(
        course__instructor=request.user
    ).count()
    
    # Get total lessons created
    total_lessons = 0
    for course in courses:
        total_lessons += course.lessons.count()
    
    # Get session logs (last 5)
    try:
        session_logs = get_instructor_session_logs(request.user.id)[:5]
    except:
        session_logs = []
    
    # Get recent enrollments
    recent_enrollments = Enrollment.objects.filter(
        course__instructor=request.user
    ).select_related('student', 'course').order_by('-enrolled_at')[:5]
    
    context = {
        'courses': courses,
        'total_courses': courses.count(),
        'total_students': total_students,
        'total_lessons': total_lessons,
        'session_logs': session_logs,
        'recent_enrollments': recent_enrollments,
        # Home page sections
        'blogs': TechBlog.objects.all()[:6],
        'core_subjects': CoreSubject.objects.all()[:6],
        'trending_skills': TrendingSkill.objects.all()[:6],
        'learning_paths': LearningPath.objects.all()[:6],
        'success_stories': SuccessStory.objects.all()[:3],
        'daily_quiz': DailyQuiz.objects.filter(date=timezone.now().date()).first(),
        'free_resources': FreeResource.objects.all()[:6],
        'upcoming_webinars': Webinar.objects.filter(date__gte=timezone.now())[:4],
        'placement_opportunities': PlacementOpportunity.objects.all()[:6],
    }
    
    return render(request, 'dashboards/instructor_dashboard.html', context)


def home_page(request):
    """
    Home page view with all content sections
    """
    context = {
        'blogs': TechBlog.objects.all()[:6],
        'core_subjects': CoreSubject.objects.all()[:6],
        'trending_skills': TrendingSkill.objects.all()[:6],
        'learning_paths': LearningPath.objects.all()[:6],
        'success_stories': SuccessStory.objects.all()[:3],
        'daily_quiz': DailyQuiz.objects.filter(date=timezone.now().date()).first(),
        'free_resources': FreeResource.objects.all()[:6],
        'upcoming_webinars': Webinar.objects.filter(date__gte=timezone.now())[:4],
        'placement_opportunities': PlacementOpportunity.objects.all()[:6],
    }
    return render(request, 'home.html', context)


# Resource Pages
def blogs_page(request):
    """View all tech blogs"""
    blogs = TechBlog.objects.all().order_by('-published_date')
    context = {'blogs': blogs, 'title': 'Recent Tech Blogs'}
    return render(request, 'dashboards/blogs.html', context)


def subjects_page(request):
    """View all core subjects"""
    subjects = CoreSubject.objects.all()
    context = {'subjects': subjects, 'title': 'Learn for Interviews'}
    return render(request, 'dashboards/subjects.html', context)


def skills_page(request):
    """View all trending skills"""
    skills = TrendingSkill.objects.all()
    context = {'skills': skills, 'title': 'Trending Skills'}
    return render(request, 'dashboards/skills.html', context)


def paths_page(request):
    """View all learning paths"""
    paths = LearningPath.objects.all()
    context = {'paths': paths, 'title': 'Learning Paths'}
    return render(request, 'dashboards/paths.html', context)


def stories_page(request):
    """View all success stories"""
    stories = SuccessStory.objects.all()
    context = {'stories': stories, 'title': 'Student Success Stories'}
    return render(request, 'dashboards/stories.html', context)


def resources_page(request):
    """View all free resources"""
    resources = FreeResource.objects.all()
    context = {'resources': resources, 'title': 'Free Resources'}
    return render(request, 'dashboards/resources.html', context)


def webinars_page(request):
    """View all upcoming webinars"""
    webinars = Webinar.objects.filter(date__gte=timezone.now()).order_by('date')
    context = {'webinars': webinars, 'title': 'Upcoming Webinars'}
    return render(request, 'dashboards/webinars.html', context)


def placements_page(request):
    """View all placement opportunities"""
    placements = PlacementOpportunity.objects.all()
    context = {'placements': placements, 'title': 'Placement Corner'}
    return render(request, 'dashboards/placements.html', context)