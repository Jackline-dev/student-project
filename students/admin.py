

# Register your models here.
from django.contrib import admin
from .models import UserProfile, Event, Participant, Comment

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'event_date', 'creator', 'participant_count')
    list_filter = ('category',)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'joined_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'author', 'created_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)