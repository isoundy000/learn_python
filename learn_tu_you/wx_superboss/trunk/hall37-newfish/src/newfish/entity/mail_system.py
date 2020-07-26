# -*- coding=utf-8 -*-
"""
Created by hhx on 17/6/20.
"""
import time
import json

from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.protocol import router
from poker.entity.dao import gamedata, userdata
from newfish.entity import util, module_tip, config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.event import SendMailEvent, ReceiveMailEvent
from newfish.servers.util.rpc import user_rpc
from newfish.entity.msg import GameMsg
from poker.entity.biz import bireport


# 邮件发送方类型
class MailSenderType:
    MT_SYS = 1      # 系统
    MT_USERS = 2    # 玩家


# 邮件奖励类型
class MailRewardType:
    SystemReward = 0        # 系统奖励
    Present = 1             # 赠送
    StarRank = 2            # 海星榜奖励
    SystemCompensate = 3    # 系统补偿
    HonorReward = 4         # 称号奖励
    FriendReward = 5        # 渔友对战胜利奖励
    FriendUnbind = 6        # 渔友对战房间解散退还
    RobberyRank = 7         # 招财赢家榜奖励
    RobberyCompensate = 8   # 招财补偿
    ChestReward = 9         # 宝箱兑换奖励
    ShareReward = 10        # 分享奖励
    MatchReward = 11        # 比赛奖励
    InviteReward = 12       # 邀请有礼
    ActivityReward = 13     # 活动奖励
    TreasureReward = 14     # 宝藏奖励
    SystemInfo = 15         # 系统通知
    FishCanReturn = 16      # 鱼罐头返还
    GrandPrixReward = 17    # 大奖赛奖励
    PoseidonRank = 18       # 海皇赢家榜奖励
    PoseidonCompensate = 19 # 海皇补偿


# 邮件状态
class MailState:
    Default = 0
    Received = 1            # 已领取
    Delete = 2              # 已删除


# 1:系统邮件, 2:玩家邮件
MAIL_SENDER_TYPE_LIST = [MailSenderType.MT_SYS, MailSenderType.MT_USERS]
# 收件箱容量.
MAIL_DISPLAY_COUNT = 50
# 发件箱容量.
MAX_OUT_MAIL_COUNT = 10


def _getMailExpireTime(mailSenderType):
    """
    获取邮件过期时间
    """
    expireDay = 1
    mailExpireDay = config.getPublic("mailExpireDay", [])
    if len(mailExpireDay) > mailSenderType:
        expireDay = mailExpireDay[mailSenderType]
    return int(expireDay) * 86400


def addOneMail(senderUserId, receiverUserId, mailRewardType, rewards=None, message=None, title=None):
    """
    添加一封邮件
    :param senderUserId: 发件人
    :param receiverUserId: 收件人
    :param mailRewardType: 邮件类型
    :param rewards: 附件奖励
    :param message: 邮件内容
    :param title: 标题
    :return: 是否添加成功
    """
    if ftlog.is_debug():
        ftlog.debug("addOneMail->", senderUserId, receiverUserId, mailRewardType, rewards, message, title)
    message = message or ""
    rewards = rewards or []
    title = title or ""
    # # 查询收件人信息
    # _key = GameData.mailInfos if senderUserId == config.ROBOT_MAX_USER_ID else GameData.userMailInfos
    # mailInfos = gamedata.getGameAttrJson(receiverUserId, FISH_GAMEID, _key, [])
    # mailInfos = _removeMailExpData(mailInfos, MAIL_DISPLAY_COUNT)
    # tempMail = _getUnDeleteMail(mailInfos[0:MAIL_DISPLAY_COUNT])
    # if len(tempMail) >= MAIL_DISPLAY_COUNT and mailRewardType == MailRewardType.Present:  # 收件箱已满
    #     return False
    # 添加邮件到发件人发件箱
    if senderUserId > config.ROBOT_MAX_USER_ID:
        _sendMailBySender(senderUserId, receiverUserId, mailRewardType, rewards, message, title)
    # 添加邮件到收件人收件箱
    user_rpc.sendMailToReceiver(senderUserId, receiverUserId, mailRewardType, rewards, message, title)
    from newfish.game import TGFish
    event = SendMailEvent(senderUserId, FISH_GAMEID, receiverUserId, rewards)
    TGFish.getEventBus().publishEvent(event)
    return True


