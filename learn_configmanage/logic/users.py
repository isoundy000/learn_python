#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import hashlib
from common.dbhelper import DBHelperObject
from systemlog import SystemLogObject
import public
from common.common_function import database_execute


class UsersObject(object):

    def __init__(self):
        self.con = DBHelperObject.CONFIG_CON

    def update_pass(self, user, old_pass, new_pass):
        """
        更新密码
        :param user: 用户
        :param old_pass: 旧密码
        :param new_pass: 新密码
        :return:
        """
        data = self.validate_user(user, old_pass)
        if data["status"] == 0:
            u_sql = "UPDATE t_users SET password='%s' WHERE username='%s'" % (new_pass, user)
            self.con.execute(u_sql)
        return data

    def validate_user(self, user_name, pass_word):
        """
        验证用户
        :param user_name: 用户名
        :param pass_word: 密码
        :return:
        """
        query_sql = "SELECT * FROM t_users WHERE username='%s'" % user_name
        data = self.con.get(query_sql)
        if not data:
            return {"status": 1}
        if data["password"] == pass_word:
            status = 0
        else:
            status = 2
        data["status"] = status
        return data

    def get_count(self):
        '''
        获取条数
        :return:
        '''
        sql = "SELECT COUNT(id) AS total FROM t_users"
        return self.con.get(sql)["total"]

    def get_all_user(self, start=0, end=0):
        """
        获取所有的玩家
        :param start: 开始索引
        :param end: 获取多少条数据
        :return:
        """
        query_sql = "SELECT * FROM t_users"
        if start or end:
            query_sql += " LIMIT %d, %d" % (start, end)
        return self.con.query(query_sql)

    def isexit_username(self, user_name):
        '''
        根据用户名查询玩家id
        :param user_name:
        :return:
        '''
        query_sql = "SELECT id FROM t_users WHERE username='%s'" % user_name
        return self.con.get(query_sql)

    def operate_user(self, user, user_id, name, user_name, pass_word, user_type, user_game, upload_is, select_channel,
                     is_start, is_recharge, mail_approve, operate_type, email, phone, real_ip):
        '''
        操作用户
        :param user:
        :param user_id:
        :param name:
        :param user_name:
        :param pass_word:
        :param user_type:
        :param user_game:
        :param upload_is:
        :param select_channel:
        :param is_start:
        :param is_recharge:
        :param mail_approve:
        :param operate_type:
        :param email:
        :param phone:
        :param real_ip:
        :return:
        '''
        user_data = self.isexit_username(user_name)
        data = {}
        md5_password = hashlib.md5(pass_word).hexdigest()
        user_role1 = 0
        user_role2 = 0
        user_role3 = 0
        user_role4 = 0
        user_role5 = 0

        for u in user_type:
            if u:
                if u == "1":
                    user_role1 = 1
                if u == "2":
                    user_role2 = 1
                if u == "3":
                    user_role3 = 1
                if u == "4":
                    user_role4 = 1
                if u == "5":
                    user_role5 = 1
        if user_id:
            user_id = int(user_id)
            exe_sql = "UPDATE t_users SET name='%s', role1=%d, role2=%d, role3=%d, role4=%d, role5=%d, game='%s', upload=%d, " \
                      "channel=%d, start='%s', recharge='%s',custom='%s', approve=%d, email='%s', phone='%s'" % (name, user_role1,
                       user_role2, user_role3, user_role4, user_role5, user_game, int(upload_is), select_channel,
                      is_start, is_recharge, operate_type, mail_approve, email, phone)
            if pass_word:
                exe_sql += ", password='%s'" % md5_password
            exe_sql += " WHERE id=%d" % user_id
            log_str = "修改用户" + user_name
        else:
            if user_data and user_data["id"]:
                data["status"] = 0
                return data

            exe_sql = "INSERT INTO t_users(name, username, password, role1, role2, role3, role4, role5, channel, game, " \
                      "upload, start, recharge, simulator, custom, approve, email, phone) VALUES ('%s', '%s', '%s', %d, %d, " \
                      "%d, %d, %d, %d, '%s', %d, '%s', '%s', 0, '%s', %d, '%s', '%s')" % (name, user_name,
                                                                                          md5_password, user_role1,
                                                                                          user_role2, user_role3,
                                                                                          user_role4, user_role5,
                                                                                          select_channel, user_game,
                                                                                          int(upload_is), is_start,
                                                                                          is_recharge, operate_type,
                                                                                          mail_approve, email, phone)
            log_str = "添加用户" + user_name
            print "exe_sql", exe_sql
        SystemLogObject.insert_log(user, 3, log_str, real_ip)
        return database_execute(exe_sql)

    def delete_user(self, user_id):
        """
        删除用户
        :param user_id:
        :return:
        """
        del_sql = "DELETE FROM t_users WHERE id=%d" % int(user_id)
        data = {}
        count = self.con.execute(del_sql)

        if count >= 0:
            data["status"] = 1
        else:
            data["status"] = 0
        return data