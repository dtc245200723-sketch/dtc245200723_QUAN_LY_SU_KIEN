from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone

from .forms import AccountSettingsForm, EventForm, RegistrationForm, SignUpForm
from .models import Event, Registration, Ticket


def home(request):
    query = request.GET.get('q', '').strip()
    events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')
    if query:
        events = events.filter(
            Q(title__icontains=query)
            | Q(event_code__icontains=query)
            | Q(location__icontains=query)
            | Q(category__icontains=query)
        )
    categories = Event.objects.filter(event_date__gte=timezone.now()).order_by().values_list(
        'category', flat=True
    ).distinct()
    return render(request, 'events/home.html', {
        'events': events,
        'query': query,
        'categories': categories,
    })


def dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(event_date__gte=now).order_by('event_date')
    open_event_count = sum(1 for event in upcoming_events if event.is_active())
    total_capacity = upcoming_events.aggregate(total=Sum('capacity'))['total'] or 0
    total_registered = Registration.objects.filter(
        status=Registration.STATUS_CONFIRMED,
        event__event_date__gte=now,
    ).count()
    cancelled_count = Registration.objects.filter(status=Registration.STATUS_CANCELLED).count()
    top_events = upcoming_events.annotate(
        confirmed_count=Count(
            'registrations',
            filter=Q(registrations__status=Registration.STATUS_CONFIRMED),
        )
    ).order_by('-confirmed_count', 'event_date')[:5]
    return render(request, 'events/dashboard.html', {
        'total_events': Event.objects.count(),
        'open_event_count': open_event_count,
        'total_registrations': total_registered,
        'cancelled_count': cancelled_count,
        'available_seats': max(
            total_capacity - sum(event.registered_count for event in upcoming_events),
            0,
        ),
        'fill_rate': round(total_registered / total_capacity * 100, 1) if total_capacity else 0,
        'top_events': top_events,
        'upcoming_events': upcoming_events[:5],
    })


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    already_registered = False
    if request.user.is_authenticated:
        already_registered = Registration.objects.filter(
            user=request.user, event=event
        ).exclude(status=Registration.STATUS_CANCELLED).exists()
    registration_form = RegistrationForm(user=request.user) if request.user.is_authenticated else None
    return render(request, 'events/event_detail.html', {
        'event': event,
        'already_registered': already_registered,
        'registration_form': registration_form,
    })


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Tạo tài khoản thành công.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'events/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Đăng nhập thành công.')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'events/login.html', {'form': form})


@staff_member_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Tạo sự kiện thành công.')
            return redirect('event_detail', event_id=event.pk)
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})