def sendSystemMail(userId, mailRewardType, rewards=None, message=None, title=None):
    """
    发送系统邮件
    """
    addOneMail(config.ROBOT_MAX_USER_ID, userId, mailRewardType, rewards, message, title)


def isMailFull(userId, type, mailSenderType):
    """
    获取收件箱是否已满
    """
    # 邮件只保留有限数量,多了自动删除,所以不存在邮箱已满的情况了.
    # # 查询收件人信息
    # _key = GameData.mailInfos if mailSenderType == MailSenderType.MT_SYS else GameData.userMailInfos
    # mailInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, _key, [])
    # mailInfos = _removeMailExpData(mailInfos, len(mailInfos))
    # tempMail = _getUnDeleteMail(mailInfos[0:MAIL_DISPLAY_COUNT])
    # if len(tempMail) >= MAIL_DISPLAY_COUNT and type == MailRewardType.Present:  # 收件箱已满
    #     return True
    return False


def _sendMailBySender(senderUserId, receiverUserId, type, reward=None, desc=None, title=None):
    """
    添加邮件到发件人发件箱
    :param senderUserId: 发件人
    :param receiverUserId: 收件人
    :param type: 邮件类型
    :param reward: 附件奖励
    :param desc: 邮件内容
    :param title: 标题
    """
    curTime = int(time.time())
    desc = desc or ""
    reward = reward or []
    title = title or ""
    mailOutId = gamedata.incrGameAttr(senderUserId, FISH_GAMEID, GameData.outMailId, 1)
    mailOutInfos = gamedata.getGameAttrJson(senderUserId, FISH_GAMEID, GameData.outMailInfos, [])
    receiverUserName = util.getNickname(receiverUserId)
    mailOutInfos.insert(0, {"id": mailOutId, "userId": receiverUserId, "time": curTime, "name": receiverUserName,
                            "reward": reward, "type": type, "desc": desc, "title": title})
    mailOutInfos = _removeOutMailExpData(mailOutInfos, MAX_OUT_MAIL_COUNT)
    gamedata.setGameAttr(senderUserId, FISH_GAMEID, GameData.outMailInfos, json.dumps(mailOutInfos))
    if type == MailRewardType.Present:
        lang = util.getLanguage(senderUserId)
        message = config.getMultiLangTextConf("ID_PRESENT_TO_OTHER_MSG", lang=lang).format(receiverUserName, receiverUserId, util.buildRewardsDesc(reward, lang))
        GameMsg.sendPrivate(FISH_GAMEID, senderUserId, 0, message)


def sendMailToReceiver(senderUserId, receiverUserId, type, reward=None, desc=None, title=None):
    """
    添加邮件到收件人收件箱
    :param senderUserId: 发件人
    :param receiverUserId: 收件人
    :param type: 邮件类型
    :param reward: 附件奖励
    :param desc: 邮件内容
    :param title: 标题
    """
    curTime = int(time.time())
    desc = desc or ""
    reward = reward or []
    title = title or ""
    # 邮件的有效期.
    mailSenderType = MailSenderType.MT_SYS if senderUserId == config.ROBOT_MAX_USER_ID else MailSenderType.MT_USERS
    expireTs = curTime + _getMailExpireTime(mailSenderType)

    mailSendId = gamedata.incrGameAttr(receiverUserId, FISH_GAMEID, GameData.mailId, 1)
    _key = GameData.mailInfos if senderUserId == config.ROBOT_MAX_USER_ID else GameData.userMailInfos
    mailInfos = gamedata.getGameAttrJson(receiverUserId, FISH_GAMEID, _key, [])
    senderUserName = util.getNickname(senderUserId)
    mailInfos.insert(0, {"id": mailSendId, "userId": senderUserId, "time": curTime, "expireTime": expireTs,
                         "name": senderUserName, "reward": reward, "type": type, "desc": desc,
                         "state": MailState.Default, "title": title})
    mailInfos = _removeMailExpData(mailInfos, MAIL_DISPLAY_COUNT)
    gamedata.setGameAttr(receiverUserId, FISH_GAMEID, _key, json.dumps(mailInfos))
    _dealTips(receiverUserId, mailInfos, mailSenderType)
    if type == MailRewardType.Present:
        lang = util.getLanguage(receiverUserId)
        message = config.getMultiLangTextConf("ID_ACCEPT_PRESENT_MSG", lang=lang).format(senderUserName, senderUserId, util.buildRewardsDesc(reward, lang))
        GameMsg.sendPrivate(FISH_GAMEID, receiverUserId, 0, message)


def getAllOutVipHelpMail(userId):
    """
    获取发件(赠送)记录
    """
    mailInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.outMailInfos, [])
    tempMail = []
    for index, value in enumerate(mailInfos):
        if value["type"] == MailRewardType.Present:
            tempMail.append(value)
    tempMail = _removeOutMailExpData(tempMail, MAIL_DISPLAY_COUNT)
    return tempMail


def doGetAllMails(userId, mailSenderType):
    """
    发送收件箱邮件列表消息
    """
    if util.isFinishAllRedTask(userId):
        message = MsgPack()
        message.setCmd("fishMailList")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", userId)
        message.setResult("mailTypeList", MAIL_SENDER_TYPE_LIST)
        message.setResult("mailType", mailSenderType)
        mails = getAllMail(userId).get(mailSenderType, [])
        message.setResult("mails", mails)
        router.sendToUser(message, userId)


def getAllMail(userId):
    """
    获取收件箱所有邮件
    """
    tempMail = {}
    for _mt in MAIL_SENDER_TYPE_LIST:
        _key = GameData.mailInfos if _mt == MailSenderType.MT_SYS else GameData.userMailInfos
        mailInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, _key, [])
        tempMail[_mt] = _removeMailExpData(mailInfos, MAIL_DISPLAY_COUNT)
        # tempMail[_mt] = _getUnDeleteMail(tempMail[_mt])
        _dealTips(userId, tempMail[_mt], _mt)
        # tempMail[_mt].sort(cmp=_sortState)
    return tempMail


def _dealMail(userId, mailIds, mailSenderType):
    """
    领取邮件奖励
    :param mailType: 1为表示系统邮件，为2表示其他邮件
    """
    code = 0
    rewards = []
    curTime = int(time.time())
    _key = GameData.mailInfos if mailSenderType == MailSenderType.MT_SYS else GameData.userMailInfos
    mailInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, _key, [])
    for _mailInfo in mailInfos:
        expireTime = _mailInfo.get("expireTime")
        # 过期邮件不可领取.
        if expireTime and expireTime + 10 < curTime:
            continue
        if (not mailIds or _mailInfo["id"] in mailIds) and _mailInfo["state"] == MailState.Default:
            eventId = "BI_NFISH_MAIL_REWARDS"
            intEventParam = int(_mailInfo["type"])
            param0 = None
            if _mailInfo["type"] == MailRewardType.Present:
                eventId = "ACCEPT_PRESENT_ITEM"
                intEventParam = _mailInfo["userId"]
            elif _mailInfo["type"] in [MailRewardType.StarRank, MailRewardType.RobberyRank, MailRewardType.PoseidonRank]:
                eventId = "BI_NFISH_RANKING_REWARDS"
            elif _mailInfo["type"] == MailRewardType.InviteReward:
                param0 = _mailInfo["userId"]
            elif _mailInfo["type"] == MailRewardType.MatchReward:
                eventId = "MATCH_REWARD"
            elif _mailInfo["type"] == MailRewardType.TreasureReward:
                eventId = "BI_NFISH_TREASURE_REWARDS"
            elif _mailInfo["type"] == MailRewardType.FishCanReturn:
                eventId = "BI_NFISH_FISH_CAN_RETURN"

            commonRewards = []
            chestRewards = []
            if _mailInfo["reward"]:
                commonRewards, chestRewards, totalRewards = _getAllRewardInfo(userId, _mailInfo["reward"])
                code = util.addRewards(userId, totalRewards, eventId, intEventParam, param01=param0)
            if code == 0:
                _mailInfo["state"] = MailState.Received
                rewards.append({"commonReward": commonRewards, "chestRewards": chestRewards})
            elif code == 4:  # code 4 ----  没有奖励
                code = 0
                _mailInfo["state"] = MailState.Received
    if ftlog.is_debug():
        ftlog.debug("_dealMail=====>userId =", userId, "rewawrds =", rewards, "mailSenderType =", mailSenderType)
    gamedata.setGameAttr(userId, FISH_GAMEID, _key, json.dumps(mailInfos))
    # _dealTips(userId, _getUnDeleteMail(mailInfos[0:30]))
    return code, rewards


