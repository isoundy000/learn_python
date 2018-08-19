# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_soul2(Base):
    __tablename__ = "t_soul"
    __table_args__ = {'extend_existing':True}
    id = Column(Integer, primary_key=True)
    rid = Column(Integer, nullable=False)
    cid = Column(Integer, nullable=False)
    exp  = Column(Integer, nullable=True, default=0)
    level  = Column(Integer, nullable=True, default=1)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
