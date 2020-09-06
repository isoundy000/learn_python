#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/9/6
"""
Created by lichen on 17/4/25.
mergingFishGroup：合并前鱼阵文件（文件数量过多，避免客户端读取时间过长）
mergedFishGroup：合并后鱼阵文件
通过该脚本把mergingFishGroup中的鱼阵文件，按照合并类型，合并生成新的鱼阵文件并导出到mergedFishGroup目录下
"""

import os
import json
import copy
import traceback
from collections import OrderedDict
import platform

# 需要合并的鱼阵
needMergeGroupName = ["call_", "boss_", "coupon_", "chest_", "red_",
"activity_", "random_", "rboss_", "buffer_", "multiple", "share_", "newbie",
"group_", "tide_", "atide_", "atide2_", "rainbow_", "terror_", "autofill_",
"grandprix_", "superboss_", "tuition_", "superbossborn_", "superbossfast_",
"platter_", "shoal_", "minigame_"]

# 分渔场合并类型
fishPoolGroupName = ["group_", "tide_", "atide_", "atide2_", "rainbow_", "tuition_"]


def getResourcePath(fileName):
    """
    取得当前文件下某一个资源的绝对路径
    """
    cpath = os.path.abspath(__file__)
    cpath = os.path.dirname(cpath)
    fpath = cpath + os.path.sep + fileName
    return fpath


def mergeFishGroup():
    br = "\r\n"
    if platform.system() == "Windows":
        br = "\n"
    groupsPath = getResourcePath("mergingFishGroup")
    outJson = OrderedDict()
    for fileName in sorted(os.listdir(groupsPath)):
        abstractFilePath = os.path.join(groupsPath, fileName)
        isOK = False
        for groupName in needMergeGroupName:
            if groupName in abstractFilePath:
                isOK = True
        if not os.path.isfile(abstractFilePath) or not isOK:
            continue
        outJson[fileName] = {}
        outJson[fileName]["id"] = fileName
        outJson[fileName]["fishes"] = []
        with open(abstractFilePath, "r") as fHandle:
            try:
                lines = fHandle.readlines()
                for i in range(len(lines)):
                    line = lines[i]
                    if i == 0:
                        outJson[fileName]["totalTime"] = float(lines[i])
                    else:
                        line.strip()
                        if len(line) == 0:
                            continue
                        fields = line.split("|", 4)
                        if platform.system() != "Windows":
                            print fields, abstractFilePath
                        fishType = int(fields[0])
                        enterTime = "%.2f" % float(fields[1])
                        exitTime = "%.2f" % float(fields[2])
                        path = int(fields[3])
                        if len(fields) > 4:
                            extends = str(fields[4]).strip()
                            fish = [fishType, enterTime, exitTime, path, extends]
                        else:
                            fish = [fishType, enterTime, exitTime, path]
                        outJson[fileName]["fishes"].append(fish)
            except Exception as e:
                print abstractFilePath
                raise

    fishGroupMap = OrderedDict()
    fishGroupConfig = copy.deepcopy(outJson)
    for fileName in fishGroupConfig:
        for groupName in needMergeGroupName:
            if fileName.startswith(groupName):
                mergedFileName = fileName.split("_")[0]
                if groupName in fishPoolGroupName:
                    mergedFileName = groupName + fileName.split("_")[1]
                fishGroupMap.setdefault(mergedFileName, []).append(fishGroupConfig[fileName])

    outFilePath = os.path.split(os.path.realpath(__file__))[0] + "/mergedFishGroup/"
    for fishGroupName in fishGroupMap:
        with open(outFilePath + fishGroupName, "w+") as fHandle:
            fishGroups = fishGroupMap[fishGroupName]
            for fishGroupInfo in fishGroups:
                fishes = fishGroupInfo["fishes"]
                totalTime = fishGroupInfo["totalTime"]
                groupId = fishGroupInfo["id"]
                fHandle.write("#%s%s" % (groupId, br))
                fHandle.write("%.2f%s" % (totalTime, br))
                for fish in fishes:
                    fHandle.write(str("|".join(map(str, fish)) + br))


if __name__ == "__main__":
    print "begin"
    mergeFishGroup()
    print "successfully"