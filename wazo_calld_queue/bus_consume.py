# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import datetime, logging, math

from .events import (
    QueueCallerAbandonEvent,
    QueueCallerJoinEvent,
    QueueCallerLeaveEvent,
    QueueMemberAddedEvent,
    QueueMemberPauseEvent,
    QueueMemberPenaltyEvent,
    QueueMemberRemovedEvent,
    QueueMemberRingInUseEvent,
    QueueMemberStatusEvent,
    QueueLiveStatsEvent,
    QueueAgentsStatusEvent
)

from .agent import AgentStatusHandler


stats = {}
agents = {}

logger = logging.getLogger(__name__)


class QueuesBusEventHandler(object):

    def __init__(self, bus_publisher, confd, agentd):
        self.bus_publisher = bus_publisher
        self.confd = confd
        self.agentd = agentd

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
            self._update_agents_status_cache(event, tenant_uuid)
        bus_event = QueueCallerLeaveEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_added(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        self._update_agents_status_cache(event, tenant_uuid)
        bus_event = QueueMemberAddedEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_pause(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        self._update_agents_status_cache(event, tenant_uuid)
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
        self._update_agents_status_cache(event, tenant_uuid)
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
        self._update_agents_status_cache(event, tenant_uuid)
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
        self.bus_publisher.publish(bus_event)

    def _queue_agents_status(self, event, tenant_uuid, agent):
        bus_event = QueueAgentsStatusEvent(
            event[tenant_uuid][agent],
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def get_agents_status(self, tenant_uuid):
        if tenant_uuid not in agents:
            agents[tenant_uuid] = {}
            agentList = self.confd.agents.list(tenant_uuid=tenant_uuid)
            agentStatus = self.agentd.agents.get_agent_statuses(tenant_uuid=tenant_uuid)

            for agent in agentList['items']:
                agent_fullname = " ".join(filter(None, [agent.get('firstname'), agent.get('lastname')]))

                status = next((x.__dict__ for x in agentStatus if x.__dict__.get('id') == agent['id']), {})
                agent_islogged = status.get('logged', False)
                agent_ispaused = status.get('paused', False)

                if agent['id'] not in agents[tenant_uuid]:
                    agents[tenant_uuid][agent['id']] = {
                        'id': agent['id'],
                        'number': agent['number'],
                        'fullname': agent_fullname,
                        'is_logged': agent_islogged,
                        'is_paused': agent_ispaused,
                        'is_talking': False,
                        'is_ringing': False,
                        'logged_at': "",
                        'paused_at': "",
                        'talked_at': "",
                        'talked_with_number': "",
                        'talked_with_name': ""
                    }

        return agents[tenant_uuid]

    def get_stats(self, name):
        # If the queue stats does not exist, create the object with default values || Reset if day is different
        if not stats.get(name) or (stats.get(name) and stats[name]['updated_at'] != datetime.datetime.now().day):
            stats.update({
                name: {
                    'count': 0,
                    'count_color': 'green',
                    'received': 0,
                    'abandonned': 0,
                    'answered': 0,
                    'awr': 0,
                    'waiting_calls': [],
                    'updated_at': datetime.datetime.now().day
                }
            })
        return stats[name]


    def _update_agents_status_cache(self, event, tenant_uuid):
        global agents

        eventsList = (
            'QueueCallerLeave',
            'QueueMemberStatus',
            'QueueMemberAdded',
            'QueueMemberRemoved',
            'QueueMemberPause'
        )

        if 'Event' not in event or event['Event'] not in eventsList:
            return

        handler = AgentStatusHandler(event)
        agent_id = handler.get_agent_id() or handler.find_agent_id_by_number(event, agents[tenant_uuid])
        result = handler.handle_event()

        if result and agent_id:
            self.get_agents_status(tenant_uuid)
            agents[tenant_uuid][agent_id].update(result)
            self._queue_agents_status(agents, tenant_uuid, agent_id)

    def _livestats(self, event, tenant_uuid):
        name = event['Queue']

        self.get_stats(name)

        queue_event = event['Event']
        if queue_event == "QueueCallerJoin":
            stats[name]['count'] = int(event['Count'])
            stats[name]['updated_at'] = datetime.datetime.now().day
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
            stats[name]['updated_at'] = datetime.datetime.now().day
            stats[name]['answered'] -= 1
            if stats[name]['received'] > 0:
                stats[name]['awr'] = math.ceil(stats[name]['answered'] / stats[name]['received'] * 100)
            for i in range(len(stats[name]['waiting_calls'])):
                if stats[name]['waiting_calls'][i]['uniqueid'] == event['Uniqueid']:
                    stats[name]['waiting_calls'].pop(i)
        elif queue_event == "QueueCallerLeave":
            stats[name]['count'] = int(event['Count'])
            stats[name]['updated_at'] = datetime.datetime.now().day
            stats[name]['answered'] += 1
            stats[name]['received'] += 1
            if stats[name]['received'] > 0:
                stats[name]['awr'] = math.ceil(stats[name]['answered'] / stats[name]['received'] * 100)
            for i in range(len(stats[name]['waiting_calls'])):
                if stats[name]['waiting_calls'][i]['uniqueid'] == event['Uniqueid']:
                    stats[name]['waiting_calls'].pop(i)

        #Set color depending on limit value
        stats[name]['count_color'] = "green"
        if stats[name]['count'] > 1:
            stats[name]['count_color'] = "red"

        self._queue_livestats(stats, tenant_uuid)

    def _extract_tenant_uuid(self, event):
        interface = event.get('Interface')
        if interface:
            agent_id = interface.split('-')[1].split('@')[0]
            agent = self.agentd.agents.get_agent_status(agent_id=agent_id)
            tenant_uuid = agent.tenant_uuid
        else:
            tenant_uuid = event['ChanVariable']['WAZO_TENANT_UUID']

        return tenant_uuid
