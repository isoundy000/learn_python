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
# 以下type为鱼种类别
# 普通金币鱼
NORMAL_FISH_TYPE = [1, 3]
# 道具鱼
ITEM_FISH_TYPE = [4, 11, 12, 13, 14, 15, 16]
# 捕获后掉口红的鱼
HIPPO_FISH_TYPE = [22]
# 红包鱼（包含奖券、话费、红包、京东卡、分享奖券鱼）
RED_FISH_TYPE = [4, 11, 13, 14, 15, 27]
# 捕获后会掉落海星的鱼
STAR_FISH_TYPE = [1, 2, 3, 8, 9, 19]
# 捕获后会掉落珍珠的鱼
PEARL_FISH_TYPE = [1, 2, 3, 8, 9, 19, 26]
# 捕获后会掉落紫水晶/黄水晶的鱼
CRYSTAL_FISH_TYPE = [1, 2, 3, 8, 9, 19]
# Boss鱼
BOSS_FISH_TYPE = [2, 8, 9, 19]
# 金币宝箱
CHIP_CHEST_FISH_TYPE = [10]
# 招财模式倍率鱼
ROBBERY_MULTIPLE_FISH_TYPE = [18]
# 招财模式boss鱼
ROBBERY_BOSS_FISH_TYPE = [20]
# 倍率鱼
MULTIPLE_FISH_TYPE = [3]
# 炸弹鱼
BOMB_FISH_TYPE = [5]
# 冰锥
ICE_FISH_TYPE = [6]
# 捕鱼机器人
ROBOT_FISH_TYPE = [7]
# Buffer鱼
BUFFER_FISH_TYPE = [21]
# 分享宝箱鱼
SHARE_CHEST_FISH_TYPE = [25]
# 彩虹鱼
RAINBOW_FISH_TYPE = [26]
# 分享奖券鱼
SHARE_COUPON_FISH_TYPE = [27]
# 电鳗鱼
NUMB_FISH_TYPE = [28]
# 钻头鱼
DRILL_FISH_TYPE = [29]
# 恐怖鱼
TERROR_FISH_TYPE = [5, 28, 29]
# 超级boss
SUPERBOSS_FISH_TYPE = [31]
# 概率专用鱼种类别
# 非高冷鱼
NON_ALOOF_FISH_TYPE = [1, 3]
# 使用彩虹奖池的鱼
RAINBOW_BONUS_FISH_TYPE = [5, 26, 28, 29]

# 日志专用鱼种类别
# 需要输出日志的鱼
LOG_OUTPUT_FISH_TYPE = [2, 3, 5, 8, 9, 10, 11, 13, 14, 15, 18, 19, 20, 28, 29]


# -------------------------
# 以下type为武器类别
# 火炮/千炮
GUN_WEAPON_TYPE = 1
# 技能
SKILL_WEAPON_TYPE = 2
# 猎鱼机甲开火
RB_FIRE_WEAPON_TYPE = 3
# 猎鱼机甲爆炸
RB_BOMB_WEAPON_TYPE = 4
# 炸弹鱼爆炸
BOMB_WEAPON_TYPE = 5
# 招财模式火炮
ROBBERY_WEAPON_TYPE = 6
# 电鳗
NUMB_WEAPON_TYPE = 7
# 钻头鱼
DRILL_WEAPON_TYPE = 8
# 超级boss
SUPERBOSS_WEAPON_TYPE = 9

# -------------------------

# 红包券:奖券 比率
COUPON_DISPLAY_RATE = 0.01
# 技能卡片道具ID与技能ID对应表
skillCardKindIdMap = {
    1145: 5101,
    1146: 5102,
    1147: 5103,
    1148: 5104,
    1149: 5105,
    1150: 5106,
    1151: 5107,
    1152: 5108,
    1153: 5109,
    1154: 5110
}
# 升星卡片道具ID与技能ID对应表
starCardKindIdMap = {
    1155: 5101,
    1156: 5102,
    1157: 5103,
    1158: 5104,
    1159: 5105,
    1160: 5106,
    1161: 5107,
    1162: 5108,
    1163: 5109,
    1164: 5110
}

# 与技能升级、升星有关的道具ID
upgradeSkillKindIds = [14124, 14125, 14126, 14127, 1145, 1147, 1149, 1150, 1152, 1153, 1154]

# 与火炮升级有关的道具ID
upgradeGunKindIds = [PEARL_KINDID, PURPLE_CRYSTAL_KINDID, YELLOW_CRYSTAL_KINDID]

# 自定义ID与资产ID对应表
customKindIdMap = {
    CHIP_KINDID: "user:chip",
    DIAMOND_KINDID: "user:diamond",
    COUPON_KINDID: "user:coupon"
}

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
sceneGroupConf = {}             # 加载渔场鱼阵配置 scene场景鱼阵 [group_44201_1、group_44201_2、... group_44201_30]
sceneGroupConf_m = {}
groupsConf = {}                 # 所有鱼阵配置All
groupsConf_m = {}               # 所有千炮鱼阵配置All
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


def getNcmpttTaskConf(fishPool):
    """
    获取限时任务配置
    """
    global ncmpttTaskConf
    return rwcopy(ncmpttTaskConf.get(str(fishPool), []))


def loadBonusTaskConf():
    """
    加载奖金赛配置
    """
    global bonusTaskConf
    bonusTaskConfTmp = getGameConf("bonusTask")
    bonusTaskConf = {}
    for key, value in bonusTaskConfTmp.iteritems():
        fishPool = value["fishPool"]
        if fishPool not in bonusTaskConf:
            bonusTaskConf[fishPool] = []
        bonusTaskConf[fishPool].append(value)
    bonusTaskConf = rocopy(bonusTaskConf)


