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
        """请求要弹框的活动"""
        fish_activity_system.sendShowActivity(userId)

    @markCmdActionMethod(cmd="activity_fish", action="fishActivityShowed", clientIdVer=0, scope="game", lockParamName="userId")
    def doShowedActivity(self, userId, gameId, clientId, acId):
        """发送要求弹框的活动"""
        fish_activity_system.sendShowedActivity(userId, acId)

    @markCmdActionMethod(cmd="activity_fish", action="fishActVipHelpHistory", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetAllVipHelpHistory(self, userId, gameId, clientId):
        """获取玩家的赠送历史数据"""
        fish_activity_system.doGetAllVipHelpHistory(userId)

    @markCmdActionMethod(cmd="activity_fish", action="fishActVipHelpGiveReward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGiveReward(self, userId, gameId, clientId, otherUserId, rewards, title):
        """赠送别人奖励"""
        fish_activity_system.doGiveReward(userId, otherUserId, rewards, title)

    @markCmdActionMethod(cmd="activity_fish", action="fishActBulletDoubleHistory", clientIdVer=0, scope="game", lockParamName="userId")
    def getBulletDoubleInfo(self, userId, gameId, clientId, acId, timestamp):
        fish_activity_system.getBulletDoubleInfo(userId, acId, timestamp)

    @markCmdActionMethod(cmd="item_fish", action="buy", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyItem(self, userId, gameId, clientId, actionType, itemId, count, buyType, rebateItemId=0):
        """
        在商城购买商品（非人民币购买方式）
        """
        ftlog.debug("doBuyItem", userId, gameId, actionType, itemId, count, buyType, rebateItemId)
        # 只有购买珍珠时count有效，其余全部为1
        if actionType == 5:
            product = config.getStoreConf(clientId).get("chestStore", {}).get("items", {}).get(str(itemId), {})
            if not product.get("convenientBuy"):
                count = 1
        else:
            count = 1
        ftlog.debug("doBuyItem2", userId, gameId, actionType, itemId, count, buyType, rebateItemId)
        itemId, ret = item.doBuyItem(userId, clientId, actionType, itemId, count, buyType, rebateItemId)
        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "buy")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("actionType", actionType)
        mo.setResult("itemId", itemId)
        mo.setResult("count", count)
        mo.setResult("buyType", buyType)
        for k, v in ret.iteritems():
            mo.setResult(k, v)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="bag_list", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetItemBagList(self, userId, gameId, clientId):
        """获取背包列表"""
        ftlog.debug("doGetItemBagList", userId, gameId, clientId)
        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "bag_list")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("items", item.getItemList(userId, clientId))
        mo.setResult("hallItems", item.getHallItemList(userId, clientId))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="sale", clientIdVer=0, scope="game", lockParamName="userId")
    def doSaleItem(self, userId, gameId, clientId, itemId, kindId, count):
        """打开|出售道具"""
        ftlog.debug("doSaleItem", userId, gameId, clientId, itemId, kindId, count)
        reason, rewards, dropConf = item.saleItem(userId, itemId, kindId, count, clientId)
        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "sale")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("itemId", itemId)
        mo.setResult("kindId", kindId)
        mo.setResult("count", count)
        mo.setResult("reason", reason)
        if reason == 0:
            mo.setResult("rewards", rewards)
        if dropConf is not None:
            mo.setResult("egg_dropConf", dropConf)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="convert", clientIdVer=0, scope="game", lockParamName="userId")
    def doConvertItem(self, userId, gameId, clientId, kindId, count, convertKindId):
        """兑换道具"""
        ftlog.debug("doConvertItem", userId, gameId, clientId, kindId, count, convertKindId)
        reason, rewards = item.convertItem(userId, kindId, count, convertKindId, clientId)
        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "convert")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("kindId", kindId)
        mo.setResult("count", count)
        mo.setResult("convertKindId", convertKindId)
        mo.setResult("reason", reason)
        if reason == 0:
            mo.setResult("rewards", rewards)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="select", clientIdVer=0, scope="game", lockParamName="userId")
    def doSelectItem(self, userId, gameId, clientId, kindId, count, idx):
        """选择道具奖励"""
        ftlog.debug("doSelectItem", userId, gameId, clientId, kindId, count, idx)
        reason, rewards = item.selectItemRewards(userId, kindId, count, idx, clientId)
        mo = MsgPack()
        mo.setCmd("item_fish")
        mo.setResult("action", "select")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("kindId", kindId)
        mo.setResult("count", count)
        mo.setResult("idx", idx)
        mo.setResult("reason", reason)
        if reason == 0:
            mo.setResult("rewards", rewards)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="up_skill", clientIdVer=0, scope="game", lockParamName="userId")
    def doUseItem(self, userId, gameId, clientId, kindId, skillId):
        """使用道具"""
        ftlog.debug("doUseItem", userId, gameId, clientId, kindId, skillId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        actionType = 0
        if isIn:
            pass
        else:
            mo = MsgPack()
            mo.setCmd("skill_upgrade")
            mo.setResult("gameId", FISH_GAMEID)
            mo.setResult("userId", userId)
            mo.setResult("skillId", skillId)
            mo.setResult("actionType", actionType)
            code, starLevel, originalLevel, currentLevel, previousLevel = skill_system.upgradeMaxSkill(userId, kindId,
                                                                                                       clientId)
            mo.setResult("starLevel", starLevel)
            mo.setResult("originalLevel", originalLevel)
            mo.setResult("currentLevel", currentLevel)
            mo.setResult("previousLevel", previousLevel)
            mo.setResult("code", code)
            router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="chest_list", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetChestList(self, userId, gameId, clientId):
        """发送宝箱列表消息"""
        ftlog.debug("doGetChestList", userId, gameId)
        chest_system.sendChestListInfo(userId)

    @markCmdActionMethod(cmd="item_fish", action="chest_order", clientIdVer=0, scope="game", lockParamName="userId")
    def doAdjustChestOrder(self, userId, gameId, clientId, oldOrder, newOrder):
        """调整宝箱位置"""
        ftlog.debug("doAdjustChestOrder", userId, gameId)
        mo = MsgPack()
        mo.setCmd("chest_order")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("code", 0 if chest_system.adjustChestOrder(userId, oldOrder, newOrder) else 1)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="chest_open", clientIdVer=0, scope="game", lockParamName="userId")
    def doOpenChest(self, userId, gameId, clientId, order, atOnce):
        """对宝箱执行行为"""
        ftlog.debug("doOpenChest", userId, gameId)
        mo = MsgPack()
        mo.setCmd("chest_open")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        code, rewards = chest_system.executeChestAction(userId, order, atOnce)
        mo.setResult("code", code)
        if code == 0:
            mo.setResult("rewards", rewards)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="treasure_list", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetTreasureList(self, userId, gameId, clientId):
        """宝藏列表"""
        ftlog.debug("doGetTreasureList", userId, gameId, clientId)
        mo = MsgPack()
        mo.setCmd("treasure_list")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("treasures", treasure_system.getTreasureList(userId))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="treasure_upgrade", clientIdVer=0, scope="game", lockParamName="userId")
    def doUpgradeTreasure(self, userId, gameId, clientId, kindId):
        """升级宝藏"""
        ftlog.debug("doUpgradeTreasure", userId, gameId, clientId, kindId)
        mo = MsgPack()
        mo.setCmd("treasure_upgrade")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        code, level = treasure_system.upgradeTreasure(userId, kindId)
        mo.setResult("code", code)
        mo.setResult("level", level)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="item_fish", action="treasure_convert", clientIdVer=0, scope="game", lockParamName="userId")
    def doConvertTreasure(self, userId, gameId, clientId, kindId, count):
        """兑换宝藏碎片"""
        ftlog.debug("doConvertTreasure", userId, gameId, clientId, kindId, count)
        mo = MsgPack()
        mo.setCmd("treasure_convert")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        code, rewards = treasure_system.convertTreasure(userId, kindId, count)
        mo.setResult("code", code)
        if code == 0:
            mo.setResult("rewards", rewards)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="task", action="unlockLevel", clientIdVer=0, scope="game", lockParamName="")
    def doTaskUnlocklevel(self, userId, gameId):
        """获取相关任务按钮解锁信息"""
        from newfish.entity import config
        ftlog.debug("doTaskUnlocklevel", userId, gameId)
        mo = MsgPack()
        mo.setCmd("task")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("action", "unlockLevel")
        mo.setResult("dailyTask", config.getCommonValueByKey("dailyQuestOpenLevel"))
        mo.setResult("achievementTask", config.getCommonValueByKey("achievementOpenLevel"))
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="task", action="update", clientIdVer=0, scope="game", lockParamName="")
    def doTaskUpdate(self, userId, gameId, clientId):
        """获取玩家每日任务数据"""
        ftlog.debug("doTaskUpdate", userId, gameId, clientId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "task_update")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            router.sendTableServer(mo, roomId)
        else:
            quest_system.getQuestInfo(userId, clientId)

    @markCmdActionMethod(cmd="task", action="dailyReward", clientIdVer=0, scope="game", lockParamName="")
    def doTaskDailyReward(self, userId, gameId, star, type):
        """领取每日任务星级奖励"""
        ftlog.debug("doTaskDailyReward", userId, gameId)
        daily_quest.getDailyQuestReward(userId, star, type)

    @markCmdActionMethod(cmd="task", action="questReward", clientIdVer=0, scope="game", lockParamName="")
    def doTaskQuestReward(self, userId, gameId, taskId):
        """领取每日任务奖励"""
        ftlog.debug("doTaskQuestReward", userId, gameId, taskId)
        daily_quest.getQuestReward(userId, taskId)

    @markCmdActionMethod(cmd="task", action="refreshQuest", clientIdVer=0, scope="game", lockParamName="")
    def doRefreshQuestTask(self, userId, gameId, taskId):
        """手动刷新每日任务"""
        ftlog.debug("doRefreshQuestTask", userId, gameId, taskId)
        daily_quest.refreshQuestTaskId(userId, taskId)

    @markCmdActionMethod(cmd="task", action="achievement_info", clientIdVer=0, scope="game", lockParamName="userId")
    def getAchievementInfo(self, userId, gameId, clientId):
        """获取所有成就信息"""
        ftlog.debug("getAchievementInfo", gameId, clientId, userId)
        achievement_system.doGetAllAchievementInfo(userId)

    @markCmdActionMethod(cmd="task", action="achievement_level_info", clientIdVer=0, scope="game", lockParamName="userId")
    def getAchievementLevelInfo(self, userId, gameId, clientId):
        """获取所有成就等级信息"""
        ftlog.debug("getAchievementLevelInfo", gameId, clientId, userId)
        achievement_system.doGetAchievelLevelInfos(userId)

    @markCmdActionMethod(cmd="task", action="achievement_tasks", clientIdVer=0, scope="game", lockParamName="userId")
    def getAchievementAllTask(self, userId, gameId, clientId, honorId):
        """获取所有成就任务"""
        ftlog.debug("getAchievementAllTask", gameId, clientId, userId, honorId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "achievement_tasks")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("honorId", honorId)
            router.sendTableServer(mo, roomId)
        else:
            achievement_system.doGetAllAchievementTasks(userId, honorId)

    @markCmdActionMethod(cmd="task", action="achievement_tasks_reward", clientIdVer=0, scope="game", lockParamName="userId")
    def getAchievementTaskReward(self, userId, gameId, clientId, taskId):
        """获取成就任务奖励"""
        ftlog.debug("getAchievementTaskReward", gameId, clientId, userId, taskId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "achievement_tasks_reward")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("taskId", taskId)
            router.sendTableServer(mo, roomId)
        else:
            achievement_system.doReceiveTaskReward(userId, taskId)

    @markCmdActionMethod(cmd="task", action="achievement_level_reward", clientIdVer=0, scope="game", lockParamName="userId")
    def getAchievementLevelReward(self, userId, gameId, clientId, level):
        """称号等级奖励领取"""
        ftlog.debug("getAchievementLevelReward", gameId, clientId, userId, level)
        achievement_system.doReceiveAchieveLevelRewards(userId, level)

    @markCmdActionMethod(cmd="task", action="fishAchievementTask", clientIdVer=0, scope="game", lockParamName="userId")
    def getAchievementTaskResultOld(self, userId, gameId, clientId):
        pass

    @markCmdActionMethod(cmd="task", action="fishAchievementTaskReward", clientIdVer=0, scope="game", lockParamName="userId")
    def getAchievementTaskRewardResultOld(self, userId, gameId, clientId, groupId):
        pass

    @markCmdActionMethod(cmd="task", action="red_task_list", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetRedTaskList(self, userId, gameId, clientId):
        """获取任务列表"""
        ftlog.debug("getRedTaskList", gameId, clientId, userId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "red_task_list")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            router.sendTableServer(mo, roomId)

    @markCmdActionMethod(cmd="task", action="invite_task_infos", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetInviteTasks(self, userId, gameId, clientId, actionType):
        ftlog.debug("doGetInviteTasks", gameId, clientId, userId, actionType)
        from newfish.entity import invite_system
        invite_system.doGetInviteTasks(userId, actionType)

    @markCmdActionMethod(cmd="task", action="invite_task_receive", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetInviteTaskRewards(self, userId, gameId, clientId, taskId, actionType):
        ftlog.debug("doGetInviteTaskRewards", gameId, clientId, userId, taskId, actionType)
        from newfish.entity import invite_system
        invite_system.doGetTaskRewards(userId, taskId, actionType)

    @markCmdActionMethod(cmd="task", action="thanks_letter_reward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetThanksLetterRewards(self, userId, gameId, clientId):
        ftlog.debug("doGetThanksLetterRewards", gameId, clientId, userId)
        from newfish.entity import user_system
        user_system.sendThanksLetterReward(userId)

    @markCmdActionMethod(cmd="task", action="share_task_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetShareTaskInfo(self, userId, gameId):
        """获取分享有礼信息"""
        ftlog.debug("doGetShareTaskInfo", gameId, userId)
        from newfish.entity import user_system
        user_system.getShareTaskInfo(userId)

    @markCmdActionMethod(cmd="task", action="share_task_receive", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetShareTaskRewards(self, userId, gameId, taskId):
        """领取分享好礼奖励"""
        ftlog.debug("doGetShareTaskRewards", gameId, userId, taskId)
        from newfish.entity import user_system
        user_system.getShareTaskRewards(userId, taskId)

    @markCmdActionMethod(cmd="task", action="bind_shared_user_button", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetBindSharedUserButton(self, userId, gameId):
        """获取邀请有礼的绑定按钮是否展示以及剩余时间"""
        ftlog.debug("doGetBindSharedUserButton", gameId, userId)
        fish_activity_system.getBindSharedUserButton(userId)

    @markCmdActionMethod(cmd="task", action="bind_shared_user", clientIdVer=0, scope="game", lockParamName="userId")
    def doBindSharedUser(self, userId, gameId, sharedUserId):
        """绑定邀请者(单包使用)"""
        ftlog.debug("doBindSharedUser", gameId, userId, sharedUserId)
        fish_activity_system.bindSharedUser(userId, sharedUserId)

    @markCmdActionMethod(cmd="task", action="get_bind_shared_user_list", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetBindSharedUserList(self, userId, gameId):
        """获取绑定了该玩家的用户信息(单包使用)"""
        ftlog.debug("doGetBindSharedUserList", gameId, userId)
        fish_activity_system.getBindSharedUserInfo(userId)

    @markCmdActionMethod(cmd="task", action="setMainDisplay", clientIdVer=0, scope="game", lockParamName="userId")
    def doSetMainQuestDisplay(self, userId, gameId, clientId, display):
        """设置主线任务是否在渔场显示"""
        ftlog.debug("doSetMainQuestDisplay", userId, gameId, clientId, display)
        main_quest.setMainQuestDisplay(userId, display)

    @markCmdActionMethod(cmd="task", action="mainReward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetMainQuestRewards(self, userId, gameId, clientId, taskId):
        ftlog.debug("doGetMainQuestRewards", userId, gameId, clientId, taskId)
        isIn, roomId, tableId, seatId = util.isInFishTable(userId)
        if isIn:
            mo = MsgPack()
            mo.setCmd("table_call")
            mo.setParam("action", "main_reward")
            mo.setParam("gameId", FISH_GAMEID)
            mo.setParam("clientId", clientId)
            mo.setParam("userId", userId)
            mo.setParam("roomId", roomId)
            mo.setParam("tableId", tableId)
            mo.setParam("seatId", seatId)
            mo.setParam("taskId", taskId)
            router.sendTableServer(mo, roomId)
        else:
            main_quest.getQuestRewards(userId, clientId, taskId)

    @markCmdActionMethod(cmd="task", action="sectionReward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetMainQuestSectionRewards(self, userId, gameId, clientId, sectionId):
        ftlog.debug("doGetMainQuestSectionRewards", userId, gameId, clientId, sectionId)
        # main_quest.getSectionRewards(userId, clientId, sectionId)

    @markCmdActionMethod(cmd="task", action="sectionStarReward", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetMainQuestSectionStarRewards(self, userId, gameId, clientId, sectionId, star):
        """领取章节星级奖励"""
        ftlog.debug("doGetMainQuestSectionStarRewards", userId, gameId, clientId, sectionId, star)
        main_quest.getSectionStarRewards(userId, clientId, sectionId, star)

    @markCmdActionMethod(cmd="activity_fish", action="fishDailyGift", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetFishDailyGift(self, userId, gameId, clientId):
        """
        获取每日礼包
        """
        ftlog.debug("doGetFishDailyGift", userId, gameId)
        daily_gift.doSendGift(userId, clientId)

    @markCmdActionMethod(cmd="activity_fish", action="buyFishDailyGift", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyFishDailyGift(self, userId, gameId, clientId, giftId, buyType, rebateItemId=0):
        """
        购买每日礼包
        """
        ftlog.debug("doBuyFishDailyGift", userId, gameId, giftId, buyType, rebateItemId)
        daily_gift.doBuyGift(userId, clientId, giftId, buyType, rebateItemId)

    @markCmdActionMethod(cmd="game", action="getGrandPrizePool", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetGrandPrizePool(self, userId, gameId, roomId0):
        """
        获取巨奖奖池数据
        """
        ret = GrandPrizePool.getGrandPoolData(roomId0)
        ftlog.debug("doGetGrandPrizePool", userId, gameId, roomId0, ret)
        mo = MsgPack()
        mo.setCmd("getGrandPrizePool")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("poolList", ret)
        record = GrandPrizePool.getRecord()
        if len(record) > 0:
            ret2 = []
            for val in ret:
                ret2.append({"roomId": val["roomId"], "pool": record[-1].get("remainPool", 0) // 2})
            mo.setResult("lastRewardTs", record[-1].get("ts", 0))
            mo.setResult("lastPoolList", ret2)
        else:
            mo.setResult("lastRewardTs", 0)
            mo.setResult("lastPoolList", {})
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="game", action="getGrandPrizeRecord", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetGrandPrizeRecord(self, userId, gameId, roomId0):
        """
        获取巨奖中奖纪录
        """
        ftlog.debug("doGetGrandPrizeRecord", userId, gameId, roomId0)
        ret = GrandPrizePool.getGrandPrizeRecord(roomId0)
        mo = MsgPack()
        mo.setCmd("getGrandPrizeRecord")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("info", ret[::-1])
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="game", action="piggyBankInfo", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetPiggyBankInfo(self, userId, gameId, clientId):
        """
        获取存钱罐数据
        """
        ftlog.debug("doGetPiggyBankInfo", userId, gameId)
        piggy_bank.getPiggyBankInfo(userId, clientId)

    @markCmdActionMethod(cmd="game", action="piggyBankBuy", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyPiggyBank(self, userId, gameId, clientId, productId, buyType):
        """
        购买存钱罐
        """
        ftlog.debug("doBuyPiggyBank", userId, gameId, clientId, productId, buyType)
        piggy_bank.buyPiggyBank(userId, clientId, productId, buyType)

    @markCmdActionMethod(cmd="game", action="piggyBankGet", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetPiggyBankMoney(self, userId, gameId, clientId, productId):
        """
        领取存钱罐
        """
        ftlog.debug("doGetPiggyBankMoney", userId, gameId, clientId, productId)
        piggy_bank.getMoneyFromPiggyBank(userId, clientId, productId)

    @markCmdActionMethod(cmd="game", action="levelRewardsData", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLevelRewardsData(self, userId, gameId):
        """
        获取等级奖励数据
        """
        ftlog.debug("doGetLevelRewardsData", userId, gameId)
        level_rewards.getLevelRewardsData(userId)

    @markCmdActionMethod(cmd="game", action="levelRewards", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLevelRewards(self, userId, gameId, level):
        """
        领取等级奖励
        """
        ftlog.debug("doGetLevelRewards", userId, gameId, level)
        if level > 0:
            level_rewards.getLevelRewards(userId, level)

    @markCmdActionMethod(cmd="game", action="levelFundsData", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLevelFundsData(self, userId, clientId, gameId, gameMode):
        """
        获取成长基金数据
        """
        if ftlog.is_debug():
            ftlog.debug("doGetLevelFundsData", userId, clientId, gameId, gameMode)
        level_funds.getLevelFundsData(userId, clientId, gameMode)

    @markCmdActionMethod(cmd="game", action="levelFundsRewards", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetLevelFundsRewards(self, userId, gameId, clientId, productId, level, rewardType):
        """
        领取成长基金奖励
        """
        ftlog.debug("doGetLevelFundsRewards", userId, gameId, clientId, productId, level, rewardType)
        level_funds.getLevelFundsRewards(userId, clientId, productId, level, rewardType)

    @markCmdActionMethod(cmd="game", action="buyLevelFunds", clientIdVer=0, scope="game", lockParamName="userId")
    def doBuyLevelFunds(self, userId, gameId, clientId, productId, buyType):
        """
        购买成长基金
        """
        ftlog.debug("doBuyLevelFunds", userId, gameId, clientId, productId, buyType)
        level_funds.doBuyLevelFunds(userId, clientId, buyType, productId)

    @markCmdActionMethod(cmd="game", action="grand_prix_info", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetGrandPrixInfo(self, userId, gameId, clientId):
        """
        获取大奖赛信息
        """
        ftlog.debug("doGetGrandPrixInfo", userId, gameId, clientId)
        from newfish.entity import grand_prix
        grand_prix.sendGrandPrixInfo(userId)

    @markCmdActionMethod(cmd="game", action="tower_history", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetTowerHistory(self, userId, gameId, clientId):
        """获取魔塔记录"""
        ftlog.debug("doGetTowerHistory", userId, gameId, clientId)
        from newfish.entity.lotterypool import poseidon_lottery_pool
        historys = poseidon_lottery_pool.getTowerHistory()
        mo = MsgPack()
        mo.setCmd("tower_history")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", userId)
        mo.setResult("history", historys)
        router.sendToUser(mo, userId)

    @markCmdActionMethod(cmd="game", action="moduleRule", clientIdVer=0, scope="game", lockParamName="userId")
    def doGetModuleRule(self, userId, gameId, clientId, module, id):
        """
        获取模块规则文本
        """
        message = MsgPack()
        message.setCmd("moduleRule")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", userId)
        message.setResult("module", module)
        message.setResult("id", id)
        rule = {}
        if module == "activity":
            acConfig = config.getActivityConfigById(id)
            rule = acConfig.get("rule", {})
        elif module == "superboss":
            rule = config.getSuperbossCommonConf().get(str(id), {}).get("rule", {})
        lang = util.getLanguage(userId, clientId)
        ruleTxt = {k: config.getMultiLangTextConf(v, lang) for k, v in rule.iteritems()}
        message.setResult("rule", ruleTxt)
        router.sendToUser(message, userId)