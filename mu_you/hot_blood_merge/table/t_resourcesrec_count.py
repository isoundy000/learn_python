# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_resourcesrec_count(Base):
    __tablename__ = 't_resourcesrec_count'
    __table_args__ = {'extend_existing': True}
    rid = Column(Integer, primary_key=True)
    day = Column(Integer, primary_key=True)
    tag = Column(Integer, nullable=False, default=0)
    c1 = Column(Integer, nullable=False, default=0)  # 活跃度宝箱25 (0没有、1有)
    c2 = Column(Integer, nullable=False, default=0)  # 活跃度宝箱50 (0没有、1有)
    c3 = Column(Integer, nullable=False, default=0)  # 活跃度宝箱75 (0没有、1有)
    c4 = Column(Integer, nullable=False, default=0)  # 活跃度宝箱100 (0没有、1有)
    c5 = Column(Integer, nullable=False, default=0)  # 活跃度宝箱150 (0没有、1有)
    c6 = Column(Integer, nullable=False, default=0)  # 十二宫 (0没有、1有)
    c7 = Column(Integer, nullable=False, default=1)  # 圣兽降临（中午）(0没有、1有)
    c8 = Column(Integer, nullable=False, default=1)  # 圣兽降临（晚上）(0没有、1有)
    c9 = Column(Integer, nullable=False, default=0)  # 社团祭拜 (0没有、1有)
    c10 = Column(Integer, nullable=False, default=0)  # 回转寿司 (0没有、<0 次数)
    c11 = Column(Integer, nullable=False, default=0)  # 地下拳赛 (0没有、<0 次数)
    c12 = Column(Integer, nullable=False, default=0)  # 经验副本 (0没有、<0 次数)
    c13 = Column(Integer, nullable=False, default=0)  # 好友副本 (0没有、<0 次数)
    c14 = Column(Integer, nullable=False, default=0)  # 神的试炼 (0没有、<0 次数)
    c15 = Column(Integer, nullable=False, default=0)  # 古渊 (0没有、<0 次数)
    c16 = Column(Integer, nullable=False, default=0)  # 十二生肖 是否参与
    c17 = Column(Integer, nullable=False, default=0)  # 荣耀对决次数
    c18 = Column(Integer, nullable=False, default=0)  # 夺宝奇兵次数
    c19 = Column(Integer, nullable=False, default=0)
    c20 = Column(Integer, nullable=False, default=0)
    i1 = Column(Integer, nullable=False, default=0)  # 古渊当天最高层
    i2 = Column(Integer, nullable=False, default=0)  # 经验副本当天最高关卡
    i3 = Column(Integer, nullable=False, default=0)  # 好友副本当天最高关卡
    i4 = Column(Integer, nullable=False, default=0)  # 王的男人当天最高关卡
    i5 = Column(Integer, nullable=False, default=0)
    i6 = Column(Integer, nullable=False, default=0)
    i7 = Column(Integer, nullable=False, default=0)
    i8 = Column(Integer, nullable=False, default=0)
    i9 = Column(Integer, nullable=False, default=0)
    i10 = Column(Integer, nullable=False, default=0)
    s1 = Column(Enum("yes", "no", "get"), nullable=False, default="no")  # 是否打圣兽（中午）
    s2 = Column(Enum("yes", "no", "get"), nullable=False, default="no")  # 是否打圣兽（晚上）
    s3 = Column(Enum("yes", "no", "get"), nullable=False, default="no")
    s4 = Column(Enum("yes", "no", "get"), nullable=False, default="no")
    s5 = Column(Enum("yes", "no", "get"), nullable=False, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