def getBonusTaskConf(fishPool):
    """
    获取奖金赛配置
    """
    global bonusTaskConf
    return rwcopy(bonusTaskConf.get(str(fishPool), []))


def loadGuideTaskConf():
    """
    加载新手任务配置
    """
    global guideTaskConf
    guideTaskConf = rocopy(getGameConf("guideTask"))


def getGuideTaskConf(taskId):
    """
    获取新手任务配置
    """
    global guideTaskConf
    return rwcopy(guideTaskConf.get(str(taskId), {}))


def loadFishConf():
    """
    加载所有鱼配置
    """
    global fishConf
    fishConf = getGameConf("fish")
    for key, value in fishConf.iteritems():
        value["fishType"] = int(key)
    fishConf = rocopy(fishConf)


def loadFishConf_m():
    """
    加载千炮所有鱼配置
    """
    global fishConf_m
    fishConf_m = getGameConf("fish_m")
    for key, value in fishConf_m.iteritems():
        value["fishType"] = int(key)
    fishConf_m = rocopy(fishConf_m)


def getFishConf(fishType, typeName, multiple=1):
    """
    获取鱼配置 fishType: 鱼的ID typeName 渔场类型[好友、比赛、...] multiple渔场倍率
    """
    global fishConf, fishConf_m
    if typeName in [FISH_TIME_MATCH, FISH_FIGHT, FISH_TIME_POINT_MATCH]:    # 回馈赛渔场、渔友竞技渔场、定时积分赛渔场
        return getMatchFishConf(fishType)
    else:
        conf = fishConf_m.get(str(fishType), {}) if fishType == FISH_MULTIPLE else fishConf.get(str(fishType), {})
        if multiple != 1 and conf.get("type", 0) in ITEM_FISH_TYPE:
            conf = rwcopy(conf)
            conf["probb1"] /= multiple
            conf["probb2"] /= multiple
            conf["value"] /= multiple
        return conf


def loadMatchFishConf():
    """
    加载比赛鱼配置
    """
    global matchFishConf
    matchFishConf = getGameConf("matchFish")
    for key, value in matchFishConf.iteritems():
        value["fishType"] = int(key)
    matchFishConf = rocopy(matchFishConf)


def getMatchFishConf(fishId):
    """
    获取比赛鱼配置
    """
    global matchFishConf
    return matchFishConf.get(str(fishId), {})


def getAllMatchFish(fishPool):
    """
    获取所有比赛加倍鱼
    """
    allMatchFish = {}
    global matchFishConf
    for fishId, fish in matchFishConf.iteritems():
        if fish["multiple"] > 1 and fishPool in fish["fishPool"]:
            allMatchFish[int(fishId)] = fish["multiple"]
    return allMatchFish


def loadWeaponConf():
    """
    加载武器配置
    """
    global weaponConf
    global minWeaponId
    weaponConf = rocopy(getGameConf("weapon"))
    keys = [int(x) for x in weaponConf.keys()]
    keys2 = sorted(keys)
    minWeaponId = keys2[0]


def getWeaponConf(wpId, useRate=True, mode=CLASSIC_MODE):
    """
    获取武器配置
    """
    global weaponConf
    global weaponConf_m
    conf = weaponConf if mode == CLASSIC_MODE else weaponConf_m
    weaponInfo = conf.get(str(wpId), {})
    powerRateConfig = getWeaponPowerRateConf(wpId)
    if useRate and powerRateConfig:
        weaponInfo = rwcopy(weaponInfo)
        probab = random.randint(1, 10000)
        for probabInfo in powerRateConfig:
            probbArr = probabInfo["probb"]
            if probbArr[0] <= probab <= probbArr[1]:
                if len(probabInfo["value"]) == 1:
                    rate = probabInfo["value"][0]
                else:
                    rate = round(random.uniform(probabInfo["value"][0], probabInfo["value"][1]), 2)
                    if ftlog.is_debug():
                        ftlog.debug("getWeaponConf", wpId, probabInfo["value"], rate)
                weaponInfo["power"] *= rate
                break
    return weaponInfo


def loadWeaponConf_m():
    """
    加载千炮武器配置
    """
    global weaponConf_m
    global minWeaponId_m
    weaponConf_m = rocopy(getGameConf("weapon_m"))
    keys = [int(x) for x in weaponConf_m.keys()]
    keys2 = sorted(keys)
    minWeaponId_m = keys2[0]


def loadWeaponPowerRateConf():
    """
    加载武器威力加成配置
    """
    global weaponPowerRateConf
    weaponPowerRateConf = rocopy(getGameConf("weaponPowerRate"))


def getWeaponPowerRateConf(wpId):
    """
    获取武器威力加成配置
    """
    global weaponPowerRateConf
    return weaponPowerRateConf.get(str(wpId), [])


def getMinWeaponId():
    """
    获取最小武器ID
    """
    global minWeaponId
    return minWeaponId





















def loadCommonConf():
    """
    加载通用配置
    """
    global commonConf
    commonConf = rocopy((getGameConf("common")))


def getCommonValueByKey(key_, default=0):
    """
    获取通用数据
    """
    global commonConf
    return commonConf.get(key_, default)


def loadRankRewardConf():
    """
    加载排行榜配置
    """
    global rankRewardConf
    rankRewardConf = rocopy(getGameConf("rankReward"))


