#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Created by lichen on 17/2/8.
执行该脚本，将会生成newfish_common.xlsm对应的json配置文件
以及multiLangText_multiple.xlsx、multiLangText.xlsx对应的多语言json配置文件
"""

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
    ws = getWorkBook("multiLangText_multiple.xlsx").get_sheet_by_name('multiLangText')
    i = 0
    for row in ws.rows:
        i = i+1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        # if str(cols[0]) in config:
            # raise KeyError("key %s repeat" % str(cols[0]))
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


def drop_config():
    """
    掉落的配置
    :return:
    """
    print "drop_config, start"
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
    print "drop_config, end"


def activity_config():
    """活动配置"""
    reload(sys)
    sys.setdefaultencoding("utf-8")
    outPath = getOutPath("activity")
    ws = getWorkBook().get_sheet_by_name("Activity")
    taskConfig = activity_task()
    config = collections.OrderedDict()
    config["activityInfo"] = collections.OrderedDict()
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
        if str(cols[0]) in config["activityInfo"]:
            raise KeyError("activityId %d repeat" % int(cols[0]))
        one["Id"] = cols[0]
        one["tip"] = cols[1]
        one["name"] = cols[2]
        if cols[3]:
            one["rule"] = json.loads(cols[3])
        else:
            one["rule"] = {}
        one["type"] = int(cols[4])
        one["tabType"] = int(cols[5])
        one["tabName"] = str(cols[6])
        one["clientModel"] = int(cols[7])
        one["modelUIType"] = int(cols[8])
        one["isDailyReset"] = int(cols[9])
        one["limitVip"] = int(cols[10])
        one["limitLevel"] = int(cols[11])
        one["limitGuide"] = int(cols[12])
        one["limitGameTime"] = int(cols[13])
        one["registerTime"] = int(cols[14])
        one["reward"] = cols[15]
        one["order"] = int(cols[16])
        one["lowClientVersion"] = (cols[17])
        one["reviewVerLimit"] = int(cols[18])
        if cols[19] and str(cols[20]) != "0":
            one["sysLimit"] = json.loads(cols[19])
        if str(cols[20]) == "0":
            continue
        try:
            one["activityEnable"] = json.loads(cols[20])
        except ValueError:
            raise KeyError("activity_config %s" % cols[0])
        one["effectiveTime"] = 0
        if cols[21] and cols[21] != "0":
            one["effectiveTime"] = {}
            one["effectiveTime"]["start"] = cols[21]
            one["effectiveTime"]["end"] = cols[22]
        if cols[23] and cols[23] != "0":
            timeArr = str(cols[23]).split("|")
            one["realAcTime"] = {}
            one["realAcTime"]["start"] = timeArr[0]
            one["realAcTime"]["end"] = timeArr[1]
        one["overDay"] = int(cols[24])
        one["receivedVisible"] = int(cols[25])
        if cols[26] and cols[26] != "0":
            one["dayTimeLimit"] = int(cols[26])
        if cols[27] and cols[27] != "0":
            one["notInTable"] = int(cols[27])
        if cols[28] and cols[28] != "0":
            one["sort"] = int(cols[28])
        one["colors"] = cols[29]
        one["activityTag"] = int(cols[30])
        one["isShowModuleTip"] = int(cols[31])
        if cols[32]:
            try:
                one["extends"] = json.loads(cols[32])
            except:
                one["extends"] = str(cols[32])
        one["acImg"] = cols[33]
        if cols[34]:
            one["acImgApp"] = cols[34] or ""
        if cols[35]:
            one["acImgQQ"] = cols[35] or ""
        if cols[36]:
            one["acImgEN"] = cols[36] or ""
        one["buttonParams"] = []
        for x in xrange(37, len(cols), 5):
            if cols[x]:
                item = {}
                item["action"] = cols[x]
                item["btnStr"] = cols[x + 1]
                if cols[x + 2]:
                    item["btnStrEN"] = cols[x + 2]
                item["param"] = cols[x + 3]
                item["btnPos"] = cols[x + 4]
                one["buttonParams"].append(item)
            else:
                break
        taskKey = one["Id"][0:-9]
        if taskConfig.has_key(taskKey):
            one["task"] = taskConfig[taskKey]
        config["activityInfo"][str(cols[0])] = one
    # config["notice"] = notice_config()
    config["activityClient"] = activity_Client()
    result = json.dumps(config, indent=4, ensure_ascii=False)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()


def getClientIdMap():
    """获取客户端的映射map"""
    import urllib2
    import urllib
    import json
    from hashlib import md5
    def dohttpquery(posturl, datadict):
        Headers = {"Content-type": "application/x-www-form-urlencoded"}
        postData = urllib.urlencode(datadict)
        request = urllib2.Request(url=posturl, data=postData, headers=Headers)
        response = urllib2.urlopen(request)
        if response != None :
            retstr = response.read()
            return retstr
        return "{}"
    ct = int(time.time())
    sign = "gdss.touch4.me-api-" + str(ct) + "-gdss.touch4.me-api"
    m = md5()
    m.update(sign)
    md5code = m.hexdigest()
    sign = md5code.lower()
    posturl = "%s/?act=api.%s&time=%d&sign=%s" % ("http://gdss.touch4.me", "getClientIdDict", ct, sign)
    retstr = dohttpquery(posturl, {})
    return json.loads(retstr).get("retmsg", {})


def activity_task():
    """活动的任务"""
    ws = getWorkBook().get_sheet_by_name("ActivityTask")
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
        one = collections.OrderedDict()
        if config.has_key(str(cols[1])) and str(cols[0]) in config[str(cols[1])]:
            raise KeyError("activityId %d repeat" % int(cols[0]))
        one["id"] = cols[0]
        one["frontTasks"] = cols[2]
        one["showForever"] = cols[3]
        one["repeat"] = cols[4]
        one["type"] = cols[5]
        if cols[6]:
            one["isInside"] = cols[6]
        one["value"] = cols[7]
        one["reward"] = cols[8]
        if cols[9]:
            one["spareReward"] = cols[9]
        one["taskDesc"] = cols[10]
        one["taskImg"] = cols[12]
        one["taskDisableImg"] = cols[13]
        one["totalCount"] = cols[14]
        one["takeTimesPerDay"] = cols[15]
       
        if str(cols[1]) not in config:
            config[str(cols[1])] = collections.OrderedDict()
        config[str(cols[1])][str(cols[0])] = one
    return config    
    # result = json.dumps(config, indent=4, ensure_ascii=False)        
    # return result


def getClientIdNum(clientId):
    """获取客户端的数字标识"""
    global ClientIdMap
    ClientIdMap = ClientIdMap or getClientIdMap()
    result = ClientIdMap.get(clientId)
    print clientId, result
    assert result
    return result


def activity_Client():
    """活动客户端使用的活动模板"""
    ws = getWorkBook().get_sheet_by_name("ClientId")
    config = collections.OrderedDict()
    zhTempDict = collections.OrderedDict()
    enTempDict = collections.OrderedDict()
    config2 = []
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
        one = []
        clientId = str(cols[0])
        clientIdNum = getClientIdNum(clientId)
        if cols[1]:
            zhTempDict[clientIdNum] = cols[1]
        if cols[2]:
            enTempDict[clientIdNum] = cols[2]
        if int(cols[3]) == 1:
            config2.append(clientIdNum)
    config["zh"] = zhTempDict
    config["en"] = enTempDict
    outPath = getOutPath("common")
    outHandle = open(outPath, "r")
    conf = json.load(outHandle)
    outHandle.close()
    conf["reviewLimitClientIds"] = config2
    def sortDict(_conf):
        if isinstance(_conf, dict):
            conf_sorted = sorted(_conf.iteritems())
            _conf = collections.OrderedDict()
            for k, v in conf_sorted:
                if isinstance(v, dict):
                    v = sortDict(v)
                elif isinstance(v, list):
                    __v = [sortDict(_v) for _v in v]
                    v = __v
                _conf[k] = v
        return _conf
    conf = sortDict(conf)
    # conf_sorted = sorted(conf.items(), key=lambda k: k[0])
    # conf = collections.OrderedDict()
    # for k, v in conf_sorted:
    #     conf[k] = v
    result = json.dumps(conf, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    return config


def skill_config():
    """
    解析技能表
    """
    print "skill_config, start"
    outPath = getOutPath("skill")
    ws = getWorkBook().get_sheet_by_name("Skill")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    levelDict = collections.OrderedDict()
    starDict = collections.OrderedDict()
    config["grade"] = levelDict
    config["star"] = starDict
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        for cell in row:
            cols.append(cell.value)
        if not cols[1]:
            continue
        if cols[1] and cols[1] not in levelDict.keys():
            level = collections.OrderedDict()
            levelDict[cols[1]] = level                      # {技能id: {}}
        if cols[6] and cols[6] not in starDict.keys():
            star = collections.OrderedDict()
            starDict[row[6].value] = star
        if cols[2]:
            one = collections.OrderedDict()
            level[str(cols[2])] = one
            one["consume"] = json.loads(cols[3])
        if cols[7]:
            one = collections.OrderedDict()
            star[str(cols[7])] = one
            one["consume"] = json.loads(cols[8])
    result = json.dumps(config, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print "skill_config, end"


def lucky_tree_conf():
    """
    免费金币摇钱树配置
    """
    print "lucky_tree_conf, start, "
    outPath = getOutPath("luckyTree")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("LuckyTree")
    config = collections.OrderedDict()
    config["rewardList"] = []
    config["accelerateTime"] = 0
    config["interval"] = 0
    config["rewardCount"] = 0
    config["rule"] = ""
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
            config["rewardList"].append(one)
            one["id"] = int(cols[0])
            one["reward"] = json.loads(cols[1])
            one["targetVal"] = int(cols[2])

        if cols[4]:
            config["accelerateTime"] = int(cols[4])
            config["interval"]= int(cols[5])
            config["rewardCount"] = int(cols[6])
            config["rule"] = str(cols[7])
            config["vipLimit"] = int(cols[8])
            config["maxSkiptimes"] = int(cols[9])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "lucky_tree_conf, end"


def chest_config():
    print u"start 宝箱配置Chest"
    outPath = getOutPath("chest")
    ws = getWorkBook().get_sheet_by_name("Chest")
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
        one = collections.OrderedDict()
        if str(cols[0]) in config:
            raise KeyError("chestId %d repeat" % int(cols[0]))
        config[str(cols[0])] = one
        one["chestId"] = int(cols[0])
        one["name"] = unicode(cols[1])
        one["star"] = int(cols[3])
        one["type"] = int(cols[4])
        one["show"] = int(cols[5])                          # 是否显示星级
        one["kindId"] = int(cols[6])                        # 兑换券道具ID
        one["unlockTime"] = int(cols[7])                    # 解锁时间
        one["levelRange"] = json.loads(cols[8])             # 宝箱级别范围
        one["openCoin"] = int(cols[9])                      # 开启消耗金币/分钟
        startNum = 9
        assert int(cols[startNum + 1]) <= int(cols[startNum + 2])
        one["coinRange"] = [int(cols[startNum + 1]), int(cols[startNum + 2])]
        assert int(cols[startNum + 3]) <= int(cols[startNum + 4])
        one["pearlRange"] = [int(cols[startNum + 3]), int(cols[startNum + 4])]
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
        i = i+1
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
        one["kindId"] = int(cols[0])    # 物品ID
        one["type"] = int(cols[3])
        one["rare"] = int(cols[4])      # 稀有度
        one["level"] = int(cols[5])
        one["unlock"] = int(cols[6])    # 解锁等级
        one["weight"] = int(cols[7])
        one["convertCoin"] = int(cols[8])   # 溢出后转换金币数

    result = json.dumps(config, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()
    print u"end 宝箱掉落配置ChestDrop"


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
            if cols[4]:
                one["name"] = str(cols[4])
            if cols[5]:
                one["desc"] = str(cols[5])
            if cols[6]:
                one["itemType"] = int(cols[6])
            if cols[7]:
                one["typeName"] = str(cols[7])
            if cols[8]:
                one["minimumVersion"] = str(cols[8])
            one["reviewVerLimit"] = int(cols[9]) if cols[9] else 0
            actCnt = int(cols[10])
            for i in range(11, 11 + 2 * actCnt, 2):
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


def store_config(clientId=0):
    """商店配置"""
    reload(sys)
    sys.setdefaultencoding("utf-8")

    sn = "WeiXin" if clientId == 0 else str(clientId)
    fn = "0.json" if clientId == 0 else str(clientId) + ".json"
    outPath = getOutPath("store", fn)
    ws = getWorkBook("store.xlsx").get_sheet_by_name(sn)
    config = collections.OrderedDict()
    config["coinStore"] = collections.OrderedDict()
    config["coinStore"]["items"] = collections.OrderedDict()
    config["diamondStore"] = collections.OrderedDict()
    config["diamondStore"]["items"] = collections.OrderedDict()
    config["pearlStore"] = collections.OrderedDict()
    config["chestStore"] = collections.OrderedDict()
    config["chestStore"]["items"] = collections.OrderedDict()
    config["chestStore"]["shop"] = collections.OrderedDict()
    config["itemStore"] = collections.OrderedDict()
    config["itemStore"]["items"] = collections.OrderedDict()
    config["couponStore"] = collections.OrderedDict()
    config["couponStore"]["items"] = collections.OrderedDict()
    config["gunSkinStore"] = collections.OrderedDict()
    config["bulletStore"] = collections.OrderedDict()
    config["bulletStore"]["hall37"] = collections.OrderedDict()
    config["hotStore"] = collections.OrderedDict()
    config["hotStore"]["items"] = collections.OrderedDict()

    i = 0
    startRowNum = 4
    hot_store_num = 0
    coin_store_num = 7
    diamond_store_num = 31
    chest_store_num = 55
    item_store_num = 79
    coupon_store_num = 103
    pearl_store_num = 127
    gun_skin_num = 142
    robbery_store_num = 156
    storeTabDict = {"coinStore": coin_store_num, "diamondStore": diamond_store_num,
                    "chestStore": chest_store_num, "itemStore": item_store_num, "couponStore": coupon_store_num}
    for row in ws.rows:
        i = i+1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[hot_store_num]:
            one = collections.OrderedDict()
            config["hotStore"]["items"][str(cols[hot_store_num])] = one
            one["order"] = int(cols[hot_store_num + 1])
            one["pt"] = str(cols[hot_store_num + 2]) if cols[hot_store_num + 2] else ""
            one["extendData"] = json.loads(cols[hot_store_num + 3])
            one["limitCond"] = json.loads(cols[hot_store_num + 4])
            if cols[hot_store_num + 5]:
                config["hotStore"]["shop"] = json.loads(cols[hot_store_num + 5])

        for tab, _idx in storeTabDict.iteritems():
            if cols[_idx] is not None:
                one = collections.OrderedDict()
                config[tab]["items"][str(cols[_idx])] = one
                one["name"] = json.loads(cols[_idx + 1])
                one["order"] = int(cols[_idx + 2])
                one["pt"] = str(cols[_idx + 3]) if cols[_idx + 3] else ""
                one["itemId"] = int(cols[_idx + 4])
                one["count"] = json.loads(cols[_idx + 5])
                one["price"] = int(cols[_idx + 6]) if cols[_idx + 6] else 0
                one["cur_price"] = json.loads(cols[_idx + 7])
                one["price_direct"] = int(cols[_idx + 8]) if cols[_idx + 8] else 0
                one["price_diamond"] = int(cols[_idx + 9]) if cols[_idx + 9] else 0
                one["pic"] = str(cols[_idx + 10]) if cols[_idx + 10] != "\"\"" else ""
                one["buyType"] = str(cols[_idx + 11])
                one["otherBuyType"] = json.loads(cols[_idx + 12])
                one["label1"] = json.loads(cols[_idx + 13])
                if cols[_idx + 14]:
                    one["label1BgType"] = json.loads(cols[_idx + 14])
                one["label2"] = json.loads(cols[_idx + 15])
                if cols[_idx + 16]:
                    one["label2BgType"] = json.loads(cols[_idx + 16])
                one["label3"] = json.loads(cols[_idx + 17])
                if cols[_idx + 18]:
                    one["label3BgType"] = json.loads(cols[_idx + 18])
                one["additionVip"] = int(cols[_idx + 19])
                one["extendData"] = json.loads(cols[_idx + 20])
                one["limitCond"] = json.loads(cols[_idx + 21])
                if cols[_idx + 22] and cols[_idx + 22] != "\"\"":
                    config[tab]["shop"] = json.loads(cols[_idx + 22])

        if cols[pearl_store_num]:
            one = collections.OrderedDict()
            config["pearlStore"][str(cols[pearl_store_num])] = one
            one["name"] = json.loads(cols[pearl_store_num+1])
            one["itemId"] = int(cols[pearl_store_num+2])
            one["count"] = json.loads(cols[pearl_store_num+3])
            one["order"] = int(cols[pearl_store_num+4])
            one["price"] = int(cols[pearl_store_num+5])
            one["price_direct"] = int(cols[pearl_store_num+6])
            one["price_diamond"] = int(cols[pearl_store_num+7])
            one["additionVip"] = int(cols[pearl_store_num+8])
            one["tag"] = int(cols[pearl_store_num+9])
            one["addition"] = json.loads(cols[pearl_store_num+10])
            if cols[pearl_store_num+11] == "\"\"":
                one["pic"] = ""
            else:
                one["pic"] = str(cols[pearl_store_num+11])
            one["buyType"] = str(cols[pearl_store_num+12])
            one["otherBuyType"] = json.loads(cols[pearl_store_num+13])

        if cols[gun_skin_num]:
            one = collections.OrderedDict()
            config["gunSkinStore"][str(cols[gun_skin_num])] = one
            one["name"] = str(cols[gun_skin_num+1])
            one["itemId"] = int(cols[gun_skin_num+2])
            one["count"] = int(cols[gun_skin_num+3])
            one["order"] = int(cols[gun_skin_num+4])
            if cols[gun_skin_num+5] is not None:
                one["vip"] = int(cols[gun_skin_num+5])
            if cols[gun_skin_num+6] != "\"\"":
                one["desc"] = str(cols[gun_skin_num+6])
            else:
                one["desc"] = ""
            one["price"] = int(cols[gun_skin_num+7])
            one["discountPrice"] = json.loads(cols[gun_skin_num+8])
            one["tag"] = int(cols[gun_skin_num+9])
            one["addition"] = json.loads(cols[gun_skin_num+10])
            if cols[gun_skin_num+11] != "\"\"":
                one["pic"] = str(cols[gun_skin_num+11])
            else:
                one["pic"] = ""
            one["buyType"] = str(cols[gun_skin_num+12])

        if cols[robbery_store_num]:
            one = collections.OrderedDict()
            config["bulletStore"]["hall37"][str(cols[robbery_store_num])] = one
            one["name"] = str(cols[robbery_store_num+1])
            one["itemId"] = int(cols[robbery_store_num+2])
            one["count"] = int(cols[robbery_store_num+3])
            one["order"] = int(cols[robbery_store_num+4])
            one["price"] = int(cols[robbery_store_num+5])
            one["price_direct"] = int(cols[robbery_store_num+6])
            one["price_diamond"] = int(cols[robbery_store_num+7])
            one["tag"] = int(cols[robbery_store_num+8])
            one["addition"] = json.loads(cols[robbery_store_num+9])
            if cols[robbery_store_num+10] != "\"\"":
                one["pic"] = str(cols[robbery_store_num+10])
            else:
                one["pic"] = ""
            one["buyType"] = str(cols[robbery_store_num+11])
            one["robberyBonus"] = int(cols[robbery_store_num+12])
            one["vipAddition"] = json.loads(cols[robbery_store_num+13])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "store_config, end"


def time_limited_store_config():
    """
    限时商城配置
    """
    reload(sys)
    sys.setdefaultencoding("utf-8")
    print "time_limited_store_config, start"
    outPath = getOutPath("timeLimitedStore")
    ws = getWorkBook("store.xlsx").get_sheet_by_name("TimeLimitedStore")
    config = collections.OrderedDict()
    config["stores"] = collections.OrderedDict()
    config["slot"] = []
    config["types"] = {}
    startRowNum = 4
    h = 0
    for row in ws.rows:
        h = h + 1
        if h < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        one = collections.OrderedDict()
        if cols[0]:
            config["stores"][str(cols[0])] = one
            one["id"] = str(cols[0])
            one["name"] = str(cols[1])
            one["itemId"] = int(cols[2])
            one["count"] = int(cols[3])
            one["buyType"] = unicode(cols[4] or "")
            one["price"] = int(cols[5])
            one["levelRange"] = json.loads(cols[6])
            one["rate"] = int(cols[7])
            one["types"] = json.loads(cols[8])
            one["maxBuyCount"] = int(cols[9])
            one["label1"] = unicode(cols[10] or "")
            one["labelBgType"] = unicode(cols[11] or "")
            one["label2"] = unicode(cols[12] or "")
            one["label2BgType"] = unicode(cols[13] or "")
            one["label3"] = unicode(cols[14] or "")
            one["label3BgType"] = unicode(cols[15] or "")

            for t in json.loads(cols[8]):
                config["types"].setdefault(str(t), [])
                config["types"][str(t)].append(one)

        if cols[17]:
            config["slot"].append({"idx": int(cols[17]), "unlockLevel": int(cols[18]), "typeList": json.loads(cols[19])})

        if cols[21]:
            config["vipLimit"] = int(cols[21])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    result = re.sub(r"\\\\n", r"\\n", result)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "time_limited_store_config, end"


def exchange_store_config():
    """
    兑换商城
    """
    reload(sys)
    sys.setdefaultencoding("utf-8")
    print "exchange_store_config, start"
    outPath = getOutPath("exchangeStore")
    ws = getWorkBook("store.xlsx").get_sheet_by_name("ExchangeStore")
    config = collections.OrderedDict()
    config["items"] = collections.OrderedDict()
    i = 0
    startRowNum = 4
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)
        _idx = 0
        if cols[_idx] is not None:
            one = collections.OrderedDict()
            config["items"][str(cols[_idx])] = one
            one["name"] = json.loads(cols[_idx + 1])
            one["order"] = int(cols[_idx + 2])
            one["pt"] = str(cols[_idx + 3]) if cols[_idx + 3] else ""
            one["itemId"] = int(cols[_idx + 4])
            one["count"] = json.loads(cols[_idx + 5])
            one["price"] = int(cols[_idx + 6]) if cols[_idx + 6] else 0
            one["cur_price"] = json.loads(cols[_idx + 7])
            one["price_direct"] = int(cols[_idx + 8]) if cols[_idx + 8] else 0
            one["price_diamond"] = int(cols[_idx + 9]) if cols[_idx + 9] else 0
            one["pic"] = str(cols[_idx + 10]) if cols[_idx + 10] != "\"\"" else ""
            one["buyType"] = str(cols[_idx + 11])
            one["otherBuyType"] = json.loads(cols[_idx + 12])
            one["label1"] = json.loads(cols[_idx + 13])
            if cols[_idx + 14]:
                one["label1BgType"] = json.loads(cols[_idx + 14])
            one["label2"] = json.loads(cols[_idx + 15])
            if cols[_idx + 16]:
                one["label2BgType"] = json.loads(cols[_idx + 16])
            one["label3"] = json.loads(cols[_idx + 17])
            if cols[_idx + 18]:
                one["label3BgType"] = json.loads(cols[_idx + 18])  
            one["additionVip"] = int(cols[_idx + 19])
            one["extendData"] = json.loads(cols[_idx + 20])
            one["limitCond"] = json.loads(cols[_idx + 21])
            one["categoryId"] = int(cols[_idx + 22])
            if cols[_idx + 23] and cols[_idx + 23] != "\"\"":
                config["shop"] = str(cols[_idx + 23])

        if cols[_idx + 25]:
            config["startTS"] = str(cols[_idx + 25])
        if cols[_idx + 26]:
            config["loopDays"] = int(cols[_idx + 26])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "exchange_store_config, end"


def piggy_bank_config():
    """
    存钱罐池配置
    """
    reload(sys)
    sys.setdefaultencoding("utf-8")
    print "piggy_bank_config, start"
    outPath = getOutPath("piggyBank")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("PiggyBank")
    config = collections.OrderedDict()
    rule = {}
    startRowNum = 4
    h = 0
    for row in ws.rows:
        h = h + 1
        if h < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        for k in range(0, 4, 2):
            if cols[k]:
                rule[str(cols[k])] = unicode(cols[k + 1] or "")
        if cols[5] is None:
            break
        one = collections.OrderedDict()
        config[int(cols[5])] = one
        for i in range(6, len(cols), 18):
            one[str(cols[i])] = collections.OrderedDict()
            one[str(cols[i])]["type"] = str(cols[i])
            one[str(cols[i])]["productId"] = str(cols[i + 1])
            one[str(cols[i])]["productName"] = unicode("存钱罐")
            one[str(cols[i])]["initVal"] = int(cols[i + 2])
            if cols[i + 3] > 0:
                one[str(cols[i])]["maxDailyCount"] = int(cols[i + 3] * 10000)
            else:
                one[str(cols[i])]["maxDailyCount"] = int(cols[i + 3])
            if cols[i + 4] > 0:
                one[str(cols[i])]["maxCount"] = int(cols[i + 4] * 10000)
            else:
                one[str(cols[i])]["maxCount"] = int(cols[i + 4])
            one[str(cols[i])]["iscooling"] = int(cols[i + 5])
            one[str(cols[i])]["endcoolingTime"] = int(cols[i + 6])
            one[str(cols[i])]["price_direct"] = int(cols[i + 7])
            one[str(cols[i])]["price_diamond"] = int(cols[i + 8])
            one[str(cols[i])]["inroom"] = int(cols[i + 9])
            one[str(cols[i])]["outroom"] = int(cols[i + 10])
            one[str(cols[i])]["firePct"] = cols[i + 11]
            one[str(cols[i])]["buyType"] = unicode(cols[i + 12] or "")
            one[str(cols[i])]["otherBuyType"] = json.loads(cols[i + 13])
            one[str(cols[i])]["price"] = int(cols[i + 14])
            one[str(cols[i])]["resetTime"] = int(cols[i + 15])
            one[str(cols[i])]["rule"] = rule[str(cols[i])]
            one[str(cols[i])]["profitPct"] = cols[i + 16]
            one[str(cols[i])]["dailyTimes"] = cols[i + 17]
    result = json.dumps(config, indent=4, ensure_ascii=False)
    result = re.sub(r"\\\\n", r"\\n", result)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "piggy_bank_config, end"


def checkin_config():
    """
    更服奖励配置
    """
    print "checkin_config, start"
    outPath = getOutPath("checkin")
    wb = getWorkBook()
    ws = wb.get_sheet_by_name("Checkin")
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

        if cols[0] is not None:
            config.setdefault("oldcheckinData", collections.OrderedDict())
            config["oldcheckinData"][str(cols[0])] = {"normalReward": json.loads(cols[1]), "shareReward": json.loads(cols[2])}

        if cols[4] is not None:
            config.setdefault("resetInfo", collections.OrderedDict())
            config["resetInfo"]["vip"] = int(cols[4])
            config["resetInfo"]["resetWeekDay"] = int(cols[5])

        if cols[8] is not None:
            config.setdefault("checkinData", collections.OrderedDict())
            one = collections.OrderedDict()
            config["checkinData"][str(cols[8])] = one
            one["type"] = str(cols[8])
            one["unlockdays"] = int(cols[9])
            one["datas"] = []
            for x in range(10, len(cols), 2):
                if cols[x]:
                    if cols[8] != "multiple":
                        one["datas"].append({"rewards": json.loads(cols[x]), "rate": int(cols[x + 1])})
                    else:
                        one["datas"].append({"rewards": int(cols[x]), "rate": int(cols[x + 1])})

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "checkin_config, end"


def treasure_config():
    """
    宝藏配置
    """
    outPath = getOutPath("treasure")
    ws = getWorkBook().get_sheet_by_name("Treasure")
    config = collections.OrderedDict()
    startRowNum = 4
    i = 0
    one = collections.OrderedDict()
    levels = None
    for row in ws.rows:
        i = i+1
        cols = []
        if i < startRowNum:
            continue
        if row[1].value not in config.keys():
            one = collections.OrderedDict()
            config[row[1].value] = one
            levels = collections.OrderedDict()
        for cell in row:
            cols.append(cell.value)
        if not cols[2]:
            continue
        one["kindId"] = int(cols[1])
        one["name"] = str(cols[2])
        one["desc"] = str(cols[3])
        one["sortId"] = int(cols[4])
        one["effectType"] = int(cols[5])
        one["limitCount"] = int(cols[6])
        one["convert"] = json.loads(cols[7])
        levelMap = collections.OrderedDict()
        levelMap["cost"] = int(cols[9])
        levelMap["params"] = json.loads(cols[10])
        levels[int(cols[8])] = (levelMap)
        one["levels"] = levels
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def main_quest_config():
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
        task["star"] = int(cols[7])

        if cols[9]:
            section = collections.OrderedDict()
            sections[int(cols[9])] = section
            section["sectionId"] = int(cols[9])
            section["sortId"] = int(cols[10])
            section["taskIds"] = json.loads(cols[11])
            section["starRewards"] = json.loads(cols[12] or "{}")
            section["display"] = int(cols[13])
    config["tasks"] = tasks
    config["sections"] = sections
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def daily_quest_config():
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
        one["gunX"] = int(cols[10])
        one["fpMultiple"] = int(cols[11])
        showDay = cols[12]
        if isinstance(showDay, unicode):
            showDay = showDay.split("|")
            showDay = [int(x) for x in showDay]
        else:
            showDay = [showDay]
        one["showDay"] = showDay
        if cols[13]:
            one["rewards"] = json.loads(cols[13])
        if cols[15]:
            conf["questOrder"] = json.loads(cols[15])

    result = json.dumps(conf, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    daily_quest_reward_config()


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


def gift_abctest_config():
    """
    礼包abc测试配置
    """
    print "gift_abctest_config, start"
    outPath = getOutPath("giftAbcTest")
    ws = getWorkBook().get_sheet_by_name("Gift_abcTest")
    config = collections.OrderedDict()
    config["enable"] = 0                                        # 开启测试
    config["mode"] = ""                                         # 指定模式
    config["data"] = collections.OrderedDict()                  # 数据
    config["gift"] = collections.OrderedDict()                  # 礼包
    startRowNum = 4
    i = 0
    giftColsIdx = 11
    eModeGiftsIdx = 65
    eModeBestIdx = 67
    eModeGifts = []
    eModeBestIndex = {}
    for row in ws.rows:
        i = i + 1
        if i < startRowNum:
            continue
        cols = []
        for cell in row:
            cols.append(cell.value)

        if cols[0]:
            config["enable"] = int(cols[0])
        if cols[1]:
            config["mode"] = str(cols[1])
        if cols[3]:
            one = collections.OrderedDict()
            config["data"][str(cols[3])] = one                  # 渔场Id
            one["low"] = {}
            one["low"]["price"] = int(cols[4])                  # 低档参考价格
            one["low"]["giftList"] = json.loads(cols[5])        # 低档礼包ID
            one["mid"] = {}
            one["mid"]["price"] = int(cols[6])
            one["mid"]["giftList"] = json.loads(cols[7])
            one["high"] = {}
            one["high"]["price"] = int(cols[8])
            one["high"]["giftList"] = json.loads(cols[9])
        if not cols[giftColsIdx]:
            break
        one = collections.OrderedDict()
        if str(cols[giftColsIdx]) in config["gift"]:
            raise KeyError("giftId %d repeat" % int(cols[giftColsIdx]))
        config["gift"][str(cols[giftColsIdx])] = one            # 礼包Id
        one["giftId"] = int(cols[giftColsIdx])                  # 礼包Id
        one["giftName"] = unicode(cols[giftColsIdx + 1])
        one["giftType"] = int(cols[giftColsIdx + 2])            # 礼包类型
        one["productId"] = cols[giftColsIdx + 3]                # 商品Id
        one["fishPool"] = int(cols[giftColsIdx + 4])            # 出现渔场
        one["lifetime"] = int(cols[giftColsIdx + 5])            # 存活时间
        one["minLevelLimit"] = int(cols[giftColsIdx + 6])       # 最小等级限制
        one["maxLevelLimit"] = int(cols[giftColsIdx + 7])
        one["coinLimit"] = int(cols[giftColsIdx + 8])           # 金币限制
        one["buyType"] = cols[giftColsIdx + 9]                  # 购买方式
        one["price"] = int(cols[giftColsIdx + 10])              # 原价
        one["discountPrice"] = int(cols[giftColsIdx + 11])      # 折扣价
        one["price_direct"] = int(cols[giftColsIdx + 12])       # 货币价格
        one["price_diamond"] = int(cols[giftColsIdx + 13])      # 钻石价格
        one["otherBuyType"] = json.loads(cols[giftColsIdx + 14])    # 其他购买方式
        one["vip"] = int(cols[giftColsIdx + 15])
        one["giftLimit"] = int(cols[giftColsIdx + 16])              # 购买礼包限制
        one["showAfterReload"] = int(cols[giftColsIdx + 17])        # 领取后需下次登录显示
        one["showAfterTimes"] = int(cols[giftColsIdx + 18])         # 领取后多久显示(分钟)
        one["roomId"] = json.loads(cols[giftColsIdx + 19])          # 房间id
        one["recordKey"] = str(cols[giftColsIdx + 20])              # 记录累计购买次数的key(0不记录)
        one["loopTimes"] = int(cols[giftColsIdx + 21])              # 循环次数
        one["appearTimes"] = json.loads(cols[giftColsIdx + 22])     # 出现次数
        one["firstBuyRewards"] = json.loads(cols[giftColsIdx + 24]) # 首次购买奖励
        one["getAfterBuy"] = json.loads(cols[giftColsIdx + 25])     # 购买立得
        one["expireTime"] = int(cols[giftColsIdx + 26])             # 有效期(分钟)
        one["popupLevel"] = int(cols[giftColsIdx + 27])             # 弹出等级
        one["items"] = []
        for x in xrange(giftColsIdx + 28, len(cols), 5):
            if cols[x]:
                item = {}
                item["type"] = cols[x]                              # 礼物类型
                item["name"] = unicode(cols[x + 1]) if cols[x + 1] else ""      # 礼物名
                item["desc"] = unicode(cols[x + 2]) if cols[x + 2] else ""      # 礼物描述
                item["itemId"] = cols[x + 3]                        # 道具Id
                item["count"] = cols[x + 4]                         # 数量
                one["items"].append(item)
        if cols[eModeGiftsIdx]:
            eModeGifts.append(json.loads(cols[eModeGiftsIdx]))      # e模式下的各档礼包
        if cols[eModeBestIdx]:
            eModeBestIndex[str(cols[eModeBestIdx])] = cols[eModeBestIdx + 1]    # 44002、0
    config["eModeGifts"] = eModeGifts
    config["eModeBestIndex"] = eModeBestIndex
    print "gift_abctest_config, end"
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


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
        i = i + 1
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
        one["giftId"] = int(cols[0])                    # 礼包ID
        one["giftName"] = unicode(cols[1])
        one["giftType"] = int(cols[2])                  # 礼包类型
        one["productId"] = cols[3]                      # 商品ID
        one["fishPool"] = int(cols[4])                  # 出现渔场
        one["lifetime"] = int(cols[5])                  # 存活时间
        one["minLevelLimit"] = int(cols[6])             # 最小等级限制
        one["maxLevelLimit"] = int(cols[7])
        one["coinLimit"] = int(cols[8])                 # 金币限制
        one["buyType"] = cols[9]                        # 购买方式
        one["price"] = int(cols[10])                    # 原价
        one["discountPrice"] = int(cols[11])            # 折扣价
        one["price_direct"] = int(cols[12])             # 货币价格
        one["price_diamond"] = int(cols[13])            # 钻石价格
        one["otherBuyType"] = json.loads(cols[14])      # 其他购买方式
        one["vip"] = int(cols[15])                      # vip等级
        one["giftLimit"] = int(cols[16])                # 购买礼包限制
        one["showAfterReload"] = int(cols[17])          # 领取后需下次登录显示
        one["showAfterTimes"] = int(cols[18])           # 领取后多久显示(分钟)
        one["roomId"] = json.loads(cols[19])            # 房间id
        one["recordKey"] = str(cols[20])                # 记录累计购买次数的key
        one["loopTimes"] = int(cols[21])                # 循环次数
        one["appearTimes"] = json.loads(cols[22])       # 出现次数
        # 月卡专用
        if one["giftType"] == 4:
            one["monthCard"] = json.loads(cols[23])     # 对应物品(月卡专用)
        one["firstBuyRewards"] = json.loads(cols[24])   # 首次购买奖励
        one["getAfterBuy"] = json.loads(cols[25])       # 购买立得
        one["expireTime"] = int(cols[26])               # 有效期(分钟)
        one["popupLevel"] = int(cols[27])               # 弹出等级
        one["items"] = []
        for x in xrange(28, len(cols), 5):
            if not cols[x]:
                continue
            item = {}
            item["type"] = cols[x]                      # 礼物类型
            item["name"] = unicode(cols[x + 1]) if cols[x + 1] else ""      # 礼物名
            item["desc"] = unicode(cols[x + 2]) if cols[x + 2] else ""      # 礼物描述
            item["itemId"] = cols[x + 3]                # 道具Id
            item["count"] = cols[x + 4]                 # 数量
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
            config["dailyGift"][int(cols[0])] = one     # 礼包Id
            one["giftId"] = int(cols[0])                # 礼包Id
            one["giftName"] = unicode(cols[1])          # 礼包描述
            one["productId"] = cols[2]                  # 商品ID
            one["vipRange"] = json.loads(cols[3])       # vip等级限制
            one["buyType"] = cols[4]                    # 购买方式
            one["price"] = int(cols[5])                 # 价格
            one["price_direct"] = int(cols[6])          # 货币价格
            one["price_diamond"] = int(cols[7])         # 钻石价格
            one["otherBuyType"] = json.loads(cols[8])   # 其他购买方式
            one["giftInfo"] = []
            for x in range(9, len(cols), 2):
                if cols[x] is None:
                    continue
                item = collections.OrderedDict()
                item["day_idx"] = int(cols[x])          # 连购天数
                item["items"] = json.loads(cols[x + 1]) # 礼物
                one["giftInfo"].append(item)
    print "daily_gift_config, end"

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


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
        one["vipPresentCount:1137"] = int(cols[1])  # 赠送珍珠数
        one["vipPresentCount:1193"] = int(cols[2])  # 赠送银弹头数
        one["vipPresentCount:1194"] = int(cols[3])  # 赠送金弹头数
        one["vipPresentCount:1426"] = int(cols[4])  # 赠送代购券数
        one["vipPresentCount:1408"] = int(cols[5])  # 赠送冷却道具数量
        one["vipPresentCount:1429"] = int(cols[6])  # 赠送紫水晶数量
        one["vipPresentCount:1430"] = int(cols[7])  # 赠送黄水晶数量
        one["vipPresentCount:1431"] = int(cols[8])  # 赠送五彩水晶数量
        one["vipReceiveCount:1194"] = int(cols[9])  # 可接收金珠数量
        one["vipReceiveCount:1193"] = int(cols[10])  # 可接收银珠数量
        one["vipExp"] = int(cols[expStartIdx])  # VIP经验值
        one["freeRouletteTimes"] = int(cols[expStartIdx + 1])  # 免费海星许愿次数
        one["dropPearlTotalCount"] = int(cols[expStartIdx + 2])  # 掉落珍珠累计总量限制
        one["dropPearlRatioLimit"] = cols[expStartIdx + 3]  # 掉落总量超出后Level表中系数
        one["vipDesc"] = unicode(cols[expStartIdx + 4]) or ""  # VIP描述
        one["vipGift"] = json.loads(cols[expStartIdx + 5])  # VIP礼包
        one["productId"] = unicode(cols[expStartIdx + 6]) or ""  # VIP礼包ID
        one["giftName"] = unicode(cols[expStartIdx + 7]) or ""  # VIP礼包名
        one["originalPrice"] = int(cols[expStartIdx + 8])  # VIP礼包原价
        one["price"] = int(cols[expStartIdx + 9])  # VIP礼包现价
        one["pearlMultiple"] = float(cols[expStartIdx + 10])  # 任务珍珠加成倍率
        one["matchAddition"] = float(cols[expStartIdx + 11])  # 比赛分数加成
        one["setVipShow"] = int(cols[expStartIdx + 12])  # 设置vip展示
        one["almsRate"] = float(cols[expStartIdx + 13])  # 救济金倍率
        one["autoSupply:101"] = int(cols[expStartIdx + 14])  # 每日金币补足
        one["initLuckyValue:44102"] = int(cols[expStartIdx + 15])  # 比赛初始幸运值
        one["inviterReward"] = json.loads(cols[expStartIdx + 16])  # 给邀请人的奖励
        one["contFire"] = int(cols[expStartIdx + 17])  # 是否可以连发
        one["enableChat"] = int(cols[expStartIdx + 18])  # 是否可以聊天
        one["limitChatTip"] = unicode(cols[expStartIdx + 19] or "")  # 限制聊天提示
        one["convert1137ToDRate"] = json.loads(cols[expStartIdx + 20])  # 珍珠换钻石比例
        one["convert1429ToDRate"] = json.loads(cols[expStartIdx + 21])  # 紫水晶换钻石比例
        one["convert1430ToDRate"] = json.loads(cols[expStartIdx + 22])  # 黄水晶换钻石比例
        one["convert1431ToDRate"] = json.loads(cols[expStartIdx + 23])  # 五彩水晶换钻石比例
        one["grandPrixFreeTimes"] = int(cols[expStartIdx + 24])  # 大奖赛免费次数
        one["grandPrixAddition"] = float(cols[expStartIdx + 25])  # 大奖赛分数加成
        one["checkinRechargeBonus"] = int(cols[expStartIdx + 26])  # 签到增加奖池额度
        one["timeLimitedStoreRefreshTimes"] = int(cols[expStartIdx + 27])  # 限时商城刷新次数

    result = json.dumps(config, indent=4, ensure_ascii=False)
    result = re.sub(r"\\\\n", r"\\n", result)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "vip_config, end"


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


def user_level_config():
    """
    玩家等级配置
    """
    outPath = getOutPath("userLevel")
    ws = getWorkBook().get_sheet_by_name("UserLevel")
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
        if not cols[0]:
            break
        one = collections.OrderedDict()
        one["level"] = int(cols[0])
        one["exp"] = int(cols[1])
        one["rewards"] = json.loads(cols[2])
        config.append(one)
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()


def honor_config():
    """称号配置"""
    print "honor_config start"
    outPath = getOutPath("honor")
    ws = getWorkBook("achievement.xlsx").get_sheet_by_name("Honor")
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
        one = collections.OrderedDict()
        config[str(cols[1])] = one
        one["honorId"] = int(cols[1])
        one["honorName"] = str(cols[0])
        one["desc"] = unicode(cols[2])
        one["honorType"] = int(cols[3])
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "honor_config end"


def achievement_config():
    """
    成就|荣耀任务
    """
    print "achievement_config, start"
    outPath = getOutPath("achievement")
    ws = getWorkBook("achievement.xlsx").get_sheet_by_name("AchievementTask")
    config = collections.OrderedDict()
    config["tasks"] = collections.OrderedDict()
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
        one["Id"] = cols[0]
        one["desc"] = cols[1]
        one["target"] = json.loads(cols[2])
        one["type"] = cols[3]
        one["exp"] = cols[4]
        key_ = str(int(cols[0]) / 100)
        if not config["tasks"].get(key_):
            config["tasks"][key_] = collections.OrderedDict()
        config["tasks"][key_][cols[0]] = one
    config["level"] = achievement_level_config()
    config["compensate"] = achievement_compensate_config()
    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "achievement_config, end"


def achievement_level_config():
    """荣耀等级"""
    print "achievement_level_config start"
    outPath = getOutPath("achievement")
    ws = getWorkBook("achievement.xlsx").get_sheet_by_name("AchievementLevel")
    config = collections.OrderedDict()
    startRowNum = 2
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
        one["level"] = int(cols[0])
        one["exp"] = cols[1]
        if cols[2]:
            one["reward"] = {"name": int(cols[2]), "count": int(cols[3])}
        config[int(cols[0])] = one
    print "achievement_level_config end"
    return config


def achievement_compensate_config():
    """荣耀补偿"""
    outPath = getOutPath("achievement")
    ws = getWorkBook("achievement.xlsx").get_sheet_by_name("AchievementCompensate")
    config = collections.OrderedDict()
    startRowNum = 3
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
        reward = {}
        # one["Id"] = int(cols[0])
        for m in range(1, len(cols), 2):
            if not cols[m]:
                break
            reward = {"name": int(cols[m]), "count": int(cols[m + 1])}
        config[int(cols[0])] = reward
    return config


def lottery_pool_config():
    outPath = getOutPath("lotteryPool")
    ws = getWorkBook().get_sheet_by_name("LotteryPool")
    lotteryPool = collections.OrderedDict()
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
        lotteryPool[cols[0]] = one
        one["lotteryPool"] = int(cols[1])
        one["skillPool"] = int(cols[2])
        one["multiplePool"] = int(cols[3])
        one["chestPool"] = int(cols[4])
        one["rainbowPool"] = int(cols[5])
        one["bonusRatio"] = cols[6]
        one["skillRatio"] = cols[7]
        one["multipleRatio"] = cols[8]
        one["bossRatio"] = cols[9]
        one["cmpttRatio"] = cols[10]
        one["chestRatio"] = cols[11]
        one["gameTimeRatio"] = cols[12]
        one["rainbowRatio"] = cols[13]
        one["grandPrizeRatio"] = cols[14]
        one["alertThreshold"] = cols[15]
    result = json.dumps(lotteryPool, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()

def ring_lottery_pool_config():
    outPath = getOutPath("ringLotteryPool")
    ws = getWorkBook().get_sheet_by_name("RingLotteryPool")
    lotteryPool = collections.OrderedDict()
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
        lotteryPool[cols[0]] = one
        one["lotteryPool"] = int(cols[1])
        one["skillPool"] = int(cols[2])
        one["multiplePool"] = int(cols[3])
        one["chestPool"] = int(cols[4])
        one["rainbowPool"] = int(cols[5])
        one["bonusRatio"] = cols[6]
        one["skillRatio"] = cols[7]
        one["multipleRatio"] = cols[8]
        one["bossRatio"] = cols[9]
        one["cmpttRatio"] = cols[10]
        one["chestRatio"] = cols[11]
        one["gameTimeRatio"] = cols[12]
        one["rainbowRatio"] = cols[13]
        one["grandPrizeRatio"] = cols[14]
        one["alertThreshold"] = cols[15]
    result = json.dumps(lotteryPool, indent=4)        
    outHandle = open(outPath, "w")   
    outHandle.write(result)  
    outHandle.close()


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
    config["gunMultiAddition"] = []
    config["stageInfo"] = []

    startRowNum = 4

    playConfCols = 8
    openRangeConfCols = 11
    fireConfCols = 14
    feeConfCols = 16
    pointConfCols = 18
    groupConfCols = 21
    fakeDataConfCols = 28
    surpassDataCols = 33
    gunMultiAdditionCols = 37
    stageInfoCols = 41

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
            config["info"]["enable"] = int(cols[0])  # 是否开启
            config["info"]["startDay"] = str(cols[1])  # 开启时间
            config["info"]["msg"] = str(cols[2])  # 邮件内容
            config["info"]["des"] = str(cols[3])  # 提示
            config["info"]["endDes"] = str(cols[4])  # 结束页面提示
            config["info"]["robot"] = json.loads(cols[5])  # [是否启用，多久后添加，[最小间隔，最大间隔]](分钟)
            config["info"]["level"] = int(cols[6])  # 最低等级

        if cols[playConfCols] is not None:
            one = collections.OrderedDict()
            config["playAddition"].append(one)
            one["playTimes"] = int(cols[playConfCols])  # 重新挑战次数
            one["addition"] = float(cols[playConfCols + 1])  # 积分加成

        if cols[openRangeConfCols] is not None:
            config["openTimeRange"].extend([str(cols[openRangeConfCols]), str(cols[openRangeConfCols + 1])])  # 开始时间、结束时间

        if cols[fireConfCols] is not None:  # 开火，技能使用次数
            config["fireCount"] = json.loads(cols[fireConfCols])

        if cols[feeConfCols] is not None:   # 报名费
            config["fee"] = json.loads(cols[feeConfCols])

        if cols[pointConfCols] is not None:
            config["pointRewards"].append(
                {"point": int(cols[pointConfCols]), "rewards": json.loads(cols[pointConfCols + 1])})

        if cols[groupConfCols] is not None:  # 任务鱼、数量、积分
            config["group"].setdefault(str(cols[groupConfCols + 3]), [])
            config["group"][str(cols[groupConfCols + 3])].append(int(cols[groupConfCols + 1]))
            config["target"][str(cols[groupConfCols + 1])] = {"count": int(cols[groupConfCols + 4]),
                                                              "point": int(cols[groupConfCols + 5])}

        if cols[fakeDataConfCols] is not None:  # 假数据数量、最低积分、最高积分
            config["robotData"].append({
                "count": int(cols[fakeDataConfCols + 1]),
                "points": [int(cols[fakeDataConfCols + 2]), int(cols[fakeDataConfCols + 3])]
            })

        if cols[surpassDataCols] is not None:  # 名次
            config["surpassTarget"].append(int(cols[surpassDataCols]))

        if cols[gunMultiAdditionCols] is not None:
            one = collections.OrderedDict()
            config["gunMultiAddition"].append(one)
            one["rangeList"] = [int(cols[gunMultiAdditionCols]), int(cols[gunMultiAdditionCols + 1])]   # 炮倍率范围
            one["addition"] = float(cols[gunMultiAdditionCols + 2])                                     # 炮倍率加成

        if cols[gunMultiAdditionCols] is not None:
            # 阶段积分奖励
            config["stageInfo"].append({"point": int(cols[stageInfoCols]), "rewards": json.loads(cols[stageInfoCols + 1])})

    result = json.dumps(config, indent=4, ensure_ascii=False)
    result = re.sub(r"\\\\n", r"\\n", result)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "grandPrix_config, end"


def getWorkBook(filename="newfish_common.xlsm"):
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
            print "=========== export ", confFunc.__name__, " failed ! ", e, traceback.format_exc()
            err_queue.put((confFunc.__name__ + "_" + str(arg), traceback.format_exc()))


# 配置列表
config_list = [
    (multi_lang_text, None),
    (drop_config, None),
    # (activity_config, None),
    (skill_config, None),
    (lucky_tree_conf, None),
    (chest_config, None),
    (chest_drop_config, None),
    (item_config, None),
    # (item_config, 26882),
    (store_config, None),
    # (store_config, 26882),
    (time_limited_store_config, None),
    (exchange_store_config, None),
    (piggy_bank_config, None),
    (checkin_config, None),
    (vip_config, None),
    (treasure_config, None),
    (main_quest_config, None),
    (daily_quest_config, None),
    (gift_abctest_config, None),
    (gift_config, None),
    (gift_config, 25794),
    # (gift_config, 25598),
    (share_config, None),
    (user_level_config, None),
    (honor_config, None),
    (achievement_config, None),
    (lottery_pool_config, None),
    (ring_lottery_pool_config, None),
    (grandPrix_config, None),
]

if __name__ == "__main__":
    TestConfPath = ""
    RealeaseConfPath = ""
    print "begin"
    t1 = int(time.time())
    ServerPath = '/../../../../../../wx_superboss/trunk/xxfish_dev/config37/game/44'  # 默认练习路径
    if len(sys.argv) > 1 and sys.argv[1] == "-h":
        ServerPath = "/../../../../../../server/newfish-py/wechat/xxfish_test/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-l":
        ServerPath = "/../../../../../../gameServer/tygame-newfish/wechat/xxfish_test/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-t":
        ServerPath = "/../../../../../../../gameServer/newfish-py/wechat/xxfish_release/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-k":
        ServerPath = "/../../../../../../xxfish_dev/config37/game/44"
        TestConfPath = r".\..\..\..\..\..\..\xxfish_dev\config37\game\44"
        RealeaseConfPath = r".\..\..\..\..\..\..\xxfish_release\config37\game\44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-z":
        ServerPath = "/../../../../xxfish_dev/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-c":
        ServerPath = "/../../../../../../xxfish_test/config37/game/44"
        TestConfPath = r".\..\..\..\..\..\..\xxfish_test\config37\game\44"
        RealeaseConfPath = r".\..\..\..\..\..\..\xxfish_release\config37\game\44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-b":
        ServerPath = "/../../../../../../xxfish_test/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == '-d':
        ServerPath = '/../../../../../../xxfish_dev/config37/game/44'
    elif len(sys.argv) > 1 and sys.argv[1] == "-g":
        ServerPath = "/../../fishwx/xxfish_dev/config37/game/44"
    else:
        ServerPath = '/../../../../../../wx_superboss/trunk/xxfish_dev/config37/game/44'  # 默认练习路径

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