# -*- encoding: utf-8 -*-
'''
Created on 2017年3月22日

@author: ghou
'''

import json
import demjson

# json.dumps 用于将 Python 对象编码成 JSON 字符串。
data = [{ 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 }]
json_string = json.dumps(data)
print json_string

# 使用参数让 JSON 数据格式化输出：
print json.dumps({'a': 'Runoob', 'b': 7}, sort_keys=True, indent=4, separators=(',', ': '))

# json.loads 用于解码 JSON 数据。该函数返回 Python 字段的数据类型。
# 以下实例展示了Python 如何解码 JSON 对象：
jsonData = '{"a":1,"b":2,"c":3,"d":4,"e":5}';
text = json.loads(jsonData)
print text

# Demjson 是 python 的第三方模块库，可用于编码和解码 JSON 数据，包含了 JSONLint 的格式化及校验功能。
# 官方地址：http://deron.meranda.us/python/demjson/
# 在使用 Demjson 编码或解码 JSON 数据前，我们需要先安装 Demjson 模块。本教程我们会下载 Demjson 并安装：
# tar -xvzf demjson-2.2.3.tar.gz
# cd demjson-2.2.3
# python setup.py install

# json 函数
# encode     将 Python 对象编码成 JSON 字符串
# decode    将已编码的 JSON 字符串解码为 Python 对象

# Python encode() 函数用于将 Python 对象编码成 JSON 字符串。
data = [ { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 } ]
json = demjson.encode(data)
print json

# Python 可以使用 demjson.decode() 函数解码 JSON 数据。该函数返回 Python 字段的数据类型。
json = '{"a":1,"b":2,"c":3,"d":4,"e":5}';
text = demjson.decode(json)
print  text