def getAllRankConfs():
    """
    获取排行榜配置
    """
    global rankRewardConf
    return rankRewardConf


def getRankRewardConf(rankType):
    """
    获取排行榜配置
    """
    global rankRewardConf
    return rankRewardConf.get("ranks", {}).get(str(rankType), {})


def loadSpecialItemConf():
    """
    加载特殊物品配置
    """
    global specialItemConf
    specialItemConf = rocopy(getGameConf("specialItem"))


def getSpecialItemConf():
    """
    获取特殊物品配置
    """
    global specialItemConf
    return specialItemConf


def loadMultiLangTextConf():
    """
    加载多语言文本
    """
    global multiLangTextConf
    multiLangTextConf = rocopy(getGameConf("multiLangText"))


def getMultiLangTextConf(id, lang="zh"):
    """
    获取多语言文本
    getMultiLangTextConf(?!.*?lang).*$
    """
    global multiLangTextConf
    conf = multiLangTextConf.get(id, {})
    if not conf:
        ftlog.error("getMultiLangTextConf error", id)
    return conf.get(lang, "")


def getIncrPearlDropRatio(userId):
    """
    获取可以增加的珍珠额外掉率
    """
    global specialItemConf
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    ratio = 0.
    for k, v in specialItemConf.iteritems():
        if v.get("incrPearlDropRate", 0):
            item = userBag.getItemByKindId(int(k))
            if item and not item.isDied(int(time.time())):
                ratio += v["incrPearlDropRate"]
    return ratio


def getIncrCrystalDropRatio(userId):
    """
    获取可以增加的水晶额外掉率
    """
    global specialItemConf
    userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    ratio = 0.
    for k, v in specialItemConf.iteritems():
        if v.get("incrCrystalDropRate", 0):
            item = userBag.getItemByKindId(int(k))
            if item and not item.isDied(int(time.time())):
                ratio += v["incrCrystalDropRate"]
    return ratio


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


def loadAutofillFishConf_m():
    """
    加载自动填充鱼配置
    """
    global autofillFishConf_m
    autofillFishConf_m = rocopy(getGameConf("autofillFish_m"))


def getAutofillFishConf_m(mode, fishPool):
    """
    获取自动填充鱼配置
    """
    global autofillFishConf_m
    return autofillFishConf_m.get(mode, {}).get(str(fishPool), {})


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


def getDynamicOddsConf(fishPool):
    """
    获取动态概率配置
    """
    global dynamicOddsConf
    return dynamicOddsConf.get(str(fishPool), {})

















def loadCatchDropConf():
    """
    加载捕获掉率配置
    """
    global catchDropConf
    catchDropConf = rocopy(getGameConf("catchDrop"))


def getCatchDropConf(fpMultiple, fishType, uid):
    """
    读取捕获掉率配置
    """
    dropConf = None
    global catchDropConf
    # dropConf = catchDropConf.get(str(fishPool), {})
    _conf = _getCatchDropGroupConf(fpMultiple, fishType)
    if _conf:
        kindId = _getCatchDropKindId(int(_conf["dropGroupId"]), uid)
    pass



















def loadPrizeWheelConf():
    """
    加载渔场轮盘配置
    """
    global prizeWheelConf
    prizeWheelConf = rocopy(getGameConf("prizeWheel"))


def getPrizeWheelConf():
    """
    获取渔场轮盘配置
    """
    global prizeWheelConf
    return prizeWheelConf


def loadGrandPrixPrizeWheelConf():
    """
    加载渔场轮盘配置
    """
    global grandPrixPrizeWheelConf
    grandPrixPrizeWheelConf = rocopy(getGameConf("grandPrixPrizeWheel"))


def getGrandPrixPrizeWheelConf():
    """
    获取渔场轮盘配置
    """
    global grandPrixPrizeWheelConf
    return grandPrixPrizeWheelConf


def _getCatchDropKindId(groupId, uid):
    """
    根据玩家uid和掉落组返回掉落kindId
    """
    pass

def _getCatchDropGroupConf(fpMultiple, fishType):
    """
    根据渔场和捕到的鱼的类型获得掉落组
    """
    pass

def loadVipConf():
    """
    加载VIP配置
    """
    global vipConf
    vipConf = rocopy(getGameConf("vip"))


def getVipConf(vipLevel=None):
    """
    读取VIP配置
    """
    global vipConf
    if vipLevel is None:
        return vipConf
    return vipConf.get(str(vipLevel), {})


def loadFixedMultipleFishConf():
    """
    加载固定倍率鱼配置
    """
    global fixedMultipleFishConf
    fixedMultipleFishConf = rocopy(getGameConf("fixedMultipleFish"))


def getFixedMultipleFishConf(fishPool):
    """
    获取固定倍率鱼配置
    """
    global fixedMultipleFishConf
    return fixedMultipleFishConf.get(str(fishPool), {})


def loadItemConf(intClientId=0):
    """
    加载道具配置
    """
    global itemConf
    _conf = getGameConf("item", intClientidNum=intClientId)
    if _conf:
        itemConfDict = OrderedDict(sorted(_conf.iteritems(), key=lambda d: d[1]["order"]))
        itemConf[intClientId] = rocopy(itemConfDict)
    else:
        itemConf[intClientId] = {}


def _getItemConfByClientId(clientId):
    """
    获取clientId对应的道具配置
    """
    global itemConf
    intClientId = configure.clientIdToNumber((clientId) if clientId else defaultIntClientId)
    if itemConf.get(intClientId) is None:
        loadItemConf(intClientId)
    if itemConf.get(intClientId):
        return itemConf[intClientId]
    return itemConf[defaultIntClientId]


