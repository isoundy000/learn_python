# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_watchstar(Base):
    __tablename__ = 't_watchstar'
    rid = Column(Integer, primary_key=True)
    star = Column(Integer, nullable=False, default=0)
    c1 = Column(Integer, nullable=False, default=0)
    c2 = Column(Integer, nullable=False, default=0)
    s1 = Column(Integer, nullable=False, default=0)
    s2 = Column(Integer, nullable=False, default=0)
    s3 = Column(Integer, nullable=False, default=0)
    s4 = Column(Integer, nullable=False, default=0)
    s5 = Column(Integer, nullable=False, default=0)
    s6 = Column(Integer, nullable=False, default=0)
    s7 = Column(Integer, nullable=False, default=0)
    s8 = Column(Integer, nullable=False, default=0)
    r1 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r2 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r3 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r4 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r5 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r6 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r7 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r8 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r9 = Column(Enum('yes','no','get'), nullable=False, default='no')
    r10 = Column(Enum('yes','no','get'), nullable=False, default='no')
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)  # 观星档位

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name in ['level']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
