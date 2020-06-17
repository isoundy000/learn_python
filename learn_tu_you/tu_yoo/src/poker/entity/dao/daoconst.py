#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2
from poker.entity.dao import dataschema
from poker.util import city_locator

OFFLINE = 0     # 用户不在线
ONLINE = 1      # 用户在线

ATT_CHIP = 'chip'               # 金币
ATT_COIN = 'coin'               # 金币
ATT_DIAMOND = 'diamond'         # 钻石
ATT_COUPON = 'coupon'           # 奖券
ATT_TABLE_CHIP = 'tablechip'    # 桌子金币
ATT_EXP = 'exp'                 # 经验
ATT_CHARM = 'charm'             #
ATT_NAME = 'name'
ATT_TRU_NAME = 'truename'
ATT_TABLE_ID = 'tableId'
ATT_SEAT_ID = 'seatId'
ATT_CLIENT_ID = 'clientId'
ATT_APP_ID = 'appId'

HKEY_USERDATA = 'user:'         # 用户数据
HKEY_GAMEDATA = 'gamedata:'     # 游戏数据
HKEY_STATEDATA = 'statedata:'   # 状态数据
HKEY_ONLINE_STATE = 'os:'
HKEY_ONLINE_LOC = 'ol:'
HKEY_PLAYERDATA = 'playerdata:'
HKEY_TABLECHIP = 'tablechip:'
HKEY_TABLEDATA = 'tabledata:%d:%d'


FILTER_KEYWORD_FIELDS = {ATT_NAME, ATT_TRU_NAME}
FILTER_MUST_FUNC_FIELDS = {ATT_CHIP, ATT_DIAMOND, ATT_COIN, ATT_COUPON, ATT_CHARM}

OLD_COUPON_ITEMID = '50'
VIP_ITEMID = '88'

CHIP_NOT_ENOUGH_OP_MODE_NONE = 0
CHIP_NOT_ENOUGH_OP_MODE_CLEAR_ZERO = 1

CHIP_TYPE_CHIP = 1  # 金币
CHIP_TYPE_TABLE_CHIP = 2  # TABLE_CHIP
CHIP_TYPE_COIN = 3  # COIN
CHIP_TYPE_DIAMOND = 4  # DIAMODN
CHIP_TYPE_COUPON = 5  # COUPON
CHIP_TYPE_ITEM = 6  # ITEM
CHIP_TYPE_ALL = (CHIP_TYPE_CHIP, CHIP_TYPE_TABLE_CHIP, CHIP_TYPE_COIN, CHIP_TYPE_DIAMOND, CHIP_TYPE_COUPON, CHIP_TYPE_ITEM)


###############################################################################
# USER 数据库数据键值定义
###############################################################################
