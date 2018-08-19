# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_trigger_gift(Base):
    __tablename__ = "t_trigger_gift"
    id = Column(Integer,primary_key=True, autoincrement=True)
    rid = Column(Integer,nullable=False)
    cfg_id = Column(Integer, nullable=False, default=0)
    ts = Column(TIMESTAMP, nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
