# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import datetime
import logging
import math

logger = logging.getLogger(__name__)


class QueueStatusHandler:
    def __init__(self, stats):
        self.stats = stats

    def _update_waiting_calls(self, uniqueid):
        self.stats['waiting_calls'] = [call for call in self.stats['waiting_calls'] if call['uniqueid'] != uniqueid]

    def _calculate_awr(self):
        if self.stats['received'] > 0:
            self.stats['awr'] = math.ceil(self.stats['answered'] / self.stats['received'] * 100)

    def _update_stats_color(self):
        self.stats['count_color'] = "red" if self.stats['count'] > 1 else "green"

    def livestats(self, event, tenant_uuid):
        queue_event = event['Event']
        self.stats['updated_at'] = datetime.datetime.now().day

        if queue_event == "QueueCallerJoin":
            self.stats['count'] = int(event['Count'])
            self.stats['waiting_calls'].append({
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
            self.stats['abandonned'] += 1
            self.stats['answered'] -= 1
            self._calculate_awr()
            self._update_waiting_calls(event['Uniqueid'])
        elif queue_event == "QueueCallerLeave":
            self.stats['count'] = int(event['Count'])
            self.stats['answered'] += 1
            self.stats['received'] += 1
            self._calculate_awr()
            self._update_waiting_calls(event['Uniqueid'])

        self._update_stats_color()

        return self.stats
