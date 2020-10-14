# -*- coding=utf-8 -*-
"""
Created by hhx on 18/03/30.
"""

import time
import json
import random
import math
import datetime
import re
from distutils.version import StrictVersion

from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.util import keywords, strutil
from poker.protocol import router
from poker.entity.dao import gamedata, userdata, daobase, sessiondata
from poker.entity.biz import bireport
from poker.entity.configure import gdata, pokerconf
from hall.entity import hallvip, hall_share2, hallitem
from hall.entity.hall_share2 import ParsedClientId
from newfish.entity.config import FISH_GAMEID
from newfish.entity.honor import honor_system
from newfish.entity import config, util, weakdata, module_tip, returner_mission
from newfish.entity.redis_keys import GameData, WeakData, ABTestData
from newfish.servers.util.rpc import user_rpc



# 分享消息
def sendShareReward(userId, actionType, pointId, clientId):
    mo = MsgPack()
    mo.setCmd("fish_share")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("clientId", clientId)
    mo.setResult("userId", userId)
    parseClientId = ParsedClientId.parseClientId(clientId)
    sharePoint, _ = hall_share2.getShareContent(FISH_GAMEID, userId, parseClientId, pointId)
    _, rcf = hall_share2.loadShareStatus(FISH_GAMEID, userId, sharePoint, int(time.time()))
    shareReward = sharePoint.reward.content.getItems()
    code = 1
    mo.setResult("shareCount", rcf)
    rewards = []
    for r in shareReward:
        rewards.append({"itemId": r.assetKindId, "count": r.count})
    mo.setResult("reward", rewards)
    mo.setResult("code", code)
    router.sendToUser(mo, userId)


#  --获取用户信息
def doGetUserInfo(userId, otherUserId, kindId):
    """
    :param kindId: 赠送的道具ID
    """
    userdata.checkUserData(otherUserId)
    name = util.getNickname(otherUserId)
    sex, purl, charm = userdata.getAttrs(otherUserId, ["sex", "purl", "charm"])
    vipLv = util.getVipShowLevel(otherUserId)
    level = util.getUserValidCheckLevel(otherUserId)
    honors = honor_system.getHonorList(otherUserId)
    _, leftReceiveCount = _isCanReceiveFromOther(otherUserId, kindId)
    code = 0
    if name is None or name == "" or not level or level == 0:
        code = 1
    if otherUserId in config.getPublic("banGiftList", []):
        code = 1
    name = str(name) if name else ""
    message = MsgPack()
    message.setCmd("fishUserInfo")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if code == 0:
        userInfos = {
            "userId": otherUserId,
            "name": name,
            "sex": sex,
            "purl": purl,
            "level": level,
            "vipLv": vipLv,
            "charm": charm,
            "honors": honors,
            "leftReceiveCount": leftReceiveCount
        }
        message.setResult("userInfos", userInfos)
    message.setResult("code", code)
    router.sendToUser(message, userId)


def _isCanReceiveFromOther(otherUserId, kindId):
    """
    检查是否可以接收他人赠送招财珠
    """
    from newfish.entity.config import SILVER_BULLET_KINDID, GOLD_BULLET_KINDID
    if kindId in [SILVER_BULLET_KINDID, GOLD_BULLET_KINDID]:
        silverBulletKey = WeakData.vipReceiveCount % SILVER_BULLET_KINDID
        if userdata.checkUserData(otherUserId):
            vipLevel = util.getVipRealLevel(otherUserId)
            dayReceiveCount = weakdata.getDayFishData(otherUserId, silverBulletKey, 0)
            dayLimitCount = config.getVipConf(vipLevel).get(silverBulletKey, 0)
            leftReceiveCount = dayLimitCount - dayReceiveCount
            if leftReceiveCount > 0 and not util.isProtectionLimit(otherUserId):
                if kindId == GOLD_BULLET_KINDID:
                    leftReceiveCount = leftReceiveCount // 5
                return 0, leftReceiveCount  # 可以接受赠送
            else:
                return 1, 0  # 不可以接受赠送
    return 0, 99999


