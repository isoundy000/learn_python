# -*- coding: utf-8 -*-
'''
Created on 6/9/2017

@author: ghou
'''
import os
import json
from scripts.vip.loginsight_get_message.base.js import JsParser


def main():
    data= {}
    parser_path = "".join([os.path.abspath('.'), os.path.sep, 'js_file', os.path.sep])
    print parser_path, '11111'
    for fileName in os.listdir(parser_path):
        abspath =  parser_path + fileName
        fileName1 = fileName.split('.')[0]
        extension = fileName.split('.')[1]
        if extension.endswith('js'):
            parser = JsParser(abspath)
            parser.load()
            data[fileName1] = {}
            for i in parser._string_item_list:
                if i.key and i.key not in data[fileName1]:
                    data[fileName1][i.key.strip('"')] = i.value.strip(" ")
    change_dir = "".join([os.path.abspath('.'), os.path.sep, 'js_json', os.path.sep])
    for fileName, v in data.iteritems():
        absPathName = os.path.sep.join([change_dir, fileName+'.json'])
        fp = open(absPathName, 'w')
        encode_json = json.dumps(v)
        fp.write(encode_json)
        fp.close()

if __name__ == '__main__':
    main()