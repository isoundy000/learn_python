#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/9/6
"""
检查鱼阵是否存在无效fishType
根据fish_check.xlsx文件确定各鱼阵文件中fishType范围，筛选出可能存在问题的鱼阵文件
"""

import os
import os.path
import re
import json
import sys
reload(sys)
from openpyxl import load_workbook

# 鱼阵文件夹
fishGroupFolderPath = './mergedFishGroup/'
# 鱼阵有效fishTye文件
validGroupFishTypeFile = './fish_check.xlsx'
# 结果文件保存地址 不合法的
outputPath = './check_result_invalid_fishtype'

print '--- 读取鱼阵有效fishType文件 ---'
configFile = validGroupFishTypeFile
wb = load_workbook(filename=configFile, read_only=True, data_only=True)
ws = wb.get_sheet_by_name("check")
validGroupFishType = {}
i = 0
for row in ws.rows:
    i += 1
    if i < 2:
        continue
    cols = []
    for cell in row:
        cols.append(cell.value)
    validGroupFishType[cols[0]] = json.loads(cols[1])

files = os.listdir(fishGroupFolderPath)

print '--- 检测鱼阵fishType ---'
invalidGroupFishType = {}
for file in files:
    txt_path = fishGroupFolderPath + file.decode('utf-8')
    if txt_path.find('.json') >= 0 or txt_path.find('.py') >= 0:
        continue
    file = open(txt_path, 'r')
    data = file.readlines()

    lastGroup = ''
    for line in data:
        if line.find('#') >= 0:
            lastGroup = line[1:]
            lastGroup = lastGroup.replace('\r\n', '')
            invalidGroupFishType[lastGroup] = []
        elif len(line.split('|')) > 1:
            fishType = int(line.split('|')[0])
            if len(validGroupFishType.get(lastGroup, [])) > 0:
                if fishType not in validGroupFishType.get(lastGroup) and fishType not in invalidGroupFishType[lastGroup]:
                    invalidGroupFishType[lastGroup].append(fishType)

invalidFishGroupFile = open(outputPath, 'w')
line = ''
for k, v in invalidGroupFishType.iteritems():
    if len(v) > 0:
        line = str(k) + ' :' + json.dumps(v) + '\n'
        invalidFishGroupFile.write(line)
invalidFishGroupFile.close()

if line != '':
    print '--- 鱼阵fishType存在错误！查看文件: %s ---' % outputPath
else:
    print '--- 鱼阵fishType正确！---'
