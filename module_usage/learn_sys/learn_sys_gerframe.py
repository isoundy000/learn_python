#!/usr/bin/env python
# -*- coding:utf-8 -*-

# python之sys._getframe() 用于查看函数被什么函数调用以及被第几行调用及被调用函数所在文件

import sys
def get_cur_info():
    print(sys._getframe().f_code.co_filename)  # 当前文件名，可以通过__file__获得
    print(sys._getframe(0).f_code.co_name) # 当前函数名
    print(sys._getframe(1).f_code.co_name)  # 调用该函数的函数名字，如果没有被调用，则返回<module>
    print(sys._getframe(0).f_lineno) #当前函数的行号
    print(sys._getframe(1).f_lineno) # 调用该函数的行号