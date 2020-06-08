#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
import random
import json
from collections import OrderedDict
from copy import deepcopy

from freetime.util import log as ftlog
from poker.entity.configure import configure, gdata
from poker.entity.events import tyeventbus
from poker.entity.events.tyevent import EventConfigure
from hall.entity import hallitem, hallconf
from newfish import resource


# 游戏ID
FISH_GAMEID = 44
# 系统默认clientId
CLIENTID_ROBOT = "H5_5.1_weixin.weixin.0-hall44.weixin.tyjdby"
# 系统默认clientVersion
CLIENT_VERSION_ROBOT = 3.97
# 机器人userId上限
ROBOT_MAX_USER_ID = 10000
# 微信AppId
WX_APPID = "wx30efe34580243475"
# 微信公众平台AppId
WX_MP_APPID = "wxfdc57a92b5a5d72f"
# 服务器版本号
SERVER_VERSION = int(time.strftime("%Y%m%d", time.localtime(time.time())))
# 金币
CHIP_KINDID = 101
# 钻石
DIAMOND_KINDID = 102
# 红宝石
RUBY_KINDID = 13543
# 红包券
COUPON_KINDID = 103
# 微信红包
REDPACKET_KINDID = 104
# 珍珠
PEARL_KINDID = 1137
# 海星
STARFISH_KINDID = 3106
# 海星抽奖券
STARFISH_TICKET_KINDID = 1380
# 代购券
VOUCHER_KINDID = 1426
# 青铜招财珠
BRONZE_BULLET_KINDID = 1301
# 白银招财珠
SILVER_BULLET_KINDID = 1193
# 黄金招财珠
GOLD_BULLET_KINDID = 1194
# 紫水晶
PURPLE_CRYSTAL_KINDID = 1429
# 黄水晶
YELLOW_CRYSTAL_KINDID = 1430
# 五彩水晶
COLOR_CRYSTAL_KINDID = 1431
# 魔晶
MAGIC_CRYSTAL_KINDID = 13761
# 改名卡
RENAME_KINDID = 14070
# 招财珠
BULLET_KINDID = [BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID]
# 招财珠-金币价值
BULLET_KINDIDS = {
    BRONZE_BULLET_KINDID: 10000,
    SILVER_BULLET_KINDID: 100000,
    GOLD_BULLET_KINDID: 500000
}
# 金银招财珠转换成青铜招财珠价值
BULLET_VALUE = {
    SILVER_BULLET_KINDID: 10,
    GOLD_BULLET_KINDID: 50
}
# 试玩青铜招财珠
TM_BRONZE_BULLET_KINDID = 1495
# 试玩白银招财珠
TM_SILVER_BULLET_KINDID = 1496
# 试玩黄金招财珠
TM_GOLD_BULLET_KINDID = 1497
# 试玩招财珠-金币价值
TM_BULLET_KINDIDS = {
    TM_BRONZE_BULLET_KINDID: 10000,
    TM_SILVER_BULLET_KINDID: 100000,
    TM_GOLD_BULLET_KINDID: 500000
}
# 技能刷新冷却
SKILLCD_KINDID = 1408
# 红包鱼配置
RED_KINDIDS = {1: 2057, 5: 2061, 10: 2048, 20: 2062, 50: 2059, 100: 2050}
# 实物道具ID对应金额
RED_AMOUNTS = {
    4141: 10,
    4142: 30,
    4143: 50,
    4144: 100,
    4178: 1,
    4180: 5,
    4230: 10,
    4232: 50,
    4233: 100,
    4369: 500
}

# 月卡
MONTH_CARD_KINDID = 1452
# 永久月卡
PERMANENT_MONTH_CARD_KINDID = 14009
# 竞赛活动积分
DEER_COMP_ACT_POINT_KINDID = 13962
SHIP_COMP_ACT_POINT_KINDID = 14048
DRAGON_COMP_ACT_POINT_KINDID = 14050
COMP_ACT_POINT_KINDID_LIST = [DEER_COMP_ACT_POINT_KINDID, SHIP_COMP_ACT_POINT_KINDID, DRAGON_COMP_ACT_POINT_KINDID]

# 海皇来袭冰塔
ICE_TOWERID = 1
# 海皇来袭火塔
FIRE_TOWERID = 2
# 海皇来袭电塔
ELEC_TOWERID = 3
# 海皇来袭所有魔塔
TOWERIDS = [ICE_TOWERID, FIRE_TOWERID, ELEC_TOWERID]

