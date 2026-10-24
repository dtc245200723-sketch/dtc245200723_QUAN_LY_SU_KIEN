from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('event/<int:event_id>/register/', views.register_event, name='register_event'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('manage/registrations/', views.registration_management, name='registration_management'),
    path('reports/', views.reports, name='reports'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('health/', views.health_check, name='health_check'),
]
