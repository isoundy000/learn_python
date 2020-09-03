#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/8/21

"""
测试方法:
复制所需代码到管理器-动态代码补丁，SERVERIDS填写:UT9999000001，执行
"""

# 快速初始化用户数据，SERVERIDS填写:UT9999000001
import time
import json
from poker.entity.dao import gamedata
from newfish.entity import config
from newfish.entity.skill import skill_system

userId = 10001
level = 30
level = min(level, config.getMaxUserLevel())
exp = 0


def _main():
    gunLevel = gunLevel_m = 2100 + level
    gunLevel = min(gunLevel, config.getMaxGunLevel(0))
    gunLevel_m = min(gunLevel_m, config.getMaxGunLevel(1))
    userGuideStep = json.dumps(config.getPublic("allGuideIds", []))
    gamedata.setGameAttrs(userId, 44, ["level", "exp", "gunLevel", "gunLevel_m", "userGuideStep", "redState"],
                          [level, exp, gunLevel, gunLevel_m, userGuideStep, 1])
    for skillId in config.getAllSkillId():
        skillInfo = [5, 20, 20, 0, 0]
        skill_system.setSkill(userId, skillId, skillInfo)


from freetime.core.timer import FTLoopTimer
FTLoopTimer(0.1, 0, _main).start()
# 快速初始化用户数据


# 支付测试, SERVERIDS填写:HT9999000001
userId = 10247
productId = "TY0044C00120001"
gameId = 44


def _main():
    from freetime.entity.msg import MsgPack
    from freetime.util import log as ftlog
    from poker.util import webpage, strutil
    from poker.util.constants import CLIENT_SYS_H5
    from poker.entity.dao import daobase, sessiondata
    from poker.entity.configure import gdata
    from poker.protocol import router
    from hall.entity import hallstore, hallconf
    # 开始支付
    serverUrl = gdata.httpGame()
    product = hallstore.findProduct(gameId, userId, productId)
    appId = 9999
    appKey = hallconf.getAppKeyInfo(appId).get("key", "")
    clientId = sessiondata.getClientId(userId)
    clientOs = sessiondata.getClientIdSys(userId)
    if clientOs == CLIENT_SYS_H5:
        # 发起支付请求
        httpUrl = serverUrl + "/open/v4/pay/order"
        datas = {
            "userId": userId,
            "appId": appId,
            "wxAppId": "wx30efe34580243475",
            "clientId": clientId,
            "imei": "null",
            "uuid": "9503fcb2e234423081a13010cd401554",
            "prodId": productId,
            "prodName": product.displayName,
            "prodCount": 1,
            "prodPrice": product.price,
            "chargeType": "wxapp.iap",
            "gameId": gameId,
            "appInfo": "",
            "mustcharge": 1
        }
        ret, _ = webpage.webgetJson(httpUrl, datas)
        if ret.get("result").get("code") != 0:
            ftlog.error("pay test error", ret, datas)
            return
        platformOrder = ret.get("result").get("chargeInfo").get("platformOrderId")
        chargeData = daobase._executePayDataCmd("HGET", "sdk.charge:%s" % platformOrder, "consume")
        orderId = strutil.loads(chargeData, False, True, {}).get("prodOrderId")
        # SDK通知游戏服钻石变更
        httpUrl = serverUrl + "/v2/game/charge/notify"
        datas = {
            "appId": appId,
            "clientId": clientId,
            "userId": userId,
            "buttonId": productId,
            "diamonds": int(product.priceDiamond),
            "rmbs": float(product.price)
        }
        ret = webpage.webget(httpUrl, datas)
        print ret
        # SDK通知游戏服发货
        httpUrl = serverUrl + "/v2/game/consume/delivery"
        datas = {
            "apiver": 2,
            "appId": appId,
            "appInfo": "1",
            "chargeType": "wxwap",
            "chargedDiamonds": int(product.priceDiamond),
            "chargedRmbs": float(product.price),
            "clientId": clientId,
            "consumeCoin": product.priceDiamond,
            "consumeId": orderId,
            "orderId": orderId,
            "platformOrder": platformOrder,
            "prodCount": 1,
            "prodId": productId,
            "prodPrice": product.price,
            "userId": userId
        }
        webpage.webget(httpUrl, datas, appKey)
    else:
        # SDK通知游戏服钻石变更
        httpUrl = serverUrl + "/api/hall5/store/charge/notify"
        datas = {
            "appId": appId,
            "userId": userId,
            "chargedDiamonds": int(product.priceDiamond),
            "chargedRmbs": float(product.price),
            "clientId": clientId,
            "prodId": productId,
            "realGameId": 9998
        }
        ret = webpage.webget(httpUrl, datas, appKey)
        print ret
