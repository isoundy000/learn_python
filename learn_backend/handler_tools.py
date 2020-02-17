#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json

import settings


def to_json(obj):
    """# to_json: 将一些特殊类型转换为json
    args:
        obj:    ---    arg
    returns:
        0    ---
    """
    from logics.private_city import AreaStatus
    if isinstance(obj, AreaStatus):
        return obj.s
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(repr(obj) + ' is not json seralizable')


def get_client_config_version(user, login=False, request=None):
    last_config = request.get_argument('last_config', None)
    return {}


def result_generator(rc, data, msg, user, login=False, r=None, request=None):
    """# result_generator: 各个接口的返回数据，user数据，以及乱七八糟数据，混合，变json
    args:
        arg:    --  arg
        rc      --  接口的return_code
        data    --  接口的返回数据
        user    --  用户对象
        login   --  如果是登录接口，需要修改新手引导值
    returns:
        0    ---
    """
    # if user:

    r = {
        'data': data,
        'status': rc,
        'msg': msg,
        'user_status': {
            # 'role': user.role,
        } if user else {},
    }
    r.update(get_client_config_version(user, login=login, request=request))
    indent = 1 if settings.DEBUG else None
    r = json.dumps(r, ensure_ascii=False, separators=(',', ':'), encoding='utf-8', indent=indent, default=to_json)
    return r