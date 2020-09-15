# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/9/4.
装饰器模块
"""

import sys

from freetime.util import log as ftlog


def findCaller(func):
    """
    显示调用栈
    """
    def wrapper(*args, **kwargs):
        if ftlog.is_debug():
            f = sys._getframe()
            filename = f.f_back.f_code.co_filename
            lineno = f.f_back.f_lineno
            name = f.f_back.f_code.co_name
            ftlog.debug("######################################")
            ftlog.debug("File \"%s\", line %s, in %s" % (filename, lineno, name))
            ftlog.debug("the passed args is", args, kwargs)
            ftlog.debug("######################################")
        func(*args, **kwargs)
    return wrapper