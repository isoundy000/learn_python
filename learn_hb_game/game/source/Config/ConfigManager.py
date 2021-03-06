#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from XMLToDictionary import CovertXMLFileToDictionary


class ConfigManager:
    '''
    本地配置管理器
    '''
    _config_dict = None

    def _singleton():
        return ConfigManager._config_dict

    Singleton = staticmethod(_singleton)

    Data = Singleton

    def _create(xml_file_path):
        ConfigManager._config_dict = CovertXMLFileToDictionary(xml_file_path)

    Create = staticmethod(_create)