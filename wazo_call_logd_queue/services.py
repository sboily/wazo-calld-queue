# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging


class Services(object):

    def __init__(self, dao, publisher):
        self._dao = dao
        self._publisher = publisher

    def queue_log(self, queue_log):
        self._publisher._queue_log(queue_log)
        #self._dao.queue_log.insert_entry(**queue_log)
        return 1
