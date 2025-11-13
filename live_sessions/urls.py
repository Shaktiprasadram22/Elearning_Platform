from django.urls import path
from . import views

app_name = 'live_sessions'

urlpatterns = [
    path('request/<int:lesson_id>/', views.request_session_view, name='request'),
    path('room/<str:room_name>/', views.session_room_view, name='room'),
    path('instructor-dashboard/', views.instructor_dashboard_view, name='instructor_dashboard'),
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('accept/<int:session_id>/', views.accept_session_view, name='accept'),
    path('reject/<int:session_id>/', views.reject_session_view, name='reject'),
    path('end/<int:session_id>/', views.end_session_view, name='end'),
]
