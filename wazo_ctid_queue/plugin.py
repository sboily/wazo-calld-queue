# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_amid_client import Client as AmidClient
from xivo_auth_client import Client as AuthClient

from .resources import (
    QueuesResource,
    QueueResource,
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

        queues_service = QueueService(amid_client)

        queues_bus_event_handler = QueuesBusEventHandler(bus_publisher)
        queues_bus_event_handler.subscribe(bus_consumer)

        api.add_resource(QueuesResource, '/queues', resource_class_args=[queues_service])
        api.add_resource(QueueResource, '/queues/<queue_name>', resource_class_args=[queues_service])
