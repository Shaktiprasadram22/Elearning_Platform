from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list_view, name='list'),
    path('<int:course_id>/', views.course_detail_view, name='detail'),
    path('create/', views.course_create_view, name='create'),
    path('<int:course_id>/add-lesson/', views.lesson_create_view, name='add_lesson'),
    path('<int:course_id>/enroll/', views.enroll_course_view, name='enroll'),
    path('lesson/<int:lesson_id>/', views.lesson_watch_view, name='lesson_watch'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_complete'),
]
