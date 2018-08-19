# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_role_status(Base):
    __tablename__ = "t_role_status"
    rid = Column(Integer,primary_key=True)
    status = Column(Enum('normal','block','dead'), nullable=False, default = 'normal')
    time = Column(TIMESTAMP, nullable=True, default = None)
    c1 = Column(Integer, nullable=False, default = 0)#abnormal count
    c2 = Column(Integer, nullable=False, default = 0)#error count
    c3 = Column(Integer, nullable=False, default = 0)#favorite select cid
    c4 = Column(Integer, nullable=False, default = 0)
    c5 = Column(Integer, nullable=False, default = 0)
    c6 = Column(Integer, nullable=False, default = 0)
    c7 = Column(Integer, nullable=False, default = 0)
    c8 = Column(Integer, nullable=False, default = 0)
    c9 = Column(Integer, nullable=False, default = 0)
    c10 = Column(Integer, nullable=False, default = 0)
    opttime = Column(TIMESTAMP, nullable=True, default = None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

