# -*- coding=utf-8 -*-
"""
提取出csd中的中文文本
origin_chinese: csd中的原始中文文本
duplicate_removal_chinese: 去重后的csd中的中文文本
last_chinese: 上次已翻译的中文文本
diff_chinese: 本次新增的中文文本
"""
import os
import glob
import time
import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

path = os.path.dirname(os.path.abspath(__file__))

def readFile(file_name):
    with open(file_name, 'r') as f:
        content = f.read()
        str_content = 'LabelText="'
        startIndex = content.find(str_content, 0)
        count = 0
        target_content = ''
        while startIndex != -1:
            count = count+1
            last_index = content.find('"', startIndex + len(str_content))
            cur_str = content[startIndex + len(str_content):last_index]
            target_content = target_content + '\n' + cur_str
            startIndex = content.find('LabelText="', last_index)
        print(count)
        return target_content


if len(sys.argv) != 2:
    print "Please input csd path"
    exit()
dirname = sys.argv[1]
print(dirname)
if os.path.isdir(dirname):
    with open(path + '/origin_chinese.txt', 'w') as f:
        for (thisdir, subdir, fileshere) in os.walk(dirname):
            for filename in fileshere:
                if filename.endswith('.csd'):
                    fullname = os.path.join(thisdir, filename)
                    target_content = readFile(fullname)
                    print('file name: '+fullname)
                    print(''+target_content)
                    f.write(target_content)


def duplicateRemoval(dirname, file_name="/origin_chinese.txt", target_file_name="/duplicate_removal_chinese.txt", 
                     last_file_name="/last_chinese.txt", diff_file_name="/diff_chinese.txt"):
    """
    origin_chinese: csd中的中文文本
    duplicate_removal_chinese: 去重后的csd中的中文文本
    last_chinese: 上次已翻译的中文文本
    diff_chinese: 本次新增的中文文本
    去除重复行               
    """
    print "***duplicate removal begin!"
    original_list = [""]
    newlist = [""]
    newtxt = ""
    with open(dirname + file_name, "r+") as f:
        original_list = f.readlines()
        [newlist.append(i) for i in original_list if i not in newlist and is_contains_chinese(unicode(i, "utf-8"))]
        newtxt = "".join(newlist)
    with open(dirname + target_file_name, "w") as f1:
        f1.write(newtxt)
    if os.path.exists(dirname + last_file_name):
        with open(dirname + last_file_name, "r+") as f:
            lastlist = f.readlines()
            difflist = set(newlist) - set(lastlist)
            difftxt = "".join(difflist)
            with open(dirname + diff_file_name, "w") as f1:
                f1.write(difftxt)
    print "***duplicate removal end!"


def is_contains_chinese(strings):
    for _char in strings:
        if _char >= u'\u4e00' and _char <= u'\u9fa5':
            return True
    return False


duplicateRemoval(os.path.dirname(os.path.abspath(__file__)))
