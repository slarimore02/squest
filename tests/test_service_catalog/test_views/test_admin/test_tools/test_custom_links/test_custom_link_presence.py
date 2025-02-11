from django.urls import reverse

from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLink


class CustomLinksPresenceTest(BaseTestCustomLink):

    def setUp(self):
        super(CustomLinksPresenceTest, self).setUp()

        self.args = {
            "instance_id": self.test_instance.id
        }
        self.test_instance.spoc = self.standard_user
        self.test_instance.save()
        self.instance_detail_url = reverse('service_catalog:instance_details', kwargs=self.args)

    def _validate_can_see_button(self):
        response = self.client.get(self.instance_detail_url)
        expected_button = 'custom_link'
        self.assertContains(response, expected_button)

    def _validate_cannot_see_button(self):
        response = self.client.get(self.instance_detail_url)
        expected_button = 'custom_link'
        self.assertNotContains(response, expected_button)

    def test_custom_link_present(self):
        self._validate_can_see_button()

    def test_custom_link_admin_only(self):
        self.test_custom_link.is_admin_only = True
        self.test_custom_link.save()
        self._validate_can_see_button()
        self.client.login(username=self.standard_user, password=self.common_password)
        self._validate_cannot_see_button()

    def test_custom_link_disabled(self):
        self.test_custom_link.enabled = False
        self.test_custom_link.save()
        self._validate_cannot_see_button()
        self.client.login(username=self.standard_user, password=self.common_password)
        self._validate_cannot_see_button()

    def test_custom_link_when(self):
        self.test_custom_link.when = "instance.spec.key1 == 'value1'"
        self.test_custom_link.save()
        self.test_instance.spec = {
            "key1": "value1"
        }
        self.test_instance.save()
        self._validate_can_see_button()
        self.test_instance.spec = {
            "key1": "value2"
        }
        self.test_instance.save()
        self._validate_cannot_see_button()

    def test_custom_link_dropdown(self):
        self.test_instance.spec = {
            "my_list": ["item1",
                        "item2"]
        }
        self.test_instance.save()
        self.test_custom_link.loop = "{{ instance.spec.my_list }}"
        self.test_custom_link.save()

        response = self.client.get(self.instance_detail_url)
        self.assertContains(response, "item1")
        self.assertContains(response, "item2")
