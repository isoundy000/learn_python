# -*-coding:utf-8-*-
'''
Created on 2017年8月16日

@author: houguangdong
'''
import imp
# imp.get_suffixes()
# 返回3元组列表(suffix, mode, type), 获得特殊模块的描述.suffix为文件后缀名;mode为打开文件模式; type为文件类型, 1代表PY_SOURCE, 2代表PY_COMPILED, 3代表C_EXTENSION
print imp.get_suffixes()
# [('.x86_64-linux-gnu.so', 'rb', 3), ('.so', 'rb', 3), ('module.so', 'rb', 3), ('.py', 'U', 1), ('.pyc', 'rb', 2)]
# imp.find_module(name[, path])
# 如果path为空,则按照sys.path路径搜索模块名, 返回三元组(file, pathname, description).file为刚打开的模块文件, pathname为模块的路径, description为imp.get_suffixes()返回的元组.
# 如果模块为包,file返回None, pathname为包路径, description返回的type为PKG_DIRECTORY.
# find_module不会处理层次结构的模块名(带’.’号的模块名module.name1.name2).
# “path”必须是一个列表.
print imp.find_module('os')
# (<open file '/usr/lib/python2.7/os.py', mode 'U' at 0x7fdeebd53a50>, '/usr/lib/python2.7/os.py', ('.py', 'U', 1))
# imp.load_module(name, file, pathname, description)
# 加载一个被find_module找到的模块. 如果模块已经被加载, 等同于reload().
# 当模块是包或者不从文件加载时, file和pathname可以是None和”.
# 成功加载后返回一个模块对象,否则抛出 ImportError异常.
# 需要自己关闭file,最好用try…finally…
# 实例
file1, pathname, desc = imp.find_module('os')
myos = imp.load_module('sep', file1, pathname, desc)
print myos
# <module 'sep' from '/usr/lib/python2.7/os.pyc'>
print myos.getcwd()
# '/home/ydoing/github/autorunner'