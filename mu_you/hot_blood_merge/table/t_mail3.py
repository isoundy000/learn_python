# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()

class t_mail3(Base):
    __tablename__ = 't_mail3'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rid = Column(Integer, nullable=False)

    mtype = Column(Integer, nullable=False, default=0)
    source = Column(Integer, nullable=True, default=None)
    type = Column(Enum('system', 'battle', 'normal'), nullable=False, default='normal')
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    attachment = Column(String, nullable=True, default=None)
    time = Column(TIMESTAMP, nullable=True, default=datetime.now)
    status = Column(Enum('yes', 'no', 'get'), nullable=False, default="no")
    pn = Column(Integer, nullable=False, default=0)
    p1 = Column(String, nullable=True, default=None)
    p2 = Column(String, nullable=True, default=None)
    p3 = Column(String, nullable=True, default=None)
    p4 = Column(String, nullable=True, default=None)
    p5 = Column(String, nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

