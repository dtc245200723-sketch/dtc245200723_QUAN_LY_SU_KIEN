from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def available_tickets(self):
        total_booked = sum(registration.ticket_count for registration in self.registrations.all())
        return max(self.capacity - total_booked, 0)

    def is_active(self):
        return self.event_date > timezone.now()

    def __str__(self):
        return self.title


class Registration(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
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
        (STATUS_VALID, 'Valid'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_USED, 'Used'),
    ]

    ticket_code = models.CharField(max_length=20, unique=True, default=lambda: uuid.uuid4().hex[:12].upper())
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
