from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """
    Course Model
    Represents a course created by an instructor
    """
    CATEGORY_CHOICES = (
        ('programming', 'Programming'),
        ('data_science', 'Data Science'),
        ('web_dev', 'Web Development'),
        ('mobile_dev', 'Mobile Development'),
        ('ai_ml', 'AI & Machine Learning'),
        ('database', 'Database'),
        ('devops', 'DevOps'),
        ('other', 'Other'),
    )
    
    instructor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='courses_taught'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='other'
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/', 
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_total_lessons(self):
        """Return total number of lessons in this course"""
        return self.lessons.count()
    
    def get_total_students(self):
        """Return total number of enrolled students"""
        return self.enrollments.count()
    
    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


class Lesson(models.Model):
    """
    Lesson Model
    Represents individual lessons within a course
    """
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(
        upload_to='lesson_videos/', 
        blank=True, 
        null=True
    )
    pdf_file = models.FileField(
        upload_to='lesson_pdfs/', 
        blank=True, 
        null=True
    )
    order = models.IntegerField(default=0)
    duration = models.IntegerField(
        default=0, 
        help_text='Duration in minutes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    class Meta:
        db_table = 'lessons'
        ordering = ['order', 'created_at']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'


class Enrollment(models.Model):
    """
    Enrollment Model
    Tracks student enrollments in courses
    """
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
    
    def get_progress_percentage(self):
        """Calculate course completion percentage"""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            student=self.student,
            lesson__course=self.course,
            completed=True
        ).count()
        return int((completed_lessons / total_lessons) * 100)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'


class LessonProgress(models.Model):
    """
    Lesson Progress Model
    Tracks individual lesson completion by students
    """
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='progress'
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"
    
    class Meta:
        db_table = 'lesson_progress'
        unique_together = ('student', 'lesson')
        verbose_name = 'Lesson Progress'
        verbose_name_plural = 'Lesson Progress'
