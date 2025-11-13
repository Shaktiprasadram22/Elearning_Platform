from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class DashboardViewTests(TestCase):
    """Test cases for dashboard views"""
    
    def setUp(self):
        """Create test users"""
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
        
        self.client = Client()
    
    def test_student_dashboard_access(self):
        """Test student can access student dashboard"""
        self.client.login(username='student', password='test123')
        response = self.client.get(reverse('dashboards:student'))
        self.assertEqual(response.status_code, 200)
    
    def test_instructor_dashboard_access(self):
        """Test instructor can access instructor dashboard"""
        self.client.login(username='instructor', password='test123')
        response = self.client.get(reverse('dashboards:instructor'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_redirect(self):
        """Test dashboard redirect works correctly"""
        # Test student redirect
        self.client.login(username='student', password='test123')
        response = self.client.get(reverse('dashboards:redirect'))
        self.assertRedirects(response, reverse('dashboards:student'))
        
        # Test instructor redirect
        self.client.logout()
        self.client.login(username='instructor', password='test123')
        response = self.client.get(reverse('dashboards:redirect'))
        self.assertRedirects(response, reverse('dashboards:instructor'))
