# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_mysteryshop(Base):
    __tablename__ = 't_mysteryshop'
    rid = Column(Integer, primary_key=True)
    free = Column(Integer, nullable=False,default=0)
    i1 = Column(Integer, nullable=True, default=None)
    c1 = Column(Integer, nullable=True, default=0)
    i2 = Column(Integer, nullable=True, default=None)
    c2 = Column(Integer, nullable=True, default=0)
    i3 = Column(Integer, nullable=True, default=None)
    c3 = Column(Integer, nullable=True, default=0)
    i4 = Column(Integer, nullable=True, default=None)
    c4 = Column(Integer, nullable=True, default=0)
    i5 = Column(Integer, nullable=True, default=None)
    c5 = Column(Integer, nullable=True, default=0)
    i6 = Column(Integer, nullable=True, default=None)
    c6 = Column(Integer, nullable=True, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
