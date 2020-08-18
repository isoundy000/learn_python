#!/usr/bin/env python
# -*- coding:utf-8 -*-

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
        i = i + 1
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
        i = i + 1
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
        if str(cols[0]) in config:
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
        i = i + 1
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
    print "skill_config1, start"
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
        i = i + 1
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
            config["interval"] = int(cols[5])
            config["rewardCount"] = int(cols[6])
            config["rule"] = str(cols[7])
            config["vipLimit"] = int(cols[8])
            config["maxSkiptimes"] = int(cols[9])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "lucky_tree_conf, end"


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
            if cols[3]:
                one["up_skill"] = 1
            one["actions"] = []
            one["name"] = str(cols[4])
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
                    config[tab]["shop"] = str(cols[_idx + 22])

        if cols[pearl_store_num]:
            one = collections.OrderedDict()
            config["pearlStore"][str(cols[pearl_store_num])] = one
            one["name"] = json.loads(cols[pearl_store_num + 1])
            one["itemId"] = int(cols[pearl_store_num + 2])
            one["count"] = json.loads(cols[pearl_store_num + 3])
            one["order"] = int(cols[pearl_store_num + 4])
            one["price"] = int(cols[pearl_store_num + 5])
            one["price_direct"] = int(cols[pearl_store_num + 6])
            one["price_diamond"] = int(cols[pearl_store_num + 7])
            one["additionVip"] = int(cols[pearl_store_num + 8])
            one["tag"] = int(cols[pearl_store_num + 9])
            one["addition"] = json.loads(cols[pearl_store_num + 10])
            if cols[pearl_store_num + 11] == "\"\"":
                one["pic"] = ""
            else:
                one["pic"] = str(cols[pearl_store_num + 11])
            one["buyType"] = str(cols[pearl_store_num + 12])
            one["otherBuyType"] = json.loads(cols[pearl_store_num + 13])

        if cols[gun_skin_num]:
            one = collections.OrderedDict()
            config["gunSkinStore"][str(cols[gun_skin_num])] = one
            one["name"] = str(cols[gun_skin_num + 1])
            one["itemId"] = int(cols[gun_skin_num + 2])
            one["count"] = int(cols[gun_skin_num + 3])
            one["order"] = int(cols[gun_skin_num + 4])
            if cols[gun_skin_num + 5] is not None:
                one["vip"] = int(cols[gun_skin_num + 5])
            if cols[gun_skin_num + 6] != "\"\"":
                one["desc"] = str(cols[gun_skin_num + 6])
            else:
                one["desc"] = ""
            one["price"] = int(cols[gun_skin_num + 7])
            one["discountPrice"] = json.loads(cols[gun_skin_num + 8])
            one["tag"] = int(cols[gun_skin_num + 9])
            one["addition"] = json.loads(cols[gun_skin_num + 10])
            if cols[gun_skin_num + 11] != "\"\"":
                one["pic"] = str(cols[gun_skin_num + 11])
            else:
                one["pic"] = ""
            one["buyType"] = str(cols[gun_skin_num + 12])

        if cols[robbery_store_num]:
            one = collections.OrderedDict()
            config["bulletStore"]["hall37"][str(cols[robbery_store_num])] = one
            one["name"] = str(cols[robbery_store_num + 1])
            one["itemId"] = int(cols[robbery_store_num + 2])
            one["count"] = int(cols[robbery_store_num + 3])
            one["order"] = int(cols[robbery_store_num + 4])
            one["price"] = int(cols[robbery_store_num + 5])
            one["price_direct"] = int(cols[robbery_store_num + 6])
            one["price_diamond"] = int(cols[robbery_store_num + 7])
            one["tag"] = int(cols[robbery_store_num + 8])
            one["addition"] = json.loads(cols[robbery_store_num + 9])
            if cols[robbery_store_num + 10] != "\"\"":
                one["pic"] = str(cols[robbery_store_num + 10])
            else:
                one["pic"] = ""
            one["buyType"] = str(cols[robbery_store_num + 11])
            one["robberyBonus"] = int(cols[robbery_store_num + 12])
            one["vipAddition"] = json.loads(cols[robbery_store_num + 13])

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
    wb = getWorkBook()
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
        one["vipPresentCount:1137"] = int(cols[1])
        one["vipPresentCount:1193"] = int(cols[2])
        one["vipPresentCount:1194"] = int(cols[3])
        one["vipPresentCount:1426"] = int(cols[4])
        one["vipPresentCount:1408"] = int(cols[5])
        one["vipPresentCount:1429"] = int(cols[6])
        one["vipPresentCount:1430"] = int(cols[7])
        one["vipPresentCount:1431"] = int(cols[8])
        one["vipReceiveCount:1194"] = int(cols[9])
        one["vipReceiveCount:1193"] = int(cols[10])
        one["vipExp"] = int(cols[expStartIdx])
        one["freeRouletteTimes"] = int(cols[expStartIdx + 1])
        one["dropPearlTotalCount"] = int(cols[expStartIdx + 2])
        one["dropPearlRatioLimit"] = cols[expStartIdx + 3]
        one["vipDesc"] = unicode(cols[expStartIdx + 4]) or ""
        one["vipGift"] = json.loads(cols[expStartIdx + 5])
        one["originalPrice"] = int(cols[expStartIdx + 6])
        one["price"] = int(cols[expStartIdx + 7])
        one["pearlMultiple"] = float(cols[expStartIdx + 8])
        one["matchAddition"] = float(cols[expStartIdx + 9])
        one["setVipShow"] = int(cols[expStartIdx + 10])
        one["almsRate"] = float(cols[expStartIdx + 11])
        one["autoSupply:101"] = int(cols[expStartIdx + 12])
        one["initLuckyValue:44102"] = int(cols[expStartIdx + 13])
        one["inviterReward"] = json.loads(cols[expStartIdx + 14])
        one["contFire"] = int(cols[expStartIdx + 15])
        one["enableChat"] = int(cols[expStartIdx + 16])
        one["limitChatTip"] = unicode(cols[expStartIdx + 17] or "")
        one["convert1137ToDRate"] = json.loads(cols[expStartIdx + 18])
        one["convert1429ToDRate"] = json.loads(cols[expStartIdx + 19])
        one["convert1430ToDRate"] = json.loads(cols[expStartIdx + 20])
        one["convert1431ToDRate"] = json.loads(cols[expStartIdx + 21])
        one["grandPrixFreeTimes"] = int(cols[expStartIdx + 22])
        one["grandPrixAddition"] = float(cols[expStartIdx + 23])
        one["checkinRechargeBonus"] = int(cols[expStartIdx + 24])

    result = json.dumps(config, indent=4, ensure_ascii=False)
    result = re.sub(r"\\\\n", r"\\n", result)
    outHandle = open(outPath, "w")
    outHandle.write(result)
    outHandle.close()
    print "vip_config, end"


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



def honor_config():
    """称号配置"""
    print "honor_config start"
    outPath = getOutPath("honor")
    ws = getWorkBook("achievement.xlsx").get_sheet_by_name("Honor")
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
    (activity_config, None),
    (skill_config, None),
    (lucky_tree_conf, None),
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
    (time_limited_store_config, None),
    (exchange_store_config, None),
    # (piggy_bank_config, None),
    # (checkin_config, None),
    (vip_config, None),
    # (treasure_config, None),
    # (main_quest_config, None),
    # (daily_quest_config, None),
    (gift_abctest_config, None),
    (gift_config, None),
    (gift_config, 25794),
    (gift_config, 25598),
    (gift_config, 26120),
    (gift_config, 26121),
    (gift_config, 26122),
    # (share_config, None),
    # (user_level_config, None),
    (honor_config, None),
    (achievement_config, None),
    # (lottery_pool_config, None),
    # (ring_lottery_pool_config, None)
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