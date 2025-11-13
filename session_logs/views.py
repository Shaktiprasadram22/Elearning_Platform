from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services import (
    create_session_log, 
    end_session_log, 
    get_student_session_logs, 
    get_instructor_session_logs
)
import json


@login_required
def create_log_view(request):
    """
    API endpoint to create a new session log
    Called when a WebRTC session starts
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            log_id = create_session_log(
                student_id=data.get('student_id'),
                instructor_id=data.get('instructor_id'),
                course_id=data.get('course_id'),
                chat_log=data.get('chat_log', [])
            )
            
            return JsonResponse({
                'status': 'success',
                'log_id': log_id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'POST request required'
    }, status=400)


@login_required
def end_log_view(request, log_id):
    """
    API endpoint to end a session log
    Called when WebRTC session ends
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chat_log = data.get('chat_log', [])
            
            end_session_log(log_id, chat_log)
            
            return JsonResponse({
                'status': 'success'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'POST request required'
    }, status=400)


@login_required
def my_logs_view(request):
    """
    View to display session logs for current user
    Shows different logs based on user role (student/instructor)
    """
    if request.user.profile.role == 'student':
        logs = get_student_session_logs(request.user.id)
    else:
        logs = get_instructor_session_logs(request.user.id)
    
    return render(request, 'session_logs/my_logs.html', {
        'logs': logs,
        'user_role': request.user.profile.role
    })
