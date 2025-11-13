from django.db import models
from django.contrib.auth.models import User

# No models needed for dashboards app
# This app only handles views and templates for displaying data
# All data comes from accounts, courses, and session_logs apps

class TechBlog(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    content = models.TextField()
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default='Technology')
    image_url = models.URLField(blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-published_date']
    
    def __str__(self):
        return self.title


class CoreSubject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')])
    icon_url = models.URLField(blank=True)
    resource_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name


class TrendingSkill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    demand_level = models.CharField(max_length=20, choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')])
    icon_url = models.URLField(blank=True)
    courses_available = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-demand_level']
    
    def __str__(self):
        return self.name


class LearningPath(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')])
    duration_weeks = models.IntegerField()
    icon_url = models.URLField(blank=True)
    enrolled_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title


class SuccessStory(models.Model):
    student_name = models.CharField(max_length=100)
    story_title = models.CharField(max_length=200)
    story_content = models.TextField()
    achievement = models.CharField(max_length=200)
    image_url = models.URLField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student_name} - {self.story_title}"


class DailyQuiz(models.Model):
    title = models.CharField(max_length=200)
    question = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=200)
    explanation = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class FreeResource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=50, choices=[('notes', 'Notes'), ('cheatsheet', 'Cheat Sheet'), ('guide', 'Guide')])
    file_url = models.URLField()
    subject = models.CharField(max_length=100)
    downloads = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title


class Webinar(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    speaker = models.CharField(max_length=100)
    date = models.DateTimeField()
    duration_minutes = models.IntegerField()
    registration_link = models.URLField()
    image_url = models.URLField(blank=True)
    registered_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return self.title


class PlacementOpportunity(models.Model):
    company_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    description = models.TextField()
    salary_range = models.CharField(max_length=100)
    required_skills = models.JSONField()
    application_link = models.URLField()
    posted_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-posted_date']
    
    def __str__(self):
        return f"{self.company_name} - {self.position}"
