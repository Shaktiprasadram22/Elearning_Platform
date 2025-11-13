from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileTestCase(TestCase):
    """
    Test cases for UserProfile model
    """
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test that profile is automatically created"""
        self.assertIsNotNone(self.user.profile)
        self.assertEqual(self.user.profile.role, 'student')
    
    def test_profile_str(self):
        """Test profile string representation"""
        expected = f"{self.user.username} - {self.user.profile.role}"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_role_choices(self):
        """Test that role can be set to instructor"""
        self.user.profile.role = 'instructor'
        self.user.profile.save()
        self.assertEqual(self.user.profile.role, 'instructor')
