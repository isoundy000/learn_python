#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
"""
注意:key的最后一位必须为数字（user id或game id）
redis数据key的规范：
  基本格式： <logic name>:<key type>:<swap policy>:<user id>
    说明：
      各分段之间必须使用“:”(英文半角冒号）进行分割

      logic name   : 业务逻辑自定义部分，任何有效的名称均可

      key type       : 当前key的数据类型，枚举类型（一个小写英文字符），可以为
              s    — String 字符串
              h    — Hash键值(key=>value)对集合
              l    — List 数组列表
              e  — Set 哈希无序集合
              z  — ZSet 哈希有序集合

      swap policy  : 热转冷时的执行策略，枚举类型（一个小写英文字符），可以为
              s  — save 需要转入冷库的数据
              n  — not save 不需要转入冷库的数据
              p  — passby 不需要处理，忽律的数据

      user id    : 用户的UserId，数字类型

    示例：
      game:6:h:s:10001  — 用户10001的游戏6的主数据，Hash类型，需要热转冷保存
      weak:6:s:n:10001  — 用户10001的临时数据，字符串类型，不需要进入冷库
      rank:z:p:6    — 游戏6的排行榜数据，不需要冷热处理，忽略掉
"""

class GameData:
    """
    存储在gamedata:gameId:userId数据库中的key值
    """
    # 上次登录时间（大厅默认字段，无用）
    lastlogin = "lastlogin"
    # 连续登录天数（大厅默认字段，无用）
    nslogin = "nslogin"
    # 用户经验值
    exp = "exp"
    # 用户等级
    level = "level"
    # 最近一次已拥有的皮肤炮列表（配合过期提示用）(经典和千炮模式共享)
    ownGunSkins = "ownGunSkins"                     # [1288, 1165, 1167, 1166]
    # # 最近一次已拥有的千炮皮肤炮列表（配合过期提示用）
    # ownGunSkins_m = "ownGunSkins_m"
    # 已拥有的皮肤炮皮肤(经典和千炮模式共享)
    ownGunSkinSkins = "ownGunSkinSkins"             # [1366]
    # # 已拥有的千炮皮肤炮皮肤
    # ownGunSkinSkins_m = "ownGunSkinSkins_m"
    # 已发送了过期提示弹窗的皮肤炮(经典和千炮模式共享)
    promptedGunSkins = "promptedGunSkins"
    # # 已发送了过期提示弹窗的千炮皮肤炮
    # promptedGunSkins_m = "promptedGunSkins_m"
    # 已解锁皮肤炮列表(经典和千炮模式共享)
    unlockedGunSkins = "unlockedGunSkins"
    # # 已解锁千炮皮肤炮列表
    # unlockedGunSkins_m = "unlockedGunSkins_m"
    # 用户最大火炮等级
    gunLevel = "gunLevel"                           # 用户最大火炮等级
    # 用户最大千炮倍率
    gunLevel_m = "gunLevel_m"
    # 用户当前皮肤炮ID
    gunSkinId = "gunSkinId"                 # 使用的皮肤炮ID
    # 用户当前千炮皮肤炮ID
    gunSkinId_m = "gunSkinId_m"
    # 当前玩家在经典渔场中的火炮等级
    nowGunLevel = "nowGunLevel"
    # 当前玩家在千炮渔场中的火炮倍率
    nowGunLevel_m = "nowGunLevel_m"
    # 皮肤炮奖池数据
    gunSkinPool = "gunSkinPool"
    # 用户注册时间戳
    registTime = "registTime"
    # 用户上次登录时间戳
    lastloginTime = "lastloginTime"
    # 用户累计登录天数
    loginDays = "loginDays"
    # 用户连续登录天数
    continuousLogin = "continuousLogin"
    # 红包任务邀请到的玩家列表
    redInvitePlayers = "redInvitePlayers"
    # 新手任务状态
    redState = "redState"
    # 宝箱累计开启次数
    openChestCount = "openChestCount"
    # 客户端当前版本号
    clientVersion = "clientVersion"
    # 服务端当前版本号
    serverVersion = "serverVersion"
    # 微信小游戏的客户端系统
    platformOS = "platformOS"
    # 分享信用值
    creditValue = "creditValue"
    # 金猪分享完成次数
    flyPigFinishCount = "flyPigFinishCount"
    # 已完成引导步骤列表
    userGuideStep = "userGuideStep"
    # 是否为限制区域
    isLocationLimit = "isLocationLimit"
    # 渔场任务数据
    tableTask = "tableTask:%d"
    # 是否显示VIP等级
    vipShow = "vipShow"
    # 新手任务期间捕获奖券鱼次数
    catchCouponFishCount = "catchCouponFishCount"
    # 红包任务是否提前完成
    redAdvanceOpen = "redAdvanceOpen"
    # 上次选择的房间类型
    lastRoomType = "lastRoomType"
    # 收到感谢信次数
    ThanksLetterNum = "ThanksLetterNum"
    # 领取感谢信奖励次数
    ThanksLetterRewardNum = "ThanksLetterRewardNum"
    # 已邀请玩家列表
    inviteList = "inviteList"
    # 邀请记录自增ID
    inviteId = "inviteId"
    # 用户是否关注了微信公众号
    followAccount = "followAccount"
    # 充值次数
    rechargeCount = "rechargeCount"
    # 充值奖池数据
    rechargeBonus = "rechargeBonus"
    # 是否发送过解锁全渔场弹窗
    roomUnlock = "roomUnlock"
    # 可领取的普通、升级礼包ID数据
    availableGift = "availableGift"
    # 限时礼包数据
    limitTimeGift = "limitTimeGift"
    # 已购买的普通、升级礼包ID数据
    normalGift = "normalGift"
    # 月卡礼包数据
    monthCardGift = "monthCardGift"
    # 破产礼包
    brokeGift = "brokeGift"
    # 升级礼包
    levelUpGift = "levelUpGift"
    # 月卡是否为首次领取
    firstGet = "firstGet"
    # 动态概率数据
    dynamicOdds = "dynamicOdds4"
    # 存在充值奖池时的概率数据
    rechargeOdds = "rechargeOdds"
    # 各渔场最近多次动态概率曲线涨跌
    recentWaveStateDict = "recentWaveStateDict"
    # 玩家在各场次的金币宝箱奖池
    profitChest = "profitChest"
    # 当前玩家在渔场选择的倍率
    nowFpMultiple = "nowFpMultiple"
    # 使用弹头时是否重置为低概率曲线
    limitedDynamicOdds = "limitedDynamicOdds"
    # 合金飞弹使用次数
    useMissileCount = "useMissileCount"
    # 渔友竞技历史记录数据
    fightHistory = "fightHistory"
    # 渔友竞技记录自增ID
    fightHistoryId = "fightHistoryId"
    # 签到天数
    checkinDay = "checkinDay"
    # 连续签到天的时间戳
    continuousCheckinDayTS = "continuousCheckinDayTS"
    # 中断连续签到的时间戳
    breakContinuousCheckinTS = "breakContinuousCheckinTS"
    # 邮箱-收件箱数据, 存储系统邮件
    mailInfos = "mailInfos"
    # 邮箱-收件箱数据，存储玩家发送的邮件
    userMailInfos = "userMailInfos"
    # 收件记录自增ID
    mailId = "mailId"
    # 邮箱-发件箱数据
    outMailInfos = "outMailInfos"
    # 发件记录自增ID
    outMailId = "outMailId"
    # 已购买VIP礼包的VIP等级列表
    vipGiftBought = "vipGiftBought"
    # 七日幸运榜玩家最近上榜时间
    luckyEggs7RkTime = "luckyEggs7RkTime"
    # 七日赢家榜用户个人数据
    robbery7winmost = "robbery7winmost"
    # 金币商城购买各商品次数
    buyCoinCount = "buyCoinCount"
    # 宝箱商城购买各宝箱次数
    buyChestCount = "buyChestCount"
    # 珍珠商城购买各商品次数
    buyPearlCount = "buyPearlCount"
    # 限时商城购买各商品次数
    buyTimeLimitedCount = "buyTimeLimitedCount"
    # 5元话费卡兑换次数
    exchangeCount = "exchangeCount"
    # 海星许愿幸运值（旧版）
    wishLuckyValue = "wishLuckyValue"
    # 招财模式火炮等级
    robberyGunLevel = "robberyGunLevel"
    # 招财试玩模式火炮等级
    robberyTrialGunLevel = "robberyTrialGunLevel"
    # 是否领取了惊喜礼包（微信我的小程序进入奖励）
    surpriseGift = "surpriseGift"
    # 海星转盘数据
    starfishRoulette = "starfishRoulette"
    # 此次登录是否领取了普通礼包
    alreadyTakenNormalGift = "alreadyTakenNormalGift"
    # 招财模式充值奖池
    robberyRechargePool = "robberyRechargePool"
    # vip赠送物品数量
    vipPresentCount = "vipPresentCount:%d"
    # 免费海星许愿次数
    freeRouletteTimes = "freeRouletteTimes"
    # 获得掉落珍珠的数量
    dropPearlCount = "dropPearlCount"
    # 购买普通礼包时间戳（上一次领取普通礼包时间戳）
    buyGiftTimestamp = "buyGiftTimestamp"
    # 已过期礼包
    expiredGift = "expiredGift"
    # 即将过期礼包
    futureExpiredGift = "futureExpiredGift"
    # 是否购买过月卡
    hasBoughtMonthCard = "hasBoughtMonthCard"
    # 刷新每日任务次数
    refreshDailyQuestTimes = "refreshDailyQuestTimes"
    # 玩家在各场次的盈亏金币
    profitCoin = "profitCoin"
    # 礼包购买次数
    buyGiftTimes = "buyGiftTimes"
    # 每日礼包购买次数
    buyFishDailyGiftTimes = "buyDailyGiftTimes"
    # 各场次真实盈亏
    realProfitCoin = "realProfitCoin"

    # 玩家各场次累计破产次数
    bankruptCount = "bankruptCount"
    # 礼包过期时间
    giftsExpireTS = "giftsExpireTS"
    # 需要弹出的礼包
    popupGift = "popupGift"
    # 初始玩家50倍场17级曲线
    setUserCurve5017 = "setUserCurve5017"

    # 每日数据
    # 每日自动补足物品
    autoSupplyKey = "autoSupply:%d"

    # 邀请我的人信息
    inviterInfo = "inviterInfo"
    # 每日礼包连续购买记录
    continuousPurchase = "continuousPurchase"
    # 金币不足次数
    coinShortageCount = "coinShortageCount"
    # 身份证信息
    idCardInfo = "idCardInfo"
    # 玩家各个渔场开火消耗
    fireCost = "fireCost"
    # 玩家各个渔场开火次数
    fireCount = "fireCount"
    # 每日游戏时长（有效期2天）,playGameTime:44:uid:当日零点时间戳
    playGameTime = "playGameTime:%d:%d:%d"
    # 荣耀任务经验值
    achievementExp = "achievementExp"
    # 荣耀任务等级
    achievementLevel = "achievementLevel"
    # === 存钱罐，start
    # 开启免费存钱罐的时间戳
    pb_saveMoneyTS = "pb_saveMoneyTS"
    # 下次领取存钱罐的时间
    pb_getMoneyTS = "pb_getMoneyTS"
    # 冷却结束时间
    pb_endcoolingTS = "pb_endcoolingTS"
    # 存钱罐的金额
    pb_moneyCount = "pb_moneyCount"
    pb_moneyCountDict = "pb_moneyCountDict"
    # 是否开启了存钱罐
    pb_enable = "pb_enable"
    # 存钱罐每日累计金币量
    pb_savedMoneyCount = "pb_savedMoneyCount"
    # === 存钱罐，end
    # sdk支付后自动购买商品的数据,autoBuyAfterSDKPay:44:uid
    autoBuyAfterSDKPay = "autoBuyAfterSDKPay:%d:%d"
    # === 限时商城，start
    # 限时商城数据，timeLimitedStore:44:uid
    timeLimitedStore = "timeLimitedStore:%d:%d"
    # 已刷新次数
    tls_refreshedTimes = "tls_refreshedTimes"
    # 限时商品数据
    tls_info = "tls_info"
    # 下次刷新时间戳
    tls_nextRefreshTS = "tls_nextRefreshTS"
    # 购买次数
    tls_buyCount = "tls_buyCount"
    # === 显示商城，end
    # 等级奖励
    levelRewards = "levelRewards"
    # 已购买基金索引列表[]
    lf_funds = "lf_funds"
    # 领取的奖励：{等级:[免费,付费]}
    lf_rewards = "lf_rewards"
    # 补偿旧版称号系统玩家
    compensateOldHonor = "compensateOldHonor"
    # 更版奖励
    updateVerRewards = "updateVerRewards"
    # 当前解锁的章节ID
    currSectionId = "currSectionId"
    # 主线任务是否在渔场中显示
    mainQuestDisplay = "mainQuestDisplay"
    # 是否已完成所有主线任务
    finishAllMainQuest = "finishAllMainQuest"
    # 每日盈亏金币量K
    dailyProfitCoin = "dailyProfitCoin"
    # 每日渔场盈亏金币量K
    dailyFishPoolProfitCoin = "dailyFishPoolProfitCoin"
    # 大奖赛盈亏金币量
    grandPrixProfitCoin = "grandPrixProfitCoin"
    # 闲来老用户等级
    xlUserLevel = "xlUserLevel"
    # 闲来用户的gid
    xlUserGid = "xlUserGid"
    # 通过捕鱼累计获得奖券和实物卡金额（元）
    totalEntityAmount = "totalEntityAmount"
    # 各渔场个人可见红包券鱼捕获次数
    catchUserCouponFishCount = "catchUserCouponFishCount"
    # 新解锁的渔场倍率
    unlockedFpMultiples = "unlockedFpMultiples"
    # 拥有的可使用的渔场倍率
    ownedFpMultiples = "ownedFpMultiples"
    # 玩家的游戏分辨率
    gameResolution = "gameResolution"
    # 海皇七日赢家榜数据
    poseidon7WinMost = "poseidon7WinMost"
    # 活动竞赛TeamId,[ts, id]
    compActTeamId = "compActTeamId"
    # 活动竞赛上期排名, [ts, rank]
    lastCompActRank = "lastCompActRank"
    # # 是否实名认证
    # vertified = "vertified"
    # 玩家游戏昵称
    nickname = "nickname"
    # 新手7日礼包数据
    newbie7DayGiftData = "newbie7DayGiftData"
    # 各个渔场开火消耗(用于红包券抽奖)
    lotteryFireCostChip = "lotteryFireCostChip:h:s:44"
    # 额外奖池，来源为新手8日礼包和每日签到
    extraRechargePool = "extraRechargePool"
    # 技能补偿
    skillCompensate = "skillCompensate"
    # 出现破产礼包时所在的渔场和礼包等级
    bankruptGiftInfo = "bankruptGiftInfo"
    # 回归豪礼数据
    returnerMission = "returnerMission"
    # 玩家通过活动绑定的手机号
    phoneNumber = "phoneNumber"
    # 商品下次免费的时间戳
    productFreeTS = "productFreeTS"
    # 是否为v2版本老玩家
    isOldPlayerV2 = "isOldPlayerV2"
    # 技能页面上次切换显示的模式（0:千炮 1:经典）
    skillMode = "skillMode"
    # 炮台页面上次切换显示的模式（0:千炮 1:经典）
    gunMode = "gunMode"
    # 每次抽奖的捕获鱼的数量
    levelPrizeWheelCatchFishNumber = "levelPrizeWheelCatchFishNumber"


class ABTestData:
    """
    新手AB测试相关
    """
    # 新手概率模式
    newbieMode = "newbieMode"
    # 新手房间列表模式
    newbieRoomListMode = "newbieRoomListMode"
    # 中期阶段目标模式
    midTermTargetMode = "midTermTargetMode"
    # 破产曲线模式
    bankruptCurveMode = "bankruptCurveMode"
    # 破产测试
    bankruptTestMode = "bankruptTestMode"
    # 道具赠送测试,b模式不显示物品赠送按钮及相关赠送活动
    itemPresentTestMode = "itemPresentTestMode"
    # 礼包显示测试
    giftDisplayMode = "giftDisplayMode"
    # 签到测试，b模式使用新的转盘方式
    checkinTestMode = "checkinTestMode"
    # # 50倍场17级初始曲线AB测试
    # initCurve5017TestMode = "initCurve5017TestMode"
    # # 10倍50倍动态曲线AB测试
    # dynamicOdds1050TestMode = "dynamicOdds1050TestMode"
    # 新手结束充值奖池AB测试
    rechargePoolTestMode = "rechargePoolTestMode"
    # # 火炮升级AB测试
    # upgradeGunTestMode = "upgradeGunTestMode"
    # 渔场倍率AB测试
    fpMultipleTestMode = "fpMultipleTestMode"
    # 子弹威力奖池
    bulletPowerPool = "bulletPowerPool"
    # 新手ABC测试
    newbiewABCTestMode = "newbiewABCTestMode"


class WeakData:
    """
    存储在weak:xxx:fish:gameId:userId数据库中的key值 临时数据
    """
    # 领取月卡礼包
    getMonthCardGift = "getMonthCardGift"
    # 领取永久月卡礼包
    getPermanentMonthCardGift = "getPermanentMonthCardGift"
    # 今日幸运榜金币数
    luckyEggsNum = "luckyEggsNum"
    # 前置任务每日领取次数
    frontTaskTakeTimes = "%d:frontTaskTakeTimes"
    # 该数据库上次重置时间
    resetTime = "resetTime"
    # 每日获得的海星数
    starfish = "starfish"
    # 每日进入渔场次数
    enterFishPoolTimes = "enterFishPoolTimes"
    # 是否完成公众号签到
    wechatCheckin = "wechatCheckin"
    # 已分享群ID列表
    shareGroupIds = "shareGroupIds"
    # 分享到群奖励领取状态
    shareGroupReward = "shareGroupReward"
    # 每日已购买的破产礼包数据
    dailyGift = "dailyGift"
    # 每日礼包的购买记录
    buyFishDailyGift = "buyFishDailyGift"
    # 每日任务周奖励
    dailyQuestWeeklyReward = "dailyQuestWeeklyReward"
    # 老虎机活动积分
    slotMachineIntegral = "slotMachineIntegral"
    # 摇钱树活动摇动次数
    moneyTreeCount = "MoneyTreeCount"
    # 玩家每日制作的鱼罐头个数
    fishCanCount = "fishCanCount"
    # 玩家每日已制作罐头赠送的道具数量
    vipFishCanPresentCount = "vipFishCanPresentCount:%d"
    # 玩家每日已领取罐头的道具数量（金珠、银珠）
    vipFishCanReceiveCount = "vipFishCanReceiveCount:%d"
    # 玩家修改财富榜签名次数
    modifyCount = "modifyCount"
    # vip接收赠送的金珠和银珠数量
    vipReceiveCount = "vipReceiveCount:%d"
    # 招财模式各亏损线对应的补偿机会状态
    compensateChance = "compensateChance"
    # 招财模式盈亏金币数
    bulletProfitCoin = "bulletProfitCoin"
    # 是否存在招财模式保护限制
    isProtectionLimit = "isProtectionLimit"
    # === 大奖赛，start
    # 大奖赛参赛时间戳，记录当前局是否为首次进入
    grandPrix_startTS = "grandPrix_startTS"
    # 大奖赛免费游戏次数
    grandPrix_freeTimes = "grandPrix_freeTimes"
    # 大奖赛付费游戏次数
    grandPrix_paidTimes = "grandPrix_paidTimes"
    # 大奖赛开火次数
    grandPrix_fireCount = "grandPrix_fireCount"
    # 大奖赛捕鱼积分值
    grandPrix_fishPoint = "grandPrix_fishPoint"
    # 大奖赛积分值
    grandPrix_point = "grandPrix_point"
    # 大奖赛周积分数据,[]
    grandPrix_weekPointList = "grandPrix_weekPointList"
    # 大奖赛技能使用次数,[]
    grandPrix_useSkillTimes = "grandPrix_useSkillTimes"
    # 大奖赛目标鱼
    grandPrix_targetFish = "grandPrix_targetFish"
    # 今日是否已领取积分奖励
    grandPrix_hasTakePointRewards = "grandPrix_hasTakePointRewards"
    # 大奖赛火炮等级渔场倍率, [nowGunLevel, fpMultiple]
    grandPrix_levelFpMultiple = "grandPrix_levelFpMultiple"
    # 大奖赛超越自己次数
    grandPrix_surpassCount = "grandPrix_surpassCount"
    # === 大奖赛，end
    # 节日转盘抽大奖活动积分
    festivalTurntableIntegral = "festivalTurntableIntegral"
    # 超级boss兑换次数{mgType_mode:{idx: times}}
    superbossExchangedTimes = "superbossExchangedTimes"
    # 超级boss小游戏次数{mgType_mode:times}
    superbossMGPlayedTimes = "superbossMGPlayedTimes"
    # 活动中每日收集的道具(兔耳)数
    collectActivityItemCount = "collectActivityItemCount"
    # 海皇来袭各亏损线对应的补偿机会状态
    poseidonCompensateChance = "poseidonCompensateChance"
    # 海皇来袭盈亏金币数
    poseidonProfitCoin = "poseidonProfitCoin"
    # 今日切换动态曲线次数
    waveChangeTimes = "waveChangeTimes"
    # 老虎机已经抽奖次数
    slotMachinePlayedTimes = "slotMachinePlayedTimes"
    # 每个渔场购买破产礼包的档位及次数.
    buyBankruptGiftTimesPerPool = "buyBankruptGiftTimesPerPool"
    # 回归豪礼每日登录次数
    returnerMission = "returnerMission"
    # 商品下次免费的时间戳
    productFreeTS = "productFreeTS"
    # 所有商品购买次数
    buyProductCount = "buyProductCount"
    # 商城商品购买次数(考虑使用buyProductCount代替)
    shopBuyInfo = "shop_buy_info"
    # 每日购买宝箱数量(考虑使用buyProductCount代替)
    buyDailyChestCount = "buyDailyChestCount"