# -------------------------

# 9999下的排行榜ID
RANK_STAR = "110044001"
RANK_BULLET = "110044002"
RANK_DAY_LUCKY = "110044003"
RANK_SEVEN_LUCKY = "110044004"
RANK_ROBBERY_DAY_WIN = "110044006"
RANK_ROBBERY_SEVEN_WIN = "110044007"
RANK_THOUSAND_RED_REWARD = "110044005"
RANK_MATCH_XXJR = "110044009"
RANK_MATCH_SSLY = "110044010"
RANK_MATCH_HLJJ = "110044011"
RANK_MATCH_WZZB = "110044012"
RANK_SLOT_MACHINE = "110044013"
RANK_MONEY_TREE = "110044014"
RANK_GRAND_PRIX = "110044015"
RANK_GRAND_PRIX_WEEK = "110044016"
RANK_PROFIT_COIN = "110044017"
RANK_FESTIVAL_TURNTABLE = "110044018"
RANK_MAGIC_CRYSTAL = "110044019"
RANK_COLLECT_ITEM = "110044020"
RANK_POSEIDON_DAY_WIN = "110044021"
RANK_POSEIDON_SEVEN_WIN = "110044022"
RANK_COMPETITION_T1 = "110044023"
RANK_COMPETITION_T2 = "110044024"
RANK_COMPETITION_T3 = "110044025"
RANK_COMPETITION_T4 = "110044026"
RANK_COMPETITION_T5 = "110044027"
RANK_COMPETITION = "110044028"
RANK_SBOSS_BOX = "110044029"
RANK_SBOSS_OCTOPUS = "110044030"
RANK_SBOSS_QUEEN = "110044031"
RANK_SBOSS_DRAGON = "110044032"


# 普通渔场
FISH_NORMAL = "fish_normal"
# 回馈赛渔场
FISH_TIME_MATCH = "fish_time_match"
# 渔友竞技渔场
FISH_FIGHT = "fish_fight"
# 招财模式渔场
FISH_ROBBERY = "fish_robbery"
# 好友模式渔场
FISH_FRIEND = "fish_friend"
# 新手(万元红包)渔场
FISH_NEWBIE = "fish_newbie"
# 定时积分赛渔场
FISH_TIME_POINT_MATCH = "fish_time_point_match"
# 大奖赛渔场
FISH_GRAND_PRIX = "fish_grand_prix"
# 海皇来袭
FISH_POSEIDON = "fish_poseidon"
# 千炮模式渔场
FISH_MULTIPLE = "fish_multiple"

# 快速开始自动分配房间类型
QUICK_START_ROOM_TYPE = (FISH_NEWBIE, FISH_NORMAL, FISH_FRIEND)
# 普通房间类型
NORMAL_ROOM_TYPE = (FISH_NEWBIE, FISH_NORMAL, FISH_FRIEND, FISH_GRAND_PRIX, FISH_POSEIDON, FISH_MULTIPLE)
# 使用动态曲线的房间
DYNAMIC_ODDS_ROOM_TYPE = (FISH_NEWBIE, FISH_NORMAL, FISH_FRIEND, FISH_POSEIDON)
# 使用充值奖池房间类型
RECHARGE_BONUS_ROOM_TYPE = (FISH_NEWBIE, FISH_NORMAL, FISH_FRIEND, FISH_GRAND_PRIX, FISH_POSEIDON)

# 购买类型
BT_COIN = "coin"
BT_PEARL = "pearl"
BT_DIAMOND = "diamond"
BT_COUPON = "coupon"
BT_DIRECT = "direct"
BT_VOUCHER = "voucher"
BT_RUBY = "ruby"

# 千炮游戏模式
GOLDEN_COIN = 0                 # 金币模式
GOLDEN_RING = 1                 # 金环模式

# 千炮游戏模式列表
MULTIPLE_MODES_LIST = [GOLDEN_COIN, GOLDEN_RING]

# 游戏玩法
CLASSIC_MODE = 0                # 经典玩法
MULTIPLE_MODE = 1               # 千炮玩法

# 游戏玩法列表
GAME_MODES = [CLASSIC_MODE, MULTIPLE_MODE]

