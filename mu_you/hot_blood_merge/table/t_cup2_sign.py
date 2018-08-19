# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_cup2_sign(Base):
    __tablename__ = "t_cup2_sign"
    rid = Column(Integer, primary_key=True)
    level = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    vip = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
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
    time = Column(TIMESTAMP, nullable=True, default=datetime.now)
    p1 = Column(Integer, nullable=True, default=None)
    slot_spirit = Column(Integer, nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
