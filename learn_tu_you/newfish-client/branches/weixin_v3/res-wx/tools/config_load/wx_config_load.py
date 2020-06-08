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
    # # (item_config, None),
    # # (item_config, 26312),
    # # (item_config, 26760),
    # # (item_config, 26882),
    # # (store_config, None),
    # # (store_config, 25598),
    # # (store_config, 25794),
    # # (store_config, 25840),
    # # (store_config, 26120),
    # # (store_config, 26121),
    # # (store_config, 26122),
    # # (store_config, 26312),
    # # (store_config, 26760),
    # # (store_config, 26882),
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
    # (grandPrix_config, None),
    # (bigPrize_config, None),
    # (compAct_config, None),
    # # (checkin_config, None),
    (drop_config, None),
    (fish_config, None),
    (match_fish_config, None),
    # (weapon_config, None),
    # (ulevel_config, None),
    # (skill_grade_config, None),
    # (skill_star_config, None),
    # # (main_quest_config, None),
    # # (daily_quest_config, None),
    # (chest_config, None),
    # (chest_drop_config, None),
    # (cmptt_task_config, None),
    # (ncmptt_task_config, None),
    # (bonus_task_config, None),
    # (guide_task_config, None),
    # (probability_config, None),
    # (dynamic_odds_config, None),
    # (lottery_pool_config, None),
    # # (gift_config, None),
    # # (gift_config, 25794),
    # # (gift_config, 25598),
    # # (gift_config, 26120),
    # # (gift_config, 26121),
    # # (gift_config, 26122),
    # (item_drop_config, None),
    # # (vip_config, None),
    # (fixed_multiple_fish, None),
    # (call_multiple_fish, None),
    # (fishBonus_config, None),
    # (match_multiple_fish, None),
    # # (achievement_config, None),
    # # (honor_config, None),
    # (weaponPowerRate_config, None),
    # (gunskin_config, None),
    # (gunskin_config, 26312),
    # (gunskin_config, 26760),
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