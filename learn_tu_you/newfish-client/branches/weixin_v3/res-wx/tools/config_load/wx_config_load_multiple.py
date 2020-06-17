#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
千炮玩法的配置
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
    outPath = getOutPath("superbossExchange")
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
    outPath = getOutPath("superbossMinigame")
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
            one["maxTimes"] = int(cols[2])
            one["currencyList"] = json.loads(cols[3])
        if cols[5]:
            key = "%s_%d" % (str(cols[5]), int(cols[6]))
            config["game"].setdefault(key, [])
            config["game"][key].append({
                "costs": json.loads(cols[8]),
                "rewards": json.loads(cols[9]),
                "des": str(cols[7]) if cols[7] else "",
                "mode": int(cols[6])
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
    outPath = getOutPath("superbossCommon")
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
            config[str(cols[0])] = one
            one["tabs"] = json.loads(cols[1])       # 房间的游戏玩法
            one["poolPct"] = float(cols[2])         # 奖池占房间奖池比例
            one["nextDayPoolPct"] = float(cols[3])  # 第二天奖池占房间奖池比例
            one["mgType"] = str(cols[4])            # 类型
            one["rule"] = json.loads(cols[5])       # 规则

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
    '''
    千炮玩法渔场的鱼
    :return:
    '''
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
        print cols
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("fishId %d repeat" % int(cols[0]))
        config[str(cols[3])] = one
        one["name"] = unicode(cols[1])
        one["type"] = int(cols[4])
        if is_number(cols[5]):
            one["itemId"] = int(cols[5])
        else:
            one["itemId"] = json.loads(cols[5])
        one["score"] = int(cols[6])
        one["minCount"] = int(cols[7])
        one["maxCount"] = int(cols[8])
        one["probb1"] = float("%.1f" % cols[9])
        one["probb2"] = float("%.1f" % cols[10])
        one["HP"] = int(cols[11])
        one["value"] = int(cols[12])
        if cols[14]:
            one["weaponId"] = int(cols[14])
        one["prizeWheelValue"] = float(cols[15])
        one["triggerRate"] = int(cols[16])
        one["catchValue"] = float(cols[17])
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


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
                continue
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
    """千炮升级"""
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
            upgradeItems[cols[1]] = cols[2]
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
        if cols[_tmpIdx + 13]:
            one["unlockMultiple"] = int(cols[_tmpIdx + 13])
        if cols[_tmpIdx + 14] is not None:
            one["levelAddition"] = float(cols[_tmpIdx + 14])
        one["levelValue"] = int(cols[_tmpIdx + 15])
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


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

    result = json.dumps(weaponConfig, indent=4)

    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


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
    (superboss_exchange_config, None),
    (superboss_minigame_config, None),
    (superboss_common_config, None),
    (fish_config, None),
    (skill_grade_config, None),
    (skill_star_config, None),
    (gunLevel, None),
    # (gunskin_config, None),
    # (superboss_power_config, None),
    (weapon_config, None),
    # (level_funds_config, None),
    # (level_funds_config, 25794)
]


if __name__ == '__main__':
    TestConfPath = ""
    RealeaseConfPath = ""
    print "begin"
    t1 = int(time.time())
    ServerPath = '/../../../../../../xxfish_test/config37/game/44'  # 默认练习路径
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
        conf_queue.put(conf)  # 任务队列
    cost_queue = Queue()  # 执行队列的时间
    err_queue = Queue()  # 错误的队列
    isUseMultiProcess = len(sys.argv) > 2 and sys.argv[2] == "-m" and cpu_count() > 1
    if isUseMultiProcess:
        freeze_support()
        processList = [
            Process(target=process_single_config, args=(i + 1, conf_queue, cost_queue, err_queue, ServerPath)) for i in
            range(cpu_count())]
        for p in processList:
            p.start()  # 开始时间
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