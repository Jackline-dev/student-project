from django.urls import path
from .views import (
    EventListView, EventDetailView, EventCreateView,
    EventUpdateView, EventDeleteView, register_view,
    dashboard_view, join_event, leave_event, add_comment
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='students/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', dashboard_view, name='dashboard'),
    path('events/', EventListView.as_view(), name='event_list'),
    path('event/add/', EventCreateView.as_view(), name='event_add'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('event/<int:pk>/edit/', EventUpdateView.as_view(), name='event_edit'),
    path('event/<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('event/<int:pk>/join/', join_event, name='join_event'),
    path('event/<int:pk>/leave/', leave_event, name='leave_event'),
    path('event/<int:pk>/comment/', add_comment, name='add_comment'),
]