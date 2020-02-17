#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ConfigParser
import logging


class ConfigManager(object):

    _config_dict = None

    @staticmethod
    def create(filename):
        parse_file = ParseIniFile(filename)
        parse_file.init()
        parse_file.getvalue()
        parse_file.close()
        ConfigManager._config_dict = parse_file.ini_dict

    @staticmethod
    def getvalue(arr, args):
        try:
            return ConfigManager._config_dict[arr][args]
        except AttributeError:
            logging.error("from ConfigManager._config_dict get config attribute error")
        return None


class ParseIniFile(object):
    """
         解析ini配置文件
    """
    def __init__(self, filename):
        self.filename = filename
        self.cfg = None
        self.read_handle = None
        self.ini_dict = {}

    def init(self):
        self.cfg = ConfigParser.ConfigParser()
        try:
            with open(self.filename, "r") as self.read_handle:
                self.cfg.readfp(self.read_handle)
        except IOError:
            logging.error("parse ini file error")

    def getvalue(self):
        if self.read_handle:
            for sect in self.cfg.sections():
                temp_dict = {}
                for opt in self.cfg.options(sect):
                    temp_dict[opt] = self.cfg.get(sect, opt)
                self.ini_dict[sect] = temp_dict

    def close(self):
        if self.read_handle is not None:
            self.read_handle.close()

    def write(self, data):
        for k in self.ini_dict[data]:
            self.cfg.set(data, k, self.ini_dict[data][k])

        self.cfg.write(open(self.filename, "w"))