def recordRoomType(userId, typeName):
    """
    记录上次游戏房间类型
    """
    if typeName in [config.FISH_NORMAL, config.FISH_FRIEND]:
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.lastRoomType, typeName)
    return typeName


def updateLoginData(userId):
    """
    更新用户登录数据
    """
    curTime = int(time.time())
    lastLoginTime = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.lastloginTime) or curTime
    returner_mission.refreshReturnerMissionData(userId, lastLoginTime)  # 刷新回归豪礼数据
    lastLoginTime = util.getDayStartTimestamp(lastLoginTime)
    todayStartTime = util.getDayStartTimestamp(curTime)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.lastloginTime, curTime)
    # 过天
    if todayStartTime - lastLoginTime > 24 * 3600:
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.loginDays, 1)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.continuousLogin, 1)
    elif todayStartTime - lastLoginTime == 24 * 3600:  # 正好一天
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.loginDays, 1)
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.continuousLogin, 1)


def reportBILogOnLogin(userId):
    """
    首次登录上报BI数据
    """
    # 上报玩家火炮剩余天数
    timestamp = int(time.time())
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    clientId = util.getClientId(userId)
    for mode in config.GAME_MODES:
        for itemId in config.getAllGunIds(clientId, mode):
            item = userBag.getItemByKindId(itemId)
            if item and not item.isDied(timestamp):
                bireport.reportGameEvent("BI_NFISH_GE_GUN_SKIN", userId, FISH_GAMEID, 0,
                                         0, int(itemId), item.balance(timestamp), mode, 0, [], clientId)


def refreshUserData(userId):
    """
    刷新用户是否存在地区限制
    """
    location = config.getPublic("locationLimit", [])
    requestUrl = "http://iploc.ywdier.com/api/iploc5/search/city"
    postData = {"ip": sessiondata.getClientIp(userId)}
    result = util.doHttpQuery(requestUrl, postData, timeout=3)
    isLocationLimit = 0
    if not result or set(location) & set(result.get("loc", [])):
        isLocationLimit = 1
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.isLocationLimit, isLocationLimit)


def renameNickname(userId, clientId, nickname):
    """
    修改玩家昵称
    """
    lang = util.getLanguage(userId, clientId)
    surplusCount = util.balanceItem(userId, config.RENAME_KINDID)
    try:
        if surplusCount == 0:
            code = 1
            info = config.getMultiLangTextConf("ID_RENAME_CODE_INFO_1", lang=lang) # u"昵称修改失败"
        elif len(nickname) == 0:
            code = 2
            info = config.getMultiLangTextConf("ID_RENAME_CODE_INFO_2", lang=lang) # u"昵称不能为空，请重新输入！"
        elif len(nickname.decode("utf-8").encode("gbk", "ignore")) > 16:
            code = 3
            info = config.getMultiLangTextConf("ID_RENAME_CODE_INFO_3", lang=lang) # u"昵称过长，请重新输入！"
        elif re.search(u"[^\w\u4e00-\u9fff]+", nickname.decode("utf-8")):
            code = 4
            info = config.getMultiLangTextConf("ID_RENAME_CODE_INFO_4", lang=lang) # u"昵称不能含有特殊字符，请重新输入！"
        elif util.isTextCensorLimit(nickname):
            code = 5
            info = config.getMultiLangTextConf("ID_RENAME_CODE_INFO_5", lang=lang) # u"昵称含有违规内容，请重新输入！"
        else:
            _consume = [{"name": config.RENAME_KINDID, "count": 1}]
            util.consumeItems(userId, _consume, "ITEM_USE")
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.nickname, nickname)
            userdata.setAttr(userId, "name", nickname)
            code = 0
            info = config.getMultiLangTextConf("ID_RENAME_CODE_INFO_0", lang=lang) # u"昵称修改成功"
    except:
        ftlog.error()
        code = 1
        info = config.getMultiLangTextConf("ID_RENAME_CODE_INFO_1", lang=lang)  # u"昵称修改失败"
    message = MsgPack()
    message.setCmd("rename_nickname")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("info", info)
    message.setResult("code", code)
    router.sendToUser(message, userId)


def sendThanksLetterReward(userId):
    thanksRewardNum = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.ThanksLetterRewardNum)
    message = MsgPack()
    message.setCmd("thanks_letter_reward")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if thanksRewardNum < config.getCommonValueByKey("thanksLetterRewardNum"):
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.ThanksLetterRewardNum, 1)
        rewards = config.getCommonValueByKey("thanksLetterRewards")
        util.addRewards(userId, rewards, "BI_NFISH_SHARE_REWARDS")
        message.setResult("code", 0)
        message.setResult("rewards", rewards)
    else:
        message.setResult("code", 1)
    router.sendToUser(message, userId)


def addShareGroupId(userId, groupId):
    """
    添加分享到群的群ID
    """
    shareGroupIds = weakdata.getDayFishData(userId, "shareGroupIds", [])
    if ftlog.is_debug():
        ftlog.debug("addShareGroupId", userId, groupId, shareGroupIds)
    if groupId and groupId not in shareGroupIds:
        shareGroupIds.append(groupId)
        weakdata.setDayFishData(userId, WeakData.shareGroupIds, json.dumps(shareGroupIds))
        shareGroupTotalCount = config.getCommonValueByKey("shareGroupTotalCount")
        isReceiveReward = weakdata.getDayFishData(userId, "shareGroupReward", 0)
        if not isReceiveReward and len(shareGroupIds) >= shareGroupTotalCount:
            weakdata.setDayFishData(userId, WeakData.shareGroupReward, 1)
            if not util.isVersionLimit(userId):
                module_tip.addModuleTipEvent(userId, "invite", 0)
        getShareTaskInfo(userId)


def updateInvitedState(userId, shareUserId, isNewUser=False):
    """
    更新邀请状态
    :param userId: 被邀请者
    :param shareUserId: 分享者
    :param isNewUser: 是否为新用户
    """
    isInvited = weakdata.getDayFishData(userId, "isInvited", 0)
    if not isInvited:
        user_rpc.addShareInvitedUserId(shareUserId, userId, isNewUser)
    weakdata.incrDayFishData(userId, "isInvited", 1)


def addShareInvitedUserId(shareUserId, invitedUserId, isNewUser=False):
    """
    添加分享邀请人信息
    :param shareUserId: 分享卡片的分享者
    :param invitedUserId: 点击卡片的被邀请者
    :param isNewUser: 是否为新用户
    """
    inviteCount = weakdata.getDayFishData(shareUserId, "inviteCount", 0)
    if inviteCount < config.getCommonValueByKey("inviteLimitCount", 99999):
        if not isNewUser:
            inviteOldUserCount = weakdata.getDayFishData(shareUserId, "inviteOldUserCount", 0)
            if inviteOldUserCount > config.getCommonValueByKey("inviteLimitOldCount", 99999):
                return
            weakdata.incrDayFishData(shareUserId, "inviteOldUserCount", 1)
        inviteList = gamedata.getGameAttrJson(shareUserId, FISH_GAMEID, GameData.inviteList, [])
        inviteId = gamedata.incrGameAttr(shareUserId, FISH_GAMEID, GameData.inviteId, 1)
        inviteData = {
            "inviteId": inviteId,
            "userId": invitedUserId,
            "inviteTime": int(time.time()),
            "isNewUser": isNewUser,
            "isAppUser": 1 if util.isAppClient(invitedUserId) else 0
        }
        inviteList.append(inviteData)
        gamedata.setGameAttr(shareUserId, FISH_GAMEID, GameData.inviteList, json.dumps(inviteList))
        weakdata.incrDayFishData(shareUserId, "inviteCount", 1)
        module_tip.addModuleTipEvent(shareUserId, "invite", inviteId)
        getShareTaskInfo(shareUserId)
        from newfish.game import TGFish
        from newfish.entity.event import InvitedFinishEvent
        event = InvitedFinishEvent(shareUserId, FISH_GAMEID)
        TGFish.getEventBus().publishEvent(event)


