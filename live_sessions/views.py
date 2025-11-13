from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from courses.models import Course, Lesson
from .models import DoubtSession
from session_logs.mongo_models import SessionLog
import uuid
import json


@login_required
def request_session_view(request, lesson_id):
    """
    Student requests 1-to-1 doubt session with instructor
    Generates unique room name for WebRTC session
    """
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can request doubt sessions')
        return redirect('courses:lesson_watch', lesson_id=lesson_id)
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    # Generate unique room name
    room_name = f"doubt_{request.user.id}_{course.instructor.id}_{uuid.uuid4().hex[:8]}"
    
    # Create doubt session record
    doubt_session = DoubtSession.objects.create(
        student=request.user,
        course=course,
        lesson=lesson,
        room_name=room_name,
        status='pending'
    )
    
    messages.success(request, 'Doubt session request sent to instructor!')
    return redirect('live_sessions:room', room_name=room_name)


@login_required
def session_room_view(request, room_name):
    """
    WebRTC video call room
    Handles both student and instructor joining the same room
    """
    doubt_session = get_object_or_404(DoubtSession, room_name=room_name)
    
    # Check authorization
    is_student = request.user == doubt_session.student
    is_instructor = request.user == doubt_session.instructor or (
        request.user == doubt_session.course.instructor and doubt_session.instructor is None
    )
    
    if not (is_student or is_instructor):
        messages.error(request, 'You are not authorized to join this session')
        return redirect('dashboards:redirect')
    
    # If instructor is joining for first time, update session
    if is_instructor and doubt_session.instructor is None:
        doubt_session.instructor = request.user
        doubt_session.status = 'active'
        doubt_session.started_at = timezone.now()
        doubt_session.save()
        
        # Log session start in MongoDB
        try:
            SessionLog.create_log(
                session_id=doubt_session.id,
                student_id=doubt_session.student.id,
                instructor_id=request.user.id,
                course_id=doubt_session.course.id,
                start_time=timezone.now()
            )
        except Exception as e:
            print(f"MongoDB log creation error: {e}")
    
    return render(request, 'live_sessions/doubt_session.html', {
        'room_name': room_name,
        'user': request.user,
        'doubt_session': doubt_session,
        'is_student': is_student,
        'is_instructor': is_instructor,
        'other_user': doubt_session.instructor if is_student else doubt_session.student
    })


@login_required
@require_http_methods(["GET"])
def instructor_dashboard_view(request):
    """
    Instructor dashboard showing pending doubt session requests
    """
    if request.user.profile.role != 'instructor':
        messages.error(request, 'Only instructors can access this page')
        return redirect('dashboards:redirect')
    
    # Get pending sessions
    pending_sessions = DoubtSession.objects.filter(
        course__instructor=request.user,
        status='pending'
    ).select_related('student', 'course', 'lesson')
    
    # Get active sessions
    active_sessions = DoubtSession.objects.filter(
        course__instructor=request.user,
        status='active'
    ).select_related('student', 'course', 'lesson')
    
    # Get completed sessions
    completed_sessions = DoubtSession.objects.filter(
        course__instructor=request.user,
        status='completed'
    ).select_related('student', 'course', 'lesson')[:10]
    
    return render(request, 'live_sessions/instructor_dashboard.html', {
        'pending_sessions': pending_sessions,
        'active_sessions': active_sessions,
        'completed_sessions': completed_sessions
    })


@login_required
@require_http_methods(["GET"])
def student_dashboard_view(request):
    """
    Student dashboard showing doubt session history
    """
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can access this page')
        return redirect('dashboards:redirect')
    
    # Get all sessions for student
    all_sessions = DoubtSession.objects.filter(
        student=request.user
    ).select_related('instructor', 'course', 'lesson')
    
    pending_sessions = all_sessions.filter(status='pending')
    active_sessions = all_sessions.filter(status='active')
    completed_sessions = all_sessions.filter(status='completed')
    
    return render(request, 'live_sessions/student_dashboard.html', {
        'pending_sessions': pending_sessions,
        'active_sessions': active_sessions,
        'completed_sessions': completed_sessions,
        'all_sessions': all_sessions
    })


@login_required
@require_http_methods(["POST"])
def accept_session_view(request, session_id):
    """
    Instructor accepts a pending doubt session request
    """
    if request.user.profile.role != 'instructor':
        return JsonResponse({'error': 'Only instructors can accept sessions'}, status=403)
    
    doubt_session = get_object_or_404(DoubtSession, id=session_id)
    
    if doubt_session.course.instructor != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    doubt_session.instructor = request.user
    doubt_session.status = 'active'
    doubt_session.started_at = timezone.now()
    doubt_session.save()
    
    return JsonResponse({
        'success': True,
        'room_name': doubt_session.room_name,
        'redirect_url': f'/live-sessions/room/{doubt_session.room_name}/'
    })


@login_required
@require_http_methods(["POST"])
def reject_session_view(request, session_id):
    """
    Instructor rejects a pending doubt session request
    """
    if request.user.profile.role != 'instructor':
        return JsonResponse({'error': 'Only instructors can reject sessions'}, status=403)
    
    doubt_session = get_object_or_404(DoubtSession, id=session_id)
    
    if doubt_session.course.instructor != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    doubt_session.status = 'rejected'
    doubt_session.save()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def end_session_view(request, session_id):
    """
    End a doubt session
    """
    print(f"=== END SESSION CALLED ===")
    print(f"Session ID: {session_id}")
    print(f"User: {request.user}")
    print(f"Method: {request.method}")
    
    try:
        # Get the session
        doubt_session = get_object_or_404(DoubtSession, id=session_id)
        print(f"Session found: {doubt_session}")
        print(f"Session status: {doubt_session.status}")
        print(f"Session student: {doubt_session.student}")
        print(f"Session instructor: {doubt_session.instructor}")
        
        # Check authorization - student can always end, instructor if assigned
        is_student = request.user == doubt_session.student
        is_instructor = (
            request.user == doubt_session.course.instructor or 
            (doubt_session.instructor and request.user == doubt_session.instructor)
        )
        
        print(f"Is student: {is_student}")
        print(f"Is instructor: {is_instructor}")
        
        if not (is_student or is_instructor):
            print("AUTHORIZATION FAILED")
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # End session if not already completed
        if doubt_session.status != 'completed':
            print("Setting session to completed...")
            doubt_session.status = 'completed'
            doubt_session.ended_at = timezone.now()
            
            # Calculate duration
            if doubt_session.started_at:
                duration = (doubt_session.ended_at - doubt_session.started_at).total_seconds() / 60
                doubt_session.duration_minutes = int(duration)
                print(f"Duration calculated: {doubt_session.duration_minutes} minutes")
            else:
                print("No started_at, using requested_at")
                # If not started, set started_at to requested_at
                doubt_session.started_at = doubt_session.requested_at
                duration = (doubt_session.ended_at - doubt_session.started_at).total_seconds() / 60
                doubt_session.duration_minutes = int(duration)
            
            print("Saving session...")
            doubt_session.save()
            print("Session saved successfully!")
            
            # Update MongoDB log only if session was actually started (has instructor)
            if doubt_session.instructor:
                print("Updating MongoDB log...")
                try:
                    SessionLog.update_log(
                        log_id=str(doubt_session.id),
                        end_time=timezone.now(),
                        chat_transcript=[]
                    )
                    print("MongoDB log updated successfully")
                except Exception as e:
                    # Log the error but don't fail the request
                    print(f"MongoDB log error (non-critical): {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("No instructor assigned, skipping MongoDB update")
        else:
            print("Session already completed")
        
        print("Returning success response")
        return JsonResponse({'success': True})
        
    except DoubtSession.DoesNotExist:
        print(f"ERROR: Session {session_id} not found")
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        print(f"CRITICAL ERROR ending session: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Failed to end session: {str(e)}'}, status=500)