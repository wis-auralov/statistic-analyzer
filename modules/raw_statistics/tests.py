# -*- coding: utf-8 -*-

from django.test import TestCase
from raw_statistics.helpers import xor_encode_dict
from raw_statistics.models import RawClientActionLog


class ActionSetUpTestDataMixin(object):
    # TODO: в будущем вынести в общий модуль для тестов
    @classmethod
    def setUpTestData(cls):
        cls.action_update_price_data = {
            'client_uuid': '517eac00-8438-4c88-8699-3548687001c8',
            'action_uuid': '023fd502-2028-45cc-a94a-979fcbb0d3b4',
            'dealer_uname': 'Shukunov',
            'dealer_pass': '160363',
            'params': '{}',
        }
        cls.action_auth_data = {
            'client_uuid': '517eac00-8438-4c88-8699-3548687001c8',
            'action_uuid': 'ec41783a-a825-44f3-909b-2fb608b13cb3',
            'dealer_uname': 'Shukunov',
            'dealer_pass': '160363',
            'params': {
                "client_ip": "93.90.213.46",
                "build_number": "8005008",
                "client_home_path": "\\Documents and Settings\\Work",
                "client_domain": "ND",
                "client_computer_name": "ND",
                "dealer_name": "-\u0428\u0423\u041a\u0423\u041d\u041e\u0412 \u0410.\u041a. (\u0434\u0438\u043b\u0435\u0440)",
                "client_login": "Shukunov",
                "client_os": "Windows_NT",
                "dealer_uuid": "f649de80-b1f7-11e2-93f1-002655df3ac1",
                "client_user_name": "Work",
            }
        }

        super(ActionSetUpTestDataMixin, cls).setUpTestData()


class PutRawStatisticsViewTests(ActionSetUpTestDataMixin, TestCase):
    fixtures = ['action_initial.json']

    def _check_statistics(self, response, action_data):
        self.assertEqual(response.status_code, 200)
        # проверяем, что событие сохранилось в БД
        raw_action_log = RawClientActionLog.objects.filter(
            client_uuid=action_data['client_uuid'],
            action_uuid=action_data['action_uuid'],
        )[0]
        self.assertEqual(str(raw_action_log.client_uuid),
                         action_data['client_uuid'])
        self.assertEqual(str(raw_action_log.action_uuid),
                         action_data['action_uuid'])

    def _prepared_auth_data(self):
        auth_data = self.action_auth_data
        auth_data['params'] = repr(auth_data['params'])
        return auth_data

    def test_put_statistics(self):
        response = self.client.post('/api/put_decrypt_statistics/',
                                    self.action_update_price_data)
        self._check_statistics(response, self.action_update_price_data)

    def test_put_encrypt_statistics(self):
        encode_action_data = xor_encode_dict(self.action_update_price_data)
        response = self.client.post('/api/put_statistics/', encode_action_data)
        self._check_statistics(response, self.action_update_price_data)

    # def test_auth_data_full(self):
    # TODO: необходимо 'params' перевести в строковый вид, а там,
    # где нужно обратиться по значениям делать json.loads
    #     auth_data = self._prepared_auth_data()
    #     response = self.client.post('/api/put_decrypt_statistics/',
    #                                 auth_data)
    #     self._check_statistics(response, auth_data)
    #
    # def test_auth_data_without_dealer_u_l(self):
    #     auth_data = self._prepared_auth_data()
    #     del auth_data['dealer_uname']
    #     del auth_data['dealer_pass']
    #
    #     response = self.client.post('/api/put_decrypt_statistics/',
    #                                 auth_data)
    #     self._check_statistics(response, auth_data)