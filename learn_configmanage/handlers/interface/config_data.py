#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from handlers.basehandler import BaseHandler
from common.configmanager import ConfigManager


class GetWebInfo(BaseHandler):

    def get(self):
        '''
        获取网站信息
        :return:
        '''
        data = {'title': '侯广东', 'platform_name': '广东渠道', 'platform_group': '广东游戏'}
        data['title'] = ConfigManager.getvalue('WEB_INFO', 'title')
        data['platform_name'] = ConfigManager.getvalue('WEB_INFO', 'platform')
        data['platform_group'] = ConfigManager.getvalue('WEB_INFO', 'platform_group')
        return_data = {'status': 'ok', 'data': data}
        self.write(return_data)


def cdkey_info():
    '''
    获取cdkey的ip和port
    :return:
    '''
    ip = ConfigManager.getvalue('CDKEY', 'ip')
    port = ConfigManager.getvalue('CDKEY', 'port')
    return {'ip': ip, 'port': port}