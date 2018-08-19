# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_general_collect(Base):
    __tablename__ = "t_general_collect"
    rid = Column(Integer, primary_key=True, nullable=False)
    cid = Column(Integer, primary_key=True, nullable=False)
    status = Column(Enum("have", "see"), nullable=False)
    num = Column(Integer, nullable=False)
    count = Column(Integer, nullable=True, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
