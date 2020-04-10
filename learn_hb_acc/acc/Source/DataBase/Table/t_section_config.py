#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
Base = declarative_base()


class t_section_config(Base):
    '''分区配置'''
    __tablename__ = "t_section_config"

    section = Column(Integer, primary_key=True)     # 分区
    ctype = Column(String(64), primary_key=True)    # 文件名
    version = Column(Integer, nullable=False)       # 配置版本号
    excute = Column(Integer, nullable=False)        # 执行到第几个文件
    desc = Column(String(256), nullable=True)       # 描述