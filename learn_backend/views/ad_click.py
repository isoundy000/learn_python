#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
积分墙相关 数据 记录各个设备激活与否的相关信息：
    {'ts': 0,
    'source': 'yijifen',                            # 广告平台来源
    'callback': 'http://www.baidu.com',             # 回调地址
    'deviceid': '0C74C2E9F2D0'                      # 设备标识
    'idfa': '99AD5E51-1164-47E4-BF0F-69646AE8F5B6', # 设备标识
    'mac': '0C74C2E9F2D0',                          # 设备标识
    'activate': False,                              # 是否激活
    'uids': {                                       # qiku 腾讯云平台才有的字段，标记用户达到的阶段
        uid: [step1, step2, step3]
        }
    }
"""
import urllib
import time
import settings
import game_config

from models.code import Adver
from lib.utils import http
from logics.user import User as UserL
# from logics.gift import add_gift

URL = 'https://itunes.apple.com/us/app/chao-ji-ying-xiong/id683031739?l=zh&ls=1&mt=8'
YOUXIDUO_AD_URL = 'https://itunes.apple.com/cn/app/chao-ji-ying-xiong/id683031739?mt=8'
APPID = '683031739'


def ad_callback(env, lv=2):
    """游戏内回调各种广告平台
    """
    device_mark = env.get_argument('device_mark', '')
    info = Adver.get(device_mark)
    if info and not info['activate']:
        callback_url = info['callback']
        need_lv = game_config.scorewall.get(info['source'], lv)
        need_lv = 2 if need_lv < 2 else 5 if need_lv > 5 else need_lv
        if lv != need_lv:
            return
        if callback_url:
            activateip = env.request.headers.get('X-Real-Ip', '')
            acts = time.time()
            info['acts'] = int(acts)
            info['activateip'] = activateip

            if info['source'] == 'anwo':
                callback_url += '&acts=%(acts)s&activateip=%(activateip)s' % {'acts': int(acts * 1000), 'activateip': activateip}
            try:
                rc, data = http.get(callback_url, timeout=2)
            except:
                rc = 599
            if rc == 200:
                info['activate'] = True
                Adver.activate(device_mark, info)


def update_qiku_mid_info(user, mid=None):
    """
    更新设备激活
    """
    mid = mid or user.mid_qiku
    mac = user.device_mark
    info = Adver.get(mid)
    if not info:
        info = {
            'ts': time.time(),
            'source': 'qiku',
            'callback': '',
            'deviceid': mac,
            'idfa': mid,
            'mac': mac,
            'activate': False,
            'openudid': '',
            'uids': {
                # uid: [step1, step2, step3]
            }
        }
    if user.uid not in info['uids']:
        info['uids'][user.uid] = []
    Adver.update(mid, info)


