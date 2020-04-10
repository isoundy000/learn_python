#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP

Base = declarative_base()


class t_section_config_files(Base):

    __tablename__ = "t_section_config_files"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)  # 自增id
    ctype = Column(String(64), nullable=False)                                  # 文件名
    filepath = Column(String(256), nullable=True)                               # 文件路径
    url = Column(String(256), nullable=False)                                   # 文件url
    updatetime = Column(TIMESTAMP, nullable=False)                              # 更新时间
    bywho = Column(Integer, nullable=False)                                     # 谁传的表
    desc = Column(String(256), nullable=True)                                   # 描述
    url2 = Column(String(256), nullable=True, default=None)                     # 文件url2
    url3 = Column(String(256), nullable=True, default=None)                     # 文件url3