# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_olddriver(Base):
    __tablename__ = 't_olddriver'
    rid = Column(Integer, primary_key=True)
    s0 = Column(Enum('no','yes','get'), nullable=False, default='no')
    s1 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s2 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s3 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s4 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s5 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s6 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s7 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s8 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s9 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s10 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s11 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s12 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s13 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s14 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s15 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s16 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s17 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s18 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s19 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s20 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s21 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s22 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s23 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s24 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s25 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s26 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s27 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s28 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s29 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    s30 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')
    c1 = Column(Integer, nullable=False, default=0)
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)
    c11 = Column(Integer, nullable=False, default=0)
    c12 = Column(Integer, nullable=False, default=0)
    c13 = Column(Integer, nullable=False, default=0)
    c14 = Column(Integer, nullable=False, default=0)
    c15 = Column(Integer, nullable=False, default=0)
    c16 = Column(Integer, nullable=False, default=0)
    c17 = Column(Integer, nullable=False, default=0)
    c18 = Column(Integer, nullable=False, default=0)
    c19 = Column(Integer, nullable=False, default=0)
    c20 = Column(Integer, nullable=False, default=0)
    c21 = Column(Integer, nullable=False, default=0)
    c22 = Column(Integer, nullable=False, default=0)
    c23 = Column(Integer, nullable=False, default=0)
    c24 = Column(Integer, nullable=False, default=0)
    c25 = Column(Integer, nullable=False, default=0)
    c26 = Column(Integer, nullable=False, default=0)
    c27 = Column(Integer, nullable=False, default=0)
    c28 = Column(Integer, nullable=False, default=0)
    c29 = Column(Integer, nullable=False, default=0)
    c30 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
