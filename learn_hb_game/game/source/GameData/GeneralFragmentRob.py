#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from Source.DataBase.Table.t_general import t_general
from Source.GameConfig.GameConfigManager2 import GameConfigManager
from Source.DataBase.Common.DBEngine import session_scope


# 拥有武将碎片的玩家 {cid: [rid1, rid2]}
GENERAL_FRAGMENT_HAVE = {

}


def Add(cid, rid):
    '''
    添加到缓存中
    :param cid: 武将碎片cid
    :param rid: 玩家rid
    :return:
    '''
    global GENERAL_FRAGMENT_HAVE
    if not GENERAL_FRAGMENT_HAVE.has_key(cid):
        GENERAL_FRAGMENT_HAVE[cid] = [rid]
    else:
        if rid not in GENERAL_FRAGMENT_HAVE[cid]:
            GENERAL_FRAGMENT_HAVE[cid].append(rid)


def Init():
    '''
    AccServerSyncConfig 同步配置的时候清空缓存
    :return:
    '''
    global GENERAL_FRAGMENT_HAVE
    GENERAL_FRAGMENT_HAVE = {}
    generalsConfig = GameConfigManager.Data()["general"]    # 武将的配置
    for sCid, config in generalsConfig.items():
        cid = int(sCid)
        with session_scope() as session:
            generals = session.query(t_general.rid).filter(t_general.cid == cid).limit(20).all()  # 获取每个玩家20武将的信息
            for general in generals:
                Add(cid, general.rid)


def Del(cid, rid):
    '''
    删掉公共缓存数据中拥有碎片的玩家
    :param cid: 武将碎片cid
    :param rid: 玩家rid
    :return:
    '''
    global GENERAL_FRAGMENT_HAVE
    if GENERAL_FRAGMENT_HAVE.has_key(cid):
        GENERAL_FRAGMENT_HAVE[cid].remove(rid)