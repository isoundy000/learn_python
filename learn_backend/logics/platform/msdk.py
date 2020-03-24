#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import http
import json
import urllib
import hashlib
import hmac
import binascii

from lib.utils.debug import print_log

mapping = {
    '1': 'mpqq',
    '2': 'wechat',
}

HOSTS = {
    'sandbox': 'http://msdktest.qq.com',    # 测试
    'official': 'http://msdk.qq.com',   # 正式
}

PLATFORM_SETTINGS = {
    'wechat': {     # 微信
        'app_id': 'wx86e877f7e51daff4',
        'app_key': 'd4624c36b6795d1d99dcf0547af5443d',
        'app_key_pay': 'd4624c36b6795d1d99dcf0547af5443d',
        'name': 'msdk_wechat',  # 自己支付使用
        'login_verify_url': '/auth/check_token/',
        'balance': '/mpay/get_balance_m',
        'pay': '/mpay/pay_m',
    },
    'mpqq': {       # 手机QQ
        'app_id': 1104950218,
        'app_key': 'zjy3L6fVprPMkiAi',  # 沙箱appkey，用于现网和测试登录，和测试的支付
        'app_key_pay': '6iBB5jjma3mDFTr2W0g4OgNF8G7bNn0z',   # 现网appkey，用于现网的支付
        'name': 'msdk_mpqq',    # 自己支付使用
        'login_verify_url': '/auth/verify_login/',
        'balance': '/mpay/get_balance_m',
        'pay': '/mpay/pay_m',
    },
}


def get_platform_app_key(config, is_sandbox=False):
    """ 获取平台app_key

    :param config:
    :param is_sandbox:
    :return:
    """
    if is_sandbox:
        return config['app_key']
    else:
        return config['app_key_pay']


def get_host(is_sandbox):
    """ 获取域名

    :param env:
    :return:
    """
    if is_sandbox:
        return HOSTS.get('sandbox', '')
    else:
        return HOSTS.get('official', '')


def mk_source(method, url_path, params):
    str_params = urllib.quote("&".join(k + "=" + str(params[k]) for k in sorted(params.keys())), '')
    source = '%s&%s&%s' % (
        method.upper(),
        urllib.quote(url_path, ''),
        str_params
    )
    return source


def hmac_sha1_sig(method, url_path, params, secret):
    source = mk_source(method, url_path, params)
    hashed = hmac.new(secret, source, hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]


def mk_msdk_sig(appkey, ts):
    str_params = str(appkey) + str(ts)
    m = hashlib.md5()
    m.update(str_params)
    return m.hexdigest()


def login_verify(login_type, openid, openkey, userip='', is_sandbox=False):
    """ 登录验证

    :param login_type: 环境 1: 手机QQ 2: 微信
    :param openid: 普通用户唯一标识(QQ平台) | 普通用户唯一标识(微信平台)
    :param openkey: 授权凭证access_token | 授权凭证
    :param userip: 用户客户端ip
    :param is_sandbox: 是否沙箱
    :return:
    """
    env = mapping[login_type]

    config = PLATFORM_SETTINGS.get(env)
    if not config:
        return False

    now = int(time.time())

    if env == 'wechat':     # 微信
        params = {
            'openid': openid,
            'accessToken': openkey,
        }
    else:                   # 手机QQ
        params = {
            'appid': config['app_id'],
            'openid': openid,
            'openkey': openkey,
            'userip': userip
        }

    app_key = config['app_key']

    qs = urllib.urlencode({
        'appid': config['app_id'],
        'timestamp': now,
        'sig': mk_msdk_sig(app_key, now),
        'encode': 1,
        'openid': openid,
    })

    host = get_host(is_sandbox)

    url = '%s%s?%s' % (host, config['login_verify_url'], qs)

    http_code, content = http.post(url, json.dumps(params), timeout=10)

    if http_code != 200:
        return None

    obj = json.loads(content)

    if obj.get('ret') != 0:
        return None

    return openid


def balance(login_type, params, is_sandbox=False):
    """ 获取余额接口, 微信登录态和手Q登录态使用的支付接口相同，支付ID相同； 服务端使用的appid和appkey都使用手Qappid和appkey

    :param login_type: 环境 1: 手机QQ 2: 微信
    :param params:
    :param is_sandbox: 是否沙箱
    :return:
    """
    basic_env = mapping['1']
    env = mapping[login_type]

    config = PLATFORM_SETTINGS.get(env)
    if not config:
        return False

    basic_config = PLATFORM_SETTINGS.get(basic_env)

    if env == 'wechat':     # 微信
        session_type = 'wc_actoken'
        session_id = 'hy_gameid'
    else:
        session_type = 'kp_actoken'
        session_id = 'openid'

    cookie = {
        'org_loc': urllib.quote(config['balance']),
        'session_id': session_id,
        'session_type': session_type,
        # 'appip': basic_config['app_id'],
    }
    headers = {
        'Cookie': "; ".join('%s=%s' % (k, v) for k, v in cookie.items()),
    }

    app_key = get_platform_app_key(basic_config, is_sandbox)

    app_key = '%s&' % app_key

    params['appid'] = basic_config['app_id']
    params['ts'] = int(time.time())

    params['sig'] = hmac_sha1_sig('GET', config['balance'], params, app_key)

    host = get_host(is_sandbox)

    url = '%s%s?%s' % (host, config['balance'], urllib.urlencode(params))

    http_code, content = http.get(url, headers=headers, timeout=10)

    if http_code != 200:
        return False

    obj = json.loads(content)

    # if obj['ret'] != 0:
    #     return False

    return obj


def pay(login_type, params, is_sandbox=False):
    """ 扣除游戏币接口, 微信登录态和手Q登录态使用的支付接口相同，支付ID相同； 服务端使用的appid和appkey都使用手Qappid和appkey

    :param login_type: 环境 1: 手机QQ 2: 微信
    :param params:
    :param is_sandbox: 是否沙箱
    """
    basic_env = mapping['1']
    env = mapping[login_type]

    config = PLATFORM_SETTINGS.get(env)
    if not config:
        return False

    basic_config = PLATFORM_SETTINGS.get(basic_env)

    if env == 'wechat':     # 微信
        session_type = 'wc_actoken',
        session_id = 'hy_gameid'
    else:                   # 手机QQ
        session_type = 'kp_actoken',
        session_id = 'openid'

    cookie = {
        'org_loc': urllib.quote(config['pay']),
        'session_id': session_id,
        'session_type': session_type,
        # 'appip': basic_config['app_id']
    }
    headers = {
        'Cookie': "; ".join('%s=%s' % (k, v) for k, v in cookie.items()),
    }

    app_key = get_platform_app_key(basic_config, is_sandbox)

    app_key = '%s&' % app_key

    params['appid'] = basic_config['app_id']
    params['ts'] = int(time.time())

    params['sig'] = hmac_sha1_sig('GET', config['pay'], params, app_key)

    host = get_host(is_sandbox)

    url = '%s%s?%s' % (host, config['pay'], urllib.urlencode(params))

    http_code, content = http.get(url, headers=headers, timeout=10)

    if http_code != 200:
        return False

    obj = json.loads(content)

    if obj['ret'] != 0:
        return False

    obj['game_platform'] = config['name']

    return obj