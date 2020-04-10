#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from common.dbhelper import DBHelperObject
from common.common_function import database_get_max


class PartnerObject(object):

    def __init__(self):
        self.con = DBHelperObject.CONFIG_CON

    def get_count(self):
        sql = "SELECT COUNT(*) AS total FROM t_partner"
        return self.con.get(sql)["total"]

    def query(self):
        q_sql = "SELECT * FROM t_partner"
        return self.con.query(q_sql)

    def query_partner(self, start, end):
        q_sql = "SELECT * FROM t_partner LIMIT %d, %d" % (start, end)
        return self.con.query(q_sql)

    def delete_one(self, pid):
        d_sql = "DELETE FROM t_partner WHERE id=%d" % pid
        count = self.con.execute(d_sql)
        return {"status": count}

    def get_one(self, pid):
        g_sql = "SELECT * FROM t_partner WHERE id=%d" % pid
        return self.con.get(g_sql)

    def get_one_by_name(self, alias):
        g_sql = "SELECT * FROM t_partner WHERE `alias`='%s' limit 1" % alias
        return self.con.get(g_sql)

    def get_max_id(self):
        return database_get_max(table='t_partner', max_str="id", condition=[])

    def operate(self, pid, name, partner_nname, discount, desc):
        data = {}
        if pid:
            sql = "UPDATE t_partner SET name='%s', `alias`='%s', discount='%d', `desc`='%s' WHERE id=%d" % (name,
                   partner_nname, int(discount), desc, int(pid))
        else:
            sql = "INSERT INTO t_partner(name, `alias`, discount, `desc`) VALUES('%s', '%s', %d, '%s')" % (name,
                  partner_nname, int(discount), desc)

        count = self.con.execute(sql)
        if count >= 0:
            data["status"] = 1
        else:
            data["status"] = 2
        return data