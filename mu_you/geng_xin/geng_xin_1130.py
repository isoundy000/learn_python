# -*- encoding: utf-8 -*-
'''
Created on 2018年11月30日

@author: houguangdong
'''

# # 限时兑换优化(上到快游了)
# game/Source/DataBase/Table/t_limittimeexchange.py
# game/Source/GameOperation/LimitTimeExchange/MakeItems.py
# game/Source/Timer/DayHour/LimitTimeExchangeDayClear.py
# game/Source/WorkPool/Functions/Config.py
# game/Source/WorkPool/Functions/UserLimitTimeExchange.py
# game/Source/WorkPool/Functions/UserLimitTimeExchangeQuery.py
# game/Source/WorkPool/Functions/UserLimitTimeExchangeQueryNew.py
# game/Source/WorkPool/Functions/UserLimitTimeExchangeRefresh.py
# game/Source/WorkPool/Functions/UserHint.py
#
# # 工会解散功(上到快游了)
# game/Source/GameData/Gang2.py
# game/Source/WorkPool/Functions/Config.py
# game/Source/WorkPool/Functions/UserGang2Dissolve.py
# game/Source/WorkPool/Functions/UserGang2Req.py


# # 合服活动
# game/Source/DataBase/Table/Activity/__init__.py
# game/Source/DataBase/Table/Activity/t_combine_server_online_reward.py
# game/Source/GameData/CombineServerOnlineReward.py
# game/Source/GameData/GameData.py
# game/Source/GameData/GameDataManager.py
# game/Source/GameData/ActivityStatus.py
# game/Source/GameOperation/Activity/CombineServer/CombineServerOnlineRewardHandler.py
# game/Source/GameOperation/Activity/CombineServer/__init__.py
# game/Source/GameOperation/Hint/build475_online_reward.py
# game/Source/GameOperation/Activity/ComputeActivityValid.py
# game/Source/GameOperation/Hint/config.py
# game/Source/Timer/Config/Config.py
# game/Source/Timer/DayHour/CombineServerOnlineRewardDayClear.py
# game/Source/UserData/UserDataConfig.py
# game/Source/WorkPool/Functions/Config.py
# game/Source/WorkPool/Functions/UserCombineServerOnlineReward.py
# game/Source/WorkPool/Functions/UserHint.py
#
#
# # 巅峰活动
# game/Source/DataBase/Table/Activity/t_combine_server_top_of_world_role.py
# game/Source/DataBase/Table/Activity/t_combine_server_top_of_world_role_count.py
# game/Source/DataBase/Table/Activity/t_combine_server_top_of_world_role_exchange.py
# game/Source/DataBase/Table/t_general4.py
# game/Source/GameConfig/GameConfigManager2.py
# game/Source/GameData/ActivityStatus.py
# game/Source/GameData/CombineServerTopOfWorld.py
# game/Source/GameData/GameData.py
# game/Source/GameData/GameDataManager.py
# game/Source/GameData/ManorTask.py
# game/Source/GameOperation/Activity/CombineServer/CombineServerTopOfWorld/CheckTasks.py
# game/Source/GameOperation/Activity/CombineServer/CombineServerTopOfWorld/CombineDaysCompute.py
# game/Source/GameOperation/Activity/CombineServer/CombineServerTopOfWorld/CombineServerCheckTOWTypeTask.py
# game/Source/GameOperation/Budokai/__init__.py
# game/Source/GameOperation/Groundhog/Groundhog.py
# game/Source/GameOperation/Mieshendian/MieshendianModup.py
# game/Source/GameOperation/Recharge/RechargeComm.py
# game/Source/GameOperation/Role/ComputePower.py
# game/Source/GameOperation/Role/RoleGetExp.py
# game/Source/GameOperation/Hint/build476t503_combineservertopofworld.py
# game/Source/GameOperation/Hint/config.py
# game/Source/Timer/Config/Config.py
# game/Source/Timer/DayHour/CombineServerTopOfWorldClear.py
# game/Source/UserData/UserDataConfig.py
# game/Source/WSGI/GM/GMSysParam.py
# game/Source/WorkPool/Functions/ActivityCopyModUp.py
# game/Source/WorkPool/Functions/Config.py
# game/Source/WorkPool/Functions/UserActivityExpDanCopy.py
# game/Source/WorkPool/Functions/UserAthleticsAttack2.py
# game/Source/WorkPool/Functions/UserAthleticsBoss.py
# game/Source/WorkPool/Functions/UserCombineServerTopOfWorldQuery.py
# game/Source/WorkPool/Functions/UserCombineServerTopOfWorldReward.py
# game/Source/WorkPool/Functions/UserCopyAttack22.py
# game/Source/WorkPool/Functions/UserCopyModUp2.py
# game/Source/WorkPool/Functions/UserCupBattleBet.py
# game/Source/WorkPool/Functions/UserEquipAllFragmentCompound.py
# game/Source/WorkPool/Functions/UserEquipBaptizeConfirm.py
# game/Source/WorkPool/Functions/UserEquipBaptizeFree.py
# game/Source/WorkPool/Functions/UserEquipFragmentCompound.py
# game/Source/WorkPool/Functions/UserFavoriteGeneralUseProp.py
# game/Source/WorkPool/Functions/UserFriendCopyAttack.py
# game/Source/WorkPool/Functions/UserGang2BossBattle.py
# game/Source/WorkPool/Functions/UserGang2Pray.py
# game/Source/WorkPool/Functions/UserGeneralBreak.py
# game/Source/WorkPool/Functions/UserGeneralCopyAttack.py
# game/Source/WorkPool/Functions/UserGeneralFosterConfirm2.py
# game/Source/WorkPool/Functions/UserGeneralFosterFree.py
# game/Source/WorkPool/Functions/UserKingManBattle.py
# game/Source/WorkPool/Functions/UserManorNoticeQuery.py
# game/Source/WorkPool/Functions/UserManorQuery.py
# game/Source/WorkPool/Functions/UserMieshendianBattle1.py
# game/Source/WorkPool/Functions/UserMieshendianBattle2.py
# game/Source/WorkPool/Functions/UserMieshendianModupCDClear.py
# game/Source/WorkPool/Functions/UserMieshendianReset.py
# game/Source/WorkPool/Functions/UserOverPassBattle.py
# game/Source/WorkPool/Functions/UserOverPassGetReward.py
# game/Source/WorkPool/Functions/UserPatrolDo.py
# game/Source/WorkPool/Functions/UserPatrolQueryEx.py
# game/Source/WorkPool/Functions/UserProtagonistGrowUp.py
# game/Source/WorkPool/Functions/UserTreasureFragmentRob.py
# game/Source/WorkPool/Functions/UserTrialBattle.py
# game/Source/WorkPool/Functions/UserTrialOpenBox.py
# game/Source/WorkPool/Functions/UserWatchStarReward.py
# game/Source/WorkPool/Functions/UserWatchStarWatch.py
# game/Source/WorkPool/Functions/UserWorldBoss1Attack.py
# game/Source/WorkPool/Functions/UserWorldBoss2Attack.py
# game/Source/WorkPool/Functions/UserZodiac.py