# -*- coding=utf-8 -*-
"""
Created by lichen on 17/2/16.
"""

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
    if ftlog.is_debug():
        ftlog.debug("getGroupConfig, fishGroupPath =", fishGroupPath, "mode =", mode)
    for fileName in os.listdir(groupsPath):
        abstractFilePath = os.path.join(groupsPath, fileName)
        if not os.path.isfile(abstractFilePath):
            continue
        if ftlog.is_debug():
            ftlog.debug("load group:", fileName, mode)
        fHandle = open(abstractFilePath, "r")
        lines = fHandle.readlines()
        isTotalTime = False
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith("#"):
                line = line.strip()
                fileName = line.split("#")[1]
                outJson[fileName] = {}
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
                    "exitTime": float(fields[2])
                })
        fHandle.close()
    return outJson

