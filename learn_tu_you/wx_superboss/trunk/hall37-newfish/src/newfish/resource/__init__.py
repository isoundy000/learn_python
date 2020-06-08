#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/1


import os
import freetime.util.log as ftlog


def getResourcePath(fileName):
    """
    取得当前文件下某一个资源的绝对路径
    """
    cpath = os.path.abspath(__file__)
    cpath = os.path.dirname(cpath)
    fpath = cpath + os.path.sep + fileName
    return fpath


def loadResource(fileName):
    """
    取得当前文件下某一个资源的文件内容
    """
    fpath = getResourcePath(fileName)
    f = open(fpath)
    c = f.read()
    f.close()
    return c


def getGroupConfig(mode=0):
    """
    获取鱼阵配置
    :param mode: 0:经典模式；1:千炮模式
    """
    fishGroupPath = "fish_group" if mode == 0 else "fish_group_m"
    groupsPath = getResourcePath(fishGroupPath)
    outJson = {}
    ftlog.debug("getGroupConfig, fishGroupPath =", fishGroupPath, "mode =", mode)
    for fileName in os.listdir(groupsPath):
        abstractFilePath = os.path.join(groupsPath, fileName)
        if not os.path.isfile(abstractFilePath):
            continue
        ftlog.debug("--------load group:" + fileName)
        fHandle = open(abstractFilePath, "r")
        lines = fHandle.readlines()
        isTotalTime = False
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith("#"):
                line = line.strip()
                fileName = line.split("#")[1]
                outJson[fileName] = {}          # {atide2_44001_1: {"id": "atide2_44001_1", "fishes": [{"fishType": 28050, "enterTime": 15.00. "exitTime": 60.87}, {"fishType": 28050, "enterTime": 15.00. "exitTime": 60.93}, {"fishType": 28050, "enterTime": 17.00. "exitTime": 60.87}], "totalTime": 90.91}}
                outJson[fileName]["id"] = fileName
                outJson[fileName]["fishes"] = []
                isTotalTime = True
                continue
            if isTotalTime:
                outJson[fileName]["totalTime"] = float(lines[i])
                isTotalTime = False
            else:
                line = line.strip()
                if len(line) == 0:
                    continue
                fields = line.split("|")
                outJson[fileName]["fishes"].append({
                    "fishType": int(fields[0]),
                    "enterTime": float(fields[1]),
                    "exitTime": float(fields[2]),
                })
        fHandle.close()
    return outJson