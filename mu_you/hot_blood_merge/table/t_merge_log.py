# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_merge_log(Base):
    __tablename__ = 't_merge_log'
    id = Column(Integer,primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False)
    identifier = Column(String(200), nullable=False)
    old_id = Column(Integer, nullable=False)
    new_id = Column(Integer, nullable=False)
