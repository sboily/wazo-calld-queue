# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_amid_client import Client as AmidClient
from wazo_auth_client import Client as AuthClient

from .resources import (
    QueuesResource,
    QueueResource,
    QueueAddMemberResource,
    QueueRemoveMemberResource,
    QueuePauseMemberResource,
    QueueLogStoreResource,
    QueueLogRequireResource,
    )
from .services import QueueService
from .bus_consume import QueuesBusEventHandler


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        bus_publisher = dependencies['bus_publisher']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        bus_consumer = dependencies['bus_consumer']
        bus_publisher = dependencies['bus_publisher']

        amid_client = AmidClient(**config['amid'])

        token_changed_subscribe(amid_client.set_token)

        queues_bus_event_handler = QueuesBusEventHandler(bus_publisher)
        queues_bus_event_handler.subscribe(bus_consumer)

        queues_service = QueueService(amid_client, queues_bus_event_handler)

        api.add_resource(QueuesResource, '/queues', resource_class_args=[queues_service])
        api.add_resource(QueueResource, '/queues/<queue_name>', resource_class_args=[queues_service])
        api.add_resource(QueueAddMemberResource, '/queues/<queue_name>/add_member', resource_class_args=[queues_service])
        api.add_resource(QueueRemoveMemberResource, '/queues/<queue_name>/remove_member', resource_class_args=[queues_service])
        api.add_resource(QueuePauseMemberResource, '/queues/<queue_name>/pause_member', resource_class_args=[queues_service])
        api.add_resource(QueueLogStoreResource, '/queues/queue_log/store', resource_class_args=[queues_service])
        api.add_resource(QueueLogRequireResource, '/queues/queue_log/require', resource_class_args=[queues_service])
