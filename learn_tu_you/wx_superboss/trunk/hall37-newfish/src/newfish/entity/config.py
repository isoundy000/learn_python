# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import time
import random
import json
from collections import OrderedDict
from copy import deepcopy

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
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
# 海洋之星
OCEANSTAR_KINDID = 3157
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
# 千炮模式下普通鱼
NORMAL_FISH_TYPE_M = [1]
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

# -------------------------
# 以下type为武器类别
# 普通火炮
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
# 超级Boss
SUPER_BOSS_WEAPON_TYPE = 9
# 能量宝珠
ENERGY_ORB = 10
# 三叉戟
TRIDENT = 11
# 金钱箱
MONEY_BOX = 12
# 特殊武器类别集合
SPECIAL_WEAPON_TYPE_SET = (BOMB_WEAPON_TYPE, NUMB_WEAPON_TYPE, DRILL_WEAPON_TYPE,
                           SUPER_BOSS_WEAPON_TYPE, ENERGY_ORB, TRIDENT)
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
# 新手渔场
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
# 冰冻道具冻住的概率
FREEZE_PROBB = 10000
# 锁定道具ID
LOCK_ITEM = "14120"

# 购买类型
BT_COIN = "coin"
BT_PEARL = "pearl"
BT_DIAMOND = "diamond"
BT_COUPON = "coupon"
BT_DIRECT = "direct"
BT_VOUCHER = "voucher"
BT_RUBY = "ruby"
BT_OCEANSTAR = "oceanStar"

# 千炮游戏模式
GOLDEN_COIN = 0     # 金币模式
GOLDEN_RING = 1     # 金环模式

# 千炮游戏模式列表
MULTIPLE_MODES_LIST = [GOLDEN_COIN, GOLDEN_RING]

# 游戏玩法
CLASSIC_MODE = 0        # 经典玩法
MULTIPLE_MODE = 1       # 千炮玩法

# 游戏玩法列表
GAME_MODES = [CLASSIC_MODE, MULTIPLE_MODE]

# 新手引导步骤
NEWBIE_GUIDE_GUN_UP = 1003      # 升级
NEWBIE_GUIDE_LOCK = 1004        # 锁定
NEWBIE_GUIDE_FREEZE = 1005      # 冰冻
NEWBIE_GUIDE_MISSILE = 1006     # 合金弹头

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
probabilityConf_m = {}
terrorFishConf = {}
terrorFishConf_m = {}
dynamicOddsConf = {}
lotteryPoolConf = {}
ringLotteryPoolConf = {}
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
superbossExchangeConf = {}
superbossMinigameConf = {}
superbossCommonConf = {}
collectItemConf = {}
poseidonConf = {}
bigPrizeConf = {}
compActConf = {}
newbie7DaysGiftConf = {}
passCardConf = {}
skillCompenConf = {}
abTestConf = {}
returnerMissionConf = {}
miniGameConf = {}
miniGameLevelMap = {}
luckyTreeConf = {}
superbossPowerConf = {}
levelPrizeWheelConf = {}
timePointMatchSkillConf = {}
autofillFishConf_m = {}
tideTaskConf = {}


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
        return skillGradeConf_m.get(str(skillId), {}).get(str(level), {})
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
        conf = fishConf_m.get(str(fishType), {}) if typeName != FISH_FRIEND else fishConf.get(str(fishType), {})
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


def loadTimeLimitedStoreConf():
    """
    加载限时商城
    """
    global timeLimitedStoreConf
    timeLimitedStoreConf = rocopy(getGameConf("timeLimitedStore"))


def getTimeLimitedStoreConf():
    """
    获取限时商城配置
    """
    global timeLimitedStoreConf
    return timeLimitedStoreConf


def loadExchangeStoreConf():
    """
    加载兑换商城
    """
    global exchangeStoreConf
    exchangeStoreConf = rocopy(getGameConf("exchangeStore"))


def getExchangeStoreConf():
    """
    获取兑换商城配置
    """
    global exchangeStoreConf
    return exchangeStoreConf


def loadStoreConf(intClientId=0):
    """
    加载默认商店配置
    """
    global storeConf
    _conf = getGameConf("store", intClientidNum=intClientId)
    storeConf[intClientId] = rocopy(generateStoreConf(_conf)) if _conf else {}


