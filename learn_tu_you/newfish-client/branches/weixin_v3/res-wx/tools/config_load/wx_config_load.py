#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
from openpyxl import load_workbook
import os, sys, json, copy
import collections
import re
import csv
from multiprocessing import Queue, Process, cpu_count, freeze_support

ServerPath = ""
ClientIdMap = None


def drop_config():
    '''
    掉落的配置
    :return:
    '''
    outPath = getOutPath("drop")                    # 输出的文件名字
    ws = getWorkBook().get_sheet_by_name("Drop")    # 获取的Drop
    dropConfig = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        print cols
        if len(cols) < 5:
            continue
        oneDrop = {}
        if str(cols[0]) in dropConfig:
            raise KeyError("dropId %d repeat" % int(cols[0]))
        dropConfig[str(cols[0])] = oneDrop
        oneDrop["type"] = int(cols[2])
        oneDrop["randomCount"] = int(cols[3])
        oneDrop["items"] = []
        probb = 0
        for m in range(4, len(cols), 3):
            if len(cols) - m < 3:
                break
            if not cols[m]:
                break
            item = {}
            item["itemId"] = cols[m]
            item["number"] = cols[m + 1]
            itemProbb = cols[m + 2]
            item["probb"] = [probb + 1, probb + itemProbb]
            oneDrop["items"].append(item)
            probb += itemProbb
    result = json.dumps(dropConfig, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def fish_config():
    '''
    鱼的配置
    :return:
    '''
    outPath = getOutPath("fish")
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
        if not cols[3]:                 # 鱼种ID
            continue
        print cols
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("fishId %d repeat" % int(cols[0]))
        config[str(cols[3])] = one          # {11001: {}}
        one["name"] = unicode(cols[1])      # 鱼的名字
        one["type"] = int(cols[4])          # 鱼的类别
        if is_number(cols[5]):
            one["itemId"] = int(cols[5])    # 捕鱼掉道具 数字
        else:
            one["itemId"] = json.loads(cols[5])     # [10000,10002]
        one["score"] = int(cols[6])                 # 分值
        one["minCount"] = int(cols[7])              # 掉落最小值
        one["maxCount"] = int(cols[8])
        one["probb1"] = float("%.1f" % cols[9])     # 无HP时概率基数
        one["probb2"] = float("%.1f" % cols[10])
        one["HP"] = int(cols[11])                   # 生命
        one["value"] = int(cols[12])                # 实际价值
        if cols[14]:
            one["weaponId"] = int(cols[14])         # 武器Id
        one["prizeWheelValue"] = float(cols[15])    # 积攒价值
        one["triggerRate"] = int(cols[16])          # 触发几率(10000)
        one["catchValue"] = float(cols[17])         # 价值
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def is_number(s):
    try:
        float(s)                        # 是float类型
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)          # 把一个表示数字的字符串转换为浮点数返回
        return True
    except (TypeError, ValueError):
        pass

    return False


def match_fish_config():
    '''
    比赛鱼的配置
    :return:
    '''
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
        print cols
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