def refreshInviteData(userId):
    """
    刷新邀请数据
    """
    inviteList = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.inviteList, [])
    for _, inviteData in enumerate(inviteList[:]):
        if inviteData.get("receiveTime"):
            if util.getDayStartTimestamp(inviteData["receiveTime"]) != util.getDayStartTimestamp(int(time.time())):
                inviteList.remove(inviteData)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.inviteList, json.dumps(inviteList))
    return inviteList


def getShareTaskInfo(userId):
    """
    获取分享有礼信息
    """
    shareGroupIds = weakdata.getDayFishData(userId, "shareGroupIds", [])
    shareGroupTotalCount = config.getCommonValueByKey("shareGroupTotalCount")
    shareGroupCurrentCount = min(len(shareGroupIds), shareGroupTotalCount)
    groupTask = {
        "taskId": 0,
        "progress": [shareGroupCurrentCount, shareGroupTotalCount], # 分享群数/总数
        "rewards": config.getCommonValueByKey("shareGroupRewards"),
        "state": weakdata.getDayFishData(userId, "shareGroupReward", 0)
    }
    if groupTask["state"] == 0 or util.isVersionLimit(userId):
        module_tip.cancelModuleTipEvent(userId, "invite", 0)
    inviteTasks = []
    inviteList = refreshInviteData(userId)
    for _, inviteData in enumerate(inviteList):
        name = util.getNickname(inviteData["userId"])
        avatar = userdata.getAttr(inviteData["userId"], "purl")
        if inviteData.get("isAppUser", 0) == 1:
            continue
        if inviteData.get("isNewUser"):
            rewards = config.getCommonValueByKey("newUserInviteFriendRewards")
        else:
            rewards = config.getCommonValueByKey("inviteFriendRewards")
        task = {
            "taskId": inviteData["inviteId"],
            "name": name,
            "avatar": avatar,
            "vip": hallvip.userVipSystem.getUserVip(userId).vipLevel.level,
            "state": 2 if inviteData.get("receiveTime") else 1,
            "rewards": rewards
        }
        inviteTasks.append(task)
    inviteCount = weakdata.getDayFishData(userId, "inviteCount", 0)
    inviteTotalCount = config.getCommonValueByKey("inviteLimitCount", 99999)
    inviteCount = min(inviteCount, inviteTotalCount)
    friendTask = {
        "progress": [inviteCount, inviteTotalCount],
        "rewards": config.getCommonValueByKey("inviteFriendRewards"),
        "newUserRewards": config.getCommonValueByKey("newUserInviteFriendRewards"),
        "tasks": inviteTasks
    }
    message = MsgPack()
    message.setCmd("share_task_info")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    if not util.isVersionLimit(userId):
        message.setResult("groupTask", groupTask)
    message.setResult("friendTask", friendTask)
    router.sendToUser(message, userId)


