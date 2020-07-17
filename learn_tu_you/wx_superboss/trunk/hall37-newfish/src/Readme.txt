#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/16

# 任务系统
# table_task_base.py    任务状态
# bonus_task.py         奖金赛任务 竞争                1-2名发放奖励
# cmptt_task.py         竞争性任务(夺宝赛)             第一名
# ncmptt_task.py        非竞争性任务(限时任务)
# task_system_table.py  负责管理上面的类

# task_base.py          任务基础
# task_system_user.py   新手场任务

# 事件是一对多
# 发布一个事件  多个处理事件顺序执行


1 请求流程
newfish/servers/util/superboss_handler
entity—>superboss—>gameplay


106 插件测试服
107 微信测试服 线上2.0
116 3.0测试服
P 50进程 X 25         T桌子 X 4人       0.03表示负载均衡。游戏内的

trunk插件分支
    trunk开发
        branches仿真
        tags线上

wechat 2.0
wx_superboss 3.0开发者(2.5.5往3.0开发中)
xianlai 闲来插件

配置表更新过程
/Users/houguangdong/svn/tuyou_project/newfish-client/branches/weixin/res-wx/tools/config_load
Python wx_config_load.py -d -m  # m表示多线程

/Users/houguangdong/svn/tuyou_project/newfish-client/branches/weixin_v3/res-wx/tools/config_load
1 wx_config_load_common.py      # 经典和千炮模式共用数据表
2 wx_config_load_multiple.py        # 千炮模式特有的表
3 wx_config_load.py         # 经典模式

添加新的鱼阵
weixin_v3\res-wx\newfish\config
platter
在scene_m中添加鱼阵


config37  item|product
1 svn update
2 python wx_config_load.py -d -m (多线程)
3 xxfish_test update
4 commit
5 冲突就tf放弃


# 服务器会手动改代码，然后会冲突
# 冲突之后会滚
svn revert . -R

Webmgr5 svn更新
config37&config5 —>同步hall51
更新config37和hall51               item和product 107需要手动提交之后本地更新
xxfish_dev                      116  3.0测试服
xxfish_test                     107  微信测试服
xxfish_release                          微信仿真服

房间进程的配置
# poker/cmd.json
# WeChat.txt                                    # 前后端协议的api文档
xxfish_test/config37/game/44/room/0.json            # 进程数
                              44101.json        # 房间的配置
                              44401             2倍场
                              44402             10倍场
                              44403             50倍场
                                          44404             200倍场
                              44405                    500倍场
                                  44501         大奖赛模式(可以调节倍率)
                                  room/44031.json   # 房间的配置
场景sceneName
xxfish_test/config37/game/44/scene/0.json
鱼阵 分独特自己场景鱼阵scene|公共鱼阵common
配置group_44001_1
代码中路径
src/newfish/resource/fish_group/group_44001

获取场景鱼阵
sceneGroupConf
common通用鱼阵
groupsConf所有鱼阵

1 游戏中配置名和服务器上的文件夹名一致
2 游戏配置名和写在解析中的文件名字一致
wx_superboss                        是微信3.0
wechat                          是微信2.0
room-table-player
hall-py                         游戏代码

1 xxfish_test/poker/cmd.json表示命令进入xxx进程
    RB 机器人
    GR room:房间命令入口 betpool_tableid:地主彩池 fanfanle_tableid:翻翻乐小游戏
    GROUP_MATCH:
    GT: betpool:彩池 fanfanle:翻翻乐小游戏  fish_table_call:捕鱼桌面出牌命令    table_call2:捕鱼桌面消息，不锁桌子
    UT: act:活动 activity_fish:捕鱼活动
2 具体命令的返回值
    weixin_v3—>res-wx--->Protocols—>WeChat.txt
    cmd+action决定前端请求的唯一命令
    cmd可以单独出现返回给钱前端 里面是返回给前端的值
3 具体业务流程
    请求流程的handler
    src/newfish/servers/util/
        xxxhanlder.py

    src/newfish/room
        FishFightRoom   捕鱼渔友竞技房间
        FishFriendRoom  捕鱼好友模式房间
        FishGrandPrixRoom 大奖赛模式房间
        FishMultipleRoom    捕鱼千炮模式房间
        FishNewbieRoom  捕鱼新手房间
        FishNormalRoom  捕鱼普通房间
        FishPoseidonRoom    捕鱼海皇来袭房间
        FishRobberyRoom 捕鱼招财模式房间
        FishTimeMatchRoom   捕鱼回馈赛房间
        FishTimePointMatchRoom  定时积分赛房间

    src/newfish/table
        economic_data.py    渔场内资产缓存数据
        fight_table.py
        …
        robbery_table.py
        time_match_table.py
        time_point_match_table.py
        table_base.py
        tableconf.py

    src/player/player_base.py
        子弹的兑换
        10000 200 50颗子弹
        redis数据库内存是渔场外的金币   场外与场内互相转换
        memory渔场内的金币
        auto过程自动转换子弹

    src/newfish/entity
        config          游戏的配置表
        weakdata            设置有效期的数据 每日、每周、每月
        achievement     荣耀等级|荣耀任务等级
        fishgroup           鱼阵|群
        dynamic_odds        动态概率控制
        gun             大炮
        redis_keys      存储在gamedata:gameId:userId数据库中的key值
                        GameData
                        UserData
        util.py         获得客户端标示
        prize_wheel.py      捕鱼场内的转盘
        chest.py            宝箱
        quest.py            每日任务
        honor.py            称号

tuyoo/src/poker/entity/dao/game
    gamedata.py             获取玩家的数据

4 定时器事件 本进程通知 不能跨进程通知 (重新写函数走热更)
5 函数的定义也是不能改变的，可以在返回给前端的数据做保护(重新写函数)
6 连接服日志
    1 登录日志 查询hall0里的sdk服务器日志
    2 查询COxxx.log，xxx=userId % COServer数 + 1，例如40个CO server，userid为40000001的玩家日志记录在co002.log里
        3 UT服日志
        UT是处理quick_start、game（比赛、房间类表等）消息的服务器；
        查询UTxxx.log，原理同连接服日志
    4 GR服日志
        GR是处理room/quick_start、room/leave、room/mdes等消息的服务器；
        查询GR[gameId]-001-998-1.log
    5 GT服日志
        GT是处理牌桌内游戏消息的服务器；
        查询GT[gameId]-001-998-1.log
7 服务无法启动处理
svn冲突处理
测试服上经常会手动需改配置文件，当更新svn配置后，会出现冲突，导致服务无法启动。
简单处理方式，以8/room/0.json 冲突为例，
cd .../8/room/
mv -f 0.json.mine 0.json
svn resolved 0.json

8 重要数据用info打印到日志中   (debug不打印)

9 后台数据的查询
数据库管理 —> 数据库命令
数据库管理 —> 用户数据查询
hset
gamedata:44:107014
achievementExp
20

10 http方式的查询 后端的后门
src/newfish/servers/http/http_handler.py
http://ip:8000/gtest/newfish/user?xxxx

# 重置玩家数据
Tools/config_load/test_script.py

Hmset key field1 value1 field2 value2






# 大厅添加新的道具
1 test/9999/item/0.json —> copy添加的道具json
2 xxx_dev/9999/item/0.json   粘贴道具信息
3 更新配置—>同步hall37到hall5.     Hall5大厅配置依赖于9999/9998
4 cd svnprojects/hall51-config5
5 提交9998得道具
6 更新hall37配置、更新hall5配置，表示道具生效
7 重启进程/game.sh

