#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import http
import time
import utils
import re
import json
import urllib
import hashlib


PLATFORM_CMGE_SETTINGS = {
    0: {    # IOS越狱版
        'game_id': 'D10046',
        'server_id': 'M1063',
        'app_key': 'qccsxup8yw80o80yk5zx',
        'secret_key': 'dxop1l01mjcyzqx2lij1',
        # 'syn_key': '12345678',
        'syn_key': 'daksrejtwkj0wpxdin6y',
        'project_id': 'P10370',
        'grant_type': 'authorization_code',
        'access_token_uri': 'http://iosrs.tisgame.com/sdksrv/auth/getToken.lg',
        'user_info_uri': 'http://iosrs.tisgame.com/sdksrv/auth/getUserInfo.lg',
    },
    1: {    # IOS正式版
        'game_id': 'D10047',
        'server_id': 'M1064',
        'app_key': 'ywh2rdlzai1o42kj6qdx',
        'secret_key': '2baxnr08qsution1p4yc',
        'syn_key': 'risx1t2ybpfqieuz52ze',
        'project_id': 'P10371',
        'grant_type': 'authorization_code',
        'access_token_uri': 'http://iosrs.tisgame.com/sdksrv/auth/getToken.lg',
        'user_info_uri': 'http://iosrs.tisgame.com/sdksrv/auth/getUserInfo.lg',
    },
    2: {    # android版
        'game_id': 'D10060A',
        'server_id': 'M1083A',
        'app_key': '10zsompz0bso3u5zljdt',
        'secret_key': 'n0c8f1qezyylhsyz9syn',
        'syn_key': 'qoibup4o6vn5rf1d6cl5',
        'project_id': 'P12272A',
        'grant_type': 'authorization_code',
        'access_token_uri': 'http://andrs.tisgame.com/andsrv/auth/getToken.lg',
        'user_info_uri': 'http://andrs.tisgame.com/andsrv/auth/getUserInfo.lg',
    }
}


# 支付验证成功返回数据
PAYMENT_SUCCESS_RETURN = 'success'
# 支付验证失败返回数据
PAYMENT_FAILURE_RETURN = 'failed'


def login_verify(authorization_code, app_type):
    """
    sid用户会话验证
    Args:
        authorization_code: authorization_code
        app_type: 标识ios类型，1表示正式版，0表示越狱版, 2表示android
    Returns:
        用户标识id
    """
    platform_mapping = {0: 'cmge', 1: 'cmgeapp', 2: 'androidcmge'}
    conf = PLATFORM_CMGE_SETTINGS[app_type]

    access_token = get_access_token(authorization_code, conf)

    if not access_token:
        return None

    userinfo_post_data = urllib.urlencode({
        'access_token': access_token,
    })
    http_code, content = http.post(conf['user_info_uri'], userinfo_post_data)
    if http_code != 200:
        return None

    obj = json.loads(content)
    # {u'username': u'U12638056', u'cmStatus': 0, u'codes': u'0', u'id': 10721935, u'sdkuserid': u'U12638056'}
    if int(obj['codes']) != 0:
        return None

    openid = obj['id']
    tel = obj.get('tel', '')
    if tel:
        # TODO: 前端发新包之后删除
        # 2014年5月20日12：00~5月30日12：00
        end_time = 1401422400   # 5月30日12：00
        if time.time() < 30 * 24 * 3600 + end_time:
            from models.user import UnameUid, User
            account = '%s_%s' % (platform_mapping.get(app_type, ''), openid)
            uu = UnameUid.get(account)
            if uu.current_server:
                uid = uu.servers.get(uu.current_server)
                if uid:
                    u = User.get(uid, uu.current_server)
                    if not u.mobile:
                        u.moblie = tel
                        u.save()

    return {
        'openid': openid,
        'access_token': access_token,
        'sdkuserid': obj['sdkuserid'],
        'username': obj['username'],
        'code': authorization_code,
        'tel': tel,
    }


def get_access_token(authorization_code, conf):
    """通过code获得token
    Args:
        authorization_code: authorization_code
        conf: 配置
    """
    token_post_data = urllib.urlencode({
        'productId': conf['game_id'],
        'redirect_uri': '1',
        'client_id': conf['app_key'],
        'client_secret': conf['secret_key'],
        'grant_type': conf['grant_type'],
        'code': authorization_code,
    })
    http_code, content = http.post(conf['access_token_uri'], token_post_data)
    if http_code != 200:
        return None

    token_data = json.loads(content)

    return token_data.get('access_token')


# bytearray是可变的二进制数据(byte)。
# 要构造bytearray对象，方法之一是将bytes数据作为bytearray()方法的参数，或者将str数据和编码作为参数。

def cmge_encode(src, syn_key):
    """用syn_key加密src数据
    """
    rs = []
    data = bytearray(src)
    keys = bytearray(syn_key)
    for idx, i in enumerate(data):
        n = (0xff & i) + (0xff & keys[idx % len(keys)])
        rs.append('@%s' % n)
    return ''.join(rs)


def cmge_decode(src, syn_key):
    """用syn_key解密src数据
    """
    if not src:
        return src

    keys = bytearray(syn_key)
    pattern = re.compile('\\d+')
    l = [int(x) for x in pattern.findall(src)]
    if not l:
        return src

    data = []
    for idx, i in enumerate(l):
        data.append(chr(i - (0xff & keys[idx % len(keys)])))
    return ''.join(data)


