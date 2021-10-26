# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_bus.resources.common.event import ArbitraryEvent


logger = logging.getLogger(__name__)


class QueueBusPublisher(object):

    def __init__(self, bus_publisher):
        self.bus_publisher = bus_publisher

    def _queue_log(self, event):
        bus_event = ArbitraryEvent(
            name='queue_log',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.queue_log'
        self.bus_publisher.publish(bus_event)