def weapon_config():
    """武器配置"""
    print "weapon_config"
    outPath = getOutPath("weapon")
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

    result = json.dumps(weaponConfig, indent=4)

    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def chest_config():
    print u"start 宝箱配置Chest"
    outPath = getOutPath("chest")
    ws = getWorkBook().get_sheet_by_name("Chest")
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
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("chestId %d repeat" % int(cols[0]))
        config[str(cols[0])] = one
        one["chestId"] = int(cols[0])
        one["name"] = unicode(cols[1])
        one["star"] = int(cols[3])
        one["type"] = int(cols[4])
        one["show"] = int(cols[5])              # 是否显示星级
        one["kindId"] = int(cols[6])            # 兑换券道具ID
        one["unlockTime"] = int(cols[7])        # 解锁时间
        one["levelRange"] = map(int, str(cols[8]).split(","))   # 宝箱级别范围
        one["openCoin"] = int(cols[9])          # 开启消耗金币/分钟
        startNum = 9
        assert int(cols[startNum + 1]) <= int(cols[startNum + 2])
        one["coinRange"] = [int(cols[startNum + 1]), int(cols[startNum + 2])]   # 金币最小数量 金币最大数量
        assert int(cols[startNum + 3]) <= int(cols[startNum + 4])
        one["pearlRange"] = [int(cols[startNum + 3]), int(cols[startNum + 4])]  # 珍珠最小数量
        # 技能卡
        one["nCardRate"] = int(cols[startNum + 5])
        one["nCardRandom"] = int(cols[startNum + 6])
        assert int(cols[startNum + 7]) <= int(cols[startNum + 8])
        one["nCardRange"] = [int(cols[startNum + 7]), int(cols[startNum + 8])]
        one["rCardRate"] = int(cols[startNum + 9])
        one["rCardRandom"] = int(cols[startNum + 10])
        assert int(cols[startNum + 11]) <= int(cols[startNum + 12])
        one["rCardRange"] = [int(cols[startNum + 11]), int(cols[startNum + 12])]
        one["srCardRate"] = int(cols[startNum + 13])
        one["srCardRandom"] = int(cols[startNum + 14])
        assert int(cols[startNum + 15]) <= int(cols[startNum + 16])
        one["srCardRange"] = [int(cols[startNum + 15]), int(cols[startNum + 16])]
        one["cardCertain"] = int(cols[startNum + 17])
        one["cardCertainRateRange"] = map(int, str(cols[startNum + 18]).split(",")) if cols[startNum + 18] else []
        one["cardCertainNum"] = int(cols[startNum + 19])
        # 升星卡
        one["nStarCardRate"] = int(cols[startNum + 20])
        one["nStarCardRandom"] = int(cols[startNum + 21])
        assert int(cols[startNum + 22]) <= int(cols[startNum + 23])
        one["nStarCardRange"] = [int(cols[startNum + 22]), int(cols[startNum + 23])]
        one["rStarCardRate"] = int(cols[startNum + 24])
        one["rStarCardRandom"] = int(cols[startNum + 25])
        assert int(cols[startNum + 26]) <= int(cols[startNum + 27])
        one["rStarCardRange"] = [int(cols[startNum + 26]), int(cols[startNum + 27])]
        one["srStarCardRate"] = int(cols[startNum + 28])
        one["srStarCardRandom"] = int(cols[startNum + 29])
        assert int(cols[startNum + 30]) <= int(cols[startNum + 31])
        one["srStarCardRange"] = [int(cols[startNum + 30]), int(cols[startNum + 31])]
        one["starCardCertain"] = int(cols[startNum + 32])
        one["starCardCertainRateRange"] = map(int, str(cols[startNum + 33]).split(",")) if cols[startNum + 33] else []
        one["starCardCertainNum"] = int(cols[startNum + 34])
        # 火炮、水晶、奖券、海星、冷却
        one["gunSkinRate"] = int(cols[startNum + 35])
        one["gunSkinRandom"] = int(cols[startNum + 36])
        assert int(cols[startNum + 37]) <= int(cols[startNum + 38])
        one["gunSkinRange"] = [int(cols[startNum + 37]), int(cols[startNum + 38])]
        one["crystalRate"] = int(cols[startNum + 39])
        one["crystalRandom"] = int(cols[startNum + 40])
        assert int(cols[startNum + 41]) <= int(cols[startNum + 42])
        one["crystalRange"] = [int(cols[startNum + 41]), int(cols[startNum + 42])]
        one["couponRate"] = int(cols[startNum + 43])
        assert int(cols[startNum + 44]) <= int(cols[startNum + 45])
        one["couponRange"] = [int(cols[startNum + 44]), int(cols[startNum + 45])]
        one["starfishRate"] = int(cols[startNum + 46])
        assert int(cols[startNum + 47]) <= int(cols[startNum + 48])
        one["starfishRange"] = [int(cols[startNum + 47]), int(cols[startNum + 48])]
        one["coolDownRate"] = int(cols[startNum + 49])
        assert int(cols[startNum + 50]) <= int(cols[startNum + 51])
        one["coolDownRange"] = [int(cols[startNum + 50]), int(cols[startNum + 51])]
        # 青铜、白银、黄金招财珠数
        one["bronzeBulletRate"] = int(cols[startNum + 52])
        assert int(cols[startNum + 53]) <= int(cols[startNum + 54])
        one["bronzeBulletRange"] = [int(cols[startNum + 53]), int(cols[startNum + 54])]
        one["silverBulletRate"] = int(cols[startNum + 55])
        assert int(cols[startNum + 56]) <= int(cols[startNum + 57])
        one["silverBulletRange"] = [int(cols[startNum + 56]), int(cols[startNum + 57])]
        one["goldBulletRate"] = int(cols[startNum + 58])
        assert int(cols[startNum + 59]) <= int(cols[startNum + 60])
        one["goldBulletRange"] = [int(cols[startNum + 59]), int(cols[startNum + 60])]
        # 红宝石
        one["rubyRate"] = int(cols[startNum + 61])
        assert int(cols[startNum + 62]) <= int(cols[startNum + 63])
        one["rubyRange"] = [int(cols[startNum + 62]), int(cols[startNum + 63])]
        # 出现其他物品id，概率，最小数量，最大数量
        one["itemsData"] = json.loads(cols[startNum + 64])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print u"end 宝箱配置Chest"


