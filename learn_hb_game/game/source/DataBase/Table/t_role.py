#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, and_, func
Base = declarative_base()

from Source.DataBase.Common.DBEngine import DBEngine, session_scope
from Source.GameOperation.Role.CreateRole import CreateRole
from Source.DataBase.Table.t_server_nextrid import t_server_nextrid
import re

from Source.GameOperation.Time.ConvertToUTCSeconds import ConvertToUTCSeconds
from Source.GameData import GameData
from Source.Log.Write import Log


class t_role(Base):
    '''角色rid'''
    __tablename__ = 't_role'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=False)
    gender = Column(Enum("male", "female"), nullable=True, default="male")
    name = Column(String, nullable=True, default="")
    vip = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    exp = Column(Integer, nullable=False, default=0)
    coin = Column(Integer, nullable=False, default=0)
    gold = Column(Integer, nullable=False, default=100000)
    stamina = Column(Integer, nullable=False)  # 体力
    maxstamina = Column(Integer, nullable=False, default=100)
    energy = Column(Integer, nullable=False)  # 精力
    maxenergy = Column(Integer, nullable=False, default=100)
    prestige = Column(Integer, nullable=False, default=0)  # 竞技场积分
    athletics = Column(Integer, nullable=False, default=3)  # 竞技场剩余的次数
    createtime = Column(TIMESTAMP, nullable=False)  # 建角时间
    maxfriend = Column(Integer, nullable=True, default=10)
    profile = Column(Integer, nullable=True, default=None)  # 头像标识
    channel = Column(String, nullable=True, default=None)
    power = Column(Integer, nullable=True, default=0)
    platform = Column(Enum('ios', 'android', nullable=True, default=None))
    lastlogin = Column(TIMESTAMP, nullable=True, default=None)  # 最后一次登陆的时间
    avatar = Column(Integer, nullable=False, default=0)  # 头像框

    @staticmethod
    def LoadUserData(userid):
        # 引入合服机制, 通过判断userid的组成, 判断什么模式
        # 正常模式 userid 为整数
        # 合服模式 userid 为userid_server
        result = None
        if isinstance(userid, int) or isinstance(userid, long):     # 正常模式
            with session_scope() as session:
                result = session.query(t_role).filter(t_role.uid == userid).first()
            if result is None:
                result = t_role()
                result.uid = userid
                result.createtime = GameData.sysTickTime
                CreateRole(result)
                DBEngine.Add(result)
                DBEngine.Update(result)
            result.__server_fix = None
        else:                                                       # 合服模式
            Log.Write("LoadUserData merge tip")
            userid_a = userid.split("_")
            if len(userid_a) < 2:
                raise TypeError("Merge Mode t_role error")

            userid_fix = int(userid_a[0])
            server_fix = int(userid_a[1])
            Log.Write(userid_fix, server_fix)
            with session_scope() as session:
                result = session.query(t_role).filter(
                    and_(
                        t_role.uid == userid_fix,
                        and_(t_role.id > (1000000 * server_fix),
                            (t_role.id < (1000000 * (server_fix + 1)))
                        )
                    )
                ).first()
            if result is None:
                result = t_role()
                result.uid = userid_fix
                result.createtime = GameData.sysTickTime
                CreateRole(result, server_fix)
                DBEngine.Add(result)
                DBEngine.Update(result)
            else:
                m = re.match(r"^S(\d+)-", result.name)      # S999999-xxxx
                server_test = None
                try:
                    xxxtuple = m.groups()
                    server_test = int(xxxtuple[0])              # 服务器编号999999
                    Log.Write("[TIP]server_test", server_test)
                except:
                    pass
                if server_test != server_fix:
                    result.name = u"S%d-" % server_fix + result.name
                    Log.Write("[TIP]name", result.name)
                    DBEngine.Update(result)
            result.__server_fix = server_fix
        Log.Write("LoadUserData", userid, result.id, result.__server_fix)
        result.createtime_utc = ConvertToUTCSeconds(result.createtime)
        return result

    @staticmethod
    def LoadUserData2(userid):
        # 引入合服机制,通过判断userid的组成,判断什么模式
        # 正常模式 userid 为整数
        # 合服模式 userid 为userid_server
        result = None
        if isinstance(userid, int):
            with session_scope() as session:
                result = session.query(t_role).filter(t_role.uid == userid).first()
        else:
            Log.Write("LoadUserData2 merge tip")
            userid_a = userid.split("_")
            if len(userid_a) < 2:
                raise TypeError("Merge Mode t_role error")

            userid_fix = int(userid_a[0])
            server_fix = int(userid_a[1])
            Log.Write(userid_fix, server_fix)
            with session_scope() as session:
                result = session.query(t_role).filter(
                    and_(
                        t_role.uid == userid_fix,
                        and_(t_role.id > (1000000 * server_fix),
                            (t_role.id < (1000000 * (server_fix + 1)))
                        )
                    )
                ).first()

        if result:
            Log.Write("LoadUserData", userid, result.id)
            result.createtime_utc = ConvertToUTCSeconds(result.createtime)
        return result

    @staticmethod
    def LoadRoleData(roleid):
        '''
        根据rid获取玩家本身的数据
        :param roleid:
        :return:
        '''
        with session_scope() as session:
            result = session.query(t_role).filter(t_role.id == roleid).first()
            if result:
                rid = result.id
                server_fix = None
                if rid > 1000000:
                    server_fix = rid // 1000000     # server_id [1,2,3,...1000]
                    Log.Write("[TIP]server_fix", server_fix)
                    m = re.match(r"^S(\d+)-", result.name)
                    server_test = None
                    try:
                        xxxtuple = m.groups()
                        server_test = int(xxxtuple[0])
                        Log.Write("[TIP]server_test", server_test)
                    except:
                        pass
                    if server_test != server_fix:
                        result.name = u"S%d-" % server_fix + result.name
                        Log.Write("[TIP]name", result.name)
                        DBEngine.Update(result)
                result.createtime_utc = ConvertToUTCSeconds(result.createtime)
        return result

    @staticmethod
    def CheckUniqueName(name):
        '''
        名字是否唯一
        :param name:
        :return:
        '''
        with session_scope() as session:
            if session.query(t_role).filter(t_role.name == name).count() > 0:
                return False
        return True

    @staticmethod
    def FindRoleIdByName(name):
        '''
        通过名字获取t_role.id
        :param name:
        :return:
        '''
        with session_scope() as session:
            result = session.query(t_role.id).filter(t_role.name == name).first()
        if result:
            return result.id
        else:
            return 0

    @staticmethod
    def FindRoleIdByLevel(level, num, exceptId=0):
        '''
        获取相同等级的一票(num数量)玩家rid
        :param level: 玩家等级
        :param num: 获取的数量
        :param exceptId: 除去id
        :return:
        '''
        with session_scope() as session:
            result = session.query(t_role.id).filter(t_role.level == level).filter(t_role.id != exceptId).limit(num).all()
        rets = []
        for role in result:
            rets.append(role.id)
        return rets

    @staticmethod
    def RandomRoleIdFromTo(fromlv, tolv, exceptId=0):
        '''
        从某等级到某等级随机一个t_role.id
        :param fromlv: 从xxx等级
        :param tolv: 到xxx等级
        :param exceptId: 除去id
        :return:
        '''
        Log.Write("RandomRoleIdFromTo", fromlv, tolv)
        with session_scope() as session:
            result = session.query(t_role.id).filter(and_(t_role.level >= fromlv, t_role.level <= tolv)).filter(
                t_role.id != exceptId).order_by(func.random()).first()
            if result:
                Log.Write(result.id)
                return result.id
        return None

    @staticmethod
    def ValidLevelNum(lv):
        '''
        合法的等级数量
        :param lv:
        :return:
        '''
        with session_scope() as session:
            rs = session.query(func.count(t_role.id)).filter(t_role.level >= lv).first()
            Log.Write("ValidLevelNum", lv, rs)
            return rs[0]
        return 0

    @staticmethod
    def RandomLvPower(lv1, lv2, pw1, pw2):
        '''
        按照等级和战斗力随机一个玩家
        :param lv1:
        :param lv2:
        :param pw1:
        :param pw2:
        :return:
        '''
        # SQL = "select id from t_role where level >= %d and level <= %d and power >= %d and power <= %d order by RAND() limit 1;" % (lv1, lv2, pw1, pw2,)
        with session_scope() as session:
            result = session.query(t_role.id).filter(and_(t_role.level >= lv1, t_role.level <= lv2)).filter(
                and_(t_role.power >= pw1, t_role.power <= pw2)).order_by(func.random()).limit(1).first()
            if result:
                return result.id
        return None

    @staticmethod
    def RandomPower(pw1, pw2):
        '''
        按照战斗力随机一个玩家
        :param pw1:
        :param pw2:
        :return:
        '''
        # SQL = "select id from t_role where level >= %d and level <= %d and power >= %d and power <= %d order by RAND() limit 1;"%(lv1, lv2, pw1, pw2,)
        with session_scope() as session:
            result = session.query(t_role.id).filter(and_(t_role.power >= pw1, t_role.power <= pw2)).order_by(
                func.random()).limit(1).first()
            if result:
                return result.id
        return None

    @staticmethod
    def QueryLvPowerAscLimit(lv, limit):
        '''
        按照升序等级查询n个玩家
        :param lv:
        :param limit:
        :return:
        '''
        result = []
        with session_scope() as session:
            roles = session.query(t_role.id).filter(t_role.level >= lv).order_by(t_role.power).limit(limit).all()

        for role in roles:
            result.append(role.id)
        return result

    @staticmethod
    def QueryLvPowerDescLimit(lv, limit):
        '''
        按照降序等级查询n个玩家
        :param lv:
        :param limit:
        :return:
        '''
        result = []
        with session_scope() as session:
            roles = session.query(t_role.id).filter(t_role.level >= lv).order_by(t_role.power.desc()).limit(limit).all()
        for role in roles:
            result.append(role.id)
        return result

    @staticmethod
    def FindRoleIdOverVipAndLevel(vip, level):
        '''
        查询超过固定vip和等级玩家
        :param vip:
        :param level:
        :return:
        '''
        with session_scope() as session:
            result = session.query(t_role.id).filter(t_role.vip >= vip).filter(t_role.level >= level).all()
        rets = []
        for role in result:
            rets.append(role.id)
        return rets


# 挂在角色表数据信息
t_server_nextrid.t_role = t_role