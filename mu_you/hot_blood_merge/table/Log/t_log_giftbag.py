# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_log_giftbag(Base):
    __tablename__ = 't_log_giftbag'
    rid =  Column(Integer, primary_key=True)
    cid = Column(Integer, primary_key=True)
    num = Column(Integer, nullable=False,default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj