#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/8

import json

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.entity.dao import gamedata, onlinedata, userchip
from poker.protocol import router
from poker.entity.biz.exceptions import TYBizException
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.entity.events.tyevent import OnLineGameChangedEvent
from poker.servers.conn.rpc import onlines
from poker.servers.rpc import roommgr
from poker.util import strutil
from hall.entity import halluser
from hall.game import TGHall
from hall.entity.hallconf import HALL_GAMEID
from hall.entity.hallevent import EventAfterUserLogin
from hall.entity.hall_clipboardhaner import Clipboard
from hall.servers.common.base_checker import BaseMsgPackChecker
from hall.servers.util.util_helper import UtilHelper
from newfish.room import fight_room
from newfish.entity import checkin, mail_system, util, config, \
    fight_history, user_system, share_system, vip_system, weakdata, led, returner_mission, free_coin_lucky_tree
from newfish.entity.gift import newbie_7days_gift
from newfish.entity.chest import chest_system
from newfish.entity.config import FISH_GAMEID
from newfish.entity.skill import skill_system
from newfish.entity.bonusgame import starfish_bonus
from newfish.entity.honor import honor_system
from newfish.entity.gun import gun_system
from newfish.entity.fishactivity import starfish_turntable
from newfish.entity.fishactivity import slot_machine_activity, super_egg_activity, competition_activity
from newfish.entity.redis_keys import GameData, WeakData, ABTestData


