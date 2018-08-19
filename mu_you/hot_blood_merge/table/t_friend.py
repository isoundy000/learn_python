# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_friend(Base):
    __tablename__ = 't_friend'
    rid = Column(Integer, primary_key=True)
    fid = Column(Integer, primary_key=True)
    ftime = Column(TIMESTAMP, nullable=True, default=datetime.now)
    fg = Column(Integer, nullable=True, default=None)
    sg = Column(Integer, nullable=True, default=None)
    use = Column(Enum("yes","no"), nullable=False, default="no")
    sendgift = Column(Enum("yes","no"), nullable=False, default="no")
    recvgift = Column(Enum("yes","no", "get"), nullable=False, default="no")
    recvgifttime = Column(TIMESTAMP, nullable=True)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid', 'fid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
