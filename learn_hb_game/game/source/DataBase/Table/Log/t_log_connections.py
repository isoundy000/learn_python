#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import TIMESTAMP, Integer, Column
Base = declarative_base()

from Source.DataBase.Common.DBEngine import DBEngine

from Source.GameData import GameData


class t_log_connections(Base):

    __tablename__ = 't_log_connections'

    t = Column(TIMESTAMP, primary_key=True)
    c = Column(Integer, nullable=False)
    u = Column(Integer, nullable=False)

    @staticmethod
    def Now(c, u):
        nowLogConnections = t_log_connections()
        nowLogConnections.t = GameData.sysTickTime
        nowLogConnections.c = c
        nowLogConnections.u = u
        DBEngine.Add(nowLogConnections)