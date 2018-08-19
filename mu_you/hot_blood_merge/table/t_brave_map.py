#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_brave_map(Base):
    __tablename__ = "t_brave_map"
    rid = Column(Integer, primary_key=True, nullable=False)
    map = Column(Integer, primary_key=True, nullable=False)
    status = Column(Enum("excute", "complete", "all3star1", "all3star2"), nullable=False, default="excute")
    prestige = Column(Integer, nullable=False, default=0)
    pa1 = Column(Enum("no", "yes", "have"), nullable=False, default="no")
    pa2 = Column(Enum("no", "yes", "have"), nullable=False, default="no")
    pa3 = Column(Enum("no", "yes", "have"), nullable=False, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
