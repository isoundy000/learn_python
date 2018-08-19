#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_gemdiscount_shop2(Base):
    __tablename__ = 't_gemdiscount_shop2'
    rid = Column(Integer, primary_key=True)
    i1 = Column(Integer, nullable=True, default=None)
    i2 = Column(Integer, nullable=True, default=None)
    i3 = Column(Integer, nullable=True, default=None)
    i4 = Column(Integer, nullable=True, default=None)
    i5 = Column(Integer, nullable=True, default=None)
    i6 = Column(Integer, nullable=True, default=None)
    i7 = Column(Integer, nullable=True, default=None)
    i8 = Column(Integer, nullable=True, default=None)
    i9 = Column(Integer, nullable=True, default=None)
    i10 = Column(Integer, nullable=True, default=None)
    i11 = Column(Integer, nullable=True, default=None)
    i12 = Column(Integer, nullable=True, default=None)
    i13 = Column(Integer, nullable=True, default=None)
    i14 = Column(Integer, nullable=True, default=None)
    i15 = Column(Integer, nullable=True, default=None)
    i16 = Column(Integer, nullable=True, default=None)
    i17 = Column(Integer, nullable=True, default=None)
    i18 = Column(Integer, nullable=True, default=None)
    i19 = Column(Integer, nullable=True, default=None)
    i20 = Column(Integer, nullable=True, default=None)
    i21 = Column(Integer, nullable=True, default=None)
    i22 = Column(Integer, nullable=True, default=None)
    i23 = Column(Integer, nullable=True, default=None)
    i24 = Column(Integer, nullable=True, default=None)
    i25 = Column(Integer, nullable=True, default=None)
    i26 = Column(Integer, nullable=True, default=None)
    i27 = Column(Integer, nullable=True, default=None)
    i28 = Column(Integer, nullable=True, default=None)
    i29 = Column(Integer, nullable=True, default=None)
    i30 = Column(Integer, nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
