# -*- encoding: utf-8 -*-
'''
Created on 2018年10月6日

@author: houguangdong
'''


def HanlderError1006(game_id):
    if int(game_id) not in [30, 32, 33, 36, 37, 38, 39, 42, 999999]:
        return
    t_sql = "select id from t_role;"
    with session_scope() as session:
        rows_all = session.execute(t_sql)
    for data in rows_all:
        rid = data[0]
        if int(rid) <= 5:
            continue
        CreateSystemMail(rid,
                         "打龙中断补偿",
                         "打龙中断兽魂补偿",
                         ConvertRewardDictToAttachmentJson({1028: 3000}),
                         checkHint=False)