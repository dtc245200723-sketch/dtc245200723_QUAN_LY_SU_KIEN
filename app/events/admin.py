from django.contrib import admin
from .models import Event, Registration, Ticket


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_code', 'title', 'event_date', 'location', 'capacity', 'available_tickets')
    search_fields = ('event_code', 'title', 'location')
    list_filter = ('event_date',)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('attendee_name', 'user', 'event', 'registered_at', 'status')
    list_filter = ('status', 'registered_at')
    search_fields = ('attendee_name', 'user__username', 'user__email', 'event__title')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'user', 'event', 'status')
    search_fields = ('ticket_code', 'user__username', 'event__title')
    list_filter = ('status',)
