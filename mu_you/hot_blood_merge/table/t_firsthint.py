# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_firsthint(Base):
    # 新服加速标签兑换次数
    __tablename__ = 't_firsthint'
    rid = Column(Integer, primary_key=True)
    c1 = Column(Integer, nullable=True, default=1)  # 冲级奖励
    c2 = Column(Integer, nullable=True, default=1)  # 神翼排行榜
    c3 = Column(Integer, nullable=True, default=1)  # 战力排行榜
    c4 = Column(Integer, nullable=True, default=1)
    c5 = Column(Integer, nullable=True, default=1)
    c6 = Column(Integer, nullable=True, default=1)
    c7 = Column(Integer, nullable=True, default=1)
    c8 = Column(Integer, nullable=True, default=1)
    c9 = Column(Integer, nullable=True, default=1)
    c10 = Column(Integer, nullable=True, default=1)
    c11 = Column(Integer, nullable=True, default=1)
    c12 = Column(Integer, nullable=True, default=1)
    c13 = Column(Integer, nullable=True, default=1)
    c14 = Column(Integer, nullable=True, default=1)
    c15 = Column(Integer, nullable=True, default=1)
    c16 = Column(Integer, nullable=True, default=1)
    c17 = Column(Integer, nullable=True, default=1)
    c18 = Column(Integer, nullable=True, default=1)
    c19 = Column(Integer, nullable=True, default=1)
    c20 = Column(Integer, nullable=True, default=1)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj