from django.contrib import admin
from .models import UserProfile, Event, Participant, Comment

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # Added 'is_verified' to display and making it editable directly in the list
    list_display = ('title', 'creator', 'category', 'event_date', 'participant_count', 'is_verified')
    
    # Allows you to click the checkmark in the list view without opening the event
    list_editable = ('is_verified',)
    
    # Added filters to quickly find pending events or specific categories
    list_filter = ('is_verified', 'category', 'event_date')
    
    # Search functionality for titles and creators
    search_fields = ('title', 'creator__username', 'location')
    
    # Custom bulk actions
    actions = ['approve_events', 'unapprove_events']

    @admin.action(description='Verify selected events (Go Live)')
    def approve_events(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} events were successfully verified.')

    @admin.action(description='Unverify selected events (Take Offline)')
    def unapprove_events(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} events were taken offline.')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'joined_at')
    list_filter = ('joined_at', 'event')
    search_fields = ('user__username', 'event__title')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'event', 'short_body', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('body', 'author__username')

    def short_body(self, obj):
        return obj.body[:50] + "..." if len(obj.body) > 50 else obj.body
    short_body.short_description = 'Comment Preview'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio_preview')
    
    def bio_preview(self, obj):
        return obj.bio[:30] + "..." if obj.bio else "No bio"