class UserData:
    """
    存储在user库中的key值 玩家存档gameId:userId
    """
    # 活动数据
    activity = "activity:%d:%d"
    # 荣耀数据
    achievement = "achievement3:%d:%d"
    # 称号数据
    honor = "honor3:%d:%d"
    # 火炮数据
    gunskin = "gunskin:%d:%d"
    # 千炮火炮数据
    gunskin_m = "gunskin_m:%d:%d"
    # 宝藏数据
    treasure = "treasure2:%d:h:s:%d"
    # 分享数据
    share = "share:%s:%s"
    # 技能数据
    skill = "skill:%d:%d"
    # 每日任务类型的完成进度存档
    fishDailyQuest = "fishDailyQuest:%d:%d"
    # 每日任务星级奖励领取存档
    fishDailyQuestReward = "fishDailyQuestReward:%d:%d"
    # 每日任务星级周奖励领取存档
    fishDailyQuestWeeklyReward = "fishDailyQuestWeeklyReward:%d:%d"
    # 每日任务完成状态存档
    fishDailyQuestInfo = "fishDailyQuestInfo:%d:%d"
    # 任务分组的当前难度等级数据
    fishDailyQuestGroupLv = "fishDailyQuestGroupLv:%d:%d"
    # 排行榜分数数据（用于同分时按时间排名）
    rankingInfo = "rankingInfo:%s:%s:%d:%d"
    # 渔场转盘数据
    prizeWheelData = "prizeWheelData:%d:%d"
    # 成长基金数据
    levelFundsData = "levelFundsData:%d:%d"
    # 成长基金数据
    levelFundsData_m = "levelFundsData_m:%d:h:s:%d"
    # 存钱罐数据
    piggyBankData = "piggyBankData:%d:%d"
    # 主线任务类型完成数量数据
    questType = "questType:%s:%s"
    # 招财财富榜玩家数据
    robberyconsume = "robberyconsume:%d:%d:%s"
    # 招财赢家榜玩家数据
    robberywinmost = "robberywinmost:%d:%d:%s"
    # 海皇赢家榜玩家个人数据
    poseidonWinMost = "poseidonWinMost:%d:%d:%s"
    # 新手期间技能使用次数
    newbieUseSkillTimes = "newbieUseSkillTimes:%d:%d"
    # 渔场红包券抽奖数据
    lotteryTicketData = "lotteryTicketData:%d:h:s:%d"
    # 免费金币摇钱树数据
    luckyTreeData = "luckyTreeData:%d:s:s:%d"
    # 所有商品购买次数
    buyProductCount = "buyProductCount:%d:h:s:%d"
    # 兑换商城商品购买数据
    buyExchangeProduct = "buyExchangeProduct:%d:%d:h:s:%d"
    # 等级转盘的key
    prizeWheelData_m = "prizeWheelData_m:%d:h:s:%d"


