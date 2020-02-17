#!/usr/bin/env python
# -*- coding:utf-8 -*-

import torndb
from configmanager import ConfigManager


class DBHelperObject(object):

    CONFIG_CON = None
    CONFIG_DB_NAME = None
    ACC_CON = None

    @staticmethod
    def init_connection():
        host1 = "%s:%s" % (ConfigManager.getvalue("DATABASE1", "host"),
                           ConfigManager.getvalue("DATABASE1", "port"))
        db_name1 = ConfigManager.getvalue("DATABASE1", "database")
        DBHelperObject.CONFIG_DB_NAME = db_name1
        username1 = ConfigManager.getvalue("DATABASE1", "username")
        password1 = ConfigManager.getvalue("DATABASE1", "password")
        DBHelperObject.CONFIG_CON = DBHelperObject.create_connection(host1, db_name1, username1, password1)

        host2 = "%s:%s" % (ConfigManager.getvalue("DATABASE2", "host"),
                           ConfigManager.getvalue("DATABASE2", "port"))
        db_name2 = ConfigManager.getvalue("DATABASE2", "database")
        username2 = ConfigManager.getvalue("DATABASE2", "username")
        password2 = ConfigManager.getvalue("DATABASE2", "password")
        DBHelperObject.ACC_CON = DBHelperObject.create_connection(host2, db_name2, username2, password2)

    @staticmethod
    def config_connection():
        host1 = "%s:%s" % (ConfigManager.getvalue("DATABASE1", "host"),
                           ConfigManager.getvalue("DATABASE1", "port"))
        DBHelperObject.CONFIG_DB_NAME = ConfigManager.getvalue("DATABASE1", "database")
        username1 = ConfigManager.getvalue("DATABASE1", "username")
        password1 = ConfigManager.getvalue("DATABASE1", "password")
        return DBHelperObject.create_connection(host1, DBHelperObject.CONFIG_DB_NAME, username1, password1)

    @staticmethod
    def create_acc_connection():
        # host2 = "%s:%s" % (ConfigManager.getvalue("DATABASE2", "host"),
        #                    ConfigManager.getvalue("DATABASE2", "port"))
        # db_name2 = ConfigManager.getvalue("DATABASE2", "database")
        # username2 = ConfigManager.getvalue("DATABASE2", "username")
        # password2 = ConfigManager.getvalue("DATABASE2", "password")
        # return DBHelperObject.create_connection(host2, db_name2, username2, password2)
        return DBHelperObject.ACC_CON

    @staticmethod
    def create_sensor_connection():
        if "DATABASE3" in ConfigManager._config_dict:
            host2 = "%s:%s" % (ConfigManager.getvalue("DATABASE3", "host"),
                               ConfigManager.getvalue("DATABASE3", "port"))
            db_name2 = ConfigManager.getvalue("DATABASE3", "database")
            username2 = ConfigManager.getvalue("DATABASE3", "username")
            password2 = ConfigManager.getvalue("DATABASE3", "password")
            return DBHelperObject.create_connection(host2, db_name2, username2, password2)

    @staticmethod
    def create_language_acc_connection(language):
        host_ip = ConfigManager._config_dict[language]["host"]
        port = ConfigManager._config_dict[language]["port"]
        data_base = ConfigManager._config_dict[language]["database"]
        user = ConfigManager._config_dict[language]["username"]
        password = ConfigManager._config_dict[language]["password"]
        con = DBHelperObject.create_game_connection(ip=host_ip, port=port, database=data_base, user=user, password=password)
        return con

    @staticmethod
    def create_game_connection(**kwargs):
        host = "%s:%s" % (kwargs["ip"], kwargs["port"])
        db_name = kwargs["database"]
        user_name = kwargs["user"]
        password = kwargs["password"]
        return DBHelperObject.create_connection(host, db_name, user_name, password)

    @staticmethod
    def create_connection(host, db_name, user_name, password):
        return torndb.Connection(host=host, database=db_name, user=user_name, password=password, time_zone="+8:00")