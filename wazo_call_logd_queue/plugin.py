# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resources import (
    QueueLogStoreResource,
    QueueLogRequireResource
    )
from .services import Services
from .bus_publish import QueueBusPublish

class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        dao = dependencies['dao']
        bus = dependencies['bus_publisher']

        publisher = QueueBusPublish(bus)
        services = QueueService(dao, publisher)

        api.add_resource(QueueLogStoreResource, '/queues/queue_log/store', resource_class_args=[services])
        api.add_resource(QueueLogRequireResource, '/queues/queue_log/require', resource_class_args=[services])
