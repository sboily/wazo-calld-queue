# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from xivo_ctid_ng.auth import required_acl
from xivo_ctid_ng.rest_api import AuthResource

from .schema import (
    queue_list_schema,
    queue_schema,
)


class QueuesResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('ctid-ng.queues.read')
    def get(self):
        queues = self._queues_service.list_queues()

        return {
            'items': queue_list_schema.dump(queues, many=True).data
        }, 200


class QueueResource(AuthResource):

    def __init__(self, queues_service):
        self._queues_service = queues_service

    @required_acl('ctid-ng.queues.{queue_name}.read')
    def get(self, queue_name):
        queue = self._queues_service.get_queue(queue_name)

        return queue_schema.dump(queue).data
