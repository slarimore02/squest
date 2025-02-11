from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import NotificationFilter
from tests.test_profile.base_test_profile import BaseTestProfile


class TestApiNotificationFilterDelete(BaseTestProfile):

    def setUp(self):
        super(TestApiNotificationFilterDelete, self).setUp()
        self.notification_filter_to_delete_id = self.notification_filter_test.id
        self.kwargs = {
            'pk': self.notification_filter_to_delete_id
        }
        self.delete_notification_filter_url = reverse('api_notification_filter_details', kwargs=self.kwargs)

    def test_admin_delete_notification_filter(self):
        notification_filter_count = NotificationFilter.objects.count()
        response = self.client.delete(self.delete_notification_filter_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(notification_filter_count - 1, NotificationFilter.objects.count())
        self.assertFalse(NotificationFilter.objects.filter(id=self.notification_filter_to_delete_id).exists())

    def test_admin_cannot_delete_notification_filter_of_another_user(self):
        self.client.force_login(user=self.superuser_2)
        response = self.client.delete(self.delete_notification_filter_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(NotificationFilter.objects.filter(id=self.notification_filter_to_delete_id).exists())


    def test_customer_cannot_delete_notification_filter(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.delete_notification_filter_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_notification_filter_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.delete_notification_filter_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
