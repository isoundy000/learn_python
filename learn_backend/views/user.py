#!/usr/bin/env python
# -*- coding:utf-8 -*-

import settings

from lib.utils import rand_string

from models.user import UnameUid
from models.config import ServerConfig


def loading(req):
    """# login: docstring
    args:
        env:    ---    arg
    returns:
        0    ---
    """
    return 0, {}


def loading_for_test(req):
    """# loading_for_test: 为了在关闭config下载的时候，让前端手动获得新配置
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    all_config_version, client_config_version_for_test = None, None
    return 0, None, {

    }


def register(req):
    """# register: 注册新用户，并且将当前的uid绑定到用户上
    args:
        req:    ---    arg
    returns:
        0    ---
        1: unicode('没有用户名或者密码', 'utf-8'),
        3: unicode('这个账户已经有人了', 'utf-8'),
        5: unicode('已经绑定的账户', 'utf-8'),
        6: unicode('缺少uid', 'utf-8'),
        7：unicode('账号只能为6-20位的字母数字组合', 'utf-8')
    """
    account = req.get_argument('account', '')
    if not (account.isalnum() and 6 <= len(account) <= 20):
        return 7, None, {}
    password = req.get_argument('passwd', '')
    old_account = req.get_argument('old_account', '')
    uid = req.get_argument('user_token', '')
    if not account or not password:
        return 1, None, {}      # 没有用户名或者密码
    # if not old_account:
    #     return 2, None, {}      # 没有老账户
    if UnameUid.check_exist(account):
        return 3, None, {}      # 这个账户已经有人了
    if 'fake_account_' not in old_account or not UnameUid.check_exist(old_account):
        if old_account != account:
            pass


def mark_user_login(req):
    """# mark_user_login: 标记用户最近登录，防多设备登录
    args:
        req:    ---    arg
    returns:
        0    ---
    """
    pass


def new_account(req):
    """# new_account: 创建一个账户，作为用户绑定账户前的替代物
    args:
        env:    ---    arg
    returns:
        0    ---
    """
    version = req.get_argument('version', '')

    f_account = 'fake_account_' + rand_string(8)
    while UnameUid.check_exist(f_account):
        f_account = 'fc' + rand_string(8)
    replace_lua_url = True if settings.ENV_NAME in [settings.ENV_IOS, settings.ENV_STG_IOS, settings.ENV_TEST_IOS] and version >= '1.2.7' else False
    return 0, None, {
        'fake_account': f_account,
        'server_list': ServerConfig.get().server_list(replace_lua_url=replace_lua_url)
    }
