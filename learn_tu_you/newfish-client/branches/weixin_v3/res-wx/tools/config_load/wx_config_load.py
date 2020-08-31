#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Created by lichen on 17/2/8.
执行该脚本，将会生成newfish.xlsm对应的json配置文件
"""

import time
from openpyxl import load_workbook
import os, sys, json, copy
import collections
import re
import csv
import traceback
from multiprocessing import Queue, Process, cpu_count, freeze_support

ServerPath = ""
ClientIdMap = None


def fish_config():
    """
    鱼的配置
    :return:
    """
    print "fish_config, start"
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
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("fishId %d repeat" % int(cols[0]))
        config[str(cols[3])] = one          # {11001: {}}
        one["fishType"] = int(cols[3])
        one["name"] = unicode(cols[1])      # 鱼的名字
        one["type"] = int(cols[4])          # 鱼的类别
        if is_number(cols[5]):
            one["itemId"] = int(cols[5])    # 捕鱼掉道具 数字
        else:
            one["itemId"] = json.loads(cols[5])     # [10000,10002]
        one["score"] = int(cols[6])                 # 分值
        one["probb1"] = float("%.1f" % cols[7])     # 无HP时概率基数
        one["probb2"] = float("%.1f" % cols[8])
        one["HP"] = int(cols[9])                   # 生命
        one["value"] = int(cols[10])                # 实际价值
        if cols[12]:
            one["weaponId"] = int(cols[12])         # 武器Id
        one["prizeWheelValue"] = float(cols[13])    # 积攒价值
        one["triggerRate"] = int(cols[14])          # 触发几率(10000)
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "fish_config, end"


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


def weapon_config():
    """武器配置"""
    print "weapon_config, start"
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
    print "weapon_config, end"


def skill_grade_config():
    print "skill_grade_config, start"
    outPath = getOutPath("skillGrade")
    ws = getWorkBook().get_sheet_by_name("SkillGrade")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    skillId = collections.OrderedDict()
    for row in ws.rows:
        i = i+1
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
        one["cost"] = int(cols[3])
        one["power"] = int(cols[4])
        one["HP"] = int(cols[5])      
        one["impale"] = int(cols[6])
        one["clip"] = int(cols[7])
        one["interval"] = float(cols[8])
        one["duration"] = float(cols[9])
        one["coolDown"] = int(cols[10])
        one["weaponId"] = int(cols[11])
        one["double"] = json.loads(str(cols[12]))
        one["isReturn"] = int(cols[13])
    result = json.dumps(config, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "skill_grade_config, end"


def skill_star_config():
    print "skill_star_config, start"
    outPath = getOutPath("skillStar")
    ws = getWorkBook().get_sheet_by_name("SkillStar")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    skillId = collections.OrderedDict()
    for row in ws.rows:
        i = i+1
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
            ability["ability"] = int(cols[x])
            ability["valueType"] = int(cols[x+1])
            ability["value"] = int(cols[x+2])
            abilities.append(ability)
    result = json.dumps(config, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "skill_star_config, end"


def main_quest_config():
    print "main_quest_config, start"
    outPath = getOutPath("mainQuest")
    ws = getWorkBook().get_sheet_by_name("MainQuest")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    tasks = collections.OrderedDict()
    sections = collections.OrderedDict()
    for row in ws.rows:
        i = i + 1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        task = collections.OrderedDict()
        tasks[int(cols[0])] = task
        task["taskId"] = int(cols[0])
        task["title"] = str(cols[1])
        task["desc"] = unicode(cols[2])
        task["num"] = int(cols[3])
        task["normalRewards"] = json.loads(cols[4])
        task["chestRewards"] = json.loads(cols[5])
        task["type"] = int(cols[6])

        if cols[8]:
            section = collections.OrderedDict()
            sections[int(cols[8])] = section
            section["sectionId"] = int(cols[8])
            section["sortId"] = int(cols[9])
            section["taskIds"] = json.loads(cols[10])
            section["rewards"] = json.loads(cols[11])
            section["honorId"] = int(cols[12])
            section["display"] = int(cols[13])
    config["tasks"] = tasks
    config["sections"] = sections
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "main_quest_config, end"


def ulevel_config():
    print "ulevel_config, start"
    outPath = getOutPath("ulevel")
    ws = getWorkBook().get_sheet_by_name("Level")
    uLevelConfig = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        oneLevel = collections.OrderedDict()
        uLevelConfig[int(cols[0])] = oneLevel
        oneLevel["500"] = cols[1]
        oneLevel["2000"] = cols[2]
        oneLevel["5000"] = cols[3]
    result = json.dumps(uLevelConfig, indent=4)
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "ulevel_config, end"

    
def cmptt_task_config():
    print "cmptt_task_config, start"
    outPath = getOutPath("cmpttTask")
    ws = getWorkBook().get_sheet_by_name("Cmptt")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("taskId %d repeat" % int(cols[0]))
        if cols[0] == None:
            break
        config[str(cols[0])] = one
        one["taskId"] = cols[0]
        one["fishPool"] = cols[1]
        assert int(cols[2]) in [1, 2]
        one["taskType"] = cols[2]
        one["desc"] = unicode(cols[3] or "")
        one["timeLong"] = cols[4]
        one["chestReward"] = cols[11].split("|")
        # one["coinReward"] = cols[10]
        # one["pearlReward"] = cols[11]
        # one["couponReward"] = cols[12]
        one["readySeconds"] = 10
        targets = collections.OrderedDict()
        one["targets"] = targets
        if cols[5]:
            targets["target1"] = cols[5]
        if cols[6]:
            targets["number1"] = cols[6]
        if cols[5] and cols[7]:
            targets["inter1"] = cols[7]
        if cols[8]:
            targets["target2"] = cols[8]
        if cols[9]:
            targets["number2"] = cols[9]
        if cols[8] and cols[10]:
            targets["inter2"] = cols[10]
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "cmptt_task_config, end"


def ncmptt_task_config():
    print "ncmptt_task_config, start"
    outPath = getOutPath("ncmpttTask")
    ws = getWorkBook().get_sheet_by_name("Ncmptt")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("taskId %d repeat" % int(cols[0]))
        config[str(cols[0])] = one
        one["taskId"] = cols[0]
        one["fishPool"] = cols[1]
        assert int(cols[2]) in [1, 2, 3, 4, 5]
        one["taskType"] = cols[2]
        one["desc"] = unicode(cols[3] or "")
        one["timeLong"] = cols[4]
        one["chestReward"] = cols[11]
        # one["coinReward"] = cols[10]
        one["readySeconds"] = 3
        targets = collections.OrderedDict()
        one["targets"] = targets
        if cols[5]:
            targets["target1"] = cols[5]
        if cols[6]:
            targets["number1"] = cols[6]
        if cols[5] and cols[7]:
            targets["inter1"] = cols[7]
        if cols[8]:
            targets["target2"] = cols[8]
        if cols[9]:
            targets["number2"] = cols[9]
        if cols[8] and cols[10]:
            targets["inter2"] = cols[10]
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "ncmptt_task_config, end"


def bonus_task_config():
    print "bonus_task_config, start"
    outPath = getOutPath("bonusTask")
    ws = getWorkBook().get_sheet_by_name("Bonus")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        if len(cols) < 7 or cols[0] is None:
            continue
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("taskId %d repeat" % int(cols[0]))
        config[str(cols[0])] = one
        one["taskId"] = cols[0]
        one["fishPool"] = cols[1]
        assert int(cols[2]) in [1, 2, 4]
        one["taskType"] = cols[2]
        one["desc"] = unicode(cols[3] or "")
        one["timeLong"] = cols[4]
        # one["firstChestReward"] = cols[7]
        # one["secondChestReward"] = cols[8]
        one["readySeconds"] = 10
        targets = collections.OrderedDict()
        one["targets"] = targets
        if cols[5]:
            targets["target1"] = cols[5]
        if cols[5] and cols[6]:
            targets["inter1"] = cols[6]
        if cols[7]:
            targets["target2"] = cols[7]
        if cols[7] and cols[8]:
            targets["inter2"] = cols[8]
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close() 
    print "bonus_task_config, end"


def guide_task_config():
    print "guide_task_config, start"
    outPath = getOutPath("guideTask")
    ws = getWorkBook().get_sheet_by_name("Guide")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("taskId %d repeat" % int(cols[0]))
        config[str(cols[0])] = one
        one["taskId"] = cols[0]
        assert int(cols[1]) in [1, 2, 3, 4, 5, 6]
        one["taskType"] = cols[1]
        one["coinReward"] = cols[7]
        one["pearlReward"] = cols[8]
        one["skillReward"] = cols[9]
        one["chestReward"] = cols[10]
        one["steps"] = eval(cols[11])
        targets = collections.OrderedDict()
        one["targets"] = targets
        if cols[3]:
            targets["target1"] = cols[3]
        if cols[4]:
            targets["number1"] = cols[4]
        if cols[5]:
            targets["target2"] = cols[5]
        if cols[6]:
            targets["number2"] = cols[6]
    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "guide_task_config, end"


def daily_quest_config():
    print "daily_quest_config, start"
    outPath = getOutPath("dailyQuest")
    ws = getWorkBook().get_sheet_by_name("DailyQuest")
    conf = collections.OrderedDict()
    conf["questData"] = collections.OrderedDict()
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
        one = collections.OrderedDict()
        conf["questData"][cols[0]] = one
        one["taskId"] = cols[0]
        one["taskType"] = cols[1]
        one["des"] = unicode(cols[2] or "")
        one["lv"] = cols[3]
        one["activeLv"] = cols[4]
        one["unlockUserLv"] = cols[5]
        one["taskLevel"] = cols[6]
        one["groupId"] = cols[7]
        one["targetsNum"] = cols[8]
        one["fishPool"] = json.loads(cols[9])
        one["fpMultiple"] = int(cols[10])
        showDay = cols[11]
        if isinstance(showDay, unicode):
            showDay = showDay.split("|")
            showDay = [int(x) for x in showDay]
        else:
            showDay = [showDay]
        one["showDay"] = showDay
        if cols[12]:
            one["rewards"] = json.loads(cols[12])

        if cols[14]:
            conf["questOrder"] = json.loads(cols[14])

    result = json.dumps(conf, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    daily_quest_reward_config()
    print "daily_quest_config, end"

def daily_quest_reward_config():
    outPath = getOutPath("dailyQuestReward")
    ws = getWorkBook().get_sheet_by_name("DailyQuestReward")
    conf = collections.OrderedDict()
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
        conf[cols[0]] = collections.OrderedDict()
        for k in range(1, len(cols), 5):
            one = collections.OrderedDict()
            conf[cols[0]][cols[k]] = one
            one["finishedStar"] = cols[k]
            one["type"] = str(cols[k + 1])
            one["rewards"] = [{"itemId": cols[k + 3], "count": 1, "name": cols[k + 2], "reward": json.loads(cols[k + 4])}]

    result = json.dumps(conf, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
   

def getCouponFish(ws):
    couponFish = collections.OrderedDict()
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
        couponFish[str(cols[0])] = one
        one["fishPool"] = int(cols[0])
        one["totalBullet"] = int(cols[1])
        one["minSecond"] = int(cols[2])
        one["maxSecond"] = int(cols[3])
        one["couponRange"] = json.loads(cols[4])
        fishes = []
        probb = 0
        for x in xrange(5, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["fishType"] = int(cols[x])
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            fishes.append(fish)
        one["fishes"] = fishes
    return couponFish


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
            itemProbb = int(cols[x + 1])
            itemHighProbb = int(cols[x + 2])
            itemRechargeProbb = int(cols[x + 3])
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


# def getHitBoss(ws):
    # hitBoss = []
    # startRowNum = 4
    # i = 0
    # for row in ws.rows:
    #     i = i + 1
    #     if i < startRowNum:
    #         continue
    #     cols = []
    #     for cell in row:
    #         cols.append(cell.value)
    #     if not cols[0]: 
    #         continue
    #     probb = 0 
    #     for x in xrange(0, len(cols), 2):
    #         if not cols[x]:
    #             continue
    #         one = collections.OrderedDict()
    #         oneProbb = int(cols[x])
    #         one["probb"] = [probb + 1, probb + oneProbb]
    #         one["multiple"] = float(cols[x + 1])
    #         probb += oneProbb
    #         hitBoss.append(one)
    # return hitBoss


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


def getChestFish(ws):
    chestFish = collections.OrderedDict()
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
        chestFish[str(cols[0])] = one
        one["maxCoin"] = cols[1]
        one["minCoin"] = cols[2]
        one["probbs"] = []
        probb = 0
        for x in xrange(3, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["score"] = int(cols[x])
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            one["probbs"].append(fish)
    return chestFish


def getActivityFish(ws):
    activityFish = collections.OrderedDict()
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
        activityFish[str(cols[0])] = one
        one["fishPool"] = int(cols[0])
        one["totalBullet"] = int(cols[1])
        one["minSecond"] = int(cols[2])
        one["maxSecond"] = int(cols[3])
        fishes = []
        probb = 0
        for x in xrange(4, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["fishType"] = int(cols[x])
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            fishes.append(fish)
        one["fishes"] = fishes
    return activityFish


def getShareFish(ws):
    shareFish = collections.OrderedDict()
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
        shareFish[str(cols[0])] = one
        one["fishPool"] = int(cols[0])
        one["totalBullet"] = int(cols[1])
        one["minSecond"] = int(cols[2])
        one["maxSecond"] = int(cols[3])
        fishes = []
        probb = 0
        for x in xrange(4, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["fishType"] = int(cols[x])
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            fishes.append(fish)
        one["fishes"] = fishes
    return shareFish


def getAutofillFish(ws):
    autofillFish = collections.OrderedDict()
    startRowNum = 4
    i = 0
    isFindBlank = False
    for row in ws.rows:
        i = i + 1
        cols = []
        if not isFindBlank and i >= startRowNum:
            for cell in row:
                cols.append(cell.value)
            if not cols[0]:
                isFindBlank = True
                continue
            one = collections.OrderedDict()
            autofillFish[str(cols[0])] = []
            autofillFish[str(cols[0])].append(one)
            one["supplyInterval"] = int(cols[1])
            one["minCount"] = int(cols[2])
            one["maxCount"] = int(cols[3])
            one["minInterval"] = int(cols[4])
            one["maxInterval"] = int(cols[5])
            one["fish"] = []
            probb = 0
            for x in xrange(6, len(cols), 2):
                if not cols[x]:
                    continue
                fish = {}
                fish["fishType"] = int(cols[x])
                itemProbb = int(cols[x + 1])
                fish["probb"] = [probb + 1, probb + itemProbb]
                probb += itemProbb
                one["fish"].append(fish)

        if isFindBlank:
            for cell in row:
                cols.append(cell.value)
            if not cols[0]:
                continue
            try:
                supplyInterval = int(cols[1])
            except:
                continue
            for x in xrange(2, len(cols), 5):
                if not cols[x]:
                    continue
                one = collections.OrderedDict()
                fish = {}
                fish["fishType"] = int(cols[x])
                fish["probb"] = [0, 10000]
                one["fish"] = []
                one["fish"].append(fish)
                one["minCount"] = int(cols[x + 1])
                one["maxCount"] = int(cols[x + 2])
                one["minInterval"] = int(cols[x + 3])
                one["maxInterval"] = int(cols[x + 4])
                one["supplyInterval"] = supplyInterval
                autofillFish[str(cols[0])].append(one)
    return autofillFish


def getHippoFish(ws):
    hippoFish = collections.OrderedDict()
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
        one = {}
        hippoFish[str(cols[0])] = one
        one["fishType"] = int(cols[1])
        one["minTime"] = int(cols[2])
        one["maxTime"] = int(cols[3])
        one["rewards"] = []
        probb = 0
        for x in xrange(4, len(cols), 3):
            if not cols[x] or not cols[x + 1] or not cols[x + 2]:
                continue
            itemInfo = {}
            itemInfo["name"] = int(cols[x])
            itemInfo["count"] = int(cols[x + 1])
            itemProbb = int(cols[x + 2])
            itemInfo["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            one["rewards"].append(itemInfo)
    return hippoFish


def getUserCouponFish(ws):
    userCouponFish = collections.OrderedDict()
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
        userCouponFish.setdefault(str(cols[0]), []).append(one)
        # userCouponFish[str(cols[0])] = one
        one["fishPool"] = int(cols[0])
        one["limitCount"] = int(cols[1])
        one["sections"] = json.loads(cols[2])
        one["totalBullet"] = int(cols[3])
        one["minSecond"] = int(cols[4])
        one["maxSecond"] = int(cols[5])
        fishes = []
        probb = 0
        for x in xrange(6, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                continue
            fish = {}
            fish["fishType"] = int(cols[x])
            itemProbb = int(cols[x + 1])
            fish["probb"] = [probb + 1, probb + itemProbb] 
            probb += itemProbb
            fishes.append(fish)
        one["fishes"] = fishes
    return userCouponFish

def probability_config():
    outPath = getOutPath("probability")
    wb = getWorkBook()
    config = collections.OrderedDict()
    couponFish = getCouponFish(wb.get_sheet_by_name("CouponFish"))
    multipleFish = getMultipleFish(wb.get_sheet_by_name("MultipleFish"))
    # hitBoss = getHitBoss(wb.get_sheet_by_name("HitBoss"))
    bossFish = getBossFish(wb.get_sheet_by_name("BossFish"))
    chestFish = getChestFish(wb.get_sheet_by_name("ChestFish"))
    activityFish = getActivityFish(wb.get_sheet_by_name("ActivityFish"))
    shareFish = getShareFish(wb.get_sheet_by_name("ShareFish"))
    autofillFish = getAutofillFish(wb.get_sheet_by_name("AutofillFish"))
    hippoFish = getHippoFish(wb.get_sheet_by_name("HippoFish"))
    userCouponFish = getUserCouponFish(wb.get_sheet_by_name("UserCouponFish"))

    config["couponFish"] = couponFish
    config["multipleFish"] = multipleFish
    config["bossFish"] = bossFish
    # config["hitBoss"] = hitBoss
    config["chestFish"] = chestFish
    config["activityFish"] = activityFish
    config["shareFish"] = shareFish
    config["autofillFish"] = autofillFish
    config["hippoFish"] = hippoFish
    config["userCouponFish"] = userCouponFish
    result = json.dumps(config, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  


def terror_fish():
    """特殊鱼出现的概率和间隔"""
    outPath = getOutPath("terrorFish")
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
        terrorFish[str(cols[0])] = one
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
    config["terrorFish"] = terrorFish
    result = json.dumps(config, indent=4)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


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


def gift_config(clientId=0):
    """
    礼包配置
    """
    sn = "Gift" if clientId == 0 else "Gift" + "_" + str(clientId)
    fn = "0.json" if clientId == 0 else str(clientId) + ".json"
    outPath = getOutPath("gift", fn)
    ws = getWorkBook().get_sheet_by_name(sn)
    config = collections.OrderedDict()
    config["gift"] = collections.OrderedDict()
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
            if i != startRowNum:
                break
            continue
        one = collections.OrderedDict()
        if str(cols[0]) in config["gift"]:
            raise KeyError("giftId %d repeat" % int(cols[0]))
        config["gift"][str(cols[0])] = one
        one["giftId"] = int(cols[0])
        one["giftName"] = unicode(cols[1])
        one["giftType"] = int(cols[2])
        one["productId"] = cols[3]
        one["fishPool"] = int(cols[4])
        one["lifetime"] = int(cols[5])
        one["minLevelLimit"] = int(cols[6])
        one["maxLevelLimit"] = int(cols[7])
        one["coinLimit"] = int(cols[8])
        one["buyType"] = cols[9]
        one["price"] = int(cols[10])
        one["discountPrice"] = int(cols[11])
        one["price_direct"] = int(cols[12])
        one["price_diamond"] = int(cols[13])
        one["otherBuyType"] = json.loads(cols[14])
        one["vip"] = int(cols[15])
        one["giftLimit"] = int(cols[16])
        one["showAfterReload"] = int(cols[17])
        one["showAfterTimes"] = int(cols[18])
        one["roomId"] = json.loads(cols[19])
        one["recordKey"] = str(cols[20])
        one["loopTimes"] = int(cols[21])
        one["appearTimes"] = json.loads(cols[22])
        # 月卡专用
        if one["giftType"] == 4:
            one["monthCard"] = json.loads(cols[23])
        one["firstBuyRewards"] = json.loads(cols[24])
        one["getAfterBuy"] = json.loads(cols[25])
        one["expireTime"] = int(cols[26])
        one["popupLevel"] = int(cols[27])
        one["items"] = []
        for x in xrange(28, len(cols), 5):
            if cols[x]:
                item = {}
                item["type"] = cols[x]
                item["name"] = unicode(cols[x + 1]) if cols[x + 1] else ""
                item["desc"] = unicode(cols[x + 2]) if cols[x + 2] else ""
                item["itemId"] = cols[x + 3]
                item["count"] = cols[x + 4]
                one["items"].append(item)

    # 每日礼包配置
    print "daily_gift_config, start"
    sn = "DailyGift" if clientId == 0 else "DailyGift" + "_" + str(clientId)
    ws = getWorkBook().get_sheet_by_name(sn)
    config["dailyGift"] = collections.OrderedDict()
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
            config["dailyGift"][int(cols[0])] = one
            one["giftId"] = int(cols[0])
            one["giftName"] = unicode(cols[1])
            one["productId"] = cols[2]
            one["vipRange"] = json.loads(cols[3])
            one["buyType"] = cols[4]
            one["price"] = int(cols[5])
            one["price_direct"] = int(cols[6])
            one["price_diamond"] = int(cols[7])
            one["otherBuyType"] = json.loads(cols[8])
            one["giftInfo"] = []
            for x in range(9, len(cols), 2):
                if cols[x] is None:
                    continue
                item = collections.OrderedDict()
                item["day_idx"] = int(cols[x])
                item["items"] = json.loads(cols[x + 1])
                one["giftInfo"].append(item)
    print "daily_gift_config, end"

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def lottery_pool_config():
    pass


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


def achievement_config_old():
    outPath = getOutPath("achievement")
    ws = getWorkBook().get_sheet_by_name("AchievementTask")
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
        if cols[6] not in config:
            config[cols[6]] = []
        one = collections.OrderedDict()
        one["taskId"] = cols[0]
        one["desc"] = cols[1]
        one["target"] = json.loads(cols[2])
        one["type"] = cols[3]
        one["isMax"] = cols[4]
        one["repeat"] = cols[5]
        one["groupId"] = cols[6]
        one["honorId"] = cols[7]
        one["norReward"] = _getRewardInfo(cols[8])
        one["chestReward"] = _getRewardInfo(cols[9])
        config[cols[6]].append(one)
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()



def weaponPowerRate_config():
    outPath = getOutPath("weaponPowerRate")
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


def weapon_stage_count_config():
    """
    武器的爆炸次数
    """
    print "weapon_stage_count_config, start"
    outPath = getOutPath("weaponStageCount")
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
        i = i+1
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


def achievement_config_old():
    outPath = getOutPath("achievement")
    ws = getWorkBook().get_sheet_by_name("AchievementTask")
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
        if cols[0] != 0 and not cols[0]: 
            continue
        if cols[6] not in config:
            config[cols[6]] = []
        one = collections.OrderedDict()
        one["taskId"] = cols[0]
        one["desc"] = cols[1]
        one["target"] = json.loads(cols[2])
        one["type"] = cols[3]
        one["isMax"] = cols[4]
        one["repeat"] = cols[5]
        one["groupId"] = cols[6]
        one["honorId"] = cols[7]
        one["norReward"] = _getRewardInfo(cols[8])
        one["chestReward"] = _getRewardInfo(cols[9])
        config[cols[6]].append(one)
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()


def plyerBuffer_config():
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


def randomMultipleFish_config():
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


def guideFollowedTask_config():
    outPath = getOutPath("GuideFollowedTask")
    ws = getWorkBook().get_sheet_by_name("GuideFollowedTask")
    config = []
    startRowNum = 4
    i = 0 
    for row in ws.rows:
        i = i+1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if cols[0] !=0 and not cols[0]: 
            continue
        one = collections.OrderedDict()
        one["taskId"] = int(cols[0])
        one["desc"] = cols[1]
        one["type"] = int(cols[2])
        one["repeat"] = int(cols[3])
        one["target"] = json.loads(cols[4])
        one["reward"] = _getRewardInfo(cols[5])
        config.append(one)
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()  


def _getRewardInfo(reward):
    """获取奖励信息"""
    reward = json.loads(reward)
    rewardInfo = []
    for x in xrange(0, len(reward), 2):
        reward_ = {"name": reward[x], "count": reward[x+1]}
        rewardInfo.append(reward_)
    return rewardInfo


def gunLevel():
    """火炮等级配置"""
    outPath = getOutPath("gunLevel")
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
        if cols[_tmpIdx + 13] is not None:
            one["levelAddition"] = float(cols[_tmpIdx + 13])
        one["levelValue"] = int(cols[_tmpIdx + 14])
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()


def tableTask():
    outPath = getOutPath("tableTask")
    ws = getWorkBook().get_sheet_by_name("TableTask")
    wsRoomTask = getWorkBook().get_sheet_by_name("RoomTask")
    config = collections.OrderedDict()
    config["tasks"] = collections.OrderedDict()
    config["roomTask"] = collections.OrderedDict()
    startRowNum = 2
    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if cols[0] !=0 and not cols[0]: 
            continue
        one = collections.OrderedDict()
        config["tasks"][str(cols[0])] = one
        one["taskId"] = int(cols[0])
        one["type"] = int(cols[1])
        one["desc"] = cols[2]
        one["target"] = int(cols[3])
        one["targetNum"] = int(cols[4])
        one["timeLong"] = int(cols[5])
        one["failTime"] = int(cols[6])
        one["rewards"] = []
        for m in range(7, 9, 3):
            if not cols[m]:
                break
            reward = {"name": int(cols[m]), "count": int(cols[m+1])}
            one["rewards"].append(reward)
        one["suggestTarget"] = int(cols[10])
        one["waitTime"] = int(cols[11])
    i = 0
    for row in wsRoomTask.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if cols[0] !=0 and not cols[0]: 
            continue
        if not cols[1] or cols[1] == "":
            continue
        one = collections.OrderedDict()
        config["roomTask"][str(cols[0])] = one
        one["mainTask"] = json.loads(cols[1])
        one["branchTask"] = json.loads(cols[2])
        one["randomTask"] = json.loads(cols[3])
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()  


def inviteTask_config():
    outPath = getOutPath("inviteTask")
    ws = getWorkBook().get_sheet_by_name("InviteTask")
    config = collections.OrderedDict()
    config["inviteTask"] = collections.OrderedDict()
    config["recallTask"] = collections.OrderedDict()
    startRowNum = 3
    i = 0 
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if cols[0] !=0 and not cols[0]: 
            continue
        one = collections.OrderedDict()
        if int(cols[1]) == 1:
            config["inviteTask"][str(cols[0])] = one
        else:
            config["recallTask"][str(cols[0])] = one
         
        one["Id"] = int(cols[0])
        one["type"] = int(cols[1])
        one["target"] = int(cols[2])
        one["rewards"] = []
        for m in range(3, len(cols), 2):
            if not cols[m]:
                break
            reward = {"name": int(cols[m]), "count": int(cols[m+1])}
            one["rewards"].append(reward)
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()


def rechargePool_config():
    outPath = getOutPath("rechargePool")
    ws = getWorkBook().get_sheet_by_name("RechargePool")
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
        config[str(cols[0])] = one
        one["productId"] = str(cols[0])
        bonuses = []
        probb = 0
        for x in range(1, len(cols), 2):
            if not cols[x] or not cols[x + 1]:
                break
            bonus = collections.OrderedDict()
            bonus["bonus"] = int(cols[x])
            bonus["probb"] = [probb + 1, probb + int(cols[x + 1])]
            probb += int(cols[x + 1])
            bonuses.append(bonus)
        one["bonuses"] = bonuses
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()


def share_config():
    outPath = getOutPath("share")
    ws = getWorkBook().get_sheet_by_name("Share")
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
        if cols[0] !=0 and not cols[0]: 
            continue
        one = collections.OrderedDict()
        config[str(cols[0])] = one
        one["shareId"] = int(cols[0])
        one["typeId"] = str(cols[1])
        one["title"] = unicode(cols[2] or "")
        one["desc1"] = unicode(cols[3] or "")
        one["desc2"] = unicode(cols[4] or "")
        one["vipLimit"] = int(cols[6])
        one["levelLimit"] = int(cols[7])
        one["versionLimit"] = json.loads(cols[8])
        one["timeLimit"] = json.loads(cols[9])
        one["locationLimit"] = [unicode(x) for x in cols[10].split(",")] if cols[10] else []
        one["popCountLimit"] = int(cols[11])
        one["finishCountLimit"] = int(cols[12])
        one["expiresType"] = int(cols[13])
        one["finishType"] = int(cols[14])
        one["groupType"] = int(cols[15])
        one["modes"] = json.loads(cols[16])
        one["rewards1"] = json.loads(cols[17])
        one["rewards2"] = json.loads(cols[18])
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()


def fly_pig_config():
    outPath = getOutPath("flyPigReward")
    ws = getWorkBook().get_sheet_by_name("FlyPigReward")
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
            break
        probb = 0
        items = []
        config[str(cols[0])] = items
        for x in range(1, len(cols), 6):
            if not cols[x] or not cols[x + 1]:
                continue
            itemDict = collections.OrderedDict()
            itemDict["probb"] = [probb + 1, probb + int(cols[x])]
            itemDict["kindId"] = int(cols[x + 1])
            itemDict["displayCount"] = int(cols[x + 2])
            itemDict["shareMultiple"] = int(cols[x + 3])
            itemDict["advertMultiple"] = int(cols[x + 4])
            itemDict["saleCoin"] = int(cols[x + 5])
            items.append(itemDict)
            probb += int(cols[x])
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()


def starfish_roulette_config():
    """
    海星轮盘配置
    """
    print "starfish_roulette_config, start"
    outPath = getOutPath("starfishRoulette")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("StarfishTurntable")
    config = collections.OrderedDict()

    config["starfishRoulette"] = []
    config["priceInfo"] = {}
    config["rouletteLevel"] = []
    config["unlockLevel"] = 0
    config["rule"] = ""

    # 轮盘配置数据范围
    # rouletteStartColIdx = 1
    rouletteEndColIdx = 7

    # 价格配置数据范围
    priceStartColIdx = 8
    priceEndColIdx = 13

    # 轮盘等级配置数据范围
    levelStartColIdx = 15
    levelEndColIdx = 17

    # 轮盘解锁等级
    unlockLevelColIdx = 19

    ruleIdx = 21

    startRowNum = 4
    i = 0
    lastLevelInfo = {"level": 0, "exp": 0, "count": 0}
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0]:
            one = collections.OrderedDict()
            config["starfishRoulette"].append(one)
            one["Id"] = int(cols[0])
            one["starweight"] = int(cols[1])
            one["ticketweight"] = int(cols[2])
            one["rewards"] = []
            for x in xrange(3, rouletteEndColIdx, 4):
                item = {}
                item["name"] = int(cols[x + 0])
                item["count"] = int(cols[x + 1])
                item["rare"] = int(cols[x + 2])
                item["des"] = str(cols[x + 3])
                one["rewards"].append(item)

        if cols[priceStartColIdx]:
            priceCount = int(cols[priceStartColIdx])
            itemId = int(cols[priceStartColIdx + 1])
            if itemId:
                priceIdx = 0
                itemDict = {}
                for idx in xrange(priceStartColIdx + 2, priceEndColIdx, 2):
                    if priceIdx >= priceCount:
                        break
                    priceIdx = priceIdx + 1
                    item = {}
                    playTimes = int(cols[idx + 0])
                    item["name"] = int(itemId)
                    item["count"] = int(cols[idx + 1])
                    itemDict[playTimes] = item
                config["priceInfo"][itemId] = itemDict

        if cols[levelStartColIdx]:
            level = int(cols[levelStartColIdx])
            exp = int(cols[levelStartColIdx + 1])
            count = int(cols[levelStartColIdx + 2])
            if len(config["rouletteLevel"]) == 0:
                config["rouletteLevel"].append({"level": 0, "exp": 0, "count": 0})

            lastLevel = lastLevelInfo["level"]
            if level - lastLevel > 1:
                for idx in range(level - lastLevel - 1):
                    item = copy.deepcopy(lastLevelInfo)
                    item["level"] = lastLevel + idx + 1
                    config["rouletteLevel"].append(item)

            lastLevelInfo["level"] = level
            lastLevelInfo["exp"] = exp
            lastLevelInfo["count"] = count
            levelItem = copy.deepcopy(lastLevelInfo)
            config["rouletteLevel"].append(levelItem)

        if cols[unlockLevelColIdx]:
            config["unlockLevel"] = int(cols[unlockLevelColIdx])

        if cols[ruleIdx]:
            config["rule"] = str(cols[ruleIdx])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "starfish_roulette_config, end"


def surpass_target_config():
    """
    比赛超越目标配置
    """
    print "surpass_target_config, start"
    outPath = getOutPath("surpassTarget")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("SurpassTarget")
    config = []

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
            rank = int(cols[0])
            config.append(rank)

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "surpass_target_config, end"


def special_item_config():
    """
    特殊物品配置
    """
    print "special_item_config, start"
    outPath = getOutPath("specialItem")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("SpecialItem")
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

        if cols[0]:
            one = collections.OrderedDict()
            config[int(cols[0])] = one
            one["itemId"] = int(cols[0])
            one["incrPearlDropRate"] = cols[1]
            one["incrCrystalDropRate"] = cols[2]

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "special_item_config, end"


def report_fish_cb_config():
    """
    上报捕鱼成本收益配置
    """
    print "report_fish_cb_config, start"
    outPath = getOutPath("reportFishCB")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("ReportFishCB")
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
        
        if cols[0]:
            one = collections.OrderedDict()
            config[int(cols[0])] = one
            one["enable"] = int(cols[1])
            one["interval"] = cols[2]
            one["count"] = cols[3]

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "report_fish_cb_config, end"


def robot_config():
    """
    机器人配置
    """
    print "robot_config, start"
    outPath = getOutPath("robot")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("Robot")
    config = collections.OrderedDict()
    outHandle = open(outPath, "r")
    ret = outHandle.read()
    outHandle.close()
    conf = json.loads(ret)
    conf["robotScript"] = config
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
            one["enable"] = int(cols[1])
            one["scripts"] = []
            for x in range(2, len(cols), 6):
                if cols[x] is None:
                    continue
                item = collections.OrderedDict()
                item["level"] = int(cols[x])
                item["fireRange"] = json.loads(cols[x + 1])
                item["idleRange"] = json.loads(cols[x + 2])
                item["leaveRange"] = json.loads(cols[x + 3])
                item["chatExp"] = json.loads(cols[x + 4])
                item["probb"] = int(cols[x + 5])
                one["scripts"].append(item)

    result = json.dumps(conf, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "robot_config, end"


def multi_lang_text():
    """
    多语言文本配置
    """
    print "multi_lang_text, start"
    reload(sys)
    sys.setdefaultencoding("utf-8")
    ws = getWorkBook("multiLangText.xlsx").get_sheet_by_name('multiLangText')
    config = collections.OrderedDict()
    outPath = getOutPath("multiLangText")
    i = 0 
    startRowNum = 4
    for row in ws.rows:
        i = i+1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        if str(cols[0]) in config:
            raise KeyError("key %s repeat" % str(cols[0]))
        if cols[0] is not None:
            one = collections.OrderedDict()
            config[str(cols[0])] = one
            one["zh"] = str(cols[1])
            if cols[2]:
                one["en"] = str(cols[2])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    result = re.sub(r"\\\\n", r"\\n", result)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "multi_lang_text, end"


def prizewheel_config():
    """
    渔场轮盘配置
    """
    print "prizewheel_config, start"
    outPath = getOutPath("prizeWheel")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("PrizeWheel")
    config = collections.OrderedDict()
    config["maxSpinTimes"] = 1
    config["energy"] = []
    config["prize"] = collections.OrderedDict()
    config["bet"] = collections.OrderedDict()
    startRowNum = 4
    h = 0

    wheelIdx = 16
    betIdx = 51
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
            one = collections.OrderedDict()
            config["energy"].append(one)
            for i in range(3, 14, 3):
                one[str(cols[i])] = collections.OrderedDict()
                one[str(cols[i])]["fishPool"] = int(cols[i])
                one[str(cols[i])]["cost"] = int(cols[i + 1])
                one[str(cols[i])]["add"] = json.loads(cols[i + 2])

        if cols[wheelIdx]:
            config["prize"].setdefault(str(cols[wheelIdx]), collections.OrderedDict())
            config["prize"][str(cols[wheelIdx])]["nextRoomId"] = int(cols[wheelIdx + 1])
            config["prize"][str(cols[wheelIdx])]["nextRoomMultiple"] = int(cols[wheelIdx + 2])
            config["prize"][str(cols[wheelIdx])]["betList"] = json.loads(cols[wheelIdx + 3])
            wheel = []
            for i in range(wheelIdx + 4, wheelIdx + 34, 3):
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

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "prizewheel_config, end"


def grandPrixPrizewheel_config():
    """
    渔场轮盘配置
    """
    print "grandPrixPrizewheel_config, start"
    outPath = getOutPath("grandPrixPrizeWheel")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("GrandPrixPrizeWheel")
    config = collections.OrderedDict()
    config["maxSpinTimes"] = 1
    config["ratio"] = {}
    config["energy"] = []
    config["prize"] = collections.OrderedDict()
    config["bet"] = collections.OrderedDict()
    startRowNum = 4
    h = 0

    wheelIdx = 18
    betIdx = 51
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
            config["ratio"] = {"fire": float(cols[2]), "loss": float(cols[3])}      # 开火充能系数 亏损充能系数

        if cols[5]:
            one = collections.OrderedDict()
            config["energy"].append(one)
            for i in range(5, 16, 3):
                one[str(cols[i])] = collections.OrderedDict()
                one[str(cols[i])]["fpMultiple"] = int(cols[i])                      # 倍率
                one[str(cols[i])]["addUnit"] = int(cols[i + 1])                     # 单次充能
                one[str(cols[i])]["cost"] = int(cols[i + 2])                        # 单次耗能
                one[str(cols[i])]["add"] = {}                                       #

        if cols[wheelIdx]:
            config["prize"].setdefault(str(cols[wheelIdx]), collections.OrderedDict())
            config["prize"][str(cols[wheelIdx])]["nextRoomId"] = 0
            config["prize"][str(cols[wheelIdx])]["nextRoomMultiple"] = 0
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

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "grandPrixPrizewheel_config, end"


def level_funds_config(clientId=0):
    """
    成长基金奖励配置
    """
    sn = "LevelFunds" if clientId == 0 else "LevelFunds" + "_" + str(clientId)
    fn = "0.json" if clientId == 0 else str(clientId) + ".json"
    print "level_funds_config, start, ", sn, fn
    outPath = getOutPath("levelFunds", fn)
    wb = getWorkBook()
    ws = wb.get_sheet_by_name(sn)
    config = collections.OrderedDict()
    config["canBuyIdx"] = []
    config["funds"] = []
    config["rewards"] = collections.OrderedDict()
    startRowNum = 4
    fundIdx = 2
    rewardsIdx = 12
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
            config["funds"].append(one)
            one["productId"] = cols[fundIdx + 1]
            one["idx"] = cols[fundIdx + 0]
            one["type"] = cols[fundIdx + 2]
            one["name"] = cols[fundIdx + 3]
            one["buyType"] = cols[fundIdx + 4]
            one["price_direct"] = one["price"] = cols[fundIdx + 5]
            one["price_diamond"] = cols[fundIdx + 6]
            one["otherBuyType"] = json.loads(cols[fundIdx + 7])
            one["title"] = cols[fundIdx + 8]

        if cols[rewardsIdx]:
            config["rewards"].setdefault(str(cols[rewardsIdx + 1]), [])
            one = collections.OrderedDict()
            config["rewards"][str(cols[rewardsIdx + 1])].append(one)
            one["level"] = int(cols[rewardsIdx + 0])
            one["free_rewards"] = json.loads(cols[rewardsIdx + 3])
            one["rechargeBonus"] = int(cols[rewardsIdx + 4])
            one["funds_rewards"] = json.loads(cols[rewardsIdx + 6])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "level_funds_config, end"


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
    configFile = os.path.split(os.path.realpath(__file__))[0] + "/%s" % filename
    return load_workbook(filename=configFile, read_only=True, data_only=True)


def getOutPath(dirname, filename="0.json"):
    global ServerPath
    dirPath = os.path.split(os.path.realpath(__file__))[0] + ServerPath + "/%s/" % dirname
    filePath = dirPath + filename
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    return filePath


def process_single_config(idx, task_queue, cost_queue, err_queue, sp):
    """
    处理单个配置文件
    """
    reload(sys)
    sys.setdefaultencoding("utf-8")
    print "---- %d cpu start!" % idx
    global ServerPath
    ServerPath = sp
    while not task_queue.empty():
        confFunc, arg = task_queue.get()
        try:
            t1 = time.time()
            if arg is None:
                confFunc()
            else:
                confFunc(arg)
            _costTime = time.time() - t1
            if arg is None:
                cost_queue.put((confFunc.__name__, _costTime))
            else:
                cost_queue.put((confFunc.__name__ + "_" + str(arg), _costTime))
        except Exception, e:
            print "=========== export ", confFunc.__name__, " failed ! ", traceback.format_exc()
            err_queue.put((confFunc.__name__ + "_" + str(arg), e))


# 配置列表
config_list = [
    # (activity_config, None),
    # (multi_lang_text, None),
    (newbie7DaysGift_config, None),
    (lottery_ticket_config, None),
    (pass_card_config, None),
    (skill_compen_config, None),
    (grand_prize_pool_config, None),
    # (piggy_bank_config, None),
    (prizewheel_config, None),
    (grandPrixPrizewheel_config, None),
    # (time_limited_store_config, None),
    (levelRewards_config, None),
    (level_funds_config, None),
    (level_funds_config, 25794),
    (super_egg_config, None),
    (updateVerRewards_config, None),
    (bigPrize_config, None),
    (compAct_config, None),
    # (checkin_config, None),
    (fish_config, None),
    (weapon_config, None),
    (ulevel_config, None),
    (skill_grade_config, None),
    (skill_star_config, None),
    # (main_quest_config, None),
    # (daily_quest_config, None),
    (cmptt_task_config, None),
    (ncmptt_task_config, None),
    (bonus_task_config, None),
    (guide_task_config, None),
    (probability_config, None),
    (dynamic_odds_config, None),
    # (lottery_pool_config, None),
    (catch_drop_config, None),
    # (vip_config, None),
    # (fixed_multiple_fish, None),
    (call_multiple_fish, None),
    (fishBonus_config, None),
    # (match_multiple_fish, None),
    # (achievement_config, None),
    # (honor_config, None),
    (weaponPowerRate_config, None),
    (weapon_stage_count_config, None),
    (gunskin_config, None),
    # (plyerBuffer_config, None),
    # (randomMultipleFish_config, None),
    (gunLevel, None),
    (tableTask, None),
    (inviteTask_config, None),
    (rechargePool_config, None),
    # (share_config, None),
    (fly_pig_config, None),
    (starfish_roulette_config, None),
    (surpass_target_config, None),
    (special_item_config, None),
    (robot_config, None),
    (report_fish_cb_config, None),
    # (treasure_config, None),
    (statistic_prop_config, None),
    (slot_machine_config, None),
    (money_tree_config, None),
    (canned_fish_config, None),
    (credit_store_config, None),
    (supply_box_config, None),
    (festival_turntable_config, None),
    (collect_item_config, None),
    (abtest_config, None),
    # (world_boss_config, None),
    (terror_fish, None),
]

if __name__ == "__main__":
    TestConfPath = ""
    RealeaseConfPath = ""
    print "begin"
    t1 = int(time.time())
    ServerPath = '/../../../../../../wx_superboss/trunk/xxfish_dev/config37/game/44'          # 默认练习路径
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
        conf_queue.put(conf)
    cost_queue = Queue()
    err_queue = Queue()
    isUseMultiProcess = len(sys.argv) > 2 and sys.argv[2] == "-m" and cpu_count() > 1
    if isUseMultiProcess:
        freeze_support()
        processList = [Process(target=process_single_config, args=(i + 1, conf_queue, cost_queue, err_queue, ServerPath)) for i in range(cpu_count())]
        for p in processList:
            p.start()
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

