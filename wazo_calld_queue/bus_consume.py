# -*- coding: utf-8 -*-
# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_bus.resources.common.event import ArbitraryEvent

logger = logging.getLogger(__name__)


class QueuesBusEventHandler(object):

    def __init__(self, bus_publisher):
        self.bus_publisher = bus_publisher

    @staticmethod
    def _build_headers(user_uuids=None, **kwargs):
        headers = {}
        for uuid in user_uuids or []:
            headers[f'user_uuid:{uuid}'] = True

        for key, value in kwargs.items():
            if value:
                headers[key] = value
        return headers

    def subscribe(self, bus_consumer):
        bus_consumer.subscribe('QueueCallerAbandon', self._queue_caller_abandon)
        bus_consumer.subscribe('QueueCallerJoin', self._queue_caller_join)
        bus_consumer.subscribe('QueueCallerLeave', self._queue_caller_leave)
        bus_consumer.subscribe('QueueMemberAdded', self._queue_member_added)
        bus_consumer.subscribe('QueueMemberPause', self._queue_member_pause)
        bus_consumer.subscribe('QueueMemberPenalty', self._queue_member_penalty)
        bus_consumer.subscribe('QueueMemberRemoved', self._queue_member_removed)
        bus_consumer.subscribe('QueueMemberRinginuse', self._queue_member_ringinuse)
        bus_consumer.subscribe('QueueMemberStatus', self._queue_member_status)

    def _queue_caller_abandon(self, event):
        bus_event = ArbitraryEvent(
            name='queue_caller_abandon',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.caller_abandon'
        self.bus_publisher.publish(bus_event)

    def _queue_caller_join(self, event):
        bus_event = ArbitraryEvent(
            name='queue_caller_join',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.caller_join'
        headers = self._build_headers(
            user_uuids=[event.get('ChanVariable', {}).get('XIVO_USERUUID')],
            tenant_uuid=event['ChanVariable']['WAZO_TENANT_UUID'],
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_caller_leave(self, event):
        bus_event = ArbitraryEvent(
            name='queue_caller_leave',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.caller_leave'
        headers = self._build_headers(
            user_uuids=[event.get('ChanVariable', {}).get('XIVO_USERUUID')],
            tenant_uuid=event['ChanVariable']['WAZO_TENANT_UUID'],
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_added(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_added',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_added'
        headers = self._build_headers(
            user_uuids=[event.get('ChanVariable', {}).get('XIVO_USERUUID')],
            tenant_uuid=event['ChanVariable']['WAZO_TENANT_UUID'],
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_pause(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_pause',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_pause'
        headers = self._build_headers(
            user_uuids=[event.get('ChanVariable', {}).get('XIVO_USERUUID')],
            tenant_uuid=event['ChanVariable']['WAZO_TENANT_UUID'],
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_penalty(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_penalty',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_penalty'
        headers = self._build_headers(
            user_uuids=[event.get('ChanVariable', {}).get('XIVO_USERUUID')],
            tenant_uuid=event['ChanVariable']['WAZO_TENANT_UUID'],
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_removed(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_removed',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_removed'
        headers = self._build_headers(
            user_uuids=[event.get('ChanVariable', {}).get('XIVO_USERUUID')],
            tenant_uuid=event['ChanVariable']['WAZO_TENANT_UUID'],
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_ringinuse(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_ringinuse',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_ringinuse'
        headers = self._build_headers(
            user_uuids=[event.get('ChanVariable', {}).get('XIVO_USERUUID')],
            tenant_uuid=event['ChanVariable']['WAZO_TENANT_UUID'],
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_status(self, event):
        logger.warning("===============_queue_member_status===============")
        logger.warning(event)
        bus_event = ArbitraryEvent(
            name='queue_member_status',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_status'
        headers = self._build_headers(
            user_uuids=[event.get('ChanVariable', {}).get('XIVO_USERUUID')],
            tenant_uuid=event['ChanVariable']['WAZO_TENANT_UUID'],
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _publish(self, bus_event):
        self.bus_publisher.publish(bus_event, headers={'name': bus_event.name})
