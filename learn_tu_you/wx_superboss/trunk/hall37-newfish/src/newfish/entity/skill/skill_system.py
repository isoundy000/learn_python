#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import json
from copy import deepcopy
from collections import OrderedDict

import freetime.util.log as ftlog
import poker.util.timestamp as pktimestamp
from poker.util import strutil
from poker.entity.dao import daobase, gamedata
from hall.entity import hallitem, datachangenotify
from newfish.entity import config, module_tip, util, mail_system
from newfish.entity.config import FISH_GAMEID, PEARL_KINDID, CHIP_KINDID
from newfish.entity.redis_keys import UserData, GameData


# 5101: [0, 0, 0, 0, 0]
# skillMode 0:经典 1:千炮
DEFAULT_VALUE = [0, 0, 0, 0, 0]
MAX_STAR_LEVEL = 5          # 最大技能星级
MAX_ORIGINAL_LEVEL = 25     # 最大技能等级
MAX_INSTALL_NUM = 3         # 最大装备数（经典）
MAX_INSTALL_NUM_M = 2       # 最大装备数（千炮）
INDEX_STAR_LEVEL = 0        # 第0位:技能星级
INDEX_ORIGINAL_LEVEL = 1    # 第1位:技能原始等级
INDEX_CURRENT_LEVEL = 2     # 第2位:技能当前等级
INDEX_STATE = 3             # 第3位:技能状态&顺序（经典）
INDEX_STATE_M = 4           # 第4位:技能状态&顺序（千炮）
AUXILIARY_SKILL_NUM = 2     # 辅助技能个数


def initSkill(userId):
    """
    初始化技能数据
    """
    for skillId in config.getAllSkillId():
        updateSkill(userId, skillId)


def updateSkill(userId, skillId):
    """
    更新新增技能数据  如果 key 不存在，一个新哈希表被创建并执行 HSETNX 命令。
    """
    assert str(skillId) in config.getAllSkillId()
    daobase.executeUserCmd(userId, "HSETNX", _getUserSkillKey(userId), str(skillId), json.dumps(DEFAULT_VALUE))


def setSkill(userId, skillId, skillInfo):
    """
    存储单个技能数据
    """
    assert str(skillId) in config.getAllSkillId()
    assert isinstance(skillInfo, list) and len(skillInfo) == len(DEFAULT_VALUE)
    daobase.executeUserCmd(userId, "HSET", _getUserSkillKey(userId), str(skillId), json.dumps(skillInfo))


def getSkill(userId, skillId):
    """
    获得单个技能数据
    """
    value = daobase.executeUserCmd(userId, "HGET", _getUserSkillKey(userId), str(skillId))
    if value:
        return strutil.loads(value, False, True)    # 字符串不转assci、忽略异常
    return deepcopy(DEFAULT_VALUE)


def _getAllSkills(userId):
    """
    获得所有技能数据
    """
    assert isinstance(userId, int) and userId > 0
    value = daobase.executeUserCmd(userId, "HGETALL", _getUserSkillKey(userId))     # skill:44:10007  [1, 2, 3, 4, 5, 6]
    if value:
        skillIds = value[0::2]      # fileds [1, 3, 5]
        infos = [strutil.loads(info, False, True) for info in value[1::2] if info]  # [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        skillDict = dict(zip(skillIds, infos))
        allSkillIdsConf = config.getAllSkillId()        # 获取配置中所有技能ID
        popSkillIds = [skillId for skillId in skillIds if str(skillId) not in allSkillIdsConf]
        for _skillId in popSkillIds:
            del skillDict[_skillId]                     # 删掉存档中与配置中不存在的skillId
        return skillDict
    return {}


def getInstalledSkill(userId, skillMode):
    """
    获得已装备技能数据 玩家userId skillMode 0经典 1千炮
    """
    skills = {}
    allSkills = _getAllSkills(userId)
    if allSkills:
        for skillId, info in allSkills.iteritems():
            if config.getSkillStarConf(skillId, info[INDEX_STAR_LEVEL], skillMode):
                state = info[INDEX_STATE] if skillMode == config.CLASSIC_MODE else info[INDEX_STATE_M]
                if state:
                    skills[int(skillId)] = [info[INDEX_STAR_LEVEL], info[INDEX_CURRENT_LEVEL]]
    return skills


def getAuxiliarySkill(userId):
    """
    获得辅助技能数据
    """
    skills = {}
    allSkills = _getAllSkills(userId)
    if allSkills:
        for skillId, info in allSkills.iteritems():
            # 魔术炮，极冻炮
            if int(skillId) in [5102, 5104] \
                and 0 < info[INDEX_STAR_LEVEL] <= MAX_STAR_LEVEL \
                and 0 < info[INDEX_ORIGINAL_LEVEL] <= MAX_ORIGINAL_LEVEL:
                skills[int(skillId)] = [info[INDEX_STAR_LEVEL], info[INDEX_CURRENT_LEVEL]]
    return skills


def _getUserSkillKey(userId):
    """
    技能数据存取key
    """
    return UserData.skill % (FISH_GAMEID, userId)


def getSkillList(userId, skillMode=0):
    """
    获取技能信息列表
    """
    skills = []
    allSkills = _getAllSkills(userId)
    if allSkills:
        for skillId, info in allSkills.iteritems():
            if config.getSkillStarConf(skillId, info[INDEX_STAR_LEVEL], skillMode):
                skill = dict()
                skill["skillId"] = int(skillId)
                skill["starLevel"] = info[INDEX_STAR_LEVEL]
                skill["originalLevel"] = info[INDEX_ORIGINAL_LEVEL]
                skill["currentLevel"] = info[INDEX_CURRENT_LEVEL]
                skill["state"] = info[INDEX_STATE] if skillMode == config.CLASSIC_MODE else info[INDEX_STATE_M]
                skills.append(skill)
    return skills


def upgradeSkill(userId, skillId, actionType):
    """
    技能升级0、升星1  渔场内、渔场外
    """
    code, skill = checkSkillStatus(userId, skillId)
    if code != 0:
        return code, 0, 0, 0, 0
    previousLevel = skill[INDEX_ORIGINAL_LEVEL]         # 之前的等级

    if actionType == 0:                                 # 升级
        if skill[INDEX_ORIGINAL_LEVEL] >= MAX_ORIGINAL_LEVEL:
            return 6, 0, 0, 0, 0
        skillGradeConf = config.getSkillGradeCommonConf(skillId, skill[INDEX_ORIGINAL_LEVEL] + 1)
        isOK = consumeUpgradeSkillItem(userId, skillGradeConf["consume"], skillId, skill[INDEX_ORIGINAL_LEVEL] + 1)
        if isOK:
            skill[INDEX_ORIGINAL_LEVEL] += 1
            skill[INDEX_CURRENT_LEVEL] = skill[INDEX_ORIGINAL_LEVEL]
            setSkill(userId, skillId, skill)
        else:
            return 4, skill[INDEX_STAR_LEVEL], skill[INDEX_ORIGINAL_LEVEL], skill[INDEX_CURRENT_LEVEL], previousLevel
    else:                                               # 升星
        if skill[INDEX_STAR_LEVEL] >= MAX_STAR_LEVEL:
            return 6, 0, 0, 0, 0
        skillStarConf = config.getSkillStarCommonConf(skillId, skill[INDEX_STAR_LEVEL] + 1)
        isOK = consumeUpgradeSkillItem(userId, skillStarConf["consume"], skillId, skill[INDEX_STAR_LEVEL] + 1)
        if isOK:
            skill[INDEX_STAR_LEVEL] += 1
            setSkill(userId, skillId, skill)
        else:
            return 4, skill[INDEX_STAR_LEVEL], skill[INDEX_ORIGINAL_LEVEL], skill[INDEX_CURRENT_LEVEL], previousLevel

    upgradedSkill = getSkill(userId, skillId)
    if not upgradedSkill:
        ftlog.error("upgradeSkill-> getSkill error", userId, skillId)
        return 5, skill[INDEX_STAR_LEVEL], skill[INDEX_ORIGINAL_LEVEL], skill[INDEX_CURRENT_LEVEL], previousLevel
    datachangenotify.sendDataChangeNotify(FISH_GAMEID, userId, "item")
    from newfish.game import TGFish
    from newfish.entity.event import SkillItemCountChangeEvent
    event = SkillItemCountChangeEvent(userId, FISH_GAMEID)
    TGFish.getEventBus().publishEvent(event)
    # 技能升级事件
    from newfish.game import TGFish
    from newfish.entity.event import SkillLevelUpEvent
    event = SkillLevelUpEvent(userId, FISH_GAMEID, getSkillList(userId), actionType)
    TGFish.getEventBus().publishEvent(event)
    return 0, upgradedSkill[INDEX_STAR_LEVEL], upgradedSkill[INDEX_ORIGINAL_LEVEL], upgradedSkill[INDEX_CURRENT_LEVEL], previousLevel


