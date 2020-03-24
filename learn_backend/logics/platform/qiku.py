#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import http
import json
import hashlib
import urllib
import hmac
import binascii

import os
import settings

from tornado.httputil import HTTPHeaders
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPClient


# 平台名字
PLATFORM_NAME = 'qiku'
# 应用ID
APP_ID = '1101819566'
# 分配的应用KEY
APP_KEY = '0mR2qHHdjzg7DeH9&'

# 正式环境支付扣费验证地址
QIKU_VERIFY_RECEIPTS_URL = 'https://openapi.tencentyun.com'
# 沙箱环境支付扣费验证地址
QIKU_SANDBOX_VERIFY_RECEIPTS_URL = 'http://119.147.19.43'


def login_verify(uid, session_id):
    pass


def payment_verify(params, sandbox=False):
    method = 'GET'
    url_path = '/mpay/pay_m'

    sig = hmac_sha1_sig(method, url_path, params, APP_KEY)
    params['sig'] = sig

    if sandbox:
        url = '%s%s?%s' % (QIKU_SANDBOX_VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))
    else:
        url = '%s%s?%s' % (QIKU_VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))

    cookies = '; '.join(['session_id=openid', 'session_type=kp_actoken', 'org_loc=%s' % url_path])
    headers = HTTPHeaders()
    headers.add("Cookie", cookies)

    # http = HTTPClient()
    # request = HTTPRequest(url, headers=headers)
    #
    # response = http.fetch(request, validate_cert=False)
    # rc, data = response.code, response.body
    rc, data = http.get(url, headers=headers)

    if sandbox:
        path = os.path.join(settings.BASE_ROOT, 'logs', 'pay_%s_%s.txt' % ('pay', time.strftime('%F-%T')))
        f = open(path, 'w')
        f.write(repr({'headers': headers, 'url': url, 'response': data, 'params': params}))
        f.close()

    data = json.loads(data)
    if rc != 200:
        return False, data

    if data['ret'] != 0:
        return False, data
    return True, data


def get_qiku_balance(params, sandbox=False):
    method = 'GET'
    url_path = '/mpay/get_balance_m'

    sig = hmac_sha1_sig(method, url_path, params, APP_KEY)
    params['sig'] = sig
    if sandbox:
        url = '%s%s?%s' % (QIKU_SANDBOX_VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))
    else:
        url = '%s%s?%s' % (QIKU_VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))

    cookies = '; '.join(['session_id=openid', 'session_type=kp_actoken', 'org_loc=%s' % url_path])
    headers = HTTPHeaders()
    headers.add("Cookie", cookies)

    # http = HTTPClient()
    # request = HTTPRequest(url, headers=headers)
    # response = http.fetch(request, validate_cert=False)
    # rc, data = response.code, response.body

    rc, data = http.get(url, headers=headers)
    if sandbox:
        path = os.path.join(settings.BASE_ROOT, 'logs', 'pay_%s_%s.txt' % ('qk_balance', time.strftime('%F-%T')))
        f = open(path, 'w')
        f.write(repr({'headers': headers, 'url': url, 'response': data}))
        f.close()

    data = json.loads(data)
    return data['ret'], data


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


def main(params, url_path='', pre_sig='', secret=''):
    method = 'GET'
    url_path = url_path
    secret = secret

    print 'mk_source--',  mk_source(method, url_path, params)
    sig = hmac_sha1_sig(method, url_path, params, secret)
    print sig, pre_sig, sig == pre_sig


always_safe = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
)

_safe_map = {}
for i, c in zip(xrange(256), str(bytearray(xrange(256)))):
    _safe_map[c] = c if (i < 128 and c in always_safe) else '%{:02X}'.format(i)
_safe_quoters = {}


