# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()

class t_chat_blacklst(Base):
    __tablename__ = 't_chat_blacklst'
    rid = Column(Integer, primary_key=True)
    oid = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=True,default=datetime.now)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

