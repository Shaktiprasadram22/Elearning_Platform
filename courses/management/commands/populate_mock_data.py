from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Course, Lesson, Enrollment
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Populate database with mock courses, lessons, and users'

    def handle(self, *args, **options):
        self.stdout.write('Starting mock data population...')
        
        # Create mock instructors
        instructors = []
        instructor_names = [
            ('instructor1', 'Instructor One', 'instructor1@example.com'),
            ('instructor2', 'Instructor Two', 'instructor2@example.com'),
            ('instructor3', 'Instructor Three', 'instructor3@example.com'),
        ]
        
        for username, name, email in instructor_names:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': name.split()[0],
                    'last_name': name.split()[1],
                    'email': email,
                    'is_staff': False
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                # Create profile with instructor role
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': 'instructor'}
                )
                self.stdout.write(self.style.SUCCESS(f'Created instructor: {username}'))
            instructors.append(user)
        
        # Create mock students
        students = []
        student_names = [
            ('student1', 'Student One', 'student1@example.com'),
            ('student2', 'Student Two', 'student2@example.com'),
            ('student3', 'Student Three', 'student3@example.com'),
            ('student4', 'Student Four', 'student4@example.com'),
            ('student5', 'Student Five', 'student5@example.com'),
        ]
        
        for username, name, email in student_names:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': name.split()[0],
                    'last_name': name.split()[1],
                    'email': email,
                    'is_staff': False
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                # Create profile with student role
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': 'student'}
                )
                self.stdout.write(self.style.SUCCESS(f'Created student: {username}'))
            students.append(user)
        
        # Create mock courses
        course_data = [
            {
                'title': 'Python Programming Fundamentals',
                'description': 'Learn Python from scratch. This course covers basic syntax, data structures, functions, and OOP concepts.',
                'category': 'programming',
                'price': 99.99,
                'instructor': instructors[0]
            },
            {
                'title': 'Web Development with Django',
                'description': 'Master Django framework for building scalable web applications. Includes REST APIs and real-time features.',
                'category': 'web_dev',
                'price': 149.99,
                'instructor': instructors[1]
            },
            {
                'title': 'Data Science with Python',
                'description': 'Learn data analysis, visualization, and machine learning using Python libraries like Pandas, NumPy, and Scikit-learn.',
                'category': 'data_science',
                'price': 199.99,
                'instructor': instructors[2]
            },
            {
                'title': 'JavaScript Essentials',
                'description': 'Complete guide to JavaScript. Learn ES6+, async programming, DOM manipulation, and modern frameworks.',
                'category': 'web_dev',
                'price': 89.99,
                'instructor': instructors[0]
            },
            {
                'title': 'Machine Learning Basics',
                'description': 'Introduction to machine learning algorithms, supervised learning, unsupervised learning, and neural networks.',
                'category': 'ai_ml',
                'price': 249.99,
                'instructor': instructors[1]
            },
        ]
        
        courses = []
        for course_info in course_data:
            course, created = Course.objects.get_or_create(
                title=course_info['title'],
                instructor=course_info['instructor'],
                defaults={
                    'description': course_info['description'],
                    'category': course_info['category'],
                    'price': course_info['price']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))
            courses.append(course)
        
        # Create mock lessons for each course
        lessons_data = {
            0: [  # Python Programming
                {'title': 'Introduction to Python', 'description': 'Get started with Python basics', 'duration': 45},
                {'title': 'Variables and Data Types', 'description': 'Learn about variables, strings, numbers, and lists', 'duration': 60},
                {'title': 'Control Flow', 'description': 'If statements, loops, and conditional logic', 'duration': 50},
                {'title': 'Functions and Modules', 'description': 'Creating reusable code with functions', 'duration': 55},
                {'title': 'Object-Oriented Programming', 'description': 'Classes, objects, inheritance, and polymorphism', 'duration': 75},
            ],
            1: [  # Django Web Development
                {'title': 'Django Setup and Project Structure', 'description': 'Setting up Django projects and understanding architecture', 'duration': 40},
                {'title': 'Models and Databases', 'description': 'Creating models and working with databases', 'duration': 65},
                {'title': 'Views and URL Routing', 'description': 'Creating views and URL patterns', 'duration': 55},
                {'title': 'Templates and Static Files', 'description': 'Django templates and CSS/JavaScript integration', 'duration': 50},
                {'title': 'Django REST Framework', 'description': 'Building RESTful APIs with Django', 'duration': 70},
            ],
            2: [  # Data Science
                {'title': 'NumPy Fundamentals', 'description': 'Working with arrays and numerical operations', 'duration': 50},
                {'title': 'Pandas for Data Analysis', 'description': 'DataFrames, data cleaning, and manipulation', 'duration': 65},
                {'title': 'Data Visualization', 'description': 'Creating charts and visualizations with Matplotlib and Seaborn', 'duration': 55},
                {'title': 'Statistical Analysis', 'description': 'Descriptive and inferential statistics', 'duration': 60},
                {'title': 'Introduction to ML', 'description': 'Machine learning concepts and algorithms', 'duration': 75},
            ],
            3: [  # JavaScript
                {'title': 'JavaScript Basics', 'description': 'Syntax, variables, and operators', 'duration': 45},
                {'title': 'Functions and Scope', 'description': 'Function declarations, arrow functions, and scope', 'duration': 50},
                {'title': 'Async Programming', 'description': 'Promises, async/await, and callbacks', 'duration': 60},
                {'title': 'DOM Manipulation', 'description': 'Selecting and modifying DOM elements', 'duration': 55},
                {'title': 'Modern JavaScript', 'description': 'ES6+ features and best practices', 'duration': 65},
            ],
            4: [  # Machine Learning
                {'title': 'ML Concepts', 'description': 'Understanding machine learning fundamentals', 'duration': 50},
                {'title': 'Supervised Learning', 'description': 'Regression and classification algorithms', 'duration': 70},
                {'title': 'Unsupervised Learning', 'description': 'Clustering and dimensionality reduction', 'duration': 65},
                {'title': 'Neural Networks', 'description': 'Deep learning and neural network basics', 'duration': 80},
                {'title': 'Model Evaluation', 'description': 'Testing, validation, and performance metrics', 'duration': 60},
            ],
        }
        
        for course_idx, course in enumerate(courses):
            if course_idx in lessons_data:
                for order, lesson_info in enumerate(lessons_data[course_idx], 1):
                    lesson, created = Lesson.objects.get_or_create(
                        course=course,
                        title=lesson_info['title'],
                        defaults={
                            'description': lesson_info['description'],
                            'duration': lesson_info['duration'],
                            'order': order
                        }
                    )
                    if created:
                        self.stdout.write(f'  Created lesson: {lesson.title}')
        
        # Enroll students in courses
        for student in students:
            # Each student enrolls in 2-3 random courses
            import random
            num_courses = random.randint(2, 3)
            selected_courses = random.sample(courses, num_courses)
            
            for course in selected_courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course
                )
                if created:
                    self.stdout.write(f'  Enrolled {student.username} in {course.title}')
        
        self.stdout.write(self.style.SUCCESS('Mock data population completed successfully!'))
