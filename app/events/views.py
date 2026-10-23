from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import EventForm, SignUpForm
from .models import Event, Registration, Ticket


def home(request):
    events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')
    return render(request, 'events/home.html', {'events': events})


def event_detail(request, event_id):
    event = Event.objects.get(pk=event_id)
    already_registered = False
    if request.user.is_authenticated:
        already_registered = Registration.objects.filter(user=request.user, event=event).exists()
    return render(request, 'events/event_detail.html', {'event': event, 'already_registered': already_registered})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created successfully.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'events/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'You are now logged in.')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'events/login.html', {'form': form})


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Event created successfully.')
            return redirect('event_detail', event_id=event.pk)
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})


@login_required
def edit_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('event_detail', event_id=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('home')
    return render(request, 'events/delete_event.html', {'event': event})


@login_required
def register_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if not event.is_active():
        messages.error(request, 'This event has already ended.')
        return redirect('event_detail', event_id=event.pk)

    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.error(request, 'You are already registered for this event.')
        return redirect('event_detail', event_id=event.pk)

    if event.available_tickets <= 0:
        messages.error(request, 'This event is sold out.')
        return redirect('event_detail', event_id=event.pk)

    try:
        with transaction.atomic():
            registration = Registration.objects.create(user=request.user, event=event, status=Registration.STATUS_CONFIRMED)
            ticket = Ticket.objects.create(user=request.user, event=event, registration=registration)
            messages.success(request, f'Registration successful. Your ticket code is {ticket.ticket_code}.')
    except IntegrityError:
        messages.error(request, 'Registration failed due to a duplicate or capacity issue.')

    return redirect('event_detail', event_id=event.pk)


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('event', 'registration')
    return render(request, 'events/my_tickets.html', {'tickets': tickets})


@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(user=request.user).select_related('event')
    return render(request, 'events/my_registrations.html', {'registrations': registrations})


def health_check(request):
    return render(request, 'events/health.html', {'status': 'ok'})
