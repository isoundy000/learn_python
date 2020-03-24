#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

KBEFOREBATTLE = 1                   # 战斗前触发
KBEFOREATTACK = 2                   # 攻击前触发代替攻击
KATTACK = 3                         # 攻击触发器标志
KBEFOREHERT = 4                     # 受伤后触发技能 ，原为受伤前触发器，由于某些特殊原因，改为受伤后触发
KBEATTACK = 5                       # 被攻击触发器标志 ， 原为受伤后触发器，由于某些原因，现改为受伤前触发
KDEAD = 6                           # 某个单位死亡
KBEFOREROUND = 7                    # 回合排序前触发技能
KAFTERHURT = KBEFOREHERT            # 受伤后触发器

KBUFFATTACK = 10000                 # buff攻击前触发效果
KBUFFBEATTACK = KBUFFATTACK + 1     # buff被攻击前触发效果
KBUFFDEAD = KBUFFATTACK + 2         # buff死亡触发效果
KBUFFADDBUFF = KBUFFATTACK + 3      # buff被增加buff的时候触发效果
KBUFFBEFOREROUND = KBUFFATTACK + 4  # buff回合排序前触发
KBUFFKEEP = KBUFFATTACK + 5         # buff持续生效


key_to_tregger = {
    "KBEFOREBATTLE": KBEFOREBATTLE,
    "KBEFOREATTACK": KBEFOREATTACK,
    "KATTACK": KATTACK,
    "KBEFOREHERT": KBEFOREHERT,
    "KBEATTACK": KBEATTACK,
    "KDEAD": KDEAD,
    "KBEFOREROUND": KBEFOREROUND,
    "KAFTERHURT": KAFTERHURT,

    "KBUFFATTACK": KBUFFATTACK,
    "KBUFFBEATTACK": KBUFFBEATTACK,
    "KBUFFDEAD": KBUFFDEAD,
    "KBUFFADDBUFF": KBUFFADDBUFF,
    "KBUFFBEFOREROUND": KBUFFBEFOREROUND,
    "KBUFFKEEP": KBUFFKEEP,
}