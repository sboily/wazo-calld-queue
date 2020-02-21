# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from flask import request
from flask_restful import Resource

from wazo_calld.auth import required_acl
from wazo_calld.http import AuthResource

from .schema import (
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
            'items': queue_list_schema.dump(queues, many=True).data
        }, 200


class QueueResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.read')
    def get(self, queue_name):
        queue = self._queues_service.get_queue(queue_name)

        return queue_schema.dump(queue).data


class QueueAddMemberResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.add_member.update')
    def put(self, queue_name):
        request_body = queue_member_schema.load(request.get_json(force=True)).data
        result = self._queues_service.add_queue_member(queue_name, request_body)

        return result, 204


class QueueRemoveMemberResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.remove_member.update')
    def put(self, queue_name):
        request_body = queue_member_schema.load(request.get_json(force=True)).data
        result = self._queues_service.remove_queue_member(queue_name, request_body['interface'])

        return result, 204


class QueuePauseMemberResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('calld.queues.{queue_name}.pause_member.update')
    def put(self, queue_name):
        request_body = queue_member_schema.load(request.get_json(force=True)).data
        result = self._queues_service.pause_queue_member(queue_name, request_body)

        return result, 204


class QueueLogStoreResource(Resource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    def post(self):
        request_body = request.form.to_dict()
        result = self._queues_service.queue_log(request_body)
        return result, 200


class QueueLogRequireResource(Resource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    def post(self):
        return 0, 200