@markCmdActionHandler
class UserTcpHandler(BaseMsgPackChecker):

    def __init__(self):
        self.helper = UtilHelper()

    def _check_param_sessionIndex(self, msg, key, params):
        sessionIndex = msg.getParam(key)
        if isinstance(sessionIndex, int) and sessionIndex >= 0:
            return None, sessionIndex
        return None, -1

    def _check_param_otherUserId(self, msg, key, params):
        otherUserId = msg.getParam("otherUserId")
        if otherUserId and isinstance(otherUserId, int):
            return None, otherUserId
        return "ERROR of otherUserId !" + str(otherUserId), None

    def _check_param_step(self, msg, key, params):
        step = msg.getParam(key)
        if isinstance(step, int) and step > 0:
            return None, step
        return "ERROR of step !" + str(step), -1

    def _check_param_count(self, msg, key, params):
        count = msg.getParam("count")
        if isinstance(count, int) and count > 0:
            return None, count
        return "ERROR of count !" + str(count), None

    def _check_param_gunId(self, msg, key, params):
        gunId = msg.getParam("gunId")
        if isinstance(gunId, int):
            return None, gunId
        return "ERROR of gunId !" + str(gunId), None

    def _check_param_skillId(self, msg, key, params):
        skillId = msg.getParam("skillId")
        if isinstance(skillId, int):
            return None, skillId
        return "ERROR of skillId !" + str(skillId), None

    def _check_param_actionType(self, msg, key, params):
        actionType = msg.getParam("actionType")
        if isinstance(actionType, int):
            return None, actionType
        return "ERROR of actionType !" + str(actionType), None

    def _check_param_level(self, msg, key, params):
        level = msg.getParam("level")
        if isinstance(level, int) and level > 0:
            return None, level
        return "ERROR of level !" + str(level), None

    def _check_param_install(self, msg, key, params):
        install = msg.getParam("install")
        if isinstance(install, int) and install in [0, 1, 2, 3]:
            return None, install
        return "ERROR of install !" + str(install), None

    def _check_param_installSkillId(self, msg, key, params):
        installSkillId = msg.getParam("installSkillId")
        if isinstance(installSkillId, int):
            return None, installSkillId
        return "ERROR of installSkillId !" + str(installSkillId), None

    def _check_param_uninstallSkillId(self, msg, key, params):
        uninstallSkillId = msg.getParam("uninstallSkillId")
        if isinstance(uninstallSkillId, int):
            return None, uninstallSkillId
        return "ERROR of uninstallSkillId !" + str(uninstallSkillId), None

    def _check_param_clientVersion(self, msg, key, params):
        clientVersion = msg.getParam("clientVersion")
        if clientVersion:
            return None, clientVersion
        return "ERROR of clientVersion !" + str(clientVersion), None

    def _check_param_platformOS(self, msg, key, params):
        platformOS = msg.getParam("platformOS", "")
        return None, platformOS

    def _check_param_day(self, msg, key, params):
        day = msg.getParam("day")
        if isinstance(day, int):
            return None, day
        return "ERROR of day !" + str(day), None

    def _check_param_mailIds(self, msg, key, params):
        mailIds = msg.getParam("mailIds")
        if isinstance(mailIds, list):
            return None, mailIds
        return "ERROR of mailIds !" + str(mailIds), None

    def _check_param_honorId(self, msg, key, params):
        honorId = msg.getParam("honorId")
        if isinstance(honorId, int):
            return None, honorId
        return "ERROR of honorId !" + str(honorId), None

    def _check_param_timestamp(self, msg, key, params):
        timestamp = msg.getParam("timestamp")
        if isinstance(timestamp, int):
            return None, timestamp
        return "ERROR of timestamp !" + str(timestamp), None

    def _check_param_continueWindow(self, msg, key, params):
        continueWindow = msg.getParam("continueWindow")
        if isinstance(continueWindow, int):
            return None, continueWindow
        return "ERROR of continueWindow !" + str(continueWindow), None

    def _check_param_fee(self, msg, key, params):
        fee = msg.getParam("fee")
        if isinstance(fee, list):
            return None, fee
        return "ERROR of mailIds !" + str(fee), None

    def _check_param_ftId(self, msg, key, params):
        ftId = msg.getParam("ftId")
        if isinstance(ftId, (int, str, unicode)):
            return None, ftId
        return "ERROR of ftId !" + str(ftId), None

    def _check_param_pointId(self, msg, key, params):
        pointId = msg.getParam("pointId")
        if isinstance(pointId, (int)):
            return None, pointId
        return "ERROR of pointId !" + str(pointId), None

    def _check_param_typeName(self, msg, key, params):
        typeName = msg.getParam("typeName")
        if isinstance(typeName, (str, unicode)):
            return None, typeName
        return "ERROR of typeName !" + str(typeName), None

    def _check_param_clipboardContent(self, msg, key, params):
        value = msg.getParam(key, "")
        return None, value

    def _check_param_inviter(self, msg, key, params):
        inviter = msg.getParam("inviter") or 0
        if str(inviter):
            return None, inviter
        return "ERROR of inviter !" + str(inviter), None

    def _check_param_shareId(self, msg, key, params):
        shareId = msg.getParam("shareId")
        if isinstance(shareId, int):
            return None, shareId
        return "ERROR of shareId !" + str(shareId), None

    def _check_param_typeId(self, msg, key, params):
        typeId = msg.getParam("typeId", "")
        return None, typeId

    def _check_param_shareUserId(self, msg, key, params):
        shareUserId = msg.getParam("shareUserId")
        if isinstance(shareUserId, int):
            return None, shareUserId
        return "ERROR of shareUserId !" + str(shareUserId), None

    def _check_param_groupId(self, msg, key, params):
        groupId = msg.getParam("groupId", "")
        return None, groupId

    def _check_param_order(self, msg, key, params):
        order = msg.getParam("order")
        if isinstance(order, int):
            return None, order
        return "ERROR of order !" + str(order), None

    def _check_param_extends(self, msg, key, params):
        extends = msg.getParam("extends", {})
        return None, extends

    def _check_param_itemId(self, msg, key, params):
        itemId = msg.getParam("itemId")
        if isinstance(itemId, int) and itemId > 0:
            return None, itemId
        return "ERROR of itemId !" + str(itemId), None

    def _check_param_skinId(self, msg, key, params):
        skinId = msg.getParam("skinId")
        if isinstance(skinId, int):
            return None, skinId
        return "ERROR of skinId !" + str(skinId), None

    def _check_param_protect(self, msg, key, params):
        protect = msg.getParam("protect")
        if isinstance(protect, int):
            return None, protect
        return "ERROR of protect !" + str(protect), None

    def _check_param_modify(self, msg, key, params):
        modify = msg.getParam("modify")
        if isinstance(modify, int):
            return None, modify
        return "ERROR of modify !" + str(modify), None

    def _check_param_cardId(self, msg, key, params):
        cardId = msg.getParam("cardId")
        if cardId:
            return None, cardId
        return "ERROR of cardId !" + str(cardId), None

    def _check_param_cardName(self, msg, key, params):
        cardName = msg.getParam("cardName")
        if cardName:
            return None, cardName
        return "ERROR of cardName !" + str(cardName), None

    def _check_param_accessToken(self, msg, key, params):
        accessToken = msg.getParam("accessToken")
        if accessToken:
            return None, accessToken
        return "ERROR of accessToken !" + str(accessToken), None

    def _check_param_openId(self, msg, key, params):
        openId = msg.getParam("openId")
        if openId:
            return None, openId
        return "ERROR of openId !" + str(openId), None

    def _check_param_drawMode(self, msg, key, params):
        drawMode = msg.getParam("drawMode")
        if drawMode:
            return None, drawMode
        return "ERROR of drawMode !" + str(drawMode), None

    def _check_param_act(self, msg, key, params):
        act = msg.getParam("act")
        if act:
            return None, act
        return "ERROR of act !" + str(act), None

    def _check_param_cannedNumber(self, msg, key, params):
        cannedNumber = msg.getParam("cannedNumber")
        if cannedNumber:
            return None, cannedNumber
        return "ERROR of cannedNumber!" + str(cannedNumber), None

    def _check_param_batchNumber(self, msg, key, params):
        batchNumber = msg.getParam("batchNumber", "")
        return None, batchNumber

    def _check_param_productDate(self, msg, key, params):
        productDate = msg.getParam("productDate", "")
        return None, productDate

    def _check_param_name(self, msg, key, params):
        name = msg.getParam("name")
        if name:
            return None, name
        return "ERROR of name !" + str(name), None

    def _check_param_desc(self, msg, key, params):
        desc = msg.getParam("desc", "")
        return None, desc

    def _check_param_buyType(self, msg, key, params):
        buyType = msg.getParam("buyType")
        if buyType and (buyType == "direct" or config.isThirdBuyType(buyType)):
            return "ERROR of buyType !" + str(buyType), None
        return None, buyType

    def _check_param_productId(self, msg, key, params):
        productId = msg.getParam("productId")
        if isinstance(productId, (int, str, unicode)):
            return None, productId
        return "ERROR of productId !" + str(productId), None

    def _check_param_kindId(self, msg, key, params):
        kindId = msg.getParam("kindId") or 0
        if kindId:
            if isinstance(kindId, int):
                return None, kindId
            else:
                return "ERROR of kindId !" + str(kindId), None
        return None, kindId

    def _check_param_voteResult(self, msg, key, params):
        voteResult = msg.getParam("voteResult", 0)
        if isinstance(voteResult, int):
            return None, voteResult
        return "ERROR of voteResult !" + str(voteResult), None

    def _check_param_gameResolution(self, msg, key, params):
        gameResolution = msg.getParam("gameResolution", [])
        if isinstance(gameResolution, list):
            return None, gameResolution
        return "ERROR of gameResolution !" + str(gameResolution), None

    def _check_param_actType(self, msg, key, params):
        from newfish.entity.fishactivity.fish_activity import ActivityType
        actType = msg.getParam("actType", ActivityType.SlotMachine)
        if isinstance(actType, int):
            return None, actType
        return "ERROR of actType !" + str(actType), None

    def _check_param_boxId(self, msg, key, params):
        boxId = msg.getParam("boxId", 0)
        if isinstance(boxId, int):
            return None, boxId
        return "ERROR of boxId !" + str(boxId), None

    def _check_param_nickname(self, msg, key, params):
        nickname = str(msg.getParam("nickname", ""))
        return None, nickname

    def _check_param_idx(self, msg, key, params):
        idx = msg.getParam("idx")
        if isinstance(idx, int):
            return None, idx
        return "ERROR of idx !" + str(idx), None

    def _check_param_taskId(self, msg, key, params):
        taskId = msg.getParam("taskId", "")
        if isinstance(taskId, (int, str, unicode)):
            return None, taskId
        return "ERROR of taskId !" + str(taskId), None

    def _check_param_acId(self, msg, key, params):
        acId = msg.getParam("acId", 0)
        if isinstance(acId, (str, unicode)):
            return None, acId
        return "ERROR of acId !" + str(acId), None

    def _check_param_mobile(self, msg, key, params):
        mobile = msg.getParam("mobile")
        if isinstance(mobile, int):
            return None, mobile
        return "ERROR of mobile !" + str(mobile), None

    def _check_param_vcode(self, msg, key, params):
        vcode = msg.getParam("vcode")
        if isinstance(vcode, int):
            return None, vcode
        return "ERROR of vcode !" + str(vcode), None

    def _check_param_rebateItemId(self, msg, key, params):
        rebateItemId = msg.getParam("rebateItemId", 0)
        if isinstance(rebateItemId, int) and rebateItemId >= 0:
            return None, rebateItemId
        return "ERROR of rebateItemId !" + str(rebateItemId), None

    def _check_param_mailType(self, msg, key, params):
        mailType = msg.getParam("mailType", 1)
        if isinstance(mailType, int):
            return None, mailType
        return "ERROR of mailType !" + str(mailType), None

    def _check_param_skillMode(self, msg, key, params):
        skillMode = msg.getParam("skillMode", 0)
        if skillMode == 0 or skillMode == 1:
            return None, skillMode
        return "ERROR of skillMode !" + str(skillMode), None

    def _check_param_gameMode(self, msg, key, params):
        gameMode = msg.getParam("gameMode", 0)
        if gameMode == 0 or gameMode == 1:
            return None, gameMode
        return "ERROR of gameMode !" + str(gameMode), None

    def checkForceLogout(self, userId):
        """
        检查是否运行登录
        """
        if halluser.isForceLogout(userId):
            onlines.forceLogOut(userId, "")
            return 1
        return 0

    def updateBiggestHallVersion(self, userId, gameId, clientId):
        """
        记录更新该用户最高的版本号
        """
        if gameId != HALL_GAMEID:
            return

        _, clientVer, _ = strutil.parseClientId(clientId)
        if not clientVer:
            return

        bVer = 1.0
        biggestClientIdStr = gamedata.getGameAttr(userId, gameId, "biggestHallVer")
        if biggestClientIdStr:
            bVer = float(biggestClientIdStr)

        if clientVer > bVer:
            gamedata.setGameAttr(userId, gameId, "biggestHallVer", str(clientVer))
            ftlog.debug("update user biggest hallVersion:", clientVer)

