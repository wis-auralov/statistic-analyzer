# -*- coding: utf-8 -*-

from django.test import TestCase
from raw_statistics.tests import ActionSetUpTestDataMixin
from raw_statistics.views import PutRawStatisticsView
from statistics.models import Dealer, Client
from statistics.signals import client_login_action
from kmclient.models import User as KmClientDealer


class CreateOrUpdateClientSignalTests(ActionSetUpTestDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(CreateOrUpdateClientSignalTests, cls).setUpTestData()
        KmClientDealer.objects.create(
            id=1,
            uuid=cls.action_auth_data['params']['dealer_uuid'],
            name=u'-ШУКУНОВ А.К. (дилер)',
            active=1,
            props=u'qwe',
            uname=cls.action_auth_data['dealer_uname'],
            pass_field=cls.action_auth_data['dealer_pass'],
        )

    def check_dealer_exist(self, dealer_uuid):
        dealer = Dealer.objects.filter(
            uuid=dealer_uuid
        )
        self.assertEqual(dealer.count(), 1)

    def check_client_exist(self, client_uuid):
        client = Client.objects.get(uuid=client_uuid)
        self.assertEqual(client.ip,
                         self.action_auth_data['params']['client_ip'])

    def test_create_client(self):
        client_login_action.send(
            PutRawStatisticsView,
            client_uuid=self.action_auth_data['client_uuid'],
            dealer_uname=self.action_auth_data['dealer_uname'],
            dealer_pass=self.action_auth_data['dealer_pass'],
            params=self.action_auth_data['params'],
        )

        self.check_dealer_exist(self.action_auth_data['params']['dealer_uuid'])
        self.check_client_exist(self.action_auth_data['client_uuid'])

    def test_create_client_without_dealer_uuid(self):
        dealer_uuid = self.action_auth_data['params']['dealer_uuid']
        del self.action_auth_data['params']['dealer_uuid']

        client_login_action.send(
            PutRawStatisticsView,
            client_uuid=self.action_auth_data['client_uuid'],
            dealer_uname=self.action_auth_data['dealer_uname'],
            dealer_pass=self.action_auth_data['dealer_pass'],
            params=self.action_auth_data['params'],
        )

        self.check_dealer_exist(dealer_uuid)
        self.check_client_exist(self.action_auth_data['client_uuid'])