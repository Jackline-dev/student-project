from django import forms
from .models import Event, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class EventForm(forms.ModelForm):
    event_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'category', 'event_date', 'max_participants']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')