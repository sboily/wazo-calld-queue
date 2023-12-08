# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging, math

from .events import (
    AgentConnectEvent,
    QueueCallerAbandonEvent,
    QueueCallerJoinEvent,
    QueueCallerLeaveEvent,
    QueueMemberAddedEvent,
    QueueMemberPauseEvent,
    QueueMemberPenaltyEvent,
    QueueMemberRemovedEvent,
    QueueMemberRingInUseEvent,
    QueueMemberStatusEvent,
    QueueLiveStatsEvent
)


stats = {}

# stats = [
# {'name', 'count', 'received', 'abandonned', 'answered', 'awr'}
# ]

MY_TENANT = '6209d5e0-4015-4853-ab2b-2e556bef5e46'

logger = logging.getLogger(__name__)


class QueuesBusEventHandler(object):

    def __init__(self, bus_publisher):
        self.bus_publisher = bus_publisher

    def subscribe(self, bus_consumer):
        bus_consumer.subscribe('AgentConnect', self._agent_connect)
        bus_consumer.subscribe('QueueCallerAbandon', self._queue_caller_abandon)
        bus_consumer.subscribe('QueueCallerJoin', self._queue_caller_join)
        bus_consumer.subscribe('QueueCallerLeave', self._queue_caller_leave)
        bus_consumer.subscribe('QueueMemberAdded', self._queue_member_added)
        bus_consumer.subscribe('QueueMemberPause', self._queue_member_pause)
        bus_consumer.subscribe('QueueMemberPenalty', self._queue_member_penalty)
        bus_consumer.subscribe('QueueMemberRemoved', self._queue_member_removed)
        bus_consumer.subscribe('QueueMemberRinginuse', self._queue_member_ringinuse)
        bus_consumer.subscribe('QueueMemberStatus', self._queue_member_status)

    def _agent_connect(self, event):
        #print(event)
        tenant_uuid = self._extract_tenant_uuid(event)
        bus_event = AgentConnectEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_caller_abandon(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        if event['Context'] == "queue":
            self._livestats(event, tenant_uuid)
        bus_event = QueueCallerAbandonEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_caller_join(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        # Check if the call concerns a Queue and not a group
        if event['Context'] == "queue":
            self._livestats(event, tenant_uuid)
        bus_event = QueueCallerJoinEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_caller_leave(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        if event['Context'] == "queue":
            self._livestats(event, tenant_uuid)
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

    def _queue_livestats(self, event, tenant_uuid):
        bus_event = QueueLiveStatsEvent(
            event,
            tenant_uuid
        )
        print(bus_event)
        self.bus_publisher.publish(bus_event)

    def _livestats(self, event, tenant_uuid):
        name = event['Queue']

        # If the queue stats doesnot exist, create the object with default values
        if not stats.get(name):
            stats.update({
                name: {
                    'count': 0,
                    'count_color': 'green',
                    'received': 0,
                    'abandonned': 0,
                    'answered': 0,
                    'awr': 0,
                    'waiting_calls': []
                }
            })
        
        queue_event = event['Event']
        if queue_event == "QueueCallerJoin":
            stats[name]['count'] = int(event['Count'])
            stats[name]['waiting_calls'].append({
                'uniqueid': event['Uniqueid'],
                'calleridnum': event['CallerIDNum'],
                'calleridname': event['CallerIDName'],
                'position': event['Position'],
                'channelstate': event['ChannelState'],
                'channelstatedesc': event['ChannelStateDesc'],
                'time': event['ChanVariable']['WAZO_ANSWER_TIME'],
                'entryexten': event['ChanVariable']['WAZO_ENTRY_EXTEN']
            })
        elif queue_event == "QueueCallerAbandon":
            stats[name]['abandonned'] += 1
            stats[name]['answered'] -= 1
            if stats[name]['received'] > 0:
                stats[name]['awr'] = math.ceil(stats[name]['answered'] / stats[name]['received'] * 100)
            for i in range(len(stats[name]['waiting_calls'])):
                if stats[name]['waiting_calls'][i]['uniqueid'] == event['Uniqueid']:
                    stats[name]['waiting_calls'].pop(i)
        elif queue_event == "QueueCallerLeave":
            stats[name]['count'] = int(event['Count'])
            stats[name]['answered'] += 1
            stats[name]['received'] += 1
            if stats[name]['received'] > 0:
                stats[name]['awr'] = math.ceil(stats[name]['answered'] / stats[name]['received'] * 100)
            for i in range(len(stats[name]['waiting_calls'])):
                if stats[name]['waiting_calls'][i]['uniqueid'] == event['Uniqueid']:
                    stats[name]['waiting_calls'].pop(i)

        #Set color depending on limit value
        stats[name]['count_color'] = "green";
        if stats[name]['count'] > 0:
            stats[name]['count_color'] = "red"

        self._queue_livestats(stats, tenant_uuid)

    def _extract_tenant_uuid(self, event):
        try:
            tenant_uuid = event['ChanVariable']['WAZO_TENANT_UUID']
        except:
            tenant_uuid = MY_TENANT
        return tenant_uuid
