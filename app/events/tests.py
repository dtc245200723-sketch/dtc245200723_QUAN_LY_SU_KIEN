from types import SimpleNamespace
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import SimpleTestCase
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from .models import Event, Registration, Ticket
from .views import create_event, delete_event, edit_event


class MetricsEndpointTests(SimpleTestCase):
    def test_metrics_endpoint_is_available(self):
        response = self.client.get('/metrics')

        self.assertEqual(response.status_code, 200)
        self.assertIn('django_http_requests_total_by_view_transport_method_total', response.content.decode())


class PublicWebPageTests(SimpleTestCase):
    def test_health_page_is_available(self):
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, 200)

    def test_login_page_is_available(self):
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)

    def test_signup_page_is_available(self):
        response = self.client.get('/signup/')

        self.assertEqual(response.status_code, 200)


class EventManagementPermissionTests(SimpleTestCase):
    def test_non_staff_user_cannot_manage_events(self):
        request = RequestFactory().get('/event/create/')
        request.user = SimpleNamespace(is_active=True, is_staff=False)

        responses = (
            create_event(request),
            edit_event(request, event_id=1),
            delete_event(request, event_id=1),
        )

        for response in responses:
            self.assertEqual(response.status_code, 302)
            self.assertIn('/admin/login/', response.url)


class EventWebsiteTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            event_code='EVTTEST',
            title='Sự kiện kiểm thử EventHub',
            description='Mô tả sự kiện kiểm thử.',
            event_date=timezone.now() + timedelta(days=14),
            end_date=timezone.now() + timedelta(days=14, hours=3),
            registration_deadline=timezone.now() + timedelta(days=10),
            location='Hà Nội',
            category='Công nghệ',
            capacity=10,
        )

    def test_homepage_shows_upcoming_event_and_search(self):
        response = self.client.get(reverse('home'), {'q': 'EVTTEST'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sự kiện kiểm thử EventHub')
        self.assertContains(response, 'EVTTEST')

    def test_dashboard_stats_are_calculated_from_database(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_events'], 1)
        self.assertEqual(response.context['open_event_count'], 1)
        self.assertEqual(response.context['available_seats'], 10)

    def test_event_detail_shows_real_registration_information(self):
        response = self.client.get(reverse('event_detail', args=[self.event.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.event_code)
        self.assertContains(response, 'Sức chứa')
        self.assertContains(response, 'Hạn đăng ký')

    def test_registration_creates_registration_and_unique_ticket(self):
        user = get_user_model().objects.create_user(
            username='eventhub-test-user',
            email='eventhub-test@example.invalid',
            password='Strong-test-password-928!',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('register_event', args=[self.event.pk]),
            {'attendee_name': 'Nguyễn An', 'email': user.email, 'phone': '0900000000'},
        )

        self.assertRedirects(response, reverse('event_detail', args=[self.event.pk]))
        self.assertEqual(Registration.objects.filter(user=user, event=self.event).count(), 1)
        ticket = Ticket.objects.get(user=user, event=self.event)
        self.assertEqual(ticket.registration.attendee_name, 'Nguyễn An')

    def test_registration_form_get_does_not_create_a_registration(self):
        user = get_user_model().objects.create_user(
            username='eventhub-get-test-user',
            email='eventhub-get@example.invalid',
            password='Strong-test-password-928!',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('register_event', args=[self.event.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Registration.objects.count(), 0)

    def test_ticket_page_only_shows_current_users_tickets(self):
        owner = get_user_model().objects.create_user(
            username='ticket-owner',
            email='ticket-owner@example.invalid',
            password='Strong-test-password-928!',
        )
        other_user = get_user_model().objects.create_user(
            username='ticket-other',
            email='ticket-other@example.invalid',
            password='Strong-test-password-928!',
        )
        registration = Registration.objects.create(
            user=owner,
            event=self.event,
            attendee_name='Chủ vé',
            status=Registration.STATUS_CONFIRMED,
        )
        Ticket.objects.create(user=owner, event=self.event, registration=registration)
        self.client.force_login(other_user)

        response = self.client.get(reverse('my_tickets'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tickets'].count(), 0)

    def test_staff_can_view_registration_management_and_reports(self):
        staff_user = get_user_model().objects.create_user(
            username='eventhub-staff',
            email='eventhub-staff@example.invalid',
            password='Strong-test-password-928!',
            is_staff=True,
        )
        self.client.force_login(staff_user)

        registrations_response = self.client.get(reverse('registration_management'))
        reports_response = self.client.get(reverse('reports'))

        self.assertEqual(registrations_response.status_code, 200)
        self.assertEqual(reports_response.status_code, 200)
        self.assertContains(reports_response, 'Tỷ lệ lấp đầy')
