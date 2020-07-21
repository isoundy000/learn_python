#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/14

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker
from newfish.entity import config, gift_system, item, util, daily_gift
from newfish.entity.config import FISH_GAMEID
from newfish.entity.quest import quest_system
from newfish.entity.quest import daily_quest, main_quest
from newfish.entity.chest import chest_system
from newfish.entity.fishactivity import fish_activity_system
from newfish.entity.achievement import achievement_system
from newfish.entity.skill import skill_system
from newfish.entity import fish_notice_system
from newfish.entity.grand_prize_pool import GrandPrizePool          # 巨奖奖池
from newfish.entity import piggy_bank
from newfish.entity import treasure_system
from newfish.entity import level_rewards, level_funds


@markCmdActionHandler
class GameTcpHandler(BaseMsgPackChecker):

    def _check_param_star(self, msg, key, params):
        star = msg.getParam(key)
        if isinstance(star, int) and star > 0:
            return None, star
        return "ERROR of star !" + str(star), -1

    def _check_param_kindId(self, msg, key, params):
        kindId = msg.getParam("kindId")
        if kindId and isinstance(kindId, int):
            return None, kindId
        return "ERROR of kindId !" + str(kindId), None

    def _check_param_itemId(self, msg, key, params):
        itemId = msg.getParam("itemId")
        if itemId:
            return None, itemId
        return "ERROR of itemId !" + str(itemId), None

    def _check_param_rebateItemId(self, msg, key, params):
        rebateItemId = msg.getParam("rebateItemId", 0)
        if isinstance(rebateItemId, int) and rebateItemId >= 0:
            return None, rebateItemId
        return "ERROR of rebateItemId !" + str(rebateItemId), None

    def _check_param_count(self, msg, key, params):
        count = msg.getParam("count")
        if isinstance(count, int) and count > 0:
            return None, count
        return "ERROR of count !" + str(count), None

    def _check_param_oldOrder(self, msg, key, params):
        oldOrder = msg.getParam("oldOrder")
        if isinstance(oldOrder, int) and oldOrder >= 0:
            return None, oldOrder
        return "ERROR of oldOrder !" + str(oldOrder), None

    def _check_param_newOrder(self, msg, key, params):
        newOrder = msg.getParam("newOrder")
        if isinstance(newOrder, int) and newOrder >= 0:
            return None, newOrder
        return "ERROR of newOrder !" + str(newOrder), None

    def _check_param_order(self, msg, key, params):
        order = msg.getParam("order")
        if isinstance(order, int) and order >= 0:
            return None, order
        return "ERROR of order !" + str(order), None

    def _check_param_atOnce(self, msg, key, params):
        atOnce = msg.getParam("atOnce")
        if isinstance(atOnce, int) and atOnce in [0, 1, 2]:
            return None, atOnce
        return "ERROR of atOnce !" + str(atOnce), None

    def _check_param_actionType(self, msg, key, params):
        actionType = msg.getParam("actionType")
        if isinstance(actionType, int):
            return None, actionType
        return "ERROR of actionType !" + str(actionType), None

    def _check_param_giftId(self, msg, key, params):
        giftId = msg.getParam("giftId")
        if isinstance(giftId, int):
            return None, giftId
        return "ERROR of giftId !" + str(giftId), None

    def _check_param_acId(self, msg, key, params):
        acId = msg.getParam("acId")
        if acId:
            return None, acId
        return "ERROR of acId !" + str(acId), None

    def _check_param_taskId(self, msg, key, params):
        taskId = msg.getParam("taskId")
        if isinstance(taskId, (int, str, unicode)):
            return None, taskId
        return "ERROR of taskId !" + str(taskId), None

    def _check_param_otherUserId(self, msg, key, params):
        otherUserId = msg.getParam("otherUserId")
        if otherUserId and isinstance(otherUserId, int):
            return None, otherUserId
        return "ERROR of otherUserId !" + str(otherUserId), None

    def _check_param_rewards(self, msg, key, params):
        rewards = msg.getParam("rewards")
        if rewards:
            return None, rewards
        return "ERROR of rewards !" + str(rewards), None

    def _check_param_groupId(self, msg, key, params):
        groupId = msg.getParam("groupId")
        if isinstance(groupId, int):
            return None, groupId
        return "ERROR of groupId !" + str(groupId), None

    def _check_param_exchangeCode(self, msg, key, params):
        exchangeCode = msg.getParam("exchangeCode")
        if exchangeCode:
            return None, exchangeCode
        return "ERROR of exchangeCode !" + str(exchangeCode), None

    def _check_param_extend(self, msg, key, params):
        extend = msg.getParam("extend") or 0
        if str(extend):
            return None, extend
        return "ERROR of extend !" + str(extend), None

    def _check_param_convertKindId(self, msg, key, params):
        convertKindId = msg.getParam("convertKindId")
        if isinstance(convertKindId, int):
            return None, convertKindId
        return "ERROR of convertKindId !" + str(convertKindId), None

    def _check_param_buyType(self, msg, key, params):
        buyType = msg.getParam("buyType")
        if buyType and (buyType == "direct" or config.isThirdBuyType(buyType)):
            return "ERROR of buyType !" + str(buyType), None
        return None, buyType

    def _check_param_title(self, msg, key, params):
        title = msg.getParam("title")
        return None, title

    def _check_param_gunId(self, msg, key, params):
        gunId = msg.getParam("gunId")
        if isinstance(gunId, int):
            return None, gunId
        return "ERROR of gunId !" + str(gunId), None

    def _check_param_skinId(self, msg, key, params):
        skinId = msg.getParam("skinId")
        if isinstance(skinId, int):
            return None, skinId
        return "ERROR of skinId !" + str(skinId), None

    def _check_param_skillId(self, msg, key, params):
        skillId = msg.getParam("skillId")
        if isinstance(skillId, int):
            return None, skillId
        return "ERROR of skillId !" + str(skillId), None

    def _check_param_sharedUserId(self, msg, key, params):
        sharedUserId = msg.getParam("sharedUserId")
        if isinstance(sharedUserId, int) and sharedUserId > 0:
            return None, sharedUserId
        return "ERROR of sharedUserId !" + str(sharedUserId), None

    def _check_param_timestamp(self, msg, key, params):
        timestamp = msg.getParam("timestamp")
        if isinstance(timestamp, int):
            return None, timestamp
        return "ERROR of timestamp !" + str(timestamp), None

    def _check_param_noticeId(self, msg, key, params):
        noticeId = msg.getParam("noticeId")
        if str(noticeId):
            return None, noticeId
        return "ERROR of noticeId !" + str(noticeId), None

    def _check_param_type(self, msg, key, params):
        type = msg.getParam("type")
        if isinstance(type, (int, str, unicode)):
            return None, type
        return "ERROR of type !" + str(type), None

    def _check_param_honorId(self, msg, key, params):
        honorId = msg.getParam("honorId")
        if isinstance(honorId, int):
            return None, honorId
        return "ERROR of honorId !" + str(honorId), None

    def _check_param_level(self, msg, key, params):
        level = msg.getParam("level")
        if isinstance(level, int) and level >= 0:
            return None, level
        return "ERROR of level !" + str(level), None

    def _check_param_productId(self, msg, key, params):
        productId = msg.getParam("productId")
        if isinstance(productId, (int, str, unicode)):
            return None, productId
        return "ERROR of productId !" + str(productId), None

    def _check_param_display(self, msg, key, params):
        display = msg.getParam("display")
        if isinstance(display, int):
            return None, display
        return "ERROR of display !" + str(display), None

    def _check_param_sectionId(self, msg, key, params):
        sectionId = msg.getParam("sectionId")
        if isinstance(sectionId, int):
            return None, sectionId
        return "ERROR of sectionId !" + str(sectionId), None

    def _check_param_rewardType(self, msg, key, params):
        rewardType = msg.getParam("rewardType")
        if isinstance(rewardType, int):
            return None, rewardType
        return "ERROR of rewardType !" + str(rewardType), None

    def _check_param_idx(self, msg, key, params):
        idx = msg.getParam("idx")
        if isinstance(idx, int):
            return None, idx
        return "ERROR of idx !" + str(idx), None

    def _check_param_module(self, msg, key, params):
        module = msg.getParam("module")
        if module:
            return None, module
        return "ERROR of module !" + str(module), None

    def _check_param_id(self, msg, key, params):
        id = msg.getParam("id")
        if id:
            return None, id
        return "ERROR of id !" + str(id), None

    def _check_param_gameMode(self, msg, key, params):
        gameMode = msg.getParam("gameMode", 0)
        if gameMode == 0 or gameMode == 1:
            return None, gameMode
        return "ERROR of gameMode !" + str(gameMode), None

    @markCmdActionMethod(cmd="activity_fish", action="fishGift", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishGift(self, userId, gameId, clientId, giftId, buyType, rebateItemId=0):
        """发送礼包消息"""
        ftlog.debug("doGetFishGift", userId, gameId)
        gift_system.doSendFishGift(userId, clientId)

    @markCmdActionMethod(cmd="activity_fish", action="buyFishGift", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyFishGift(self, userId, gameId, clientId, giftId, buyType, rebateItemId=0):
        """购买礼包"""
        ftlog.debug("doBuyFishGift", userId, gameId, clientId, giftId, buyType, rebateItemId)
        if buyType:
            gift_system.doBuyFishGift(userId, clientId, giftId, buyType, rebateItemId)

    @markCmdActionMethod(cmd="activity_fish", action="fishGiftReward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishGiftReward(self, userId, gameId, clientId, giftId):
        """领取礼包"""
        ftlog.debug("doGetFishGiftReward", userId, gameId, clientId, giftId)
        gift_system.doGetFishGiftReward(userId, clientId, giftId)

    @markCmdActionMethod(cmd="activity_fish", action="monthGiftInfo", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetMonthCardGiftInfo(self, userId, gameId, clientId):
        """获取月卡礼包信息"""
        ftlog.debug("doGetMonthCardGiftInfo", userId, gameId, clientId)
        gift_system.doSendNewMonthCardGiftInfo(userId, clientId)

    # @markCmdActionMethod(cmd="activity_fish", action="monthGiftBuy", clientIdVer=0, scope="game", lockParamName="userId")
    # def doBuyMonthCardGift(self, userId, gameId, giftId, buyType):
    #     ftlog.debug("doBuyMonthCardGift", userId, gameId, buyType)
    #     gift_system.doBuyFishGift(userId, giftId, buyType)


    @markCmdActionMethod(cmd="activity_fish", action="monthGiftGet", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetMonthGiftReward(self, userId, gameId, clientId, giftId):
        """领取月卡礼包"""
        ftlog.debug("doGetMonthGiftReward", userId, gameId, clientId, giftId)
        gift_system.doGetFishGiftReward(userId, clientId, giftId)

    @markCmdActionMethod(cmd="activity_fish", action="fishExchange", clientIdVer=0, scope="game", lockParamName="userId")
    def doFishExchange(self, userId, gameId, clientId, exchangeCode):
        """兑换码"""
        exchangeInfo = fish_activity_system.doExchange(userId, clientId, exchangeCode)
        message = MsgPack()
        message.setCmd("fishExchange")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", userId)
        message.setResult("exchangeInfo", exchangeInfo)
        router.sendToUser(message, userId)

    @markCmdActionMethod(cmd="activity_fish", action="fishNoticeBtns", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishNoticeBtnInfos(self, userId, gameId, clientId):
        """获取所有公告信息"""
        fish_notice_system.doGetFishAllNoticeInfos(userId, clientId)

    @markCmdActionMethod(cmd="activity_fish", action="fishNoticeRead", clientIdVer=0, scope="game", lockParamName="userId")
    def doReadFishNotice(self, userId, gameId, clientId, noticeId):
        """读通知"""
        ftlog.debug("doReadFishNotice==》", userId, gameId, noticeId)
        fish_notice_system.doReadFishNotice(userId, clientId, noticeId)

    @markCmdActionMethod(cmd="activity_fish", action="fishActivityInfo", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishActivityOneInfo(self, userId, gameId, clientId, acId, extend):
        """获取单个活动数据"""
        fish_activity_system.doGetFishOneActivity(userId, acId, extend)

    @markCmdActionMethod(cmd="activity_fish", action="fishActivityBtns", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishActivityBtnInfos(self, userId, gameId, clientId):
        """活动按钮数据"""
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "fishActivityBtns")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            router.sendTableServer(mo, roomId)
        else:
            fish_activity_system.doGetFishAllActivityBtns(userId, False)

    @markCmdActionMethod(cmd="activity_fish", action="fishActivityRead", clientIdVer=0, scope="game", lockParamName="userId")
    def doReadFishActivity(self, userId, gameId, clientId, acId):
        """活动已读"""
        ftlog.debug("doReadFishAc==》", userId, gameId, acId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "fishActivityRead")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("acId", acId)
            router.sendTableServer(mo, roomId)
        else:
            fish_activity_system.doReadFishActivity(userId, acId, False)

    @markCmdActionMethod(cmd="activity_fish", action="fishActivityReceive", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishAcReward(self, userId, gameId, clientId, acId, taskId, extend):
        """领取活动奖励请求"""
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "fishActivityReceive")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("acId", acId)
            mo.setParam("taskId", taskId)
            mo.setParam("extend", extend)
            router.sendTableServer(mo, roomId)
        else:
            fish_activity_system.doGetFishAcReward(userId, acId, taskId, extend)

    @markCmdActionMethod(cmd="activity_fish", action="fishActivityBonusResult", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishAcBonusReward(self, userId, gameId, clientId, acId, count, extend):
        """获取抽奖结果"""
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "fishActivityBonusResult")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("acId", acId)
            mo.setParam("count", count)
            mo.setParam("extend", extend)
            router.sendTableServer(mo, roomId)
        else:
            fish_activity_system.doGetFishActivityBonusReward(userId, acId, count, extend)

    @markCmdActionMethod(cmd="activity_fish", action="fishActivityShow", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetShowActivity(self, userId, gameId, clientId):
        fish_activity_system.sendShowActivity(userId)

    @markCmdActionMethod(cmd="activity_fish", action="fishActivityShowed", clientIdVer=0, scope="game", lockParamName="userId")
    def doShowedActivity(self, userId, gameId, clientId, acId):
        fish_activity_system.sendShowedActivity(userId, acId)

    @markCmdActionMethod(cmd="activity_fish", action="fishActVipHelpHistory", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetAllVipHelpHistory(self, userId, gameId, clientId):
        fish_activity_system.doGetAllVipHelpHistory(userId)

    @markCmdActionMethod(cmd="activity_fish", action="fishActVipHelpGiveReward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGiveReward(self, userId, gameId, clientId, otherUserId, rewards, title):
        fish_activity_system.doGiveReward(userId, otherUserId, rewards, title)

    @markCmdActionMethod(cmd="activity_fish", action="fishActBulletDoubleHistory", clientIdVer=0, scope="game", lockParamName="userId")
    def getBulletDoubleInfo(self, userId, gameId, clientId, acId, timestamp):
        fish_activity_system.getBulletDoubleInfo(userId, acId, timestamp)











    @markCmdActionMethod(cmd="game", action="grand_prix_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetGrandPrixInfo(self, userId, gameId, clientId):
        """
        获取大奖赛信息
        """
        ftlog.debug("doGetGrandPrixInfo", userId, gameId, clientId)
        from newfish.entity import grand_prix
        grand_prix.sendGrandPrixInfo(userId)