def _getAllRewardInfo(userId, mailReward):
    """
    拆分邮件中的奖励并返回相应信息
    """
    from newfish.entity.chest import chest_system
    commonRewards = []
    chestRewards = []
    totalRewards = []
    for reward in mailReward:
        itemId = reward["name"]
        if util.isChestRewardId(itemId):
            rewards = chest_system.getChestRewards(userId, itemId)
            chestRewards.append({"name": itemId, "reward": rewards})
            totalRewards.extend(rewards)
        else:
            commonRewards.append(reward)
            totalRewards.append(reward)
    return commonRewards, chestRewards, totalRewards


def deleteMail(userId, mailIds, mailSenderType, isForceDel=False):
    """
    删除邮件
    :param userId: 需要删除邮件的用户
    :param mailIds: 邮件ID列表（客户端传空列表为全部删除）
    :param mailType: 为1表示系统邮件，为2表示其他邮件
    :param isForceDel: 是否强制删除
    """
    code = 0
    _key = GameData.mailInfos if mailSenderType == MailSenderType.MT_SYS else GameData.userMailInfos
    mailInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, _key, [])
    for mailInfo in mailInfos:
        if not isForceDel:
            if mailInfo["state"] == MailState.Default:  # 未读或奖励未领取
                continue
        if not mailIds or mailInfo["id"] in mailIds:
            mailInfo["state"] = MailState.Delete
            if ftlog.is_debug():
                ftlog.debug("deleteMail=====>userId =", userId, "mailSenderType =", mailSenderType, "mailInfos =", mailInfos)
    mailInfos = _removeMailExpData(mailInfos, len(mailInfos))
    gamedata.setGameAttr(userId, FISH_GAMEID, _key, json.dumps(mailInfos))
    # _dealTips(userId, _removeMailExpData(mailInfos), mailType)
    return code


def doReceiveMail(userId, mailIds, mailSenderType):
    """
    领取邮件奖励
    :param userId: 玩家Id
    :param mailIds: 空是一键领取
    :param mailSenderType: 邮件类型:1系统邮件,2其他邮件
    """
    message = MsgPack()
    message.setCmd("fishMailReceive")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    code, rewards = _dealMail(userId, mailIds, mailSenderType)
    message.setResult("code", code)
    message.setResult("rewards", rewards)
    mails = getAllMail(userId).get(mailSenderType, [])
    message.setResult("mailType", mailSenderType)
    message.setResult("mails", mails)
    router.sendToUser(message, userId)
    from newfish.game import TGFish
    event = ReceiveMailEvent(userId, FISH_GAMEID)
    TGFish.getEventBus().publishEvent(event)


def doDeleteMail(userId, mailIds, mailSenderType):
    """
    执行删除邮件并发送消息
    """
    message = MsgPack()
    message.setCmd("fishMailDelete")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)
    code = deleteMail(userId, mailIds, mailSenderType)
    message.setResult("code", code)
    mails = getAllMail(userId).get(mailSenderType, [])
    message.setResult("mailType", mailSenderType)
    message.setResult("mails", mails)
    router.sendToUser(message, userId)
    if ftlog.is_debug():
        ftlog.debug("doDeleteMail, userId =", userId, "mailIds =", mailIds, "mailSenderType =", mailSenderType, "code =", code)


def _getUnDeleteMail(mailInfos):
    """
    获取未删除的的邮件
    """
    tempMail = []
    for _mailInfo in mailInfos:
        if ftlog.is_debug():
            ftlog.debug("_getUnDeleteMail ====>", _mailInfo)
        if _mailInfo["state"] != MailState.Delete:
            tempMail.append(_mailInfo)
    return tempMail


def _dealTips(userId, mailInfos, mailSenderType):
    """
    更新邮箱小红点
    """
    # 兼容处理老玩家数据。
    module_tip.cancelModuleTipEvent(userId, "mail", 0)
    module_tip.cancelModuleTipEvent(userId, "mail", mailSenderType)
    for mailInfo in mailInfos:
        if mailInfo["state"] == MailState.Default:
            module_tip.addModuleTipEvent(userId, "mail", mailSenderType)
            return
    # module_tip.resetModuleTipEvent(userId, "mail")


