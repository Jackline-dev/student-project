from django import forms
from .models import Event, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'category', 'event_date', 'max_participants']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Annual Tech Symposium'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'What is this event about?'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Main Hall, Room 302'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'event_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Leave blank for unlimited'
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Add a public comment...'
            }),
        }
        labels = {
            'body': '', # Removes the "Body" label for a cleaner look
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required for RSVP confirmations.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically add Bootstrap classes to all fields in the registration form
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
