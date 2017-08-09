# -*- coding: utf-8 -*-
'''
Created on 8/9/2017

@author: ghou
'''
import logging


def test_get_logger(name):
    logger = logging.getLogger()
    #set loghandler
    file1 = logging.FileHandler(name)
    logger.addHandler(file1)
    #set formater
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file1.setFormatter(formatter)
    #set log level
    logger.setLevel(logging.ERROR)
    return logger


def read_config():
    file1 = open('./config', mode='r')
    stream_data = file1.readlines()
    lines = iter(stream_data)
    data = {}
    for line in lines:
        line = line.strip('\n').strip()
        if not line:
            continue
        if line[0] == '#':
            continue
        key, value = line.split(' ', 1)
        value_list = value.split(',')
        if len(value_list)>1:
            if len(value_list) == 2:
                data[key] = [value_list[0].strip(' ')]
            else:
                data[key] = [i and i.strip(' ') for i in value_list]
        else:
            data[key] = value.strip(' ')
        value_list = value.split(';')
#         if
    file1.close()
    return data