def generateStoreConf(conf):
    """
    生成clientId对应的商店配置
    """
    coinStoreConfTmp = conf.get("coinStore", {}).get("items", {})
    coinStoreConf = OrderedDict(sorted(coinStoreConfTmp.iteritems(), key=lambda d: d[1]["order"]))

    diamondStoreConfTmp = conf.get("diamondStore", {}).get("items", {})
    diamondStoreConf = OrderedDict(sorted(diamondStoreConfTmp.iteritems(), key=lambda d: d[1]["order"]))

    pearlStoreConfTmp = conf.get("pearlStore", {})
    pearlStoreConf = OrderedDict(sorted(pearlStoreConfTmp.iteritems(), key=lambda d: d[1]["order"]))

    itemStoreConfTmp = conf.get("itemStore", {}).get("items", {})
    itemStoreConf = OrderedDict(sorted(itemStoreConfTmp.iteritems(), key=lambda d: d[1]["order"]))

    chestStoreConfTmp = conf.get("chestStore").get("items")
    chestStoreConf = OrderedDict()

    chestStoreConf["items"] = OrderedDict(sorted(chestStoreConfTmp.iteritems(), key=lambda d: d[1]["order"]))
    chestStoreConf["ads"] = conf.get("chestStore").get("ads")

    couponStoreConfTmp = conf.get("couponStore", {}).get("items", {})
    couponStoreConf = OrderedDict(sorted(couponStoreConfTmp.iteritems(), key=lambda d: d[1]["order"]))

    gunSkinStoreConfTmp = conf.get("gunSkinStore", {})
    gunSkinStoreConf = OrderedDict(sorted(gunSkinStoreConfTmp.iteritems(), key=lambda d: d[1]["order"]))

    bulletStoreConfTmp = conf.get("bulletStore", {})
    bulletStoreConf = OrderedDict()
    for platform, _conf in bulletStoreConfTmp.iteritems():
        _conf = OrderedDict(sorted(_conf.iteritems(), key=lambda d: d[1]["order"]))
        bulletStoreConf[platform] = _conf

    # 处理热卖商城商品配置.
    hotStoreConfTmp = conf.get("hotStore", {}).get("items", {})
    hotStoreConfTmp = OrderedDict(sorted(hotStoreConfTmp.iteritems(), key=lambda d: d[1]["order"]))
    hotStoreConf = OrderedDict()
    hotStoreConf["items"] = OrderedDict()
    for productId, v in hotStoreConfTmp.iteritems():
        if v.get("pt") == "coin":
            product = coinStoreConf.get(str(productId))
        elif v.get("pt") == "diamondStore":
            product = diamondStoreConf.get(str(productId))
        elif v.get("pt") == "chestStore":
            product = chestStoreConf["items"].get(str(productId))
        elif v.get("pt") == "itemStore":
            product = itemStoreConf.get(str(productId))
        else:
            product = None
        if product:
            productConf = deepcopy(product)
            productConf["pt"] = v["pt"]
            productConf["extendData"].update(v.get("extendData", {}))
            productConf["limitCond"].update(v.get("limitCond", {}))
            hotStoreConf["items"][str(productId)] = productConf
    hotStoreConf["shop"] = conf.get("hotStore", {}).get("shop", {})

    generateConf = OrderedDict()
    generateConf["coinStore"] = {}                                          # 金币商店商品
    generateConf["diamondStore"] = {}
    generateConf["itemStore"] = {}
    generateConf["chestStore"] = {}
    generateConf["couponStore"] = {}
    generateConf["coinStore"].setdefault("items", coinStoreConf)
    generateConf["diamondStore"].setdefault("items", diamondStoreConf)
    generateConf["pearlStore"] = pearlStoreConf
    generateConf["itemStore"].setdefault("items", itemStoreConf)
    generateConf["chestStore"] = chestStoreConf
    generateConf["couponStore"].setdefault("items", couponStoreConf)
    generateConf["gunSkinStore"] = gunSkinStoreConf
    generateConf["bulletStore"] = bulletStoreConf
    generateConf["hotStore"] = hotStoreConf
    return generateConf


def getStoreConf(clientId=None):
    """
    获取clientId对应的商店配置
    """
    global storeConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if storeConf.get(intClientId) is None:
        loadStoreConf(intClientId)
    if storeConf.get(intClientId):
        return storeConf[intClientId]
    return storeConf[defaultIntClientId]


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


def loadMainQuestConf(intClientId=0):
    """
    加载主线任务配置
    """
    global mainQuestConf
    _conf = getGameConf("mainQuest", intClientidNum=intClientId)
    if _conf:
        tasks = OrderedDict(sorted(_conf.get("tasks", {}).iteritems()))
        sections = OrderedDict(sorted(_conf.get("sections", {}).iteritems()))
        _mainQuestConf = OrderedDict()
        _mainQuestConf["tasks"] = rocopy(tasks)
        _mainQuestConf["sections"] = rocopy(sections)
        mainQuestConf[intClientId] = rocopy(_mainQuestConf)
    else:
        mainQuestConf[intClientId] = {}


def _getMainQuestTaskConfByClientId(clientId):
    """
    获取clientId对应的主线任务中章节任务配置
    """
    global mainQuestConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if mainQuestConf.get(intClientId) is None:
        loadMainQuestConf(intClientId)
    if mainQuestConf.get(intClientId):
        return mainQuestConf[intClientId]
    return mainQuestConf[defaultIntClientId]


def getMainQuestTaskConf(clientId, taskId=None):
    """
    获取主线任务中章节任务配置
    """
    _mainQuestConf = _getMainQuestTaskConfByClientId(clientId)
    if taskId is None:
        return _mainQuestConf.get("tasks", {})
    return _mainQuestConf.get("tasks", {}).get(str(taskId), {})


def getMainQuestTasksConfByType(clientId, questType):
    """
    获取主线任务中指定任务类型的所有任务配置
    """
    _mainQuestConf = _getMainQuestTaskConfByClientId(clientId)
    tasksConf = []
    for _, _taskConf in _mainQuestConf.get("tasks", {}).iteritems():
        if _taskConf["type"] == questType:
            tasksConf.append(_taskConf)
    return tasksConf


def getMainQuestSectionConf(clientId, sectionId=None):
    """
    获取主线任务中章节配置
    """
    _mainQuestConf = _getMainQuestTaskConfByClientId(clientId)
    if sectionId is None:
        return _mainQuestConf.get("sections", {})
    return _mainQuestConf.get("sections", {}).get(str(sectionId), {})


def loadDailyQuestConf():
    """
    加载每日任务配置
    """
    global dailyQuestConf
    dailyQuestConf = rocopy(getGameConf("dailyQuest"))
    global dailyQuestsByTypeConf
    dailyQuestsByTypeConf = {}
    for _, dailyQuest in dailyQuestConf.get("questData", {}).iteritems():
        dailyQuestsByTypeConf.setdefault(dailyQuest.get("taskType"), []).append(rwcopy(dailyQuest))


def getDailyQuestConf(taskId=None):
    """
    获取每日任务配置
    """
    global dailyQuestConf
    if taskId is None:
        return dailyQuestConf.get("questData", {})
    return dailyQuestConf.get("questData", {}).get(str(taskId), {})


def getDailyQuestGroupOrder():
    """
    获取每日任务分组排序
    """
    global dailyQuestConf
    return dailyQuestConf.get("questOrder", [])


def getDailyQuestConfsByType(taskType):
    """
    获取该任务类型下的所有每日任务
    """
    global dailyQuestsByTypeConf
    return dailyQuestsByTypeConf.get(taskType, [])


def getDailyQuestRefreshConf():
    """
    获取每日任务刷新数据
    """
    global dailyQuestConf
    return dailyQuestConf.get("refreshData", {})


