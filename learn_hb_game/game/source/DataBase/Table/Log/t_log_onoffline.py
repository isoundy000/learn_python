#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Enum, TIMESTAMP
Base = declarative_base()

from Source.DataBase.Common.DBEngine import DBEngine

LOG_USE_COIN_TAG_DEFAULT = "default"


class t_log_onoffline(Base):
    """
    角色在线|离线日志
    """
    __tablename__ = 't_log_onoffline'

    id = Column(Integer, primary_key=True)
    rid = Column(Integer, nullable=False)
    opt = Column(Enum("on", "off"), nullable=False, default="on")
    sock = Column(Integer, nullable=True, default=None)             # sockfileno
    time = Column(TIMESTAMP, nullable=True, default=datetime.now())

    @staticmethod
    def On(rid, sock):
        '''
        在线
        :param rid: 角色rid
        :param sock: sockfileno
        :return:
        '''
        if not rid:
            return
        log = t_log_onoffline()
        log.rid = rid
        log.sock = sock
        DBEngine.Add(log)

    @staticmethod
    def Off(rid, sock):
        '''
        离线
        :param rid: 角色rid
        :param sock: sockfileno
        :return:
        '''
        if not rid:
            return
        log = t_log_onoffline()
        log.rid = rid
        log.opt = "off"
        log.sock = sock
        DBEngine.Add(log)