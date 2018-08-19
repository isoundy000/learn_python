# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_recharge_lifetime(Base):
    __tablename__ = 't_activity_recharge_lifetime'
    rid = Column(Integer, primary_key=True)
    cid = Column(Integer, nullable=False, default=1)  # 配置ID
    rmb = Column(Integer, nullable=False, default=0)  # 累计充值的RMB
    status = Column(Enum('yes', 'no', 'get'), nullable=False, default="no")  # 奖励领取状态


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj