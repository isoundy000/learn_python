#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_section_resource_files(Base):

    __tablename__ = "t_section_resource_files"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    r_id = Column(Integer, nullable=False)                                      # 资源版本号
    filepath = Column(String(256), nullable=False)
    url = Column(String(256), nullable=False)
    updatetime = Column(TIMESTAMP, nullable=False, default=datetime.now())
    bywho = Column(Integer, nullable=False)
    desc = Column(String(256), nullable=True)
    platform = Column(Enum("ios", "android", "all"), nullable=False, default="all")
    length = Column(Integer, default=0)
    url2 = Column(String(256), nullable=True, default=None)
    url3 = Column(String(256), nullable=True, default=None)