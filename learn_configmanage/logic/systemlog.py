#!/usr/bin/env python
# -*- coding:utf-8 -*-

from common.dbhelper import DBHelperObject
import public
from common.common_function import database_execute


class SystemLogObject(object):

    def __init__(self):
        self.con = DBHelperObject.CONFIG_CON

    def insert_log(self, user, l_type, content, ip='0.0.0.0'):
        content = public.addslashes(content)
        add_sql = "INSERT INTO t_log(`type`, op_time, user, content, ip) VALUES(%d, now(), '%s', '%s', '%s')" % (l_type, user, content, ip)
        return database_execute(add_sql)