def getItemConf(clientId, kindId=None):
    """
    获取道具配置
    """
    _itemConf = _getItemConfByClientId(clientId)
    if kindId is None:
        return _itemConf
    return rwcopy(_itemConf.get(str(kindId), {}))


def loadGunTypeConf(intClientId=0):
    """
    加载炮配置
    """
    global gunTypeConf
    _conf = getGameConf("gun", intClientidNum=intClientId)
    gunTypeConf[intClientId] = rocopy(_conf) if _conf else {}


def loadGunTypeConf_m(intClientId=0):
    """
    加载炮配置
    """
    global gunTypeConf_m
    _conf = getGameConf("gun_m", intClientidNum=intClientId)
    gunTypeConf_m[intClientId] = rocopy(_conf) if _conf else {}


def getAllGunIds(clientId, mode):
    """
    获取所有炮IDS
    """
    global gunTypeConf, gunTypeConf_m
    typeConf = gunTypeConf if mode == CLASSIC_MODE else gunTypeConf_m
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if typeConf.get(intClientId) is None:
        if mode == CLASSIC_MODE:
            loadGunTypeConf(intClientId)
        else:
            loadGunTypeConf_m(intClientId)
    if typeConf.get(intClientId):
        return typeConf[intClientId].get("gunIds", [])
    return typeConf.get(defaultIntClientId, {}).get("gunIds", [])


def getGunMaxLevel(gunId, clientId, mode):
    """
    获取指定炮ID的最大等级
    """
    global gunTypeConf, gunTypeConf_m
    typeConf = gunTypeConf if mode == CLASSIC_MODE else gunTypeConf_m
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if typeConf.get(intClientId) is None:
        if mode == CLASSIC_MODE:
            loadGunTypeConf(intClientId)
        else:
            loadGunTypeConf_m(intClientId)
    if typeConf.get(intClientId):
        return len(typeConf[intClientId].get("gun", {}).get(str(gunId), {}))
    return len(typeConf.get(defaultIntClientId, {}).get("gun", {}).get(str(gunId), {}))


def getGunConf(gunId, clientId, level=1, mode=CLASSIC_MODE):
    """
    获取皮肤炮指定等级配置
    """
    global gunTypeConf, gunTypeConf_m
    typeConf = gunTypeConf if mode == CLASSIC_MODE else gunTypeConf_m
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if typeConf.get(intClientId) is None:
        if mode == CLASSIC_MODE:
            loadGunTypeConf(intClientId)
        else:
            loadGunTypeConf_m(intClientId)
    if typeConf.get(intClientId):
        return typeConf[intClientId].get("gun", {}).get(str(gunId), {}).get(str(level), {})
    return typeConf.get(defaultIntClientId, {}).get("gun", {}).get(str(gunId), {}).get(str(level), {})


def getGunSkinConf(gunSkinId, clientId, mode):
    """
    获取皮肤配置
    """
    global gunTypeConf, gunTypeConf_m
    typeConf = gunTypeConf if mode == CLASSIC_MODE else gunTypeConf_m
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if typeConf.get(intClientId) is None:
        if mode == CLASSIC_MODE:
            loadGunTypeConf(intClientId)
        else:
            loadGunTypeConf_m(intClientId)
    if typeConf.get(intClientId):
        return typeConf[intClientId].get("skin", {}).get(str(gunSkinId))
    return typeConf.get(defaultIntClientId, {}).get("skin", {}).get(str(gunSkinId))


def loadExpressionConf():
    """
    加载表情配置
    """
    global expressionConf
    expressionConf = rocopy(getGameConf("expression"))


def getExpressionConf(bigRoomId):
    """
    获取表情配置
    """
    global expressionConf
    conf = expressionConf.get("rooms", {}).get(str(bigRoomId), None)
    if conf:
        return expressionConf.get("templates", {}).get(conf, {})
    return {}


def isClientIgnoredConf(key, val, clientId=""):
    pass


def loadUlevelConf():
    """
    加载用户等级配置
    """
    global ulevelConf
    ulevelConf = rocopy(getGameConf("ulevel"))


def getUlevelNum():
    """
    获取用户最大等级
    """
    global ulevelConf
    return len(ulevelConf)


def getUlevel(levelId):
    """
    获取用户等级配置
    """
    global ulevelConf
    return ulevelConf.get(str(levelId), {})


def loadUserLevelConf():
    """
    加载用户等级配置
    """
    global userLevelConf
    userLevelConf = rocopy(getGameConf("userLevel"))


def getUserLevelConf():
    """
    获取用户等级配置
    """
    global userLevelConf
    return userLevelConf








def loadRobotConf():
    """
    加载机器人配置
    """
    global robotConf
    robotConf = rocopy(getGameConf("robot"))


def getRobotConf(key):
    """
    读取机器人配置
    """
    global robotConf
    return robotConf.get(str(key))


def loadRandomMultipleFishConf():
    """
    加载随机倍率鱼出现概率配置
    """
    global randomMultipleFishConf
    randomMultipleFishConf = rocopy(getGameConf("randomMultipleFish"))


def getRandomMultipleFishConf(fishPool):
    """
    读取随机倍率鱼出现概率配置
    """
    global randomMultipleFishConf
    return randomMultipleFishConf.get(str(fishPool), [])