def loadDailyQuestRewardConf():
    """
    加载每日任务奖励配置
    """
    global dailyQuestRewardConf, dailyQuestRewardFinishedStars
    rewardConf = getGameConf("dailyQuestReward").values()[-1]
    for k, v in rewardConf.iteritems():
        dailyQuestRewardFinishedStars.setdefault(v.get("type"), {})
        stars = json.loads(v.get("finishedStar", "[0, 0]"))
        dailyQuestRewardFinishedStars[v.get("type")].setdefault(0, []).append(stars[0])
        dailyQuestRewardFinishedStars[v.get("type")].setdefault(1, []).append(stars[1])
    for k in dailyQuestRewardFinishedStars.keys():
        for k1 in dailyQuestRewardFinishedStars[k].keys():
            dailyQuestRewardFinishedStars[k][k1].sort()

    dailyQuestRewardConf = {}
    for key, val in getGameConf("dailyQuestReward").iteritems():
        dailyQuestRewardConf[key] = {}
        for k1, v1 in val.iteritems():
            k1 = json.loads(k1)
            dailyQuestRewardConf[key].setdefault(0, {})
            dailyQuestRewardConf[key][0][str(k1[0])] = rwcopy(v1)
            dailyQuestRewardConf[key][0][str(k1[0])]["finishedStar"] = int(k1[0])
            dailyQuestRewardConf[key].setdefault(1, {})
            dailyQuestRewardConf[key][1][str(k1[1])] = rwcopy(v1)
            dailyQuestRewardConf[key][1][str(k1[1])]["finishedStar"] = int(k1[1])
    if ftlog.is_debug():
        ftlog.debug("loadDailyQuestRewardConf", dailyQuestRewardFinishedStars, dailyQuestRewardConf)


def getDailyQuestRewardConf(activeLv=None, all=True):
    """
    获取每日任务奖励配置
    """
    global dailyQuestRewardConf
    if activeLv:
        if all:
            return dailyQuestRewardConf.get(str(activeLv), {}).get(1, {})
        else:
            return dailyQuestRewardConf.get(str(activeLv), {}).get(0, {})
    else:
        return dailyQuestRewardConf


def getDailyQuestRewardFinishedStars(type, all=True):
    """
    获取每日任务阶段奖励对应星星数
    """
    global dailyQuestRewardFinishedStars
    if all:
        finishedStars = dailyQuestRewardFinishedStars.get(type).get(1, [])
    else:
        finishedStars = dailyQuestRewardFinishedStars.get(type).get(0, [])
    if ftlog.is_debug():
        ftlog.debug("getDailyQuestRewardFinishedStars", type, all, finishedStars)
    return finishedStars


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


def loadProbabilityConf():
    """
    加载概率配置
    """
    global probabilityConf
    probabilityConf = rocopy(getGameConf("probability"))


def loadProbabilityConf_m():
    """
    加载概率配置
    """
    global probabilityConf_m
    probabilityConf_m = rocopy(getGameConf("probability_m"))


def getCouponFishConf(fishPool):
    """
    获取奖券鱼配置
    """
    global probabilityConf
    return probabilityConf.get("couponFish", {}).get(str(fishPool), {})


def getMultipleFishConf(fishPool, mode=CLASSIC_MODE):
    """
    获取倍率鱼配置
    """
    global probabilityConf, probabilityConf_m
    if mode == CLASSIC_MODE:
        return probabilityConf.get("multipleFish", {}).get(str(fishPool), [])
    return probabilityConf_m.get("multipleFish", {}).get(str(fishPool), [])


def getBossFishConf(fishPool, mode=CLASSIC_MODE):
    """
    获取Boss鱼配置
    """
    global probabilityConf, probabilityConf_m
    if mode == CLASSIC_MODE:
        return probabilityConf.get("bossFish", {}).get(str(fishPool), [])
    return probabilityConf_m.get("bossFish", {}).get(str(fishPool), [])


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


def getBufferFishConf(fishPool, mode=CLASSIC_MODE):
    """
    获取Buffer鱼配置
    """
    global probabilityConf, probabilityConf_m
    if mode == CLASSIC_MODE:
        return probabilityConf.get("bufferFish", {}).get(str(fishPool), [])
    return probabilityConf_m.get("bufferFish", {}).get(str(fishPool), [])


def getHippoFishConf(fishPool):
    """
    获取河马鱼配置
    """
    global probabilityConf
    return probabilityConf.get("hippoFish", {}).get(str(fishPool), [])


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


def loadTerrorFishConf():
    """
    加载特殊鱼
    """
    global terrorFishConf
    terrorFishConf = rocopy(getGameConf("terrorFish"))


def loadTerrorFishConf_m():
    """
    加载特殊鱼
    """
    global terrorFishConf_m
    terrorFishConf_m = rocopy(getGameConf("terrorFish_m"))


def getTerrorFishConf(fishPool, mode=CLASSIC_MODE):
    """
    获取恐怖鱼配置
    """
    global terrorFishConf, terrorFishConf_m
    if mode == CLASSIC_MODE:
        return terrorFishConf.get("terrorFish", {}).get(str(fishPool), [])
    else:
        return terrorFishConf_m.get("terrorFish_m", {}).get(str(fishPool), [])


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


def loadLotteryPoolConf():
    """
    加载普通渔场金币奖池配置
    """
    global lotteryPoolConf
    lotteryPoolConf = rocopy(getGameConf("lotteryPool"))


def getLotteryPoolConf(fishPool):
    """
    获取普通渔场金币奖池配置
    """
    global lotteryPoolConf
    return lotteryPoolConf.get(str(fishPool), {})

def loadRingLotteryPoolConf():
    """
    加载普通渔场金币奖池配置
    """
    global ringLotteryPoolConf
    ringLotteryPoolConf = rocopy(getGameConf("ringLotteryPool"))

def getRingLotteryPoolConf(fishPool):
    """
    获取普通渔场金环奖池配置
    """
    global ringLotteryPoolConf
    return ringLotteryPoolConf.get(str(fishPool), {})