def _removeMailExpData(infos, totalCount):
    """
    删除收件箱过期邮件
    """
    curTime = int(time.time())
    ftlog.debug("_removeMailExpData", len(infos), totalCount)
    # 删除过期邮件.
    for idx in range(len(infos) - 1, -1, -1):
        expireTime = infos[idx].get("expireTime")
        if (expireTime and curTime > expireTime) or infos[idx].get("state") == MailState.Delete:
            infos.pop(idx)
    # infos.sort(key=lambda data: (data["id"]), reverse=True)
    infos.sort(key=lambda data: (data["time"]), reverse=True)
    # infos.sort(cmp=_sortMail)
    if len(infos) > totalCount:# 最多50条
        infos = infos[0:totalCount]
    return infos


def _sortMail(x, y):
    """
    邮件排序
    """
    if x["state"] - y["state"] > 0:
        return 1
    elif x["state"] == y["state"]:
        if x["time"] - y["time"] < 0:
            return 1
        elif x["time"] == y["time"]:
            if x["id"] - y["id"] < 0:
                return 1
            else:
                return -1
        else:
            return -1
    else:
        return -1


def _sortState(x, y):
    """
    邮件状态排序
    """
    if x["state"] - y["state"] >= 0:
        return 1
    else:
        return -1


def _removeOutMailExpData(infos, totalCount):
    """
    删除发件箱过期邮件
    """
    if ftlog.is_debug():
        ftlog.debug("_removeOutMailExpData==>", len(infos), totalCount)
    infos.sort(key=lambda data: (data["time"]), reverse=True)
    if len(infos) > totalCount:                                         # 最多50条
        tempMail = infos[0: (totalCount)]
        return tempMail
    else:
        return infos


def reportBILogMailPropCount(userId):
    """
    统计邮件中指定道具数量上报BI
    """
    mailInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.mailInfos, [])
    statisPropList = []
    for _mailInfo in mailInfos:
        if _mailInfo["reward"] and _mailInfo["state"] == MailState.Default:
            for mailReward in _mailInfo["reward"]:
                statisPropList.append(mailReward)
    if ftlog.is_debug():
        ftlog.debug("reportBILogMailPropCount========>", userId, statisPropList)
    return statisPropList


def _triggerReportBIPropEvent(event):
    """统计上报BI系统"""
    propList = config.getStatisPropConf()
    mailStatisProp = reportBILogMailPropCount(event.userId)
    if not mailStatisProp:
        return
    for mailStatis in mailStatisProp:
        propId = int(mailStatis.get("name"))
        propCount = mailStatis.get("count")
        if propId not in propList:
            continue
        bireport.reportGameEvent("BI_STATISTIC_Mail_PROP", event.userId, event.gameId, 0, 0, propId, propCount, 0, 0, [], event.clientId)
        if ftlog.is_debug():
            ftlog.debug("_triggerReportBIPropEvent", "propId=", propId, "propCount=", propCount, event.userId)


def _removeExpireMail(event):
    """
    移除过期邮件,此函数有同步风险,暂不使用.
    """
    userId = event.userId
    curTime = int(time.time())
    # 邮件的有效期（以天为单位）
    for _mt in MAIL_SENDER_TYPE_LIST:
        _key = GameData.mailInfos if _mt == MailSenderType.MT_SYS else GameData.userMailInfos
        mailInfos = gamedata.getGameAttrJson(userId, FISH_GAMEID, _key, [])
        for idx in range(len(mailInfos) - 1, -1, -1):
            expireTs = mailInfos[idx].get("expireTime", 0)
            if expireTs:
                if curTime > expireTs: # 过期就删除
                    mailInfos.pop(idx)
            # else:
            #     # 如果没有过期时间属性，就添加
            #     mailExpireDay = _getMailExpireTime(_mt)
            #     _mail["expireTime"] = curTime + mailExpireDay * 86400
        gamedata.setGameAttr(userId, FISH_GAMEID, _key, json.dumps(mailInfos))
        if ftlog.is_debug():
            ftlog.debug("_removeExpireMail, userId =", userId, "mailType =", _mt, "mailInfos =", mailInfos)


def _triggerCheckExpireMail(event):
    """
    检测过期邮件并移除
    """
    _removeExpireMail(event)


_inited = False


def initialize():
    ftlog.debug("newfish mailSystem￿ initialize begin")
    global _inited
    if not _inited:
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerReportBIPropEvent)
        # TGFish.getEventBus().subscribe(EventUserLogin, _triggerCheckExpireMail)
    ftlog.debug("newfish mailSystem initialize end")