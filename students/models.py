from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

CATEGORY_CHOICES = [
    ('Lecture', 'Lecture'),
    ('Workshop', 'Workshop'),
    ('Social', 'Social'),
    ('Sports', 'Sports'),
    ('Club Meeting', 'Club Meeting'),
    ('Exhibition', 'Exhibition'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Lecture')
    event_date = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.title} ({self.category})"

    def participant_count(self):
        return self.participants.count()

    # FIX: Added this property to solve the 'divide' filter error
    @property
    def attendance_progress(self):
        """Calculates the percentage of attendance for the progress bar."""
        if self.max_participants and self.max_participants > 0:
            count = self.participant_count()
            # Calculate percentage: (current / max) * 100
            progress = (count / self.max_participants) * 100
            return min(progress, 100)  # Cap at 100%
        return 0 # Default to 0 if no limit is set or limit is 0

    @property
    def is_full(self):
        if self.max_participants:
            return self.participant_count() >= self.max_participants
        return False

    @property
    def is_upcoming(self):
        return self.event_date >= timezone.now()

class Participant(models.Model):
    event = models.ForeignKey(Event, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} joined {self.event.title}"

class Comment(models.Model):
    event = models.ForeignKey(Event, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.event.title}"