#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, and_
from sqlalchemy.sql import func
Base = declarative_base()
from Source.DataBase.Common.DBEngine import session_scope, DBEngine


class t_server_nextrid(Base):

    __tablename__ = "t_server_nextrid"
    __table_args__ = {'extend_existing': True}

    server = Column(Integer, primary_key=True)
    nextrid = Column(Integer, nullable=False)

    @staticmethod
    def NextServerRid(server):
        '''
        获取当前服的最大rid
        :param server:
        :return:
        '''
        t_role = t_server_nextrid.t_role        # 角色表
        with session_scope() as session:
            result = session.query(t_server_nextrid).filter(t_server_nextrid == server).first()
            if not result:
                ret = session.query(func.max(t_role.id).label("max_rid")).filter(and_(t_role.id > (1000000 * server), (t_role.id < (1000000 * (server + 1))))).first()
                result = t_server_nextrid()
                result.server = server
                if ret and ret.max_rid:
                    result.nextrid = ret.max_rid + 1
                else:
                    result.nextrid = 1000000 * server + 1
            nextrid = result.nextrid
            result.nextrid += 1
            DBEngine.Update(result)
            return nextrid