#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

from XMLToDictionary import CovertXMLFileToDictionary


class ConfigManager:

    _config_dict = None

    def _singleton():
        return ConfigManager._config_dict

    Singleton = staticmethod(_singleton)

    Data = Singleton

    def _create(xml_file_path):
        ConfigManager._config_dict = CovertXMLFileToDictionary(xml_file_path)

    Create = staticmethod(_create)