def loadGunLevelConf():
    """
    加载火炮等级配置
    """
    global gunMultipleConf
    gunMultipleConf = OrderedDict()
    global gunLevelConf
    gunLevelConfTmp = getGameConf("gunLevel")
    gunLevels = sorted(gunLevelConfTmp.iteritems(), key=lambda d: d[0])
    gunLevelConf = OrderedDict()
    for key, value in gunLevels:
        gunLevelConf[key] = value
        unlockMultiple = value.get("unlockMultiple")    # 解锁倍率
        if unlockMultiple and unlockMultiple not in gunMultipleConf:
            gunMultipleConf[unlockMultiple] = int(key)
    gunLevelConf = rocopy(gunLevelConf)
    gunMultipleConf = rocopy(gunMultipleConf)
    # print "gunMultipleConf =", gunMultipleConf


def loadGunLevelConf_m():
    """
    加载千炮火炮等级配置
    """
    global gunLevelConf_m
    gunLevelConfTmp = getGameConf("gunLevel_m")
    gunLevels = sorted(gunLevelConfTmp.iteritems(), key=lambda d: d[0])
    gunLevelConf_m = OrderedDict()
    for key, value in gunLevels:
        gunLevelConf_m[key] = value
    gunLevelConf_m = rocopy(gunLevelConf_m)


def getGunLevelConf(gunLevel, mode):
    """
    读取火炮等级配置
    """
    global gunLevelConf, gunLevelConf_m
    if mode == CLASSIC_MODE:
        return gunLevelConf.get(str(gunLevel), {})
    else:
        return gunLevelConf_m.get(str(gunLevel), {})


def getMaxGunLevel(mode):
    """
    获得最大火炮等级
    """
    global gunLevelConf, gunLevelConf_m
    if mode == CLASSIC_MODE:
        return int(sorted(gunLevelConf.keys())[-1])
    else:
        return int(sorted(gunLevelConf_m.keys())[-1])


def getNextGunLevel(gunLevel, mode):
    """
    获得下个火炮等级
    """
    # gunLevel = int(gunLevel)
    # global gunLevelConf, gunLevelConf_m
    # if mode == CLASSIC_MODE:
    #     gunLevelList = sorted(map(int, gunLevelConf.keys()))
    # else:
    #     gunLevelList = sorted(map(int, gunLevelConf_m.keys()))
    # if gunLevel not in gunLevelList:
    #     return -1
    # idx = gunLevelList.index(gunLevel)
    # if idx + 1 < len(gunLevelList):
    #     return gunLevelList[idx + 1]
    # else:
    #     return gunLevelList[-1]
    gunLevel += 1
    gunLevel = min(gunLevel, getMaxGunLevel(mode))
    return gunLevel


def getGunLevelKeysConf(mode):
    """
    读取火炮等级配置
    """
    global gunLevelConf, gunLevelConf_m
    if mode == CLASSIC_MODE:
        return sorted(map(int, gunLevelConf.keys()))
    else:
        return sorted(map(int, gunLevelConf_m.keys()))


def getGunMultipleConf():
    """
    返回火炮等级和解锁倍率配置
    """
    global gunMultipleConf
    return gunMultipleConf


def loadTreasureConf():
    """
    加载宝藏配置
    """
    global treasureConf
    treasureConf = rocopy(getGameConf("treasure"))


def getTreasureConf(kindId=None, effectType=None, level=None):
    """
    获取宝藏配置
    """
    global treasureConf
    _conf = {}
    if kindId:
        _conf = treasureConf.get(str(kindId), {})
    elif effectType:
        for _, conf in treasureConf.iteritems():
            if conf["effectType"] == effectType:
                _conf = conf
                break
    if kindId or effectType:
        if level:
            return _conf.get("levels", {}).get(str(level))
        return _conf
    return treasureConf





























def loadLevelFundsConf(intClientId=0):
    """
    加载成长基金配置
    """
    global levelFundsConf
    _conf = getGameConf("levelFunds", intClientidNum=intClientId)
    levelFundsConf[intClientId] = rocopy(_conf) if _conf else {}


def loadLevelFundsConf_m(intClientId=0):
    """
    加载成长基金配置
    """
    global levelFundsConf_m
    _conf = getGameConf("levelFunds_m", intClientidNum=intClientId)
    levelFundsConf_m[intClientId] = rocopy(_conf) if _conf else {}


def getLevelFundsConf(clientId, mode):
    """
    获取成长基金配置
    """
    global levelFundsConf, levelFundsConf_m
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    _conf = levelFundsConf if mode == CLASSIC_MODE else levelFundsConf_m
    if _conf.get(intClientId) is None:
        if mode == CLASSIC_MODE:
            loadLevelFundsConf(intClientId)
        else:
            loadLevelFundsConf_m(intClientId)
    if _conf.get(intClientId):
        return _conf[intClientId]
    return _conf[defaultIntClientId]


def loadSuperEggsConf(intClientId=0):
    """
    加载超级扭蛋配置
    """
    global superEggsConf
    _conf = getGameConf("superEggs", intClientidNum=intClientId)
    superEggsConf[intClientId] = rocopy(_conf) if _conf else {}


def getSuperEggsConf(clientId):
    """
    获取超级扭蛋配置
    """
    global superEggsConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if superEggsConf.get(intClientId) is None:
        loadSuperEggsConf(intClientId)
    if superEggsConf.get(intClientId):
        return superEggsConf[intClientId]
    return superEggsConf[defaultIntClientId]


def loadSupplyBoxConf():
    """
    加载补给箱活动配置
    """
    global supplyBoxConf
    supplyBoxConf = rocopy(getGameConf("supplyBox"))


def getSupplyBoxConf(key_=None):
    """
    获取补给箱活动配置
    """
    global supplyBoxConf
    if key_ is None:
        return supplyBoxConf
    return rwcopy(supplyBoxConf.get(str(key_)))


