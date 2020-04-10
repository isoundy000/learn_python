#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import os
from sqlalchemy.orm.exc import NoResultFound

from Source.Log.Write import Log
from Source.DataBase.Common.DBEngine import DBEngine, and_
from Source.DataBase.Table.t_section_config import t_section_config
from Source.DataBase.Table.t_section_config_files import t_section_config_files
from Source.Config.ConfigManager import ConfigManager


class GameConfigManager:

    # static members define
    _config_dict = {}

    @staticmethod
    def Data(section):
        return GameConfigManager._config_dict[section]

    @staticmethod
    def Init():
        session = DBEngine.NewSession()
        try:
            config_files = session.query(t_section_config, t_section_config_files). \
                filter(t_section_config.excute == t_section_config_files.id).all()

            if config_files is None:
                Log.Write("[Error]GameConfig Error: No GameConfig Data")
                return False

            GameConfigManager._config_dict = {}

            appConfig = ConfigManager.Singleton()

            for config_file in config_files:
                section = config_file[0].section
                config_file_info = {
                    "section": section,
                    "ctype": config_file[0].ctype,
                    "version": config_file[0].version,
                    "excute": config_file[0].excute,
                    "url": config_file[1].url,
                    "filepath": config_file[1].filepath,
                    "url2": config_file[1].url2,
                    "url3": config_file[1].url3
                }
                # Log.Write(section, config_file_info)
                if not GameConfigManager._config_dict.has_key(section):
                    GameConfigManager._config_dict[section] = {}
                GameConfigManager._config_dict[section][config_file[0].ctype] = config_file_info
            # for k, v in GameConfigManager._config_dict.items():
            #     Log.Write("section", k)
            return True
        except NoResultFound, nf:
            Log.Write("[Error]Database Error: %s" % str(nf))
            return False
        finally:
            DBEngine.DelSession(session)

    @staticmethod
    def Update(section, ctype):
        session = DBEngine.NewSession()
        try:
            config_file = session.query(t_section_config, t_section_config_files).\
                filter(and_(t_section_config.section == section, t_section_config.ctype == ctype)).\
                filter(t_section_config.excute == t_section_config_files.id).first()

            if config_file is None:
                Log.Write("[Error]GameConfig Error:No GameConfig Data")
                return None
            config_file_info = {
                "section": config_file[0].section,
                "ctype": config_file[0].ctype,
                "version": config_file[0].version,
                "excute": config_file[0].excute,
                "url": config_file[1].url,
                "filepath": config_file[1].filepath,
                "url2": config_file[1].url2,
                "url3": config_file[1].url3
            }
            if not GameConfigManager._config_dict.has_key(config_file_info["section"]):
                GameConfigManager._config_dict[config_file_info["section"]] = {}
            GameConfigManager._config_dict[config_file_info["section"]][config_file[0].ctype] = config_file_info
            return config_file_info
        except NoResultFound, nf:
            Log.Write("[Error]Database Error: %s" % str(nf))
            return None
        finally:
            DBEngine.DelSession(session)


import sys
reload(sys)
sys.setdefaultencoding('utf-8')