#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Enum, Column
Base = declarative_base()
from Source.DataBase.Common.DBEngine import session_scope
from Source.GameData import GeneralFragmentRob   # 可抢夺的武将碎片


class t_general_collect(Base):
    '''武将碎片的收集'''
    __tablename__ = "t_general_collect"

    rid = Column(Integer, primary_key=True, nullable=False)     # 玩家rid
    cid = Column(Integer, primary_key=True, nullable=False)     # 武将cid
    status = Column(Enum("have", "see"), nullable=False)        # 有|看
    num = Column(Integer, nullable=False)
    count = Column(Integer, nullable=True, default=0)           # 不能为空

    @staticmethod
    def LoadRoleData(roleid):
        '''
        加载玩家的所有武将碎片数据
        :param roleid:
        :return:
        '''
        result = {}
        with session_scope() as session:
            generallist = session.query(t_general_collect).filter(t_general_collect.rid == roleid).all()
            for general in generallist:
                result[general.cid] = general
                GeneralFragmentRob.Add(general.cid, roleid)
        return result