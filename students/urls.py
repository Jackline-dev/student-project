from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- Landing Page & Dashboard ---
    path('', views.index_view, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- Authentication ---
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='students/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='students/logout.html'), name='logout'),

    # --- Event Discovery ---
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),

    # --- Event Management (CRUD) ---
    path('event/add/', views.EventCreateView.as_view(), name='add_event'),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='update_event'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='delete_event'),

    # --- Interactivity ---
    path('event/<int:pk>/join/', views.join_event, name='join_event'),
    path('event/<int:pk>/leave/', views.leave_event, name='leave_event'),
    path('event/<int:pk>/comment/', views.add_comment, name='add_comment'),

    # --- OTP Password Reset (Custom Flow) ---
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
]