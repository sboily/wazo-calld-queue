# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
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


stats = {}
agents = {}

MY_TENANT = '6209d5e0-4015-4853-ab2b-2e556bef5e46'

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
            self._agents_status(event, tenant_uuid)
        bus_event = QueueCallerLeaveEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_added(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        self._agents_status(event, tenant_uuid)
        bus_event = QueueMemberAddedEvent(
            event,
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def _queue_member_pause(self, event):
        tenant_uuid = self._extract_tenant_uuid(event)
        self._agents_status(event, tenant_uuid)
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
        self._agents_status(event, tenant_uuid)
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
        self._agents_status(event, tenant_uuid)
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

    def _queue_agents_status(self, event, tenant_uuid):
        bus_event = QueueAgentsStatusEvent(
            event[tenant_uuid],
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def get_agents_status(self, tenant_uuid):
        if not agents.get(tenant_uuid):
            agents.update({
                tenant_uuid: {}
            })

            agentList = self.confd.agents.list(tenant_uuid=tenant_uuid)

            for agent in agentList['items']:
                agent_id = "Agent/" + agent['number']
                agent_fullname = ""
                if str(agent['firstname']) != "None":
                    agent_fullname = str(agent['firstname']) + " "
                if str(agent['lastname']) != "None":
                    agent_fullname += str(agent['lastname'])

                if not agents[tenant_uuid].get(agent_id):
                    agents[tenant_uuid].update({
                        agent_id: {
                            'id': agent['id'],
                            'fullname': agent_fullname,
                            'is_loggued': False,
                            'is_paused': False,
                            'is_talking': False,
                            'is_ringing': False,
                            'loggued_at': "",
                            'paused_at': "",
                            'talked_at': "",
                            'talked_with_number': "",
                            'talked_with_name': "",
                            'interface': ""
                        }
                    })
        return agents[tenant_uuid]

    def get_stats(self, name):
        # If the queue stats doesnot exist, create the object with default values || Reset if day is different
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


    def _agents_status(self, event, tenant_uuid):

        # QueueCallerLeave Get info about call
        if event['Event'] == "QueueCallerLeave" and event['ConnectedLineNum'] != "<unknown>":
            agentID = "Agent/" + event['ConnectedLineNum']
            try:
                agents[tenant_uuid][agentID]['talked_with_number'] = event['CallerIDNum']
            except:
                pass 
            
            try:
                agents[tenant_uuid][agentID]['talked_with_name'] = event['CallerIDName']
            except:
                pass
        
        # Check if agents for this tenant exists
        if event['Event'] != "QueueCallerLeave":
            agent = event['MemberName']
            if not agents.get(tenant_uuid) or not agents[tenant_uuid].get(agent):
                self.get_agents_status(tenant_uuid)

        # QueueMemberStatus
        if event['Event'] == "QueueMemberStatus" and event['Membership'] == "dynamic":
            if event['Status'] == "6":
                # Ringing
                agents[tenant_uuid][agent]['is_ringing'] = True
            if event['Status'] == "2":
                # In comm
                agents[tenant_uuid][agent]['is_talking'] = True
                agents[tenant_uuid][agent]['is_ringing'] = False
                agents[tenant_uuid][agent]['talked_at'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

            if event['Status'] == "1":
                # Hangup
                agents[tenant_uuid][agent]['is_talking'] = False
                agents[tenant_uuid][agent]['is_ringing'] = False
                agents[tenant_uuid][agent]['talked_at'] = ""
                agents[tenant_uuid][agent]['talked_with_number'] = ""
                agents[tenant_uuid][agent]['talked_with_name'] = ""

        if event['Event'] == "QueueMemberAdded" and event['Membership'] == "dynamic":
            # Handle connection
            agents[tenant_uuid][agent]['is_loggued'] = True
            agents[tenant_uuid][agent]['interface'] = event['StateInterface']
            agents[tenant_uuid][agent]['loggued_at'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f') #LoginTime

        if event['Event'] == "QueueMemberRemoved" and event['Membership'] == "dynamic":
            # Handle disconnection
            agents[tenant_uuid][agent]['is_loggued'] = False
            agents[tenant_uuid][agent]['is_paused'] = False
            agents[tenant_uuid][agent]['is_talking'] = False
            agents[tenant_uuid][agent]['is_ringing'] = False
            agents[tenant_uuid][agent]['loggued_at'] = ""
            agents[tenant_uuid][agent]['paused_at'] = ""
            agents[tenant_uuid][agent]['talked_at'] = ""
            agents[tenant_uuid][agent]['talked_with_number'] = ""
            agents[tenant_uuid][agent]['talked_with_name'] = ""

        if event['Event'] == "QueueMemberPause" and event['Membership'] == "dynamic":
            # Handle pause
            agent = event['MemberName']
            if event['Paused'] == "1":
                agents[tenant_uuid][agent]['is_paused'] = True
                agents[tenant_uuid][agent]['paused_at'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f') #LastPause
            else:
                agents[tenant_uuid][agent]['is_paused'] = False
                agents[tenant_uuid][agent]['paused_at'] = ""

        self._queue_agents_status(agents, tenant_uuid)

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
        stats[name]['count_color'] = "green";
        if stats[name]['count'] > 1:
            stats[name]['count_color'] = "red"

        self._queue_livestats(stats, tenant_uuid)

    def _extract_tenant_uuid(self, event):
        try:
            tenant_uuid = event['ChanVariable']['WAZO_TENANT_UUID']
        except:
            tenant_uuid = MY_TENANT
        return tenant_uuid
