# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_spinampwin(Base):
    __tablename__ = 't_spinampwin'
    rid = Column(Integer, primary_key=True)
    c1 = Column(Integer, nullable=False, default=0)#抽奖次数
    c2 = Column(Integer, nullable=False, default=0)#抽奖积分
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)

    s1 = Column(Integer, nullable=False, default=0)
    s2 = Column(Integer, nullable=False, default=0)
    s3 = Column(Integer, nullable=False, default=0)
    s4 = Column(Integer, nullable=False, default=0)
    s5 = Column(Integer, nullable=False, default=0)
    s6 = Column(Integer, nullable=False, default=0)
    s7 = Column(Integer, nullable=False, default=0)
    s8 = Column(Integer, nullable=False, default=0)
    s9 = Column(Integer, nullable=False, default=0)
    s10 = Column(Integer, nullable=False, default=0)
    s11 = Column(Integer, nullable=False, default=0)
    s12 = Column(Integer, nullable=False, default=0)
    s13 = Column(Integer, nullable=False, default=0)
    s14 = Column(Integer, nullable=False, default=0)
    s15 = Column(Integer, nullable=False, default=0)
    s16 = Column(Integer, nullable=False, default=0)
    s17 = Column(Integer, nullable=False, default=0)
    s18 = Column(Integer, nullable=False, default=0)
    s19 = Column(Integer, nullable=False, default=0)
    s20 = Column(Integer, nullable=False, default=0)

    t1 = Column(Enum('yes','no','get'), nullable=False,default='no')
    t2 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')
    t3 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')
    t4 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')
    t5 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')
    t6 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')
    t7 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')
    t8 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')
    t9 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')
    t10 = Column(Enum('yes', 'no', 'get'), nullable=False, default='no')

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
