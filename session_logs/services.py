from datetime import datetime
from .mongo_models import SessionLog
from django.contrib.auth.models import User
from courses.models import Course


def create_session_log(student_id, instructor_id, course_id, chat_log=None):
    """
    Create a new session log in MongoDB
    
    Args:
        student_id: ID of the student user
        instructor_id: ID of the instructor user
        course_id: ID of the course
        chat_log: Optional list of initial chat messages
    
    Returns:
        str: MongoDB document ID
    """
    start_time = datetime.now()
    
    log_id = SessionLog.create_log(
        student_id=student_id,
        instructor_id=instructor_id,
        course_id=course_id,
        start_time=start_time,
        chat_transcript=chat_log or []
    )
    
    return log_id


def end_session_log(log_id, chat_log):
    """
    Update session log with end time and final chat transcript
    
    Args:
        log_id: MongoDB document ID
        chat_log: Complete list of chat messages
    """
    end_time = datetime.now()
    SessionLog.update_log(log_id, end_time, chat_log)


def get_student_session_logs(student_id):
    """
    Get all session logs for a student with enriched data
    
    Args:
        student_id: ID of the student user
    
    Returns:
        list: Enriched session logs with user and course info
    """
    logs = SessionLog.get_logs_by_student(student_id)
    return enrich_logs(logs)


def get_instructor_session_logs(instructor_id):
    """
    Get all session logs for an instructor with enriched data
    
    Args:
        instructor_id: ID of the instructor user
    
    Returns:
        list: Enriched session logs with user and course info
    """
    logs = SessionLog.get_logs_by_instructor(instructor_id)
    return enrich_logs(logs)


def enrich_logs(logs):
    """
    Add user and course information to logs
    
    Args:
        logs: List of raw MongoDB log documents
    
    Returns:
        list: Logs enriched with readable user and course names
    """
    enriched_logs = []
    
    for log in logs:
        try:
            # Get user and course objects
            student = User.objects.get(id=log['student_id'])
            instructor = User.objects.get(id=log['instructor_id'])
            course = Course.objects.get(id=log['course_id'])
            
            # Add readable names
            log['student_name'] = student.username
            log['instructor_name'] = instructor.username
            log['course_name'] = course.title
            
            # Calculate duration
            if log.get('end_time') and log.get('start_time'):
                duration = log['end_time'] - log['start_time']
                log['duration_minutes'] = int(duration.total_seconds() / 60)
            else:
                log['duration_minutes'] = 0
            
            enriched_logs.append(log)
            
        except Exception as e:
            print(f"Error enriching log: {e}")
            continue
    
    return enriched_logs


def get_session_statistics(user_id, role):
    """
    Get session statistics for a user
    
    Args:
        user_id: ID of the user
        role: 'student' or 'instructor'
    
    Returns:
        dict: Statistics including total sessions and duration
    """
    if role == 'student':
        return SessionLog.get_stats_by_student(user_id)
    else:
        logs = SessionLog.get_logs_by_instructor(user_id)
        total_sessions = len(logs)
        total_minutes = 0
        
        for log in logs:
            if log.get('end_time') and log.get('start_time'):
                duration = (log['end_time'] - log['start_time']).total_seconds() / 60
                total_minutes += duration
        
        return {
            'total_sessions': total_sessions,
            'total_minutes': int(total_minutes)
        }
