/**
 * Created by wangrui on 15/9/7.
 */

var $role_id_info_1 = $('#role_id_info_1');
var $select_game = $('#select_game');
var $role_name_info_1 = $('#role_name_info_1');
OPERATE_TYPE = {
    "UserRandomName": "获取名字 参数为性别",
    "UserSetName": "设置名字",
    "UserSetProfile": "选择主角形象",
    "UserRechargePre": "充值准备",
    "UserVipRechargeQuery": "充值查询",
    "UserGlobalParams": "UserGlobalParams",
    "UserArrive": "UserArrive",
    "UserRoleInfo": "玩家信息查询",
    "UserSlotInfo": "玩家阵位信息查询",
    "UserGeneralChangePos": "武将换阵",
    "UserCheerPos": "更换助阵位武将",
    "UserSlotChangeEquip": "更换装备",
    "UserSlotChangeSoul": "更换命格",
    "UserQuickEquip3": "一键装备",
    "UserUpgradeSkill": "UserUpgradeSkill",
    "UserChangePosOnSlot": "布阵",
// 武将
    "UserGeneralInheritPreview": "UserGeneralInheritPreview",
    "UserGeneralInheritConfirm": "UserGeneralInheritConfirm",
    "UserGeneralFragment": "武将魂魄列表",
    "UserGeneralFosterPreview2": "伙伴培养",
    "UserGeneralFosterConfirm2": "伙伴培养确认",
    "UserGeneralCollect": "武将图鉴",
    "UserGeneralCompound": "武将合成",
    "UserGeneralBreak": "武将突破",
    "UserGeneralFragmentRobQuery": "抢夺武将碎片查询",
    "UserGeneralFragmentRob": "抢夺武将碎片抢夺",
    "UserOtherSlotInfo": "查询好友阵位信息",
    "UserGeneralExchange": "伙伴兑换",
    "UserBattleOther": "好友切磋",
    "UserGeneralBreakPreview": "武将突破预览",
    "UserSystemMail": "系统邮件查询",
    "UserCount": "玩家计数埋点",
    "UserHint": "红点查询",
    "UserRecordBattle": "UserRecordBattle",
    "UserGeneralReset": "武将重生",
    "UserGeneralFragmentResolve": "武将碎片炼化",
    "UserGeneralResolve": "武将化魂",
    "UserUseExpDan": "武将使用经验丹",
    "UserGeneralResolve2": "武将、武将碎片炼化",
    "UserGeneralAwaken": "武将觉醒",
// 武将专属神器
    "UserGeneralArtifactLevel1": "专属神器强化",
// 魔宫
    "UserProtagonist2": "魔宫查询",
    "UserProtagonist2AddAttr": "魔宫主角添加属性",
    "UserProtagonist2GrowupPreveiw": "魔宫主角进阶预览",
    "UserProtagonist2Growup": "魔宫主角进阶",
    "UserEquipList": "装备背包查询",
    "UserEquipStrengthen": "装备强化",
    "UserEquipRefine": "UserEquipRefine",
    "UserEquipCollect": "装备图鉴",
    "UserEquipResolve": "装备分解",
    "UserTreasureUp": "宝物升华",
    "UserTreasureRefine": "宝物精炼",
    "UserEquipFragment": "装备碎片",
    "UserEquipFragmentCompound": "装备碎片合成",
    "UserEquipStrengthenEx": "装备一键强化",
// 书籍宝物碎片
    "UserTreasureFragmentRobQuery": "书籍宝物碎片查询",
    "UserTreasureFragmentRob": "书籍宝物碎片抢夺",
    "UserAvoidBattleTimer": "查询免战时间",
    "UserAddAvoidBattleTimer": "增加免战时间",
    "UserTreasureFragmentRob10": "UserTreasureFragmentRob10",
    "UserEquipRefineEx": "一键精炼 装备",
    "UserTreasureRefineEx": "一键精炼 宝物",
    "UserEquipReset": "装备重生",
    "UserTreasureStrengthen": "宝物强化",
    "UserTreasureRefine2": "宝物精炼",
// 道具
    "UserPropsList": "查询道具",
    "UserUseProps": "使用道具",
// 副本
    "UserCopyQuery": "普通副本查询",
    "UserCopyPrestigeReward": "声望奖励",
    "UserCopyRecoverKill": "清除副本次数",
    "UserCopyAttack2": "普通副本战斗",
    "UserCopyModUp2": "普通副本扫荡",
    "UserExpeditionQuery": "UserExpeditionQuery",
    "UserExpeditionAttack": "UserExpeditionAttack",
    "UserFriendCopyRank": "UserFriendCopyRank",
    "UserFriendCopy": "好友副本查询",
    "UserFriendCopyAttack": "好友副本攻打",
    "UserBraveCopyQuery": "UserBraveCopyQuery",
    "UserBraveCopyPrestigeReward": "UserBraveCopyPrestigeReward",
    "UserBraveCopyRecoverKill": "UserBraveCopyRecoverKill",
    "UserBraveCopyAttack2": "UserBraveCopyAttack2",
    "UserBraveCopyModUp2": "UserBraveCopyModUp2",
// 点将台
    "UserRecruit2Query": "招募查询",
    "UserRecruit2General": "武将招募",
// 竞技场
    "UserAthleticsList": "竞技场查询",
    "UserAthleticsAttack2": "竞技场战斗",
    "UserAthleticsOtherDetail": "竞技场他人详情",
    "UserAthleticsRewardsQuery3": "竞技场商店查询",
    "UserAthleticsRewardsExchange3": "竞技场商店对换",
    "UserAthleticsRankRewardsStatus": "竞技场排行奖励状态",
    "UserAthleticsBoss": "竞技场boss攻打",
// 活动
    "UserActivityQuery": "活动查询",
    "UserActivityEatChickenQuery": "蟠桃宴查询",
    "UserActivityEatChicken": "蟠桃宴领奖",
    "UserConsumeGift": "消费有礼查询",
    "UserConsumeGiftReward": "消费有礼奖励领取",
    "UserDayDayGift": "天天好礼查询",
    "UserDayDayGiftReward": "天天好礼领取",
    "UserRechargeGift": "充值有礼查询",
    "UserRechargeGiftReward": "充值有礼奖励领取",
    "UserExchangeSysQuery": "兑换系统查询",
    "UserExchangeSysExchange": "兑换系统兑换",
    "UserExchangeSysReset": "兑换系统刷新",
    "UserSignInStatus": "签到状态",
    "UserSignIn": "签到",
// 观星
    "UserWatchStarQuery": "观星查询",
    "UserWatchStarWatch": "观星",
    "UserWatchStarChange": "换星",
    "UserWatchStarGet": "观星领取星辰",
    "UserWatchStarReward": "观星领奖",
    "UserWatchStarUpLevel": "观星升档",
    "UserInviteCode": "好友邀请查询",
    "UserInviteCodeSet": "好友邀请输入邀请码",
    "UserInviteCodeReward": "领取好友邀请奖励",
    "UserCDKeyExchange": "CDKey兑换",
    "UserActivityMammonQuery": "迎财神查询",
    "UserActivityMammon": "迎财神",
    "UserActivityMammonTips": "迎财神消息推送",
    "UserMonthCard": "月卡查询",
    "UserMonthCardGet": "月卡奖励领取",
    "UserMonthCardReward": "月卡奖励查询",
    "UserMonthCardRewardGet": "月卡奖励领取",
    "UserGrowPlan": "成长计划查询",
    "UserGrowPlanBuy": "成长计划购买",
    "UserGrowPlanReward": "成长计划领奖",
    "UserRechargeDouble": "多倍充值查询",
    "UserRechargeDoubleX1": "复制多倍充值查询",
    "UserFirstRechargeReward": "领取首冲奖励",
    "UserFirestRchargeStatus": "档位首冲状态查询",
    "UserActivityStartGiftQuery": "累计登录奖励查询",
    "UserActivityStartGift": "累计登录奖励领取",
    "UserOnlineRewardQuery": "在线奖励查询",
    "UserOnlineReward": "在线奖励领取",
    "UserGrowPlanGlobal": "全名成长计划查询",
    "UserGrowPlanGlobalReward": "全民成长计划奖励领取",
// 聊天
    "UserChatQuery": "聊天查询",
    "UserChat": "聊天",
    "UserGangChatQuery": "公会聊天查询",
    "UserGangChat": "公会聊天",
// 邮件
    "UserMailList": "邮件查询",
    "UserMailRead": "邮件阅读",
    "UserMailDelete": "删除邮件",
    "UserMailSend": "发邮件",
// 商城
    "UserShopQuery": "商城查询",
    "UserShopBuy": "商城购买",
    "UserGiftBagQuery": "商城礼包查询",
    "UserGiftBagBuy": "购买商城礼包",
// 引导
    "UserGuideQuery": "新手引导查询",
    "UserGuideExcute": "新手引导",
    "UserInitGeneral": "生成主角",
    "UserChangeGender": "性别更改",
    "UserGenderQuery": "性别查询",
// 登陆奖励
    "UserContinue7Query": "连续7日奖励",
    "UserContinue7Reward": "UserContinue7Reward",
// 好友
    "UserFriendQuery": "好友显示",
    "UserFriendRecommend": "好友推荐",
    "UserFriendReq": "申请好友",
    "UserFriendReqQuery": "申请好友查询",
    "UserFriendRep": "申请好友确认",
    "UserFriendChatQuery": "好友聊天查询",
    "UserFriendChat": "好友聊天",
    "UserFriendSearch": "搜索好友",
    "UserFriendSendGift": "好友送礼",
    "UserFriendRecvGift": "好友收礼",
    "UserFriendDelete": "删除好友",
    "UserFriendAllReq": "UserFriendAllReq",
// 人物
    "UserTaskQuery": "任务查询",
    "UserTaskComplete": "任务奖励领取",
    "UserLiveness": "活跃度",
    "UserLivenessReward": "活跃度领奖",
// vip相关
    "UserVipQuery": "Vip状态查询",
    "UserBuyStamina": "购买体力",
    "UserBuyEnergy": "购买精力",
// 神魂
    "UserSoulList": "神魂列表",
    "UserSoulHuntQuery": "猎魂信息查询",
    "UserSoulHunt": "猎魂执行",
    "UserSoulExchange": "神魂置换",
    "UserSoulUpgrade": "神魂升级",
    "UserSoulHunt41": "猎魂直接到4",
    "UserSoulResolve": "武魂分解",
    "UserSlotCompoundSoul": "在阵武魂合成",
// 世界Boss1
    "UserWorldBoss1Query": "青光妖龙查询",
    "UserWorldBoss1Attack": "青光妖龙攻打",
    "UserWorldBoss1Rank": "青光妖龙伤害排名",
    "UserWorldBoss1RealNotify": "青光妖龙攻打动态",
    "UserWorldBoss1PreRank": "青光妖龙上次排行榜",
    "UserWorldBoss2Query": "炽炎朱雀查询",
    "UserWorldBoss2Attack": "炽炎朱雀攻打",
    "UserWorldBoss2Rank": "炽炎朱雀伤害排名",
    "UserWorldBoss2RealNotify": "炽炎朱雀通知",
    "UserWorldBoss2PreRank": "炽炎朱雀上次排行榜查询",
    "UserLevelRankQuery": "排行榜查询",
    "UserLevelRankStatus": "等级排行榜状态",
// 21xx 杯赛
    "UserCupStatus": "杯赛查询",
    "UserCupJoinTomorrow": "杯赛参赛",
    "UserCupTop": "强占查看",
    "UserCupBattlePlay": "观看战斗",
    "UserCupBattleReward": "杯赛领奖",
    "UserCupBattleBet": "杯赛押注",
    "UserCupBattleRewardEx": "杯赛一键领奖",
    "UserCupRank": "杯赛排名",
    "UserPenglai2": "UserPenglai2",
    "UserPenglai2GoToPos": "UserPenglai2GoToPos",
    "UserPenglai2Next": "UserPenglai2Next",
    "UserPenglai2GetTodayReward": "UserPenglai2GetTodayReward",
    "UserPenglai2Task": "UserPenglai2Task",
    "UserPenglai2TaskRewards": "UserPenglai2TaskRewards",
    "UserPenglai2Rank": "UserPenglai2Rank",
    "UserPenglai2GlobalPointRewards": "UserPenglai2GlobalPointRewards",
    "UserPenglai2GlobalPointRewardsGet": "UserPenglai2GlobalPointRewardsGet",
    "UserGang2": "公会查询",
    "UserGang2Create": "创建公会",
    "UserGang2List": "公会列表查询",
    "UserGang2Req": "申请加入公会",
    "UserGang2ReqQuery": "公会申请列表查询",
    "UserGang2Rep": "处理公会申请",
    "UserGang2Member": "公会成员查询",
    "UserGang2MSetContent1": "公会内部公告编辑",
    "UserGang2MSetContent2": "公会宣言编辑",
    "UserGang2MSetVice": "公会设置副会长",
    "UserGang2MKick": "公会开除公会成员",
    "UserGang2MPass": "降职副会长",
    "UserGang2Quit": "退出公会",
    "UserGang2Search": "搜索公会",
    "UserGang2PrayQuery": "公会拜神查询",
    "UserGang2Pray": "公会拜神",
    "UserGang2Shop": "公会商店查询",
    "UserGang2ShopBuy": "公会商店购买",
    "UserGang2Opts": "公会动态查询",
    "UserGang2Impeach": "弹劾会长",
    "UserGang2Fishpond": "公会温泉查询",
    "UserGang2FishpondFeed": "公会一键肥皂",
    "UserGang2FishpondReward": "公会温泉领奖",
    "UserGang2MSetName": "设置公会名称",
    "UserGang2DailyReward": "公会每日奖励领取",
    "UserGang2FishpondPointRank": "公会温泉贡献排行榜",
// 26xx魔王堡垒
    "UserDevilFotressStatus": "魔王堡垒状态",
    "UserDevilFotressGangDef": "魔王堡垒防御查询",
    "UserDevilFotressGangDefSet": "魔王堡垒防御设置",
    "UserDevilFotressGangDefs": "魔王堡垒查询",
    "UserDevilFotressGangProciam": "魔王堡垒宣战",
    "UserDevilFtoressTarget": "魔王堡垒（目标）状态",
    "UserDevilFotressAutoBattle": "自动战斗",
    "UserDevilFotressTargetBattle": "目标战斗",
    "NewBattleTest": "NewBattleTest",
// 50000~60000设定为与ext Server通讯命令字
    "ExtReady": "ExtReady",
    "InnerExtDisconnect": "InnerExtDisconnect",
    "ExtTaskDispath": "ExtTaskDispath",
    "ExtBattle": "ExtBattle",
    "InnerUserOffline": "InnerUserOffline",
    "InnerGatesNotifyUserOffline": "InnerGatesNotifyUserOffline",
    "MessageToGang": "MessageToGang",
// 50100~50199 预留给杯赛
    "ExtCupRoundNotify": "ExtCupRoundNotify",
    "ExtPenglai2RankRefresh": "ExtPenglai2RankRefresh",
// 50200~50299 预留给魔王堡垒
    "ExtMessageToUser": "ExtMessageToUser",
    "ExtDevilFotressAutoBattle": "ExtDevilFotressAutoBattle",
    "ExtDevilFotressTargetBattle": "ExtDevilFotressTargetBattle",
// 50 invitecode
    "AccInviteCodeRep": "AccInviteCodeRep",
    "AccInviteCodeLevelValid": "AccInviteCodeLevelValid",
    "AccInviteCodeSetRep": "AccInviteCodeSetRep",
    "AccCDKeyExchange": "AccCDKeyExchange",
    "UserMieshendianQuery": "灭神殿查询",
    "UserMieshendianBattle1": "灭神殿普通关卡战斗",
    "UserMieshendianBattle2": "灭神殿5关关卡战斗",
    "UserMieshendianModup": "灭神殿扫荡",
    "UserMieshendianModupCDClear": "灭神殿扫荡立即完成",
    "UserMieshendianRank": "灭神殿排行榜",
    "UserMieshendianReset": "灭神殿重置",
// 7日
    "UserBegin7Days": "开服7天 查询",
    "UserBegin7DaysReward": "开服7天领奖",
// 限时商店
    "UserLimitTimeShop": "限时商店查询",
    "UserLimitTimeShopBuy": "限时商店购买",
    "UserLimitTimeShopRefresh": "限时商店刷新",
// 黑市商店
    "UserBlackMarket": "黑市商店查询",
    "UserBlackMarketBuy": "黑市商店购买",
    "UserBlackMarketRefresh": "黑市商店刷新",
// 神秘商店
    "UserMystery": "神秘商店查询",
    "UserMysteryBuy": "神秘商店购买",
    "UserMysteryRefresh": "神秘商店刷新",
// 夺宝商店
    "UserRobShop": "夺宝商店查询",
    "UserRobShopBuy": "夺宝商店购买",
// 好感度
    "UserFavoriteGeneral": "查询单个武将好感当度，输入ids 如果没有ids返回默认",
    "UserFavoriteGenerals": "查询所有武将好感度",
    "UserFavoriteGeneralUseProp": "武将使用好感度道具",
    "UserFavoriteTask": "好感度成就",
    "UserFavoriteTaskGet": "好感度成就领取",
    "UserFavoriteGeneralSwap": "好感度互换",
// 签到2
    "UserSignIn2Status": "签到查询",
    "UserSignIn2": "签到",
    "UserPetQuery": "魔宠查询",
    "UserPetLevel1Up": "UserPetLevel1Up",
    "UserPetLevel2Up": "UserPetLevel2Up",
    "UserPetSet": "魔宠上阵",
    "UserPetFragment": "魔宠碎片",
    "UserPetCompound": "UserPetCompound",
    "UserPetLevel1Up2": "魔宠图鉴升级",
    "UserPetLevel2Up2": "魔宠进阶",
    "UserPetPassiveSkillQuery": "魔宠被动技能查询",
    "UserPetStudySkill": "魔宠被动技能学习",
    "UserPetCompound2": "新魔宠合成",
    "UserPetPassiveSkillLock": "魔宠被动技能锁",
    "UserPetPassiveSkillReset": "魔宠被动技能重置",
    "UserPetPassiveSkillRed": "魔宠被动技能升红",
// 奇遇
    "UserEncounterQuery": "奇遇查询",
    "UserEncounterUse": "奇遇使用",
    "UserMagicstoneUp": "神石升级",
// 洗练
    "UserEquipBaptizePreview": "装备洗炼",
    "UserEquipBaptizeConfirm": "装备洗练替换",
// 蓬莱仙岛第三版
    "UserPenglai3": "蓬莱仙岛查询",
    "UserPenglai3Dice": "蓬莱仙岛扔塞子",
    "UserPenglai3Reward": "蓬莱仙岛领奖",
    "UserPenglai3Reset": "蓬莱仙岛重置",
    "UserPenglai3Card": "蓬莱仙岛翻牌子查询",
    "UserPenglai3CardOpen": "蓬莱仙岛翻牌子开",
    "UserPenglai3CardClose": "蓬莱仙岛翻牌子关闭",
    "UserGangPointCatalogue": "帮派据点总体查询",
    "UserGangPointQuery": "帮派据点详情查询",
    "UserGangPointJoinConfirm": "帮派据点报名 确认",
    "UserGangPointJoinQuery": "查看报名",
    "UserGangPointEnterBattlefield": "帮派据点 进入战场",
    "UserGangPointJoinBattle": "参加战斗",
    "UserGangPointInspireCoin": "帮派据点 鼓舞1 coin",
    "UserGangPointInspireGold": "帮派据点 鼓舞2 gold",
    "UserGangPointBattleStatusQuery": "帮派据点 战斗状态查询",
    "UserGangPointSumBattlePlay": "帮派据点 汇总战斗播放",
    "UserGangPointSumBattleList": "帮派据点 汇总战斗分场战斗列表",
    "UserGangPointBraBattlePlay": "帮派据点 汇总战斗分场战斗播放",
    "UserGangPointAward": "帮派据点 领奖",
    "UserGangPointWelfare": "据点福利查询",
    "ExtGPMBattle": "Ext通知mbattle结果&通知Ext进行mbattle",
// 活动副本
    "UserActivityCopy": "活动副本查询",
    "UserActivityCoinCopy": "银币副本挑战",
    "UserActivityExpDanCopy": "经验丹副本挑战",
    "UserActivityForgeStoneCopy": "锻造石副本挑战",
    "UserActivityEquipStarStoneCopy": "升星石副本挑战",
    "UserZhenfuCopy": "阵符副本挑战",
    "ActivityCopyModUp": "活动副本一键完成",
// 王的男人
    "UserKingManQuery": "个人Boss活动主页查询",
    "UserKingManBattle": "个人Boss攻打",
    "UserKingManArrayQuery": "个人Boss布阵查询",
    "UserKingManArrayComfirm": "个人Boss布阵确认",
// 豪华签到
    "UserLuxurySignInStatus": "豪华签到状态查询",
    "UserLuxurySignIn": "豪华签到",
// 月基金
    "UserMonthGrowQuery": "月成长计划查询",
    "UserMonthGrowGetReward": "领取月成长计划奖励",
    "UserMonthGrowWelfareQuery": "月成长福利查询",
    "UserMonthGrowWelfareGetReward": "月成长福利领奖",
// 分享活动
    "UserShareActivityQuery": "分享活动查询",
    "UserShareActivity": "分享成功",
// 魔符系统
    "UserSigilLevelUp": "魔符升级",
    "UserSigilChangePos": "魔符更换",
// 名将副本
    "UserGeneralCopyQuery": "名将副本查询",
    "UserGeneralCopyAttack": "名将副本攻打",
    "UserGeneralCopyGetBox": "名将副本领取首次通关奖励领取",
// 法宝系统
    "UserInstrumentQuery": "法宝查询",
    "UserInstrumentUnlock": "法宝解锁",
    "UserInstrumentForgePreview": "法宝锻造预览",
    "UserInstrumentForgeConfirm": "法宝锻造确认",
// 装备进阶
    "UserEquipEvolve": "装备进阶",
//
// 珍品折扣
    "UserTitbitDiscountQury": "珍品折扣查询",
    "UserTitbitDiscountBuy": "珍品折扣兑换",
    "UserTitbitDiscountQury1": "珍品折扣1查询",
    "UserTitbitDiscountBuy1": "珍品折扣1兑换",
    "UserTitbitDiscountQury2": "珍品折扣2查询",
    "UserTitbitDiscountBuy2": "珍品折扣2兑换",
    "UserTitbitDiscountQury3": "珍品折扣3查询",
    "UserTitbitDiscountBuy3": "珍品折扣3兑换",
// 远古迷宫
    "UserMazeQuery": "远古迷宫查询",
    "UserMazeMove": "迷宫移动",
    "UserMazeRandomEvent": "随机事件",
    "UserMazeReset": "远古迷宫重置",
    "UserMazeEnemyRefresh": "刷新/查询 敌方阵容",
    "UserMazeSlotQuery": "阵容查询",
    "UserMazeSlotChange": "阵容修改",
    "UserMazeBattle": "远古迷宫战斗",
    "UserMazeShopQuery": "迷宫商店查询",
    "UserMazeShopRefresh": "迷宫商店刷新",
    "UserMazeShopBuy": "迷宫商店购买",
    "UserMazeTaskQuery": "迷宫成就奖励查询",
    "UserMazeTaskGetReward": "迷宫成就奖励领取",
// 灭神殿商店
    "UserMieshendianShop": "灭神殿商店",
    "UserMieshendianShopBuy": "灭神殿商店",
// 乾坤炉化魂，王的男人在阵武将过滤
    "UserGeneralResolveFilter": "乾坤炉化魂过滤在阵武将查询",
// 聚宝盆
    "UserCornucopiaQuery": "聚宝盆查询",
    "UserCornucopia": "聚宝盆聚宝",
    "UserCornucopiaReward": "聚宝盆宝箱领奖",
// 公会技能
    "UserGang2SkillQuery": "公会技能查询",
    "UserGang2SkillStudy": "公会技能学习",
// 推荐者容奖励
    "UserTeamRecomQuery": "阵容推荐查询",
    "UserTeamRecomReward": "阵容推荐领奖",
    "UserChatBlackLstQuery": "聊天黑名单查询",
    "UserChatBlackLstAdd": "聊天黑名单添加",
    "UserChatBlackLstDel": "聊天黑名单删除",
// 冠军试炼
    "UserTrialQuery": "冠军试炼查询",
    "UserTrialBattle": "冠军试炼战斗",
    "UserTrialNext": "冠军试炼下一关",
    "UserTrialReset": "冠军试炼重置",
    "UserTrialOpenBox": "冠军试炼开宝箱",
    "UserTrialShopQuery": "冠军试炼商店查询",
    "UserTrialShopBuy": "冠军试炼商店购买",
    "UserTrialShopRefresh": "冠军试炼商店重置",
// 过关斩将——积分赛
    "UserOverPassQuery": "积分赛查询",
    "UserOverPassRankQuery": "积分赛排行榜查询",
    "UserOverPassShopQuery": "积分赛商店查询",
    "UserOverPassShopBuy": "积分赛商店购买",
    "UserOverPassBattle": "积分赛战斗",
    "UserOverPassChangeBoss": "积分赛换对手",
    "UserOverPassGetReward": "积分赛领取宝箱奖励",
    "UserOverPassShopRefresh": "积分赛商店刷新",
    "UserFriendChatNew": "飞鸽传书查询",
    "UserFriendChatNewTag": "UserFriendChatNewTag",
// 端午嘉年华
    "UserCamivalQuery": "端午嘉年华查询",
    "UserCamivalLuckDraw": "端午嘉年华抽奖",
    "UserCamivalExchange": "端午嘉年华兑换",
// 端午扔粽子（祭贤）
    "UserZongziQuery": "端午祭贤查询",
    "UserZongzi": "端午祭贤扔粽子",
    "UserDragonBoatRaceQuery": "赛龙舟查询",
    "UserDragonBoatRaceGuess": "赛龙舟下注",
// 天天好礼2
    "UserDayDayGift2": "每日有礼查询",
    "UserDayDayGiftReward2": "每日有礼领奖",
// 老司机模板活动
    "UserOldDriverQuery": "老司机查询",
    "UserOldDriverOpt": "老司机领奖",
// 老虎鸡
    "userSpinampWinQuery": "老虎鸡查询",
    "userSpinampWinDo": "老虎鸡领奖",
    "userSpinampWinShopQuery": "老虎机商店查询",
    "userSpinampWinShopExchange": "老虎机商店兑换",
// 分享活动
    "UserActivityShare1Query": "分享活动查询",
    "UserActivityShare1Do": "分享活动操作",
    "UserActivityShare1Reward": "分享活动领奖",
// 武道会
    "UserBudokaiQuery": "武道会查询",
    "UserBudokaiMatch": "武道会匹配",
    "UserBudokaiBox": "武道会开宝箱",
    "UserBudokaiReport": "武道会战报",
    "UserBudokaiLotteryQuery": "武道会积分兑换查询",
    "UserBudokaiLotteryReward": "武道会积分兑换",
    "UserBudokaiLadderQuery": "武道会天梯段位查询",
    "UserBudokaiLadderReward": "武道会天梯段位奖励领取",
// 时装
    "UserFashionDressQuery": "时装查询",
    "UserFashionDressHide": "时装显示隐藏",
    "UserFashionDressStrange": "时装强化",
    "UserFashionDressChange": "时装更换",
    "UserFashionDressGet": "获取时装",
    "UserFashionDressActQuery": "时装活动查询",
    "UserFashionDressShopQuery": "时装商店查询",
    "UserFashionDressReset": "时装重生",
// 装备升星
    "UserEquipStar": "装备升星",
// 灵阵图
    "UserSlotSpiritQuery": "灵阵图查询",
    "UserSlotSpiritUse": "灵阵图使用",
    "UserSlotSpiritLevelup": "灵阵图升级",
    "UserSlotSpiritAdditionQuery": "灵阵图成就查询",
// 天神下凡
    "UserGodDownQuery": "天神下凡查询",
    "UserGodDownTribute": "天神下凡上香",
    "UserGodDownTributeReward": "天神下凡领取奖励",
    "UserGodDownTributeImmediate": "天神下凡立刻领取奖励",
    "UserGodDownGift": "天神下凡功德值奖励",
    "UserGodDownShopQuery": "天神下凡商店查询",
    "UserGodDownShopReward": "天神下凡商店兑换",
    "UserGodDownRankQuery": "天神下凡排行榜",
// 限时兑换
    "UserLimitTimeExchangeQuery": "限时兑换查询",
    "UserLimitTimeExchange": "限时兑换兑换",
    "UserLimitTimeExchangeRefresh": "限时兑换刷新",
// 魔王游戏厅
    "UserProtagonistGameQuery": "魔王游戏厅查询",
    "UserProtagonistGameEatBeans": "魔王游戏厅吃豆",
    "UserProtagonistGamePopcorn": "魔王游戏厅爆豆",
// Q
    "UserActivityQShopQuery": "喷他Q商店查询",
    "UserActivityQShopReward": "喷他Q商店兑换",
// 一键观星
    "UserWatchStarWatchEx": "一键观星",
// 魔罩
    "UserSlotCoverQuery": "魔罩查询",
    "UserSlotCoverup": "魔罩升级/突破",
    "UserSlotCoverMasterQuery": "魔罩恋蛋大师成就查询",
    "UserSlotCoverShop": "魔罩商店查询",
    "UserSlotCoverShopBuy": "魔罩商店购买",
    "UserSlotCoverEvolve": "魔罩进阶",
// 天庭银座,生命古树
    "UserPatrolQuery": "巡山查询",
    "UserPatrolStatus": "巡山状态",
    "UserPatrolAttack": "巡山解封挑战",
    "UserPatrolDo": "巡山开始",
    "UserPatrolReward": "巡山领取收益",
    "UserPatrolEventDo": "巡山随机事件",
    "UserPatrolQueryEx": "生命古树一键上阵查询",
    "UserPatrolDoEx": "生命古树一键上阵",
    "UserPatrolRewardEx": "生命古树一键领取",
// 中秋兑换
    "UserMidAutumnShopQuery": "中秋兑换商店查询",
    "UserMidAutumnShopReward": "中秋兑换商店兑换",
// vip福利
    "UserVipWelfareExchange": "vip福利兑换",
// 主角翅膀
    "UserWing": "主角翅膀查询",
    "UserWingUpSatr": "主角翅膀升星",
    "UserWingEvolve": "主角翅膀进阶/激活",
    "UserWingDyeing": "主角翅膀染/换色",
    "UserWingColorQuery": "翅膀颜色查询",
// 单笔充值
    "UserSingleRechargeGift": "查询",
    "UserSingleRechargeGiftReward": "领取",
// 限时成就
    "UserAchievementLimitTime": "限时成就查询",
    "UserAchievementLimitTimeReward": "限时成就领取奖励",
// 十一活动
    "UserOctober1st": "十一活动查询",
    "UserOctober1stReward": "十一活动领奖",
    "UserWorldWarPrepareQuery": "跨服战准备阶段查询",
    "UserWorldWarSubmitItem": "跨服战上交上古卷轴",
    "UserWorldWarQuery": "跨服战查询",
    "UserWorldWarRoleBattles": "跨服战个人战绩",
    "UserWorldWarPrepareUpdateSlot": "跨服战更新阵容",
    "UserWorldWarSignInfo": "跨服战本服参赛名单",
    "UserWorldWarChampionQuery": "跨服战历届冠军",
    "UserWorldWarGroupInfo": "跨服战赛区信息",
    "UserWorldWarTop": "跨服战淘汰赛",
    "UserWorldWarTopInfo": "跨服战淘汰赛观战信息",
    "UserWorldWarBattlePlay": "跨服战战报",
    "UserWorldWarTopUserInfo": "跨服战淘汰赛玩家信息",
    "UserWorldWarTopBetInfo": "跨服战淘汰赛下注信息",
    "UserWorldWarRoleReward": "跨服战个人战绩领奖",
    "UserWorldWarRank": "跨服战海选阶段本服玩家积分排名",
    "UserWorldWarWeedBet": "跨服战淘汰赛押注",
    "UserWorldWarCurrentChampionQuery": "跨服战本届冠军",
    "UserWorldWarWorship": "跨服战膜拜冠军",
    "UserWorldWarChampionSlotInfo": "跨服战冠军信息",
    "UserTriggerGiftQuery": "触发礼包查询",
    "UserTriggerGiftReward": "触发礼包兑换",
// 老用户召回
    "UserRecall": "魔王召回查询",
    "UserRecallReward": "魔王召回查询领奖",
    "UserReturn": "老玩家回归",
    "UserReturnReward": "老玩家回归领奖",
    "UserInputRecallCode": "召回码输入",
    "UserRecallCode": "召回码确认(数据添加)(用于 与acc的交互)",
// 武将升红材料查询
    "GeneralBestQuery": "武将升红材料查询",
// 周礼包月礼包
    "UserTimeGift": "周/月礼宝查询",
    "UserTimeGiftReward": "周/月礼宝领取",
// MSDK 应用宝特殊接口
    "UserMSDKArrive": "应用宝 登陆专有消息传递",
    "UserMSDKRechargeNotify": "应用宝 充值完成通知",
    "UserYSDKArrive": "应用宝 登陆专有消息传递",
    "UserYSDKRechargeNotify": "应用宝 充值完成通知",
// apple 特殊接口
    "UserInAppPurchase": "前端通知receipt",
    "AccInAppPurchase": "Acc通知结果",
    "UserRechargeGetQuery": "用户获取充值信息",
// battle分流
    "ExtBattleIO": "ExtBattleIO",
// WorldWar
    "WorldWarCollect": "跨服战报名信息收集(传给跨服战服务器)",
    "WorldWarResultNotify": "跨服战战斗结果数据接收(由跨服战服务器传回)",
    "WorldWarGameServerInfos": "WorldWarGameServerInfos",
    "WorldWarFixSignWingCollect": "翅膀修复信息收集",
    "WorldWarFixSignWingResultNotify": "翅膀修复淘汰赛信息推送",
// 双11
// 在线奖励复制活动
    "UserOnlineExt": "查询接口",
    "UserOnlineExtReward": "领奖接口",
// 复制迎财神
    "UserActivityMammonQuery_x1": "复制迎财神查询",
    "UserActivityMammon_x1": "复制迎财神消费领奖",
    "UserActivityMammonTips_x1": "复制迎财神动态查询",
// 圣诞活动
    "UserChristmasShopQuery": "圣诞活动查询",
    "UserChristmasShopReward": "圣诞活动兑换",
// 广播标签
    "UserBroadcastQuery": "聊天广播标签",
// 道具回收
    "UserPropRecovery": "道具回收",
// 嘉年华复制 大转盘
    "UserTurntableQuery": "查询",
    "UserTurntableDraw": "抽奖",
// 分档 嘉年华
    "UserDivideStallCarnivalQuery": "查询",
    "UserDivideStallCarnivalDraw": "抽奖",
// 拍卖行
    "UserAuctionHouseQuery": "拍卖行查询",
    "UserAuctionHouseAuction": "拍卖行竞拍",
    "UserAuctionHouseGet": "拍卖行一口价",
    "UserAuctionHouseLog": "拍卖行上次交易日志查询",
    "UserAuctionHouseOpts": "本次竞拍活动动态",
    "WorldAuctionHouse": "跨服拍卖数据接收",
    "WorldAuctionHouseUpdateInfo": "更新拍卖行变更信息",
    "WorldAuctionHouseDispatchGold": "返还竞拍元宝",
// 积分嘉年华
    "UserIntegralTurntableQuery": "积分转盘查询",
    "UserIntegralTurntableLuckDraw": "积分转盘抽奖",
// 累充2
    "UserTotalRechargeQuery": "累计充值2查询",
    "UserTotalRechargeGetReward": "累计充值2充值奖励领取",
// 庄园查询
    "UserManorQuery": "庄园查询",
    "UserManorFriendListQuery": "庄园好友列表查询",
    "UserManorLevelUp": "庄园建筑升级",
    "UserManorGetWood": "庄园材料领取",
    "UserManorNoticeQuery": "庄园任务栏查询/刷新",
    "UserManorNoticeGetTask": "庄园任务栏接任务",
    "UserManorNoticeDoneTask": "庄园任务栏领奖/立即完成",
    "UserManorYaoBattle": "庄园挑战小妖",
    "UserManorShop": "庄园商店查询",
    "UserManorShopExchange": "庄园商店兑换",
    "UserManorConcent": "庄园公告写入",
// 公会Boss
    "UserGang2Boss": "公会Boss",
    "UserGang2BossRank": "公会Boss公会伤害排行榜",
    "UserGang2RoleRank": "公会Boss成员贡献排行榜查询",
    "UserGang2BossInspire": "公会Boss鼓舞",
    "UserGang2BossBattle": "公会Boss挑战",
// 充值/消费返利
    "UserRebate": "充值/消费返利查询",
    "UserRebateGet": "充值/消费返利领奖",
// 回收站默认品质
    "UserRecycleBin": "回收站默认品质查询/更改",
// 装备自动洗练
    "UserEquipBaptizeFree": "装备自动洗练",
// 法宝自动锻造
    "UserInstrumentForgeFree": "法宝自动锻造",
// 跨服八戒圆梦
    "UserKGodDownQuery": "天神下凡查询",
    "UserKGodDownTribute": "天神下凡上香",
    "UserKGodDownTributeReward": "天神下凡领取奖励",
    "UserKGodDownTributeImmediate": "天神下凡立刻领取奖励",
    "UserKGodDownGift": "天神下凡功德值奖励",
    "UserKGodDownShopQuery": "天神下凡商店查询",
    "UserKGodDownShopReward": "天神下凡商店兑换",
    "UserKGodDownRankQuery": "天神下凡排行榜",
    "WorldKGodDownRank": "返还跨服排行榜数据",
// 跨服奖池大转盘
    "UserTurntableWorldQuery": "查询",
    "UserTurntableWorldDraw": "抽奖",
    "TurntableWorldGet": "跨服奖池大转盘奖池数据查询",
    "TurntableWorldRefresh": "跨服奖池大转盘奖池数据查询",
// 新服加速
    "UserNew7days": "新服加速查询",
    "UserNew7daysReward": "新服加速领奖",
// 奖池转盘中奖纪录查询
    "UserTurntableRecord": "奖池转盘中奖纪录查询",
// 魔罩排行榜数据更新
    "GameCoverRank": "魔罩排行榜数据更新",
// vip周礼包功能
    "UserVipWeekGiftQuery": "vip周礼包查询",
    "UserVipWeekGiftReward": "vip周礼包购买",
// 777游戏机
    "UserGameConsoles777Query": "777游戏机查询",
    "UserGameConsoles777reward": "777游戏机摇奖",
    "UserGameConsoles777Shop": "777游戏机商店",
    "UserGameConsoles777ShopExchange": "777游戏机商店兑换",
// 复制开服轮换活动
// 累计充值 - 原接口 2024,2025
    "UserRechargeGiftRota": "轮换累计充值查询",
    "UserRechargeGiftRotaReward": "轮换累计充值领奖",
// 天天好礼 - 原接口 2022,2023
    "UserDayDayGiftRota": "轮换天天好礼查询",
    "UserDayDayGiftRotaReward": "轮换天天好礼领奖",
// 天神下凡 - 原接口 4300,4301,4302,4303,4304,4310,4311,4320
    "UserGodDownRotaQuery": "天神下凡查询",
    "UserGodDownRotaTribute": "天神下凡上香",
    "UserGodDownRotaTributeReward": "天神下凡领取奖励",
    "UserGodDownRotaTributeImmediate": "天神下凡立刻领取奖励",
    "UserGodDownRotaGift": "天神下凡功德值奖励",
    "UserGodDownRotaShopQuery": "天神下凡商店查询",
    "UserGodDownRotaShopReward": "天神下凡商店兑换",
    "UserGodDownRotaRankQuery": "天神下凡排行榜",
// 老虎鸡 - 原接口 1406,1407,1408,1409
    "UserSpinampWinRotaQuery": "轮换老虎机查询",
    "UserSpinampWinRotaDo": "轮换老虎机领奖",
    "UserSpinampWinRotaShopQuery": "轮换老虎机商店查询",
    "UserSpinampWinRotaShopExchange": "轮换老虎机商店兑换",
// 限时成就 - 原接口 3760,3761
    "UserAchievementLimitTimeRota": "限时成就查询",
    "UserAchievementLimitTimeRotaReward": "限时成就领取奖励",
// 珍品折扣 - 原接口 4010,4011
    "UserTitbitDiscountRotaQury": "珍品折扣查询",
    "UserTitbitDiscountRotaBuy": "珍品折扣兑换",
// 老司机模板活动 - 原接口 1404,1405
    "UserOldDriverRotaQuery": "轮换老司机查询",
    "UserOldDriverRotaOpt": "轮换老司机领奖",
// 双倍充值 - 原接口 2097
    "UserRechargeDoubleRota": "轮换多倍充值查询",
// 喷他Q - 原接口 4400,4401
    "UserActivityQRotaShopQuery": "喷他Q商店查询",
    "UserActivityQRotaShopReward": "喷他Q商店兑换",
// 嘉年华复制 大转盘 - 原接口 4630,4631
    "UserTurntableRotaQuery": "轮换奖池转盘查询",
    "UserTurntableRotaDraw": "轮换奖池转盘抽奖",
// 消费有礼 - 原接口 2020,2021
    "UserConsumeGiftRota": "轮换消费有礼查询",
    "UserConsumeGiftRotaReward": "轮换消费有礼领奖",
// 充值/消费返利 - 原接口 4850,4851
    "UserRebateRota": "轮换充值/消费返利查询",
    "UserRebateRotaGet": "轮换充值/消费返利领奖",
// 限时商店 - 原接口 3615,3616,3617
    "UserLimitTimeShopRota": "轮换显示商店查询",
    "UserLimitTimeShopRotaBuy": "轮换显示商店购买",
    "UserLimitTimeShopRotaRefresh": "轮换显示商店刷新",
// 登陆奖励 - 原接口 212,213
    "UserContinue7RotaQuery": "轮换连续7日查询",
    "UserContinue7RotaReward": "轮换连续7日领奖",
// 新服加速 - 原接口 4880,4881
    "UserNew7daysRota": "轮换新服加速查询",
    "UserNew7daysRotaReward": "轮换新服加速领奖",
// 单笔充值 - 原接口 3750,3751
    "UserSingleRechargeGiftRota": "轮换单充送礼查询",
    "UserSingleRechargeGiftRotaReward": "轮换单充送礼领取",
// 限时兑换 - 原接口 3710,3711，3712
    "UserLimitTimeExchangeRotaQuery": "轮换限时兑换查询",
    "UserLimitTimeExchangeRota": "轮换限时兑换兑换",
    "UserLimitTimeExchangeRotaRefresh": "轮换限时兑换刷新",
// 累充 - 原接口 4860,4861
    "UserTotalRechargeRotaQuery": "轮换累计充值2查询",
    "UserTotalRechargeRotaGetReward": "轮换累计充值2充值奖励领取",
// 积分嘉年华 - 原接口 4660,4661
    "UserIntegralTurntableRotaQuery": "轮换积分转盘查询",
    "UserIntegralTurntableRotaLuckDraw": "轮换积分转盘抽奖",
// 神龙许愿
    "UserDragonWishingQuery": "升龙许愿查询",
    "UserDragonWishingGet": "神龙许愿摇骰子",
    "UserDragonWishingReward": "神龙许愿领大奖",
    "UserDragonWishingEvent": "神龙许奇遇事件",
    "UserDragonWishingEventClose": "升龙许奇遇事件关闭",
    "UserDragonWishingShop": "神龙许愿商店购买",
// 公会玩法,打地鼠
    "UserGang2GroundhogQuery": "打地鼠游戏状态查询",
    "UserGang2GroundhogStart": "打地鼠开始游戏",
    "UserGang2GroundhogGetHogs": "打地鼠获取地鼠",
    "UserGang2GroundhogCatchHog": "打地鼠抓到地鼠",
    "UserGang2GroundhogIntegalBoxRewards": "打地鼠积分宝箱奖励领取",
    "UserGang2GroundhogRank": "打地鼠排行榜",
    "UserGang2GroundhogGameOver_New": "打地鼠本局游戏结束",
// 英雄挑战
    "UserHeroBossQuery": "英雄挑战整体查询",
    "UserHeroBossFollow": "英雄挑战关注",
    "UserHeroBossEnter": "英雄挑战进入",
    "UserHeroBossAttack": "英雄挑战战斗",
    "UserHeroBossCheer": "英雄挑战助威",
    "UserHeroBossRank": "英雄挑战排行",
    "UserHeroBossRealNotify": "UserHeroBossRealNotify",
    "UserHeroBossAwardRecord": "英雄挑战大奖查询",
    "UserHeroBossRevive": "UserHeroBossRevive",
    "UserHeroBossDoubleBattle": "双倍挑战勾选",
// 道馆
    "UserDaoGuanQuery": "打开道馆活动",
    "UserDaoGuanAward": "领取徽章奖励",
    "UserDaoGuanEnter": "进入道馆",
    "UserDaoGuanAttack": "挑战",
    "UserDaoGuanRecord": "查看战报",
    "UserDaoGuanArrayQuery": "打开布阵",
    "UserDaoGuanArrayComfirm": "UserDaoGuanArrayComfirm",
// 周年庆
    "UserAnniversaryQuery": "周年庆查询",
    "UserAnniversaryWish": "周年庆许愿",
    "UserAnniversaryTakenTask": "周年庆任务领取",
    "UserAnniversaryTakenTaskReward": "周年庆任务领奖",
    "UserAnniversaryRefreshTask": "周年庆任务刷新",
    "UserAnniversaryTaskCancel": "周年庆任务取消",
// 超值回馈礼包
    "UserFeedbackGiftQuery": "超值回馈礼包查询",
    "UserFeedbackGiftBuy": "购买礼包",
    "UserFeedbackGiftBoxReward": "领取奖励",
// 终身充值
    "UserRecharge4LifetimeQuery": "终身充值查询接口",
    "UserRecharge4LifetimeTakeRewards": "终身充值奖励领取接口",
// 招募商店
    "UserRecruitShopQuery": "招募商店查询",
    "UserRecruitShopExchange": "招募商店兑换",
// 种树
    "UserPlantTreesQuery": "种树查询",
    "UserPlantTreesatering": "浇水",
    "UserPlantTreesTakeTask": "种树接任务",
    "UserPlantTreesTakenTaskReward": "种树完成任务",
    "UserPlantTreesTaskCancel": "取消任务",
    "UserPlantTreesBuyWaterDrop": "购买水滴",
    "UserPlantTreesRefreshTask": "种树刷新任务",
    "UserPlantTreesTakenBoxReward": "种树领取档位宝箱",
    "UserPlantTreesRankQuery": "种树积分排行榜",
// 防沉迷
    "UserAnti_addiction": "防沉迷在线时长查询/推送",
    "UserVerifiedRewardQuery": "实名认证奖励状态查询",
    "UserVerifiedReward": "实名认证奖励领取",
    "AccVerifiedRewardSta": "实名认证acc返回数据接收",
    "AccVerifiedlogin": "acc传回  防沉迷 顶号",
    "UserAntiGamblingPropGet": "防赌博道具购买",
    "UserAntiGamblingRewardRecord": "防赌博大奖记录"
};
var system_dict = null;

