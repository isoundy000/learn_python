#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time

import game_config
from lib.db import ModelBase
from return_msg_config import i18n_msg

MAX_NOTICE_NUM = 100
MAX_SYS_NOTICE_NUM = 10


def get_client_key(user):
    '''
    获取公告redis的客户端, 生成公告的key, 系统公告的key
    :param user:
    :return:
    '''
    server_name = user._server_name
    _client = ModelBase.get_redis_client('notice', server_name)
    NOTICE_KEY = ModelBase.make_key_cls('notice', server_name)
    SYS_NOTICE_KEY = ModelBase.make_key_cls('sys_notice', server_name)

    return _client, NOTICE_KEY, SYS_NOTICE_KEY


def get_notice(user, num=10, ts=None):
    '''
    必出的系统公告 获取公告
    :param user: 玩家
    :param num: 公告数量
    :param ts: 时间
    :return:
    '''
    _client, NOTICE_KEY, SYS_NOTICE_KEY = get_client_key(user)

    notices = [eval(x) for x in _client.lrange(SYS_NOTICE_KEY, 0, num)]
    notices.extend([eval(x) for x in _client.lrange(NOTICE_KEY, 0, num)])
    _client.ltrim(NOTICE_KEY, 0, MAX_NOTICE_NUM)

    if user and user.notice.notices:            # 玩家自身的公告
        notices.extend([user.notice.notices])
        user.notice.clear_notice()
    return notices                              # 返回公告信息


def _add_sys_notice(user, data={}):
    '''
    增加系统公告
    :param user:
    :param data:
    :return:
    '''
    _client, NOTICE_KEY, SYS_NOTICE_KEY = get_client_key(user)
    if data:
        _client.lpush(SYS_NOTICE_KEY, data)
        _client.ltrim(SYS_NOTICE_KEY, 0, MAX_SYS_NOTICE_NUM)


def _add_notice(user=None, data={}, is_self=0):
    """
    args
        user: logics.user 实例
        data: 广播信息
        is_self: 是否私有信息
    """
    if not data:
        return
    data['ts'] = int(time.time())
    _client, NOTICE_KEY, SYS_NOTICE_KEY = get_client_key(user)
    _client.lpush(NOTICE_KEY, data)
    if user and is_self:
        user.notice.add_notice(data, True)


# sort 1
def notice_4_level_up(user, **kwargs):
    """玩家升级
    args:
        user：logice.user 实例
    """
    change_lvs = kwargs.get('change_lvs', [])   # 连升多级
    if change_lvs:
        for v in game_config.notice.itervalues():
            if v['trigger_sort'] == 1:
                if v['trigger'] in change_lvs:
                    data = {
                        'msg': v['text'] % user.name,
                        'ts': int(time.time()),
                        'notice_lv': v['notice_level'],
                    }
                    _add_notice(user, data, is_self=v['is_self'])


# sort 2
def notice_4_recapture(user, **kwargs):
    """完成关卡
    args:
        user：logice.user 实例
    """
    for v in game_config.notice.itervalues():
        if v['trigger_sort'] == 2:
            if int(kwargs.get('city_id', 0)) == v['trigger']:
                data = {
                    'msg': v['text'] % user.name,
                    'notice_lv': v['notice_level']
                }
                _add_notice(user, data, is_self=v['is_self'])
                break


# sort 3
def notice_4_active(user, **kwargs):
    """活动开始
    args:
        user：logice.user 实例
    """
    # TODO: notice_4_active
    for v in game_config.notice.itervalues():
        break


# sort 4
def notice_4_get_card(user, **kwargs):
    """获得卡牌
    args:
        user：logice.user 实例
    """
    if not user:
        return

    config_id = kwargs['config_id']
    _config = kwargs.get('card_config') or game_config.character_detail[config_id]

    for v in game_config.notice.itervalues():
        if v['trigger_sort'] == 4:
            if config_id == v['trigger']:
                data = {
                    'msg': v['text'] % (user.name, _config['name']),
                    'notice_lv': v['notice_level'],
                }
                _add_notice(user, data, is_self=v['is_self'])
                break


# sort 5
def notice_4_get_equip(user, **kwargs):
    """获得装备
    args:
        user：logice.user 实例
    """
    if not user:
        return

    config_id = kwargs['config_id']
    _config = kwargs.get('equip_config') or game_config.equip[config_id]

    for v in game_config.notice.itervalues():
        if v['trigger_sort'] == 5:
            if config_id == v['trigger']:
                data = {
                    'msg': v['text'] % (user.name, _config['name']),
                    'notice_lv': v['notice_level'],
                }
                _add_notice(user, data, is_self=v['is_self'])
                break


# sort 6
def notice_4_get_item(user, **kwargs):
    """获得道具
    args:
        user：logice.user 实例
    """
    if not user:
        return

    config_id = kwargs['config_id']
    _config = kwargs.get('item_config') or game_config.item[config_id]

    for v in game_config.notice.itervalues():
        if v['trigger_sort'] == 6:
            if config_id == v['trigger']:
                data = {
                    'msg': v['text'] % (user.name, _config['name']),
                    'notice_lv': v['notice_level'],
                }
                _add_notice(user, data, is_self=v['is_self'])
                break


# sort 7
def notice_4_kill_boss(user, **kwargs):
    """击杀boss
    args:
        user：logice.user 实例
    """
    if not user:
        return
    # config_id = kwargs['config_id']
    for v in game_config.notice.itervalues():
        if v['trigger_sort'] == 7:
            data = {
                'msg': v['text'] % (user.name, i18n_msg[1036]),
                'notice_lv': v['notice_level'],
            }
            _add_notice(user, data, is_self=v['is_self'])
            break


# sort 8
def notice_4_arena_top_one(user, **kwargs):
    """竞技场排名第一
    args:
        user：logice.user 实例
    """
    target_user = kwargs['target_user']
    for v in game_config.notice.itervalues():
        if v['trigger_sort'] == 8:
            data = {
                'msg': v['text'] % (user.name, target_user.name),
                'notice_lv': v['notice_level'],
            }
            _add_notice(user, data, is_self=v['is_self'])
            break


# sort 9
def notice_4_arena_continue_win(user, **kwargs):
    """竞技场连胜10场
    args:
        user：logice.user 实例
    """
    for v in game_config.notice.itervalues():
        if v['trigger_sort'] == 9:
            if v['trigger'] == user.arena.continue_win:
                data = {
                    'msg': v['text'] % (user.name),
                    'notice_lv': v['notice_level'],
                }
                _add_notice(user, data, is_self=v['is_self'])
                break