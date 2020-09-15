# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

from newfish.entity import config


class FishTableConf(object):
    """
    渔场桌子内的配置
    """
    def __init__(self, datas):
        self.datas = datas
        fishGroupsName = self.datas.get("fishGroupsName")
        if fishGroupsName:
            self.datas["fishGroups"] = config.getFishGroups(fishGroupsName, self.datas.get("gameMode", 0))
        self.allGroupIds = self.fishGroups.keys()           # 该场次可使用的所有鱼阵
        self.allNormalGroupIds = []                         # 普通鱼
        self.allBossGroupIds = {}                           # boss鱼阵
        self.allCallGroupIds = []                           # 召唤鱼阵
        self.allTideGroupIds = []                           # 普通鱼潮
        self.allActTideGroupIds = []                        # 活动鱼潮1
        self.allActTide2GroupIds = []                       # 活动鱼潮2
        self.allChestGroupIds = []                          # 金币宝箱
        self.allCouponGroupIds = {}                         # 奖券鱼
        self.allActivityGroupIds = {}                       # 活动鱼（海螺）
        self.allRobberyBossGroupIds = []                    # 招财模式Boss
        self.allBufferGroupIds = []                         # 回馈赛Buffer
        self.allMultipleGroupIds = {}                       # 回馈赛随机倍率鱼
        self.allShareGroupIds = {}                          # 所有分享宝箱鱼
        self.allRainbowGroupIds = []                        # 所有的彩虹鱼鱼群
        self.allTerrorGroupIds = {}                         # terror鱼初始化
        self.allAutofillGroupIds = {}                       # 自动填充鱼
        self.allAutofillShoalGroupIds = {}                  # 自动填充鱼群
        self.allGrandPrixGroupIds = {}                      # 大奖所有鱼群
        self.allSuperBossGroupIds = {}                      # 超级Boss正常鱼群
        self.allSuperBossBornGroupIds = {}                  # 超级Boss出生鱼群
        self.allSuperBossFastMoveGroupIds = {}              # 没有保护罩的超级Boss
        self.allPlatterGroupIds = {}                        # 大盘鱼初始化
        self.allMiniGameGroupIds = {}                       # 小游戏Boss（美人鱼）

        for key in self.allGroupIds:
            fishType = key.split("_")[1]
            if key.startswith("group_"):
                self.allNormalGroupIds.append(key)
            elif key.startswith("boss_"):
                self.allBossGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("call_"):
                self.allCallGroupIds.append(key)
            elif key.startswith("tide_"):
                self.allTideGroupIds.append(key)
            elif key.startswith("atide_"):
                self.allActTideGroupIds.append(key)
            elif key.startswith("atide2_"):
                self.allActTide2GroupIds.append(key)
            elif key.startswith("chest_"):
                self.allChestGroupIds.append(key)
            elif key.startswith("rboss_"):
                self.allRobberyBossGroupIds.append(key)
            elif key.startswith("coupon_") or key.startswith("red_") or key.startswith("random_"):
                self.allCouponGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("activity_"):
                self.allActivityGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("buffer_"):
                self.allBufferGroupIds.append(key)
            elif key.startswith("multiple_"):
                self.allMultipleGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("share_"):
                self.allShareGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("rainbow_"):
                self.allRainbowGroupIds.append(key)
            elif key.startswith("terror_"):
                self.allTerrorGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("autofill_"):
                self.allAutofillGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("shoal_"):
                self.allAutofillShoalGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("grandprix_"):
                self.allGrandPrixGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("superboss_"):
                self.allSuperBossGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("superbossborn_"):
                self.allSuperBossBornGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("superbossfast_"):
                self.allSuperBossFastMoveGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("platter_"):
                self.allPlatterGroupIds.setdefault(int(fishType), []).append(key)
            elif key.startswith("minigame_"):
                self.allMiniGameGroupIds.setdefault(int(fishType), []).append(key)

    def getAllDatas(self):
        return self.datas

    @property
    def name(self):
        """
        渔场名
        """
        return self.datas.get("name", "")       # ID_ROOM_NAME_44402

    @property
    def title(self):
        """
        渔场标题（用于led显示）
        """
        return self.datas.get("title", "") or self.name     # ID_ROOM_NAME_44402

    @property
    def fishGroups(self):
        """
        该场次可使用的所有鱼阵
        """
        return self.datas.get("fishGroups", {})

    @property
    def fishPool(self):
        """
        渔场编号
        """
        return self.datas.get("fishPool", 44001)

    @property
    def bullets(self):
        """
        场次可购买弹药数列表
        """
        return self.datas.get("bullets", [])        # [2000, 5000, 10000, 50000]

    @property
    def multiple(self):
        """
        场次倍率
        """
        return self.datas.get("multiple", 1)

    @property
    def lack(self):
        """
        子弹数不足时自动购买
        """
        return self.datas.get("lack", 50)

    @property
    def showLevel(self):
        """
        客户端解锁显示等级
        """
        return self.datas.get("showLevel", 0)

    @property
    def minUserLevel(self):
        """
        最小准入用户等级
        """
        return self.datas.get("minLevel", 0)

    @property
    def maxUserLevel(self):
        """
        最大准入用户等级
        """
        return self.datas.get("maxLevel", 0)

    @property
    def expLimitLevel(self):
        """
        经验值增加上限等级
        """
        return self.datas.get("expLimitLevel", 0)

    @property
    def minCoin(self):
        """
        最小准入金币
        """
        return self.datas.get("minCoin", 0)

    @property
    def maxCoin(self):
        """
        最大准入金币
        """
        return self.datas.get("maxCoin", 0)

    @property
    def minGunLevel(self):
        """
        最小火炮等级/千炮倍率
        """
        return self.datas.get("minGunLevel", 0)

    @property
    def maxGunLevel(self):
        """
        最大火炮等级/千炮倍率
        """
        return self.datas.get("maxGunLevel", 0)

    @property
    def maxSkillLevel(self):
        """
        最大技能等级
        """
        return self.datas.get("maxSkillLevel", 5)

    @property
    def usableBullets(self):
        """
        可使用招财珠
        """
        return self.datas.get("usableBullets", [])

    @property
    def maxGunLevelLimit(self):
        """
        招财模式下招财珠对应的最大火炮等级
        """
        return self.datas.get("maxGunLevelLimit", {})

    @property
    def playTime(self):
        """
        招财模式游戏时间
        """
        return self.datas.get("playTime", 300)

    @property
    def timeLimit(self):
        """
        场次开放时间
        """
        return self.datas.get("timeLimit", [])

    @property
    def isMatch(self):
        """
        是否为比赛
        """
        return self.datas.get("isMatch", 0)

    @property
    def typeName(self):
        """
        渔场类型
        """
        return self.datas.get("typeName", config.FISH_NORMAL)

    @property
    def gameMode(self):
        """
        游戏模式
        """
        return self.datas.get("gameMode", 0)

    @property
    def hasRobot(self):
        """
        是否存在机器人
        """
        return self.datas.get("hasrobot", 0)

    @property
    def matchConf(self):
        """
        比赛配置
        """
        return self.datas.get("matchConf", {})

    @property
    def playingTime(self):
        """
        比赛时间
        """
        return self.datas.get("matchConf", {}).get("playingTime", 300)

    @property
    def matchType(self):
        """
        比赛类型
        """
        return self.datas.get("matchConf", {}).get("type", 0)

    @property
    def coinShortage(self):
        """
        破产线
        """
        return self.datas.get("coinShortage", -1)

    @property
    def minWaveRadix(self):
        """
        最小波动基数
        """
        return self.datas.get("minWaveRadix", -1)

    @property
    def maxWaveRadix(self):
        """
        最大波动基数
        """
        return self.datas.get("maxWaveRadix", -1)

    @property
    def waveRadixRate(self):
        """
        波动基数衰减比例
        """
        return self.datas.get("waveRadixRate", -1)

    @property
    def bankruptcyCoin(self):
        """
        破产线
        """
        return self.datas.get("bankruptcyCoin", -1)

    @property
    def lossCoin(self):
        """
        亏损返奖中的亏损线
        """
        return self.datas.get("lossRebate", {}).get("lossCoin", 0)

    @property
    def rebateCoin(self):
        """
        亏损返奖中的充值奖池返还金币
        """
        return self.datas.get("lossRebate", {}).get("rebateCoin", 0)

    @property
    def taskSystemType(self):
        """
        使用的任务系统
        """
        return self.datas.get("taskSystemType", [])

    @property
    def taskLoopInterval(self):
        """
        一个比赛的轮回
        """
        return self.datas.get("taskLoopInterval", 900)

    @property
    def bonusTaskInterval(self):
        """
        奖金赛开赛时间
        """
        return self.datas.get("bonusTaskInterval", 720)

    @property
    def minBonus(self):
        """
        奖金赛
        """
        return self.datas.get("minBonus", 0)

    @property
    def systemBonus(self):
        """
        系统奖金赛
        """
        return self.datas.get("systemBonus", 0)

    @property
    def trialMode(self):
        return self.datas.get("trialMode", 0)

    @property
    def allBets(self):
        """
        海皇来袭中的充能金币档位
        """
        return self.datas.get("towerConf", {}).get("allBets", [])

    @property
    def maxBet(self):
        """
        海皇来袭中的充能金币档位
        """
        return self.datas.get("towerConf", {}).get("maxBet", 5000000)

    @property
    def skill_item(self):
        """
        道具的技能
        """
        return self.datas.get("skill_item", {})