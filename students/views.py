from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Event, Participant
from .forms import EventForm, CommentForm, RegisterForm
from django.contrib.auth import login
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from.forms import EventForm




# Registration view
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally create UserProfile here
            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'students/register.html', {'form': form})

# Dashboard
def dashboard_view(request):
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')
    joined_events = Event.objects.filter(participants__user=request.user) if request.user.is_authenticated else []
    return render(request, 'students/base.html', {'upcoming_events': upcoming_events, 'joined_events': joined_events})

# Event List
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'students/event_list.html'
    context_object_name = 'events'

# Event Detail
class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'students/event_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comment_form'] = CommentForm()
        ctx['participants'] = self.object.participants.all()
        return ctx

# Create Event
class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'students/students_form.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

# Update Event (only creator)
class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'students/event_form.html'

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.creator

# Delete Event (only creator)
class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'students/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.creator

# Join event
def join_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    # check capacity
    if event.max_participants and event.participant_count() >= event.max_participants:
        messages.error(request, "Event is full.")
        return redirect('event_detail', pk=pk)
    Participant.objects.get_or_create(event=event, user=request.user)
    # send confirmation email (printed to console in dev)
    if request.user.email:
        send_mail(
            subject=f'RSVP Confirmation for {event.title}',
            message=f'You have successfully joined the event: {event.title}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
        )
    messages.success(request, "You joined the event.")
    return redirect('event_detail', pk=pk)

# Leave event
def leave_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    Participant.objects.filter(event=event, user=request.user).delete()
    messages.success(request, "You left the event.")
    return redirect('event_detail', pk=pk)

# Add comment
def add_comment(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.author = request.user
            c.event = event
            c.save()
    return redirect('event_detail', pk=pk)