@staff_member_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật sự kiện thành công.')
            return redirect('event_detail', event_id=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@staff_member_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Đã xóa sự kiện.')
        return redirect('home')
    return render(request, 'events/delete_event.html', {'event': event})


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'GET':
        if not event.is_active():
            messages.error(request, 'Sự kiện đã kết thúc hoặc đóng đăng ký.')
            return redirect('event_detail', event_id=event.pk)
        return render(request, 'events/register_event.html', {
            'event': event,
            'form': RegistrationForm(user=request.user),
        })

    if not event.is_active():
        messages.error(request, 'Sự kiện đã kết thúc hoặc đóng đăng ký.')
        return redirect('event_detail', event_id=event.pk)

    if Registration.objects.filter(user=request.user, event=event).exclude(
        status=Registration.STATUS_CANCELLED
    ).exists():
        messages.error(request, 'Bạn đã đăng ký sự kiện này.')
        return redirect('event_detail', event_id=event.pk)

    if event.available_tickets <= 0:
        messages.error(
            request,
            'Rất tiếc, sự kiện đã đạt số lượng người tham dự tối đa. Vui lòng chọn sự kiện khác.',
        )
        return redirect('event_detail', event_id=event.pk)

    form = RegistrationForm(request.POST, user=request.user)
    if not form.is_valid():
        messages.error(request, 'Vui lòng kiểm tra lại thông tin đăng ký.')
        return redirect('event_detail', event_id=event.pk)

    try:
        with transaction.atomic():
            registration = Registration.objects.filter(
                user=request.user,
                event=event,
                status=Registration.STATUS_CANCELLED,
            ).first()
            if registration:
                registration.attendee_name = form.cleaned_data['attendee_name']
                registration.phone = form.cleaned_data['phone']
                registration.status = Registration.STATUS_CONFIRMED
                registration.save()
            else:
                registration = Registration.objects.create(
                    user=request.user,
                    event=event,
                    attendee_name=form.cleaned_data['attendee_name'],
                    phone=form.cleaned_data['phone'],
                    status=Registration.STATUS_CONFIRMED,
                )
            ticket = registration.tickets.filter(status=Ticket.STATUS_VALID).first()
            if ticket is None:
                ticket = Ticket.objects.create(
                    user=request.user,
                    event=event,
                    registration=registration,
                )
            messages.success(
                request,
                f'Đăng ký tham dự thành công! Vé điện tử đã được tạo. Mã vé: {ticket.ticket_code}.',
            )
    except IntegrityError:
        messages.error(request, 'Đăng ký không thành công do trùng đăng ký hoặc sự kiện vừa hết chỗ.')
    return redirect('event_detail', event_id=event.pk)


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).select_related(
        'event', 'registration'
    ).order_by('-created_at')
    return render(request, 'events/my_tickets.html', {'tickets': tickets})


@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(user=request.user).select_related(
        'event'
    ).order_by('-registered_at')
    return render(request, 'events/my_registrations.html', {'registrations': registrations})


@staff_member_required
def registration_management(request):
    registrations = Registration.objects.select_related('user', 'event').prefetch_related('tickets')
    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    event_id = request.GET.get('event', '')
    if search:
        registrations = registrations.filter(
            Q(attendee_name__icontains=search)
            | Q(user__email__icontains=search)
            | Q(event__title__icontains=search)
            | Q(tickets__ticket_code__icontains=search)
        ).distinct()
    if status in dict(Registration.STATUS_CHOICES):
        registrations = registrations.filter(status=status)
    if event_id.isdigit():
        registrations = registrations.filter(event_id=int(event_id))
    return render(request, 'events/registration_management.html', {
        'registrations': registrations.order_by('-registered_at'),
        'events': Event.objects.order_by('title'),
        'search': search,
        'selected_status': status,
        'selected_event': event_id,
        'statuses': Registration.STATUS_CHOICES,
    })


@staff_member_required
def reports(request):
    now = timezone.now()
    events = Event.objects.filter(event_date__gte=now).annotate(
        confirmed_count=Count(
            'registrations',
            filter=Q(registrations__status=Registration.STATUS_CONFIRMED),
        )
    )
    total_capacity = events.aggregate(total=Sum('capacity'))['total'] or 0
    total_confirmed = Registration.objects.filter(
        status=Registration.STATUS_CONFIRMED,
        event__event_date__gte=now,
    ).count()
    return render(request, 'events/reports.html', {
        'total_events': Event.objects.count(),
        'open_events': sum(1 for event in events if event.is_active()),
        'confirmed_registrations': total_confirmed,
        'cancelled_registrations': Registration.objects.filter(status=Registration.STATUS_CANCELLED).count(),
        'fill_rate': round(total_confirmed / total_capacity * 100, 1) if total_capacity else 0,
        'top_events': events.order_by('-confirmed_count', 'event_date')[:10],
    })


@login_required
def account_settings(request):
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thông tin tài khoản.')
            return redirect('account_settings')
    else:
        form = AccountSettingsForm(instance=request.user)
    return render(request, 'events/account_settings.html', {'form': form})


def health_check(request):
    return render(request, 'events/health.html', {'status': 'ok'})
