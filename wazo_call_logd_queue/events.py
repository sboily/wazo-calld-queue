# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_bus.resources.common.event import ServiceEvent


class QueueLogEvent(ServiceEvent):
    service = 'calld'
    name = 'queue_log'
    routing_key_fmt = 'calls.queues.queue_log'
    required_acl_fmt = 'events.queues'

    def __init__(self, content):
        super().__init__(content)