def chest_drop_config():
    print u"start 宝箱掉落配置ChestDrop"
    outPath = getOutPath("chestDrop")
    ws = getWorkBook().get_sheet_by_name("ChestDrop")
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
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("kindId %d repeat" % int(cols[0]))
        config[str(cols[0])] = one
        one["kindId"] = int(cols[0])            # 物品ID
        one["type"] = int(cols[3])
        one["rare"] = int(cols[4])              # 稀有度
        one["level"] = int(cols[5])
        one["unlock"] = int(cols[6])
        one["weight"] = int(cols[7])
        one["convertCoin"] = int(cols[8])       # 溢出后转换金币数

    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print u"end 宝箱掉落配置ChestDrop"


def dynamic_odds_config():
    print u"start 动态概率配置 DynamicOdds"
    outPath = getOutPath("dynamicOdds")
    ws = getWorkBook().get_sheet_by_name("DynamicOdds")
    dynamicOdds = collections.OrderedDict()
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
        dynamicOdds.setdefault(int(cols[0]), collections.OrderedDict())     # 所在渔场
        fishPool = dynamicOdds[int(cols[0])]
        wave = collections.OrderedDict()
        fishPool[str(cols[1])] = wave   # 曲线ID
        wave["waveId"] = int(cols[1])   # 曲线ID
        wave["weight"] = int(cols[2])   # 权重
        wave["type"] = float(cols[3])   # 涨还是跌 0为分界线
        wave["frequency"] = []          # 曲率列表
        for x in xrange(4, len(cols)):
            if cols[x] is None:
                break
            wave["frequency"].append(float(cols[x]))

    result = json.dumps(dynamicOdds, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print u"end 动态概率配置 DynamicOdds"


def vip_config():
    print "vip_config, start"
    outPath = getOutPath("vip")
    reload(sys)
    sys.setdefaultencoding("utf-8")
    ws = getWorkBook().get_sheet_by_name("Vip")
    config = collections.OrderedDict()
    startRowNum = 4

    expStartIdx = 11
    i = 0
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if not cols[0]:
            if i != startRowNum:
                break
        one = collections.OrderedDict()
        config[str(cols[0])] = one
        one["vipLv"] = int(cols[0])
        one["vipPresentCount:1137"] = int(cols[1])      # 赠送珍珠数
        one["vipPresentCount:1193"] = int(cols[2])      # 赠送银弹头数
        one["vipPresentCount:1194"] = int(cols[3])      # 赠送金弹头数
        one["vipPresentCount:1426"] = int(cols[4])      # 赠送代购券数
        one["vipPresentCount:1408"] = int(cols[5])      # 赠送冷却道具数量
        one["vipPresentCount:1429"] = int(cols[6])      # 赠送紫水晶数量
        one["vipPresentCount:1430"] = int(cols[7])      # 赠送黄水晶数量
        one["vipPresentCount:1431"] = int(cols[8])      # 赠送五彩水晶数量
        one["vipReceiveCount:1194"] = int(cols[9])      # 可接收金珠数量
        one["vipReceiveCount:1193"] = int(cols[10])     # 可接收银珠数量
        one["vipExp"] = int(cols[expStartIdx])          # VIP经验值
        one["freeRouletteTimes"] = int(cols[expStartIdx + 1])   # 免费海星许愿次数
        one["dropPearlTotalCount"] = int(cols[expStartIdx + 2]) # 掉落珍珠累计总量限制
        one["dropPearlRatioLimit"] = cols[expStartIdx + 3]      # 掉落总量超出后Level表中系数
        one["vipDesc"] = unicode(cols[expStartIdx + 4]) or ""   # VIP描述
        one["vipGift"] = json.loads(cols[expStartIdx + 5])      # VIP礼包
        one["originalPrice"] = int(cols[expStartIdx + 6])       # VIP礼包原价
        one["price"] = int(cols[expStartIdx + 7])               # VIP礼包现价
        one["pearlMultiple"] = float(cols[expStartIdx + 8])     # 任务珍珠加成倍率
        one["matchAddition"] = float(cols[expStartIdx + 9])     # 比赛分数加成
        one["setVipShow"] = int(cols[expStartIdx + 10])         # 设置vip展示
        one["almsRate"] = float(cols[expStartIdx + 11])         # 救济金倍率
        one["autoSupply:101"] = int(cols[expStartIdx + 12])     # 每日金币补足
        one["initLuckyValue:44102"] = int(cols[expStartIdx + 13])   # 比赛初始幸运值
        one["inviterReward"] = json.loads(cols[expStartIdx + 14])   # 给邀请人的奖励
        one["contFire"] = int(cols[expStartIdx + 15])               # 是否可以连发
        one["enableChat"] = int(cols[expStartIdx + 16])             # 是否可以聊天
        one["limitChatTip"] = unicode(cols[expStartIdx + 17] or "") # 限制聊天提示
        one["convert1137ToDRate"] = json.loads(cols[expStartIdx + 18])  # 珍珠换钻石比例
        one["convert1429ToDRate"] = json.loads(cols[expStartIdx + 19])  # 紫水晶换钻石比例
        one["convert1430ToDRate"] = json.loads(cols[expStartIdx + 20])  # 黄水晶换钻石比例
        one["convert1431ToDRate"] = json.loads(cols[expStartIdx + 21])  # 五彩水晶换钻石比例
        one["grandPrixFreeTimes"] = int(cols[expStartIdx + 22])         # 大奖赛免费次数
        one["grandPrixAddition"] = float(cols[expStartIdx + 23])        # 大奖赛分数加成
        one["checkinRechargeBonus"] = int(cols[expStartIdx + 24])       # 签到增加奖池额度

    result = json.dumps(config, indent=4, ensure_ascii=False)
    result = re.sub(r"\\\\n", r"\\n", result)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "vip_config, end"





def fixed_multiple_fish():
    """固定倍率鱼"""
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


def weaponPowerRate_config():
    """加载武器威力加成配置"""
    outPath = getOutPath("weaponPowerRate")
    ws = getWorkBook().get_sheet_by_name("WeaponPowerRate")
    powerRateConfig = collections.OrderedDict()
    startRowNum = 4
    i = 0
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        oneRate = []
        if str(cols[0]) in powerRateConfig:
            raise KeyError("weaponId %d repeat" % int(cols[0]))
        powerRateConfig[str(cols[0])] = oneRate
        probb = 0
        for m in range(1, len(cols), 2):
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


def gunskin_config(clientId=0):
    """皮肤炮配置"""
    sn = "Gun" if clientId == 0 else "Gun" + "_" + str(clientId)
    sn2 = "GunSkin" if clientId == 0 else "GunSkin" + "_" + str(clientId)
    fn = "0.json" if clientId == 0 else str(clientId) + ".json"
    outPath = getOutPath("gun", fn)     # 输出到gun文件夹下 0.json 26312.json
    ws = getWorkBook().get_sheet_by_name(sn)
    wsSkin = getWorkBook().get_sheet_by_name(sn2)
    startRowNum = 4
    i = 0
    config = collections.OrderedDict()
    gunIds = []
    config["gunIds"] = gunIds                       # 皮肤炮IDS
    config["gun"] = collections.OrderedDict()       # 皮肤炮配置
    config["skin"] = collections.OrderedDict()      # 皮肤炮皮肤
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
        one["multiple"] = int(cols[3])
        one["unlockType"] = int(cols[4])
        one["unlockValue"] = int(cols[5])
        one["equipType"] = int(cols[6])
        one["equipValue"] = int(cols[7])
        one["exp"] = int(cols[8])
        one["totalExp"] = int(cols[9])
        one["effectAddition"] = float(cols[10])
        one["effectType"] = int(cols[11])
        one["effectProbb"] = int(cols[12])
        one["unlockDesc"] = unicode(cols[13] or "")
        one["equipDesc"] = unicode(cols[14] or "")
        one["unitPrice"] = int(cols[15])
        one["skins"] = json.loads(str(cols[16]))
        aloofOdds = []
        one["aloofOdds"] = aloofOdds
        for m in range(17, len(cols), 2):
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
        config["skin"][cols[0]] = one
        one["skinId"] = cols[0]
        one["gunId"] = cols[1]
        one["kindId"] = cols[2]
        one["consumeCount"] = cols[3]
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def item_config(clientId=0):
    """
    道具配置
    """
    sn = "Item" if clientId == 0 else "Item" + "_" + str(clientId)
    fn = "0.json" if clientId == 0 else str(clientId) + ".json"
    print "item_config, start, ", sn, fn
    outPath = getOutPath("item", fn)
    wb = getWorkBook()
    ws = wb.get_sheet_by_name(sn)
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

        if cols[0]:
            one = collections.OrderedDict()
            config[str(cols[0])] = one
            one["kindId"] = int(cols[0])
            one["order"] = int(cols[1])
            if not cols[2]:
                one["visibleInBag"] = 0
                continue
            if cols[3]:
                one["up_skill"] = 1
            one["actions"] = []
            one["name"] = str(cols[4])
            one["desc"] = str(cols[5])
            if cols[6]:
                one["minimumVersion"] = str(cols[6])
            one["reviewVerLimit"] = int(cols[7]) if cols[7] else 0
            actCnt = int(cols[8])
            for i in range(9, 9 + 2 * actCnt, 2):
                tmp = collections.OrderedDict()
                tmp["action"] = str(cols[i])
                if cols[i + 1]:
                    tmp["params"] = json.loads(cols[i + 1])
                one["actions"].append(tmp)

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "item_config, end"


def store_config():
    pass


def grandPrix_config():
    """
    大奖赛配置
    """
    # reload(sys)
    # sys.setdefaultencoding("utf-8")
    print "grandPrix_config, start"
    outPath = getOutPath("grandPrix")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("GrandPrix")
    config = collections.OrderedDict()
    config["info"] = collections.OrderedDict()
    config["playAddition"] = []
    config["openTimeRange"] = []
    config["fireCount"] = 0
    config["fee"] = collections.OrderedDict()
    config["pointRewards"] = []
    config["group"] = {}
    config["target"] = {}
    config["robotData"] = []
    config["surpassTarget"] = []

    startRowNum = 4

    playConfCols = 6
    openRangeConfCols = 11
    fireConfCols = 14
    feeConfCols = 16
    pointConfCols = 18
    groupConfCols = 21
    fakeDataConfCols = 28
    surpassDataCols = 33

    h = 0
    cnt = 1
    for row in ws.rows:
        h = h + 1
        if h < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0] is not None:
            config["info"]["enable"] = int(cols[0])         # 是否开启
            config["info"]["startDay"] = str(cols[1])       # 开启时间
            config["info"]["msg"] = str(cols[2])            # 邮件内容
            config["info"]["des"] = str(cols[3])            # 提示
            config["info"]["endDes"] = str(cols[4])         # 结束页面提示
            config["info"]["robot"] = json.loads(cols[5])   # [是否启用，多久后添加，[最小间隔，最大间隔]](分钟)
            config["info"]["level"] = int(cols[6])          # 最低等级

        if cols[playConfCols] is not None:
            one = collections.OrderedDict()
            config["playAddition"].append(one)
            one["playTimes"] = int(cols[playConfCols])          # 重新挑战次数
            one["addition"] = float(cols[playConfCols + 1])     # 积分加成 0.1

        if cols[openRangeConfCols] is not None:
            config["openTimeRange"].extend([str(cols[openRangeConfCols]), str(cols[openRangeConfCols + 1])])    # 开始时间、结束时间

        if cols[fireConfCols] is not None:                      # 开火，技能使用次数
            config["fireCount"] = json.loads(cols[fireConfCols])

        if cols[feeConfCols] is not None:
            config["fee"] = json.loads(cols[feeConfCols])       # 报名费

        if cols[pointConfCols] is not None:                     # 积分、奖励
            config["pointRewards"].append({"point": int(cols[pointConfCols]), "rewards": json.loads(cols[pointConfCols + 1])})

        if cols[groupConfCols] is not None:                     # 任务鱼、数量、积分
            config["group"].setdefault(str(cols[groupConfCols + 3]), [])
            config["group"][str(cols[groupConfCols + 3])].append(int(cols[groupConfCols + 1]))
            config["target"][str(cols[groupConfCols + 1])] = {"count": int(cols[groupConfCols + 4]), "point": int(cols[groupConfCols + 5])}

        if cols[fakeDataConfCols] is not None:                  # 假数据数量、最低积分、最高积分
            config["robotData"].append({"count": int(cols[fakeDataConfCols + 1]), "points": [int(cols[fakeDataConfCols + 2]), int(cols[fakeDataConfCols + 3])]})

        if cols[surpassDataCols] is not None:                   # 名次
            config["surpassTarget"].append(int(cols[surpassDataCols]))

    result = json.dumps(config, indent=4, ensure_ascii=False)
    result = re.sub(r"\\\\n", r"\\n", result)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "grandPrix_config, end"