def loadGiftConf(intClientId=0):
    """
    加载所有礼包配置
    """
    global giftConf
    _conf = getGameConf("gift", intClientidNum=intClientId)
    giftConf[intClientId] = rocopy(_conf) if _conf else {}


def _getGiftConfByClientId(clientId):
    """
    获取clientId对应的礼包配置
    """
    global giftConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if giftConf.get(intClientId) is None:
        loadGiftConf(intClientId)
    if giftConf.get(intClientId):
        return giftConf[intClientId]
    return giftConf[defaultIntClientId]


def getGiftConf(clientId, giftId=None):
    """
    获取礼包配置
    """
    _giftConf = _getGiftConfByClientId(clientId)
    if giftId is None:
        return _giftConf.get("gift", {})
    return _giftConf.get("gift", {}).get(str(giftId), {})


def loadGiftAbcTestConf(intClientId=0):
    """
    加载礼包abc测试配置
    """
    global giftAbcTestConf
    _conf = getGameConf("giftAbcTest", intClientidNum=intClientId)
    giftAbcTestConf[intClientId] = rocopy(_conf) if _conf else {}


def getGiftAbcTestConf(clientId):
    """
    获取礼包abc测试配置
    """
    global giftAbcTestConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if giftAbcTestConf.get(intClientId) is None:
        loadGiftAbcTestConf(intClientId)
    if giftAbcTestConf.get(intClientId):
        return giftAbcTestConf[intClientId]
    return giftAbcTestConf[defaultIntClientId]



def getLimitTimeGiftConf(clientId, fishPool):
    """
    加载限时礼包配置
    """
    _giftConf = _getGiftConfByClientId(clientId)
    for giftId, gift in _giftConf.get("gift", {}).iteritems():
        if gift.get("fishPool") == fishPool and gift.get("giftType") == 1:
            return gift
    return None


def getGiftListConf(clientId, giftType):
    """
    获取礼包种类列表配置
    """
    _giftConf = _getGiftConfByClientId(clientId)
    gifts = []
    for giftId in sorted(_giftConf.get("gift", {}).keys()):
        if _giftConf.get("gift", {}).get(giftId).get("giftType") == giftType:
            gifts.append(int(giftId))
    return gifts


def getDailyGiftConf(clientId):
    """
    获取每日礼包配置
    """
    _giftConf = _getGiftConfByClientId(clientId)
    return _giftConf.get("dailyGift", {})


def fromStrToJson(strInfo):
    try:
        jsStr = json.loads(strInfo)
    except:
        jsStr = strInfo
    return jsStr


def loadActivityConf():
    """
    加载活动配置
    """
    from newfish.entity.fishactivity.fish_activity import AcTableTypes
    global activityConf
    _activityConf = getGameConf("activity")
    activityInfoConf = _activityConf.get("activityInfo", {})
    for acInfo in activityInfoConf.values():
        acInfo["reward"] = fromStrToJson(acInfo.get("reward", ""))
        if "task" in acInfo:
            for taskInfo in acInfo.get("task", {}).values():
                taskInfo["value"] = fromStrToJson(taskInfo.get("value", ""))
                taskInfo["reward"] = fromStrToJson(taskInfo.get("reward", ""))
                taskInfo["frontTasks"] = fromStrToJson(taskInfo.get("frontTasks", ""))
                if taskInfo.get("spareReward"):
                    taskInfo["spareReward"] = fromStrToJson(taskInfo.get("spareReward", ""))
                if taskInfo["type"] in AcTableTypes and not acInfo.get("hasTableTask", False):
                    acInfo["hasTableTask"] = True
    activityConf = rocopy(_activityConf)
    if gdata.serverType() == gdata.SRV_TYPE_UTIL:
        FTLoopTimer(300, 0, checkActivityItemConf).start()


def getActivityConfig():
    """
    获取所有活动配置
    """
    global activityConf
    return activityConf.get("activityInfo", {})


def getNoticeConf(noticeId=None):
    """
    获取公告配置
    """
    global activityConf
    if noticeId:
        return activityConf.get("notice", {}).get(str(noticeId))
    else:
        return activityConf.get("notice", {})


def getActivityTemplateByClientIdNum(clientIdNum, lang):
    """
    获取ClientId对应活动模板
    """
    global activityConf
    clientInfos = activityConf.get("activityClient", {}).get(lang, {})
    return clientInfos.get(str(clientIdNum), 1)


def getActivityConfigById(acId):
    """
    获取活动配置
    """
    global activityConf
    return activityConf.get("activityInfo", {}).get(str(acId), {})


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
        if kindId:
            dropConf = {}
            dropConf["kindId"] = kindId
            dropConf["min"] = _conf["min"]
            dropConf["max"] = _conf["max"]
            dropConf["probability"] = _conf["probability"]
    if ftlog.is_debug():
        ftlog.debug("getCatchDropConf===>", fpMultiple, fishType, uid, dropConf)
    return dropConf


def _getCatchDropKindId(groupId, uid):
    """
    根据玩家uid和掉落组返回掉落kindId
    """
    groupId = str(groupId)
    kindId = None
    global catchDropConf
    if catchDropConf.get("dropGroup"):
        dropList = catchDropConf["dropGroup"].get(groupId, [])
        idx = int(uid) % 2
        if len(dropList) > idx:
            total = 0
            for item in dropList[idx]:
                total += item["poss"]
            ret = random.randint(1, total)
            old_ret = ret
            for item in dropList[idx]:
                if item["poss"] >= ret:
                    kindId = int(item["kindId"])
                    break
                else:
                    ret -= item["poss"]
            if ftlog.is_debug():
                ftlog.debug("_getCatchDropKindId===>", groupId, uid, dropList[idx], idx, total, old_ret, kindId)
    return kindId


def _getCatchDropGroupConf(fpMultiple, fishType):
    """
    根据渔场和捕到的鱼的类型获得掉落组
    """
    global catchDropConf
    fpList = catchDropConf.get("fishDrop").keys()
    fpList = sorted([int(val) for val in fpList])
    finalFp = fpMultiple
    for val in fpList:
        if fpMultiple >= val:
            finalFp = val
    finalFp = str(finalFp)
    fishType = str(fishType)
    dropConf = None
    if catchDropConf.get("fishDrop") and catchDropConf["fishDrop"].get(finalFp) \
            and catchDropConf["fishDrop"][finalFp].get(fishType):
        dropGroupList = catchDropConf["fishDrop"][finalFp][fishType]
        if len(dropGroupList) > 1:
            total = 0
            for item in dropGroupList:
                total += item["dropGroupPoss"]
            ret = random.randint(1, total)
            old_ret = ret
            for item in dropGroupList:
                if item["dropGroupPoss"] >= ret:
                    dropConf = item# rocopy(item)
                    break
                else:
                    ret -= item["dropGroupPoss"]
            if ftlog.is_debug():
                ftlog.debug("_getCatchDropGroupId 2 ===>", fpMultiple, finalFp, fishType, total, old_ret, dropGroupList)
        elif len(dropGroupList) == 1:
            dropConf = dropGroupList[0]# rocopy(dropGroupList[0])
    if ftlog.is_debug():
        ftlog.debug("_getCatchDropGroupId===>", fpMultiple, finalFp, fishType, dropConf)
    return dropConf


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


def loadCallMultipleFishConf():
    """
    加载召唤鱼配置
    """
    global callMultipleFishConf
    callMultipleFishConf = rocopy(getGameConf("callMultipleFish"))


def getCallMultipleFishConf(skillGrade, typeName, fishPool):
    """
    获取召唤鱼配置
    """
    global callMultipleFishConf
    if typeName in [FISH_TIME_MATCH, FISH_TIME_POINT_MATCH]:
        fishConf = rwcopy(callMultipleFishConf.get("match", {}).get(str(skillGrade), []))
    else:
        fishConf = rwcopy(callMultipleFishConf.get("normal", {}).get(str(skillGrade), []))
    validFishList = callMultipleFishConf.get("validGroup", {}).get(str(fishPool), None)
    # ftlog.debug("getCallMultipleFishConf 1", validFishList, fishConf, fishPool)
    if validFishList is not None:
        for fish in fishConf:
            if fish["fishType"] not in validFishList:
                fish["weight"] = 0
    # ftlog.debug("getCallMultipleFishConf 2", validFishList, fishConf, fishPool)
    return fishConf


def loadMatchMultipleFishConf():
    """
    加载比赛倍率鱼配置
    """
    global matchMultipleFishConf
    matchMultipleFishConf = rocopy(getGameConf("matchMultipleFish"))


def getMatchMultipleFishConf(fishPool, luckyValue):
    """
    获取比赛倍率鱼配置
    """
    global matchMultipleFishConf
    for d in matchMultipleFishConf.get(str(fishPool), []):
        if luckyValue <= d["luckyValue"]:
            if ftlog.is_debug():
                ftlog.debug("getMatchMultipleFishConf->", luckyValue, d)
            return d["multiples"]
    return []


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


def loadBounsGameConf():
    """
    加载海星抽奖配置
    """
    global bonusGameConf
    bonusGameConf = rocopy(getGameConf("fishBonusGame"))


def loadStarfishRouletteConf():
    """
    加载海星转盘抽奖配置
    """
    global starfishRouletteConf
    starfishRouletteConf = rocopy(getGameConf("starfishRoulette"))


def getStarfishBonusConf():
    """
    获取海星抽奖配置
    """
    global bonusGameConf
    starfishBonusConfig = bonusGameConf.get("starfishBonus", [])
    starfishBonusConfig = sorted(starfishBonusConfig, key=lambda rewardInfo: rewardInfo["Id"])
    return starfishBonusConfig


def getStarfishRouletteConf():
    """
    获取海星转盘抽奖配置
    """
    global starfishRouletteConf
    starfishConf = starfishRouletteConf.get("starfishRoulette", [])
    starfishConf = sorted(starfishConf, key=lambda rewardInfo: rewardInfo["Id"])
    return starfishConf


def getStarfishRoulettePriceConf():
    """
    获取海星转盘价格配置
    """
    global starfishRouletteConf
    priceConf = starfishRouletteConf.get("priceInfo", {})
    return priceConf


def getStarfishRouletteLevelConf():
    """
    获取海星转盘等级配置
    """
    global starfishRouletteConf
    levelConf = starfishRouletteConf.get("rouletteLevel", [])
    return levelConf


def getStarfishRouletteUnlockConf():
    """
    获取海星转盘解锁等级配置
    """
    global starfishRouletteConf
    unlockLevel = starfishRouletteConf.get("unlockLevel", 0)
    return unlockLevel


def getStarfishRouletteRuleConf():
    """
    获取海星转盘规则
    """
    global starfishRouletteConf
    rule = starfishRouletteConf.get("rule", "")
    return rule


def getBonusConf(keyName, sortKey="weight"):
    """
    获取扭蛋抽奖配置
    """
    global bonusGameConf
    gameTimeBonusConfig = bonusGameConf.get(str(keyName), [])
    gameTimeBonusConfig = sorted(gameTimeBonusConfig, key=lambda bonusInfo: bonusInfo[sortKey])
    return gameTimeBonusConfig


def getBonusHashConf(keyName):
    """
    获取抽奖配置
    """
    global bonusGameConf
    gameTimeBonusConfig = bonusGameConf.get(str(keyName), {})
    return gameTimeBonusConfig


def getEggsBonusDropConf():
    """
    获取扭蛋奖励列表配置
    """
    global bonusGameConf
    return bonusGameConf.get("eggs_dropConf", {})


def getEggsMinCoinRangeConf(kindId):
    """
    获取扭蛋最小值配置
    """
    global bonusGameConf
    return bonusGameConf.get("eggs_minCoinRange", {}).get(str(kindId), [100, 100])


def loadSurpassTargetConf():
    """
    加载比赛超越目标配置
    """
    global surpassTargetConf
    surpassTargetConf = rocopy(getGameConf("surpassTarget"))


def getSurpassTargetConf():
    """
    获取比赛超越目标配置
    """
    global surpassTargetConf
    return surpassTargetConf


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


def loadAchievementConf():
    """
    加载荣耀任务配置
    """
    global achievementConf
    achievementConf = rocopy(getGameConf("achievement"))


def getAchievementConf():
    """
    获取荣耀任务配置
    """
    global achievementConf
    return achievementConf


def getAchievementTaskInfo(keyName):
    """
    获取荣耀任务信息
    """
    global achievementConf
    return achievementConf.get("tasks", {}).get(keyName)


def getAchievementLevelConfig(keyName):
    """
    获取荣耀任务信息
    """
    global achievementConf
    return achievementConf.get("level", {}).get(str(keyName))


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
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
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


def loadHonorConf():
    """
    加载称号配置
    """
    global honorConf
    honorConf = rocopy(getGameConf("honor"))


def getHonorConf(honorId=None):
    """
    获取称号配置
    """
    global honorConf
    if honorId is None:
        return honorConf
    return honorConf.get(str(honorId), {})


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


def loadRobberyConf():
    """
    加载招财模式配置
    """
    global robberyConf
    robberyConf = rocopy(getGameConf("robbery"))


def getRobberyConf():
    """
    获取招财模式配置
    """
    global robberyConf
    return robberyConf


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


def getIgnoreConf(key, clientId=""):
    """
    获取屏蔽数据
    """
    global commonConf
    _confList = commonConf.get("ignoreConf", [])
    for _conf in _confList:
        if clientId in _conf.get("clientIds", []):
            return _conf.get(key)
    return None


def isClientIgnoredConf(key, val, clientId=""):
    """
    数据是否对客户端被屏蔽
    """
    _conf = getIgnoreConf(key, clientId)
    if _conf is None:
        return False
    if isinstance(_conf, int):
        return _conf == val
    else:
        return val in _conf


def loadPlayerBufferConf():
    """
    加载用户buffer配置
    """
    global playerBufferConf
    playerBufferConf = rocopy(getGameConf("playerBuffer"))


def getPlayerBufferConf(bufferId):
    """
    获取buffer配置
    """
    global playerBufferConf
    return playerBufferConf.get(str(bufferId), {})


def getAllBufferIds():
    """
    获取buffer配置
    """
    global playerBufferConf
    allKeys = playerBufferConf.keys()
    return allKeys


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
    global gunLevelConf
    gunLevelConfTmp = getGameConf("gunLevel")
    gunLevels = sorted(gunLevelConfTmp.iteritems(), key=lambda d: d[0])
    gunLevelConf = OrderedDict()
    for key, value in gunLevels:
        gunLevelConf[key] = value
    gunLevelConf = rocopy(gunLevelConf)


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


def loadTableTaskConf():
    """
    加载主线任务配置
    """
    global tableTaskConf
    tableTaskConf = rocopy(getGameConf("tableTask"))


def getAllTableTaskIds(roomId):
    """
    加载主线任务配置
    """
    global tableTaskConf
    idsConfs = tableTaskConf.get("roomTask", {}).get(str(roomId), {})
    return idsConfs


def getTableTaskConfById(taskId):
    global tableTaskConf
    return tableTaskConf.get("tasks", {}).get(str(taskId), {})


def loadInviteTaskConf():
    """
    加载邀请奖励配置
    """
    global inviteTaskConf
    inviteTaskConf = rocopy(getGameConf("inviteTask"))


def getInviteTasks(actionType):
    """
    获取邀请任务数值
    """
    global inviteTaskConf
    return inviteTaskConf.get("inviteTask", {}) if actionType == 0 else inviteTaskConf.get("recallTask", {})


def getInviteTaskConf(taskId, actionType):
    """
    获取邀请任务数值
    """
    global inviteTaskConf
    if actionType == 0:
        return inviteTaskConf.get("inviteTask", {}).get(str(taskId))
    return inviteTaskConf.get("recallTask", {}).get(str(taskId))


def loadRechargePoolConf():
    """
    加载充值奖池配置
    """
    global rechargePoolConf
    rechargePoolConf = rocopy(getGameConf("rechargePool"))


def getRechargePoolConf(productId):
    """
    获取充值奖池配置
    """
    global rechargePoolConf
    return rechargePoolConf.get(productId, {})


def loadShareConf():
    """
    加载分享配置
    """
    global shareConf
    shareConf = rocopy(getGameConf("share"))


def getShareConf(shareId=None, typeId=None):
    """
    获取分享配置
    """
    global shareConf
    if shareId:
        return shareConf.get(str(shareId), {})
    elif typeId:
        for _, conf in shareConf.iteritems():
            if conf["typeId"] == typeId:
                return conf
    return shareConf


def loadFlyPigRewardConf():
    """
    加载金猪分享奖励配置
    """
    global flyPigRewardConf
    flyPigRewardConf = rocopy(getGameConf("flyPigReward"))


def getFlyPigRewardConf(fishPool):
    """
    获取金猪分享奖励配置
    """
    global flyPigRewardConf
    return flyPigRewardConf.get(str(fishPool), [])


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


def loadReportFishCBConf():
    """
    加载上报捕鱼成本配置
    """
    global reportFishCBConf
    reportFishCBConf = rocopy(getGameConf("reportFishCB"))


def getReportFishCBConf(fishPool):
    global reportFishCBConf
    return reportFishCBConf.get(str(fishPool), {})


def loadIdCardAreaConf():
    """
    加载身份证地区配置
    """
    global idCardAreaConf
    idCardAreaConf = rocopy(getGameConf("idCard"))


def getIdCardAreaConf(areaId):
    global idCardAreaConf
    return areaId in idCardAreaConf


def loadGrandPrizeConf():
    """
    加载巨奖奖池配置
    """
    global grandPrizeConf
    grandPrizeConf = rocopy(getGameConf("grandPrize"))


def getGrandPrizeConf():
    """
    获取巨奖奖池配置
    """
    global grandPrizeConf
    return grandPrizeConf


def loadPiggyBankConf(intClientId=0):
    """
    加载存钱罐配置
    """
    global piggyBankConf
    _conf = getGameConf("piggyBank", intClientidNum=intClientId)
    piggyBankConf[intClientId] = rocopy(_conf) if _conf else {}


def _getPiggyBankConfByClientId(clientId):
    """
    根据clientId找到对应存钱罐配置
    """
    global piggyBankConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if piggyBankConf.get(intClientId) is None:
        loadPiggyBankConf(intClientId)
    if piggyBankConf.get(intClientId):
        return piggyBankConf[intClientId]
    return piggyBankConf[defaultIntClientId]


def getPiggyBankConf(clientId, vipLevel):
    """
    获取存钱罐配置
    """
    _piggyBankConf = _getPiggyBankConfByClientId(clientId)
    return _piggyBankConf.get(str(vipLevel), {})


def getPiggyBankProduct(clientId, productId):
    """
    获取存钱罐商品数据
    """
    _piggyBankConf = _getPiggyBankConfByClientId(clientId)
    for _, v in _piggyBankConf.iteritems():
        for _, v1 in v.iteritems():
            if v1.get("productId", "") == productId:
                return v1
    return None


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
        if level is not None:
            return _conf.get("levels", {}).get(str(level))
        return _conf
    return treasureConf


def loadBuyTypeConf():
    """
    加载支付方式配置
    """
    global buyTypeConf
    buyTypeConf = rocopy(getGameConf("buyType"))


def isThirdBuyType(buyType):
    """
    是否为第三方渠道支付
    """
    return buyType in buyTypeConf.get("thirdBuyType", {})


def getBuyTypeConf(buyType):
    """
    获取支付方式配置
    """
    global buyTypeConf
    return buyTypeConf.get("defaultBuyType", {}).get(buyType) or \
           buyTypeConf.get("thirdBuyType", {}).get(buyType)


def loadLevelRewardsConf(intClientId=0):
    """
    加载等级奖励配置
    """
    global levelRewardsConf
    _conf = getGameConf("levelRewards", intClientidNum=intClientId)
    levelRewardsConf[intClientId] = rocopy(_conf) if _conf else {}


def _getLevelRewardsConfByClientId(clientId):
    """
    获取clientId对应的等级奖励配置
    """
    global levelRewardsConf
    intClientId = configure.clientIdToNumber(clientId) if clientId else defaultIntClientId
    if levelRewardsConf.get(intClientId) is None:
        loadLevelRewardsConf(intClientId)
    if levelRewardsConf.get(intClientId):
        return levelRewardsConf[intClientId]
    return levelRewardsConf[defaultIntClientId]


def getLevelRewards(clientId, level=None):
    """
    获取等级奖励配置
    """
    _levelRewardsConf = _getLevelRewardsConfByClientId(clientId)
    if level is None:
        return _levelRewardsConf
    return _levelRewardsConf.get(str(level), {})


def loadUpdateVerRewardsConf():
    """
    加载更版奖励配置
    """
    global updateVerRewardsConf
    updateVerRewardsConf = rocopy(getGameConf("updateVerRewards"))


def getUpdateVerRewardsConf():
    """
    获取更版奖励配置
    """
    global updateVerRewardsConf
    return updateVerRewardsConf


def loadItemMonitorConf():
    """
    加载物品监测配置
    """
    global itemMonitorConf
    itemMonitorConf = rocopy(getGameConf("itemMonitor"))


def getItemMonitorConf():
    """
    获取物品监测配置
    """
    global itemMonitorConf
    return itemMonitorConf


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


def loadSlotMachineConf():
    """
    加载老虎机活动配置
    """
    global slotMachineConf
    slotMachineConf = rocopy(getGameConf("slotMachine"))


def getSlotMachineConf():
    """
    获取老虎机活动转盘抽奖配置
    """
    global slotMachineConf
    slotMachinePropConf = slotMachineConf.get("slotmachine", [])
    return slotMachinePropConf


def getSlotMachineIntegralConf():
    """
    获取老虎机活动积分奖励配置
    """
    global slotMachineConf
    slotMachineIntegralConf = slotMachineConf.get("integralrewards", [])
    return slotMachineIntegralConf


def getSlotMachineFreeTimeConf():
    """
    获取老虎机活动免费抽奖时间配置
    """
    global slotMachineConf
    slotMachineFreeTimeConf = slotMachineConf.get("freetime", [])
    return slotMachineFreeTimeConf


def getSlotMachineMaxPlayTimeConf():
    """
    获取老虎机活动抽奖次数配置
    """
    global slotMachineConf
    maxPlayTimes = slotMachineConf.get("maxPlayTimes", -1)
    return maxPlayTimes


def getSlotMachineOutProductIdConf():
    """
    获取老虎机活动不记录抽奖次数的充值商品配置
    """
    global slotMachineConf
    outProductId = slotMachineConf.get("outProductId", [])
    return outProductId


def loadStatisPropConf():
    """
    加载需要统计上报BI的道具配置
    """
    global statisPropConf
    statisPropConf = rocopy(getGameConf("statisProp"))


def getStatisPropConf():
    """
    获取需要统计并上报BI的道具配置
    """
    global statisPropConf
    statisBiPropConf = statisPropConf.get("statisPropId", [])
    return statisBiPropConf


def loadMoneyTreeConf():
    """
    加载摇钱树活动配置
    """
    global moneyTreeConf
    moneyTreeConf = rocopy(getGameConf("moneyTree"))


def getMoneyTreeConf(key_=None):
    """
    获取摇钱树活动配置
    """
    global moneyTreeConf
    if key_ is None:
        return moneyTreeConf
    return rwcopy(moneyTreeConf.get(str(key_)))


def loadCannedFishConf():
    """
    加载鱼罐厂活动配置
    """
    global cannedFishConf
    cannedFishConf = rocopy(getGameConf("cannedFish"))


