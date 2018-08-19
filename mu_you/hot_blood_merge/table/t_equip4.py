#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column
Base = declarative_base()


class t_equip4(Base):
    __tablename__ = "t_equip4"
    __table_args__ = {'extend_existing':True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    rid = Column(Integer, nullable=False)
    cid = Column(Integer, nullable=False)
    level1 = Column(Integer, nullable=False, default=1)  # 强化等级
    level2 = Column(Integer, nullable=False, default=0)  # 进阶等级
    exp2 = Column(Integer, nullable=True, default=0)
    xatk = Column(Integer, nullable=True, default=0)
    xdef = Column(Integer, nullable=True, default=0)
    xhp = Column(Integer, nullable=True, default=0)
    xadddmg = Column(Integer, nullable=True, default=0)
    xsubdmg = Column(Integer, nullable=True, default=0)
    xcount = Column(Integer, nullable=True, default=0)   # 洗练
    level3 = Column(Integer, nullable=False, default=0)  # 升星

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj