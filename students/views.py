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
from django.contrib.auth.models import User

from .models import Event, Participant, PasswordResetOTP
from .forms import EventForm, CommentForm, RegisterForm, ForgotPasswordForm, OTPVerifyForm, SetNewPasswordForm


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
    hosted_events = Event.objects.filter(creator=request.user).order_by('-event_date')
    joined_events = Event.objects.filter(participants__user=request.user)
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
        event = self.get_object()
        return self.request.user == event.creator or self.request.user.is_staff

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'students/event_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
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


# --- OTP PASSWORD RESET FLOW ---

def forgot_password_view(request):
    """Step 1: User enters their email, OTP is sent."""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # Generate and save OTP
            code = PasswordResetOTP.generate_code()
            PasswordResetOTP.objects.create(user=user, code=code)

            # Send OTP email
            send_mail(
                subject='Your Campus Events Password Reset Code',
                message=(
                    f'Hi {user.username},\n\n'
                    f'Your OTP code is: {code}\n\n'
                    f'This code expires in 10 minutes.\n\n'
                    f'If you did not request this, please ignore this email.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            request.session['otp_user_id'] = user.id
            messages.success(request, f"A 6-digit code has been sent to {email}.")
            return redirect('verify_otp')
    else:
        form = ForgotPasswordForm()
    return render(request, 'students/forgot_password.html', {'form': form})


def verify_otp_view(request):
    """Step 2: User enters the OTP code."""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please start again.")
        return redirect('forgot_password')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user = get_object_or_404(User, pk=user_id)

            otp = PasswordResetOTP.objects.filter(
                user=user, code=code, is_used=False
            ).order_by('-created_at').first()

            if otp and otp.is_valid():
                otp.is_used = True
                otp.save()
                request.session['otp_verified'] = True
                messages.success(request, "Code verified! Now set your new password.")
                return redirect('reset_password')
            else:
                messages.error(request, "Invalid or expired code. Please try again.")
    else:
        form = OTPVerifyForm()
    return render(request, 'students/verify_otp.html', {'form': form})


def reset_password_view(request):
    """Step 3: User sets their new password."""
    user_id = request.session.get('otp_user_id')
    verified = request.session.get('otp_verified')

    if not user_id or not verified:
        messages.error(request, "Unauthorized. Please start the reset process again.")
        return redirect('forgot_password')

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, pk=user_id)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            # Clear session
            del request.session['otp_user_id']
            del request.session['otp_verified']

            messages.success(request, "Password reset successful! You can now log in.")
            return redirect('login')
    else:
        form = SetNewPasswordForm()
    return render(request, 'students/reset_password.html', {'form': form})