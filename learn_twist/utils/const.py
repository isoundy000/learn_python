# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 18:23

@author: houguangdong
'''


class ConstError(Exception):
    pass


class _const(object):
    """定义常量
    """

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise ConstError
        else:
            self.__dict__[key] = value


const = _const()

const.MAX_CONNECTION = 2000
const.TIME_OUT = 1000 * 60  # 秒
const.struct_fmt = '!sssss3I'