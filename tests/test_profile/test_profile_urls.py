from django.urls import reverse
from tests.test_group.test_group_base import TestGroupBase


class TestProfileUrls(TestGroupBase):

    def setUp(self):
        super(TestProfileUrls, self).setUp()

    def test_all_get(self):
        urls_list = [
            reverse('profiles:profile'),
            reverse('profiles:user_list')
        ]
        for url in urls_list:
            response = self.client.get(url)
            self.assertEquals(200, response.status_code)
        self.client.logout()
        for url in urls_list:
            response = self.client.get(url)
            self.assertEquals(302, response.status_code)