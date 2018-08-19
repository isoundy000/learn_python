#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'jutian'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_deep_copy(Base):
    __tablename__ = "t_deep_copy"
    rid = Column(Integer, primary_key=True, nullable=False)
    map = Column(Integer, primary_key=True, nullable=False)  # 深渊副本章节ID
    point = Column(Integer, primary_key=True, nullable=False)  # 深渊副本章节据点ID
    kill = Column(Integer, nullable=False, default=-1)  # 击杀次数
    box = Column(Enum("no", "yes", "get"), nullable=False, default="no")  # 首次通关奖励领取状态
    normal = Column(Enum("no", "yes", "get"), nullable=False, default="no")  # 普通通关奖励领取状态，只有在首次通关奖励领取后才可以领取
    star = Column(Integer, nullable=False, default=0)  # 通关星级
    starrewards = Column(Enum("no", "yes", "get"), nullable=False, default="no")  # 3星奖励领取状态
    c1 = Column(Integer, nullable=False, default=0)
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
