#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2


from copy import deepcopy


def cloneData(data):
    '''
    使用JSON的loads和dump克隆一个数据对象
    '''
    return deepcopy(data)
    # try:
    #     return json.loads(json.dumps(data))
    # except:
    #     ftlog.warn('Can not use json copy !! data=' + repr(data))
    #     return deepcopy(data)