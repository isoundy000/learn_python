# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_recharge_growplan(Base):
    __tablename__ = 't_recharge_growplan'
    rid = Column(Integer, primary_key=True)
    r1 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r2 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r3 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r4 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r5 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r6 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r7 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r8 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r9 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r10 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r11 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r12 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r13 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r14 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r15 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r16 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r17 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r18 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r19 = Column(Enum('yes','no','get'),nullable=False, default='no')
    r20 = Column(Enum('yes','no','get'),nullable=False, default='no')
    time = Column(TIMESTAMP , nullable=True, default=datetime.now)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj