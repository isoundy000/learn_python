#!/usr/bin/env python
# -*- coding:utf-8 -*-

import settings
from lib.db import ModelBase
from lib.db import get_redis_client


config_types = {1: unicode('新服', 'utf-8'), 2: unicode('老服', 'utf-8'), 3: unicode('老老服', 'utf-8'), 4: unicode('新区', 'utf-8')}


class ConfigRefresh(object):

    FLAG_KEY = 'config_refresh_key'
    TEXT_KEY = 'config_refresh_text_key'

    @classmethod
    def reset(cls):
        client = get_redis_client(settings.AD_CLICK)
        client.delete(cls.FLAG_KEY)

    @classmethod
    def refresh(cls, flag=0, message=''):
        client = get_redis_client(settings.AD_CLICK)
        if flag:
            client.set(cls.FLAG_KEY, 1)
        else:
            client.delete(cls.FLAG_KEY)
        client.set(cls.TEXT_KEY, message)

    @classmethod
    def check(cls):
        client = get_redis_client(settings.AD_CLICK)
        v = client.get(cls.FLAG_KEY)
        text = client.get(cls.TEXT_KEY) or ''
        text = text.decode('utf-8')
        return (1, text) if v else (0, text)


class ChangeTime(object):

    KEY = 'change_time'

    @classmethod
    def get(cls):
        client = get_redis_client(settings.AD_CLICK)
        return client.get(cls.KEY)

    @classmethod
    def set(cls, value):
        client = get_redis_client(settings.AD_CLICK)
        client.set(cls.KEY, value)


class ResourceVersion(object):

    KEY = 'resource_version'

    @classmethod
    def get(cls):
        client = get_redis_client(settings.AD_CLICK)
        return 1 if client.get(cls.KEY) else 0

    @classmethod
    def set(cls, flag):
        client = get_redis_client(settings.AD_CLICK)
        if flag:
            client.set(cls.KEY, 1)
        else:
            client.delete(cls.KEY)


class Config(ModelBase):
    """# Config: docstring"""
    SERVER_NAME = 'master'
    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'value': {},
            'version': '',
        }
        super(Config, self).__init__(self.uid)


class Config2(ModelBase):
    """# Config: docstring"""
    SERVER_NAME = 'master'
    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'value': {},
            'version': '',
        }
        super(Config2, self).__init__(self.uid)


class Config3(ModelBase):
    """# Config: docstring"""
    SERVER_NAME = 'master'
    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'value': {},
            'version': '',
        }
        super(Config3, self).__init__(self.uid)


class Config4(ModelBase):
    """# Config: docstring"""
    SERVER_NAME = 'master'
    def __init__(self, uid=None):
        self.uid = uid
        self._attrs = {
            'value': {},
            'version': '',
        }
        super(Config4, self).__init__(self.uid)


class ConfigManager():

    @classmethod
    def get_config_obj(cls, config_name, server_name='', need_init=True, config_type=1):

        if config_type == 1:
            config_obj = Config.get(config_name, server_name=server_name, need_init=need_init)
        elif config_type == 2:
            config_obj = Config2.get(config_name, server_name=server_name, need_init=need_init)
        elif config_type == 3:
            config_obj = Config3.get(config_name, server_name=server_name, need_init=need_init)
        elif config_type == 4:
            config_obj = Config4.get(config_name, server_name=server_name, need_init=need_init)
        else:
            config_obj = Config.get(config_name, server_name=server_name, need_init=need_init)

        return config_obj


class ConfigVersion(ModelBase):
    """# ConfigVersion: 这货是为了纪录config版本的"""
    SERVER_NAME = 'master'

    def __init__(self, uid):
        self.uid = 'config_version'
        self._attrs = {
            'versions': {

            },
        }
        super(ConfigVersion, self).__init__(self.uid)

    @classmethod
    def get(cls, uid='config_version', server_name='', need_init=True):
        uid = 'config_version'
        server_name = cls.SERVER_NAME
        return super(ConfigVersion, cls).get(uid, server_name)

    def update_single(self, field, need_save=False, hex_version=None):
        """# set_single_ver: docstring
        args:
            field:    ---    arg
        returns:
            0    ---
        """
        if hex_version is None:
            ver = self.versions.get(field, 0)
            self.versions[field] = ver + 1
        else:
            self.versions[field] = hex_version

        if need_save:
            self.save()
        self.print_log('new_config_version: ', repr(field), self.versions[field])

        print 'new_config_version: ', repr(field), self.versions[field]


class ConfigVersion2(ModelBase):
    """# ConfigVersion: 这货是为了纪录config版本的"""
    SERVER_NAME = 'master'

    def __init__(self, uid):
        self.uid = 'config_version'
        self._attrs = {
            'versions': {

            },
        }
        super(ConfigVersion2, self).__init__(self.uid)

    @classmethod
    def get(cls, uid='config_version', server_name='', need_init=True):
        uid = 'config_version'
        server_name = cls.SERVER_NAME
        return super(ConfigVersion2, cls).get(uid, server_name)

    def update_single(self, field, need_save=False, hex_version=None):
        """# set_single_ver: docstring
        args:
            field:    ---    arg
        returns:
            0    ---
        """
        if hex_version is None:
            ver = self.versions.get(field, 0)
            self.versions[field] = ver + 1
        else:
            self.versions[field] = hex_version

        if need_save:
            self.save()
        self.print_log('new_config_version: ', repr(field), self.versions[field])

        print 'new_config_version: ', repr(field), self.versions[field]