var id_name = {};
function get_id_name() {
    $.ajax({
        type: 'get',
        async: false,
        url: '/config/displayexcel/by/filename',
        data: {
            file_name: 'ID_dictionary'
        },
        dataType: 'JSON',
        success: function (data) {
            var detail_data = data['data'];
            for (i in detail_data) {
                id_name[detail_data[i][0].toString()] = detail_data[i][2]
            }

        }
    })
}
get_id_name();

getGameServerData($select_game, 1);

handleDatePickers();
handleTimePickers();
$("#q_date").val(getNowFormatDate(0));

$("#start_time").val("00:00:00");
$("#end_time").val("23:59:59");


function query_log_details(tag, q_date) {
    var server_id = $select_game.val();
    var details_ = $("#details_" + tag);
    var temp_html = details_.html();
    if (details_.hasClass("hidden")) {
        details_.removeClass("hidden");
    } else {
        details_.addClass("hidden");
    }

    if (temp_html.length === 0) {
        var page_content = $('.page-content');
        App.blockUI(page_content, false);
        $.ajax({
            type: 'get',
            url: '/queryrolelogdetails',
            data: {
                server_id: server_id,
                q_date: q_date
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var inform_list = data["data"];
                var html_str = "";
                if (data["data"].length === 0) {
                    html_str = "空";
                }
                else {
                    var use_info = 'failed';
                    for (var i = 0; i < inform_list.length; i++) {
                        var temp = inform_list[i];
                        var temp_split = [];
                        var temp_info = "";
                        var name_value = "";
                        var slice_num = 0;
                        if (['msdk2'].indexOf(PLATFORM_NAME) >= 0) {
                            slice_num = 1
                        }
                        if (temp.indexOf("[prop][get]") > -1) {
                            // ('[prop][get]', 20055, 15, 'default', 15L)
                            temp_split = temp.split(",").slice(slice_num);
                            name_value = id_name[temp_split[1].replace(/\s+/g, "")];
                            if (name_value === undefined) {
                                name_value = temp_split[1].replace(/\s+/g, "")
                            }
                            temp_info = "获得" + temp_split[2] + "个" + name_value + " ,剩余" + temp_split[4].slice(0, -2).replace("L", "").replace(")", "") + "个";
                        } else if (temp.indexOf("[prop][use]") > -1) {
                            // ('[prop][use]', 20343, 1, 'default', 18L)
                            temp_split = temp.split(",").slice(slice_num);
                            name_value = id_name[temp_split[1].replace(/\s+/g, "")];
                            if (name_value === undefined) {name_value = temp_split[1].replace(/\s+/g, "")}
                            temp_info = "消耗" + temp_split[2].replace("L", "") + "个" + name_value + ", 剩余" + temp_split[4].slice(0, -2).replace("L", "").replace(")", "") + "个";
                        } else if (temp.indexOf("[coin][get]") > -1) {
                            // ('[coin][get]', 1097891L, 2000, 'default', 3334837L)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "通过" + temp_split[3] + "获得" + temp_split[2] + "个银币 ,剩余" + temp_split[4].replace("L", "").replace(")", "") + "个";
                        } else if (temp.indexOf("[gold][get]") > -1) {
                            // ('[gold][get]', 1099958L, 20, 'GetReward', 3447L)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "通过" + temp_split[3] + "获得" + temp_split[2] + "个元宝 ,剩余" + temp_split[4].replace("L", "").replace(")", "") + "个";
                        } else if (temp.indexOf("[generalbest][get]") > -1) {
                            // ('[generalbest][get]', 18825, 1, 'GetReward', 54L)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "通过" + temp_split[3] + "获得" + temp_split[2] + "个武将精华 ,剩余" + temp_split[4].replace("L", "").replace(")", "") + "个";
                        } else if (temp.indexOf("[general][create]") > -1) {
                            // ('[general][create]', 2024823L, 10506)
                            temp_split = temp.split(",").slice(slice_num);
                            name_value = id_name[temp_split[2].replace(/\s+/g, "")];
                            if (name_value === undefined) {name_value = temp_split[2].replace(/\s+/g, "")}
                            temp_info = "获得新武将" + name_value
                        } else if (temp.indexOf("[exp][get]") > -1) {
                            // ('[exp][get]', 1099732L, 6, False, 0)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "获得" + temp_split[4].replace(")", "") + "队伍经验"
                        } else if (temp.indexOf("[Integral][get]") > -1) {
                            // ('[Integral][get]', 1100199L, 20)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "获得" + temp_split[2].replace(")", "") + "充值积分"
                        } else if (temp.indexOf("[prestige][get]") > -1) {
                            // ('[prestige][get]', 1100199L, 20)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "获得" + temp_split[2].replace(")", "") + "竞技场积分"
                        } else if (temp.indexOf("[energy][get]") > -1) {
                            // ('[energy][get]', 1099347L, 1)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "获得" + temp_split[2].replace(")", "") + "杀气"
                        } else if (temp.indexOf("[stamina][get]") > -1) {
                            // ('[stamina][get]', 1099870L, 200)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "获得" + temp_split[2].replace(")", "") + "体力"
                        } else if (temp.indexOf("[athletics][get]") > -1) {
                            // ('[athletics][get]', 1099417L, 3)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "获得" + temp_split[2].replace(")", "") + "竞技场挑战次数"
                        } else if (temp.indexOf("[generalfragment][get]") > -1) {
                            // ('[generalfragment][get]', 10554, 1, 6L)
                            temp_split = temp.split(",").slice(slice_num);
                            name_value = id_name[temp_split[1].replace(/\s+/g, "")];
                            if (name_value === undefined) {name_value = temp_split[1].replace(/\s+/g, "")}
                            temp_info = "获得" + temp_split[2] + "个" + name_value + " ,剩余" + temp_split[3].replace("L", "").replace(")", "") + "个";
                        } else if (temp.indexOf("[coin][use]") > -1) {
                            // ('[coin][use]', 1098082L, 10000, 383L)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "消耗" + temp_split[2] + "个银币, 剩余" + temp_split[3].replace("L", "").replace(")", "") + "个";
                        } else if (temp.indexOf("[gold][use]") > -1) {
                            // ('[gold][use]', 1089315L, 10, 1365L)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "消耗" + temp_split[2] + "个元宝, 剩余" + temp_split[3].replace("L", "").replace(")", "") + "个";
                        } else if (temp.indexOf("[stamina][use]") > -1) {
                            // ('[stamina][use]', 1083438L, 5)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "消耗" + temp_split[2].replace(")", "") + "个体力"
                        } else if (temp.indexOf("[energy][use]") > -1) {
                            // ('[energy][use]', 1100203L, 10)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "消耗" + temp_split[2].replace(")", "") + "个杀气"
                        } else if (temp.indexOf("[prestige][use]") > -1) {
                            // ('[prestige][use]', 1098218L, 600)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "消耗" + temp_split[2].replace(")", "") + "个竞技场积分"
                        } else if (temp.indexOf("[red_item][use]") > -1) {
                            // ('[red_item][use]', 1083438L, 5)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "消耗" + temp_split[2].replace(")", "") + "个红将精华"
                        } else if (temp.indexOf("[athletics][use]") > -1) {
                            // ('[athletics][use]', 1099708L, 1)
                            temp_split = temp.split(",").slice(slice_num);
                            temp_info = "消耗" + temp_split[2].replace(")", "") + "个竞技场挑战次数"
                        } else if (temp.indexOf("[generalfragment][use]") > -1) {
                            // ('[generalfragment][use]', 10505, 0, 4L)
                            temp_split = temp.split(",").slice(slice_num);
                            name_value = id_name[temp_split[1].replace(/\s+/g, "")];
                            if (name_value === undefined) {name_value = temp_split[1].replace(/\s+/g, "")}
                            temp_info = "消耗" + temp_split[2] + "个" + name_value + " ,剩余" + temp_split[3].replace("L)", "") + "个";
                        } else if (temp.indexOf("('GetReward") > -1) {
                            // ('GetReward', 'rid:1000853', 33001, 4)
                            if (inform_list[i+1].indexOf("[prop][get]") > -1) {
                                continue
                            }
                            temp_split = temp.split(",").slice(slice_num);
                            name_value = id_name[temp_split[2].replace(/\s+/g, "")];
                            if (name_value === undefined) {name_value = temp_split[2].replace(/\s+/g, "")}
                            temp_info = "获得" + temp_split[3].replace(")", "") + "个" + name_value
                        }

                        if (temp_info) {
                            html_str += "<p>" + temp_info + "</p>";
                            use_info = 'success';
                        }
                    }
                    if (use_info === "failed") {
                        for (var x = 0; x < inform_list.length; x++) {
                            var b = inform_list[x];
                            html_str += "<p>" + b + "</p>";
                        }
                    }
                }
                details_.html(html_str);
                details_.removeClass("hidden");
            }
        });
    }
}


