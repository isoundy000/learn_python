# -*- encoding: utf-8 -*-
'''
Created on 2018年10月17日

@author: houguangdong
'''

# 跨服测试更改
# update t_world_war_sign_role set server_id = 997;
# game/Source/GameData/WorldWar.py    SATURDAY 改成需要的日期 零点刷新
# 获取时装的日期

# worldwar/Source/GameData/WorldWar.py
# 改推送的服务器限制和InitGameServer   gameservers = session.query(t_gameserver).filter(t_gameserver.status == 'online' and t_gameserver.id < 500).all()
# data/hot_kuaiyou_kuafu_2/source/SanguoGame/Source/WorkPool/Functions/GameServerInfos.py  # 有限制