def loadGrandPrixConf():
    """
    加载大奖赛配置
    """
    global grandPrixConf
    grandPrixConf = rocopy(getGameConf("grandPrix"))


def getGrandPrixConf(key_=None):
    """
    获取大奖赛配置
    """
    global grandPrixConf
    if key_ is None:
        return grandPrixConf
    return rwcopy(grandPrixConf.get(str(key_)))


def loadFestivalTurntableConf():
    """
    加载节日转盘抽大奖活动配置
    """
    global festivalTurntableConf
    festivalTurntableConf = rocopy(getGameConf("festivalTurntable"))


def getFestivalTurntableItemConf(key_=None):
    """
    获取节日转盘抽大奖配置
    """
    global festivalTurntableConf
    if key_ is None:
        return festivalTurntableConf
    return rwcopy(festivalTurntableConf.get(str(key_)))


def loadSuperbossExchangeConf():
    """
    加载超级boss兑换配置
    """
    global superbossExchangeConf
    superbossExchangeConf = rocopy(getGameConf("superbossExchange"))


def getSuperbossExchangeConf(fishPool=None):
    """
    获取超级boss兑换配置
    """
    global superbossExchangeConf
    if fishPool is None:
        return superbossExchangeConf
    return rwcopy(superbossExchangeConf.get(str(fishPool)))


def loadSuperbossMinigameConf():
    """
    加载超级boss小游戏配置
    """
    global superbossMinigameConf
    superbossMinigameConf = rocopy(getGameConf("superbossMinigame"))


def getSuperbossMinigameConf():
    """
    获取超级boss小游戏配置
    """
    global superbossMinigameConf
    return superbossMinigameConf


def loadSuperbossCommonConf():
    """
    加载超级boss通用配置
    """
    global superbossCommonConf
    superbossCommonConf = rocopy(getGameConf("superbossCommon"))


def getSuperbossCommonConf():
    """
    获取超级boss通用配置
    """
    global superbossCommonConf
    return superbossCommonConf


def loadCollectItemConf():
    """
    加载收集xx道具领奖活动配置(赢永久魅影皮肤)
    """
    global collectItemConf
    collectItemConf = rocopy(getGameConf("collectItem"))


def getCollectItemConf(key_=None):
    """
    获取收集xx道具领奖活动配置
    """
    global collectItemConf
    if key_ is None:
        return collectItemConf
    return rwcopy(collectItemConf.get(str(key_)))


def loadPoseidonConf():
    """
    加载海皇来袭配置
    """
    global poseidonConf
    poseidonConf = rocopy(getGameConf("poseidon"))


def getPoseidonConf(key_=None):
    """
    获取海皇来袭配置
    """
    global poseidonConf
    if key_ is None:
        return poseidonConf
    return poseidonConf.get(str(key_))


def loadBigPrizeConf():
    """
    加载幸运降临配置
    """
    global bigPrizeConf
    bigPrizeConf = rocopy(getGameConf("bigPrize"))


def getBigPrizeConf():
    """
    获取幸运降临配置
    """
    global bigPrizeConf
    return bigPrizeConf


def loadCompActConf(intClientId=0):
    """
    加载竞赛活动配置
    """
    global compActConf
    _conf = getGameConf("competition", intClientidNum=intClientId)
    compActConf[intClientId] = rocopy(_conf) if _conf else {}


def getCompActConf(clientId=None):
    """
    获取竞赛活动配置
    """
    global compActConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if compActConf.get(intClientId) is None:
        loadCompActConf(intClientId)
    if compActConf.get(intClientId):
        return compActConf[intClientId]
    return compActConf[defaultIntClientId]


def loadNewbie7DaysGfitConf():
    """
    加载默认商店配置
    """
    global newbie7DaysGiftConf
    newbie7DaysGiftConf = rocopy(getGameConf("newbie7DaysGift"))


def getNewbie7DaysGiftConf():
    global newbie7DaysGiftConf
    return newbie7DaysGiftConf


def loadLotteryTicActConf(intClientId=0):
    """
    加载渔场红包券抽奖配置
    """
    global lotteryTicketConf
    _conf = getGameConf("lotteryTicket", intClientidNum=intClientId)
    lotteryTicketConf[intClientId] = rocopy(_conf) if _conf else {}


def getLotteryTicActConf(clientId=None):
    """
    获取渔场红包券抽奖配置
    """
    global lotteryTicketConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if lotteryTicketConf.get(intClientId) is None:
        loadLotteryTicActConf(intClientId)
    if lotteryTicketConf.get(intClientId):
        return lotteryTicketConf[intClientId]
    return lotteryTicketConf[defaultIntClientId]


def loadPassCardConf(intClientId=0):
    """
    加载通行证活动配置
    """
    global passCardConf
    _conf = getGameConf("passCard", intClientidNum=intClientId)
    passCardConf[intClientId] = rocopy(_conf) if _conf else {}


def getPassCardConf(clientId):
    """
    获取通行证活动配置
    """
    global passCardConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if passCardConf.get(intClientId) is None:
        loadPassCardConf(intClientId)
    if passCardConf.get(intClientId):
        return passCardConf[intClientId]
    return passCardConf[defaultIntClientId]


def loadSkillCompenConf():
    """
    加载技能补偿配置
    """
    global skillCompenConf
    skillCompenConf = rocopy(getGameConf("skillCompensate"))


