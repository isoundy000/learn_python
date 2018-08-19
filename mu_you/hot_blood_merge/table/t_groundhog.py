#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'yanglei'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()
from datetime import datetime


class t_groundhog(Base):
    __tablename__ = 't_groundhog'
    rid = Column(Integer, primary_key=True)
    hog1 = Column(Integer, nullable=False, default=0)
    hog2 = Column(Integer, nullable=False, default=0)
    hog3 = Column(Integer, nullable=False, default=0)
    hog4 = Column(Integer, nullable=False, default=0)
    hog5 = Column(Integer, nullable=False, default=0)
    hog6 = Column(Integer, nullable=False, default=0)
    hog7 = Column(Integer, nullable=False, default=0)
    hog8 = Column(Integer, nullable=False, default=0)
    hog9 = Column(Integer, nullable=False, default=0)
    hognum = Column(Integer, nullable=False, default=0)  # 当前的怪物数量
    integal = Column(Integer, nullable=False, default=0)  # 本局分数
    lifes = Column(Integer, nullable=False, default=0)  # 本局所剩生命值
    energy = Column(Boolean, nullable=False, default=False)  # 是否充能
    combo = Column(Integer, nullable=False, default=0)  # 连击次数
    box1count = Column(Integer, nullable=False, default=0)  # 本局获得的随机宝箱1个数
    box2count = Column(Integer, nullable=False, default=0)  # 本局获得的随机宝箱2个数
    box3count = Column(Integer, nullable=False, default=0)  # 本局获得的随机宝箱3个数
    box4count = Column(Integer, nullable=False, default=0)  # 本局获得的随机宝箱4个数
    box5count = Column(Integer, nullable=False, default=0)  # 本局获得的随机宝箱5个数
    createtime = Column(TIMESTAMP, nullable=True, default=datetime.now)  # 游戏开始时间
    lastcatchtime = Column(TIMESTAMP, nullable=True, default=datetime.now)  # 上次抓地鼠的时间
    gameover = Column(Boolean, nullable=False, default=True)  # 是否游戏结束

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
