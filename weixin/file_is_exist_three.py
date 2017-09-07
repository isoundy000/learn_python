#-*-coding:utf-8-*-
'''
Created on 2017年9月3日

@author: houguangdong
'''
import os
# 方法1
print os.path.exists('test_file.txt')
print os.path.exists('no_exist_file.txt')
# 判断文件是否存在
print os.path.exists('test_dir')
print os.path.exists('no_exist_dir')
# 只检测文件
print os.path.isfile('test-data')
if os.access('file/path/foo.txt', os.F_OK):
    print 'file path is exist'
if os.access('file/path/foo.txt', os.R_OK):
    print 'file can to read'
if os.access('file/path/foo.txt', os.W_OK):
    print 'file can to write'
if os.access('file/path/foo.txt', os.X_OK):
    print 'file can to execute'

# 方法2
# try:
#     f = open()
#     f.close()
# except FileNotFoundError:
#     print 'file is not found'
# except PermissionError:
#     print 'you no permission'
    
try:
    f = open()
    f.close()
except IOError:
    print 'file'
    
# 3 使用pathlib模块 需要安装这个包
# path = pathlib.Path('path/file')
# print path.exist()
# path1 = pathlib.Path('path/file')
# print path1.is_file()