def getShareTaskRewards(userId, taskId):
    """
    领取分享好礼奖励
    """
    code = 1
    chestId = 0
    rewards = []
    eventId = "BI_NFISH_INVITE_TASK_REWARDS"
    if taskId == 0:
        isReceiveReward = weakdata.getDayFishData(userId, "shareGroupReward", 0)
        shareGroupIds = weakdata.getDayFishData(userId, "shareGroupIds", [])
        shareGroupTotalCount = config.getCommonValueByKey("shareGroupTotalCount")
        if isReceiveReward == 1 and len(shareGroupIds) >= shareGroupTotalCount:
            rewards = config.getCommonValueByKey("shareGroupRewards")
            from newfish.entity.chest import chest_system
            for reward in rewards:
                kindId = reward["name"]
                if util.isChestRewardId(kindId):
                    chestId = kindId
                    rewards = chest_system.getChestRewards(userId, kindId)
                    code = chest_system.deliveryChestRewards(userId, kindId, rewards, eventId)
                else:
                    code = util.addRewards(userId, [reward], eventId)
            weakdata.setDayFishData(userId, WeakData.shareGroupReward, 2)
    else:
        inviteList = refreshInviteData(userId)
        for _, inviteData in enumerate(inviteList):
            if inviteData["inviteId"] == taskId and not inviteData.get("receiveTime"):
                if inviteData.get("isAppUser", 0) == 1:
                    continue
                if inviteData.get("isNewUser"):
                    rewards = config.getCommonValueByKey("newUserInviteFriendRewards")
                else:
                    rewards = config.getCommonValueByKey("inviteFriendRewards")
                code = util.addRewards(userId, rewards, eventId)
                inviteData["receiveTime"] = int(time.time())
                break
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.inviteList, json.dumps(inviteList))
    message = MsgPack()
    message.setCmd("share_task_receive")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    message.setResult("taskId", taskId)
    message.setResult("code", code)
    if code == 0:
        module_tip.cancelModuleTipEvent(userId, "invite", taskId)
        message.setResult("chestId", chestId)
        message.setResult("rewards", rewards)
    router.sendToUser(message, userId)


def isFollowAccount(userId):
    """
    是否关注微信公众号
    """
    followAccount = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.followAccount)
    if followAccount:
        return True
    requestUrl = gdata.httpGame() + "/open/v4/user/act/wx/checkfollowmp"
    postData = {
        "userId": userId,
        "wxgameappid": config.WX_APPID,
        "wxmpappid": config.WX_MP_APPID
    }
    result = util.doHttpQuery(requestUrl, postData)
    if result and result.get("result", {}).get("follow") is True:
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.followAccount, 1)
        return True
    return False


def isVerfied(userId):
    """
    是否已实名认证
    """
    # vertified = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.vertified)
    # if vertified:
    #     return True
    ts = int(time.time())
    requestUrl = "https://fcmapi.tuyoo.com" + "/anti-addiction/v1/user/query/info.json"
    # 键值对升序排列
    signStr = "access_id=15e347e88f55a87d&secret_type=forever&sign_type=sha256&ts=%d&user_id=%d:dgI64ZhCoE6fjld2Ph5bhzukLlFpuvHB" % (
    ts, userId)
    import hashlib
    sign = str(hashlib.sha256(signStr).hexdigest().lower())
    postData = {"access_id": "15e347e88f55a87d",
                "sign_type": "sha256",
                "secret_type": "forever",
                "ts": ts,
                "user_id": userId,
                "sign": sign}
    try:
        result = util.doHttpQuery(requestUrl, postData)
        if ftlog.is_debug():
            ftlog.debug("query verfied, postData =", postData, "result =", result)
        if result and result.get("code") == 0 and result.get("result", {}).get("verified", 0):
            # gamedata.setGameAttr(userId, FISH_GAMEID, GameData.vertified, 1)
            return True
    except:
        ftlog.error("query verfied error !", userId)
    return False


