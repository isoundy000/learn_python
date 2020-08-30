#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
千炮玩法的配置
执行该脚本，将会生成newfish_multiple.xlsm对应的json配置文件
'''
__author__ = 'ghou'

import traceback
import time
from openpyxl import load_workbook
import os, sys, json, copy
import collections
import re
import csv
from multiprocessing import Queue, Process, cpu_count, freeze_support

ServerPath = ""
ClientIdMap = None


def superboss_exchange_config():
    """
    超级boss兑换配置
    """
    print "superboss_exchange_config, start"
    outPath = getOutPath("superBossExchange")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("SuperBossExchange")
    config = collections.OrderedDict()
    config["info"] = collections.OrderedDict()
    config["exchange"] = collections.OrderedDict()
    startRowNum = 4
    h = 0
    costCntRow = 8
    gainCntRow = 14
    for row in ws.rows:
        h = h + 1
        if h < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0]:
            one = collections.OrderedDict()
            key = "%s_%d" % (str(cols[0]), int(cols[1]))
            config["info"][key] = one
            one["mode"] = int(cols[1])
            one["currencyList"] = json.loads(cols[2])

        if cols[4]:
            key = "%s_%d" % (str(cols[4]), int(cols[5]))
            config["exchange"].setdefault(key, {})
            one = collections.OrderedDict()
            # config["exchange"][key].setdefault("items", [])
            config["exchange"][key].setdefault("exchangeItems", [])
            config["exchange"][key]["exchangeItems"].append(one)
            one["mode"] = int(cols[5])
            one["idx"] = int(cols[6])
            one["exchangeTimes"] = int(cols[7])                 # 兑换次数
            one["costItems"] = []                               # 消耗物品
            cnt = int(cols[costCntRow])                         # 消耗类型数量
            for i in range(cnt):
                one["costItems"].append(json.loads(cols[costCntRow + 1 + i]))
            one["gainItems"] = []                               # 获得物品
            cnt = int(cols[gainCntRow])                         # 获得次数
            for i in range(cnt):
                one["gainItems"].append(json.loads(cols[gainCntRow + 1 + i]))

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "superboss_exchange_config, end"


def superboss_minigame_config():
    """
    超级boss宝箱配置
    """
    print "superboss_minigame_config, start"
    outPath = getOutPath("superBossMinigame")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("SuperBossMinigame")
    config = collections.OrderedDict()
    config["info"] = collections.OrderedDict()
    config["game"] = collections.OrderedDict()
    startRowNum = 4
    h = 0
    for row in ws.rows:
        h = h + 1
        if h < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0]:
            one = collections.OrderedDict()
            key = "%s_%d" % (str(cols[0]), int(cols[1]))
            config["info"][key] = one
            one["mode"] = int(cols[1])
            one["maxTimes"] = json.loads(cols[2])
            one["currencyList"] = json.loads(cols[3])
        if cols[5]:
            key = "%s_%d" % (str(cols[5]), int(cols[6]))
            config["game"].setdefault(key, [])
            config["game"][key].append({
                "costs": json.loads(cols[9]),
                "rewards": json.loads(cols[10]),
                "des": str(cols[8]) if cols[8] else "",
                "mode": int(cols[6]),
                "level": int(cols[7])
            })

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "superboss_minigame_config, end"


def superboss_common_config():
    """
    超级boss通用配置
    """
    print "superboss_common_config, start"
    outPath = getOutPath("superBossCommon")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("SuperBossCommon")
    config = collections.OrderedDict()
    startRowNum = 4
    h = 0
    for row in ws.rows:
        h = h + 1
        if h < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0]:                                 # 房间ID
            one = collections.OrderedDict()
            key = "%s_%d" % (str(cols[0]), int(cols[1]))
            config[key] = one
            one["tabs"] = json.loads(cols[2])		# 房间的游戏玩法
            one["poolPct"] = float(cols[3])			# 奖池占房间奖池比例
            one["nextDayPoolPct"] = float(cols[4])	# 第二天奖池占房间奖池比例
            one["mgType"] = str(cols[5])			# 类型
            one["rule"] = json.loads(cols[6])		# 规则

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "superboss_common_config, end"


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def fish_config():
    """
    千炮玩法渔场的鱼
    :return:
    """
    print "fish_config, start"
    outPath = getOutPath("fish_m")
    ws = getWorkBook().get_sheet_by_name("Fish")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    reload(sys)
    sys.setdefaultencoding("utf8")
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[3]:
            continue
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("fishId %d repeat" % int(cols[0]))
        config[str(cols[3])] = one
        one["fishType"] = int(cols[3])
        one["name"] = unicode(cols[1])
        one["type"] = int(cols[4])
        if is_number(cols[5]):
            one["itemId"] = int(cols[5])
        else:
            one["itemId"] = json.loads(cols[5])
        one["score"] = int(cols[6])
        one["probb1"] = float("%.1f" % cols[7])
        one["probb2"] = float("%.1f" % cols[8])
        one["HP"] = int(cols[9])
        one["value"] = int(cols[10])
        if cols[12]:
            one["weaponId"] = int(cols[12])
        one["prizeWheelValue"] = float(cols[13])
        one["triggerRate"] = int(cols[14])
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "fish_config, end"


def match_fish_config():
    """
    比赛鱼的配置
    :return:
    """
    print "match_fish_config, start"
    outPath = getOutPath("matchFish")
    ws = getWorkBook().get_sheet_by_name("MatchFish")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    reload(sys)
    sys.setdefaultencoding("utf8")
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[2]:
            continue
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("fishId %d repeat" % int(cols[0]))
        config[str(cols[2])] = one
        one["name"] = unicode(cols[1])
        one["type"] = int(cols[3])
        if is_number(cols[4]):
            one["itemId"] = int(cols[4])
        else:
            one["itemId"] = json.loads(cols[4])
        one["score"] = int(cols[5])
        one["probb1"] = float("%.1f" % cols[6])
        one["probb2"] = float("%.1f" % cols[7])
        one["HP"] = int(cols[8])
        one["multiple"] = int(cols[9])
        fishPool = cols[10]                     # 加倍鱼出现渔场
        if isinstance(fishPool, unicode):
            fishPool = fishPool.split("|")
            fishPool = [int(x) for x in fishPool]
        else:
            fishPool = []
        one["fishPool"] = fishPool
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "match_fish_config, end"


def skill_grade_config():
    """
    技能等级配置
    """
    outPath = getOutPath("skillGrade_m")
    ws = getWorkBook().get_sheet_by_name("SkillGrade")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    skillId = collections.OrderedDict()
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue
        if row[1].value not in config.keys():       # 第一列的值 5101
            skillId = collections.OrderedDict()
            config[row[1].value] = skillId
        one = collections.OrderedDict()
        skillId[str(row[2].value)] = one            # {等级1: {}}
        for cell in row:
            cols.append(cell.value)
        if not cols[2]:
            continue
        one["cost"] = int(cols[3])                  # 消耗子弹
        one["power"] = int(cols[4])                 # 单发威力
        one["HP"] = int(cols[5])                    # HP
        one["impale"] = int(cols[6])                # 贯穿力
        one["clip"] = int(cols[7])                  # 技能子弹数
        one["interval"] = float(cols[8])            # 每发间隔时间
        one["duration"] = float(cols[9])            # 效果时间
        one["coolDown"] = int(cols[10])             # 冷却时间
        one["weaponId"] = int(cols[11])             # 对应武器
        one["double"] = json.loads(str(cols[12]))   # 双倍皮肤炮ID
        one["isReturn"] = int(cols[13])             # 打空是否返还子弹
    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def skill_star_config():
    """
    技能星级config
    """
    outPath = getOutPath("skillStar_m")
    ws = getWorkBook().get_sheet_by_name("SkillStar")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    skillId = collections.OrderedDict()
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue
        if row[1].value not in config.keys():
            skillId = collections.OrderedDict()
            config[row[1].value] = skillId
        one = collections.OrderedDict()
        skillId[str(row[2].value)] = one
        for cell in row:
            cols.append(cell.value)
        if not cols[2]:
            continue
        abilities = []
        one["abilities"] = abilities
        for x in xrange(3, len(cols), 3):
            if not cols[x]:
                break
            ability = collections.OrderedDict()
            ability["ability"] = int(cols[x])           # 提升能力类型
            ability["valueType"] = int(cols[x + 1])     # 数值类型
            ability["value"] = int(cols[x + 2])         # 数值
            abilities.append(ability)
    result = json.dumps(config, indent=4)               # {'5101': {2: {'abilities': [{'ability': 25, 'valueType': 1, 'value': 30}]}}}
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def gunLevel():
    """火炮等级配置"""
    outPath = getOutPath("gunLevel_m")
    ws = getWorkBook().get_sheet_by_name("GunLevel")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if cols[0] != 0 and not cols[0]:
            continue
        one = collections.OrderedDict()
        config[str(cols[0])] = one
        one["gunLevel"] = int(cols[0])
        upgradeItems = collections.OrderedDict()
        if int(cols[1]):
            upgradeItems[cols[1]] = int(cols[2])
        for x in range(3, 6, 2):
            if int(cols[x]):
                upgradeItems[cols[x]] = cols[x + 1]
        if upgradeItems:
            one["upgradeItems"] = upgradeItems
        _tmpIdx = 7
        one["successRate"] = int(cols[_tmpIdx])
        if int(cols[_tmpIdx]) < 10000:
            protectItems = collections.OrderedDict()
            one["protectItems"] = protectItems
            protectItems[cols[_tmpIdx + 1]] = int(cols[_tmpIdx + 2])
        returnItems = []
        probb = 0
        for x in range(_tmpIdx + 3, _tmpIdx + 12, 3):
            if int(cols[x]):
                item = collections.OrderedDict()
                item["kindId"] = cols[x]
                item["count"] = cols[x + 1]
                item["probb"] = [probb + 1, probb + cols[x + 2]]
                returnItems.append(item)
                probb += cols[x + 2]
        if returnItems:
            one["returnItems"] = returnItems
        if cols[_tmpIdx + 12]:
            one["interval"] = float(cols[_tmpIdx + 12])
        if cols[_tmpIdx + 13] is not None:
            one["levelAddition"] = float(cols[_tmpIdx + 13])
        one["levelValue"] = int(cols[_tmpIdx + 14])
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def gunskin_config(clientId=0):
    """
    火炮和皮肤信息
    """
    print "gunskin_config, start"
    sn = "Gun" if clientId == 0 else "Gun" + "_" + str(clientId)
    sn2 = "GunSkin" if clientId == 0 else "GunSkin" + "_" + str(clientId)
    fn = "0.json" if clientId == 0 else str(clientId) + ".json"
    outPath = getOutPath("gun_m", fn)
    ws = getWorkBook().get_sheet_by_name(sn)
    wsSkin = getWorkBook().get_sheet_by_name(sn2)
    startRowNum = 4
    i = 0
    config = collections.OrderedDict()
    gunIds = []
    config["gunIds"] = gunIds
    config["gun"] = collections.OrderedDict()
    config["skin"] = collections.OrderedDict()
    gunConf = collections.OrderedDict()
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        if not cols[2]:
            continue
        if row[1].value not in config["gun"].keys():
            gunConf = collections.OrderedDict()
            config["gun"][row[1].value] = gunConf
        one = collections.OrderedDict()
        gunConf[str(row[2].value)] = one
        if int(cols[1]) not in gunIds:
            gunIds.append(int(cols[1]))
        one["gunId"] = int(cols[1])
        one["gunLevel"] = int(cols[2])
        one["name"] = cols[0]
        one["multiple"] = int(cols[3])          # 消耗&奖励倍率
        one["unlockType"] = int(cols[4])        # 解锁条件
        one["unlockValue"] = int(cols[5])
        one["equipType"] = int(cols[6])         # 装备条件
        one["equipValue"] = int(cols[7])
        one["exp"] = int(cols[8])               # 所需经验
        one["totalExp"] = int(cols[9])          # 累计经验
        one["effectAddition"] = float(cols[10]) # 熟练效果加成
        one["effectType"] = int(cols[11])       # 效果类型
        one["effectProbb"] = int(cols[12])      # 触发概率
        one["unlockDesc"] = unicode(cols[13] or "")
        one["equipDesc"] = unicode(cols[14] or "")
        one["unitPrice"] = int(cols[15])
        one["skins"] = json.loads(str(cols[16]))
        one["fire_count"] = int(cols[17])
        one["power_rate"] = int(cols[18])
        one["duration"] = int(cols[19])
        one["percent"] = int(cols[20])
        aloofOdds = []
        one["aloofOdds"] = aloofOdds
        for m in range(21, len(cols), 2):
            if cols[m] is None:
                break
            oddsMap = {}
            oddsMap["odds"] = cols[m]
            oddsMap["probb"] = cols[m + 1]
            aloofOdds.append(oddsMap)

    i = 0
    for row in wsSkin.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue
        one = collections.OrderedDict()
        for cell in row:
            cols.append(cell.value)
        config["skin"][cols[0]] = one   # 皮肤
        one["skinId"] = cols[0]         # 皮肤ID
        one["gunId"] = cols[1]          # 炮ID
        one["kindId"] = cols[2]
        one["consumeCount"] = cols[3]

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "gunskin_config, end"


def weapon_config():
    print "weapon_config_m"
    outPath = getOutPath("weapon_m")
    ws = getWorkBook().get_sheet_by_name("Weapon")
    weaponConfig = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        if not cols[2]:
            continue
        oneWeapon = {}
        if str(cols[0]) in weaponConfig:
            raise KeyError("weaponId %d repeat" % int(cols[0]))
        weaponConfig[str(cols[2])] = oneWeapon
        oneWeapon["weaponId"] = int(cols[2])
        oneWeapon["costBullet"] = cols[3]
        oneWeapon["power"] = cols[4]
        oneWeapon["matchAddition"] = cols[5]
        oneWeapon["wpRatio"] = cols[12]

    print "weapon_config, end"
    result = json.dumps(weaponConfig, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def weaponPowerRate_config():
    print "weaponPowerRate_config, start"
    outPath = getOutPath("weaponPowerRate_m")
    ws = getWorkBook().get_sheet_by_name("WeaponPowerRate")
    powerRateConfig = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        oneRate =  []
        if str(cols[0]) in powerRateConfig:
            raise KeyError("weaponId %d repeat" % int(cols[0]))
        powerRateConfig[str(cols[0])] = oneRate
        probb = 0
        for m in range(2, len(cols), 2):
            if not cols[m]:
                break              
            item = {}
            item["value"] = json.loads(cols[m])
            itemProbb = cols[m + 1]
            item["probb"] = [probb + 1, probb + itemProbb]   
            oneRate.append(item)
            probb += itemProbb
    result = json.dumps(powerRateConfig, indent=4)
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "weaponPowerRate_config, end"


def level_funds_config(clientId=0):
    """
    成长基金奖励配置
    """
    sn = "LevelFunds" if clientId == 0 else "LevelFunds" + "_" + str(clientId)
    fn = "0.json" if clientId == 0 else str(clientId) + ".json"
    print "level_funds_config, start, ", sn, fn
    outPath = getOutPath("levelFunds_m", fn)
    wb = getWorkBook()
    ws = wb.get_sheet_by_name(sn)
    config = collections.OrderedDict()
    config["canBuyIdx"] = []                        # 可购买索引
    config["funds"] = []
    config["rewards"] = collections.OrderedDict()
    startRowNum = 4
    fundIdx = 2
    rewardsIdx = 13
    h = 0
    for row in ws.rows:
        h = h + 1
        if h < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0]:
            config["canBuyIdx"] = json.loads(cols[0])

        if cols[fundIdx]:
            one = collections.OrderedDict()
            config["funds"].append(one)             # 基金
            one["productId"] = cols[fundIdx + 1]    # 商品
            one["idx"] = cols[fundIdx + 0]          # 索引
            one["type"] = cols[fundIdx + 2]         # 类型
            one["name"] = cols[fundIdx + 3]
            one["buyType"] = cols[fundIdx + 4]      # 购买方式
            one["price_direct"] = one["price"] = cols[fundIdx + 5]  # 价格/元
            one["price_diamond"] = cols[fundIdx + 6]                # 钻石价格
            one["otherBuyType"] = json.loads(cols[fundIdx + 7])     # 其他购买方式
            one["title"] = cols[fundIdx + 8]        # 标题宣传语
            one["showLevel"] = cols[fundIdx + 9]    # 展示等级

        if cols[rewardsIdx]:
            config["rewards"].setdefault(str(cols[rewardsIdx + 1]), [])     # 奖励
            one = collections.OrderedDict()
            config["rewards"][str(cols[rewardsIdx + 1])].append(one)        # 商品索引: [] 要求火炮倍率
            one["level"] = int(cols[rewardsIdx + 0])                        # 等级
            one["free_rewards"] = json.loads(cols[rewardsIdx + 3])          # 免费奖励数量
            one["rechargeBonus"] = int(cols[rewardsIdx + 4])                # 充值奖池
            one["funds_rewards"] = json.loads(cols[rewardsIdx + 6])         # 基金奖励数量

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "level_funds_config, end"


def prizewheel_m_config():
    """
    渔场轮盘配置
    """
    print "prizewheel_m_config, start"
    outPath = getOutPath("prizeWheel_m")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("LevelPrizeWheel")
    config = collections.OrderedDict()
    config["maxSpinTimes"] = 1
    config["condition"] = 0
    config["energy"] = {}
    config["prize"] = collections.OrderedDict()
    config["bet"] = collections.OrderedDict()
    startRowNum = 4
    h = 0

    wheelIdx = 5
    betIdx = 38

    for row in ws.rows:
        h = h + 1
        if h < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0]:
            config["maxSpinTimes"] = int(cols[0])

        if cols[2]:
            for i in range(2, 4, 2):
                config["energy"][str(cols[i])] = int(cols[i + 1])

        if cols[wheelIdx]:
            config["prize"].setdefault(str(cols[wheelIdx]), collections.OrderedDict())
            config["prize"][str(cols[wheelIdx])]["betList"] = json.loads(cols[wheelIdx + 1])
            wheel = []
            for i in range(wheelIdx + 2, wheelIdx + 32, 3):
                one = collections.OrderedDict()
                one["rewards"] = json.loads(cols[i])
                one["rate"] = int(cols[i + 1])
                one["reset"] = int(cols[i + 2])
                wheel.append(one)
            config["prize"][str(cols[wheelIdx])]["wheel"] = wheel

        if cols[betIdx]:
            one = collections.OrderedDict()
            config["bet"][str(cols[betIdx])] = one
            for i in range(betIdx + 1, betIdx + 2, 2):
                one[str(cols[i])] = json.loads(cols[i + 1])

        if cols[42]:
            config["condition"] = cols[42]

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "prizewheel_m_config, end"


def time_point_match_skill():
    """
    回馈赛的随机技能配置
    """
    print "time_point_match_skill, start"
    outPath = getOutPath("timePointMatchSkill_m")
    ws = getWorkBook().get_sheet_by_name("TimePointMatchSkill")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue

        if row[1].value not in config.keys():
            skillId = collections.OrderedDict()
            config[int(row[1].value)] = skillId
            skillId['skill_1'] = []
            skillId['weight_1'] = []
            skillId['skill_2'] = []
            skillId['weight_2'] = []

        for cell in row:
            cols.append(cell.value)

        skillId["skill_1"].append(int(cols[2]))
        skillId["weight_1"].append(int(cols[3]))
        skillId["skill_2"].append(int(cols[4]))
        skillId["weight_2"].append(int(cols[5]))

    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "time_point_match_skill, end"


def getMultipleFish(ws):
    multipleFish = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols:
            continue
        if not cols[0]: 
            continue
        one = []
        multipleFish[str(cols[0])] = one
        probb = 0
        highProbb = 0
        rechargeProbb = 0
        for x in xrange(1, len(cols), 4):
            multiple = collections.OrderedDict()
            itemProbb = int(cols[x + 1] or 0)
            itemHighProbb = int(cols[x + 2] or 0)
            itemRechargeProbb = int(cols[x + 3] or 0)
            if itemProbb <= 0 and itemHighProbb <= 0 and itemRechargeProbb <= 0:
                continue
            multiple["multiple"] = int(cols[x])
            if itemProbb:
                multiple["probb"] = [probb + 1, probb + itemProbb]
            if itemHighProbb:
                multiple["highProbb"] = [highProbb + 1, highProbb + itemHighProbb]
            if itemRechargeProbb:
                multiple["rechargeProbb"] = [rechargeProbb + 1, rechargeProbb + itemRechargeProbb]
            probb += itemProbb
            highProbb += itemHighProbb
            rechargeProbb += itemRechargeProbb
            one.append(multiple)
    return multipleFish


def getMatchBufferFish(ws):
    bufferFish = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]: 
            continue
        one = []
        bufferFish[str(cols[0])] = one
        probb = 0
        for x in xrange(1, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["fishType"] = int(cols[x])
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            one.append(fish)
    return bufferFish


def getBossFish(ws):
    bossFish = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]: 
            continue
        one = []
        bossFish[str(cols[0])] = one
        probb = 0
        for x in xrange(1, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["fishType"] = int(cols[x])
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            one.append(fish)
    return bossFish


def getBossMultiple(ws):
    bossMultiple = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]: 
            continue
        one = []
        bossMultiple[str(cols[0])] = one
        probb = 0
        for x in xrange(1, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["multiple"] = float(cols[x])
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            one.append(fish)
    return bossMultiple


def probability_config_m():
    print "probability_config_m, start"
    outPath = getOutPath("probability_m")
    wb = getWorkBook()
    config = collections.OrderedDict()
    multipleFish = getMultipleFish(wb.get_sheet_by_name("MultipleFish"))
    bossFish = getBossFish(wb.get_sheet_by_name("BossFish"))
    bossMultiple = getBossMultiple(wb.get_sheet_by_name("BossMultiple"))
    bufferFish = getMatchBufferFish(wb.get_sheet_by_name("MatchBufferFish"))

    config["multipleFish"] = multipleFish
    config["bossFish"] = bossFish
    config["bossMultiple"] = bossMultiple
    config["bufferFish"] = bufferFish
    result = json.dumps(config, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)
    print "probability_config_m, end"


def terror_fish_m():
    """特殊鱼出现的概率和间隔"""
    outPath = getOutPath("terrorFish_m")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("TerrorFish")
    config = collections.OrderedDict()
    terrorFish = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]:
            continue
        one = []
        terrorFish[str(cols[0])] = one          # 渔场44411、44412、44414、44415、44501、44601
        interval = int(cols[1])
        probb = 0
        for x in xrange(2, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["fishType"] = int(cols[x])     # 鱼ID
            fish["interval"] = interval         # 间隔(秒)
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb]  # 概率
            probb += itemProbb
            one.append(fish)
    config["terrorFish"] = terrorFish
    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def autofill_fish_m():
    """
    填充鱼配置
    """
    def parse(saveDict, cols):
        if cols[0] and cols[0] not in saveDict:
            saveDict[cols[0]] = collections.OrderedDict()       # 渔场ID
        if cols[3] and cols[3] not in saveDict[cols[0]]:
            fishCategory = collections.OrderedDict()
            saveDict[cols[0]][cols[3]] = fishCategory           # 渔场ID: {鱼种类别: {}}
            fishCategory["categoryId"] = str(cols[3])           # 鱼种类别
            fishCategory["cSupplyInterval"] = int(cols[1])      # 鱼类填充时间间隔
            fishCategory["sSupplyInterval"] = int(cols[2])      # 鱼群填充时间间隔
            fishCategory["groups"] = []                         # 鱼群
        group = collections.OrderedDict()
        group["groupType"] = int(cols[4])                       # 分组类型
        group["fishes"] = []                                    # 鱼
        for x in xrange(5, len(cols), 6):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = collections.OrderedDict()
            fish["fishType"] = int(cols[x + 1])
            fish["weight"] = int(cols[x + 2])
            fish["fishCount"] = int(cols[x + 3])
            fish["minCount"] = int(cols[x + 4])
            fish["maxCount"] = int(cols[x + 5])
            group["fishes"].append(fish)
        saveDict[cols[0]][cols[3]]["groups"].append(group)
        return saveDict

    outPath = getOutPath("autofillFish_m")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("AutofillFish")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    isFindBlank = False
    defaultDict = collections.OrderedDict()
    bossDict = collections.OrderedDict()
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]:
            isFindBlank = True
            startRowNum += i
            continue
        if not isFindBlank:             # 是否发现空行
            defaultDict = parse(defaultDict, cols)
        else:
            bossDict = parse(bossDict, cols)
    config["default"] = defaultDict
    config["superBoss"] = bossDict
    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def weapon_stage_count_config():
    """
    武器的爆炸次数
    """
    print "weapon_stage_count_config, start"
    outPath = getOutPath("weaponStageCount_m")
    ws = getWorkBook().get_sheet_by_name("WeaponStageCount")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue

        for cell in row:
            cols.append(cell.value)

        if not cols[0]:
            continue

        if int(cols[0]) not in config:
            config[int(cols[0])] = []
        for x in xrange(2, len(cols)):
            if cols[x] is None:
                continue
            config[int(cols[0])].append(int(cols[x]))
        if sum(config[int(cols[0])]) != 10000:
            raise KeyError("weapon_stage_count_config probb error")

    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "weapon_stage_count_config, end"


def tide_task_config():
    """鱼潮任务"""
    print "tide_task_config, start"
    outPath = getOutPath("tideTask")
    ws = getWorkBook().get_sheet_by_name("TideTask")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("group_name %d repeat" % int(cols[0]))
        config[str(cols[0])] = one                                  # 鱼潮鱼阵Id
        one["group"] = cols[0]                                      # 鱼群
        one["taskId"] = cols[1]
        one["tipSeconds"] = cols[2]
        one["readySeconds"] = cols[3]                               # 准备时间
        one["timeLong"] = cols[4]
        one["taskType"] = cols[5]
        one["desc"] = unicode(cols[6] or "")
        targets = collections.OrderedDict()
        one["targets"] = targets
        if cols[7]:
            targets["target"] = cols[7]
        if cols[8]:
            targets["number"] = cols[8]
        one["rewards"] = {}
        if cols[9]:
            one["rewards"]["name"] = cols[9]
        if cols[10]:
            one["rewards"]["count"] = cols[10]
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "tide_task_config, end"


def fixed_multiple_fish():
    """倍率鱼"""
    print "fixed_multiple_fish, start"
    outPath = getOutPath("fixedMultipleFish")
    ws = getWorkBook().get_sheet_by_name("FixedMultipleFish")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]: 
            continue
        probbConf = {}
        one = []
        config[str(cols[0])] = probbConf
        probbConf["range"] = json.loads(str(cols[1]))
        probbConf["probb"] = cols[2]
        probbConf["multiples"] = one
        probb = 0
        for x in xrange(3, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            multiple = collections.OrderedDict()
            itemProbb = int(cols[x + 1])
            multiple["multiple"] = int(cols[x])
            multiple["probb"] = [probb + 1, probb + itemProbb]
            probb += itemProbb
            one.append(multiple)
    result = json.dumps(config, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "fixed_multiple_fish, end"


def match_multiple_fish():
    print "match_multiple_fish, start"
    outPath = getOutPath("matchMultipleFish")
    ws = getWorkBook().get_sheet_by_name("MatchMultipleFish")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]: 
            continue
        probbConf = []
        config[str(cols[0])] = probbConf
        for x in xrange(4):
            multiples = []
            luckyValueConf = collections.OrderedDict()
            luckyValueConf["luckyValue"] = int(cols[9 * x + 1])
            luckyValueConf["multiples"] = multiples
            probb = 0
            for y in xrange(9 * x + 2, 9 * (x + 1), 2):
                if not cols[y] or not cols[y + 1]:
                    continue
                multiple = collections.OrderedDict()
                multiples.append(multiple)
                multiple["multiple"] = int(cols[y])
                itemProbb = int(cols[y + 1])
                multiple["probb"] = [probb + 1, probb + itemProbb]
                probb += itemProbb
            probbConf.append(luckyValueConf)
    result = json.dumps(config, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "match_multiple_fish, end"


def randomMultipleFish_config():
    print "randomMultipleFish_config, start"
    outPath = getOutPath("randomMultipleFish")
    ws = getWorkBook().get_sheet_by_name("RandomMultipleFish")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i+1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]: 
            continue
        multiples = []
        config[str(cols[0])] = multiples
        totalProbb = 0
        for x in range(1, len(cols), 2):
            if not cols[x + 1]:
                continue
            one = collections.OrderedDict()
            one["fishType"] = int(cols[x])
            one["probb"] = [totalProbb + 1, totalProbb + cols[x + 1]]
            totalProbb += cols[x + 1]
            multiples.append(one)
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "randomMultipleFish_config, end"


def plyerBuffer_config():
    print "plyerBuffer_config, start"
    outPath = getOutPath("playerBuffer")
    ws = getWorkBook().get_sheet_by_name("PlayerBuffer")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i+1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if cols[0] ==0 or not cols[0]: 
            continue
        one = collections.OrderedDict()
        config[str(cols[0])] = one
        one["bufferId"] = int(cols[0])
        one["weaponIds"] = json.loads(cols[1])
        one["weaponType"] = json.loads(cols[2])
        one["cdReduce"] = float(cols[3])
        one["coinAdd"] = float(cols[4])
        one["powerAdd"] = float(cols[5])
        one["duration"] = int(cols[6])
        one["delayTime"] = float(cols[7])
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "plyerBuffer_config, end"


def platter_fish():
    """大盘鱼出现的概率和间隔"""
    outPath = getOutPath("platterFish")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("PlatterFish")
    config = collections.OrderedDict()
    platterFish = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]:
            continue
        one = []
        platterFish[str(cols[0])] = one
        interval = int(cols[1])
        probb = 0
        for x in xrange(2, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["fishType"] = int(cols[x])
            fish["interval"] = interval
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb]
            probb += itemProbb
            one.append(fish)
    config["platterFish"] = platterFish
    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def super_boss_drop_config():
    """超级Boss掉落"""
    print "super_boss_drop_config, start"
    outPath = getOutPath("superBossDrop")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("SuperBossDrop")
    config = collections.OrderedDict()
    config["goldCoin"] = collections.OrderedDict()
    config["goldRing"] = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if cols[0]:
            x = 0
            one = collections.OrderedDict()
            config["goldCoin"][str(cols[x + 1])] = one
            one["kindId"] = int((cols[x + 2]))
            one["score"] = int((cols[x + 3]))
            one["value"] = int((cols[x + 4]))
        if cols[6]:
            x = 6
            one = collections.OrderedDict()
            config["goldRing"][str(cols[x + 1])] = one
            one["kindId"] = int((cols[x + 2]))
            one["score"] = int((cols[x + 3]))
            one["value"] = int((cols[x + 4]))
    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "super_boss_drop_config, end"


def catch_drop_config():
    print "catch_drop_config, start"
    outPath = getOutPath("catchDrop_m")
    ws = getWorkBook().get_sheet_by_name("CatchDrop")
    config = collections.OrderedDict()
    startRowNum = 4
    config["dropGunX"] = collections.OrderedDict()
    config["dropGroup"] = collections.OrderedDict()

    dropDataStartIdx = 0
    dropGroupStartIdx = 18

    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[dropDataStartIdx] is not None:
            gunDropList = []
            config["dropGunX"][cols[dropDataStartIdx]] = gunDropList
            for x in xrange(dropDataStartIdx + 1, dropGroupStartIdx - 1, 4):
                if cols[x] is not None:
                    itemDict = collections.OrderedDict()
                    itemDict["dropGroupId"] = int(cols[x])
                    itemDict["min"] = int(cols[x + 1])
                    itemDict["max"] = int(cols[x + 2])
                    itemDict["probability"] = int(cols[x + 3])
                    gunDropList.append(itemDict)

        if cols[dropGroupStartIdx] is not None:
            dropGroupDict = collections.OrderedDict()
            config["dropGroup"].setdefault(int(cols[dropGroupStartIdx]), dropGroupDict)
            dropGroupDict["fishTypeList"] = json.loads(cols[dropGroupStartIdx + 1])
            dropGroupDict["dropItemList"] = [json.loads(cols[dropGroupStartIdx + 2]), json.loads(cols[dropGroupStartIdx + 3])]

    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "catch_drop_config, end"


def level_gift_config():
    print "level_gift_config, start"
    outPath = getOutPath("levelGift_m")
    ws = getWorkBook().get_sheet_by_name("LevelGift")
    config = collections.OrderedDict()
    # config["LevelGift"] = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0]:
            one = collections.OrderedDict()
            config[int(cols[0])] = one
            one["giftId"] = int(cols[0])
            one["giftName"] = unicode(cols[1])
            one["productId"] = cols[2]
            one["minLevel"] = cols[3]
            one["maxLevel"] = cols[4]
            one["levelUp"] = int(cols[5])
            one["showTime"] = cols[6]
            one["buyType"] = cols[7]
            one["priceDiamond"] = int(cols[8])
            one["discountPrice"] = int(cols[9])
            one["rewards"] = []
            for x in range(10, len(cols), 2):
                if cols[x] is None or int(cols[x]) == 0:
                    continue
                item = collections.OrderedDict()
                item["name"] = int(cols[x])
                item["count"] = int(cols[x + 1])
                one["rewards"].append(item)

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "level_gift_config, end"


def getWorkBook(filename="newfish_multiple.xlsm"):
    configFile = os.path.split(os.path.realpath(__file__))[0] + "/%s" % filename
    return load_workbook(filename=configFile, read_only=True, data_only=True)


def getOutPath(dirname, filename="0.json"):
    global ServerPath
    dirPath = os.path.split(os.path.realpath(__file__))[0] + ServerPath + "/%s/" % (dirname)
    filePath = dirPath + filename
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    return filePath


def process_single_config(idx, task_queue, cost_queue, err_queue, sp):
    """
    处理单个配置文件
    :param idx: 进程编号1、2、3、4、5、6、7、8
    :param task_queue: 任务队列
    :param cost_queue:
    :param err_queue: 出错队列
    :param sp: 文件路径
    :return:
    """
    reload(sys)
    sys.setdefaultencoding("utf-8")
    print "---- %d cpu start!" % idx
    global ServerPath
    ServerPath = sp
    while not task_queue.empty():
        confFunc, arg = task_queue.get()                            # 获取任务队列
        try:
            t1 = time.time()
            if arg is None:
                confFunc()
            else:
                confFunc(arg)
            _costTime = time.time() - t1
            if arg is None:
                cost_queue.put((confFunc.__name__, _costTime))      # 任务执行的时间
            else:
                cost_queue.put((confFunc.__name__ + "_" + str(arg), _costTime))
        except Exception, e:
            print "=========== export ", confFunc.__name__, " failed ! ", e, traceback.format_exc()
            err_queue.put((confFunc.__name__ + "_" + str(arg), traceback.format_exc()))


# 配置列表
config_list = [
    (superboss_exchange_config, None),
    (superboss_minigame_config, None),
    (superboss_common_config, None),
    (fish_config, None),
    (match_fish_config, None),
    (skill_grade_config, None),
    (skill_star_config, None),
    (gunLevel, None),                       # 火炮倍率
    (gunskin_config, None),                 # 火炮和皮肤
    (weapon_config, None),                  # 武器配置
    (weaponPowerRate_config, None),
    (weapon_stage_count_config, None),
    (level_funds_config, None),
    (level_funds_config, 25794),
    (prizewheel_m_config, None),
    (time_point_match_skill, None),
    (probability_config_m, None),
    (terror_fish_m, None),
    (autofill_fish_m, None),
    (tide_task_config, None),
    (fixed_multiple_fish, None),
    (match_multiple_fish, None),
    (randomMultipleFish_config, None),
    (plyerBuffer_config, None),
    (platter_fish, None),                   # 大盘鱼
    (super_boss_drop_config, None),
    (catch_drop_config, None),
    (level_gift_config, None),              # 等级礼包
]


if __name__ == "__main__":
    TestConfPath = ""
    RealeaseConfPath = ""
    print "begin"
    t1 = int(time.time())
    ServerPath = '/../../../../../../wx_superboss/trunk/xxfish_dev/config37/game/44'  # 默认练习路径
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        ServerPath = '/../../../../../../wx_superboss/xxfish_dev/config37/game/44'
    # else:
    #     ServerPath = "/../../../../../../../gameServer/hall37/newfish-py/wx_superboss/xxfish_dev/config37/game/44"

    import platform
    _system = platform.system()
    if _system == "Darwin" and len(sys.argv) > 1 and sys.argv[1] == "-k":
        upConfig = "svn up .%s" % ServerPath
        os.system("svn up ./")
        os.system(upConfig)
        print "update %s finish" % ServerPath

    print "----- start, config"
    conf_queue = Queue(len(config_list))
    for conf in config_list:
        conf_queue.put(conf)  # 任务队列
    cost_queue = Queue()  # 执行队列的时间
    err_queue = Queue()  # 错误的队列
    isUseMultiProcess = len(sys.argv) > 2 and sys.argv[2] == "-m" and cpu_count() > 1
    if isUseMultiProcess:
        freeze_support()
        processList = [Process(target=process_single_config, args=(i + 1, conf_queue, cost_queue, err_queue, ServerPath)) for i in range(cpu_count())]
        for p in processList:
            p.start()  # 开始时间
        for p in processList:
            p.join()
    else:
        process_single_config(0, conf_queue, cost_queue, err_queue, ServerPath)

    # s1 = set()
    # while not cost_queue.empty():
    #     fn, costTime = cost_queue.get()
    #     s1.add(fn)
    #     if costTime > 5:
    #         print fn, costTime
    while not err_queue.empty():
        print err_queue.get()
    # windows需要转换json的换行符.
    if _system == "Windows":
        # print "json format: windows->unix, start"
        import os
        if TestConfPath:
            os.system(r".\jsonDos2Unix.bat %s" % TestConfPath)
        if RealeaseConfPath:
            os.system(r".\jsonDos2Unix.bat %s" % RealeaseConfPath)
        # print "json format: windows->unix, end"

    t2 = int(time.time())
    print "----- load config successfully"
    print "----- out full path: %s" % os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + ServerPath)
    if isUseMultiProcess:
        print "----- %d cpu, process %d files, export json cost %d s" % (cpu_count(), len(config_list), t2 - t1)
    else:
        print "----- process %d files, export json cost %d s" % (len(config_list), t2 - t1)