def getSkillCompenConf(key_=None):
    """
    获取技能补偿配置
    """
    global skillCompenConf
    if key_ is None:
        return skillCompenConf
    return skillCompenConf.get(str(key_))


def loadABTestConf():
    """
    加载ab test配置
    """
    global abTestConf
    abTestConf = rocopy(getGameConf("abTest"))


def getABTestConf(key_=None):
    """
    获取ab test配置
    """
    global abTestConf
    if key_ is None:
        return abTestConf
    return abTestConf.get(str(key_), {})


def loadReturnerMissionConf():
    """
    加载回归豪礼配置
    """
    global returnerMissionConf
    returnerMissionConf = rocopy(getGameConf("returnerMission"))


def getReturnerMissionConf(key_=None):
    """
    获取回归豪礼配置
    """
    global returnerMissionConf
    if key_ is None:
        return rwcopy(returnerMissionConf)
    return rwcopy(returnerMissionConf).get(str(key_))


def loadMiniGameConf():
    """
    加载小游戏配置（美人鱼的馈赠，宝箱）
    """
    global miniGameConf
    global miniGameLevelMap
    miniGameConfTmp = getGameConf("miniGame")
    miniGameConf = {}
    miniGameLevelMap = {}
    for key, value in miniGameConfTmp.items():
        miniGameConf[int(key)] = value
        level = value["level"]
        if level not in miniGameLevelMap:
            miniGameLevelMap[level] = []
        miniGameLevelMap[level].append(int(key))


def getMiniGameConf(miniGameId):
    """
    获取小游戏配置（美人鱼的馈赠，宝箱）
    """
    global miniGameConf
    return miniGameConf.get(miniGameId)


def loadLuckyTreeConf():
    """
    加载免费金币摇钱树配置
    """
    global luckyTreeConf
    luckyTreeConf = rocopy(getGameConf("luckyTree"))


def getLuckyTreeConf(key=None):
    """
    获取免费金币摇钱树配置
    :return:
    """
    global luckyTreeConf
    if key is None:
        return luckyTreeConf
    return luckyTreeConf.get(str(key))


def loadSuperbossPowerConf():
    """
    加载超级boss威力配置
    """
    global superbossPowerConf
    superbossPowerConf = rocopy(getGameConf("superbossPower"))


def getSuperbossPowerConf():
    """
    获取超级boss威力配置
    """
    global superbossPowerConf
    return superbossPowerConf


def loadLevelPrizeWheelConf():
    """
    加载等级转盘(青铜、白银、黄金、铂金、钻石)
    :return:
    """
    global levelPrizeWheelConf
    levelPrizeWheelConf = rocopy(getGameConf("prizeWheel_m"))


def getLevelPrizeWheelConf():
    """
    获取等级转盘的配置
    :return:
    """
    global levelPrizeWheelConf
    return levelPrizeWheelConf


def getTimePointMatchSkillConf():
    '''回馈赛的随机固定技能配置'''
    global timePointMatchSkillConf
    timePointMatchSkillConf = rocopy(getGameConf("timePointMatchSkill_m"))


def loadTideTask():
    """加载鱼潮任务"""
    global tideTaskConf
    tideTaskConf = rocopy(getGameConf("tideTask"))


def getTideTask(key):
    """获取渔潮任务"""
    global tideTaskConf
    if key is None:
        return tideTaskConf
    return tideTaskConf.get(str(key))