# 游戏配置数据
defaultIntClientId = 0
sceneGroupConf = {}             # 加载渔场鱼阵配置
sceneGroupConf_m = {}
groupsConf = {}                 # 鱼阵配置
groupsConf_m = {}               # 千炮鱼阵配置
weaponConf = {}
weaponConf_m = {}
weaponPowerRateConf = {}
minWeaponId = 0
minWeaponId_m = 0
fishConf = {}
fishConf_m = {}
matchFishConf = {}
dropConf = {}
storeConf = {}
exchangeStoreConf = {}
ulevelConf = {}
userLevelConf = {}
cmpttTaskConf = {}
ncmpttTaskConf = {}
bonusTaskConf = {}
guideTaskConf = {}
publicConf = {}
checkinConf = {}
skillConf = {}
skillGradeConf = {}
skillStarConf = {}
skillGradeConf_m = {}
skillStarConf_m = {}
chestConf = {}
chestDropConf = {}
mainQuestConf = {}
dailyQuestConf = {}
dailyQuestsByTypeConf = {}
dailyQuestRewardConf = {}
dailyQuestRewardFinishedStars = {}
expressionConf = {}
probabilityConf = {}
dynamicOddsConf = {}
lotteryPoolConf = {}
giftConf = {}
giftAbcTestConf = {}
activityConf = {}
catchDropConf = {}
vipConf = {}
fixedMultipleFishConf = {}
rankRewardConf = {}
bonusGameConf = {}
callMultipleFishConf = {}
matchMultipleFishConf = {}
achievementConf = {}
itemConf = {}
honorConf = {}
robberyConf = {}
commonConf = {}
playerBufferConf = {}
robotConf = {}
randomMultipleFishConf = {}
gunTypeConf = {}
gunTypeConf_m = {}
gunLevelConf = {}
gunLevelConf_m = {}
gunMultipleConf = {}
tableTaskConf = {}
inviteTaskConf = {}
rechargePoolConf = {}
shareConf = {}
flyPigRewardConf = {}
starfishRouletteConf = {}
surpassTargetConf = {}
specialItemConf = {}
multiLangTextConf = {}
reportFishCBConf = {}
idCardAreaConf = {}
grandPrizeConf = {}
piggyBankConf = {}
treasureConf = {}
buyTypeConf = {}
timeLimitedStoreConf = {}
levelRewardsConf = {}
updateVerRewardsConf = {}
itemMonitorConf = {}
prizeWheelConf = {}
slotMachineConf = {}
statisPropConf = {}
moneyTreeConf = {}
cannedFishConf = {}
creditStoreConf = {}
levelFundsConf = {}
levelFundsConf_m = {}
superEggsConf = {}
supplyBoxConf = {}
grandPrixConf = {}
festivalTurntableConf = {}
grandPrixPrizeWheelConf = {}
superbossExchangeConf = {}
superbossMinigameConf = {}
superbossCommonConf = {}
collectItemConf = {}
poseidonConf = {}
bigPrizeConf = {}
compActConf = {}
newbie7DaysGiftConf = {}
lotteryTicketConf = {}
passCardConf = {}
skillCompenConf = {}
abTestConf = {}
returnerMissionConf = {}
miniGameConf = {}
miniGameLevelMap = {}
luckyTreeConf = {}
superbossPowerConf = {}
levelPrizeWheelConf = {}


def getGameConf(key, defaultValue=None, intClientidNum=0):
    """
    获取游戏配置
    """
    defaultValue = defaultValue or {}
    return deepcopy(configure.getGameJson(FISH_GAMEID, key, defaultValue, intClientidNum))


def loadGroupsConf():
    """
    加载所有鱼阵
    """
    global groupsConf, groupsConf_m
    groupsConf = rocopy(resource.getGroupConfig())
    groupsConf_m = rocopy(resource.getGroupConfig(1))


def loadSceneGroupConf():
    """
    加载渔场鱼阵配置
    """
    global sceneGroupConf
    sceneGroupConf = rocopy(getGameConf("scene"))


def loadSceneGroupConf_m():
    """
    加载渔场鱼阵配置
    """
    global sceneGroupConf_m
    sceneGroupConf_m = rocopy(getGameConf("scene_m"))


def getFishGroups(sceneName, mode=CLASSIC_MODE):
    """
    获取渔场对应的所有鱼阵
    """
    global sceneGroupConf, groupsConf, sceneGroupConf_m, groupsConf_m
    if mode == CLASSIC_MODE:
        effSceneGroupConf = sceneGroupConf
        effGroupsConf = groupsConf
    else:
        effSceneGroupConf = sceneGroupConf_m
        effGroupsConf = groupsConf_m
    commonGroupNames = effSceneGroupConf.get("common", [])
    groupNames = effSceneGroupConf.get(sceneName, [])
    groupNames.extend(commonGroupNames)
    sceneGroups = {}
    for groupName in groupNames:
        _groupConf = effGroupsConf.get(groupName)
        if _groupConf:
            sceneGroups[groupName] = _groupConf
    return sceneGroups


def loadDropConf():
    """
    加载掉落配置
    """
    global dropConf
    dropConf = rocopy(getGameConf("drop"))


def getDropConf(dropId):
    """
    获取掉落配置
    """
    global dropConf
    return dropConf.get(str(dropId), {})


def loadSkillConf():
    """
    加载技能配置
    """
    global skillConf
    skillConf = rocopy(getGameConf("skill"))


def getSkillGradeCommonConf(skillId, level):
    """
    获取技能等级公共配置
    """
    global skillConf
    return skillConf.get("grade", {}).get(str(skillId), {}).get(str(level), {})


def getSkillStarCommonConf(skillId, level):
    """
    获取技能星级公共配置
    """
    global skillConf
    return skillConf.get("star", {}).get(str(skillId), {}).get(str(level), {})


def getAllSkillId():
    """
    获取所有技能ID
    """
    global skillConf
    return skillConf.get("star", {}).keys()


def loadSkillGradeConf():
    """
    加载技能等级配置
    """
    global skillGradeConf
    skillGradeConf = rocopy(getGameConf("skillGrade"))


def loadSkillGradeConf_m():
    """
    加载技能等级配置
    """
    global skillGradeConf_m
    skillGradeConf_m = rocopy(getGameConf("skillGrade_m"))


def getSkillGradeConf(skillId, level, skillMode):
    """
    获取技能等级配置
    @param skillMode: 0:经典 1:千炮
    """
    global skillGradeConf, skillGradeConf_m
    if skillMode == MULTIPLE_MODE:
        skillGradeConf_m.get(str(skillId), {}).get(str(level), {})
    return skillGradeConf.get(str(skillId), {}).get(str(level), {})


def loadSkillStarConf():
    """
    加载技能星级配置
    """
    global skillStarConf
    skillStarConf = rocopy(getGameConf("skillStar"))


def loadSkillStarConf_m():
    """
    加载技能星级配置
    """
    global skillStarConf_m
    skillStarConf_m = rocopy(getGameConf("skillStar_m"))


def getSkillStarConf(skillId, level, skillMode):
    """
    获取技能星级配置
    @param skillMode: 0:经典 1:千炮
    """
    global skillStarConf, skillStarConf_m
    if skillMode == MULTIPLE_MODE:
        return skillStarConf_m.get(str(skillId), {}).get(str(level), {})
    return skillStarConf.get(str(skillId), {}).get(str(level), {})


def loadChestConf():
    """
    加载宝箱配置
    """
    global chestConf
    chestConf = rocopy(getGameConf("chest"))


def getChestConf(chestId=None):
    """
    获取宝箱配置
    """
    global chestConf
    if chestId is None:
        return rwcopy(chestConf)
    return chestConf.get(str(chestId), {})


def loadChestDropConf():
    """
    加载宝箱掉落配置
    """
    global chestDropConf
    chestDropConf["chestDrop"] = getGameConf("chestDrop")
    levelDropConf = {}
    for _, value in chestDropConf["chestDrop"].iteritems():
        levelDropConf.setdefault(value["level"], []).append(value)
    chestDropConf["levelDrop"] = levelDropConf
    ftlog.debug("chestDropConf->", chestDropConf)
    chestDropConf = rocopy(chestDropConf)


def getChestDropConf(level=None):
    """
    获取宝箱掉落配置
    """
    global chestDropConf
    if level is None:
        return chestDropConf.get("chestDrop", {})
    return chestDropConf.get("levelDrop", {}).get(str(level), [])


def loadPublicConf():
    """
    加载公共配置
    """
    global publicConf
    publicConf = rocopy(getGameConf("public"))


