# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from flask import request
from flask_restful import Resource
from xivo.tenant_flask_helpers import Tenant

from wazo_calld.auth import required_acl
from wazo_calld.http import AuthResource

from .schema import (
    intercept_schema,
    queue_list_schema,
    queue_schema,
    queue_member_schema,
)


class QueuesResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.read')
    def get(self):
        queues = self._queues_service.list_queues()

        return {
            'items': queue_list_schema.dump(queues, many=True)
        }, 200


class QueueResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.read')
    def get(self, queue_name):
        queue = self._queues_service.get_queue(queue_name)

        return queue_schema.dump(queue)


class QueueAddMemberResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.add_member.update')
    def put(self, queue_name):
        request_body = queue_member_schema.load(request.get_json(force=True))
        result = self._queues_service.add_queue_member(queue_name, request_body)

        return result, 204


class QueueRemoveMemberResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.remove_member.update')
    def put(self, queue_name):
        request_body = queue_member_schema.load(request.get_json(force=True))
        result = self._queues_service.remove_queue_member(queue_name, request_body['interface'])

        return result, 204


class QueuePauseMemberResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.pause_member.update')
    def put(self, queue_name):
        request_body = queue_member_schema.load(request.get_json(force=True))
        result = self._queues_service.pause_queue_member(queue_name, request_body)

        return result, 204


class QueueLiveStatsResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.livestats.read')
    def get(self, queue_name):
        result = self._queues_service.livestats(queue_name)

        return result, 200


class QueueAgentsStatusResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.agents_status.read')
    def get(self):
        tenant = Tenant.autodetect()
        result = self._queues_service.agents_status(tenant.uuid)

        return result, 200

class InterceptResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.intercept.create')
    def post(self, queue_name):
        tenant = Tenant.autodetect()
        request_body = intercept_schema.load(request.get_json(force=True))
        result = self._queues_service.intercept_call(queue_name, request_body)

        return result, 201