class MixData:
    """
    存储在mix库中的key值 全局
    """
    # 招财翻番乐数据
    bulletDoubleAc = "bulletDoubleAc"
    # === 巨奖数据,  start
    grandPrize = "grandPrize:%d"
    # 检测巨奖发奖计数
    gp_checkCount = "gp_checkCount"
    # 巨奖奖池数据
    gp_pool = "gp_pool"
    # 巨奖中奖纪录
    gp_record = "gp_record"
    # 巨奖开启时间戳
    gp_startTS = "gp_startTS"
    # === 巨奖数据, end
    # 鱼罐厂中世界工厂数据
    worldFishCans = "worldFishCans:%d"
    # 鱼罐厂玩家制作的罐头数据
    userFishCans = "userFishCans:%d"
    # 鱼罐厂某个玩家制作的罐头数据
    userFishCanList = "userFishCanList:%d"
    # 大奖赛排行榜机器人数据
    grandPrixRobotData = "grandPrixRobotData:%d"
    # 海皇来袭各魔塔累计充能金币数
    towerTotalBets = "towerTotalBets"
    # 海皇来袭魔塔记录
    towerHistory = "towerHistory"
    # 海皇来袭系统总盈亏
    poseidonGain = "poseidonGain:%d"
    # 海皇来袭系统盈亏池
    poseidonLotteryPool = "poseidonLotteryPool:%d"
    # 海皇来袭补偿奖池
    poseidonCompensate = "poseidonCompensate:%d"
    # 海皇来袭电塔奖池
    poseidonElecTower = "poseidonElecTower:%d"
    # 海皇宝藏
    poseidonWealthPool = "poseidonWealthPool:%d:%s"
    # 单轮Boss中所有参与玩家累计盈亏数据
    poseidonProfitAndLoss = "poseidonProfitAndLoss:%d"
    # === 竞赛活动数据, start
    # 竞赛活动数据
    compActData = "compActData:%d"
    # 参加人数,和team无关的存档
    ca_memberCnt = "ca_memberCnt"
    # 鼓舞总时长
    ca_inspireTotal = "ca_inspireTotal"
    # 鼓舞结束的时间点, key_teamId_ts
    ca_inspireEndTS = "ca_inspireEndTS"
    # 鼓舞等级
    ca_inspireLv = "ca_inspireLv"
    # 购买鼓舞的记录,和team无关的存档, [(ts, userId, teamId, interval)]
    ca_buyRecords = "ca_buyRecords"
    # team积分, key_teamId_ts
    ca_teamPoint = "ca_teamPoint"
    # team展示积分, key_teamId_ts
    ca_teamPointShow = "ca_teamPointShow"
    # 竞赛活动奖池,和team无关的存档
    ca_bonusPool = "ca_bonusPool"
    # 冠军rankType
    ca_winnnerRankType = "ca_winnnerRankType"
    # team人数
    ca_teamMemberCnt = "ca_teamMemberCnt"
    # rankType按分数的排名
    ca_rankTypeOrder = "ca_rankTypeOrder"
    # 需要平衡算法参数[teamCnt, leftTime],和team无关的存档
    ca_balanceParams = "ca_balanceParams"
    # team分数平衡算法使用数据.按排名顺序存储.
    ca_orderTeamId = "ca_orderTeamId"
    ca_compensatePoint = "ca_compensatePoint"
    # === 竞赛活动数据, end
    # 超级boss数据,superbossBonus:gameId
    superbossBonus = "superbossBonus:%d"
    # 超级boss奖池数据,superboss_bonuspool:bigRoomId
    superbossBonuspool = "superbossBonuspool:%d"
    superbossBonusRingpool = "superbossBonusRingpool:%d"
    # 所有商品全服购买数据
    buyProductServerCount = "buyProductServerCount:%d"