def getPublic(key, defaultValue=None):
    """
    获取公共配置
    """
    global publicConf
    return publicConf.get(str(key), defaultValue)


def loadCheckinConf():
    """
    加载签到配置
    """
    global checkinConf
    checkinConf = rocopy(OrderedDict(sorted(getGameConf("checkin").iteritems())))


def getCheckinConf(type, day=0):
    """
    获取签到配置
    """
    global checkinConf
    if day:
        return rwcopy(checkinConf.get(type, {}).get(str(day), {}))
    return checkinConf.get(type, {})


def getNoticeUrl():
    """
    获取通知url
    """
    return getPublic("noticeUrl", "")


def getNotice():
    """
    获取通知
    """
    return getPublic("notice", "")


def getNoticeVersion():
    """
    获取通知版本
    """
    return getPublic("noticeVersion", 1)


def isLimitClientId(clientId):
    """
    是否为限制ClientId
    """
    return set(getPublic("limitClientIds", [])) & set(list(clientId))


def getGameTimePoolIssue():
    """
    获取扭蛋抽奖池期号
    """
    return getPublic("gameTimePoolIssue", 0)


def getUsableClientVersion():
    """
    获取客户端可用版本号
    """
    return getPublic("usableClientVersion", {})


def getDisableClientVersion():
    """
    获取客户端禁止使用版本号
    """
    return getPublic("disableClientVersion", [])


def loadCmpttTaskConf():
    """
    加载宝藏争夺赛配置
    """
    global cmpttTaskConf
    cmpttTaskConfTmp = getGameConf("cmpttTask")
    cmpttTaskConf = {}
    for key, value in cmpttTaskConfTmp.iteritems():
        fishPool = value["fishPool"]
        if fishPool not in cmpttTaskConf:
            cmpttTaskConf[fishPool] = []
        cmpttTaskConf[fishPool].append(value)
    cmpttTaskConf = rocopy(cmpttTaskConf)


def getCmpttTaskConf(fishPool):
    """
    获取宝藏争夺赛配置
    """
    global cmpttTaskConf
    return rwcopy(cmpttTaskConf.get(str(fishPool), []))


def loadNcmpttTaskConf():
    """
    加载限时任务配置
    """
    global ncmpttTaskConf
    ncmpttTaskConfTmp = getGameConf("ncmpttTask")
    ncmpttTaskConf = {}
    for key, value in ncmpttTaskConfTmp.iteritems():
        fishPool = value["fishPool"]
        if fishPool not in ncmpttTaskConf:
            ncmpttTaskConf[fishPool] = []
        ncmpttTaskConf[fishPool].append(value)
    ncmpttTaskConf = rocopy(ncmpttTaskConf)




def loadProbabilityConf():
    """
    加载概率配置
    """
    global probabilityConf
    probabilityConf = rocopy(getGameConf("probability"))


def getCouponFishConf(fishPool):
    """
    获取奖券鱼配置
    """
    global probabilityConf
    return probabilityConf.get("couponFish", {}).get(str(fishPool), {})


def getMultipleFishConf(fishPool):
    """
    获取倍率鱼配置
    """
    global probabilityConf
    return probabilityConf.get("multipleFish", {}).get(str(fishPool), [])


def getBossFishConf(fishPool):
    """
    获取Boss鱼配置
    """
    global probabilityConf
    return probabilityConf.get("bossFish", {}).get(str(fishPool), [])


def getChestFishConf(fishPool):
    """
    获取宝箱鱼配置
    """
    global probabilityConf
    return probabilityConf.get("chestFish", {}).get(str(fishPool), {})


def getActivityFishConf(fishPool):
    """
    获取活动鱼配置
    """
    global probabilityConf
    return probabilityConf.get("activityFish", {}).get(str(fishPool), {})


def getShareFishConf(fishPool):
    """
    获取分享宝箱鱼配置
    """
    global probabilityConf
    return probabilityConf.get("shareFish", {}).get(str(fishPool), {})


def getHitBossConf():
    """
    获取击伤Boss配置
    """
    global probabilityConf
    return probabilityConf.get("hitBoss", [])


def getBufferFishConf(fishPool):
    """
    获取Buffer鱼配置
    """
    global probabilityConf
    return probabilityConf.get("bufferFish", {}).get(str(fishPool), [])


def getHippoFishConf(fishPool):
    """
    获取河马鱼配置
    """
    global probabilityConf
    return probabilityConf.get("hippoFish", {}).get(str(fishPool), [])


def getTerrorFishConf(fishPool):
    """
    获取恐怖鱼配置
    """
    global probabilityConf
    return probabilityConf.get("terrorFish", {}).get(str(fishPool), [])


def getAutofillFishConf(fishPool):
    """
    获取autofill鱼配置
    """
    global probabilityConf
    return probabilityConf.get("autofillFish", {}).get(str(fishPool), [])


def getUserCouponFishConf(fishPool):
    """
    获取个人可见奖券鱼配置
    """
    global probabilityConf
    return probabilityConf.get("userCouponFish", {}).get(str(fishPool), {})


def loadDynamicOddsConf():
    """
    加载动态概率配置
    """
    global dynamicOddsConf
    dynamicOddsConf = rocopy(getGameConf("dynamicOdds"))
    


def initConfig():
    """
    初始化所有配置
    """
    loadPublicConf()
    loadGroupsConf()
    loadSceneGroupConf()
    loadSceneGroupConf_m()
    loadFishConf()
    loadFishConf_m()
    loadWeaponConf()
    loadWeaponConf_m()
    loadWeaponPowerRateConf()
    loadCheckinConf()
    loadStoreConf()
    loadDropConf()
    loadUlevelConf()
    loadUserLevelConf()
    loadSkillConf()
    loadSkillGradeConf()
    loadSkillGradeConf_m()
    loadSkillStarConf()
    loadSkillStarConf_m()
    loadMainQuestConf()
    loadDailyQuestConf()
    loadDailyQuestRewardConf()
    loadCmpttTaskConf()
    loadNcmpttTaskConf()
    loadBonusTaskConf()
    loadGuideTaskConf()
    loadExpressionConf()
    loadChestConf()
    loadChestDropConf()
    loadProbabilityConf()                   # 加载概率配置
    loadDynamicOddsConf()                   # 加载动态概率配置
    loadLotteryPoolConf()
    loadGiftConf()
    loadActivityConf()
    loadCatchDropConf()
    loadVipConf()
    loadMatchFishConf()
    loadFixedMultipleFishConf()
    loadCallMultipleFishConf()
    loadMatchMultipleFishConf()
    loadRankRewardConf()
    loadBounsGameConf()
    loadAchievementConf()
    loadItemConf()
    loadHonorConf()
    loadGunTypeConf()
    loadGunTypeConf_m()
    loadRobberyConf()
    loadCommonConf()
    loadPlayerBufferConf()
    loadRobotConf()
    loadRandomMultipleFishConf()
    loadGunLevelConf()
    loadGunLevelConf_m()
    loadTableTaskConf()
    loadInviteTaskConf()
    loadRechargePoolConf()
    loadShareConf()
    loadFlyPigRewardConf()
    loadStarfishRouletteConf()
    loadSurpassTargetConf()
    loadSpecialItemConf()
    loadMultiLangTextConf()
    loadReportFishCBConf()
    loadIdCardAreaConf()
    loadGrandPrizeConf()
    loadPiggyBankConf()
    loadTreasureConf()
    loadBuyTypeConf()
    loadTimeLimitedStoreConf()
    loadLevelRewardsConf()
    loadUpdateVerRewardsConf()
    loadItemMonitorConf()
    loadPrizeWheelConf()
    loadSlotMachineConf()
    loadStatisPropConf()
    loadMoneyTreeConf()
    loadCannedFishConf()
    loadCreditStoreConf()
    loadLevelFundsConf()
    loadLevelFundsConf_m()
    loadSuperEggsConf()
    loadSupplyBoxConf()
    loadGrandPrixConf()
    loadFestivalTurntableConf()
    loadGrandPrixPrizeWheelConf()
    loadSuperbossExchangeConf()
    loadSuperbossMinigameConf()
    loadSuperbossCommonConf()
    loadCollectItemConf()
    loadPoseidonConf()
    loadBigPrizeConf()
    loadCompActConf()
    loadNewbie7DaysGfitConf()
    loadLotteryTicActConf()
    loadPassCardConf()
    loadSkillCompenConf()
    loadABTestConf()
    loadGiftAbcTestConf()
    loadReturnerMissionConf()
    loadMiniGameConf()
    loadLuckyTreeConf()
    loadExchangeStoreConf()
    loadSuperbossPowerConf()
    loadLevelPrizeWheelConf()


