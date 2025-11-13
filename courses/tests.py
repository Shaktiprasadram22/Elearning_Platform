from django.test import TestCase
from django.contrib.auth.models import User
from .models import Course, Lesson, Enrollment, LessonProgress


class CourseModelTestCase(TestCase):
    """Test cases for Course model"""
    
    def setUp(self):
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
            category='programming',
            price=999.00
        )
    
    def test_course_creation(self):
        """Test course is created correctly"""
        self.assertEqual(self.course.title, 'Test Course')
        self.assertEqual(self.course.instructor, self.instructor)
    
    def test_course_str(self):
        """Test course string representation"""
        self.assertEqual(str(self.course), 'Test Course')


class EnrollmentTestCase(TestCase):
    """Test cases for Enrollment model"""
    
    def setUp(self):
        self.student = User.objects.create_user(
            username='student',
            password='test123'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            password='test123'
        )
        self.course = Course.objects.create(
            instructor=self.instructor,
            title='Test Course',
            description='Test Description'
        )
    
    def test_enrollment_creation(self):
        """Test enrollment is created correctly"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertIsNotNone(enrollment)
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
