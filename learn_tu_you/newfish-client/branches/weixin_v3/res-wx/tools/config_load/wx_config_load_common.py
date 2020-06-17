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
    # (multi_lang_text, None),
    # (activity_config, None),
    (skill_config, None),
    # (lucky_tree_conf, None),
    (item_config, None),
    (item_config, 26312),
    (item_config, 26760),
    (item_config, 26882),
    # (store_config, None),
    # (store_config, 25598),
    # (store_config, 25794),
    # (store_config, 25840),
    # (store_config, 26120),
    # (store_config, 26121),
    # (store_config, 26122),
    # (store_config, 26312),
    # (store_config, 26760),
    # (store_config, 26882),
    # (time_limited_store_config, None),
    # (exchange_store_config, None),
    # (piggy_bank_config, None),
    # (checkin_config, None),
    # (vip_config, None),
    # (treasure_config, None),
    # (main_quest_config, None),
    # (daily_quest_config, None),
    # (gift_config, None),
    # (gift_config, 25794),
    # (gift_config, 25598),
    # (gift_config, 26120),
    # (gift_config, 26121),
    # (gift_config, 26122),
    # (share_config, None),
    # (user_level_config, None),
    # (honor_config, None),
    # (achievement_config, None),
    # (lottery_pool_config, None),
    # (ring_lottery_pool_config, None)
]


if __name__ == "__main__":
    TestConfPath = ""
    RealeaseConfPath = ""
    print "begin"
    t1 = int(time.time())
    ServerPath = '/../../../../../../xxfish_test/config37/game/44'  # 默认练习路径
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
        ServerPath = '/../../../../../../xxfish_test/config37/game/44'  # 默认练习路径

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