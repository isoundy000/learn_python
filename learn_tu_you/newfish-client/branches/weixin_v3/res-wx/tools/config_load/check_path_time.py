# -*- coding=utf-8 -*-
"""
检查鱼阵文件中每条鱼的存活时间是否和前端的path文件中的路径时间一致
使用步骤：
1、客户端通过工具把res-wx/newfish/config_src/path文件生成与之对应的pathTime文件，替换该目录下的pathTime文件
2、执行脚本，会检查"fishGroupFolderPaths"目录下的所有鱼阵文件是否存在问题
3、输出结果到"outputPath"文件
"""
import time
import os
import os.path
import re
import json
import sys
from decimal import *
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding("utf-8")

# 鱼阵文件夹路径
fishGroupFolderPaths = ["./TracksNew/", "./fishGroupMerge/mergingFishGroup/"]
# path文件地址
pathFilePath = "./pathTime"
# 结果文件地址
outputPath = "./invalid_group_" + time.strftime("%H-%M-%S", time.localtime(time.time()))
# 鱼阵文件绝对路径
fishGroupsPath = []
# 正确的pathTime对应关系
validPathTime = {}
# 存在无效path的鱼阵
invalidPathGroup = {}
# 格式化时间的鱼阵
formatTimeGroup = {}
# 修改pathTime的鱼阵
pathTimeGroup = {}
# 修改totalTime的鱼阵
totalTimeGroup = []
# 无效且最终被修复的鱼阵
invalidGroup = []


def getFishPathTime():
    print "--- 获取鱼阵的路径 ---"
    for path in fishGroupFolderPaths:
        for file in os.listdir(path):
            filePath = path + file.decode("utf-8")
            if filePath.find(".json") >= 0 or filePath.find(".py") >= 0:
                continue
            with open(filePath, "r") as file:
                data = file.readlines()
                for i, line in enumerate(data):
                    data = line.split("|")
                    if i > 0 and len(data) > 1:
                        fishGroupsPath.append(filePath)
                        break


def getExportPathTime():
    print "--- 获取导出的pathTime ---"
    with open(pathFilePath, "r") as pathFile:
        allPaths = pathFile.readlines()
        for path in allPaths:
            data = path.split("|")
            validPathTime[data[0]] = Decimal(data[1])


def repairFishGroup():
    print "--- 校验并修复鱼阵pathTime ---"
    for filePath in fishGroupsPath:
        file = open(filePath, "r")
        allData = file.readlines()
        ogiginTotalTime = 0
        newTotalTime = 0
        newData = []
        isRepair = False
        for i, line in enumerate(allData):
            data = line.strip().split("|")
            if i == 0:
                ogiginTotalTime = Decimal(line.replace("\r\n", ""))
            if len(data) > 1:
                pathName = data[3].replace("\r\n", "")
                endTime = Decimal(data[2])
                time = endTime - Decimal(data[1])
                if validPathTime.get(pathName) is None:
                    print "--- 不存在的path: %s filePath: %s ---" % (pathName, filePath)
                    invalidPathGroup[filePath] = pathName
                    continue
                pathTime = validPathTime[pathName]
                # 路径时间不对
                if "%.2f" % pathTime != "%.2f" % time and pathTime != 0:
                    endTime = Decimal(data[1]) + pathTime
                    data[2] = "%.2f" % endTime
                    print "--- pathTime modify %s ---" % filePath
                    pathTimeGroup[filePath] = pathName
                    isRepair = True
                # 时间小数点位数格式化
                if len(data[1].split(".")[-1]) != 2:
                    data[1] = "%.2f" % float(data[1])
                    print "--- enterTime modify %s ---" % filePath
                    formatTimeGroup[filePath] = pathName
                    isRepair = True
                if len(data[2].split(".")[-1]) != 2:
                    data[2] = "%.2f" % float(data[2])
                    print "--- endTime modify %s ---" % filePath
                    formatTimeGroup[filePath] = pathName
                    isRepair = True
                if isRepair:
                    line = "|".join(data) + "\r\n"
                # 计算总时间（鱼阵中最后一条鱼的退出时间）
                newTotalTime = max(newTotalTime, endTime)
            newData.append(line)
        file.close()
        if filePath not in invalidPathGroup:
            # 总时间不对
            if str(newTotalTime) != str(ogiginTotalTime):
                newData[0] = newData[0].replace(str(ogiginTotalTime), "%.2f" % newTotalTime)
                print "--- totalTime modify %s ---" % filePath
                totalTimeGroup.append(filePath)
                isRepair = True
            # 已修复的鱼阵
            if isRepair:
                invalidGroup.append(filePath)
                file = open(filePath, "w")
                file.writelines(newData)
                file.close()

    if invalidGroup or invalidPathGroup:
        print "--- 鱼阵存在错误！查看文件: %s ---" % outputPath
        outputJson = OrderedDict()
        outputJson["invalidGroup"] = invalidGroup
        outputJson["invalidPathGroup"] = invalidPathGroup
        outputJson["pathTimeGroup"] = pathTimeGroup
        outputJson["totalTimeGroup"] = totalTimeGroup
        outputJson["formatTimeGroup"] = formatTimeGroup
        invalidFishGroupFile = open(outputPath, "w")
        invalidFishGroupFile.write(json.dumps(outputJson, indent=4))
        invalidFishGroupFile.close()
    else:
        print "--- 鱼阵正确！---"


if __name__ == "__main__":
    getFishPathTime()
    getExportPathTime()
    repairFishGroup()
