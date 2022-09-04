# -*- coding: utf-8 -*-
# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import re
from xivo_bus.resources.common.event import ArbitraryEvent

logger = logging.getLogger(__name__)


class QueuesBusEventHandler(object):

    def __init__(self, bus_publisher, confd_client):
        self.bus_publisher = bus_publisher
        self.confd_client = confd_client

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
        tenant_uuid, user_uuids = self._extract_tenant_from_event(event)
        headers = self._build_headers(
            user_uuids=user_uuids,
            tenant_uuid=tenant_uuid,
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_caller_leave(self, event):
        bus_event = ArbitraryEvent(
            name='queue_caller_leave',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.caller_leave'
        tenant_uuid, user_uuids = self._extract_tenant_from_event(event)
        headers = self._build_headers(
            user_uuids=user_uuids,
            tenant_uuid=tenant_uuid,
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_added(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_added',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_added'
        tenant_uuid, user_uuids = self._extract_tenant_from_event(event)
        headers = self._build_headers(
            user_uuids=user_uuids,
            tenant_uuid=tenant_uuid,
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_pause(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_pause',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_pause'
        tenant_uuid, user_uuids = self._extract_tenant_from_event(event)
        headers = self._build_headers(
            user_uuids=user_uuids,
            tenant_uuid=tenant_uuid,
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_penalty(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_penalty',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_penalty'
        tenant_uuid, user_uuids = self._extract_tenant_from_event(event)
        headers = self._build_headers(
            user_uuids=user_uuids,
            tenant_uuid=tenant_uuid,
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_removed(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_removed',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_removed'
        tenant_uuid, user_uuids = self._extract_tenant_from_event(event)
        headers = self._build_headers(
            user_uuids=user_uuids,
            tenant_uuid=tenant_uuid,
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_ringinuse(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_ringinuse',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_ringinuse'
        tenant_uuid, user_uuids = self._extract_tenant_from_event(event)
        headers = self._build_headers(
            user_uuids=user_uuids,
            tenant_uuid=tenant_uuid,
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _queue_member_status(self, event):
        bus_event = ArbitraryEvent(
            name='queue_member_status',
            body=event,
            required_acl='events.queues'
        )
        bus_event.routing_key = 'calls.queues.member_status'
        tenant_uuid, user_uuids = self._extract_tenant_from_event(event)
        headers = self._build_headers(
            user_uuids=user_uuids,
            tenant_uuid=tenant_uuid,
        )
        self.bus_publisher.publish(bus_event, headers=headers)

    def _publish(self, bus_event):
        self.bus_publisher.publish(bus_event, headers={'name': bus_event.name})

    def _extract_tenant_from_event(self, event):
        logger.debug(event)
        user_uuids = []
        tenant_uuid = None

        if 'ChanVariable' in event:
            user_uuids = [event['ChanVariable']['XIVO_USERUUID']]
            tenant_uuid = event['ChanVariable']['WAZO_TENANT_UUID']
        elif 'Interface' in event:
            agent_regex = re.match(r'Local/id-(\d+)@agentcallback', event["Interface"])
            user_regex = re.match(r'Local/(\S+)@usersharedlines', event["Interface"])
            if len(agent_regex.groups()):
                agent_id = agent_regex.group(1)
                logger.debug("agent id is " + agent_id)
                agent = self.confd_client.agents.get(agent_id)
                logger.debug(agent)
                tenant_uuid = agent["tenant_uuid"]
                user_uuids = [user["uuid"] for user in agent["users"]]
            elif len(user_regex.groups()):
                user_id = user_regex.group(1)
                logger.debug("user id is " + user_id)
                user = self.confd_client.users.get(user_id)
                logger.debug(user)
                tenant_uuid = user["tenant_uuid"]
                user_uuids = [user_id]

        logger.debug("tenant uuid is " + tenant_uuid)
        logger.debug("user uuid :" + ','.join(user_uuids))
        return tenant_uuid, user_uuids
