# -*- coding: utf-8 -*-

# Created by xsy on 10th, August 2020

# 纪念币发放

import  freetime.util.log as ftlog
from newfish.entity import util, config, mail_system


RMB_SOUVENIR_RATE = 1


def _triggerUserVipExpChangeEvent(event):
    try:
        rmbs = int(event.toAddExp / 10)
        rewards = [
            {
                "name": config.SOUVENIR_KINDID,
                "count": int(RMB_SOUVENIR_RATE * rmbs)
            }
        ]
        message = config.getMultiLangTextConf("ID_MAIL_SOUVENIR_COIN_MESSAGE", lang=util.getLanguage(event.userId))
        mail_system.sendSystemMail(event.userId, mail_system.MailRewardType.SystemReward, rewards, message)
    except Exception as e:
        ftlog.error("souvenir_coin._triggerUserVipExpChangeEvent error", e,
                    "userId=", event.userId,
                    "toAddExp=", event.toAddExp)


_inited = False


def initialize():
    ftlog.debug("newfish souvenir coin initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from newfish.entity.event import UserVipExpChangeEvent
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(UserVipExpChangeEvent, _triggerUserVipExpChangeEvent)
    ftlog.debug("newfish souvenir coin initialize end")