# -*- encoding: utf-8 -*-
'''
Created on 2018年10月17日

@author: houguangdong
'''


# # 一键申请好友功能
# alter table t_patrol_irr add column `pos1` int(11) DEFAULT '1';
# alter table t_role modify coin bigint(20);
# alter table t_log_getcoin modify num bigint(20);
#
# # feature/8_version
# game/Source/WorkPool/Functions/Config.py
# game/Source/WorkPool/Functions/UserFriendReq.py
# game/Source/WorkPool/Functions/UserGeneralAdvanced5.py
# game/Source/DataBase/Table/t_mysteryshop.py
# game/Source/WorkPool/Functions/UserMysteryRefresh.py
# game/Source/GameData/GameData.py
# game/Source/GameData/LevelRank.py
# game/Source/WorkPool/Functions/UserLevelRankQuery.py
#
# game/Source/DataBase/Table/t_patrol.py
# game/Source/DataBase/Table/t_patrol_irr.py
# game/Source/GameData/global_kv.py
# game/Source/GameData/global_kv_opt.py
# game/Source/GameOperation/Patrol/__init__.py
# game/Source/WorkPool/Functions/UserPatrolDo.py
# game/Source/WorkPool/Functions/UserPatrolQuery.py
#
# game/Source/DataBase/Table/Log/t_log_getcoin.py
# game/Source/DataBase/Table/t_role.py
# game/Source/Protocol/ids_pb2.py
# game/Source/Protocol/role_pb2.py
# game/Source/Protocol/somethings_pb2.py
# game/Source/UserData/UserDataConfig.py
# game/Source/WorkPool/Functions/AccAskUserInfo.py
#
# game/Source/GameOperation/Battle25/Battle.py
# game/Source/GameOperation/Battle25/MutilBattle.py
# game/Source/GameOperation/Budokai/__init__.py
# game/Source/WorkPool/Functions/UserAthleticsAttack2.py
# game/Source/WorkPool/Functions/UserAthleticsBoss.py
# game/Source/WorkPool/Functions/UserBattleOther.py
# game/Source/WorkPool/Functions/UserOverPassBattle.py
# game/Source/WorkPool/Functions/UserTreasureFragmentRob.py
# game/Source/WorkPool/Functions/UserTrialBattle.py
#
# game/Source/DataBase/Table/t_activity_daydaygift.py
# game/Source/GameOperation/Hint/build112_tiantianhaoli.py
# game/Source/WorkPool/Functions/UserDayDayGift.py
# game/Source/WorkPool/Functions/UserDayDayGiftReward.py
#
# # ext扩展
# ext/Source/GameOperation/Battle25/Battle.py
# ext/Source/GameOperation/Battle25/MutilBattle.py
# ext/Source/Timer/Exact/CupBattle.py
# ext/Source/WorkPool/Functions/Config.py
# ext/Source/WorkPool/Functions/Game/GameGPMbattle.py
#
#
# # acc代码
# acc/Source/WorkPool/Functions/GameAckUserInfo.py
#
# # worldwar
# worldwar/Source/GameData/WorldWar.py
# worldwar/Source/GameOperation/Battle25/Battle.py
# worldwar/Source/GameOperation/Battle25/BattleInOut.py
# worldwar/Source/GameOperation/Battle25/MutilBattle.py
#
# # feature/hero_boss
# game/Source/WorkPool/Functions/UserHeroBoss.py