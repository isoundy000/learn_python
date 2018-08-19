# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_achievement_limittime(Base):
    __tablename__ = 't_achievement_limittime'
    rid = Column(Integer, primary_key=True)
    isfirst = Column(Integer, nullable=False, default=1) # 是否首次攻打灭神殿
    r1 = Column(Enum('yes','no','get'), nullable=False, default="no") # 按钮状态
    r2 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r3 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r4 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r5 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r6 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r7 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r8 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r9 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r10 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r11 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r12 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r13 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r14 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r15 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r16 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r17 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r18 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r19 = Column(Enum('yes','no','get'), nullable=False, default="no")
    r20 = Column(Enum('yes','no','get'), nullable=False, default="no")
    c1 = Column(Integer, nullable=False, default=0) # 每种类型的达成次数
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)
    c11 = Column(Integer, nullable=False, default=0)
    c12 = Column(Integer, nullable=False, default=0)
    c13 = Column(Integer, nullable=False, default=0)
    c14 = Column(Integer, nullable=False, default=0)
    c15 = Column(Integer, nullable=False, default=0)
    c16 = Column(Integer, nullable=False, default=0)
    c17 = Column(Integer, nullable=False, default=0)
    c18 = Column(Integer, nullable=False, default=0)
    c19 = Column(Integer, nullable=False, default=0)
    c20 = Column(Integer, nullable=False, default=0)
    c21 = Column(Integer, nullable=False, default=0)
    c22 = Column(Integer, nullable=False, default=0)
    c23 = Column(Integer, nullable=False, default=0)
    c24 = Column(Integer, nullable=False, default=0)
    c25 = Column(Integer, nullable=False, default=0)
    c26 = Column(Integer, nullable=False, default=0)
    c27 = Column(Integer, nullable=False, default=0)
    c28 = Column(Integer, nullable=False, default=0)
    c29 = Column(Integer, nullable=False, default=0)
    c30 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
