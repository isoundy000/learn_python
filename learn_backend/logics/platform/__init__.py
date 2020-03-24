#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import settings

import utils


def login_verify_cmge(env):
    """中手游登录验证
    Args:
        code: auth_code
        app_type: 1表示ios正式版，0表示ios越狱版
    Returns:
        平台用户标识
    """
    import cmge as cmge_app

    code = env.get_argument('code')
    app_type = int(env.get_argument('app_type'))

    openid = cmge_app.login_verify(code, app_type)

    return openid