#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_rechargerebate(Base):
    __tablename__ = 't_rechargerebate'
    rid = Column(Integer, primary_key=True)
    rmb = Column(Integer, nullable=False, default=0)  # 累计充值rmb/累计消费元宝
    getgold = Column(Integer, nullable=False, default=0)  # 累计返利元宝
    c1 = Column(Integer, nullable=False, default=0)
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    r1 = Column(Enum('yes','no','get'), nullable=False, default='no')  # 宝箱状态（no未达成，yes达成未领取，get已领取）
    r2 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r3 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r4 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r5 = Column(Enum('yes','no','get'), nullable=False, default='no')

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
