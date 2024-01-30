# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_bus.resources.common.event import TenantEvent


class QueueCallerAbandonEvent(TenantEvent):
    service = 'calld'
    name = 'queue_caller_abandon'
    routing_key_fmt = 'calls.queue.caller.abandon'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)


class QueueCallerJoinEvent(TenantEvent):
    service = 'calld'
    name = 'queue_caller_join'
    routing_key_fmt = 'calls.queue.caller.join'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)


class QueueCallerLeaveEvent(TenantEvent):
    service = 'calld'
    name = 'queue_caller_leave'
    routing_key_fmt = 'calls.queue.caller.leave'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)


class QueueMemberAddedEvent(TenantEvent):
    service = 'calld'
    name = 'queue_member_added'
    routing_key_fmt = 'calls.queue.member.added'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)


class QueueMemberPauseEvent(TenantEvent):
    service = 'calld'
    name = 'queue_member_pause'
    routing_key_fmt = 'calls.queue.member.pause'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)


class QueueMemberPenaltyEvent(TenantEvent):
    service = 'calld'
    name = 'queue_member_penalty'
    routing_key_fmt = 'calls.queue.member.penalty'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)


class QueueMemberRemovedEvent(TenantEvent):
    service = 'calld'
    name = 'queue_member_removed'
    routing_key_fmt = 'calls.queue.member.removed'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)


class QueueMemberRingInUseEvent(TenantEvent):
    service = 'calld'
    name = 'queue_member_ringinuse'
    routing_key_fmt = 'calls.queue.member.ringinuse'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)


class QueueMemberStatusEvent(TenantEvent):
    service = 'calld'
    name = 'queue_member_status'
    routing_key_fmt = 'calls.queue.member.status'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)

class QueueAgentsStatusEvent(TenantEvent):
    service = 'calld'
    name = 'queue_agents_status'
    routing_key_fmt = 'calls.queue.agents.status'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)

class QueueLiveStatsEvent(TenantEvent):
    service = 'calld'
    name = 'queue_livestats'
    routing_key_fmt = 'calls.queue.livestats'
    required_acl_fmt = 'events.calls.me'

    def __init__(self, content, tenant_uuid):
        super().__init__(content, tenant_uuid)