def initConfig():
    """
    初始化所有配置
    """
    loadPublicConf()                        # 加载公共配置
    loadGroupsConf()                        # 加载所有鱼阵
    loadSceneGroupConf()                    # 加载渔场鱼阵配置
    loadSceneGroupConf_m()                  # 加载千炮渔场鱼阵配置
    loadFishConf()
    loadFishConf_m()
    loadWeaponConf()                        # 加载武器配置
    loadWeaponConf_m()                      # 加载千炮武器配置
    loadWeaponPowerRateConf()               # 加载武器威力加成配置
    loadCheckinConf()                       # 加载签到配置
    loadStoreConf()
    loadDropConf()                          # 加载掉落配置
    loadUlevelConf()
    loadUserLevelConf()
    loadSkillConf()                         # 加载技能配置
    loadSkillGradeConf()                    # 加载技能升级配置
    loadSkillGradeConf_m()                  # 加载千炮技能升级配置
    loadSkillStarConf()                     # 加载技能星级配置
    loadSkillStarConf_m()                   # 加载千炮技能星级配置
    loadMainQuestConf()
    loadDailyQuestConf()
    loadDailyQuestRewardConf()
    loadCmpttTaskConf()
    loadNcmpttTaskConf()
    loadBonusTaskConf()
    loadGuideTaskConf()
    loadExpressionConf()
    loadChestConf()                         # 加载宝箱配置
    loadChestDropConf()                     # 加载宝箱掉落配置
    loadProbabilityConf()                   # 加载概率配置
    loadDynamicOddsConf()                   # 加载动态概率配置
    loadLotteryPoolConf()
    loadGiftConf()
    loadActivityConf()
    loadCatchDropConf()
    loadVipConf()
    loadMatchFishConf()
    loadFixedMultipleFishConf()             # 加载固定倍率鱼配置
    loadCallMultipleFishConf()
    loadMatchMultipleFishConf()
    loadRankRewardConf()
    loadBounsGameConf()
    loadAchievementConf()
    loadItemConf()                          # 加载道具配置
    loadHonorConf()
    loadGunTypeConf()                       # 加载皮肤炮炮配置
    loadGunTypeConf_m()                     # 加载千炮皮肤炮炮配置
    loadRobberyConf()
    loadCommonConf()
    loadPlayerBufferConf()
    loadRobotConf()
    loadRandomMultipleFishConf()
    loadGunLevelConf()                      # 加载火炮升级配置
    loadGunLevelConf_m()                    # 加载千炮火炮升级配置
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
    loadLotteryTicActConf()                                 # 加载渔场红包券抽奖配置
    loadPassCardConf()                                      # 加载通行证活动配置
    loadSkillCompenConf()                                   # 加载技能补偿配置
    loadABTestConf()                                        #  加载ab test配置
    loadGiftAbcTestConf()
    loadReturnerMissionConf()                               # 加载回归豪礼配置
    loadMiniGameConf()
    loadLuckyTreeConf()                                     # 加载免费金币摇钱树配置
    loadExchangeStoreConf()
    loadSuperbossPowerConf()                                # 加载超级boss威力配置
    loadLevelPrizeWheelConf()                               # 加载等级转盘(青铜、白银、黄金、铂金、钻石)


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
        getConfigPath("public"): loadPublicConf,            # 加载公共配置
        getConfigPath("scene"): loadSceneGroupConf,         # 加载渔场鱼阵配置
        getConfigPath("scene_m"): loadSceneGroupConf_m,     # 加载千炮渔场鱼阵配置
        getConfigPath("fish"): loadFishConf,
        getConfigPath("fish_m"): loadFishConf_m,
        getConfigPath("weapon"): loadWeaponConf,            # 加载武器配置
        getConfigPath("weapon_m"): loadWeaponConf_m,        # 加载千炮武器配置
        getConfigPath("weaponPowerRate"): loadWeaponPowerRateConf,  # 加载武器威力加成配置
        getConfigPath("checkin"): loadCheckinConf,          # 加载签到配置
        getConfigPath("store"): loadStoreConf,
        getConfigPath("drop"): loadDropConf,                # 加载掉落配置
        getConfigPath("ulevel"): loadUlevelConf,
        getConfigPath("userLevel"): loadUserLevelConf,
        getConfigPath("skill"): loadSkillConf,              # 加载技能配置
        getConfigPath("skillGrade"): loadSkillGradeConf,    # 加载技能等级配置
        getConfigPath("skillGrade_m"): loadSkillGradeConf_m,# 加载千炮技能等级配置
        getConfigPath("skillStar"): loadSkillStarConf,      # 加载技能星级配置
        getConfigPath("skillStar_m"): loadSkillStarConf_m,  # 加载千炮技能星级配置
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
        getConfigPath("probability"): loadProbabilityConf,  # 加载概率配置
        getConfigPath("dynamicOdds"): loadDynamicOddsConf,  # 加载动态概率配置
        getConfigPath("lotteryPool"): loadLotteryPoolConf,
        getConfigPath("gift"): loadGiftConf,
        getConfigPath("activity"): loadActivityConf,
        getConfigPath("catchDrop"): loadCatchDropConf,
        getConfigPath("vip"): loadVipConf,
        getConfigPath("matchFish"): loadMatchFishConf,
        getConfigPath("fixedMultipleFish"): loadFixedMultipleFishConf,  # 加载固定倍率鱼配置
        getConfigPath("callMultipleFish"): loadCallMultipleFishConf,
        getConfigPath("matchMultipleFish"): loadMatchMultipleFishConf,
        getConfigPath("rankReward"): loadRankRewardConf,
        getConfigPath("fishBonusGame"): loadBounsGameConf,
        getConfigPath("achievement"): loadAchievementConf,
        getConfigPath("item"): loadItemConf,                            # 加载道具配置
        getConfigPath("honor"): loadHonorConf,
        getConfigPath("gun"): loadGunTypeConf,                          # 加载皮肤炮炮配置
        getConfigPath("gun_m"): loadGunTypeConf_m,                      # 加载千炮皮肤炮炮配置
        getConfigPath("robbery"): loadRobberyConf,
        getConfigPath("common"): loadCommonConf,
        getConfigPath("playerBuffer"): loadPlayerBufferConf,
        getConfigPath("robot"): loadRobotConf,
        getConfigPath("randomMultipleFish"): loadRandomMultipleFishConf,
        getConfigPath("gunLevel"): loadGunLevelConf,                    # 加载火炮升级配置
        getConfigPath("gunLevel_m"): loadGunLevelConf_m,                # 加载千炮火炮升级配置
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
        getConfigPath("newbie7DaysGift"): loadNewbie7DaysGfitConf,      # 加载默认商店配置
        getConfigPath("lotteryTicket"): loadLotteryTicActConf,          # 加载渔场红包券抽奖配置
        getConfigPath("passCard"): loadPassCardConf,                    # 加载通行证活动配置
        getConfigPath("skillCompensate"): loadSkillCompenConf,          # 加载技能补偿配置
        getConfigPath("abTest"): loadABTestConf,                        # 加载ab test配置
        getConfigPath("giftAbcTest"): loadGiftAbcTestConf,
        getConfigPath("returnerMission"): loadReturnerMissionConf,      # 加载回归豪礼配置
        getConfigPath("miniGame"): loadMiniGameConf,
        getConfigPath("luckyTree"): loadLuckyTreeConf,                  # 加载免费金币摇钱树配置
        getConfigPath("exchangeStore"): loadExchangeStoreConf,
        getConfigPath("superbossPower"): loadSuperbossPowerConf,        # 加载超级boss威力配置
        getConfigPath("prizeWheel_m"): loadLevelPrizeWheelConf,         # 加载等级转盘(青铜、白银、黄金、铂金、钻石)
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