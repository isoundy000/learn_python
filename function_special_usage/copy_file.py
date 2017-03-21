# -*- coding: utf-8 -*-
'''
Created on 2017年3月21日

@author: ghou
'''
# 2 把json字典写入一个文件中
# f.write(json.dumps(comments))

# copy 文件
def copy_file(source_path, target_path):
    import shutil
    for parent,dirnames,filenames in os.walk(source_path):
        for filename in filenames:
            if not filename.endswith(".rc"): 
                continue
            file_path=parent  + "\\" + filename
            new_path = target_path + "\\" + filename
            shutil.copyfile(file_path, new_path)