def payment_verify(params, app_type):
    """
    Args:
        params: 字典参数数据
            sign: 签名
            nt_data 解密出的结果
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <cmge_message>
                        <message>
                            <login_name>zzzzzzzzcgu</login_name>
                            <game_role>h1buemf-h1-9-1396861797</game_role>
                            <order_id>303222UO10000047588</order_id>
                            <pay_time>2014-04-07 17:05:27</pay_time>
                            <amount>0.01</amount>
                            <status>0</status>
                        </message>
                    </cmge_message>'
    """
    conf = PLATFORM_CMGE_SETTINGS[app_type]

    raw_sign = cmge_decode(params['sign'], conf['syn_key'])
    new_sign = hashlib.md5('nt_data=%s' % params['nt_data']).hexdigest()
    new_sign = list(new_sign)
    trans_template = [(1, 13), (5, 17), (7, 23)]
    for start, end in trans_template:
        new_sign[start], new_sign[end] = new_sign[end], new_sign[start]
    new_sign = ''.join(new_sign)

    if raw_sign != new_sign:
        return None

    order_info = cmge_decode(params['nt_data'], conf['syn_key'])

    return utils.xml2dict(order_info)


# bytearray是可变的二进制数据(byte)。
# 要构造bytearray对象，方法之一是将bytes数据作为bytearray()方法的参数，或者将str数据和编码作为参数。
def lian_xi():
    S = b"abcd"
    BA = bytearray(S)
    print [i for i in BA]
    BA[0] = 65
    print BA


if __name__ == '__main__':
    lian_xi()
    print login_verify('120cc960-321d-3a2f-88d2-147cd65ce695', 2)
    nt_data = '@160@160@227@224@222@133@224@217@233@222@211@159@229@173@154@149@151@158@88@153@201@207@206@226@214@206@216@219@180@141@191@132@189@157@176@134@137@225@170@218@210@197@204@223@225@211@207@177@153@217@217@82@182@174@180@199@214@213@155@216@209@198@222@230@211@204@207@178@179@216@207@163@234@209@223@201@167@170@162@232@203@202@217@210@224@198@215@217@181@197@221@97@171@165@170@156@157@170@101@229@211@200@212@225@209@211@203@225@220@169@166@151@216@221@221@195@219@221@162@222@162@201@156@169@165@153@154@165@168@161@151@152@168@157@169@145@154@161@111@176@153@148@160@168@162@153@166@163@222@204@215@149@214@226@231@208@206@172@114@232@214@197@208@229@209@206@206@178@170@156@154@102@170@160@185@179@154@158@102@169@148@145@161@168@164@153@163@176@166@218@220@148@220@226@215@205@205@172@114@233@197@218@202@231@219@210@207@178@169@155@155@100@164@160@172@145@154@163@86@170@150@155@156@169@172@150@161@176@166@219@203@169@214@228@225@209@206@172@114@218@209@208@224@225@230@163@154@162@167@156@166@95@216@221@231@217@215@226@116@181@215@213@204@231@231@216@168@164@179@154@221@164@216@228@237@215@167@170@101@230@201@212@222@212@217@202@168@176@166@206@215@151@220@207@229@201@220@225@151@224@201@159'
    sign = '@148@197@162@215@213@153@206@172@169@156@156@103@218@214@217@156@161@159@109@171@149@154@158@216@165@203@208@170@167@157@163@150'
    print payment_verify({'nt_data': nt_data, 'sign': sign}, 0)
    nt_data = '@109@113@171@161@161@86@173@157@163@165@156@163@163@115@89@105@95@98@85@84@154@164@154@167@149@155@161@155@114@88@140@140@119@95@107@86@85@169@171@153@159@150@148@160@164@164@156@117@83@160@162@86@116@116@115@155@158@153@152@147@162@155@170@171@146@153@152@114@113@163@156@171@164@147@154@153@115@114@163@167@152@155@161@147@163@151@164@157@111@147@166@152@155@106@108@110@98@100@102@112@100@162@166@159@154@160@146@162@150@163@156@118@109@153@148@161@154@149@169@167@157@151@113@120@102@102@103@104@103@115@95@101@101@103@99@106@93@102@108@106@108@103@104@107@93@162@100@100@97@103@115@103@152@147@160@153@148@168@166@164@150@112@111@163@167@154@156@170@144@155@151@114@103@102@104@108@97@103@99@105@102@103@103@104@98@98@99@107@110@110@103@104@97@98@104@103@102@102@105@110@109@97@162@166@153@155@169@151@154@150@113@112@165@151@176@151@165@155@160@153@115@104@103@105@101@95@99@105@98@102@109@88@98@102@109@101@110@112@105@111@109@97@163@149@174@149@171@161@158@151@113@112@150@163@166@173@159@166@113@109@99@111@103@116@96@147@160@163@170@164@171@118@109@165@167@149@169@171@170@118@97@110@98@167@169@151@171@173@164@112@111@99@162@155@170@171@146@153@152@114@113@101@154@165@152@151@146@161@154@169@170@153@152@151@113'
    sign = '@150@152@106@108@108@103@153@157@101@151@99@154@153@154@109@157@99@107@100@106@103@103@105@109@149@100@107@100@105@104@157@158'
    print payment_verify({'nt_data': nt_data, 'sign': sign}, 0)