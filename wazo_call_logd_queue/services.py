# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
from xivo_dao.alchemy.queue_log import QueueLog

class Services(object):

    def __init__(self, dao, publisher):
        self._dao = dao
        self._publisher = publisher

    def queue_log(self, queue_log):
        self._publisher._queue_log(queue_log)
        with self._dao.cel.new_session() as session:
            self.insert_entry(session, queue_log)
        return 1

    def insert_entry(self, session, queue_log):
        entry = QueueLog(
            time=queue_log['time'],
            callid=queue_log['callid'],
            queuename=queue_log['queuename'],
            agent=queue_log['agent'],
            event=queue_log['event'],
            data1=queue_log['data1'],
            data2=queue_log['data2'],
            data3=queue_log['data3'],
            data4=queue_log['data4'],
            data5=queue_log['data5'])
        session.add(entry)
