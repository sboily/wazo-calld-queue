# -*- coding: utf-8 -*-
# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_amid_client import Client as AmidClient
from wazo_auth_client import Client as AuthClient
from wazo_confd_client import Client as ConfdClient
from wazo_agentd_client import Client as AgentdClient

from .resources import (
    QueuesResource,
    QueueResource,
    QueueAddMemberResource,
    QueueRemoveMemberResource,
    QueuePauseMemberResource,
    QueueLiveStatsResource,
    QueueAgentsStatusResource,
    QueueWithdrawCallerResource
    )
from .services import QueueService
from .bus_consume import QueuesBusEventHandler


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        ari = dependencies['ari']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        bus_consumer = dependencies['bus_consumer']
        bus_publisher = dependencies['bus_publisher']

        amid_client = AmidClient(**config['amid'])
        confd_client = ConfdClient(**config['confd'])
        agentd_client = AgentdClient(**config['agentd'])

        token_changed_subscribe(amid_client.set_token)
        token_changed_subscribe(confd_client.set_token)
        token_changed_subscribe(agentd_client.set_token)

        queues_bus_event_handler = QueuesBusEventHandler(bus_publisher, confd_client, agentd_client)
        queues_bus_event_handler.subscribe(bus_consumer)

        queues_service = QueueService(amid_client, ari.client, confd_client, agentd_client, queues_bus_event_handler)

        api.add_resource(QueuesResource, '/queues', resource_class_args=[queues_service])
        api.add_resource(QueueResource, '/queues/<queue_name>', resource_class_args=[queues_service])
        api.add_resource(QueueAddMemberResource, '/queues/<queue_name>/add_member', resource_class_args=[queues_service])
        api.add_resource(QueueRemoveMemberResource, '/queues/<queue_name>/remove_member', resource_class_args=[queues_service])
        api.add_resource(QueuePauseMemberResource, '/queues/<queue_name>/pause_member', resource_class_args=[queues_service])
        api.add_resource(QueueLiveStatsResource, '/queues/<queue_name>/livestats', resource_class_args=[queues_service])
        api.add_resource(QueueAgentsStatusResource, '/queues/agents_status', resource_class_args=[queues_service])
        api.add_resource(QueueWithdrawCallerResource, '/queues/<queue_name>/withdraw', resource_class_args=[queues_service])
