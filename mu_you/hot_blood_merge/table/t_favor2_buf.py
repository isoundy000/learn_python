#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'jutian'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_favor2_buf(Base):
    __tablename__ = 't_favor2_buf'
    rid = Column(Integer, primary_key=True)
    cid = Column(Integer, nullable=True, default=None)
    t = Column(Integer, nullable=True, default=None)
    c1 = Column(Integer, nullable=False, default=0)  # 今天送道具1次数
    c2 = Column(Integer, nullable=False, default=0)  # 今天送道具2次数
    c3 = Column(Integer, nullable=False, default=0)  # 是否还能送礼
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)  # 上一次

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
