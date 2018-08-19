# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_chat_status(Base):
    __tablename__ = 't_chat_status'
    __table_args__ = {'extend_existing':True}
    rid = Column(Integer, primary_key=True)
    status = Column(Enum('yes','no'), nullable=False,default='yes')
    limittime = Column(TIMESTAMP, nullable=True,default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj

