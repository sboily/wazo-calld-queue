# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import datetime, logging, math, re

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

#MY_TENANT = '6209d5e0-4015-4853-ab2b-2e556bef5e46'

logger = logging.getLogger(__name__)

AGENT_ID_FROM_IFACE = re.compile(r'^Local/id-(\d+)@agentcallback$')
MEMBER_NUM_FROM_AGENT = re.compile(r'^Agent/(\d+)$')

class QueuesBusEventHandler(object):

    def __init__(self, bus_publisher, confd, agentd, MY_TENANT):
        self.bus_publisher = bus_publisher
        self.confd = confd
        self.agentd = agentd
        self.MY_TENANT = MY_TENANT

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

    def _queue_agents_status(self, event, tenant_uuid, agent):
        bus_event = QueueAgentsStatusEvent(
            event[tenant_uuid][agent],
            tenant_uuid
        )
        self.bus_publisher.publish(bus_event)

    def get_agents_status(self, tenant_uuid):

        if not agents.get(tenant_uuid):
            agents.update({
                tenant_uuid: {}
            })
            agentList = self.confd.agents.list(tenant_uuid=tenant_uuid)
            agentStatus = self.agentd.agents.get_agent_statuses(tenant_uuid=tenant_uuid)

            for agent in agentList['items']:
                agent_fullname = ""
                if str(agent['firstname']) != "None":
                    agent_fullname = str(agent['firstname'])
                if str(agent['lastname']) != "None":
                    agent_fullname += " " + str(agent['lastname'])

                status = [x.__dict__ for x in agentStatus if x.__dict__.get('id') == agent['id']]
                if status[0].get('logged') is not None:
                    agent_islogged = status[0].get('logged')
                else:
                    agent_islogged = False
                if status[0].get('paused') is not None:
                    agent_ispaused = status[0].get('paused') 
                else:
                    agent_ispaused = False

                try:
                    agent_first_queue = agent['queues'][0].get('name')
                except:
                    agent_first_queue = False

                if not agents[tenant_uuid].get(agent['id']):
                    agents[tenant_uuid].update({
                        agent['id']: {
                            'id': agent['id'],
                            'number': agent['number'],
                            'fullname': agent_fullname,
                            'queue': agent_first_queue,
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
                    })
        print(agents[tenant_uuid])
        return agents[tenant_uuid]

    def add_agent(self, tenant_uuid, agent, member):
        if not agents[tenant_uuid].get(agent):
            agents[tenant_uuid].update({
                agent: {
                    'id': agent,
                    'number': member,
                    'fullname': member,
                    'queue': "",
                    'is_logged': False,
                    'is_paused': False,
                    'is_talking': False,
                    'is_ringing': False,
                    'logged_at': "",
                    'paused_at': "",
                    'talked_at': "",
                    'talked_with_number': "",
                    'talked_with_name': ""
                }
            })
        #print(agents[tenant_uuid].get(agent))
        #print(agents[tenant_uuid])

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

        agent = 0

        # QueueCallerLeave Get info about call
        if event['Event'] == "QueueCallerLeave" and event['ConnectedLineNum'] != "<unknown>":
            agentID = event['ConnectedLineNum']
            if agents.get(tenant_uuid):
                for i in range(len(agents[tenant_uuid])):
                    if agents[tenant_uuid].get(i):
                        if agents[tenant_uuid][i]['number'] == agentID:
                            agents[tenant_uuid][i]['talked_with_number'] = event['CallerIDNum']
                            agents[tenant_uuid][i]['talked_with_name'] = event['CallerIDName']
                            agent = i
                            break
        
        # Check if agents for this tenant exists
        if event['Event'] != "QueueCallerLeave" and event['Membership'] == "dynamic":
            interface = AGENT_ID_FROM_IFACE.match(event['Interface'])
            agent = int(interface.group(1))
            if not agents.get(tenant_uuid):
                self.get_agents_status(tenant_uuid)
            if not agents[tenant_uuid].get(agent):
                member = MEMBER_NUM_FROM_AGENT.match(event['MemberName'])
                member_num = int(member.group(1))
                self.add_agent(tenant_uuid, agent, member_num)
            if agents[tenant_uuid][agent]['queue'] != event['Queue']:
                agents[tenant_uuid][agent]['queue'] = event['Queue']

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
            agents[tenant_uuid][agent]['is_logged'] = True
            agents[tenant_uuid][agent]['interface'] = event['StateInterface']
            agents[tenant_uuid][agent]['logged_at'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f') #LoginTime

        if event['Event'] == "QueueMemberRemoved" and event['Membership'] == "dynamic":
            # Handle disconnection
            agents[tenant_uuid][agent]['is_logged'] = False
            agents[tenant_uuid][agent]['is_paused'] = False
            agents[tenant_uuid][agent]['is_talking'] = False
            agents[tenant_uuid][agent]['is_ringing'] = False
            agents[tenant_uuid][agent]['logged_at'] = ""
            agents[tenant_uuid][agent]['paused_at'] = ""
            agents[tenant_uuid][agent]['talked_at'] = ""
            agents[tenant_uuid][agent]['talked_with_number'] = ""
            agents[tenant_uuid][agent]['talked_with_name'] = ""

        if event['Event'] == "QueueMemberPause" and event['Membership'] == "dynamic":
            # Handle pause
            if not agents[tenant_uuid].get(agent):
                agents[tenant_uuid].update({agent: {}})
            if event['Paused'] == "1":
                agents[tenant_uuid][agent]['is_paused'] = True
                agents[tenant_uuid][agent]['paused_at'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f') #LastPause
            else:
                agents[tenant_uuid][agent]['is_paused'] = False
                agents[tenant_uuid][agent]['paused_at'] = ""

        if agent != 0:
            self._queue_agents_status(agents, tenant_uuid, agent)

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
            tenant_uuid = self.MY_TENANT
        return tenant_uuid
