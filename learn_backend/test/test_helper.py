#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import os
import sys
import new

import cPickle as pickle

TESTING = False
LOCAL = False


def EmptyObj(name='Requset', base=None, d=None, **karg):
    ''' 生成一个新的空对象
        name --- 类的名字
        base --- 类的父类
        d --- namespace dict
    '''
    if not base:
        base = (object,)
    if not isinstance(base, tuple):
        base = (base, )
    if not d:
        d = {}
    return new.classobj(name, base, d)(**karg)


class TestModel(object):
    """# TestModel: docstring"""

    @classmethod
    def is_config_model(cls):
        """ is_config_model: docstring 是否是配置模型
        args:
            :    ---    arg  if (True, False, True) 有一个为真就能执行
        returns:
            0    ---
        """
        return '_config' if (
            cls.__name__ in ['Config', 'Configs', 'Configs_obj', 'ConfigVersion']   # 配置默认
            or cls.__name__ in ['Config%s' % i for i in xrange(2, 5)]               # 配置升级
            or cls.__name__ in ['ConfigVersion%d' % i for i in xrange(2, 5)]        # 配置版本
        ) and LOCAL else '_model'

    @classmethod
    def _config_get(cls, key_name):
        """ config_get: docstring 获取配置根据配置名字
        args:
            key_name:    ---    arg
        returns:
            0    ---
        """
        if (
            cls.__name__ in ['ConfigVersion']
            or cls.__name__ in ['ConfigVersion%d' % i for i in xrange(2, 5)]
        ):
            obj = cls(key_name)
            obj.versions = {key_name: 1}        # key_name配置名: 版本号
            return obj
        from local_config import config
        obj = EmptyObj()
        obj.value = config[key_name]
        return obj

    def _config_save(self):
        """ put: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        pass

    def _model_save(self):
        """# _model_save: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        from lib.utils.debug import print_log
        from lib.db import dict_diff
        r = {}
        for k in self._attrs_base:
            data = r[k] = getattr(self, k)

            if k in self._old_data:
                old_v = self._old_data.get(k, {})
                if data != old_v:
                    if isinstance(data, dict):      # 如果是字典就dict_diff
                        update_data, remove_keys = dict_diff(old_v, data)
                    elif isinstance(data, list):
                        update_data = data
                        remove_keys = {}
                    else:
                        update_data = data
                        remove_keys = {}
                    self._diff[k] = {
                        'update': update_data,
                        'remove': remove_keys,
                    }
        r_pickled = pickle.dumps(r)
        _key = self.make_key()
        globals().setdefault('database', {}).update({_key, r_pickled})

    @classmethod
    def _model_get(cls, uid):
        """ get: docstring
        args:
            key:    ---    arg
        returns:
            0    ---
        """
        server_name = cls.get_server_name(uid)
        _key = cls.make_key_cls(uid, server_name)
        pickled_data = globals().get('database', {}).get(_key, None)
        if not pickled_data:
            o = cls(uid)
            o.uid = uid
            return o
        r = pickle.loads(pickled_data)
        old_data = pickle.loads(pickled_data)
        o = cls(uid)
        for k, v in o._attrs_base.iteritems():
            d = r.get(k)
            if d is None:
                d = v
                if k in cls._need_diff:
                    o._old_data[k] = d
            else:
                if k in cls._need_diff:
                    o._old_data[k] = old_data[k]
            setattr(o, k, d)
        return o

    def save(self):
        """# save: docstring
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return getattr(self, self.__class__.is_config_model() + '_save')()

    @classmethod
    def get(cls, uid, *args, **kwargs):
        return getattr(cls, cls.is_config_model() + '_get', lambda x, y: x)(uid)


def change_model():
    """ ChangeModel: docstring
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    if TESTING:
        from lib.db import ModelBase as Model
        for f_name in ['save', '_model_save', '_config_save']:
            f = getattr(TestModel, f_name).im_func
            setattr(Model, f_name, f)
        for f_name in ['get', 'is_config_model', '_model_get', '_config_get']:
            f = getattr(TestModel, f_name).im_func
            f = classmethod(f)
            setattr(Model, f_name, f)


def change_unittest():
    """# change_unittest: 替换调unittest.TestCase.failUnlessEqual
    args:
        :    ---    arg
    returns:
        0    ---
    """
    import unittest
    import unittest_pro
    f = getattr(unittest_pro.TestCase, 'failUnlessEqual').im_func
    f2 = getattr(unittest_pro.TestCase, 'assertEqual').im_func
    setattr(unittest.TestCase, 'failUnlessEqual', f)
    setattr(unittest.TestCase, 'assertEqual', f2)


class FakeConfigError(Exception):
    """ FakeConfigError: docstring"""
    msgs = [
        '',
        'the config_name MUST be a str',
        'the config_value MUST be a dict',
    ]
    def __init__(self, code, data=None, args=None):
        self.code = code
        self.message = self.msgs[code]
        self.data = data
        self.args = (args or [])

    def __str__(self):
        return (u'Error %s: %s' % (self.code, self.message)).encode('utf-8')


def fake_config(config_name, config_value):
    """ fake_config: 保存假配置信息
    args:
        config_name, config_value:    ---    config_name在apps.admin.views.main.setting里有完整列表
    returns:
        0    ---
    """
    if not isinstance(config_name, str):
        raise FakeConfigError(1)
    if not isinstance(config_value, dict):
        raise FakeConfigError(2)
    if config_name.startswith('town_'):
        # from apps.logics import town_config
        exec ('town_config.' + config_name + '=config_value')
    else:
        # from apps.config import common_config
        exec('common_config.' + config_name + '=config_value')


class FackeEnviron(object):
    """# FackeEnviron: docstring"""
    def __init__(self, api_method, params, user):
        self.test_data = {
            'params': params,
            'method': api_method,
        }
        self.user = user
        self.user.save()

    def get_argument(self, param_name, default=None):
        """# get_argument: docstring
        args:
            param_name, default:    ---    arg
        returns:
            0    ---
        """
        return self.test_data['params'].get(param_name, default)

    def get_arguments(self, param_name, default=None):
        """# get_argument: docstring
        args:
            param_name, default:    ---    arg
        returns:
            0    ---
        """
        r = self.test_data['params'].get(param_name, default)
        if isinstance(r, list):
            return r
        else:
            return r[r]


def get_env(user, params=None, api_method=''):
    """# get_env: docstring
    args:
        user, params=None, api_method='':    ---    arg
    returns:
        0    ---
    """
    if params is None:
        params = {}
    return FackeEnviron(api_method, params, user)


def make_test_random(module, random_func_name, result):
    '''
    生产测试的random
    :param module: 模块
    :param random_func_name: 函数名
    :param result: 结果
    :return:
    '''
    from random import Random
    r = EmptyObj(name='random', base=Random)
    f = lambda *args: result
    setattr(r, random_func_name, f)
    setattr(module, 'random', r)