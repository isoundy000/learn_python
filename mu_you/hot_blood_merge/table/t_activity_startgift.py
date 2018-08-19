#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_startgift(Base):
    __tablename__ = 't_activity_startgift'
    rid = Column(Integer, primary_key=True)
    logintime = Column(TIMESTAMP, nullable=False)
    days = Column(Integer, nullable=False, default=1)
    d1 = Column(Integer, nullable=False, default=0)
    d2 = Column(Integer, nullable=False, default=0)
    d3 = Column(Integer, nullable=False, default=0)
    d4 = Column(Integer, nullable=False, default=0)
    d5 = Column(Integer, nullable=False, default=0)
    d6 = Column(Integer, nullable=False, default=0)
    d7 = Column(Integer, nullable=False, default=0)
    d8 = Column(Integer, nullable=False, default=0)
    d9 = Column(Integer, nullable=False, default=0)
    d10 = Column(Integer, nullable=False, default=0)
    d11 = Column(Integer, nullable=False, default=0)
    d12 = Column(Integer, nullable=False, default=0)
    d13 = Column(Integer, nullable=False, default=0)
    d14 = Column(Integer, nullable=False, default=0)
    d15 = Column(Integer, nullable=False, default=0)
    d16 = Column(Integer, nullable=False, default=0)
    d17 = Column(Integer, nullable=False, default=0)
    d18 = Column(Integer, nullable=False, default=0)
    d19 = Column(Integer, nullable=False, default=0)
    d20 = Column(Integer, nullable=False, default=0)
    d21 = Column(Integer, nullable=False, default=0)
    d22 = Column(Integer, nullable=False, default=0)
    d23 = Column(Integer, nullable=False, default=0)
    d24 = Column(Integer, nullable=False, default=0)
    d25 = Column(Integer, nullable=False, default=0)
    d26 = Column(Integer, nullable=False, default=0)
    d27 = Column(Integer, nullable=False, default=0)
    d28 = Column(Integer, nullable=False, default=0)
    d29 = Column(Integer, nullable=False, default=0)
    d30 = Column(Integer, nullable=False, default=0)
    d31 = Column(Integer, nullable=False, default=0)
    d32 = Column(Integer, nullable=False, default=0)
    d33 = Column(Integer, nullable=False, default=0)
    d34 = Column(Integer, nullable=False, default=0)
    d35 = Column(Integer, nullable=False, default=0)
    d36 = Column(Integer, nullable=False, default=0)
    d37 = Column(Integer, nullable=False, default=0)
    d38 = Column(Integer, nullable=False, default=0)
    d39 = Column(Integer, nullable=False, default=0)
    d40 = Column(Integer, nullable=False, default=0)
    d41 = Column(Integer, nullable=False, default=0)
    d42 = Column(Integer, nullable=False, default=0)
    d43 = Column(Integer, nullable=False, default=0)
    d44 = Column(Integer, nullable=False, default=0)
    d45 = Column(Integer, nullable=False, default=0)
    d46 = Column(Integer, nullable=False, default=0)
    d47 = Column(Integer, nullable=False, default=0)
    d48 = Column(Integer, nullable=False, default=0)
    d49 = Column(Integer, nullable=False, default=0)
    d50 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj