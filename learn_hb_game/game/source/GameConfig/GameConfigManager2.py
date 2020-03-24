#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import traceback
import os
import codecs
import json
import gevent
from Source.DataBase.Table.t_section_config import t_section_config
from Source.Config.ConfigManager import ConfigManager
from geventhttpclient import HTTPClient
from geventhttpclient.url import URL
from Source.DataBase.Table.t_ktv import t_ktv
from Source.Log.Write import Log
from Source.DataBase.Common.DBEngine import DBEngine


class GameConfigManager:

    _dict = {}              # {3: {'activity': {'data_key': 'data_value'}}}
    _version = {}           # {3: {'activity': 1, 'xxx': 2}}
    _section = 3
    _ktv = None             # t_ktv数据

    @staticmethod
    def Init():
        Log.Write("GameConfigManager.Init 1", GameConfigManager._section)       # 分区数
        GameConfigManager._ktv = t_ktv.LoadAllToDict()
        if GameConfigManager._ktv:
            if GameConfigManager._ktv.has_key("section"):                       # 分区
                GameConfigManager._section = int(GameConfigManager._ktv["section"].value)
            Log.Write("GameConfigManager.Init 2", GameConfigManager._section)
            appConfig = ConfigManager.Singleton()
            gameconfig_root = appConfig["Server"]["Configure"]["root"]

            configFiles = t_section_config.All(GameConfigManager._section)      # 获取分区下面的配置表
            for configFile in configFiles:
                if not GameConfigManager._version.has_key(configFile.section):
                    GameConfigManager._version[configFile.section] = {}         # 版本的分区
                if not GameConfigManager._dict.has_key(configFile.section):
                    GameConfigManager._dict[configFile.section] = {}
                Log.Write(configFile.ctype, configFile.section)                 # 配置名, 分区
                GameConfigManager._version[configFile.section][configFile.ctype] = configFile.version
                Log.Write(gameconfig_root, os.sep, str(configFile.section), os.sep, configFile.ctype, ".json")  # xxxx/3/activity.json
                configFilePath = gameconfig_root + os.sep + str(configFile.section) + os.sep + configFile.ctype + ".json"
                Log.Write(configFilePath)
                try:
                    with file(configFilePath, 'r') as f:
                        GameConfigManager._dict[configFile.section][configFile.ctype] = json.loads(f, encoding='utf-8')
                except IOError, e:
                    Log.Write("[Error]GameConfig Error: %s cant read" % configFilePath)
                    return False
            GameConfigManager.ProcessExt()
        return True

    @staticmethod
    def ProcessExt():
        try:
            GameConfigManager.GeneralExt()
        except Exception, e:
            Log.Write(e)
            Log.Write(traceback.format_exc())

    @staticmethod
    def setSection(section):
        """
        设置分区
        :param section: 分区号|数字
        :return:
        """
        GameConfigManager._section = section
        if not GameConfigManager._ktv.has_key("section"):               # 初始化分区
            ktv = t_ktv()
            ktv.key = "section"
            ktv.type = "int"
            ktv.value = str(section)
            GameConfigManager._ktv["section"] = ktv
            DBEngine.Add(GameConfigManager._ktv["section"])
        else:
            if int(GameConfigManager._ktv["section"].value) != int(section):
                GameConfigManager._ktv["section"].value = str(section)  # 缓存跟数据库数据做映射
                DBEngine.Update(GameConfigManager._ktv["section"])      # 更新数据的数据

    @staticmethod
    def Data():
        """
        获取分区下所有配置数据
        :return:
        """
        # Log.Write("section", GameConfigManager._section)
        if not GameConfigManager._dict.has_key(GameConfigManager._section):
            return None
        return GameConfigManager._dict[GameConfigManager._section]

    @staticmethod
    def Version():
        """
        获取分区下配置的版本号{'activity': 1, 'xxx': 2}
        :return:
        """
        if not GameConfigManager._version.has_key(GameConfigManager._section):
            return None
        return GameConfigManager._version[GameConfigManager._section]

    @staticmethod
    def HttpDownloadFile(configurl, writetopath):
        '''
        通过http获取配置
        :param configurl: 配置url
        :param writetopath: 写入本地的路径
        :return:
        '''
        Log.Write(configurl, writetopath)
        maxlen = len(configurl)
        for i in xrange(0, 10):
            fixurl = configurl[i % maxlen]
            Log.Write("oldurl", fixurl)
            fixurl = fixurl.replace("https", "http")
            Log.Write("fixurl", fixurl)
            url = URL(fixurl)
            try:
                http = HTTPClient.from_url(url)
                response = http.get(url.request_uri)
                CHUNK_SIZE = 1024 * 16          # 16KB
                data = response.read(CHUNK_SIZE)
                sumdata = data
                while data:
                    data = response.read(CHUNK_SIZE)
                    sumdata += data
                json.loads(sumdata)
                with open(writetopath, 'w') as f:
                    f.write(sumdata)
                Log.Write("success")
            except Exception, e:
                Log.Write("fail", i, e)
                gevent.sleep(1)
                continue
            return True
        # Log.Write(response)
        # f = codecs.open(writetopath, "w", "utf-8")
        # body = response.read()
        # Log.Write("data", body.decode('gbk').encode("utf-8"))
        # f.write(body)
        # f.close()
        return False

    @staticmethod
    def Update(section, changeFiles):
        """
        更新分区配置
        :param section: 分区号
        :param changeFiles: 配置文件
        :return:
        """
        Log.Write("GameConfigManager.Update")
        appConfig = ConfigManager.Singleton()
        gameconfig_root = appConfig["Server"]["Configure"]["root"]
        GameConfigManager._section = section
        if not GameConfigManager._dict.has_key(section):
            GameConfigManager._dict[section] = {}
        configDir = gameconfig_root + os.sep + str(GameConfigManager._section)
        Log.Write("configDir", configDir)
        try:
            os.mkdir(configDir)
        except:
            pass
        for changeFile in changeFiles:
            configFilePath = configDir + os.sep + changeFile.ctype + ".json"
            Log.Write("target", changeFile.url, changeFile.urls[:])
            Log.Write("config", configFilePath)
            # f = codecs.open(configFilePath, "w", "utf-8")
            # f.write(changeFile.content)
            # f.close()
            if GameConfigManager.HttpDownloadFile([changeFile.url] + changeFile.urls[:], configFilePath):
                t_section_config.UpdateVersion(section, changeFile.ctype, changeFile.version)
                if not GameConfigManager._version.has_key(section):
                    GameConfigManager._version[section] = {}
                GameConfigManager._version[section][changeFile.ctype] = changeFile.version
                try:
                    with file(configFilePath, 'r') as f:
                        GameConfigManager._dict[section][changeFile.ctype] = json.loads(f, encoding='utf-8')
                except IOError, e:
                    Log.Write("[Error]GameConfig Error: %s cant read" % (configDir + os.sep + changeFile.ctype + ".json"))
                    return False
            # GameConfigManager._dict[section][changeFile.ctype] = json.loads(configFilePath.content, encoding='utf-8')
        GameConfigManager.ProcessExt()

    @staticmethod
    def GeneralExt():
        '''
        武将碎片扩展
        :return:
        '''
        gameConfig = GameConfigManager.Data()
        if not gameConfig:
            return
        if not gameConfig.has_key("general_fragment"):
            return
        generalFragmentConfig = gameConfig["general_fragment"]
        extDict = {}
        for fragmentid, fragment in generalFragmentConfig.items():
            extDict[fragment["general"]] = fragment
        gameConfig["general_fragment_ext"] = extDict
        generalConfig = gameConfig["general"]
        for k, v in generalConfig.items():
            for attr in ATTR_ARRAY_2:
                tag = attr + "-grow"
                if not v.has_key(tag):
                    v[tag] = 0



ATTR_ARRAY = [
    "hp", "atk", "def", "speed", "critical", "dodge", "parry"
]

ATTR_ARRAY_Level2Up = ["hp", "atk", "def"]

ATTR_ARRAY_Level2NoUp = ["speed", "critical", "dodge", "parry"]

# critical 暴击率 dodge 闪避率 parry 反击率 resilience 抗暴率 hit 命中率 arp 抗反率 criticaldmg 暴击伤害 adddmg 增伤值 subdmg 减伤值 ap 怒气点 ap 攻击增加怒气点
ATTR_ARRAY_2 = [
    "hp", "atk", "def", "speed", "critical", "dodge", "parry", "resilience", "hit", "arp", "criticaldmg", "adddmg", "subdmg", "ap", "ap_atk_p"
]