from freetime.core.timer import FTLoopTimer
FTLoopTimer(0.1, 0, _main).start()
# 支付测试


# 背包中添加宝箱，SERVERIDS填写:UT9999000001
userId = 10001
chestId = 31101
chestNum = 4
def _main():
    from newfish.entity.chest import chest_system
    for _ in xrange(chestNum):
        chest_system.newChestItem(userId, chestId, "BI_NFISH_NEW_USER_REWARDS")

from freetime.core.timer import FTLoopTimer
FTLoopTimer(0.1, 0, _main).start()
# 背包中添加宝箱


# 回馈赛添加机器人，SERVERIDS填写:GR0044001_999
def _main():
    from poker.entity.configure import gdata
    from newfish.room.time_point_match_room import FishTimePointMatchRoom
    roomId = 441041000
    count = 5
    gdata.rooms()[roomId]._callRobotSigninMatch(count)

from freetime.core.timer import FTLoopTimer
FTLoopTimer(0.1, 0, _main).start()
# 回馈赛添加机器人


# 机器人参加比赛(测试服含机器人总人数不能超过70), SERVERIDS填写:UT9999000001
import json, random
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import userdata, gamedata, onlinedata

roomId = 441041000
count = 70

for x in xrange(count):
    userId = 1 + x
    onlinedata.cleanOnlineLoc(userId)
    userdata.setSessionData(userId, {"ci": "robot_3.7_-hall6-robot"})
    luckyValue = random.randint(1, 10000)
    rankArr = []
    for _ in xrange(5):
        rankArr.append(random.randint(0,50))
    gamedata.setGameAttrs(userId, 44, ["level", "gunSkinId", "userGuideStep","m.44101"], [1, 0, json.dumps([1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2200, 2300]),
        json.dumps({"bestRank": 1, "bestRankDate": 1523956838, "isGroup": 0, "crownCount": 4, "playCount": 4, "luckyValue": luckyValue, "recentRank": rankArr})])
    mo = MsgPack()
    mo.setCmd("room")
    mo.setParam("action", "signin")
    mo.setParam("userId", userId)
    mo.setParam("gameId", 44)
    mo.setParam("roomId", roomId)
    mo.setParam("clientId", "robot_3.7_-hall6-robot")
    router.sendRoomServer(mo, roomId)
    mo.setParam("action", "enter")
    router.sendRoomServer(mo, roomId)
# 机器人参加比赛


# 50%概率捕获，SERVERIDS填写:GT0044001_999
from newfish.table.table_base import FishTable
from newfish.table.multiple_table import FishMultipleTable

def getCatchProbb(self, player, wpConf, fId, fIdsCount=1, superBullet=None, extendId=0, aloofOdds=0, nonAloofOdds=0, stageId=0, datas=None):
    # 以下注释打开即为正常概率
    # return self._getCatchProbb(player, wpConf, fId, fIdsCount, superBullet, extendId, aloofOdds, nonAloofOdds, stageId, datas)
    return 5000

FishTable.getCatchProbb = getCatchProbb
FishMultipleTable.getCatchProbb = getCatchProbb
# 50%概率捕获


# 技能50%捕获，SERVERIDS填写:GT0044001_999
import time
import random
import math

import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import gamedata
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.skill.skill_release import SkillBase

def getSkillCatchProbb(self, fId, fIdsCount, realPower, probbRadix, aloofOdds, nonAloofOdds):
    probb = 5000
    ftlog.debug("getSkillCatchProbb->50%","userId =", self.player.userId,"probb =", probb)
    return probb, realPower

SkillBase.getSkillCatchProbb = getSkillCatchProbb
# 技能50%捕获






# 测试数据库key
def _main():
    userId = 116009
    import time
    import json
    from newfish.entity import config, util, store, weakdata
    from newfish.entity.redis_keys import GameData, WeakData
    import freetime.util.log as ftlog
    data = weakdata.getDayFishData(userId, 'ceshishuju', [])
    if not data:
        weakdata.setDayFishData(userId, 'ceshishuju', json.dumps(["7909", time.time()]))
        weakdata.setDayFishData(userId, 'ceshishuju', json.dumps(["7903", time.time()]))


from freetime.core.timer import FTLoopTimer
FTLoopTimer(5, 0, _main).start()