# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from .bus_consume import QueuesBusEventHandler


class QueueService(object):

    def __init__(self, amid, confd, ari, agentd, publisher):
        self.amid = amid
        self.confd = confd
        self.ari = ari
        self.agentd = agentd
        self.publisher = publisher

    def list_queues(self):
        queues = self.amid.action('queuesummary')
        q = []
        for queue in queues:
            if queue.get('Event') == 'QueueSummary':
                q.append(self._queues(queue))

        return q


    def get_queue(self, queue_name):
        queue = self.amid.action('queuestatus', {'Queue': queue_name})
        q = {'members' : []}
        for ev in queue:
            if ev.get('Event') == 'QueueParams':
                q.update(self._queue(ev))
            if ev.get('Event') == 'QueueMember':
                q['members'].append(self._member(ev))
        return q

    def add_queue_member(self, queue_name, member):
        add_member = {
            'Queue': queue_name,
            'Interface': member.get('interface'),
            'Penalty': member.get('penalty'),
            'Paused': member.get('paused'),
            'MemberName': member.get('member_name'),
            'StateInterface': member.get('state_interface')
        }
        return self.amid.action('queueadd', add_member)


    def remove_queue_member(self, queue_name, interface):
        remove_member = {
            'Queue': queue_name,
            'Interface': interface
        }
        return self.amid.action('queueremove', remove_member)

    def pause_queue_member(self, queue_name, params):
        pause_member = {
            'Interface': params.get('interface'),
            'Paused': params.get('paused'),
            'Queue':  queue_name,
            'Reason': params.get('reason')
        }
        return self.amid.action('queuepause', pause_member)


    def livestats(self, queue_name):
        return QueuesBusEventHandler.get_stats(self, queue_name)

    def agents_status(self, tenant_uuid):
        return QueuesBusEventHandler.get_agents_status(self, tenant_uuid)

    def _queues(self, queue):
        return {'logged_in': queue['LoggedIn'],
                'available': queue['Available'],
                'talk_time': queue['TalkTime'],
                'longest_hold_time': queue['LongestHoldTime'],
                'queue': queue['Queue'],
                'talking': queue['Talking'],
                'hold_time': queue['HoldTime'],
                'callers': queue['Callers'],
                }

    def _queue(self, queue):
        return {'service_level_perf': queue.get('ServiceLevelPerf'),
                'talk_time': queue.get('TalkTime'),
                'calls': queue.get('Calls'),
                'max': queue.get('Max'),
                'completed': queue.get('Completed'),
                'service_level': queue.get('ServiceLevel'),
                'service_level_perf2': queue.get('ServiceLevelPerf2'),
                'abandoned': queue.get('Abandoned'),
                'strategy': queue.get('Strategy'),
                'queue': queue.get('Queue'),
                'weight': queue.get('Weight'),
                'hold_time': queue.get('HoldTime'),
                }

    def _member(self, member):
        return {'status': member.get('Status'),
                'penalty': member.get('Penalty'),
                'calls_taken': member.get('CallsTaken'),
                'name': member.get('Name'),
                'skills': member.get('Skills'),
                'last_pause': member.get('LastPause'),
                'queue': member.get('Queue'),
                'membership': member.get('Membership'),
                'incall': member.get('Incall'),
                'location': member.get('Location'),
                'last_call': member.get('LastCall'),
                'paused': member.get('Paused'),
                'paused_reason': member.get('PausedReason'),
                'state_interface': member.get('StateInterface'),
                }

    def intercept_call(self, queue_name, params):

        channel = self.ari.channels.get(channelId=params.get('call_id'))
        channel_name = channel.json['name']
        destination = params.get('destination')

        intercept_action = {
            'ActionID': 123,
            'Queue': queue_name,
            'Caller': channel_name,
            'WithdrawInfo': destination
        }

        return self.amid.action('queuewithdrawcaller', intercept_action)
