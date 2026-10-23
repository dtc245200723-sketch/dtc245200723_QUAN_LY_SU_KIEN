from django.contrib import admin
from .models import Event, Registration, Ticket


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'capacity', 'available_tickets')
    search_fields = ('title', 'location')
    list_filter = ('event_date',)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registered_at', 'status')
    list_filter = ('status', 'registered_at')
    search_fields = ('user__username', 'event__title')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'user', 'event', 'status')
    search_fields = ('ticket_code', 'user__username', 'event__title')
    list_filter = ('status',)