def getWorkBook(filename="newfish.xlsm"):
    '''
    获取工作sheet
    :return:
    '''
    configFile = os.path.split(os.path.realpath(__file__))[0] + '/%s' % filename
    wk = load_workbook(filename=configFile, read_only=True, data_only=True)
    # print wk.sheetnames, '1111111'
    return wk


def getOutPath(dirname, filename="0.json"):
    '''
    输出的文件
    :param dirname: 路径文件夹
    :param filename: 文件名
    :return:
    '''
    global ServerPath
    dirPath = os.path.split(os.path.realpath(__file__))[0] + ServerPath + '/%s/' % dirname
    filePath = dirPath + filename
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    return filePath


def process_single_config(idx, task_queue, cost_queue, err_queue, sp):
    '''
    处理单个配置文件
    :param idx: 进程编号1、2、3、4、5、6、7、8
    :param task_queue: 任务队列
    :param cost_queue:
    :param err_queue: 出错队列
    :param sp: 文件路径
    :return:
    '''
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
            print "=========== export ", confFunc.__name__, " failed ! ", e
            err_queue.put((confFunc.__name__ + "_" + str(arg), e))

# 配置列表
config_list = [
    # # (activity_config, None),
    (item_config, None),
    (item_config, 26312),
    (item_config, 26760),
    (item_config, 26882),
    (store_config, None),
    (store_config, 25598),
    (store_config, 25794),
    (store_config, 25840),
    (store_config, 26120),
    (store_config, 26121),
    (store_config, 26122),
    (store_config, 26312),
    (store_config, 26760),
    (store_config, 26882),
    # # (multi_lang_text, None),
    # (newbie7DaysGift_config, None),
    # (lottery_ticket_config, None),
    # (pass_card_config, None),
    # (skill_compen_config, None),
    # (grand_prize_pool_config, None),
    # # (piggy_bank_config, None),
    # (prizewheel_config, None),
    # (grandPrixPrizewheel_config, None),
    # # (time_limited_store_config, None),
    # (levelRewards_config, None),
    # (level_funds_config, None),
    # (level_funds_config, 25794),
    # (super_egg_config, None),
    # (updateVerRewards_config, None),
    (grandPrix_config, None),
    # (bigPrize_config, None),
    # (compAct_config, None),
    # # (checkin_config, None),
    (drop_config, None),
    (fish_config, None),
    (match_fish_config, None),
    (weapon_config, None),
    # (ulevel_config, None),
    # (skill_grade_config, None),
    # (skill_star_config, None),
    # # (main_quest_config, None),
    # # (daily_quest_config, None),
    (chest_config, None),               # 宝箱配置
    (chest_drop_config, None),          # 宝箱掉落配置
    # (cmptt_task_config, None),
    # (ncmptt_task_config, None),
    # (bonus_task_config, None),
    # (guide_task_config, None),
    # (probability_config, None),
    (dynamic_odds_config, None),
    # (lottery_pool_config, None),
    # # (gift_config, None),
    # # (gift_config, 25794),
    # # (gift_config, 25598),
    # # (gift_config, 26120),
    # # (gift_config, 26121),
    # # (gift_config, 26122),
    # (item_drop_config, None),
    (vip_config, None),
    (fixed_multiple_fish, None),
    # (call_multiple_fish, None),
    # (fishBonus_config, None),
    # (match_multiple_fish, None),
    # # (achievement_config, None),
    # # (honor_config, None),
    (weaponPowerRate_config, None),     # 加载武器威力加成配置
    (gunskin_config, None),             # 皮肤炮配置
    (gunskin_config, 26312),
    (gunskin_config, 26760),
    # (plyerBuffer_config, None),
    # (randomMultipleFish_config, None),
    # (gunLevel, None),
    # (tableTask, None),
    # (inviteTask_config, None),
    # (rechargePool_config, None),
    # # (share_config, None),
    # (fly_pig_config, None),
    # (starfish_roulette_config, None),
    # (surpass_target_config, None),
    # (special_item_config, None),
    # (robot_config, None),
    # (report_fish_cb_config, None),
    # # (treasure_config, None),
    # (statistic_prop_config, None),
    # (slot_machine_config, None),
    # (money_tree_config, None),
    # (canned_fish_config, None),
    # (credit_store_config, None),
    # (supply_box_config, None),
    # (festival_turntable_config, None),
    # (collect_item_config, None),
    # (abtest_config, None)
    # # (world_boss_config, None),
]


