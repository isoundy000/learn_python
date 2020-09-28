# -*- coding=utf-8 -*-
"""
更版奖励
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/6/24


import json

import freetime.util.log as ftlog
from poker.entity.dao import gamedata
from hall.entity import hallvip
from newfish.entity import mail_system, config, util
from newfish.entity.redis_keys import GameData


def sendUpdateRewards(userId, clientId):
    """
    发放更服奖励
    """
    conf = config.getUpdateVerRewardsConf()
    updateClientVer = conf.get("version")
    if updateClientVer is None:
        return
    clientVersion = gamedata.getGameAttr(userId, config.FISH_GAMEID, GameData.clientVersion)
    if clientVersion == updateClientVer:
        updateVerRewards = gamedata.getGameAttrJson(userId, config.FISH_GAMEID, GameData.updateVerRewards, [])
        if clientVersion not in updateVerRewards:
            updateVerRewards.append(clientVersion)
            gamedata.setGameAttr(userId, config.FISH_GAMEID, GameData.updateVerRewards, json.dumps(updateVerRewards))
            rewardTye = conf.get("type", 1)
            vipLv = hallvip.userVipSystem.getUserVip(userId).vipLevel.level
            #message = conf.get("msg", "")# u"您的版本更新已完成，以下是更新奖励，祝您游戏愉快！"
            lang = util.getLanguage(userId, clientId)
            message = config.getMultiLangTextConf(conf.get("msg", ""), lang=lang)
            rewards = conf.get("rewards", {}).get(str(vipLv), {}).get(str(rewardTye), [])
            if rewards:
                mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemCompensate, rewards,
                                           message, config.getMultiLangTextConf("ID_MAIL_VERSION_UPDATE_REWARDS", lang=lang))
            if ftlog.is_debug():
                ftlog.debug("sendUpdateRewards, userId =", userId, "vip =", vipLv, "type =", rewardTye,
                            "rewards =", rewards, "updateVer =", updateClientVer, "updateVerRewards =", updateVerRewards)
