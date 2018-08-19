# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_wish_tree_shop_w(Base):
    __tablename__ = 't_activity_wish_tree_shop_w'
    rid = Column(Integer, primary_key=True)
    pos1 = Column(Integer, nullable=False, default=0)  # 商店位置1兑换次数
    pos2 = Column(Integer, nullable=False, default=0)  # 商店位置2兑换次数
    pos3 = Column(Integer, nullable=False, default=0)  # 商店位置3兑换次数
    pos4 = Column(Integer, nullable=False, default=0)  # 商店位置4兑换次数
    pos5 = Column(Integer, nullable=False, default=0)  # 商店位置5兑换次数
    pos6 = Column(Integer, nullable=False, default=0)  # 商店位置6兑换次数
    pos7 = Column(Integer, nullable=False, default=0)  # 商店位置7兑换次数
    pos8 = Column(Integer, nullable=False, default=0)  # 商店位置8兑换次数
    pos9 = Column(Integer, nullable=False, default=0)  # 商店位置9兑换次数
    pos10 = Column(Integer, nullable=False, default=0)  # 商店位置10兑换次数
    pos11 = Column(Integer, nullable=False, default=0)  # 商店位置11兑换次数
    pos12 = Column(Integer, nullable=False, default=0)  # 商店位置12兑换次数
    pos13 = Column(Integer, nullable=False, default=0)  # 商店位置13兑换次数
    pos14 = Column(Integer, nullable=False, default=0)  # 商店位置14兑换次数
    pos15 = Column(Integer, nullable=False, default=0)  # 商店位置15兑换次数
    pos16 = Column(Integer, nullable=False, default=0)  # 商店位置16兑换次数
    pos17 = Column(Integer, nullable=False, default=0)  # 商店位置17兑换次数
    pos18 = Column(Integer, nullable=False, default=0)  # 商店位置18兑换次数
    pos19 = Column(Integer, nullable=False, default=0)  # 商店位置19兑换次数
    pos20 = Column(Integer, nullable=False, default=0)  # 商店位置20兑换次数


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj