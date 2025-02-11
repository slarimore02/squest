from guardian.shortcuts import get_objects_for_user
from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Request, Instance
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiRequestList(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestList, self).setUp()
        self.get_request_list_url = reverse('api_request_list')
        Request.objects.create(
            fill_in_survey={},
            admin_fill_in_survey={'float_var': 1.8},
            instance=self.test_instance,
            operation=self.create_operation_test,
            user=self.standard_user
        )
        Request.objects.create(
            fill_in_survey={},
            admin_fill_in_survey={'float_var': 1.8},
            instance=self.test_instance,
            operation=self.update_operation_test,
            user=self.standard_user
        )
        Request.objects.create(
            fill_in_survey={},
            admin_fill_in_survey={'float_var': 1.8},
            instance=self.test_instance_2,
            operation=self.create_operation_test,
            user=self.standard_user_2
        )
        Request.objects.create(
            fill_in_survey={},
            admin_fill_in_survey={'float_var': 1.8},
            instance=self.test_instance_2,
            operation=self.update_operation_test,
            user=self.standard_user_2
        )

    def test_admin_get_all_requests(self):
        response = self.client.get(self.get_request_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Request.objects.count())
        self.assertIn('admin_fill_in_survey', response.data['results'][-1].keys())

    def test_customer_get_his_requests(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_request_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'],
            get_objects_for_user(self.standard_user, 'service_catalog.view_request').count()
        )
        self.assertNotEqual(
            response.data['count'],
            Request.objects.count()
        )
        self.assertNotIn('admin_fill_in_survey', response.data['results'][-1].keys())
        request_id_list = [request['id'] for request in response.data['results']].sort()
        request_id_list_db = [request.id for request in get_objects_for_user(self.standard_user, 'service_catalog.view_request')].sort()
        self.assertEqual(request_id_list, request_id_list_db)

    def test_cannot_get_request_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_request_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
