# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_slot2(Base):
    __tablename__ = 't_slot2'
    __table_args__ = {'extend_existing':True}
    rid = Column(Integer, primary_key=True)
    s1 = Column(Integer, nullable=True, default=None)
    s2 = Column(Integer, nullable=True, default=None)
    s3 = Column(Integer, nullable=True, default=None)
    s4 = Column(Integer, nullable=True, default=None)
    s5 = Column(Integer, nullable=True, default=None)
    s6 = Column(Integer, nullable=True, default=None)
    s7 = Column(Integer, nullable=True, default=None)

    c1 = Column(Integer, nullable=True, default=None)
    c2 = Column(Integer, nullable=True, default=None)
    c3 = Column(Integer, nullable=True, default=None)
    c4 = Column(Integer, nullable=True, default=None)
    c5 = Column(Integer, nullable=True, default=None)
    c6 = Column(Integer, nullable=True, default=None)
    c7 = Column(Integer, nullable=True, default=None)
    c8 = Column(Integer, nullable=True, default=None)

    p1 = Column(Integer, nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