def upgradeMaxSkill(userId, expendItemId, clientId):
    """
    技能升级满级 使用game_handler的使用道具
    """
    if config.getItemConf(clientId, expendItemId).get("up_skill", 0) == 0:
        return 7, 0, 0, 0, 0
    actions = config.getItemConf(clientId, expendItemId).get("actions", 0)
    skillId = 0
    for it in actions:
        if it["action"] == "up_skill":
            skillId = int(it["params"][0]["skillId"])
            break




def installSkill(userId, skillId, skillMode, install):
    """
    技能装备、卸下 skillMode 0经典 1千炮
    """
    code, skill = checkSkillStatus(userId, skillId)
    if code != 0:
        return code
    allSkills = _getAllSkills(userId)
    if install:     # 装备
        installNum = 0
        maxInstallNum = MAX_INSTALL_NUM if skillMode == config.CLASSIC_MODE else MAX_INSTALL_NUM_M
        for _, info in allSkills.iteritems():
            if config.getSkillStarConf(skillId, info[INDEX_STAR_LEVEL], skillMode):
                state = info[INDEX_STATE] if skillMode == config.CLASSIC_MODE else info[INDEX_STATE_M]
                if state:
                    installNum += 1
                if state == install:
                    ftlog.error("installSkill->, has been installed", userId, skillId, skillMode, install)
                    return 4
        if installNum >= maxInstallNum:
            ftlog.error("installSkill->, attain max install num", userId, skillId, skillMode, install)
            return 4
    if skillMode == config.CLASSIC_MODE:
        skill[INDEX_STATE] = install
    else:
        skill[INDEX_STATE_M] = install
    setSkill(userId, skillId, skill)                        # 装备穿上、卸下
    installedSkill = getSkill(userId, skillId)
    state = installedSkill[INDEX_STATE] if skillMode == config.CLASSIC_MODE else installedSkill[INDEX_STATE_M]
    if state != install:
        ftlog.error("installSkill-> installSkill fail", userId, skillId, skillMode, install)
        return 5
    return 0


def replaceSkill(userId, skillMode, installSkillId, uninstallSkillId):
    """
    技能替换
    """
    uninstallSkill = getSkill(userId, uninstallSkillId)
    state = uninstallSkill[INDEX_STATE] if skillMode == config.CLASSIC_MODE else uninstallSkill[INDEX_STATE_M]
    if state:
        installSkill(userId, uninstallSkillId, skillMode, 0)            # 卸下
        return installSkill(userId, installSkillId, skillMode, state)   # 穿上
    return 0


def checkSkillStatus(userId, skillId):
    """
    检查技能状态
    """
    skill = None
    if str(skillId) not in config.getAllSkillId():
        ftlog.error("checkSkillStatus-> not skillId", userId, skillId)
        return 1, skill
    skill = getSkill(userId, skillId)       # 获取技能信息
    if not skill:
        setSkill(userId, skillId, deepcopy(DEFAULT_VALUE))                  # 存储单个技能数据
        ftlog.error("checkSkillStatus-> not skillInfo", userId, skillId)
        return 2, skill
    if skill[INDEX_STAR_LEVEL] <= 0 or \
        skill[INDEX_STAR_LEVEL] > MAX_STAR_LEVEL or \
        skill[INDEX_ORIGINAL_LEVEL] <= 0 or \
        skill[INDEX_ORIGINAL_LEVEL] > MAX_ORIGINAL_LEVEL:
        ftlog.debug("checkSkillStatus-> skillLevel error", userId, skillId)
        return 3, skill
    return 0, skill


def checkSkillUpgrade(event):
    """
    检查技能能否升级升星
    """
    userId = event.userId
    upskills = []
    for skillId in config.getAllSkillId():
        skillId = int(skillId)
        code, skill = checkSkillStatus(userId, skillId)
        if code != 0:
            continue
        if skill[INDEX_ORIGINAL_LEVEL] < MAX_ORIGINAL_LEVEL:
            skillGradeConf = config.getSkillGradeCommonConf(skillId, skill[INDEX_ORIGINAL_LEVEL] + 1)
            if checkUpgradeSkillItemCount(userId, skillGradeConf["consume"]):
                upskills.append(skillId)
        if skill[INDEX_STAR_LEVEL] < MAX_STAR_LEVEL:
            skillStarConf = config.getSkillStarCommonConf(skillId, skill[INDEX_STAR_LEVEL] + 1)
            if checkUpgradeSkillItemCount(userId, skillStarConf["consume"]):
                upskills.append(skillId)
    module_tip.resetModuleTip(userId, "upskill")
    if upskills:
        module_tip.addModuleTipEvent(userId, "upskill", upskills)
    else:
        module_tip.resetModuleTipEvent(userId, "upskill")


