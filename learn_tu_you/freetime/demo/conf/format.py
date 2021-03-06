#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/29

# Author:        zipxing@hotmail.com
# Created:       2015年04月07日 星期二 16时54分02秒
#
import sys


class JsonFormatter:

    def __init__(self, intend=4, name=""):
        self.name = name
        self.intend = intend
        self.stack = []
        self.obj = None
        self.source = self.get_source(name)
        self.prepare()

    @staticmethod
    def json_str(s):
        return '"' + s + '"'

    @staticmethod
    def get_source(name):
        with open(name, 'r') as f:
            return ''.join(f.read().split())

    def prepare(self):
        try:
            self.obj = eval(self.source)
        except:
            raise Exception('Invalid json string!')

    def line_intend(self, level=0):
        """行缩进"""
        return '\n' + ' ' * self.intend * level

    def parse_dict(self, obj=None, intend_level=0):
        """解析字典"""
        self.stack.append(self.line_intend(intend_level)+'{')
        intend_level += 1
        for key, value in obj.items():
            key = self.json_str(str(key))
            self.stack.append(self.line_intend(intend_level) + key + ':')
            self.parse(value, intend_level)
            self.stack.append(',')
        self.stack.append(self.line_intend(intend_level - 1) + '}')

    def parse_list(self, obj=None, intend_level=0):
        """解析list"""
        self.stack.append(self.line_intend(intend_level)+'[')
        intend_level += 1
        for item in obj:
            self.parse(item, intend_level)
            self.stack.append(',')
        self.stack.append(self.line_intend(intend_level-1)+']')

    def parse(self, obj, intend_level=0):
        """解析"""
        if obj is None:
            self.stack.append('null')
        elif obj is True:
            self.stack.append('true')
        elif obj is False:
            self.stack.append('false')
        elif isinstance(obj,(int,long,float)):
            self.stack.append(str(obj))
        elif isinstance(obj,str):
            self.stack.append(self.json_str(obj))
        elif isinstance(obj,(list,tuple)):
            self.parse_list(obj,intend_level)
        elif isinstance(obj,dict):
            self.parse_dict(obj,intend_level)
        else:
            raise Exception('Invalid json type %s!' % obj)

    def render(self, res_file):
        """写入新的文件"""
        self.parse(self.obj, 0)
        # res_file = 'good'+ self.name
        res=''.join(self.stack)
        with open(res_file, 'w') as f:
            f.write(res)
        print res


if __name__ == '__main__':
    jf = JsonFormatter(name=sys.argv[1])
    jf.render(sys.argv[2])