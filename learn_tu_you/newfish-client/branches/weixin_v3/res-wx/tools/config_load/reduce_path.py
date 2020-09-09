# -*- coding: utf-8 -*-
"""
作用：将path文件中没用的鱼阵路径删除并生成新的路径文件：newpath
脚本执行后会获取到该脚本所在目录下的所有鱼阵的路径ID，然后对其去重
通过与原始path文件对比，只保留用到的路径ID，精简原始path文件
最终生成的路径文件名为： newpath, 和path文件在同一目录
使用：
    1、将该脚本放在../weixin/res-wx/newfish/config/路径下
    2、修改final_pathfile为自己PC上的path文件的路径
    3、python fishgroup_id.py 执行
"""


import sys
import os
import time

path = os.path.dirname(os.path.abspath(__file__))
target_filename = "/target_file.txt"             # 去重前的路径id文件
new_path = "newpath"                             # 生成的新的path文件名
final_pathfile = "/Users/tugame/Desktop/mutian/weixin/res-wx/newfish/config_src/"   #path文件的路径

def get_filelist(path):
    """
    获取该路径下所有文件
    """
    fileList = []
    for home, dirs, files in os.walk(path):
        for filename in files:
            if not filename.endswith('.json'):
                fileList.append(os.path.join(home, filename))
    return fileList

def get_path_id():
    """
    获取鱼阵中路径ID
    """
    fileList = get_filelist(path)
    print "共%d个文件" % len( fileList)
    f1 = open(path + target_filename,"w+")
    for file in fileList:
        with open(file, "r+") as f:
            original_list = f.readlines()
            for original in original_list:
                try:
                    path_id = original.split("|")[-1]
                    f1.write(path_id)
                except Exception as e:
                    print "error"

def duplicateRemoval(path=path, target_filename=target_filename):
    """
    对ID去重             
    """
    original_list = [""]
    newlist = [""]
    newtxt = ""
    with open(path + target_filename, "r+") as f:
        original_list = f.readlines()
        for i in original_list:
            if not i in newlist and i.find("#") < 0 and i.find(".") < 0:
                newlist.append(i.replace("\r\n",""))
    return newlist

def new_path_file(newpath=final_pathfile):
    """
    生成新鱼阵文件
    """
    if os.path.exists(final_pathfile+new_path):
        os.remove(final_pathfile+new_path)
    original_list = [""]
    newlist = [""]
    newtxt = ""
    idlist = duplicateRemoval()
    print idlist
    f1 = open(final_pathfile + new_path,"a+")
    with open(final_pathfile + "path", "r+") as f:
        original_list = f.readlines()
        for original in original_list:
            try:
                path_id = original.split("|")[0]
                if original not in newlist and path_id in idlist:
                    newlist.append(original)
                newtxt = "".join(newlist)
            except Exception as e:
                print "error"
        f1.write(newtxt)

if __name__ =="__main__":
    print "begin...运行完大概需要一分半"
    begintime = int(time.time())
    if os.path.exists(path+target_filename):
        os.remove(path+target_filename)
    get_path_id()
    duplicateRemoval()
    new_path_file()
    print "end..."
    endtime = int(time.time())
    print "共耗时：%d 秒" % (endtime - begintime)


