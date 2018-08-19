#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_eatchicken(Base):
    __tablename__ = "t_activity_eatchicken"
    rid = Column(Integer, primary_key=True, nullable=False)
    time1 = Column(Enum("yes", "no"), nullable=False)
    time2 = Column(Enum("yes", "no"), nullable=False)
    time3 = Column(Enum("yes", "no"), nullable=False)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj