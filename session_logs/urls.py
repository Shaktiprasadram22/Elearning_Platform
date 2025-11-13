from django.urls import path
from . import views

app_name = 'session_logs'

urlpatterns = [
    path('create/', views.create_log_view, name='create'),
    path('end/<str:log_id>/', views.end_log_view, name='end'),
    path('my-logs/', views.my_logs_view, name='my_logs'),
]
