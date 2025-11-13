from django.contrib import admin
from .models import DoubtSession


@admin.register(DoubtSession)
class DoubtSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'instructor', 'course', 'status', 'requested_at', 'duration_minutes')
    list_filter = ('status', 'requested_at', 'course')
    search_fields = ('student__username', 'instructor__username', 'course__title')
    readonly_fields = ('room_name', 'requested_at', 'started_at', 'ended_at')
    
    fieldsets = (
        ('Session Info', {
            'fields': ('student', 'instructor', 'course', 'lesson', 'room_name')
        }),
        ('Status', {
            'fields': ('status', 'duration_minutes')
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'started_at', 'ended_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
