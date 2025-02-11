from django.contrib.auth.models import User

from profiles.models import Profile, NotificationFilter
from tests.test_profile.base_test_profile import BaseTestProfile


class TestProfile(BaseTestProfile):

    def setUp(self):
        super(TestProfile, self).setUp()

    def test_one_to_one_user_on_create(self):
        users_count = User.objects.all().count()
        profile_count = Profile.objects.all().count()
        self.assertEqual(users_count, profile_count)
        User.objects.create(username='test_profile_user')
        users_count = User.objects.all().count()
        profile_count = Profile.objects.all().count()
        self.assertEqual(users_count, profile_count)

    def test_is_notification_authorized_with_two_different_operation(self):
        self.notification_filter_test.operations.add(self.create_operation_test)
        self.notification_filter_test.save()

        self.notification_filter_test_2.operations.add(self.update_operation_test)
        self.notification_filter_test_2.save()

        self.assertTrue(self.superuser.profile.is_notification_authorized(request=self.test_request))
        self.assertTrue(self.superuser.profile.is_notification_authorized(request=self.test_request_2))
        self.assertFalse(self.superuser.profile.is_notification_authorized(request=self.test_request_3))

    def test_is_notification_authorized_no_filter(self):
        NotificationFilter.objects.all().delete()
        self.assertTrue(self.superuser.profile.is_notification_authorized(request=self.test_request))
