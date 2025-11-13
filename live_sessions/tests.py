from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from courses.models import Course


class LiveSessionViewTests(TestCase):
    """Test cases for live session views"""
    
    def setUp(self):
        """Create test users and course"""
        # Create student
        self.student = User.objects.create_user(
            username='student',
            password='test123'
        )
        self.student.profile.role = 'student'
        self.student.profile.save()
        
        # Create instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            password='test123'
        )
        self.instructor.profile.role = 'instructor'
        self.instructor.profile.save()
        
        # Create course
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Test Course',
            description='Test Description',
            price=999.00
        )
        
        self.client = Client()
    
    def test_session_request_access(self):
        """Test student can access session request page"""
        self.client.login(username='student', password='test123')
        response = self.client.get(
            reverse('live_sessions:request', args=[self.course.id])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_session_room_access(self):
        """Test user can access session room"""
        self.client.login(username='student', password='test123')
        response = self.client.get(
            reverse('live_sessions:room', args=['test_room_123'])
        )
        self.assertEqual(response.status_code, 200)
