# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .bus_consume import QueuesBusEventHandler


class QueueService(object):

    def __init__(self, amid, ari, confd, agentd, publisher):
        self.amid = amid
        self.ari = ari
        self.confd = confd
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

    def withdraw(self, queue_name, params):

        channel = self.ari.channels.get(channelId=params.get('call_id'))
        channel_name = channel.json['name']
        destination = params.get('destination')

        _withdraw = {
            'Queue':  queue_name,
            'Caller': channel_name,
            'WithdrawInfo': destination
        }
        return self.amid.action('queuewithdrawcaller', _withdraw)

    def _to_snake_case(self, s):
        return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')

    def _transform_data(self, data, keys):
        return {self._to_snake_case(key): data.get(key) for key in keys}

    def _queues(self, queue):
        keys = ['LoggedIn', 'Available', 'TalkTime', 'LongestHoldTime', 'Queue', 
                'Talking', 'HoldTime', 'Callers']
        return self._transform_data(queue, keys)

    def _queue(self, queue):
        keys = ['ServiceLevelPerf', 'TalkTime', 'Calls', 'Max', 'Completed', 
                'ServiceLevel', 'ServiceLevelPerf2', 'Abandoned', 'Strategy', 
                'Queue', 'Weight', 'HoldTime']
        return self._transform_data(queue, keys)

    def _member(self, member):
        keys = ['Status', 'Penalty', 'CallsTaken', 'Name', 'Skills', 'LastPause', 
                'Queue', 'Membership', 'Incall', 'Location', 'LastCall', 'Paused', 
                'PausedReason', 'StateInterface']
        return self._transform_data(member, keys)
