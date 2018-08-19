# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_gang2_skill(Base):
    __tablename__ = "t_gang2_skill"
    __table_args__ = {'extend_existing':True}
    rid = Column(Integer, primary_key=True, nullable=False)
    status = Column(Enum("yes","no"), nullable=False, default="no")
    level1 =  Column(Integer, nullable=False, default=0)
    level2 =  Column(Integer, nullable=False, default=0)
    level3 =  Column(Integer, nullable=False, default=0)
    level4 =  Column(Integer, nullable=False, default=0)
    level5 =  Column(Integer, nullable=False, default=0)
    level6 =  Column(Integer, nullable=False, default=0)
    level7 =  Column(Integer, nullable=False, default=0)
    level8 =  Column(Integer, nullable=False, default=0)
    level9 =  Column(Integer, nullable=False, default=0)
    level10 =  Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
