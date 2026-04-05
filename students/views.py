from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Event, Participant
from .forms import EventForm, CommentForm, RegisterForm

# --- HOME & AUTHENTICATION ---

def index_view(request):
    """Landing page: Redirects to dashboard if user is already logged in."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'students/index.html')

def register_view(request):
    """Handles new user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome to Campus Events!")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'students/register.html', {'form': form})


# --- DASHBOARD ---

@login_required
def dashboard_view(request):
    """Shows hosted events (for management) and joined events."""
    # 1. Events the user CREATED (allows them to Update/Delete)
    hosted_events = Event.objects.filter(creator=request.user).order_by('-event_date')
    
    # 2. Events the user JOINED
    joined_events = Event.objects.filter(participants__user=request.user)
    
    # 3. Explore: Upcoming verified events created by others
    upcoming_events = Event.objects.filter(
        is_verified=True, 
        event_date__gte=timezone.now()
    ).exclude(creator=request.user).order_by('event_date')[:6]
    
    return render(request, 'students/dashboard.html', {
        'hosted_events': hosted_events,
        'joined_events': joined_events,
        'upcoming_events': upcoming_events,
    })


# --- EVENT VIEWS (CRUD) ---

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'students/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Admins see all; students see only verified events
        if self.request.user.is_staff:
            return Event.objects.all().order_by('-event_date')
        return Event.objects.filter(is_verified=True).order_by('-event_date')

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'students/event_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comment_form'] = CommentForm()
        ctx['is_joined'] = self.object.participants.filter(user=self.request.user).exists()
        return ctx

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'students/add_event.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.is_verified = False 
        messages.info(self.request, "Event submitted! It will appear after admin verification.")
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'students/add_event.html'
    
    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        # Only creator or staff can edit
        event = self.get_object()
        return self.request.user == event.creator or self.request.user.is_staff

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'students/event_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        # Only creator or staff can delete
        event = self.get_object()
        return self.request.user == event.creator or self.request.user.is_staff


# --- INTERACTIVE ACTIONS (RSVP & COMMENTS) ---

@login_required
def join_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if event.max_participants and event.participants.count() >= event.max_participants:
        messages.error(request, "Sorry, this event is full.")
        return redirect('event_detail', pk=pk)
        
    Participant.objects.get_or_create(event=event, user=request.user)
    messages.success(request, f"You have joined {event.title}!")
    return redirect('event_detail', pk=pk)

@login_required
def leave_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    Participant.objects.filter(event=event, user=request.user).delete()
    messages.info(request, "You have left the event.")
    return redirect('event_detail', pk=pk)

@login_required
def add_comment(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.author = request.user
            c.event = event
            c.save()
            messages.success(request, "Comment posted.")
    return redirect('event_detail', pk=pk)