def sendCommonConfig(userId):
    clientId = util.getClientId(userId)
    mo = MsgPack()
    mo.setCmd("fishCommonConfig")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("clientId", clientId)
    mo.setResult("userId", userId)
    # sendKeys = ["weChatPublicNum", "weChatTelephone", "weChatQQGroup"]
    sendKeys = ["publicNum", "telephone"]
    sendHash = {}
    for key_ in sendKeys:
        sendHash[key_] = config.getCommonValueByKey(key_, 0)

    # led版本限制
    ledIds = config.getIgnoreConf("ledIds", clientId)
    if ledIds is None:
        ledIds = []
    groups = config.getIgnoreConf("groups", clientId)
    if groups is None:
        groups = []
    ignoreClient = config.isClientIgnoredConf("clientIds", clientId, clientId)
    sendHash["ignoreConf"] = {"ledIds": ledIds, "groups": groups, "pureClient": 1 if ignoreClient else 0}
    # 身份证验证版本限制
    cardIdInfo = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.idCardInfo)
    cardIdIdentify = config.getCommonValueByKey("cardIdIdentify")
    sendHash["cardIdIdentify"] = 1 if clientId in cardIdIdentify and not cardIdInfo else 0
    # 防沉迷配置.
    antiAddictionConf = config.getCommonValueByKey("antiAddiction", {})
    enableAntiAddiction = antiAddictionConf.get("defaultEnable", 0)
    if clientId in antiAddictionConf.get("exceptionClientId", []):
        enableAntiAddiction = 1 - enableAntiAddiction
    sendHash["enableAntiAddiction"] = enableAntiAddiction
    # 防沉迷时间限制.
    sendHash["enableAAPlay"] = antiAddictionConf.get("enablePlay", 0) if enableAntiAddiction else 1
    # 防沉迷充值限制.
    sendHash["enableAABuy"] = antiAddictionConf.get("enableBuy", 0) if enableAntiAddiction else 1
    mo.setResult("commonConfig", sendHash)
    mo.setResult("couponDisplayRate", int(1/config.COUPON_DISPLAY_RATE))
    if ftlog.is_debug():
        ftlog.debug("sendCommonConfig", mo)
    router.sendToUser(mo, userId)


def sendIdentifyReward(userId):
    """
    实名认证领奖
    """
    mo = MsgPack()
    mo.setCmd("id_card_identify_reward")
    mo.setResult("gameId", FISH_GAMEID)
    mo.setResult("userId", userId)
    identifyReward = []
    if ftlog.is_debug():
        ftlog.debug("user_system.sendIdentifyReward IN",
                    "userId=", userId)
    try:
        rewarded = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.idCardRewarded)
        if rewarded:
            code = 1
        else:
            idCardReward = config.getCommonValueByKey("idCardReward", [])
            if ftlog.is_debug():
                ftlog.debug("user_system.sendIdentifyReward send reward",
                            "userId=", userId,
                            "idCardReward=", idCardReward)
            code = util.addRewards(userId, idCardReward, "BI_NFISH_NEW_USER_REWARDS")
            if code == 0:
                identifyReward = idCardReward
                gamedata.setGameAttr(userId, FISH_GAMEID, GameData.idCardRewarded, 1)
    except Exception as e:
        ftlog.error("user_system.sendIdentifyReward error", e,
                    "userId=", userId)
        code = 3
    mo.setResult("code", code)
    mo.setResult("reward", identifyReward)
    router.sendToUser(mo, userId)


def isAdult(userId, cardId=0):
    """
    身份证日期是否合法
    """
    if not cardId:
        idInfo = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.idCardInfo)
        if not idInfo:
            return 1
        cardId = idInfo.get("id")
    birthTime = datetime.datetime.strptime(str(cardId)[6:14], "%Y%m%d")
    nowTime = datetime.datetime.now()
    if nowTime.year - birthTime.year > 18:
        return 1
    if nowTime.year - birthTime.year < 18:
        return 0
    if nowTime.month > birthTime.month:
        return 1
    if nowTime.month < birthTime.month:
        return 0
    if nowTime.day < birthTime.day:
        return 0
    else:
        return 1


def _is_contains_chinese(strs):
    """
    姓名是否合法
    """
    if len(strs) < 1 or len(strs) > 10:
        return False
    isChi = True
    for ch in strs:
        if (u"\u4e00" <= ch and ch <= u"\u9fff") or ch == ".":
            continue
        else:
            isChi = False
            break
    return isChi


def _checkIdCard(id_number):
    """
    身份证号是否合法
    """
    id_number = str(id_number)
    id_code_list = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_code_list = [1, 0, "X", 9, 8, 7, 6, 5, 4, 3, 2]
    if len(id_number) != 18:
        return 1, "Length error"
    if not re.match(r"^\d{17}(\d|X|x)$", id_number):
        return 2, "Format error"
    if not config.getIdCardAreaConf(id_number[0:6]):
        return 3, "Area code error"
    try:
        datetime.date(int(id_number[6:10]), int(id_number[10:12]), int(id_number[12:14]))
    except ValueError as ve:
        return 4, "Datetime error: {0}".format(ve)
    if str(check_code_list[sum([a * b for a, b in zip(id_code_list, [int(a) for a in id_number[0:-1]])]) % 11]) != \
            str(id_number.upper()[-1]):
        return 5, "Check code error"
    return 0, "Success"


