#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/20 22:37
# @version: 0.0.1
# @Author: houguangdong
# @File: doc.py
# @Software: PyCharm
from twisted.python import log
import struct


class DataPackError(Exception):
    """An error occurred binding to an interface"""

    def __str__(self):
        s = self.__doc__
        print(s, '11111111111111', self.__doc__)
        if self.args:
            s = '%s: %s' % (s, ' '.join(self.args))
        s = '%s.' % s
        return s


def main():
    try:
        ud = struct.unpack('!ih', b'dddd')
    except DataPackError as de:
        print(de, '00000000000000')
        log.err(de)
        # return {'result': False, 'command': 0, 'length': 0}


if __name__ == '__main__':
    main()