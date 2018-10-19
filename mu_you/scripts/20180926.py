# -*- encoding: utf-8 -*-
'''
Created on 2018年9月26日

@author: houguangdong
'''


def Error180926_kuaiyou(game_id):
    '''
    补老服的充值
    :return:
    '''
    if game_id <= 20:
        # 老服累计充值
        t_recharge_record = "select t_recharge_record.rid, sum(getgold)/10 as rmb from t_recharge_record, t_activity_rechargegift_x2 where recvtime > '2018-09-25 00:00:00' and t_recharge_record.rid = t_activity_rechargegift_x2.rid group by t_recharge_record.rid;"
        with session_scope() as session:
            role_rows = session.execute(t_recharge_record)
            for rid, rmb in role_rows:
                update_sql = "update t_activity_rechargegift_x2 set rmb = %s where rid = %s;" % (int(rmb), rid)
                session.execute(update_sql)

    if (20 < game_id and game_id <= 28) or game_id == 999999:
        if game_id in [22, 26]:
            return
        # 新服累计充值
        old_data_sql = "select * from t_activity_rechargegift_x2_20180925 where rmb > 0;"
        new_data_sql = "select * from t_activity_rechargegift_x2;"
        with session_scope() as session:
            old_rows = session.execute(old_data_sql)
            new_rows = session.execute(new_data_sql)
            rid_list = []
            for row in new_rows:
                rid_list.append(row.rid)
            for row in old_rows:
                if row["rid"] not in rid_list:
                    continue
                user_data = UserDataManager.GetUserDataByRoleId(row.rid)
                rechargegift_x2 = user_data.rechargegift_x2
                rechargegift_x2.rmb += row["rmb"]
                for x in range(1, 21):
                    new_data = rechargegift_x2['r%s' % x]
                    old_data = row['r%s' % x]
                    if (new_data == "no" or new_data == "yes") and old_data == "get":
                        rechargegift_x2['r%s' % x] = "get"
                UserDataProxy.AddChange(user_data, "rechargegift_x2")

        # 新服老司机
        if game_id == 25:
            return

        if game_id == 999999:
            laosiji_config = GameConfigManager.Data()["laosiji"]
        else:
            laosiji_config = GameConfigManager.Data()["laosiji_x3"]
        # 新服老司机
        old_driver_sql = "select * from t_olddriver_20180925;"
        new_driver_sql = "select * from t_olddriver;"
        with session_scope() as session:
            role_rows = session.execute(old_driver_sql)
            new_rows = session.execute(new_driver_sql)
            rid_list = []
            for row in new_rows:
                rid_list.append(row.rid)
            for row in role_rows:
                if row["rid"] not in rid_list:
                    continue
                user_data = UserDataManager.GetUserDataByRoleId(row.rid)
                olddriver = user_data.olddriver
                for s in range(0, 31):
                    if olddriver["s%s" % s] == "no" and row['s%s' % s] == 'yes':
                        olddriver["s%s" % s] = 'yes'
                    if row['s%s' % s] == 'get':
                        olddriver["s%s" % s] = 'get'

                for c in range(1, 31):
                    if int(row["c%s" % c]) != 0:
                        olddriver["c%s" % c] += int(row["c%s" % c])
                        for i_key in laosiji_config:
                            l_type = laosiji_config[i_key]["type"]
                            if l_type == c:
                                if olddriver["s" + i_key] == "no":
                                    if olddriver["c" + str(l_type)] >= laosiji_config[i_key]["target_num"]:
                                        olddriver["s" + i_key] = "yes"
                UserDataProxy.AddChange(user_data, "olddriver")