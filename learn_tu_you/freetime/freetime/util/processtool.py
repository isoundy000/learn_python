# coding=UTF-8
'''process tools
'''

__author__ = [
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]

import psutil
import re


def getOneProcessByKeyword(keyword):
    recpl = re.compile(keyword,re.I)
    processList = psutil.process_iter()
    for process in processList:
        try:
            cmdlineStr = " ".join(process.cmdline())
        except:
            continue
        if recpl.search(cmdlineStr):
            return process