def sendVersionUpdateTipsMsg(userId, clientId, clientVersion):
    """
    发送版本更新提示消息
    """
    clientIdNum = util.getClientIdNum(userId, clientId)
    versionUpdateConf = config.getPublic("versionUpdateConf", {}).get(str(clientIdNum), {})
    for version in sorted(versionUpdateConf.keys()):
        if StrictVersion(str(clientVersion)) < StrictVersion(str(version)):
            lang = util.getLanguage(userId, clientId)
            conf = versionUpdateConf[version]
            mo = MsgPack()
            mo.setCmd("fishTips")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("info", config.getMultiLangTextConf(conf["info"], lang=lang))
            mo.setResult("desc", config.getMultiLangTextConf(conf["desc"], lang=lang))
            mo.setResult("type", conf["type"])
            mo.setResult("tipsUrl", conf["tipsUrl"])
            router.sendToUser(mo, userId)
            break


def getChatPunish(userId):
    """
    获取玩家聊天惩罚状态
    """
    chatPunish = daobase.executeMixCmd("HGET", "chatPunish", userId)
    if chatPunish:
        punishState, _ = chatPunish.split(":")
        return int(punishState)
    return 0


def setChatPunish(userId, punishState):
    """
    设置玩家聊天惩罚状态
    :param punishState: 0:正常 1:屏蔽 2:禁言 3:封禁
    """
    if punishState == 3:
        code = executeForbidden(userId, True)
    else:
        code = executeForbidden(userId, False)
    if code == 0:
        if punishState == 0:
            daobase.executeMixCmd("HDEL", "chatPunish", userId)
        else:
            daobase.executeMixCmd("HSET", "chatPunish", userId, "%s:%s" % (punishState, int(time.time())))
    return code


def executeForbidden(userId, isForbidden):
    """
    对玩家执行封禁/解除封禁
    :return: 0:执行成功 1:执行失败
    """
    requestUrl = gdata.httpGame() + "/open/v3/user/setForbidden"
    if isForbidden:
        postData = {"lock_users": [userId]}
    else:
        postData = {"unlock_users": [userId]}
    try:
        result = util.doHttpQuery(requestUrl, postData, timeout=3)
        if result and result.get("error") is None:
            return 0
    except:
        ftlog.error("executeForbidden error", userId, isForbidden)
    return 1


def queryForbidden(userId):
    """
    查询玩家账号是否被封禁
    :return: 0:未封禁 1:已封禁
    """
    requestUrl = gdata.httpGame() + "/open/v4/tools/query_forbidden"
    signStr = "access_id=wa15b4444ce9d977f4&user_Id=%d:G64RBRAkKh57PR0EWZqsVE5H4GiPKPx7" % userId
    import hashlib
    sign = str(hashlib.sha256(signStr).hexdigest().lower())
    postData = {"user_Id": userId,
                "access_id": "wa15b4444ce9d977f4",
                "sign": sign}
    try:
        result = util.doHttpQuery(requestUrl, postData)
        if result and result.get("result", {}).get("code") == 1:
            return 1
    except:
        ftlog.error("queryForbidden error", userId)
    return 0


def _triggerChargeNotifyEvent(event):
    """
    充值发货事件
    """
    ftlog.info("user_system._triggerChargeNotifyEvent->",
               "userId =", event.userId,
               "gameId =", event.gameId,
               "rmbs =", event.rmbs,
               "productId =", event.productId,
               "clientId =", event.clientId,
               "isAddVipExp", getattr(event, "isAddVipExp", False))
    userId = event.userId
    productId = event.productId
    # 购买非代购券商品.
    if event.productId not in config.getPublic("notVipExpProductIds", []) and event.rmbs > 0:
        from newfish.entity import vip_system
        # # app充值
        # if util.isAppClient(userId):
        #     isAddVipExp = False
        # else: # 微信充值
        #     isAddVipExp = True
        isAddVipExp = getattr(event, "isAddVipExp", False)
        vip_system.addUserVipExp(event.gameId, userId, event.diamonds, "BUY_PRODUCT",
                                 pokerconf.productIdToNumber(productId), productId,
                                 rmbs=event.rmbs, isAddVipExp=isAddVipExp)


def _triggerUserLoginEvent(event):
    """
    用户登录事件
    """
    userId = event.userId
    dayFirst = event.dayFirst
    if dayFirst:
        reportBILogOnLogin(userId)
    updateLoginData(userId)
    refreshUserData(userId)


def _triggerItemChangeEvent(event):
    # 只有通过渔场外增加的资产，且用户在渔场内时才需要刷新用户数据
    if event.type == 0 and (event.changed.get("ud") or event.changed.get("items")):
        isIn, roomId, tableId, seatId = util.isInFishTable(event.userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "refresh_user_data")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", util.getClientId(event.userId))
            mo.setParam("userId", event.userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            router.sendTableServer(mo, roomId)


def _triggerAddInvitedNewUserEvent(event):
    shareUserId = event.userId
    invitedUserId = event.invitedUserId
    if ftlog.is_debug():
        ftlog.debug("_triggerAddInvitedNewUserEvent", shareUserId, invitedUserId)
    updateInvitedState(invitedUserId, shareUserId, True)


def _triggerNewbieTaskCompleteEvent(event):
    """
    增加充值奖池
    """
    util.incrUserRechargeBonus(event.userId, 100000)


def _triggerProductBuyEvent(event):
    """
    处理商品购买事件
    """
    userId = event.userId
    productId = event.productId
    rechargeConf = config.getRechargePoolConf(productId)
    if rechargeConf:
        # 第一次购买指定奖池金币，之后随机
        rechargeCountDict = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.rechargeCount, {})
        rechargeCountDict[productId] = rechargeCountDict.setdefault(productId, 0) + 1
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.rechargeCount, json.dumps(rechargeCountDict))
        rechargeBonus = 0
        if rechargeCountDict[productId] == 1:
            rechargeBonus += int(rechargeConf["bonuses"][2]["bonus"])
        else:
            randInt = random.randint(1, 10000)
            for bonusConf in rechargeConf["bonuses"]:
                probb = bonusConf["probb"]
                if probb[0] <= randInt <= probb[1]:
                    rechargeBonus += int(bonusConf["bonus"])
        # 增加充值奖池
        final = util.incrUserRechargeBonus(userId, int(rechargeBonus))
        ftlog.info("_triggerProductBuyEvent->userId =", userId,
                   "productId =", productId,
                   "rechargeBonus =", rechargeBonus,
                   "finalRechargeBonus =", final, event.buyCount)


_inited = False


def initialize():
    ftlog.info("newfish user_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import ChargeNotifyEvent
        from poker.entity.events.tyevent import EventUserLogin
        from hall.game import TGHall
        from newfish.game import TGFish
        from newfish.entity.event import ItemChangeEvent, \
            AddInvitedNewUserEvent, NewbieTaskCompleteEvent, NFChargeNotifyEvent, ProductBuyEvent
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(NFChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        TGFish.getEventBus().subscribe(ItemChangeEvent, _triggerItemChangeEvent)
        TGFish.getEventBus().subscribe(AddInvitedNewUserEvent, _triggerAddInvitedNewUserEvent)
        TGFish.getEventBus().subscribe(NewbieTaskCompleteEvent, _triggerNewbieTaskCompleteEvent)
        TGFish.getEventBus().subscribe(ProductBuyEvent, _triggerProductBuyEvent)
    ftlog.info("newfish user_system initialize end")
