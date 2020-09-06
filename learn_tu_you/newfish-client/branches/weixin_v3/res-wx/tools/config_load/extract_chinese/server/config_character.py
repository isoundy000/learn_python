# -*- coding: utf-8 -*-
"""
导出../xxfish_test/config37/game/44 目录下所有json文件中的中文文本
作用：找到后端配置中的中文文本，用于多语言
"""

import sys
import os


path = os.path.dirname(os.path.abspath(__file__))
target_filename = "/target_file.txt"          # 去重前的文件
middle_filename = "/middle_file.txt"
filename = "/final_file.txt"                 # 去重后的最终文件

def get_filelist(dir):
    """
    获取该路径下所有json文件
    """
    fileList = []
    for path, dirs, files in os.walk(configPath):
        if isIgnorePath(path):
            continue
        for filename in files:
            if filename.endswith(".json"):
                fileList.append(os.path.join(path, filename))
    return fileList


def isIgnorePath(path):
    ignorePaths = ["robot", "idCard", "iploc", "game/6", "game5", "multiLangText"]
    for _p in ignorePaths:
        if _p in path:
            return True
    return False


def is_contains_chinese(strings):
    """
    是否包含中文字符
    """
    strings = strings.decode("utf8", "ignore")
    for _char in strings:
        if _char >= u"\u4e00" and _char <= u"\u9fa5":
            return True
    return False


def duplicateRemoval(path, target_filename=target_filename, middle_filename=middle_filename):
    """
    去除重复行               
    """
    original_list = [""]
    newlist = [""]
    newtxt = ""
    with open(path + target_filename, "r+") as f:
        original_list = f.readlines()
        [newlist.append(i) for i in original_list if not i in newlist and is_contains_chinese(i)]
        newtxt = "".join(newlist)
        f1 = open(path + middle_filename,"w")
        f1.write(newtxt)


def mergeJsonTotxt(configPath):
    fileList = get_filelist(configPath)
    print "共%d个json文件" % len( fileList)
    f1 = open(path + target_filename,"w+")
    for file in fileList:
        with open(file, "r+") as f:
            original_list = f.readlines()
            for original in original_list:
                if is_contains_chinese(original):
                    original_split_list = original.split(":", 1)
                    if len(original_split_list) >= 2:
                        original = original_split_list[1]
                    else:
                        original = original_split_list[0]
                    original = original.strip()
                    endIdx = original.rfind("\"") or original.rfind(",")
                    original = original[:endIdx] + "\n"
                    if original:
                        f1.write(original)
    duplicateRemoval(path)
    with open(path+middle_filename, "r+") as f:
            original_list = f.readlines()
            f1 = open(path+filename, "w")
            for original in original_list:
                original = original.replace("\"", "")
                f1.write(original)
    if os.path.exists(path+middle_filename):
        os.remove(path+middle_filename)

if __name__ =="__main__":
    print "------ merge begin ------"
    if os.path.exists(path+target_filename):
        os.remove(path+target_filename)
    if len(sys.argv) > 1 and sys.argv[1] == "-h":
        ServerPath = "/../../../../../../../../server/newfish-py/wechat/xxfish_test/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-l":
        ServerPath = "/../../../../../../../../gameServer/tygame-newfish/wechat/xxfish_test/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-t":
        ServerPath = "/../../../../../../../../../gameServer/newfish-py/wechat/xxfish_release/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-k":
        ServerPath = "/../../../../../../../../xxfish_test/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-z":
        ServerPath = "/../../../../xxfish_test/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-c":
        ServerPath = "/../../../../../../../../xxfish_test/config37/game/44"
    elif len(sys.argv) > 1 and sys.argv[1] == "-b":
        ServerPath = "/../../../../../../../../xxfish_test/config37/game/44"
    else:
        ServerPath = "/../../../../../../../../../gameServer/hall37/newfish-py/wechat/xxfish_test/config37/game/44"
    configPath = os.path.split(os.path.realpath(__file__))[0] + ServerPath
    mergeJsonTotxt(configPath)
    print "------ merge end ------"







