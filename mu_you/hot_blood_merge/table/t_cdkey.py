# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_cdkey(Base):
    __tablename__ = 't_cdkey'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rid = Column(Integer, nullable=False)
    uid = Column(Integer, nullable=False)
    cdkey = Column(String(10), nullable=False)
    status = Column(Enum('yes','no','get'), nullable=True, default=None)
    time = Column(TIMESTAMP, nullable=False, default=datetime.now)
    cid = Column(Integer, nullable=True)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