def quote(s, safe='/'):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters.

    reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | "," | "-" | "." | "_" |

    Each of these characters is reserved in some component of a URL,
    but not necessarily in all of them.

    By default, the quote function is intended for quoting the path
    section of a URL.  Thus, it will not encode '/'.  This character
    is reserved, but in typical usage the quote function is being
    called on a path where the existing slash characters are used as
    reserved characters.

    直接copy的 urllib.quote ，只是 always_safe 里去除了 _-. 三个字符
    """
    # fastpath
    if not s:
        if s is None:
            raise TypeError('None object cannot be quoted')
        return s
    cachekey = (safe, always_safe)
    try:
        (quoter, safe) = _safe_quoters[cachekey]
    except KeyError:
        safe_map = _safe_map.copy()
        safe_map.update([(c, c) for c in safe])
        quoter = safe_map.__getitem__
        safe = always_safe + safe
        _safe_quoters[cachekey] = (quoter, safe)
    if not s.rstrip(safe):
        return s
    return ''.join(map(quoter, s))


if __name__ == '__main__':
    params = {
        'openid': 'F11669C63D76BAB0BC2F6CC869B19E53',
        'openkey': '3968DD5F3F14427EF103A05E00AB59B4',
        'pf': 'desktop_m_qq-10000144-android-2002-',
        'pfkey': '5971dce2d3035669e49a1496d590f1ba',
        'pay_token': '6554E0A9225B05A1CE4C4AF215A8C369',
        'ts': 1396522813,
        'zoneid': 1,
        'format': 'json',
        'amt': 1,
        'appid': '1101255891',
    }
    main(params, url_path='/mpay/pay_m', pre_sig='6dHhW7yDF6n3rPOjTMsn2Faf8/I=', secret='Lf6AtMEB1QlE8BYS&')

    params = {
        'openid': 'F11669C63D76BAB0BC2F6CC869B19E53',
        'openkey': '3968DD5F3F14427EF103A05E00AB59B4',
        'pf': 'desktop_m_qq-10000144-android-2002-',
        'pfkey': '5971dce2d3035669e49a1496d590f1ba',
        'pay_token': '6554E0A9225B05A1CE4C4AF215A8C369',
        'ts': 1396522716,
        'zoneid': 1,
        'format': 'json',
        'appid': 1101255891,
    }
    main(params, url_path='/mpay/get_balance_m', pre_sig='w0swu02BmhUPQyrAiS+pwuRgCcI=', secret='Lf6AtMEB1QlE8BYS&')

    print get_qiku_balance(params)

    params = {
        'appid': 24885,
        'billno': '4BE1D6AE-5324-11E3-BC76-00163EB7F40B',
        'cmd': 'check_award',
        'contractid': '24885T320131118114134',
        'openid': '000000000000000000000000025900A0',
        'payitem': 'pkg',
        'pf': 'qzone',
        'providetype': 2,
        'step': 3,
        'ts': 1385089780,
        'version': 'V3',
    }

    main(params, url_path='/cgi-bin/check_award', pre_sig='E+S6dC+hooDCtwvhnGTFIFGrfng=', secret='111222333&')
    for k, v in params.items():
        params[k] = quote(str(v))
    main(params, url_path='/cgi-bin/check_award', pre_sig='E+S6dC+hooDCtwvhnGTFIFGrfng=', secret='111222333&')

    # dev环境真实点击 的参数
    # HTTPRequest(protocol='http', host='dev.kaiqigu.net', method='GET', uri='/ad-click-qiku/?cmd=check_award&openid=f35e21eac43999514811b69805d7da4d4f4a1838&appid=1101819566&ts=1409722086&contractid=1101819566T3M20140903121140&step=3&version=V3M&billno=4859bd33f5ae795307f18824fe6da15b&payitem=461&pkey=5740d4a8971f3789d6ed94eff695db13&sig=yOWvB9A0lf0SnGvDa6Edfksgws4%3D', version='HTTP/1.1', remote_ip='127.0.0.1', headers={'Via': '1.1 mpf_proxy:80 (squid/2.6.STABLE18)', 'X-Forwarded-For': '172.27.200.138', 'X-Scheme': 'http', 'Accept': '*/*', 'User-Agent': '80', 'Host': 'dev.kaiqigu.net', 'Cache-Control': 'max-age=259200', 'X-Real-Ip': '113.108.89.16'})
    params = {
        'appid': '1101819566',
        'billno': '4859bd33f5ae795307f18824fe6da15b',
        'cmd': 'check_award',
        'contractid': '1101819566T3M20140903121140',
        'openid': 'f35e21eac43999514811b69805d7da4d4f4a1838',
        'payitem': '461',
        'pkey': '5740d4a8971f3789d6ed94eff695db13',
        # 'sig': 'yOWvB9A0lf0SnGvDa6Edfksgws4%3D',
        'step': '3',
        'ts': '1409722086',
        'version': 'V3M'
    }
    for k, v in params.items():
        params[k] = quote(str(v))
    main(params, url_path='/genesis/ad-click-qiku/', pre_sig='yOWvB9A0lf0SnGvDa6Edfksgws4=', secret=APP_KEY)