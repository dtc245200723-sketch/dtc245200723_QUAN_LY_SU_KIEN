from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def generate_ticket_code():
    return uuid.uuid4().hex[:12].upper()


class Event(models.Model):
    event_code = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=80, default='Sự kiện')
    capacity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.event_code:
            self.event_code = f'EVT{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    @property
    def available_tickets(self):
        return max(self.capacity - self.registrations.filter(status=Registration.STATUS_CONFIRMED).count(), 0)

    @property
    def registered_count(self):
        return self.registrations.filter(status=Registration.STATUS_CONFIRMED).count()

    def is_active(self):
        now = timezone.now()
        return (
            self.event_date > now
            and self.available_tickets > 0
            and (self.registration_deadline is None or self.registration_deadline >= now)
        )

    def __str__(self):
        return self.title


class Registration(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Chờ xác nhận'),
        (STATUS_CONFIRMED, 'Đã xác nhận'),
        (STATUS_CANCELLED, 'Đã hủy'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    attendee_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    @property
    def ticket_count(self):
        return self.tickets.filter(status='valid').count()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'event'], name='unique_registration_per_user_event')
        ]

    def clean(self):
        if self.event.event_date <= timezone.now():
            raise ValidationError('Event has already ended.')
        if self.event.available_tickets <= 0:
            raise ValidationError('No tickets available.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} -> {self.event.title}'


class Ticket(models.Model):
    STATUS_VALID = 'valid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_USED = 'used'

    STATUS_CHOICES = [
        (STATUS_VALID, 'Đã xác nhận'),
        (STATUS_CANCELLED, 'Đã hủy'),
        (STATUS_USED, 'Đã sử dụng'),
    ]

    ticket_code = models.CharField(max_length=20, unique=True, default=generate_ticket_code)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='tickets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_VALID)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.event.event_date <= timezone.now():
            raise ValidationError('Event has already ended.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_code