def registerConfigEvent():
    """
    监听配置刷新事件
    """
    tyeventbus.globalEventBus.subscribe(EventConfigure, reloadConfig)


def reloadConfig(event):
    """
    加载配置
    """
    ftlog.debug("reloadConfig->", event.keylist)
    config = {
        getConfigPath("public"): loadPublicConf,
        getConfigPath("scene"): loadSceneGroupConf,         # 加载渔场鱼阵配置
        getConfigPath("scene_m"): loadSceneGroupConf_m,
        getConfigPath("fish"): loadFishConf,
        getConfigPath("fish_m"): loadFishConf_m,
        getConfigPath("weapon"): loadWeaponConf,
        getConfigPath("weapon_m"): loadWeaponConf_m,
        getConfigPath("weaponPowerRate"): loadWeaponPowerRateConf,
        getConfigPath("checkin"): loadCheckinConf,
        getConfigPath("store"): loadStoreConf,
        getConfigPath("drop"): loadDropConf,                # 加载掉落配置
        getConfigPath("ulevel"): loadUlevelConf,
        getConfigPath("userLevel"): loadUserLevelConf,
        getConfigPath("skill"): loadSkillConf,              # 加载技能配置
        getConfigPath("skillGrade"): loadSkillGradeConf,    # 加载技能等级配置
        getConfigPath("skillGrade_m"): loadSkillGradeConf_m,
        getConfigPath("skillStar"): loadSkillStarConf,      # 加载技能星级配置
        getConfigPath("skillStar_m"): loadSkillStarConf_m,
        getConfigPath("mainQuest"): loadMainQuestConf,
        getConfigPath("dailyQuest"): loadDailyQuestConf,
        getConfigPath("dailyQuestReward"): loadDailyQuestRewardConf,
        getConfigPath("cmpttTask"): loadCmpttTaskConf,      # 加载宝藏争夺赛配置
        getConfigPath("ncmpttTask"): loadNcmpttTaskConf,
        getConfigPath("bonusTask"): loadBonusTaskConf,
        getConfigPath("guideTask"): loadGuideTaskConf,
        getConfigPath("expression"): loadExpressionConf,
        getConfigPath("chest"): loadChestConf,              # 加载宝箱配置
        getConfigPath("chestDrop"): loadChestDropConf,      # 加载宝箱掉落配置
        getConfigPath("probability"): loadProbabilityConf,
        getConfigPath("dynamicOdds"): loadDynamicOddsConf,
        getConfigPath("lotteryPool"): loadLotteryPoolConf,
        getConfigPath("gift"): loadGiftConf,
        getConfigPath("activity"): loadActivityConf,
        getConfigPath("catchDrop"): loadCatchDropConf,
        getConfigPath("vip"): loadVipConf,
        getConfigPath("matchFish"): loadMatchFishConf,
        getConfigPath("fixedMultipleFish"): loadFixedMultipleFishConf,
        getConfigPath("callMultipleFish"): loadCallMultipleFishConf,
        getConfigPath("matchMultipleFish"): loadMatchMultipleFishConf,
        getConfigPath("rankReward"): loadRankRewardConf,
        getConfigPath("fishBonusGame"): loadBounsGameConf,
        getConfigPath("achievement"): loadAchievementConf,
        getConfigPath("item"): loadItemConf,
        getConfigPath("honor"): loadHonorConf,
        getConfigPath("gun"): loadGunTypeConf,
        getConfigPath("gun_m"): loadGunTypeConf_m,
        getConfigPath("robbery"): loadRobberyConf,
        getConfigPath("common"): loadCommonConf,
        getConfigPath("playerBuffer"): loadPlayerBufferConf,
        getConfigPath("robot"): loadRobotConf,
        getConfigPath("randomMultipleFish"): loadRandomMultipleFishConf,
        getConfigPath("gunLevel"): loadGunLevelConf,
        getConfigPath("gunLevel_m"): loadGunLevelConf_m,
        getConfigPath("tableTask"): loadTableTaskConf,
        getConfigPath("inviteTask"): loadInviteTaskConf,
        getConfigPath("rechargePool"): loadRechargePoolConf,
        getConfigPath("share"): loadShareConf,
        getConfigPath("flyPigReward"): loadFlyPigRewardConf,
        getConfigPath("starfishRoulette"): loadStarfishRouletteConf,
        getConfigPath("surpassTarget"): loadSurpassTargetConf,
        getConfigPath("specialItem"): loadSpecialItemConf,
        getConfigPath("multiLangText"): loadMultiLangTextConf,
        getConfigPath("reportFishCB"): loadReportFishCBConf,
        getConfigPath("idCard"): loadIdCardAreaConf,
        getConfigPath("grandPrize"): loadGrandPrizeConf,
        getConfigPath("piggyBank"): loadPiggyBankConf,
        getConfigPath("treasure"): loadTreasureConf,
        getConfigPath("buyType"): loadBuyTypeConf,
        getConfigPath("timeLimitedStore"): loadTimeLimitedStoreConf,
        getConfigPath("levelRewards"): loadLevelRewardsConf,
        getConfigPath("updateVerRewards"): loadUpdateVerRewardsConf,
        getConfigPath("itemMonitor"): loadItemMonitorConf,
        getConfigPath("prizeWheel"): loadPrizeWheelConf,
        getConfigPath("slotMachine"): loadSlotMachineConf,
        getConfigPath("statisProp"): loadStatisPropConf,
        getConfigPath("moneyTree"): loadMoneyTreeConf,
        getConfigPath("cannedFish"): loadCannedFishConf,
        getConfigPath("creditStore"): loadCreditStoreConf,
        getConfigPath("levelFunds"): loadLevelFundsConf,
        getConfigPath("levelFunds_m"): loadLevelFundsConf_m,
        getConfigPath("superEggs"): loadSuperEggsConf,
        getConfigPath("supplyBox"): loadSupplyBoxConf,
        getConfigPath("grandPrix"): loadGrandPrixConf,
        getConfigPath("festivalTurntable"): loadFestivalTurntableConf,
        getConfigPath("grandPrixPrizeWheel"): loadGrandPrixPrizeWheelConf,
        getConfigPath("superbossExchange"): loadSuperbossExchangeConf,
        getConfigPath("superbossMinigame"): loadSuperbossMinigameConf(),
        getConfigPath("superbossCommon"): loadSuperbossCommonConf(),
        getConfigPath("collectItem"): loadCollectItemConf,
        getConfigPath("poseidon"): loadPoseidonConf,
        getConfigPath("bigPrize"): loadBigPrizeConf,
        getConfigPath("competition"): loadCompActConf,
        getConfigPath("newbie7DaysGift"): loadNewbie7DaysGfitConf,
        getConfigPath("lotteryTicket"): loadLotteryTicActConf,
        getConfigPath("passCard"): loadPassCardConf,
        getConfigPath("skillCompensate"): loadSkillCompenConf,
        getConfigPath("abTest"): loadABTestConf,
        getConfigPath("giftAbcTest"): loadGiftAbcTestConf,
        getConfigPath("returnerMission"): loadReturnerMissionConf,
        getConfigPath("miniGame"): loadMiniGameConf,
        getConfigPath("luckyTree"): loadLuckyTreeConf,
        getConfigPath("exchangeStore"): loadExchangeStoreConf,
        getConfigPath("superbossPower"): loadSuperbossPowerConf,
        getConfigPath("prizeWheel_m"): loadLevelPrizeWheelConf,
    }
    try:
        for keyName in event.keylist:
            configPath, clientId = keyName.rsplit(":", 1)
            if configPath in config and clientId.isdigit():
                intClientId = int(clientId)
                if intClientId:
                    config[configPath](intClientId)
                else:
                    config[configPath]()
                ftlog.info("reloadConfig->", keyName, config[configPath].__name__)
    except:
        ftlog.error()
    from newfish.entity import grand_prize_pool
    grand_prize_pool.reloadConfig(event)


def getConfigPath(configName):
    """
    获取配置路径
    """
    return "game:%s:%s" % (FISH_GAMEID, configName)


class Config(dict):
    """
    配置对象
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        raise AttributeError

    def __setitem__(self, key, value):
        raise AttributeError

    def __delattr__(self, key):
        raise AttributeError

    def __delitem__(self, key):
        raise AttributeError
    

def rocopy(data):
    """
    深拷贝只读
    """
    return json.loads(json.dumps(data), object_hook=Config)


def rwcopy(data):
    """
    深拷贝可读可写
    """
    return json.loads(json.dumps(data))