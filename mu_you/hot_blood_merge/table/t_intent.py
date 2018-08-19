__author__ = 'liuzhaoyang'
# -*- coding: UTF-8 -*-
# !/usr/bin/env python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_intent(Base):
    __tablename__ = 't_intent'
    rid = Column(Integer, primary_key=True)
    tid = Column(Integer, primary_key=True)
    status = Column(Enum('no', 'yes', 'get'), nullable=False, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
