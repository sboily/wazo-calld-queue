# -*- coding: utf-8 -*-
# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from .events import QueueLogEvent


logger = logging.getLogger(__name__)


class QueueBusPublisher:

    def __init__(self, bus_publisher):
        self.bus_publisher = bus_publisher

    def _queue_log(self, event):
        bus_event = QueueLogEvent(
            event
        )
        self.bus_publisher.publish(bus_event)
