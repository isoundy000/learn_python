# -*- coding: utf-8 -*-

import json
from datetime import datetime
import sqlalchemy
import sqlalchemy.orm

import merge

from table.t_ktv import t_ktv


class ExistDatabaseException(Exception):
    pass


class DatabaseInfo(object):
    def __init__(self, host, port, username, password, database, param, server_id):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.param = param

        self.server_id = server_id

        self.engine = None
        self.session = None
        self.ktv = None
        self.npc_friend_ids = set()

    @property
    def identifier(self):
        return "%s:%s/%s" % (self.host, self.port, self.database)

    def connect(self):
        self.engine = sqlalchemy.create_engine("mysql+pymysql://%s:%s@%s:%s/%s?%s" % (
            self.username,
            self.password,
            self.host,
            self.port,
            self.database,
            self.param,
        ))
        self.session = sqlalchemy.orm.sessionmaker(bind=self.engine)()
        self.ktv = t_ktv.load_to_dict(self.session)
        for key, value in self.ktv.iteritems():
            if key in ('TAG_NPC_FRIEND_1',
                       'TAG_NPC_FRIEND_2',
                       'TAG_NPC_FRIEND_3',
                       'TAG_NPC_FRIEND_4',
                       'TAG_NPC_FRIEND_5'):
                self.npc_friend_ids.add(int(value.value))


class WrapperDatabaseInfo(object):
    def __init__(self, database, data):
        self.database = database
        self.data = data


def wrapper_database_info(database, data):
    return WrapperDatabaseInfo(database, data)


class Config(object):
    def __init__(self):
        self.role_filter_login_datetime = None
        self.role_filter_level = 0
        self.server_id_step = 0
        self.rename_postfix = ''
        self.src_databases = []
        self.dst_database = None

        self.replace_gang_role_log = []

        self.role_merge_maps = merge.MergeMaps('t_role')
        self.general_merge_maps = merge.MergeMaps('t_general4')
        self.equip_merge_maps = merge.MergeMaps('t_equip4')
        self.soul_merge_maps = merge.MergeMaps('t_soul2')
        self.pet_merge_maps = merge.MergeMaps('t_pet3')
        self.mail_merge_maps = merge.MergeMaps('t_mail3')
        self.gem_merge_maps = merge.MergeMaps('t_gem')
        self.gang_merge_maps = merge.MergeMaps('t_gang2')
        self.cup2_general_merge_maps = merge.MergeMaps('t_cup2_general')
        self.cup2_pet3_merge_maps = merge.MergeMaps('t_cup2_pet3')

    def load_merge_log(self):
        self.gang_merge_maps.load_merge_log(self.dst_database.session)

    def dump_merge_log(self):
        self.role_merge_maps.dump_merge_log(self.dst_database.session)
        self.general_merge_maps.dump_merge_log(self.dst_database.session)
        self.equip_merge_maps.dump_merge_log(self.dst_database.session)
        self.soul_merge_maps.dump_merge_log(self.dst_database.session)
        self.pet_merge_maps.dump_merge_log(self.dst_database.session)
        self.mail_merge_maps.dump_merge_log(self.dst_database.session)
        self.gem_merge_maps.dump_merge_log(self.dst_database.session)
        self.gang_merge_maps.dump_merge_log(self.dst_database.session)
        self.cup2_general_merge_maps.dump_merge_log(self.dst_database.session)
        self.cup2_pet3_merge_maps.dump_merge_log(self.dst_database.session)

    def dump_file_log(self):
        with open('replace_gang_role.log', 'w') as f:
            f.write('\n'.join(self.replace_gang_role_log))

    def load(self, filename, cur = 0):
        database_config_tmp = []
        with open(filename) as f:
            json_obj = json.load(f)
            self.role_filter_level = json_obj['role_filter_level']
            self.server_id_step = json_obj['server_id_step']
            self.rename_postfix = json_obj['rename_postfix']
            #self.role_filter_login_datetime = datetime.strptime(json_obj['role_filter_login_datetime'],
            #                                                    '%Y-%m-%d %H:%M:%S')
            self.role_filter_login_datetime = json_obj['role_filter_login_datetime']
            self.status_url = json_obj['status_url']
            for json_info in json_obj['src_databases']:
                database_config_tmp.append(self._load_database(json_info))
            self.dst_database = self._load_database(json_obj['dst_database'])
        print "[Merge] database_config_tmp",database_config_tmp
        print "[Merge] cur", cur
        if 9999 == cur:
            database_config_tmp = []
        elif cur >= len(database_config_tmp):
            return False
        else:
            self.src_databases = [database_config_tmp[cur]]

        self._check()

        for database in self.src_databases + [self.dst_database]:
            database.connect()

        return True

    def _check(self):
        databases = self.src_databases + [self.dst_database]
        for database in databases:
            for _database in databases:
                if database == _database:
                    continue
                if database.host == _database.host and \
                    database.port == _database.port and \
                    database.database == _database.database:
                    raise ExistDatabaseException

    @staticmethod
    def _load_database(json):
        return DatabaseInfo(
            json['host'],
            json['port'],
            json['username'],
            json['password'],
            json['database'],
            json['param'],
            json.get('server_id', 0),
        )


