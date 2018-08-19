# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_quickslot(Base):
    __tablename__ = 't_quickslot'
    __table_args__ = {'extend_existing':True}
    rid = Column(Integer, primary_key=True)
    sys = Column(Integer, primary_key=True)
    param = Column(Integer, primary_key=True)
    s1 = Column(Integer, nullable=True, default=None)
    s2 = Column(Integer, nullable=True, default=None)
    s3 = Column(Integer, nullable=True, default=None)
    s4 = Column(Integer, nullable=True, default=None)
    s5 = Column(Integer, nullable=True, default=None)
    s6 = Column(Integer, nullable=True, default=None)
    s7 = Column(Integer, nullable=True, default=None)
    p1  = Column(Integer, nullable=True, default=None)
    power = Column(Integer, nullable=True, default=0)
    c1  = Column(Integer, nullable=True, default=0)
    c2  = Column(Integer, nullable=True, default=0)
    c3  = Column(Integer, nullable=True, default=0)
    c4  = Column(Integer, nullable=True, default=0)
    c5  = Column(Integer, nullable=True, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
