#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'ghou'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_god_general(Base):
    __tablename__ = 't_god_general'

    rid = Column(Integer, primary_key=True)
    point = Column(Integer, nullable=False, default=0)  # 亲感度
    p1 = Column(Integer, nullable=False, default=0)  # 积分箱子奖励 0未激活 1激活 2排名奖励
    p2 = Column(Integer, nullable=False, default=0)
    p3 = Column(Integer, nullable=False, default=0)
    p4 = Column(Integer, nullable=False, default=0)
    p5 = Column(Integer, nullable=False, default=0)
    p6 = Column(Integer, nullable=False, default=0)
    p7 = Column(Integer, nullable=False, default=0)
    p8 = Column(Integer, nullable=False, default=0)
    p9 = Column(Integer, nullable=False, default=0)
    p10 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
