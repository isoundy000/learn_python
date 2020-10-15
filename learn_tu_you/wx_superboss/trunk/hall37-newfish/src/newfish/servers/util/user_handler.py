# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/5/13.
"""

import json

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.entity.dao import gamedata, onlinedata, userchip, sessiondata
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
from newfish.entity.gift import level_gift


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

    def recoverUserTableChips(self, userId, clientId):
        try:
            tableChips = userchip.getTableChipsAll(userId)
            ftlog.debug("recoverUserTableChips->", tableChips)
            datas = None
            if isinstance(tableChips, dict):
                datas = tableChips
            elif isinstance(tableChips, list):
                datas = {}
                for x in xrange(len(tableChips) / 2):
                    datas[tableChips[x * 2]] = tableChips[x * 2 + 1]
            delTablesIds = []
            for tableId, tchip in datas.items():
                tableId, tchip = strutil.parseInts(tableId, tchip)
                troomId = strutil.getTableRoomId(tableId)
                if not troomId or troomId <= 0:
                    delTablesIds.append(tableId)
                    continue
                gameId, _, _, _ = strutil.parseInstanceRoomId(troomId)
                if not gameId or gameId <= 0:
                    delTablesIds.append(tableId)
                    continue
                seatId = 0
                try:
                    seatId, _ = roommgr.doCheckUserLoc(userId, gameId, troomId, tableId, clientId)
                except:
                    delTablesIds.append(tableId)
                    ftlog.error()
                    continue

                if not seatId:
                    userchip.moveAllTableChipToChip(userId, gameId, "TABLE_TCHIP_TO_CHIP", troomId, clientId, tableId)
                    delTablesIds.append(tableId)
                else:
                    # the user is on the table , do not clear
                    pass

            if delTablesIds:
                userchip.delTableChips(userId, delTablesIds)
        except:
            ftlog.error()

    def _isReconnect(self, userId, gameId, clientId, loc):
        """是否重连"""
        if loc:
            locList = loc.split(":")
            for subLoc in locList:
                if subLoc != "0.0.0.0":
                    return True
        return False

    @markCmdActionMethod(cmd="user", action="bind", clientIdVer=4.5)
    def doUserBind_4_5(self, userId, gameId, clientId, isFirstuserInfo, clipboardContent, inviter):
        # 检查是否禁止登录
        if self.checkForceLogout(userId):
            return
        self.updateBiggestHallVersion(userId, gameId, clientId)

        loc = ""
        isReconnect = False
        if isFirstuserInfo:
            loc = onlinedata.checkUserLoc(userId, clientId, 0)
            self.recoverUserTableChips(userId, clientId)
            isReconnect = self._isReconnect(userId, gameId, clientId, loc)
            #         # 更新基本信息
            #         halluser.updateUserBaseInfo(userId, clientId, runcmd.getMsgPack())
        clipboard = Clipboard.parse(clipboardContent)
        # 登录游戏处理
        isdayfirst, isCreate = halluser.loginGame(userId, gameId, clientId, clipboard)
        # 发送udata响应消息
        self.helper.sendUserInfoResponse(userId, gameId, clientId, loc, 1, 0)
        # 发送gdata响应消息
        self.helper.sendUserInfoResponse(userId, gameId, clientId, loc, 0, 1)
        # 发送响应消息
        if not isReconnect:
            self.helper.sendTodoTaskResponse(userId, gameId, clientId, isdayfirst)

        # 分析clipboardConent内容，根据分析结果 功能
        event = EventAfterUserLogin(userId, gameId, isdayfirst, isCreate, clientId, loc, clipboard)
        event.inviter = inviter
        TGHall.getEventBus().publishEvent(event)

        # 标记游戏时长开始
        gamedata.incrPlayTime(userId, 0, gameId)
        # BI日志统计
        bireport.userBindUser(gameId, userId, clientId)
        bireport.reportGameEvent("BIND_USER",
                                 userId, gameId, 0, 0, 0, 0, 0, 0, [], clientId)

        evt = OnLineGameChangedEvent(userId, gameId, 1, clientId)
        TGHall.getEventBus().publishEvent(evt)

    @markCmdActionMethod(cmd="user", action="heart_beat", clientIdVer=4.5)
    def doUserHeartBeat(self, userId, gameId, clientId):
        led.doSendLedToUser(userId)
        if ftlog.is_debug():
            ftlog.debug("user|heart_beat", userId, gameId, clientId)

    @markCmdActionMethod(cmd="user", action="fishNotice", clientIdVer=0, scope="game", lockParamName="userId")
    def doSendFishNotice(self, userId):
        util.doSendFishNotice(userId)

    @markCmdActionMethod(cmd="user", action="fishCommonConfig", clientIdVer=0, scope="game", lockParamName="userId")
    def doSendFishCommonConfig(self, userId):
        ftlog.debug("doSendFishCommonConfig", userId)
        # 发送common数据
        from newfish.entity import user_system
        user_system.sendCommonConfig(userId)

    @markCmdActionMethod(cmd="user", action="fishTips", clientIdVer=0, scope="game", lockParamName="userId")
    def doSendFishTips(self, userId, clientId, clientVersion):
        user_system.sendVersionUpdateTipsMsg(userId, clientId, clientVersion)

    @markCmdActionMethod(cmd="user", action="fishUserInfo", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetUserInfoNew(self, userId, gameId, clientId, otherUserId, kindId=0):
        user_system.doGetUserInfo(userId, otherUserId, kindId)

    @markCmdActionMethod(cmd="user", action="fishMailList", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetAllMails(self, userId, gameId, clientId, mailType):
        """发送收件箱邮件列表消息"""
        mail_system.doGetAllMails(userId, mailType)

    @markCmdActionMethod(cmd="user", action="fishMailReceive", clientIdVer=0, scope="game", lockParamName="userId")
    def doDealMail(self, userId, gameId, clientId, mailIds, mailType):
        """领取邮件奖励"""
        mail_system.doReceiveMail(userId, mailIds, mailType)

    @markCmdActionMethod(cmd="user", action="fishMailDelete", clientIdVer=0, scope="game", lockParamName="userId")
    def doDeleteMail(self, userId, gameId, clientId, mailIds, mailType):
        """执行删除邮件并发送消息"""
        mail_system.doDeleteMail(userId, mailIds, mailType)

    @markCmdActionMethod(cmd="user", action="fishFightHistory", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFightHistory(self, userId, gameId, clientId):
        fight_history.doGetAllHistorys(userId)

    @markCmdActionMethod(cmd="user", action="skill_list", clientIdVer=0, scope="game", lockParamName="userId")
    def getSkillList(self, userId, gameId, clientId, skillMode):
        ftlog.debug("getSkillList", userId, gameId, clientId, skillMode)
        mo = MsgPack()
        mo.setCmd("skill_list")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("skillMode", skillMode)
        mo.setResult("skills", skill_system.getSkillList(userId, skillMode))
        router.sendToUser(mo, userId)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.skillMode, skillMode)

    @markCmdActionMethod(cmd="user", action="skill_upgrade", clientIdVer=0, scope="game", lockParamName="userId")
    def doUpgradeSkill(self, userId, gameId, clientId, skillId, actionType):
        ftlog.debug("doUpgradeSkill", userId, gameId, skillId, actionType)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "skill_upgrade")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("skillId", skillId)
            mo.setParam("actionType", actionType)
            router.sendTableServer(mo, roomId)
        else:
            mo = MsgPack()
            mo.setCmd("skill_upgrade")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("userId", userId)
            mo.setResult("skillId", skillId)
            mo.setResult("actionType", actionType)
            code, starLevel, originalLevel, currentLevel, previousLevel = skill_system.upgradeSkill(userId, skillId, actionType)
            mo.setResult("starLevel", starLevel)
            mo.setResult("originalLevel", originalLevel)
            mo.setResult("currentLevel", currentLevel)
            mo.setResult("previousLevel", previousLevel)
            mo.setResult("code", code)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="skill_degrade", clientIdVer=0, scope="game", lockParamName="userId")
    def doDegradeSkill(self, userId, gameId, clientId, skillId, level):
        ftlog.debug("doDegradeSkill", userId, gameId, skillId, level)
        mo = MsgPack()
        mo.setCmd("skill_degrade")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("skillId", skillId)
        code, originalLevel, beforeLevel, currentLevel = skill_system.degradeSkill(userId, skillId, level)
        mo.setResult("originalLevel", originalLevel)
        mo.setResult("beforeLevel", beforeLevel)
        mo.setResult("currentLevel", currentLevel)
        mo.setResult("code", code)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="skill_restore", clientIdVer=0, scope="game", lockParamName="userId")
    def doRestoreSkill(self, userId, gameId, clientId, skillId):
        ftlog.debug("doRestoreSkill", userId, gameId, skillId)
        mo = MsgPack()
        mo.setCmd("skill_restore")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("skillId", skillId)
        code, originalLevel, currentLevel = skill_system.restoreSkill(userId, skillId)
        mo.setResult("originalLevel", originalLevel)
        mo.setResult("currentLevel", currentLevel)
        mo.setResult("code", code)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="skill_install", clientIdVer=0, scope="game", lockParamName="userId")
    def doInstallSkill(self, userId, gameId, clientId, skillId, skillMode, install):
        ftlog.debug("doInstallSkill", userId, gameId, skillId, skillMode, install)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "skill_install")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("skillId", skillId)
            mo.setParam("skillMode", skillMode)
            mo.setParam("install", install)
            router.sendTableServer(mo, roomId)
        else:
            mo = MsgPack()
            mo.setCmd("skill_install")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("userId", userId)
            mo.setResult("skillId", skillId)
            mo.setResult("skillMode", skillMode)
            mo.setResult("install", install)
            code = skill_system.installSkill(userId, skillId, skillMode, install)
            mo.setResult("code", code)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="skill_replace", clientIdVer=0, scope="game", lockParamName="userId")
    def doReplaceSkill(self, userId, gameId, clientId, skillMode, installSkillId, uninstallSkillId):
        ftlog.debug("doReplaceSkill", userId, gameId, skillMode, installSkillId, uninstallSkillId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "skill_replace")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("skillMode", skillMode)
            mo.setParam("installSkillId", installSkillId)
            mo.setParam("uninstallSkillId", uninstallSkillId)
            router.sendTableServer(mo, roomId)
        else:
            mo = MsgPack()
            mo.setCmd("skill_replace")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("userId", userId)
            mo.setResult("skillMode", skillMode)
            mo.setResult("installSkillId", installSkillId)
            mo.setResult("uninstallSkillId", uninstallSkillId)
            code = skill_system.replaceSkill(userId, skillMode, installSkillId, uninstallSkillId)
            mo.setResult("code", code)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="guns_list", clientIdVer=0, scope="game", lockParamName="userId")
    def getGunList(self, userId, gameId, clientId, gameMode):
        ftlog.debug("getGunSkinList", userId, gameId, clientId, gameMode)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "guns_list")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("gameMode", gameMode)
            router.sendTableServer(mo, roomId)
        else:
            gun_system.sendGunListMsg(userId, gameMode)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.gunMode, gameMode)

    @markCmdActionMethod(cmd="user", action="expired_gun", clientIdVer=0, scope="game", lockParamName="userId")
    def getExpiredGun(self, userId, gameId, clientId, gameMode):
        ftlog.debug("getExpiredGun", userId, gameId, clientId, gameMode)
        gun_system.sendExpiredGunMsg(userId, gameMode)

    @markCmdActionMethod(cmd="user", action="chg_gun", clientIdVer=0, scope="game", lockParamName="userId")
    def doChgGun(self, gameId, clientId, userId, gunId, gameMode):
        ftlog.debug("doChgGun", gameId, userId, gunId, gameMode)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("fish_table_call")
            mo.setParam("action", "chg_gun")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("userId", userId)
            mo.setParam("gunId", gunId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("gameMode", gameMode)
            router.sendTableServer(mo, roomId)
        else:
            userGunIds = gun_system.getGunIds(userId, gameMode)
            mo = MsgPack()
            mo.setCmd("chg_gun")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("userId", userId)
            mo.setResult("gameMode", gameMode)
            if gunId not in userGunIds:
                mo.setResult("reason", 1)
            else:
                gunSkinIdKey = GameData.gunSkinId if gameMode == config.CLASSIC_MODE else GameData.gunSkinId_m
                gamedata.setGameAttr(userId, FISH_GAMEID, gunSkinIdKey, gunId)
                value = gun_system.getGunData(userId, gunId, mode=gameMode)
                mo.setResult("gunId", gunId)
                mo.setResult("skinId", value[-1])
                mo.setResult("reason", 0)
                gun_system.sendGunListMsg(userId, gameMode)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="gun_change_skin", clientIdVer=0, scope="game", lockParamName="userId")
    def changeGunSkin(self, userId, gameId, clientId, gunId, skinId, gameMode):
        ftlog.debug("changeGunSkin", userId, gameId, clientId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("fish_table_call")
            mo.setParam("action", "gun_change_skin")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("gunId", gunId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("skinId", skinId)
            mo.setParam("gameMode", gameMode)
            router.sendTableServer(mo, roomId)
        else:
            gun_system.changeGunSkin(userId, gunId, skinId, gameMode)

    @markCmdActionMethod(cmd="user", action="gun_compose_skin", clientIdVer=0, scope="game", lockParamName="userId")
    def composeGunSkin(self, userId, gameId, clientId, gunId, skinId, gameMode):
        ftlog.debug("composeGunSkin", userId, gameId, clientId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("fish_table_call")
            mo.setParam("action", "gun_compose_skin")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("gunId", gunId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("skinId", skinId)
            mo.setParam("gameMode", gameMode)
            router.sendTableServer(mo, roomId)
        else:
            gun_system.composeGunSkin(userId, gunId, skinId, gameMode)

    @markCmdActionMethod(cmd="user", action="userGuideStep", clientIdVer=0, scope="game", lockParamName="userId")
    def setNewUserGuideStep(self, gameId, userId, clientId, step):
        ftlog.debug("setNewUserGuideStep", userId, gameId, step)
        mo = MsgPack()
        mo.setCmd("userGuideStep")
        code = 0
        userGuideStep = util.addGuideStep(userId, step, clientId)
        mo.setResult("gameId", gameId)
        mo.setResult("step", step)
        mo.setResult("finishedStep", userGuideStep)
        mo.setResult("code", code)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="uploadVersion", clientIdVer=0, scope="game", lockParamName="userId")
    def doUploadVersion(self, gameId, userId, clientId, clientVersion, platformOS, gameResolution):
        ftlog.debug("doUploadVersion", gameId, userId, clientVersion, platformOS, gameResolution)
        gamedata.setGameAttrs(userId, FISH_GAMEID,
                              [GameData.clientVersion, GameData.platformOS, GameData.gameResolution],
                              [clientVersion, platformOS, json.dumps(gameResolution)])
        from newfish.entity import update_version_rewards
        update_version_rewards.sendUpdateRewards(userId, clientId)

    @markCmdActionMethod(cmd="user", action="fishCheckin", clientIdVer=0, scope="game", lockParamName="userId")
    def getFishCheckin(self, gameId, userId, continueWindow):
        ftlog.debug("getFishCheckin", gameId, userId, continueWindow)
        checkin.sendFishCheckinInfo(userId, continueWindow)

    @markCmdActionMethod(cmd="user", action="fishCheckinReward", clientIdVer=0, scope="game", lockParamName="userId")
    def getFishCheckinReward(self, gameId, userId, day):
        ftlog.debug("fishCheckinReward", gameId, userId, day)
        checkin.sendFishCheckinRewardInfo(userId, day)

    @markCmdActionMethod(cmd="user", action="fishMatchTips", clientIdVer=0, scope="game", lockParamName="userId")
    def getFishMatchTips(self, gameId, userId):
        ftlog.debug("getFishMatchTips", gameId, userId)
        ctrlRoomId, startTime = util.getFishMatchSigninInfo(userId)
        if ctrlRoomId:
            mo = MsgPack()
            mo.setCmd("fishMatchTips")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("userId", userId)
            mo.setResult("roomId", ctrlRoomId)
            mo.setResult("startTime", startTime)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="ping", clientIdVer=0, scope="game", lockParamName="userId")
    def doSendPingInfo(self, gameId, userId, timestamp):
        ftlog.debug("doSendPingInfo", gameId, userId, timestamp)
        mo = MsgPack()
        mo.setCmd("ping")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("timestamp", timestamp)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="fishStarGameInfo", clientIdVer=0, scope="game", lockParamName="userId")
    def getStarfishBonusInfo(self, gameId, userId):
        """海星抽奖信息获取"""
        ftlog.debug("getStarfishBonusInfo", gameId, userId)
        starfish_bonus.doGetBonusInfo(userId)

    @markCmdActionMethod(cmd="user", action="fishStarGameResult", clientIdVer=0, scope="game", lockParamName="userId")
    def getStarfishBonusResult(self, userId, gameId, clientId, count):
        """海星抽奖抽取结果获取"""
        ftlog.debug("getStarfishBonusResult", gameId, clientId, userId)
        starfish_bonus.doGetBonusResult(userId, count)

    @markCmdActionMethod(cmd="user", action="turntableGameInfo", clientIdVer=0, scope="game", lockParamName="userId")
    def getStarfishTurntableInfo(self, gameId, userId):
        ftlog.debug("turntableGameInfo", gameId, userId)
        starfish_turntable.doGetTurntableInfo(userId)

    @markCmdActionMethod(cmd="user", action="turntableGameResult", clientIdVer=0, scope="game", lockParamName="userId")
    def getStarfishTurntableResult(self, userId, gameId, clientId, count, itemId):
        ftlog.debug("turntableGameResult", gameId, clientId, userId, count, itemId)
        starfish_turntable.doGetTurntableResult(userId, itemId, count)

    @markCmdActionMethod(cmd="user", action="slotMachineTurntableInfo", clientIdVer=0, scope="game", lockParamName="userId")
    def getSlotMachineTurntableInfo(self, gameId, userId, actType):
        ftlog.debug("slotMachineTurntableGameInfo", gameId, userId, actType)
        slot_machine_activity.doGetSlotTurntableInfo(userId, actType)

    @markCmdActionMethod(cmd="user", action="slotMachineTurntableResult", clientIdVer=0, scope="game", lockParamName="userId")
    def getSlotTurntableResult(self, userId, gameId, clientId, count, drawMode, actType):
        ftlog.debug("slotTurntableGameResult", gameId, clientId, userId, count, drawMode, actType)
        slot_machine_activity.doGetSlotTurntableResult(userId, count, drawMode, actType)

    @markCmdActionMethod(cmd="user", action="honor_list", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetHonorList(self, gameId, userId):
        ftlog.debug("doGetHonorList", gameId, userId)
        mo = MsgPack()
        mo.setCmd("honor_list")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("honors", honor_system.getHonorList(userId))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="user", action="honor_replace", clientIdVer=0, scope="game", lockParamName="userId")
    def doReplaceHonor(self, gameId, userId, clientId, honorId):
        ftlog.debug("doReplaceHonor", gameId, userId, honorId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "honor_replace")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("honorId", honorId)
            router.sendTableServer(mo, roomId)
        else:
            honor_system.replaceHonor(userId, honorId)

    @markCmdActionMethod(cmd="user", action="ft_create", clientIdVer=0, lockParamName="", scope="game")
    def doFriendFTCreate(self, userId, gameId, clientId, fee):
        ftlog.debug("doFriendFTCreate->", userId, gameId, clientId, fee)
        msg = MsgPack()
        msg.setCmd("ft_create")
        msg.setResult("gameId", gameId)
        msg.setResult("userId", userId)
        try:
            code = fight_room.createFT(userId, fee)
            msg.setResult("code", code)
            router.sendToUser(msg, userId)
        except TYBizException, e:
            msg.setResult("code", e.errorCode)
            msg.setResult("info", e.message)
            router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd="user", action="ft_enter", clientIdVer=0, lockParamName="", scope="game")
    def doFriendFTEnter(self, userId, gameId, clientId, ftId):
        ftlog.debug("doFriendFTEnter->", userId, gameId, clientId, ftId)
        from newfish.servers.room.rpc import room_remote
        msg = MsgPack()
        msg.setCmd("ft_enter")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("ftId", ftId)
        lang = util.getLanguage(userId, clientId)
        try:
            roomId = fight_room.roomIdForFTId(ftId)
            if roomId:
                code = room_remote.enterFT(userId, roomId, ftId)
                if isinstance(code, dict):
                    raise TYBizException(code["errorCode"], code["message"])
                elif isinstance(code, Exception):
                    ftlog.error("doFriendFTEnter", code, userId)
                    # raise TYBizException(1, u"您输入的房间号不存在，请重新输入。")
                    raise TYBizException(1, config.getMultiLangTextConf("ID_INPUT_ROOMID_ERROR_INFO", lang=lang))
                msg.setResult("code", code)
                router.sendToUser(msg, userId)
            else:
                raise TYBizException(1, config.getMultiLangTextConf("ID_INPUT_ROOMID_ERROR_INFO", lang=lang))
        except TYBizException, e:
            ftlog.warn("doFriendFTEnter Exception",
                       "userId=", userId,
                       "ftId=", ftId,
                       "errorCode=", e.errorCode,
                       "info=", e.message)
            msg.setResult("code", e.errorCode)
            msg.setResult("info", e.message)
            router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd="user", action="fish_share", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetShareReward(self, userId, gameId, clientId, actionType, pointId):
        ftlog.debug("fish_share", gameId, userId, actionType)
        user_system.sendShareReward(userId, actionType, pointId, clientId)

    @markCmdActionMethod(cmd="user", action="record_room_type", clientIdVer=0, scope="game", lockParamName="userId")
    def doRecordRoomType(self, userId, gameId, clientId, typeName):
        ftlog.debug("doRecordRoomType", gameId, userId, typeName)
        msg = MsgPack()
        msg.setCmd("record_room_type")
        msg.setResult("gameId", gameId)
        msg.setResult("userId", userId)
        msg.setResult("typeName", user_system.recordRoomType(userId, typeName))
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd="user", action="fish_share_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetShareInfo(self, userId, gameId, clientId, typeId, extends):
        ftlog.debug("doGetShareInfo", gameId, userId, typeId, extends)
        share_system.sendShareInfo(userId, typeId, extends)

    @markCmdActionMethod(cmd="user", action="fish_share_finish", clientIdVer=0, scope="game", lockParamName="userId")
    def doFinishShare(self, userId, gameId, clientId, shareId, groupId):
        ftlog.debug("doFinishShare", gameId, userId, shareId, groupId)
        share_system.finishShare(userId, shareId)
        user_system.addShareGroupId(userId, groupId)

    @markCmdActionMethod(cmd="user", action="fish_share_click", clientIdVer=0, scope="game", lockParamName="userId")
    def doClickShare(self, userId, gameId, clientId, shareId, shareUserId):
        ftlog.debug("doClickShare", gameId, userId, shareId, shareUserId)
        if userId != shareUserId:
            share_system.clickShare(userId, shareId, shareUserId)
            user_system.updateInvitedState(userId, shareUserId)

    @markCmdActionMethod(cmd="user", action="fish_share_receive", clientIdVer=0, scope="game", lockParamName="userId")
    def doReceiveShareRewards(self, userId, gameId, clientId, shareId):
        ftlog.debug("doReceiveShareRewards", gameId, userId, shareId)
        share_system.receiveShareRewards(userId, shareId)

    @markCmdActionMethod(cmd="user", action="fish_share_recycle", clientIdVer=0, scope="game", lockParamName="userId")
    def doRecycleShare(self, userId, gameId, clientId, shareId):
        ftlog.debug("doRecycleShare", gameId, userId, shareId)
        share_system.recycleShare(userId, shareId)

    @markCmdActionMethod(cmd="user", action="fish_vip_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishVip(self, userId, gameId, clientId):
        """发送VIP特权信息"""
        ftlog.debug("doGetFishVip", gameId, userId)
        vip_system.sendFishVipInfo(userId)
        vip_system.sendVipCirculateInfo(userId)

    @markCmdActionMethod(cmd="user", action="buy_fish_vip_gift", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyFishVipGift(self, userId, gameId, clientId, level, buyType, rebateItemId):
        """购买特定VIP等级的礼包"""
        ftlog.debug("doBuyFishVipGift", gameId, userId, level, buyType, rebateItemId)
        vip_system.buyFishVipGift(userId, level, clientId, buyType, rebateItemId)

    @markCmdActionMethod(cmd="user", action="modify_vip_show", clientIdVer=0, scope="game", lockParamName="userId")
    def doModifyVipShow(self, userId, gameId, modify):
        ftlog.debug("doModifyVipShow", gameId, userId, modify)
        vipShow, code = util.modifyVipShow(userId, modify)
        msg = MsgPack()
        msg.setCmd("modify_vip_show")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("vipShow", vipShow)
        msg.setResult("code", code)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd="user", action="limit_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLimitInfo(self, userId):
        msg = MsgPack()
        msg.setCmd("limit_info")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        # 全局地区限制（0:不限制区域 1:限制区域）
        msg.setResult("locationLimit", 1 if util.isLocationLimit(userId) else 0)
        # 提审版本号列表
        msg.setResult("version", util.getReviewVersionList(userId))
        # 全局分享限制（0:正常分享 1:微信限制下跳转到微信即算分享）
        msg.setResult("shareLimit", config.getPublic("shareLimit", 0))
        msg.setResult("needCheckWxMiniProg", config.getCommonValueByKey("needCheckWxMiniProg", 1))
        router.sendToUser(msg, userId)
        ftlog.debug("doGetLimitInfo", userId, msg)

    @markCmdActionMethod(cmd="user", action="getSurpriseGift", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetSurpriseGift(self, userId):
        ftlog.debug("doGetSurpriseGift", userId)
        surpriseGift = weakdata.getDayFishData(userId, GameData.surpriseGift, 0)
        if not surpriseGift:
            rewards = config.getCommonValueByKey("surpriseGiftRewards", [])
            msg = MsgPack()
            for reward in rewards:
                kindId = reward["name"]
                if util.isChestRewardId(kindId):
                    msg.setResult("chestId", kindId)
                    rewards = chest_system.getChestRewards(userId, kindId)
                    chest_system.deliveryChestRewards(userId, kindId, rewards, "BI_NFISH_ACTIVITY_REWARDS")
                else:
                    util.addRewards(userId, [reward], "BI_NFISH_ACTIVITY_REWARDS")
            msg.setCmd("getSurpriseGift")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", userId)
            msg.setResult("rewards", rewards)
            router.sendToUser(msg, userId)
            weakdata.setDayFishData(userId, GameData.surpriseGift, 1)

    @markCmdActionMethod(cmd="user", action="followAccount", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFollowAccountInfo(self, userId):
        ftlog.debug("doGetFollowAccountInfo", userId)
        state = 0
        followAccount = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.followAccount)
        if followAccount:
            state = 1
        else:
            if user_system.isFollowAccount(userId):
                rewards = config.getCommonValueByKey("wechatFollowAccountRewards")
                # message = u"感谢您关注“途游休闲捕鱼”公众号，现给您送上关注礼包一份~祝您游戏愉快！"
                message = config.getMultiLangTextConf("ID_FOLLOW_ACCOUNT_MESSAGE", lang=util.getLanguage(userId))
                mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, rewards, message)
                state = 1
        msg = MsgPack()
        msg.setCmd("followAccount")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("state", state)
        wechatCheckin = weakdata.getDayFishData(userId, WeakData.wechatCheckin, 0)
        msg.setResult("ischeckin", wechatCheckin)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd="user", action="gun_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doSendGunInfo(self, userId, gameMode):
        ftlog.debug("doSendGunInfo", userId, gameMode)
        gun_system.sendGunInfoMsg(userId, gameMode)

    @markCmdActionMethod(cmd="user", action="gun_up", clientIdVer=0, scope="game", lockParamName="userId")
    def doGunUpgrade(self, userId, clientId, protect, gameMode):
        ftlog.debug("doGunUpgrade", userId, clientId, protect, gameMode)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "gun_up")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("protect", protect)
            mo.setParam("gameMode", gameMode)
            router.sendTableServer(mo, roomId)
        else:
            gun_system.upgradeGun(userId, protect, gameMode)

    @markCmdActionMethod(cmd="user", action="id_card_identify_reward", clientIdVer=0, scope="game", lockParamName="userId")
    def doIdentifyIdCardReward(self, userId, clientId):
        user_system.sendIdentifyReward(userId)

    @markCmdActionMethod(cmd="user", action="bind_xl_user", clientIdVer=0, scope="game", lockParamName="userId")
    def uploadXLUserInfo(self, gameId, userId, clientId, accessToken, openId):
        ftlog.debug("uploadXLUserInfo", gameId, userId, accessToken, openId)
        from newfish.entity.fishactivity import xl_level_up_activity
        xl_level_up_activity.bindXLUserGid(userId, clientId, accessToken, openId)

    @markCmdActionMethod(cmd="user", action="money_tree_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doMoneyTreeInfo(self, gameId, userId, clientId):
        ftlog.debug("doMoneyTreeInfo", gameId, userId, clientId)
        from newfish.entity.fishactivity import money_tree_activity
        money_tree_activity.sendMoneyTreeInfo(userId, clientId)

    @markCmdActionMethod(cmd="user", action="money_tree_draw", clientIdVer=0, scope="game", lockParamName="userId")
    def doMoneyTreeDraw(self, gameId, userId, clientId, drawMode, count):
        ftlog.debug("doMoneyTreeDraw", gameId, userId, clientId)
        from newfish.entity.fishactivity import money_tree_activity
        money_tree_activity.sendMoneyTreeDraw(userId, clientId, drawMode, count)

    @markCmdActionMethod(cmd="user", action="cannedFish_list", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetWordFactoryList(self, gameId, userId, clientId, act):
        ftlog.debug("doGetWordFactoryList", gameId, userId, clientId, act)
        from newfish.entity.fishactivity import canned_fish_factory
        canned_fish_factory.doGetwordFishList(userId, act)

    @markCmdActionMethod(cmd="user", action="seek_cannedFish", clientIdVer=0, scope="game", lockParamName="userId")
    def doSeekCannedFish(self, gameId, userId, clientId, cannedNumber):
        ftlog.debug("doSeekCannedFish", gameId, userId, clientId, cannedNumber)
        from newfish.entity.fishactivity import canned_fish_factory
        canned_fish_factory.doGetSeekCannedFish(userId, cannedNumber)

    @markCmdActionMethod(cmd="user", action="guess_cannedFish", clientIdVer=0, scope="game", lockParamName="userId")
    def guessCannedFish(self, gameId, userId, clientId, act, cannedNumber, productDate, batchNumber):
        ftlog.debug("guessCannedFish", gameId, userId, clientId, cannedNumber)
        from newfish.entity.fishactivity import canned_fish_factory
        canned_fish_factory.doGetGuessCannedFish(userId, act, cannedNumber, productDate, batchNumber)

    @markCmdActionMethod(cmd="user", action="make_cannedFish", clientIdVer=0, scope="game", lockParamName="userId")
    def MakeCannedFish(self, gameId, userId, clientId, name, count, desc, batchNumber):
        ftlog.debug("MakeCannedFish", gameId, userId, clientId, name, count, desc, batchNumber)
        from newfish.entity.fishactivity import canned_fish_factory
        canned_fish_factory.doGetMakeCannedFishInfo(userId, name, count, desc, batchNumber)

    @markCmdActionMethod(cmd="user", action="make_cannedFish_propInfo", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetPropInfo(self, gameId, userId, clientId):
        ftlog.debug("doGetPropInfo", gameId, userId, clientId)
        from newfish.entity.fishactivity import canned_fish_factory
        canned_fish_factory.doGetItemList(userId)

    @markCmdActionMethod(cmd="user", action="super_egg_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetSuperEggInfo(self, gameId, userId, clientId):
        ftlog.debug("doGetSuperEggInfo", gameId, userId, clientId)
        super_egg_activity.getSuperEggInfo(userId, clientId)

    @markCmdActionMethod(cmd="user", action="super_egg_buy", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuySuperEgg(self, gameId, userId, clientId, productId, buyType, rebateItemId):
        ftlog.debug("doBuySuperEgg", gameId, userId, clientId, productId, buyType, rebateItemId)
        super_egg_activity.doBuySuperEgg(userId, clientId, buyType, productId, rebateItemId)

    @markCmdActionMethod(cmd="user", action="supply_box_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetSupplyBoxInfo(self, gameId, userId, clientId):
        ftlog.debug("doGetSupplyBoxInfo", gameId, userId, clientId)
        from newfish.entity.fishactivity import supply_box_activity
        supply_box_activity.sendSupplyBoxInfo(userId)

    @markCmdActionMethod(cmd="user", action="supply_box_preview", clientIdVer=0, scope="game", lockParamName="userId")
    def doPreviewSupplyBox(self, gameId, userId, clientId):
        ftlog.debug("doPreviewSupplyBox", gameId, userId, clientId)
        from newfish.entity.fishactivity import supply_box_activity
        supply_box_activity.sendSupplyBoxPreview(userId)

    @markCmdActionMethod(cmd="user", action="supply_box_reward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetSupplyBoxReward(self, gameId, userId, clientId, boxId, actType):
        ftlog.debug("doGetSupplyBoxReward", gameId, userId, clientId, boxId, actType)
        from newfish.entity.fishactivity import supply_box_activity
        supply_box_activity.sendSupplyBoxReward(userId, boxId, actType)

    @markCmdActionMethod(cmd="user", action="multiple_mode_vote", clientIdVer=0, scope="game", lockParamName="userId")
    def doVote(self, gameId, userId, clientId, voteResult):
        ftlog.debug("doVote", gameId, userId, clientId, voteResult)
        from newfish.entity.fishactivity import vote_activity
        vote_activity.doGetVoteResult(userId, voteResult)

    @markCmdActionMethod(cmd="user", action="comp_act_tip", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetCompActTip(self, gameId, userId, clientId):
        ftlog.debug("doGetCompActTip", gameId, userId, clientId)
        competition_activity.getCompActTip(userId)

    @markCmdActionMethod(cmd="user", action="comp_act_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetCompActInfo(self, gameId, userId, clientId):
        ftlog.debug("doGetCompActInfo", gameId, userId, clientId)
        competition_activity.getCompActInfo(userId, clientId)

    @markCmdActionMethod(cmd="user", action="comp_act_store", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetCompActItems(self, gameId, userId, clientId):
        ftlog.debug("doGetCompActItems", gameId, userId, clientId)
        competition_activity.getCompActItems(userId, clientId)

    @markCmdActionMethod(cmd="user", action="comp_act_led", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetCompActLed(self, gameId, userId, clientId):
        ftlog.debug("doGetCompActLed", gameId, userId, clientId)
        competition_activity.getCompActLed(userId)

    @markCmdActionMethod(cmd="user", action="comp_act_buy", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyCompActItem(self, gameId, userId, clientId, productId, buyType, rebateItemId):
        ftlog.debug("doBuyCompActItem", gameId, userId, clientId, productId, buyType, rebateItemId)
        competition_activity.doBuyCompActItem(userId, clientId, buyType, productId, rebateItemId)

    @markCmdActionMethod(cmd="user", action="rename_nickname", clientIdVer=0, scope="game", lockParamName="userId")
    def doRenameNickname(self, gameId, userId, clientId, nickname):
        ftlog.debug("doRenameNickname", gameId, userId, clientId, nickname)
        user_system.renameNickname(userId, clientId, nickname)

    @markCmdActionMethod(cmd="user", action="newbie_7_gift_query", clientIdVer=0, scope="game", lockParamName="userId")
    def doQueryNewbie7DaysGift(self, gameId, userId, clientId):
        ftlog.debug("doQueryNewbie7DaysGift", gameId, userId, clientId)
        newbie_7days_gift.queryNewbie7DayGift(userId, clientId)

    @markCmdActionMethod(cmd="user", action="newbie_7_gift_take", clientIdVer=0, scope="game", lockParamName="userId")
    def doTakeNewbie7DaysGift(self, gameId, userId, clientId, idx):
        ftlog.debug("doTakeNewbie7DaysGift", gameId, userId, clientId, idx)
        newbie_7days_gift.takeNewbie7DaysGift(userId, clientId, idx)

    @markCmdActionMethod(cmd="user", action="pass_card_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetPassCardInfo(self, gameId, userId, clientId, acId):
        ftlog.debug("doGetPassCardInfo", gameId, userId, clientId, acId)
        from newfish.entity.fishactivity import pass_card_activity
        pass_card_activity.sendPassCardInfo(userId, acId, clientId)

    @markCmdActionMethod(cmd="user", action="pass_card_reward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetPassCardReward(self, gameId, userId, clientId, taskId, acId):
        ftlog.debug("doGetPassCardReward", gameId, userId, clientId, taskId, acId)
        from newfish.entity.fishactivity import pass_card_activity
        pass_card_activity.sendPassCardReward(userId, acId, taskId)

    @markCmdActionMethod(cmd="user", action="pass_card_buy", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyUnlockProduct(self, gameId, userId, clientId, productId, buyType, rebateItemId):
        ftlog.debug("doBuyPassCard", gameId, userId, clientId, productId, buyType, rebateItemId)
        from newfish.entity.fishactivity import pass_card_activity
        pass_card_activity.doBuyUnlockProduct(userId, clientId, buyType, productId, rebateItemId)

    @markCmdActionMethod(cmd="user", action="product_buy", clientIdVer=0, scope="game", lockParamName="userId")
    def doUserBuyProduct(self, gameId, userId, clientId, productId, buyType, rebateItemId):
        ftlog.debug("doUserBuyProduct", gameId, userId, clientId, productId, buyType, rebateItemId)
        from newfish.entity.fishactivity import fish_activity_system
        fish_activity_system.doUserBuyProduct(userId, productId, clientId, buyType, rebateItemId)

    @markCmdActionMethod(cmd="user", action="returner_mission", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetReturnerMission(self, gameId, userId, clientId):
        ftlog.debug("doGetReturnerMission", gameId, userId, clientId)
        returner_mission.getReturnerMission(userId, clientId)

    @markCmdActionMethod(cmd="user", action="returner_reward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetReturnerReward(self, gameId, userId, clientId, taskId):
        ftlog.debug("doGetReturnerReward", gameId, userId, clientId, taskId)
        returner_mission.getReturnerReward(userId, clientId, taskId)

    @markCmdActionMethod(cmd="user", action="send_sms_code", clientIdVer=0, scope="game", lockParamName="userId")
    def doSendSmsCode(self, gameId, userId, clientId, mobile):
        ftlog.debug("doSendSmsCode", gameId, userId, clientId, mobile)
        code = 0
        if not util.verifyPhoneNumber(mobile):
            code = 1
        elif not util.sendSmsCode(userId, mobile):
            code = 2
        msg = MsgPack()
        msg.setCmd("send_sms_code")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("code", code)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd="user", action="verify_sms_code", clientIdVer=0, scope="game", lockParamName="userId")
    def doVerifySmsCode(self, gameId, userId, clientId, mobile, vcode):
        ftlog.debug("doVerifySmsCode", gameId, userId, clientId, mobile, vcode)
        code = 0
        result = util.verifySmsCode(userId, mobile, vcode)
        if result is False:
            code = 1
        elif result is None:
            code = 2
        if code == 0:
            from newfish.entity.fishactivity import bind_mobile_phone_activity
            bind_mobile_phone_activity.completeActivity(userId, mobile)
        msg = MsgPack()
        msg.setCmd("verify_sms_code")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("code", code)
        router.sendToUser(msg, userId)

    @markCmdActionMethod(cmd="user", action="lucky_tree_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLuckyTreeInfo(self, gameId, userId, clientId):
        ftlog.debug("doGetLuckyTreeInfo", gameId, userId, clientId)
        free_coin_lucky_tree.sendLuckyTreeInfo(userId, clientId)

    @markCmdActionMethod(cmd="user", action="lucky_tree_reward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLuckyTreeReward(self, gameId, userId, clientId, idx, actType):
        ftlog.debug("doGetLuckyTreeReward", gameId, userId, clientId, idx, actType)
        free_coin_lucky_tree.sendLuckyTreeReward(userId, actType, idx)

    @markCmdActionMethod(cmd="user", action="lucky_tree_accelerate", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLuckyTreeAccelerate(self, gameId, userId, clientId):
        ftlog.debug("doGetLuckyTreeAccelerate", gameId, userId, clientId)
        free_coin_lucky_tree.sendLuckyTreeAccelerate(userId)

    @markCmdActionMethod(cmd="user", action="levelGiftData", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLevelGiftData(self, gameId, userId, clientId):
        """
        获取等级礼包数据
        """
        ftlog.debug("doGetLevelGiftData", gameId, userId, clientId)
        level_gift.doSendLevelGift(userId, clientId)

    @markCmdActionMethod(cmd="user", action="buyLevelGift", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyLevelGift(self, gameId, userId, clientId, productId, buyType, rebateItemId=0):
        """
        购买等级礼包
        """
        ftlog.debug("buyLevelGift", gameId, userId, clientId, productId, buyType, rebateItemId)
        level_gift.doBuyLevelGift(userId, clientId, buyType, productId, rebateItemId)

    @markCmdActionMethod(cmd="user", action="sendUserNewLed", clientIdVer=0, scope="game", lockParamName="userId")
    def sendUserNewLed(self, gameId, userId, clientId):
        """
        新手LED
        """
        ftlog.debug("sendUserNewLed", gameId, userId, clientId)
        led.sendUserNewLed(userId, clientId)