class ConfigVersion3(ModelBase):
    """# ConfigVersion: 这货是为了纪录config版本的"""
    SERVER_NAME = 'master'

    def __init__(self, uid):
        self.uid = 'config_version'
        self._attrs = {
            'versions': {

            },
        }
        super(ConfigVersion3, self).__init__(self.uid)

    @classmethod
    def get(cls, uid='config_version', server_name='', need_init=True):
        uid = 'config_version'
        server_name = cls.SERVER_NAME
        return super(ConfigVersion3, cls).get(uid, server_name)

    def update_single(self, field, need_save=False, hex_version=None):
        """# set_single_ver: docstring
        args:
            field:    ---    arg
        returns:
            0    ---
        """
        if hex_version is None:
            ver = self.versions.get(field, 0)
            self.versions[field] = ver + 1
        else:
            self.versions[field] = hex_version

        if need_save:
            self.save()
        self.print_log('new_config_version: ', repr(field), self.versions[field])

        print 'new_config_version: ', repr(field), self.versions[field]


class ConfigVersion4(ModelBase):
    """# ConfigVersion: 这货是为了纪录config版本的"""
    SERVER_NAME = 'master'

    def __init__(self, uid):
        self.uid = 'config_version'
        self._attrs = {
            'versions': {

            },
        }
        super(ConfigVersion4, self).__init__(self.uid)

    @classmethod
    def get(cls, uid='config_version', server_name='', need_init=True):
        uid = 'config_version'
        server_name = cls.SERVER_NAME
        return super(ConfigVersion4, cls).get(uid, server_name)

    def update_single(self, field, need_save=False, hex_version=None):
        """# set_single_ver: docstring
        args:
            field:    ---    arg
        returns:
            0    ---
        """
        if hex_version is None:
            ver = self.versions.get(field, 0)
            self.versions[field] = ver + 1
        else:
            self.versions[field] = hex_version

        if need_save:
            self.save()
        self.print_log('new_config_version: ', repr(field), self.versions[field])

        print 'new_config_version: ', repr(field), self.versions[field]


class ConfigVersionManager():

    @classmethod
    def get_config_version_obj(cls, uid='config_version', server_name='', config_type=1):
        if config_type == 1:
            config_obj = ConfigVersion.get(uid, server_name=server_name)
        elif config_type == 2:
            config_obj = ConfigVersion2.get(uid, server_name=server_name)
        elif config_type == 3:
            config_obj = ConfigVersion3.get(uid, server_name=server_name)
        elif config_type == 4:
            config_obj = ConfigVersion4.get(uid, server_name=server_name)
        else:
            config_obj = ConfigVersion.get(uid, server_name=server_name)
        return config_obj


class ServerConfig(ModelBase):
    """# ServerConfig: 关于分服的设置，开关，名字，等等吧？"""
    SERVER_NAME = 'master'
    def __init__(self, uid='server_config'):
        self.uid = 'server_config'
        self._attrs = {
            'config_value': {}
        }
        super(ServerConfig, self).__init__(self.uid)
        self._server_name = 'master'
        self._redis = self.get_redis_client(self.uid, self._server_name)

    @classmethod
    def get(cls, uid='server_config'):
        uid = 'server_config'
        o = super(ServerConfig, cls).get(uid, cls.SERVER_NAME)
        for k in settings.SERVERS:
            if k not in o.config_value:
                o.config_value[k] = {
                    'name': u'' if k != 'master' else 'master',
                    'is_open': False if k != 'master' else True,
                    'is_open_for_test': True,
                    'sort_id': 0,       # 排序权重
                    'flag': 0,          # 0, 1, 2, 3, 空闲，新绿，满红，热橙
                    'open_time': -1,
                }
        return o

    def server_list(self, need_filter=True, replace_lua_url=False):
        """# server_list: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        l = []
        for k, v in self.config_value.iteritems():
            if k == 'master' and need_filter: continue
            if (v['is_open'] and v['name']) or not need_filter:
                if k not in settings.SERVERS: continue
                se = settings.SERVERS[k]
                l.append({
                    'server': k,
                    'sort_id': v.get('sort_id', 0),
                    'flag': v.get('flag', 0),
                    'open_time': v.get('open_time', -1),
                    'uid': '',
                    'master_url': settings.SERVERS['master']['server'],
                    'server_name': v['name'],
                    'is_open': v['is_open'],
                    'is_open_for_test': v['is_open_for_test'],
                    'domain': se['server'],
                    'dataosha_url': se.get('dataosha', ''),
                    'lua_url': se.get('lua64', '') if replace_lua_url else se.get('lua', ''),
                    'lua64_url': se.get('lua64', ''),
                    'lua_ver_url': se.get('lua_ver_url', '') + 'lr_version/',
                    'chat_ip': se.get('chat_ip', ''),
                    'chat_port': se.get('chat_port', ''),
                    'config_type': settings.get_config_type(k)
                })
        l.sort(key=lambda x: (x['server'] != 'master', -x['sort_id'], x['server']))
        return l

    def get_server(self, server_name):
        """ 获取单服配置

        :return:
        """
        config = self.config_value.get(server_name)
        return config