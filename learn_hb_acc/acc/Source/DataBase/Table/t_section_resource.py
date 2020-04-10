#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, TIMESTAMP, Enum, String

Base = declarative_base()


class t_section_resource(Base):

    __tablename__ = "t_section_resource"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)      # 资源版本
    updatetime = Column(TIMESTAMP, nullable=False, default=datetime.now())          # 更新时间
    bywho = Column(Integer, nullable=False)                                         # 谁
    status = Column(Enum("prepare", "excute", "error"), nullable=False)             # 状态
    desc = Column(String(256), nullable=True)                                       # 描述
    needrestart = Column(Enum("yes", "no"), nullable=False, default='no')           # 是否需要重启