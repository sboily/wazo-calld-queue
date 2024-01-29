# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import datetime
import logging

logger = logging.getLogger(__name__)


class AgentStatusHandler:
    def __init__(self, event):
        self.event = event

    def handle_event(self):
        event_method_name = f"handle_{self.event['Event']}"
        if hasattr(self, event_method_name):
            method = getattr(self, event_method_name)
            return method(self.event)
        else:
            print(f"Unhandled event type: {event['Event']}")

    def get_agent_id(self):
        if self.event.get('Interface'):
            return int(self.event['Interface'].split('-')[1].split('@')[0])
        return None

    def find_agent_id_by_number(self, event, agents):
        number = None
        if event['ConnectedLineNum'] != "<unknown>":
            number = event['ConnectedLineNum']

        if number:
            for agent_id, agent_info in agents.items():
                if agent_info.get('number') == number:
                    return agent_id
        return None

    def handle_QueueCallerLeave(self, event):
        if event['ConnectedLineNum'] != "<unknown>":
            return {
                'number': event['ConnectedLineNum'],
                'talked_with_number': event['CallerIDNum'],
                'talked_with_name': event['CallerIDName']
            }
        return None

    def handle_QueueMemberStatus(self, event):
        if event['Membership'] != "dynamic":
            return None

        is_ringing = event['Status'] == "6"
        is_talking = event['Status'] == "2"
        is_not_talking = event['Status'] == "1"

        if is_talking:
            return {
                'is_talking': True,
                'is_ringing': False,
                'talked_at': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            }
        elif is_ringing:
            return {
                'is_ringing': True,
                'is_talking': False
            }
        elif is_not_talking:
            return {
                'is_ringing': False,
                'is_talking': False
            }

        return None

    def handle_QueueMemberAdded(self, event):
        if event['Membership'] != "dynamic":
            return None

        return {
            'is_logged': True,
            'interface': event['StateInterface'],
            'logged_at': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        }

    def handle_QueueMemberRemoved(self, event):
        if event['Membership'] == "dynamic":
            return {
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

    def handle_QueueMemberPause(self, event):
        if event['Membership'] == "dynamic":
            is_paused = event['Paused'] == "1"
            paused_at = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f') if is_paused else ""
            return {
                'is_paused': is_paused,
                'paused_at': paused_at
            }
        return None