def skillCompensate(userId, skillId):
    """
    技能补偿
    """
    pass
    # skillCompenData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.skillCompensate, [])
    # if skillId in skillCompenData:
    #     return
    # skill = getSkill(userId, skillId)
    # if skill:
    #     lang = util.getLanguage(userId)
    #     skillLevel = skill[INDEX_ORIGINAL_LEVEL]
    #     skillStar = skill[INDEX_STAR_LEVEL]
    #
    #     from hall.entity import hallitem
    #     userBag = hallitem.itemSystem.loadUserAssets(userId).getUserBag()
    #     starCardItemId = config.getSkillCompenConf("starItemId")
    #     starCardItemKind = hallitem.itemSystem.findItemKind(starCardItemId)
    #     starCardCount = userBag.calcTotalUnitsCount(starCardItemKind)
    #
    #     gradeCardItemId = config.getSkillCompenConf("gradeItemId")
    #     gradeCardItemKind = hallitem.itemSystem.findItemKind(gradeCardItemId)
    #     gradeCardCount = userBag.calcTotalUnitsCount(gradeCardItemKind)
    #
    #     skillLevCompCount = config.getSkillCompenConf("skillLevComp").get(str(skillLevel), 0)
    #     starLevCompCount = config.getSkillCompenConf("starLevComp").get(str(skillStar), 0)
    #     totalCount = (gradeCardCount + skillLevCompCount) * 2000 + (starCardCount + starLevCompCount) * 600
    #     if totalCount:
    #         rewards = [{"name": 101, "count": totalCount}]
    #         skillCompenData.append(skillId)
    #         skillName = config.getMultiLangTextConf("ID_SKILL_NAME:%d" % int(skillId), lang=lang)
    #         message = config.getMultiLangTextConf(config.getSkillCompenConf("compenMail"), lang=lang).format(skillName,
    #                                                                                                        skillName)
    #         gamedata.setGameAttr(userId, FISH_GAMEID, GameData.skillCompensate, json.dumps(skillCompenData))
    #         mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemReward, rewards, message=message,
    #                                    title=config.getMultiLangTextConf("ID_MAIL_TITLE_SYSTEM_COMPENSATE", lang=lang))


def convertOverflowCardToCoin(userId, skills=None):
    """
    溢出技能卡转换为金币
    """
    pass
    # totalConvertCoin = 0
    # skills = skills or getSkillList(userId)
    # for skillInfo in skills:
    #     skillId = skillInfo["skillId"]
    #     skillLevel = skillInfo["originalLevel"]
    #     starLevel = skillInfo["starLevel"]
    #     if skillLevel >= MAX_ORIGINAL_LEVEL:
    #         # 技能卡转换
    #         skillGradeConf = config.getSkillGradeConf(skillId, skillLevel)
    #         # 满级所需技能卡数量
    #         totalCostCard = config.getSkillGradeConf(skillId, MAX_ORIGINAL_LEVEL).get("totalCard", 0)
    #         # 已消耗技能卡数量
    #         costCard = skillGradeConf.get("totalCard", 0)
    #         # 升至满级所需技能卡数量
    #         needCard = totalCostCard - costCard
    #         kindId = skillGradeConf.get("itemId", 0)
    #         surplusCount = util.balanceItem(userId, kindId)
    #         overflowCount = surplusCount - needCard
    #         if overflowCount > 0:
    #             chestDropConf = config.getChestDropConf()
    #             convertCoin = chestDropConf[str(kindId)]["convertCoin"] * overflowCount
    #             util.consumeItem(userId, kindId, overflowCount, "SALE_ITEM", convertCoin)
    #             totalConvertCoin += convertCoin
    #     if starLevel >= MAX_STAR_LEVEL:
    #         # 升星卡转换
    #         skillStarConf = config.getSkillStarConf(skillId, starLevel)
    #         # 满星所需升星卡数量
    #         totalCostCard = config.getSkillStarConf(skillId, MAX_STAR_LEVEL).get("totalCard", 0)
    #         # 已消耗升星卡数量
    #         costCard = skillStarConf.get("totalCard", 0)
    #         # 升至满星所需升星卡数量
    #         needCard = totalCostCard - costCard
    #         kindId = skillStarConf.get("itemId", 0)
    #         surplusCount = util.balanceItem(userId, kindId)
    #         overflowCount = surplusCount - needCard
    #         if overflowCount > 0:
    #             chestDropConf = config.getChestDropConf()
    #             convertCoin = chestDropConf[str(kindId)]["convertCoin"] * overflowCount
    #             util.consumeItem(userId, kindId, overflowCount, "SALE_ITEM", convertCoin)
    #             totalConvertCoin += convertCoin
    # if totalConvertCoin > 0:
    #     lang = util.getLanguage(userId)
    #     rewards = [{"name": CHIP_KINDID, "count": totalConvertCoin}]
    #     message = config.getMultiLangTextConf("ID_SKILL_CARD_CONVERT_TO_COIN", lang=lang)
    #     mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemCompensate, rewards, message)


def doSkillCompensate(userId):
    """
    卸载技能，取消要卸载技能的小红点，并补偿金币
    """
    allSkillIds = config.getAllSkillId()
    installSkillIds = getInstalledSkill(userId, 1).keys()       # 1千炮
    moduleTipSkillIds = module_tip.getTipValue(userId, module_tip.findModuleTip("upskill"))
    if installSkillIds:     # 卸载已经装备且要下线的技能
        for _skillId in installSkillIds:
            if str(_skillId) not in allSkillIds:                # 配置表的技能
                code = installSkill(userId, _skillId, 1, 0)     # 技能装备、卸下  1千炮模式 0卸下
                if code != 0:
                    ftlog.error("compensateSkill---> unstallSkill fail", userId, _skillId, code)
    compenSkillIds = config.getSkillCompenConf("skillList")
    if compenSkillIds: # 补偿要下线的技能，并去掉该技能的小红点
        for skillId in compenSkillIds:
            skillCompensate(userId, skillId)
            if skillId in moduleTipSkillIds:
                module_tip.cancelModuleTipEvent(userId, "upskill", skillId)


def compatibleSkillData(userId):
    """
    旧技能数据兼容
    """
    allSkills = _getAllSkills(userId)
    order = 0
    for skillId, info in allSkills.iteritems():
        if len(info) < len(DEFAULT_VALUE):
            if info[INDEX_STATE] == 1:              # 技能状态&顺序
                order += 1
                info[INDEX_STATE] = order
            info.append(0)
            setSkill(userId, skillId, info)


def checkUpgradeSkillItemCount(userId, items):
    """
    检查升级/升星所需道具是否足够
    """
    isOK = True
    for item in items:
        kindId = item["name"]
        needCount = item["count"]
        userAssets = hallitem.itemSystem.loadUserAssets(userId)     # 加载用户资产
        surplusCount = userAssets.balance(FISH_GAMEID, util.getAssetKindId(kindId), 
                                          pktimestamp.getCurrentTimestamp())        # 查询用户item:14119
        if surplusCount < needCount:
            isOK = FISH_GAMEID
            break
    return isOK


def consumeUpgradeSkillItem(userId, items, intEventParam=0, param01=0, param02=0):
    """
    消耗升级/升星所需道具
    """
    if checkUpgradeSkillItemCount(userId, items):
        ret = util.consumeItems(userId, items, "BI_NFISH_SKILL_UPGRADE", intEventParam, param01, param02)
        if len(ret) == len(items):
            return True
    return False


def _triggerUserLoginEvent(event):
    """
    用户登录事件
    """
    userId = event.userId
    initSkill(userId)                       # 初始化技能
    compatibleSkillData(userId)             # 旧技能数据兼容
    convertOverflowCardToCoin(event.userId)
    doSkillCompensate(userId)


_inited = False


def initialize():
    """技能系统初始化"""
    ftlog.info("newfish skill_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import EventUserLogin          # 用户登录事件
        from newfish.game import TGFish
        from newfish.entity.event import SkillItemCountChangeEvent      # 技能升级升星相关物品数量变化事件
        TGFish.getEventBus().subscribe(SkillItemCountChangeEvent, checkSkillUpgrade)
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
    ftlog.info("newfish skill_system initialize end")