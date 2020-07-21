# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/12/22.

使用方法：
找到需要热更新的进程
./game.sh -a findPid -m CT9999*
执行热更新命令
./game.sh -a hotfix -f 文件绝对路径 -s 热更进程
"""

# 给测试账号增加金币
# from poker.entity.dao import userchip
# from newfish.entity.config import FISH_GAMEID

# userIds = [100000163, 100000020, 100000021]
#
# def _main():
#     almsCoin = 5000000
#     for userId in userIds:
#         userchip.incrChip(userId, FISH_GAMEID, almsCoin, 0, "BI_NFISH_NEW_USER_REWARDS", 0, "H5_5.1_weixin.weixin.0-hall44.weixin.tyjdby")
#
# from freetime.core.timer import FTLoopTimer
# FTLoopTimer(0.1, 0, _main).start()

# 给丢单玩家补礼包
from newfish.entity import mail_system

def _main():
    userId = 100220502
    rewards = [{"name": 101, "count": 6560000}]
    message = u"您好，由于我们的问题给您造成不便，非常抱歉。现在补偿您一份小礼物，请您注意查收。祝您游戏愉快~"
    # message = u"您好，因为今天您发现并提供了游戏中出现的问题，现在送您一份小礼物哦~非常感谢您对我们游戏的关注。祝您游戏愉快~ "
    mail_system.sendSystemMail(userId, mail_system.MailType.SystemCompensate, rewards, message)

    from newfish.entity.gift import gift_system
    gift_system.doBuyFishGift(100260920, 7311)
    gift_system.doBuyFishGift(100268749, 7211)
    gift_system.doBuyFishGift(100185545, 7311)

from freetime.core.timer import FTLoopTimer

FTLoopTimer(0.1, 0, _main).start()