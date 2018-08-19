# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_pet3_passiveskill(Base):
    __tablename__ = "t_pet3_passiveskill"
    rid = Column(Integer, primary_key=True)
    p1 = Column(Integer, nullable=True, default=None)
    s1 = Column(Integer, nullable=True, default=0)#0未开启 1开启未激活 2激活
    l1 = Column(Integer, nullable=True, default=None)
    p2 = Column(Integer, nullable=True, default=None)
    s2 = Column(Integer, nullable=True, default=0)#0未开启 1开启未激活 2激活
    l2 = Column(Integer, nullable=True, default=None)
    p3 = Column(Integer, nullable=True, default=None)
    s3 = Column(Integer, nullable=True, default=0)#0未开启 1开启未激活 2激活
    l3 = Column(Integer, nullable=True, default=None)
    p4 = Column(Integer, nullable=True, default=None)
    s4 = Column(Integer, nullable=True, default=0)#0未开启 1开启未激活 2激活
    l4 = Column(Integer, nullable=True, default=None)
    p5 = Column(Integer, nullable=True, default=None)
    s5 = Column(Integer, nullable=True, default=0)#0未开启 1开启未激活 2激活
    l5 = Column(Integer, nullable=True, default=None)
    c1 = Column(Integer, nullable=False, default=0)
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    lock1 = Column(Enum("yes","no"), nullable=True, default="no")
    lock2 = Column(Enum("yes","no"), nullable=True, default="no")
    lock3 = Column(Enum("yes","no"), nullable=True, default="no")
    lock4 = Column(Enum("yes","no"), nullable=True, default="no")
    lock5 = Column(Enum("yes","no"), nullable=True, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj


