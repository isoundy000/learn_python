# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_recommend(Base):
    __tablename__ = "t_recommend"
    rid = Column(Integer, primary_key=True, nullable=False)
    r1 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r2 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r3 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r4 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r5 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r6 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r7 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r8 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r9 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r10 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r11 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r12 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r13 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r14 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r15 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r16 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r17 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r18 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r19 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r20 = Column(Enum('no','yes','get'), nullable=False, default='no')
    c1 = Column(Integer, nullable=True, default=0)
    c2 = Column(Integer, nullable=True, default=0)
    c3 = Column(Integer, nullable=True, default=0)
    c4 = Column(Integer, nullable=True, default=0)
    c5 = Column(Integer, nullable=True, default=0)
    s1 = Column(Integer, nullable=True, default=0)
    s2 = Column(Integer, nullable=True, default=0)
    s3 = Column(Integer, nullable=True, default=0)
    s4 = Column(Integer, nullable=True, default=0)
    s5 = Column(Integer, nullable=True, default=0)
    s6 = Column(Integer, nullable=True, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj