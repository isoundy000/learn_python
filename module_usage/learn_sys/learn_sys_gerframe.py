#!/usr/bin/env python
# -*- coding:utf-8 -*-

# python之sys._getframe() 用于查看函数被什么函数调用以及被第几行调用及被调用函数所在文件

import os
import sys


def get_cur_info():
    print(sys._getframe().f_code.co_filename)   # 当前文件名，可以通过__file__获得
    print os.path.normcase(sys._getframe().f_code.co_filename)  # 转换path的大小写和斜杠
    print(sys._getframe(0).f_code.co_name)      # 当前函数名
    print(sys._getframe(1).f_code.co_name)      # 调用该函数的函数名字，如果没有被调用，则返回<module>
    print(sys._getframe(0).f_lineno)            # 当前函数的行号
    print(sys._getframe(1).f_lineno)            # 调用该函数的行号
    # 在Linux和Mac平台上，该函数会原样返回path，在windows平台上会将路径中所有字符转换为小写，并将所有斜杠转换为反斜杠。
    print os.path.normcase('c:/windows\\system32\\')


if __name__ == '__main__':
    get_cur_info()