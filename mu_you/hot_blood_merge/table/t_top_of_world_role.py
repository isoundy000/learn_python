#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'yanglei'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_top_of_world_role(Base):
    # 新服加速按钮状态
    __tablename__ = 't_top_of_world_role'
    rid = Column(Integer, primary_key=True)
    days = Column(Integer, primary_key=True)
    pag = Column(Integer, primary_key=True)
    s1 = Column(Enum("yes","no","get"), nullable=True, default="no")  # 任务按钮状态
    s2 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s3 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s4 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s5 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s6 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s7 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s8 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s9 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s10 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s11 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s12 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s13 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s14 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s15 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s16 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s17 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s18 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s19 = Column(Enum("yes","no","get"), nullable=True, default="no")
    s20 = Column(Enum("yes","no","get"), nullable=True, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj


