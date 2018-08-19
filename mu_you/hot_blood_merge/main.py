# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os

import argparse
import traceback
from datetime import datetime

import config
import merge
import merge.role
import merge.friend
import merge.gang
import merge.utils
import merge.world_war
#fp = open('memory_profile_with_gc.log', 'w+')
#from memory_profiler import profile
import gc
from table.t_role import t_role
from table.t_mail3 import t_mail3


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    return args

#@profile(stream=fp)
def process_one(cur):
    args = parse_args()

    # 加载配置文件
    cfg = config.Config()
    if not cfg.load(args.config, cur):
        return False

    # 创建主建变更表
    merge.init_merge_log(cfg.dst_database, False)
    gc.collect()
    # 对于多次合服的表重新读取 t_merge_log 中t_gang2表的主键变更信息
    cfg.load_merge_log()
    gc.collect()
    # 合服处理玩家数据
    role_merge = merge.role.RoleMerge(cfg)
    role_merge.run()
    gc.collect()
    # 全服数据处理
    utils_merge = merge.utils.UtilsMerge(cfg)
    utils_merge.run()

    gc.collect()
    # t_friend表关联rid特殊处理
    friend_merge = merge.friend.FriendMerge(cfg)
    friend_merge.run()

    gc.collect()
    # 跨服战合服处理
    world_war_merge = merge.world_war.WorldWarMerge(cfg)
    world_war_merge.run()

    gc.collect()
    # 公会特殊处理公会名称，id，及关联的公会id的公会池塘和t_gang2_role表
    gang_merge = merge.gang.GangMerge(cfg)
    gang_merge.run()

    gc.collect()

    cfg.dump_merge_log()
    cfg.dump_file_log()
    del role_merge
    del utils_merge
    del friend_merge
    del world_war_merge
    del gang_merge

    for databases in cfg.src_databases:
        databases.session.expunge_all()
    cfg.dst_database.session.expunge_all()
    del cfg
    gc.collect()
    return True


def main():
    dt1 = datetime.now()
    print "[Merge]start-all  %s" % (datetime.now(),)
    for i in range(0,1000):
        print "[Merge]start %d %s" % (i, datetime.now())
        gc.collect()
        if not process_one(i):
            print "[Merge]end-all  %s" % (datetime.now(),)
            break
        print "[Merge]end %d %s" % (i, datetime.now())
    args = parse_args()
    # 加载配置文件
    cfg = config.Config()
    cfg.load(args.config, 9999)
    try:
        cfg.dst_database.session.execute("""alter table t_session add column `server` int(11) DEFAULT NULL;""")
        cfg.dst_database.session.commit()
    except Exception, e:
        #traceback.print_exc()
        pass
    try:
        cfg.dst_database.session.execute("""
        DROP TABLE IF EXISTS `t_server_nextrid`;
        CREATE TABLE `t_server_nextrid` (
          `server` int(11) NOT NULL,
          `nextrid` int(11) NOT NULL,
          PRIMARY KEY (`server`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
        """)
        cfg.dst_database.session.commit()
    except Exception, e:
        #traceback.print_exc()
        pass
    try:
        cfg.dst_database.session.execute("""truncate t_worldboss1_rank""")
        cfg.dst_database.session.execute("""truncate t_worldboss2_rank""")
        #cfg.dst_database.session.execute("""truncate t_worldboss1;""")
        #cfg.dst_database.session.execute("""truncate t_worldboss2;""")

        cfg.dst_database.session.execute("""truncate t_athletics_role;""")
        cfg.dst_database.session.execute("""truncate t_athletics;""")
        cfg.dst_database.session.execute("""truncate t_recharge_first;""")
        cfg.dst_database.session.execute("""truncate t_limittimeexchange;""")
        cfg.dst_database.session.execute("""truncate t_limittimeexchange_itemcount;""")

        cfg.dst_database.session.execute("""truncate t_gp_battle;""")
        cfg.dst_database.session.execute("""truncate t_gp_battle_old;""")
        cfg.dst_database.session.execute("""truncate t_gp_battlefield;""")
        cfg.dst_database.session.execute("""truncate t_gp_battlefield_old;""")
        cfg.dst_database.session.execute("""truncate t_gp_mbattle_old;""")
        cfg.dst_database.session.execute("""truncate t_gp_mbattle;""")
        cfg.dst_database.session.execute("""truncate t_gp_members;""")
        cfg.dst_database.session.execute("""truncate t_gp_occupy_inspire;""")
        cfg.dst_database.session.execute("""truncate t_gp_register;""")
        cfg.dst_database.session.execute("""truncate t_gp_status;""")
        cfg.dst_database.session.execute("""truncate t_gang2_welfare;""")

        table_increment = 0
        for status in cfg.dst_database.session.execute("""SHOW TABLE STATUS;"""):
            if status[0] == 't_mail3':
                table_increment = status[10]
                break

        roles = cfg.dst_database.session.query(t_role).all()
        for role in roles:
            rid = role.id

            mail = t_mail3()
            table_increment += 1
            mail.id = table_increment
            mail.rid = rid
            mail.source = 0
            mail.type = "system"
            mail.status = "no"
            # mail.title = "合服奖励"
            # mail.content = "为了让您合服后更好的体验游戏，特奖励改名卡一张，请查收！"
            mail.title = "Cross Server Reward"
            mail.content = "Get 1 Rename card after cross server"
            mail.attachment = """{"20018":1}"""
            cfg.dst_database.session.add(mail)

        cfg.dst_database.session.commit()
    except Exception, e:
        traceback.print_exc()
    try:
        for i in range(5000):
            cfg.dst_database.session.execute("""INSERT INTO t_athletics (rank) VALUES (%d)""" % (i + 1))
        cfg.dst_database.session.commit()
    except Exception, e:
        traceback.print_exc()


    dt2 = datetime.now()

    print("all time %s" % (dt2 - dt1))
    try:
        url = cfg.status_url
        os.system("curl \"%s\"" % url)
    except:
        print "[Error] url is Error"
    print ("[Speed of progress]_______:100%")


if __name__ == '__main__':
    main()
