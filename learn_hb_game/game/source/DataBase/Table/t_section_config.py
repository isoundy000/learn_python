#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String
Base = declarative_base()
from Source.DataBase.Common.DBEngine import DBEngine, session_scope


class t_section_config(Base):
    """分区配置"""
    __tablename__ = "t_section_config"
    section = Column(Integer, primary_key=True)     # 分区
    ctype = Column(String(20), primary_key=True)    # 配置
    version = Column(Integer, nullable=False)       # 版本号

    @staticmethod
    def All(section=None):
        with session_scope() as session:
            if not section:
                result = session.query(t_section_config).all()      # 获取所有的配置
            else:
                result = session.query(t_section_config).filter(t_section_config.section == section).all()  # 获取分区配置
            return result

    @staticmethod
    def UpdateVersion(section, ctype, version):
        with session_scope() as session:
            configFile = session.query(t_section_config).filter(t_section_config.section == section).filter(
                t_section_config.ctype == ctype
            ).first()
            if configFile != None:
                configFile.version = version        # 更新配置的版本
                DBEngine.Update(configFile)
            else:
                configFile = t_section_config()     # 添加新的配置
                configFile.section = section
                configFile.ctype = ctype
                configFile.version = version
                DBEngine.Add(configFile)
            return configFile