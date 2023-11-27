# -*- coding: utf-8 -*-
# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from .events import (
    QueueCallerAbandonEvent,
    QueueCallerJoinEvent,
    QueueCallerLeaveEvent,
    QueueMemberAddedEvent,
    QueueMemberPauseEvent,
    QueueMemberPenaltyEvent,
    QueueMemberRemovedEvent,
    QueueMemberRingInUseEvent,
    QueueMemberStatusEvent
)


logger = logging.getLogger(__name__)


class QueuesBusEventHandler(object):

    def __init__(self, bus_publisher):
        self.bus_publisher = bus_publisher

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
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueCallerAbandonEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_caller_join(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueCallerJoinEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_caller_leave(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueCallerLeaveEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_added(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueMemberAddedEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_pause(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueMemberPauseEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_penalty(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueMemberPenaltyEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_removed(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueMemberRemovedEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_ringinuse(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueMemberRingInUseEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_status(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = QueueMemberStatusEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _extract_tenant_uuid(self, event):
        tenant_uuid = event['ChanVariable']['WAZO_TENANT_UUID']
        return tenant_uuid
