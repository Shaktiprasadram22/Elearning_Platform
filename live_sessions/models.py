from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class DoubtSession(models.Model):
    """
    Model to track doubt solving sessions between students and instructors
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doubt_sessions_as_student'
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doubt_sessions_as_instructor'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='doubt_sessions'
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doubt_sessions'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    room_name = models.CharField(max_length=100, unique=True)
    
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    duration_minutes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Doubt Session: {self.student.username} - {self.course.title}"
    
    class Meta:
        db_table = 'doubt_sessions'
        ordering = ['-requested_at']
        verbose_name = 'Doubt Session'
        verbose_name_plural = 'Doubt Sessions'
