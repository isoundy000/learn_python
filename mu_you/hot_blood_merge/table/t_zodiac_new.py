# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_zodiac_new(Base):
    __tablename__ = 't_zodiac_new'
    rid = Column(Integer, primary_key=True, nullable=False)
    map1 = Column(Integer, nullable=False, default=0)  # 生肖难度
    map2 = Column(Integer, nullable=False, default=0)
    map3 = Column(Integer, nullable=False, default=0)
    map4 = Column(Integer, nullable=False, default=0)
    map5 = Column(Integer, nullable=False, default=0)
    map6 = Column(Integer, nullable=False, default=0)
    map7 = Column(Integer, nullable=False, default=0)
    map8 = Column(Integer, nullable=False, default=0)
    map9 = Column(Integer, nullable=False, default=0)
    map10 = Column(Integer, nullable=False, default=0)
    map11 = Column(Integer, nullable=False, default=0)
    map12 = Column(Integer, nullable=False, default=0)
    c1 = Column(Integer, nullable=False, default=0)  # 今天挑战次数
    c2 = Column(Integer, nullable=False, default=0)  # 今日刷新次数
    c3 = Column(Integer, nullable=False, default=0)  # 记录刷新到的生肖
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
