# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import hashlib

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol.decorator import markHttpHandler, markHttpMethod
from poker.protocol import runhttp
from poker.entity.configure import gdata
from poker.entity.dao import userdata, daobase, userchip
from poker.servers.conn.rpc import onlines
from hall.entity.hallconf import HALL_GAMEID
from hall.entity import hallvip
from hall.servers.common.base_http_checker import BaseHttpMsgChecker
from newfish.entity import config, util, mail_system, weakdata
from newfish.entity.gift import gift_system
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, WeakData, UserData


@markHttpHandler
class FishHttpHandler(BaseHttpMsgChecker):

    def checkCode(self):
        code = ""
        datas = runhttp.getDict()
        if "code" in datas:
            code = datas["code"]
            del datas["code"]

        signStr = util.httpParamsSign(datas)
        if code != signStr:
            return -1, "Verify code error"
        return 0, None
    
    def _check_param_ismgr(self, key, params):
        ismgr = runhttp.getParamInt(key, 0)
        if ismgr == 0 or ismgr == 1:
            return None, ismgr
        return "ERROR of ismgr !" + str(ismgr), None

    def _check_param_msgstr(self, key, params):
        msgstr = runhttp.getParamStr(key, "")
        if msgstr:
            return None, msgstr
        return "ERROR of msgstr !" + str(msgstr), None
    
    def _check_param_scope(self, key, params):
        scope = runhttp.getParamStr(key, "")
        if scope:
            return None, scope
        return "ERROR of scope !" + str(scope), None

    def _check_param_code(self, key, params):
        code = runhttp.getParamStr(key, "")
        if code:
            return None, code
        return "ERROR of code !" + str(code), None

    def _check_param_count(self, key, params):
        count = runhttp.getParamInt(key, "")
        if count or count == 0:
            return None, count
        return "ERROR of count !" + str(count), None

    def _check_param_name(self, key, params):
        name = runhttp.getParamStr(key, "")
        if name:
            return None, name
        return "ERROR of name !" + str(name), None

    def _check_param_hash(self, key, params):
        hash = runhttp.getParamInt(key, "")
        if isinstance(hash, int):
            return None, hash
        return "ERROR of hash !" + str(hash), None

    def _check_param_day(self, key, params):
        day = runhttp.getParamInt(key, "")
        if isinstance(day, int):
            return None, day
        return "ERROR of day !" + str(day), None

    def _check_param_rankType(self, key, params):
        rankType = runhttp.getParamInt(key, "")
        if isinstance(rankType, int):
            return None, rankType
        return "ERROR of rankType !" + str(rankType), None

    def _check_param_productId(self, key, params):
        productId = runhttp.getParamStr(key, "")
        if productId:
            return None, productId
        return "ERROR of productId !" + str(productId), None

    # @markHttpMethod(httppath="/gtest/newfish/sendLed")
    # def doSendLed(self, gameId, msgstr, ismgr, scope):
    #     clientIds = runhttp.getParamStr("clientIds", "")
    #     clientIdsList = []
    #     if clientIds:
    #         clientIdsList = clientIds.split(":")
    #     msg = json.dumps({"text":[{"color":"FFFFFF", "text":msgstr, "gameId":gameId}]})
    #     ftlog.info("sendLed:", gameId, msg, ismgr, scope, clientIdsList)
    #     user_rpc.sendLed(gameId, msg, ismgr, scope, clientIdsList)
    #     return {"result": "ok"}

    @markHttpMethod(httppath="/newfish/v1/user/info")
    def doGetUserInfo(self, userId):
        info = {}
        info["code"] = 0
        level = util.getUserValidCheckLevel(userId)
        if level <= 0:
            info["code"] = 1
        else:
            info["name"] = util.getNickname(userId)
            info["sex"], info["avatar"] = userdata.getAttrs(userId, ["sex", "purl"])
        ftlog.debug("doGetUserInfo->", info)
        return info

    @markHttpMethod(httppath="/gtest/newfish/user")
    def getUserData(self, userId, name, hash):
        ftlog.debug("getUserData->", userId, name, hash)
        if hash:
            return daobase.executeUserCmd(userId, "HGETALL", name)
        else:
            return daobase.executeUserCmd(userId, "GET", name)

    @markHttpMethod(httppath="/gtest/newfish/mix")
    def getMixData(self, name, hash):
        ftlog.debug("getMixData->", name, hash)
        if hash:
            return daobase.executeMixCmd("HGETALL", name)
        else:
            return daobase.executeMixCmd("GET", name)

    @markHttpMethod(httppath="/gtest/newfish/rank")
    def getRankData(self, rankType):
        userId = runhttp.getParamInt("userId", config.ROBOT_MAX_USER_ID)
        ftlog.debug("getRankData->", userId, rankType)
        from newfish.entity.ranking import ranking_system
        return ranking_system.getRankingTabs(userId, config.CLIENTID_ROBOT, rankType, True)

    @markHttpMethod(httppath="/gtest/newfish/reset")
    def doResetData(self, gameId, userId):
        ftlog.debug("doResetData->", gameId, userId)
        isDel = False
        delUserIds = [103155760, 103138308]
        if gdata.mode() == gdata.RUN_MODE_ONLINE:
            if userId in delUserIds:
                isDel = True
        else:
            isDel = True
        if isDel:
            fishDelKeys = [UserData.activity, UserData.achievement, UserData.honor, UserData.gunskin,
                           UserData.gunskin_m, UserData.treasure, UserData.share, UserData.skill,
                           UserData.fishDailyQuest, UserData.fishDailyQuestReward, UserData.fishDailyQuestWeeklyReward,
                           UserData.fishDailyQuestInfo, UserData.fishDailyQuestGroupLv, UserData.prizeWheelData,
                           UserData.levelFundsData, UserData.levelFundsData_m, UserData.piggyBankData,
                           UserData.questType, UserData.newbieUseSkillTimes, UserData.luckyTreeData,
                           UserData.buyProductCount,UserData.buyExchangeProduct, UserData.prizeWheelData_m,
                           UserData.gunEffect_m, UserData.gamedata, UserData.mainQuest]
            hallDelKeys = ["gamedata:%d:%d", "item2:%d:%d"]
            weakDelKeys = ["weak:day:1st:44", "weak:day:1st:9999", "weak:day:fish:44", "weak:week:fish:44"]
            for keyName in fishDelKeys:
                daobase.executeUserCmd(userId, "DEL", keyName % (FISH_GAMEID, userId))
            for keyName in hallDelKeys:
                daobase.executeUserCmd(userId, "DEL", keyName % (HALL_GAMEID, userId))
            for keyName in weakDelKeys:
                daobase.executeUserCmd(userId, "DEL", "%s:%s" % (keyName, userId))
            userchip.incrChip(userId, FISH_GAMEID, -userchip.getChip(userId), 0, "BI_NFISH_BUY_ITEM_CONSUME", 0, util.getClientId(userId))
            userchip.incrCoupon(userId, FISH_GAMEID, -userchip.getCoupon(userId), 0, "BI_NFISH_BUY_ITEM_CONSUME", 0, util.getClientId(userId))
            userchip.incrDiamond(userId, FISH_GAMEID, -userchip.getDiamond(userId), 0, "BI_NFISH_BUY_ITEM_CONSUME", 0, util.getClientId(userId))
            return userId

    @markHttpMethod(httppath="/newfish/v1/wechat/checkin")
    def doWechatCheckin(self, userId, day):
        """
        微信公众号签到接口
        """
        ftlog.info("doWechatCheckin", userId, day)
        level = util.getUserValidCheckLevel(userId)
        data = {}
        if level:
            wechatCheckin = weakdata.getDayFishData(userId, WeakData.wechatCheckin)
            if wechatCheckin:
                data["info"] = u"签到失败，您已签到"
                data["code"] = 1
            else:
                rewards = config.getCommonValueByKey("wechatCheckinRewards")[day - 1]
                # message = u"恭喜您在公众号完成每日签到，现给您送上签到礼包一份~祝您游戏愉快！"
                lang = util.getLanguage(userId)
                message = config.getMultiLangTextConf("ID_PUBLIC_ACCOUNT_SIGNIN_GIFT", lang=lang)
                weakdata.setDayFishData(userId, WeakData.wechatCheckin, 1)
                mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, [rewards], message)
                data["info"] = message
                data["code"] = 0
        else:
            data["info"] = u"签到失败，没有用户数据"
            data["code"] = 2
        return data

    @markHttpMethod(httppath="/newfish/v1/wechat/getProduct")
    def doWechatGetProduct(self, userId):
        """
        微信公众号支付接口（微信登录渠道）获取商品信息
        """
        ftlog.info("doWechatGetProduct", userId)
        allProduct = {}
        level = util.getUserLevel(userId)
        vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        if level <= 0:
            code = 1
        elif (level < 12 and vipLevel < 5) or util.isVersionLimit(userId) or util.isLocationLimit(userId):
            code = 2
        else:
            code = 0
            allProduct = self.getAllProduct(userId)
        allProduct["code"] = code
        return allProduct

    @markHttpMethod(httppath="/newfish/v1/public/getProduct")
    def doPublicGetProduct(self, userId):
        """
        微信公众号支付接口（全渠道）获取商品信息
        """
        ftlog.info("doPublicGetProduct", userId)
        allProduct = {}
        level = util.getUserValidCheckLevel(userId)
        if level <= 0:
            code = 1
        else:
            code = 0
            allProduct = self.getAllProduct(userId)
        allProduct["code"] = code
        return allProduct

    def getAllProduct(self, userId):
        """
        获得所有商品
        """
        allProduct = {}
        clientId = util.getClientId(userId)
        # coinStoreTab = store.getCoinStore(userId, clientId)
        # pearlStoreTab = store.getPearlStore(userId, clientId)
        # diamondStoreTab = store.getDiamondStore(userId, clientId)
        from newfish.entity.store import DiamondStoreShop, StoreTabType
        diamondStoreTab = DiamondStoreShop(userId, clientId, StoreTabType.STT_DIAMOND).getStore()
        # coinProducts = []
        # pearlProducts = []
        diamondProducts = []
        giftProducts = []
        # for item in coinStoreTab["items"]:
        #     product = self.buildProduct(item, coinStoreTab["subStore"])
        #     coinProducts.append(product)
        # for item in pearlStoreTab["items"]:
        #     product = self.buildProduct(item, pearlStoreTab["subStore"])
        #     pearlProducts.append(product)
        for item in diamondStoreTab["items"]:
            product = self.buildProduct(item, diamondStoreTab["subStore"])
            diamondProducts.append(product)
        seriesGift, bankruptGift, monthCardGift = gift_system.getWxFishGift(userId)
        if seriesGift:
            for gift in seriesGift:
                product = self.buildProduct(gift, "gift")
                giftProducts.append(product)
        if isinstance(monthCardGift, list):
            for gift in monthCardGift:
                product = self.buildProduct(gift, "gift")
                giftProducts.append(product)
        elif monthCardGift:
            product = self.buildProduct(monthCardGift, "gift")
            giftProducts.append(product)
        # allProduct["coin"] = coinProducts
        # allProduct["pearl"] = pearlProducts
        allProduct["diamond"] = diamondProducts
        allProduct["gift"] = giftProducts
        # 清理sdk支付后的自动购买数据.
        key = GameData.autoBuyAfterSDKPay % (FISH_GAMEID, userId)
        daobase.executeUserCmd(userId, "DEL", key)
        return allProduct

    def buildProduct(self, item, subStore="coin"):
        """
        构建商品详情
        """
        product = {}
        if subStore in ["coin", "pearl", "diamond"]:
            product["id"] = item["id"]
            product["name"] = item["name"]
            product["price"] = item["price"]
            product["desc"] = item["addition"]
        elif subStore == "gift":
            product["id"] = item["productId"]
            product["name"] = item["giftName"]
            product["price"] = item["price_direct"]             # item["discountPrice"]
            product["desc"] = ""
        return product

    @markHttpMethod(httppath="/newfish/v1/wechat/getCredit")
    def doGetCredit(self, userId):
        """
        微信公众号积分商城接口（获取积分商城数据）
        """
        creditStoreConf = config.getCreditStoreConf()
        mo = MsgPack()
        mo.setResult("userId", userId)
        mo.setResult("vipLevel", hallvip.userVipSystem.getUserVip(userId).vipLevel.level)
        mo.setResult("creditStore", creditStoreConf.get("creditStore", []))
        mo.setResult("creditTask", creditStoreConf.get("creditTask", []))
        mo.setResult("code", 0)
        return mo

    @markHttpMethod(httppath="/newfish/v1/wechat/exchangeCredit")
    def doExchangeCredit(self, userId, productId):
        """
        微信公众号积分商城接口（积分兑换物品发货）
        """
        mo = MsgPack()
        code, _ = self.checkCode()
        if code == 0:
            code, credit = self._exchangeCredit(userId, productId)
            if code == 0 and credit > 0:
                mo.setResult("productId", productId)
                mo.setResult("credit", credit)
        mo.setResult("code", code)
        ftlog.info("doExchangeCredit", mo)
        return mo

    def _exchangeCredit(self, userId, productId):
        code, credit = 1, 0
        vipLevel = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
        creditStoreConf = config.getCreditStoreConf()
        lang = util.getLanguage(userId)
        for creditStore in creditStoreConf.get("creditStore", []):
            if creditStore.get("productId") == productId and creditStore["credit"] > 0:
                if vipLevel >= creditStore["limitVipLevel"]:
                    rewards = [{"name": creditStore["kindId"], "count": creditStore["count"]}]
                    # message = u"恭喜您在公众号会员积分商城成功兑换%s，请查收附件！" % creditStore["name"]
                    message = config.getMultiLangTextConf("ID_PUBLIC_ACCOUNT_EXCHANGE_REWARD_MSG", lang=lang) % creditStore["name"]
                    title = config.getMultiLangTextConf("ID_MAIL_TITLE_SYSTEM_INFO", lang=lang)
                    mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, rewards, message, title) # 系统邮件
                    code, credit = 0, creditStore["credit"]
                    break
                else:
                    code = 2
        return code, credit

    @markHttpMethod(httppath="/newfish/v1/h5/getProduct")
    def doH5GetProduct(self, userId):
        return self.getH5AllProduct(userId)

    def getH5AllProduct(self, userId):
        """
        H5支付接口（全渠道）获取商品信息
        """
        allProduct = {}
        allProduct["userId"] = userId
        level = util.getUserValidCheckLevel(userId)
        if level <= 0:
            code = 1
        else:
            code = 0
        allProduct["retcode"] = code
        if code == 0:
            allProduct["nickName"] = util.getNickname(userId)
            allProduct["headImg"] = userdata.getAttr(userId, "purl")
            clientId = util.getClientId(userId)
            diamondProducts = []
            giftProducts = []
            # 钻石商品
            from newfish.entity.store import DiamondStoreShop, StoreTabType
            diamondStoreTab = DiamondStoreShop(userId, clientId, StoreTabType.STT_DIAMOND).getStore()
            for item in diamondStoreTab["items"]:
                diamondProducts.append(item)
            # 礼包商品
            seriesGift, bankruptGift, monthCardGift = gift_system.getWxFishGift(userId)
            if seriesGift:
                for gift in seriesGift:
                    giftProducts.append(gift)
            if isinstance(monthCardGift, list):
                for gift in monthCardGift:
                    giftProducts.append(gift)
            elif monthCardGift:
                giftProducts.append(monthCardGift)
            groups = [
                ["diamond", u"钻石", diamondProducts],
                ["gift", u"礼包", giftProducts]
            ]
            for i, group in enumerate(groups):
                allProduct["group_%s" % (i + 1)] = self.buildH5Group(group)
        return allProduct

    def buildH5Group(self, group):
        groupInfo = {}
        groupInfo["name"] = group[1]
        prod_item = []
        for item in group[2]:
            prod_item.append(self.buildH5Product(item, group[0]))
        groupInfo["prod_item"] = prod_item
        return groupInfo

    def buildH5Product(self, item, storeName):
        product = {}
        if storeName == "diamond":
            product["prod_name"] = item["name"]
            product["prod_id"] = item["id"]
            product["prod_prize"] = item["price"]
            product["prod_img"] = ""
        elif storeName == "gift":
            product["prod_name"] = item["giftName"]
            product["prod_id"] = item["productId"]
            product["prod_prize"] = item["price_direct"]
            product["prod_img"] = ""
        return product

    @markHttpMethod(httppath='/newfish/v1/user/forcelogout')
    def doForceLogOut(self):
        """
        玩家强制下线
        """
        userId = runhttp.getParamStr("user_id")
        try:
            if userId.find(':') != -1:
                userId = int(userId.split(':')[0])
            else:
                userId = int(userId)
        except:
            userId = config.ROBOT_MAX_USER_ID
        ts = runhttp.getParamInt('ts', 0)
        signRequest = runhttp.getParamStr('sign', "")

        params = {"user_id": userId, "access_id": "xxbyforcelogout", "sign_type": "sha256", "secret_type": "forever", "ts": ts}
        paramsList = sorted([("%s=%s" % (k, v)) for k, v in params.iteritems()])
        str = '&'.join(paramsList) + ":9kQLYmnEaTYjhubOo2IclCvxxwBXX0ST"
        sign = hashlib.sha256(str).hexdigest().lower()
        if ftlog.is_debug():
            ftlog.debug("doForceLogOut, args =", runhttp.getRequest().args, "sign =", sign)
        if sign != signRequest:
            ftlog.error("doForceLogOut, error, userId =", userId, "ts =", ts, "args =", runhttp.getRequest().args)
            return
        logoutmsg = ""
        userdata.clearUserCache(userId)
        onlines.forceLogOut(userId, logoutmsg)
        mo = MsgPack()
        mo.setCmd('forcelogout')
        mo.setResult('ok', 1)
        ftlog.info("doForceLogOut, userId =", userId, "ts =", ts, "mo =", mo)
        return mo