from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.dashboard_redirect, name='redirect'),
    path('student/', views.student_dashboard, name='student'),
    path('instructor/', views.instructor_dashboard, name='instructor'),
    path('home/', views.home_page, name='home'),
    # Resource pages
    path('resources/blogs/', views.blogs_page, name='blogs'),
    path('resources/subjects/', views.subjects_page, name='subjects'),
    path('resources/skills/', views.skills_page, name='skills'),
    path('resources/paths/', views.paths_page, name='paths'),
    path('resources/stories/', views.stories_page, name='stories'),
    path('resources/resources/', views.resources_page, name='resources'),
    path('resources/webinars/', views.webinars_page, name='webinars'),
    path('resources/placements/', views.placements_page, name='placements'),
]
