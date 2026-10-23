from types import SimpleNamespace

from django.test import SimpleTestCase
from django.test import RequestFactory

from .views import create_event, delete_event, edit_event


class MetricsEndpointTests(SimpleTestCase):
    def test_metrics_endpoint_is_available(self):
        response = self.client.get('/metrics')

        self.assertEqual(response.status_code, 200)
        self.assertIn('django_http_requests_total', response.content.decode())


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
