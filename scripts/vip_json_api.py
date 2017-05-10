#! /usr/bin/env python # coding:utf8
'''
Created on 2017年5月10日

@author: ghou
'''

import os
from l10nparser.json.vip_json import VipJsonParser


def main():
    rootdir = r"D:\testdata\ghou\\"
    for parent,dirnames,filenames in os.walk(rootdir):
        for filename in filenames:
            if not filename.endswith(".json"):
                continue
            par_type = VipJsonParser(os.path.join(parent,filename))
            par_type.load()
            print '*'*20+'Loading successfully'+'*'*20
            write_json_format(par_type._string_item_list)


def write_json_format(StringItems):
    data_format = []
    for item in StringItems:
        key = item.get_key()
        value = item.get_value()
        data_dict = {}
        data_dict[key] = key
        data_dict['translationMap'] = {key: value}
        print data_dict, '11111'
        data_format.append(data_dict)
    
        
if __name__ == "__main__":
    main()