def getCannedFishConf(key_=None):
    """
    获取鱼罐厂配置
    """
    global cannedFishConf
    if key_ is None:
        return cannedFishConf
    return rwcopy(cannedFishConf.get(str(key_)))


def getWelfareCan():
    """
    获取鱼罐厂(世界工厂)中的福利罐头配置
    """
    global cannedFishConf
    fishCanConf = cannedFishConf.get("welfareCan", {})
    return fishCanConf


def getCanProp():
    """
    获取鱼罐厂制作罐头需要消耗的道具配置
    """
    global cannedFishConf
    canPropConf = cannedFishConf.get("canProp", [])
    return canPropConf


def loadCreditStoreConf():
    """
    加载积分商城配置
    """
    global creditStoreConf
    creditStoreConf = rocopy(getGameConf("creditStore"))


def getCreditStoreConf(key_=None):
    """
    获取积分商城配置
    """
    global creditStoreConf
    if key_ is None:
        return creditStoreConf
    return rwcopy(creditStoreConf.get(str(key_)))


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


def getMiniGameLevelIds(level):
    """
    获取小游戏等级配置（美人鱼的馈赠，宝箱）
    """
    global miniGameLevelMap
    return miniGameLevelMap.get(level, [])


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


def loadTimePointMatchSkillConf():
    """回馈赛的随机固定技能配置"""
    global timePointMatchSkillConf
    timePointMatchSkillConf = rocopy(getGameConf("timePointMatchSkill_m"))


def getTimePointMatchSkillConf():
    """获取回馈赛的随机固定技能配置"""
    global timePointMatchSkillConf
    return timePointMatchSkillConf


def loadTideTask():
    """加载鱼潮任务"""
    global tideTaskConf
    tideTaskConfTmp = getGameConf("tideTask")
    tideTaskConf = {}
    for key, value in tideTaskConfTmp.iteritems():
        fishPool = value["fishPool"]
        group = value["group"]
        if fishPool not in tideTaskConf:
            tideTaskConf[fishPool] = {}
            tideTaskConf[fishPool][group] = value
        else:
            if group not in tideTaskConf[fishPool]:
                tideTaskConf[fishPool][group] = value
    tideTaskConf = rocopy(tideTaskConf)


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
    loadProbabilityConf_m()
    loadDynamicOddsConf()                   # 加载动态概率配置
    loadLotteryPoolConf()
    loadRingLotteryPoolConf()
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
    loadSuperbossExchangeConf()
    loadSuperbossMinigameConf()
    loadSuperbossCommonConf()
    loadCollectItemConf()
    loadPoseidonConf()
    loadBigPrizeConf()
    loadCompActConf()
    loadNewbie7DaysGfitConf()
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
    loadTimePointMatchSkillConf()
    loadTerrorFishConf()
    loadTerrorFishConf_m()
    loadAutofillFishConf_m()
    loadTideTask()


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
        getConfigPath("probability_m"): loadProbabilityConf_m,
        getConfigPath("dynamicOdds"): loadDynamicOddsConf,  # 加载动态概率配置
        getConfigPath("lotteryPool"): loadLotteryPoolConf,
        getConfigPath("ringLotteryPool"): loadRingLotteryPoolConf,
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
        getConfigPath("superbossExchange"): loadSuperbossExchangeConf,
        getConfigPath("superbossMinigame"): loadSuperbossMinigameConf(),
        getConfigPath("superbossCommon"): loadSuperbossCommonConf(),
        getConfigPath("collectItem"): loadCollectItemConf,
        getConfigPath("poseidon"): loadPoseidonConf,
        getConfigPath("bigPrize"): loadBigPrizeConf,
        getConfigPath("competition"): loadCompActConf,
        getConfigPath("newbie7DaysGift"): loadNewbie7DaysGfitConf,      # 加载默认商店配置
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
        getConfigPath("timePointMatchSkill_m"): loadTimePointMatchSkillConf,
        getConfigPath("terrorFish"): loadTerrorFishConf,
        getConfigPath("terrorFish_m"): loadTerrorFishConf_m,
        getConfigPath("autofillFish_m"): loadAutofillFishConf_m,
        getConfigPath("tideTask"): loadTideTask,
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
    from newfish.entity.lotterypool import grand_prize_pool
    grand_prize_pool.reloadConfig(event)


def checkActivityItemConf():
    """
    检查活动关联道具的有效期是否正确
    """
    _activityItemConf = {}
    for acId, acConf in getActivityConfig().iteritems():
        if isinstance(acConf.get("extends"), dict) and isinstance(acConf["extends"].get("checkKindIds"), list):
            for kindId in acConf["extends"]["checkKindIds"]:
                _activityItem = {}
                _activityItem["acId"] = acId
                _activityItem["expires"] = acConf.get("effectiveTime", {}).get("end")
                _activityItemConf[kindId] = _activityItem
    # config37配置
    conf = hallconf.getItemConf()
    itemKindConfList = conf.get("items", [])
    checkItemHasExpired(itemKindConfList, _activityItemConf, "config37")
    # config5配置
    from tuyoo5.core import tyconfig
    conf = tyconfig.getGameData("game5:9998:itemnew:sc")
    itemKindConfList = conf.get("items", [])
    checkItemHasExpired(itemKindConfList, _activityItemConf, "config5")


def checkItemHasExpired(itemKindConfList, activityItemConf, tag):
    """
    检查道具是否过期并发出预警
    """
    from newfish.entity import util
    for _, itemKindConf in enumerate(itemKindConfList):
        if itemKindConf.get("expires") and itemKindConf["kindId"] in activityItemConf:
            _activityItem = activityItemConf[itemKindConf["kindId"]]
            itemExpires = util.getTimestampFromStr(itemKindConf["expires"])
            activityExpires = util.getTimestampFromStr(_activityItem["expires"])
            if itemExpires < activityExpires:
                ftlog.error("%s item expired config error" % tag,
                            _activityItem["acId"], _activityItem["expires"],
                            itemKindConf["kindId"], itemKindConf["expires"])


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