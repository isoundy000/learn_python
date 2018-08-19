# -*- coding: UTF-8 -*-
# !/usr/bin/env python
__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_resourcesrec(Base):
    __tablename__ = 't_resourcesrec'
    rid = Column(Integer, primary_key=True)
    sysid = Column(Integer, primary_key=True)
    coinreward = Column(String, nullable=False)
    goldreward = Column(String, nullable=False)
    coincon = Column(Integer, nullable=False, default=None)
    goldcon = Column(Integer, nullable=False, default=None)
    s1 = Column(Enum("yes", "no", "get"), nullable=False, default="yes")  # 是否领取

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