var i = 1;
$("#btn_add").on("click", function (e) {
    e.preventDefault();
    var str_id = "call_func_" + i;
    var s = $("#" + str_id);
    var html_str = "";
    html_str += "<label class='control-label col-md-3'> <span class='required'> </span></label>";
    html_str += "<div class='col-md-3'>";
    html_str += "<div class='input-icon'>";
    html_str += "<i class='fa fa-user'></i>";
    html_str += "<input class='form-control' name='call_func' placeholder='过滤关键字' type='text'/>";
    html_str += "</div>";
    html_str += "</div>";
    i += 1;
    var next_str_id = "call_func_" + i;
    s.after("<div class=\"form-group\" id=" + next_str_id + "></div>");
    $("#" + next_str_id).html(html_str);
});


var get_role_log = function () {
    var server_id = $select_game.val();
    var r_role = $role_id_info_1.val();
    var q_date = $("#q_date").val();
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();
    if (!isNaN(r_role) == false) {
        $('.alert-danger span').html("角色ID必须为数字.");
        $('.alert-danger').show();
        return;
    }
    else {
        $('.alert-danger').hide();
    }
    var call_func = "";
    //过滤关键字
    $("input[name='call_func']").each(function () {
        var call_str = $(this).val();
        if (call_str.length != 0) {
            call_func += call_str + ",";
        }
    });
    call_func = call_func.substring(0, call_func.length - 1);


    var success = function (data) {
        var str_html = "";
        for (var i = 0; i < data.length; i++) {
            str_html += "<tr>";
            str_html += "<td>" + data[i][0] + "</td>";
            var name = OPERATE_TYPE[data[i][1]];
            if (name == undefined) {
                name = data[i][1];
            }
            str_html += "<td class='success'>" + "<a onclick=\"query_log_details(" + i + ",'" + data[i][2] + "')\">" + name + "</a>" + "</td>";
            str_html += "<td>" + data[i][2] + "</td>";
            str_html += "</tr>";

            str_html += "<tr>";
            str_html += "<td id='details_" + i + "' colspan='3' class=\"text-center hidden \"></td>";
            str_html += "</tr>";
        }
        $("#role_log_list2").html(str_html);
    };

    var data = {
        server_id: server_id,
        r_role: r_role,
        q_date: q_date,
        start_time: start_time,
        end_time: end_time,
        call_func: call_func
    };

    my_ajax(true, '/queryrolelog', 'get', data, true, success);
};


var get_role_log2 = function () {
    var server_id = $select_game.val();
    var r_role = $role_id_info_1.val();
    var q_date = $("#q_date").val();
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();
    if (!isNaN(r_role) == false) {
        $('.alert-danger span').html("角色ID必须为数字.");
        $('.alert-danger').show();
        return;
    }
    else {
        $('.alert-danger').hide();
    }
    var call_func = "";
    //过滤关键字
    $("input[name='call_func']").each(function () {
        var call_str = $(this).val();
        if (call_str.length != 0) {
            call_func += call_str + ",";
        }
    });
    call_func = call_func.substring(0, call_func.length - 1);


    var success = function (result) {
        var status = result['status'];
        var data = result['msg'];
        var title_name = ['ctime', 'uid', 'func_name', 'content'];
        if (status === 'success') {
            var str_html = "";
            for (var i = 0; i < data.length; i++) {
                str_html += "<tr>";
                for (var k = 0; k < title_name.length; k++) {
                    var row_data = '';
                    if (k === 3) {
                        row_data = data[i][title_name[k]].replace(/\r/g, "</br>")
                    } else {
                        row_data = data[i][title_name[k]]
                    }
                    str_html += "<td>" + row_data + "</td>";
                }
                str_html += "</tr>";
            }
            $("#role_log_list2").html(str_html);
        } else {
            show_error_modal(0, data);
        }

    };

    var data = {
        server_id: server_id,
        r_role: r_role,
        q_date: q_date,
        start_time: start_time,
        end_time: end_time,
        call_func: call_func
    };
    $('#role_log_list2').html('');
    my_ajax(true, '/queryrolelog', 'get', data, true, success);
};


$("#btn_rolelog").on("click", function (e) {
    e.preventDefault();
    get_role_log();
});


$("#export_rolelog").on("click", function (e) {
    e.preventDefault();
    var server_id = $select_game.val();
    var r_role = $("#r_role").val();
    var q_date = $("#q_date").val();
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();

    var export_title = "";
    $("#export_title").children().each(function (e) {
        export_title += $(this).html() + ",";
    });
    $.ajax({
        type: 'get',
        url: '/exportrolelog',
        data: {
            server_id: server_id,
            r_role: r_role,
            q_date: q_date,
            start_time: start_time,
            end_time: end_time,
            export_title: export_title
        },
        dataType: 'JSON',
        success: function (data) {
            window.open(data["url"]);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
});

var operate = "全部";

function init_system() {
    if (system_dict == null) {
        $.ajax({
            type: 'get',
            url: '/querysystemparam',
            dataType: 'JSON',
            success: function (data) {
                system_dict = data;
                var str_html = "";
                for (var u in data) {
                    str_html += "<option value='" + data[u]["id"] + "'>" + data[u]["name"] + "</option>";
                }
                $("#select_system").html(str_html);
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
}

init_system();


var j = 1;
$("#btn_select_add").on("click", function (e) {
    e.preventDefault();
    var str_id = "select_" + j;
    var s = $("#" + str_id);
    var html_str = "";
    html_str += "<label class='control-label col-md-3'></label>";
    html_str += "<div class='col-md-3'>";
    html_str += "<select id='select_system_" + j + "' name='select_system' class='form-control input-medium'>";
    for (var u in system_dict) {
        html_str += "<option value='" + system_dict[u]["id"] + "'>" + system_dict[u]["name"] + "</option>";
    }
    html_str += "</select>";
    html_str += "</div>";
    html_str += "</div>";
    j += 1;
    var next_str_id = "select_" + j;
    s.after("<div class=\"form-group\" id=" + next_str_id + "></div>");
    $("#" + next_str_id).html(html_str);
});


function get_call_fun(call_type_list) {
    console.log("111111111", call_type_list);
    var call_func = "";
    $.ajax({
        type: 'get',
        url: '/querycallfunc',
        async: false,
        data: {
            call_type_list: JSON.stringify(call_type_list)
        },
        dataType: 'JSON',
        success: function (data) {
            for (var n = 0; n < data.length; n++) {
                call_func += data[n] + ",";
            }
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
    call_func = call_func.substring(0, call_func.length - 1)
    return call_func;
}


var query_role_info = function (this_div, other_div, server_div, role_type) {
    var success = function (data) {
        if (data) {
            if (role_type === 'role_id') {
                other_div.val(data['name']);
            } else if (role_type === 'role_name') {
                other_div.val(data['id']);
            } else {
                other_div.val('');
            }
        } else {
            other_div.val('')
        }
    };
    var server_id = server_div.val();
    var role_search = this_div.val();
    var data = {role_type: role_type, role_search: role_search, server_id: server_id};
    if (role_search.length > 0) {
        my_ajax(true, "/getroleinfo", 'get', data, true, success);
    } else {
        other_div.val('')
    }
};

$select_game.bind('change', function () {
    var div_1 = $('#role_info_1').find('.current_input');
    var role_type = (div_1.attr('placeholder') === '角色名') ? 'role_name' : 'role_id';
    query_role_info(div_1, div_1.parent().siblings().find('input'), $select_game, role_type)
});
$role_id_info_1.bind("blur", function () {
    var inner_this_div = $(this);
    query_role_info(inner_this_div, $role_name_info_1, $select_game, 'role_id')
});


$("#cdkey_start_date").val(getNowFormatDate(7));
$("#cdkey_end_date").val(getNowFormatDate(0));


var select_ctype_data = {
    1: "活动卡1(同一账号,单区领取)",
    2: "活动卡2(同一账号,多区领取)",
    3: "活动卡3(同一账号,多区同类型领取)"
};


var query_excharge_log = function () {
    var ajax_source = "/cdkey/records";
    var aoColumns = [
        {
            "mDataProp": "sid",
            'sClass': 'center',
            "sTitle": "用户标识码"
        },
        {
            "mDataProp": "id2",
            'sClass': 'center',
            "sTitle": "区服"
        },
        {
            "mDataProp": "id3",
            'sClass': 'center',
            "sTitle": "角色ID"
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "类型"
        },
        {
            "mDataProp": "code",
            'sClass': 'center',
            "sTitle": "兑换码"
        },
        {
            "mDataProp": "ctype",
            'sClass': 'center',
            "sTitle": "兑换码类型"
        },
        {
            "mDataProp": "etime",
            'sClass': 'center',
            "sTitle": "兑换时间"
        }
    ];
    var server_id = $("#server_id").val();
    var role_id = $("#role_id").val();
    var cdkey = $("#cdkey").val();
    var start_time = $("#cdkey_start_date").val();
    var end_time = $("#cdkey_end_date").val();
    var data = {
        server_id: server_id,
        role_id: role_id,
        cdkey: cdkey,
        start_time: start_time,
        end_time: end_time,
        ctype: 0
    };
    var fnRowCallback = function (nRow, aData) {
        var str_html1 = select_ctype_data[aData.ctype];
        $('td:eq(5)', nRow).html(str_html1);


    };
    dataTablePage($("#excharge_log_table"), aoColumns, ajax_source, data, false, fnRowCallback);
    // App.unblockUI($page_content);
};


$("#excharge_button").bind("click", function(e){
    e.preventDefault();
    // App.blockUI($page_content, false);
    query_excharge_log();


});