if __name__ == '__main__':
    TestConfPath = ""
    RealeaseConfPath = ""
    print "begin"
    t1 = int(time.time())
    ServerPath = '/../../../../../../xxfish_test/config37/game/44'          # 默认练习路径
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        ServerPath = '/../../../../../../xxfish_test/config37/game/44'
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
        conf_queue.put(conf)                    # 任务队列
    cost_queue = Queue()                        # 执行队列的时间
    err_queue = Queue()                         # 错误的队列
    isUseMultiProcess = len(sys.argv) > 2 and sys.argv[2] == "-m" and cpu_count() > 1
    if isUseMultiProcess:
        freeze_support()
        processList = [Process(target=process_single_config, args=(i + 1, conf_queue, cost_queue, err_queue, ServerPath)) for i in range(cpu_count())]
        for p in processList:
            p.start()                           # 开始时间
        for p in processList:
            p.join()
    else:
        process_single_config(0, conf_queue, cost_queue, err_queue, ServerPath)

    t2 = int(time.time())
    print "----- load config successfully"
    print "----- out full path: %s" % os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + ServerPath)
    if isUseMultiProcess:
        print "----- %d cpu, process %d files, export json cost %d s" % (cpu_count(), len(config_list), t2 - t1)
    else:
        print "----- process %d files, export json cost %d s" % (len(config_list), t2 - t1)

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
        print "json format: windows->unix, start"
        import os
        if TestConfPath:
            os.system(r".\jsonDos2Unix.bat %s" % TestConfPath)
        if RealeaseConfPath:
            os.system(r".\jsonDos2Unix.bat %s" % RealeaseConfPath)
        print "json format: windows->unix, end"