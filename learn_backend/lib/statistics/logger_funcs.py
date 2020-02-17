#!/usr/bin/env python
# -*- coding:utf-8 -*-


'''
def module_funcname(env, args, result_data):
    """# module_funcname: module中的funcname接口的统计方法, 此函数命名规则：views中模块名_函数名
                            比如views.cards.open的统计方法命名为：cards_open
    args:
        env:
        args: 请求参数
        return_data: 比如views层函数处理后的result_data,
    returns:
        0    ---
        data:     需要记录的结果
    """
    data={}
    return data

'''
def gacha_get_gacha(env, args, data):
    return {'new_card': data['new_card']}