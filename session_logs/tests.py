from django.test import TestCase
from django.contrib.auth.models import User
from courses.models import Course
from .services import create_session_log, get_student_session_logs
from datetime import datetime


class SessionLogTests(TestCase):
    """Test cases for session log functionality"""
    
    def setUp(self):
        """Create test users and course"""
        self.student = User.objects.create_user(
            username='student',
            password='test123'
        )
        self.student.profile.role = 'student'
        self.student.profile.save()
        
        self.instructor = User.objects.create_user(
            username='instructor',
            password='test123'
        )
        self.instructor.profile.role = 'instructor'
        self.instructor.profile.save()
        
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Test Course',
            description='Test Description',
            price=999.00
        )
    
    def test_create_session_log(self):
        """Test creating a session log"""
        log_id = create_session_log(
            student_id=self.student.id,
            instructor_id=self.instructor.id,
            course_id=self.course.id
        )
        self.assertIsNotNone(log_id)
    
    def test_get_student_logs(self):
        """Test retrieving student logs"""
        create_session_log(
            student_id=self.student.id,
            instructor_id=self.instructor.id,
            course_id=self.course.id
        )
        
        logs = get_student_session_logs(self.student.id)
        self.assertGreater(len(logs), 0)
