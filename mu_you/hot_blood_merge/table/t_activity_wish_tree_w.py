# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()

class t_activity_wish_tree_w(Base):
    __tablename__ = 't_activity_wish_tree_w'
    rid = Column(Integer, primary_key=True)
    c1 = Column(Integer, nullable=False, default=0)  # 祈愿御守数量
    c2 = Column(Integer, nullable=False, default=0)  # 祈愿币数量
    c3 = Column(Integer, nullable=False, default=0)  # 今日积分
    c4 = Column(Integer, nullable=False, default=0)  # 活动内总积分
    updatetime = Column(TIMESTAMP, nullable=False, default=None)  # 数据更新时间


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj