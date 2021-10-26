# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from flask import request
from flask_restful import Resource


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
