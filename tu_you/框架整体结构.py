#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 1. 框架整体结构
#     1.1 FreeTime架构
#
#               请参考: FreeTime介绍, 主要介绍了FreeTime的由来和基本的架构设计
#     1.2 第一层 freetime
#
#               svn路径: newsvn/freetime/trunk
#
#               此工程定义和实现了:
#
#                   Twisted的启动运行, 基本的网络通讯 newsvn/freetime/trunk/freetime/core
#
#                   文件日志, 数据收集日志 newsvn/freetime/trunk/freetime/util
#
#                   数据库的基本链接操作, HTTP访问基础操作 newsvn/freetime/trunk/freetime/aio
#
#                   配置系统的基础 newsvn/freetime/trunk/freetime/entity/config.py
#
#             通常在我们的游戏业务工程中,对于此工程的引用,仅限于
#
#                   freetime/trunk/freetime/util/*
#
#                   freetime/trunk/freetime/entity/msg.py
#
#             以上文件或包内容的引用, 其他的内容一般不允许引用
#     1.3 第二层 tuyoo
#
#            svn路径: newsvn/tuyoo/trunk
#
#            此工程定义和实现了:
#
#                通用业务逻辑处理基类 tuyoo/trunk/src/poker/entity/biz/*
#
#                业务系统配置管理同步 tuyoo/trunk/src/poker/entity/configure/*
#
#                REDIS, MYSQL数据操作基类 tuyoo/trunk/src/poker/entity/dao/*
#
#                事件处理中心基类 tuyoo/trunk/src/poker/entity/events/*
#
#                游戏插件基类 tuyoo/trunk/src/poker/entity/game/*
#
#                机器人基类 tuyoo/trunk/src/poker/entity/robot/*
#
#                各个不同类型的进程的通讯, HTTP,TCP命令的注册和执行 newsvn/tuyoo/trunk/src/poker/protocol/*
#
#                通用资源 newsvn/tuyoo/trunk/src/poker/resource/*
#
#                通用的工具类 newsvn/tuyoo/trunk/src/poker/util/*
#
#            通常在我们的游戏业务工程中, 对于此工程的引用是比较频繁的, 使用较多的
#     1.4 第三层(游戏大厅, 游戏业务平行层次) tygame-hall
#
#           svn路径: newsvn/hall-py/branches/tygame-hall-2
#
#           此工程定义和实现了:
#
#                大厅业务逻辑基础 newsvn/hall-py/branches/tygame-hall-2/src/hall/entity/*
#
#                大厅处理的命令入口 newsvn/hall-py/branches/tygame-hall-2/src/hall/servers/*
#
#                大厅游戏插件入口 newsvn/hall-py/branches/tygame-hall-2/src/hall/game.py
#
#            通常在我们的游戏业务工程中, 对于此工程的引用是比较频繁的, 共同的业务逻辑较多, 较复杂,
#
#            个游戏再使用时, 需要先搞明白大厅的处理方式, 在进行调用
#     1.5 第三层(地主游戏, 示例工程) tygame-dizhu
#
#            svn路径: newsvn/hall-py/branches/tygame-dizhu-2
#
#            此工程定义和实现了:
#
#               斗地主的活动模块 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/activities/*
#
#               斗地主的大比赛模块 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/bigmatch/*
#
#               斗地主的业务逻辑基础 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/entity/*
#
#               斗地主出牌算法集合 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/gamecards/*
#
#               斗地主的玩法集合 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/gameplays/*
#
#               斗地主的桌子实现 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/gametable/*
#
#               斗地主的资源 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/resource/*
#
#               斗地主的机器人实现 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/robot/*
#
#               斗地主的命令处理入口 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/servers/*
#
#               斗地主的游戏插件入口 newsvn/hall-py/branches/tygame-dizhu-2/src/dizhu/game.py
#
#          此工程为斗地主工程, 不允许其他任何工程引用
# 2. 运行环境建立
#
#         通常公司内分配的开发机, 环境均已经建立完毕, 这里重复一次, 作为运行环境检测.
#     2.1. pypy
#
#              目前稳定的版本是: 2.4  可直接使用编译好的: http://10.3.13.254/pypy.tgz 或 http://192.168.10.88/pypy.tgz
#
#              若有需求需要自己编译pypy,那么参考: newsvn/freetime/trunk/deps/install-pypy25-with-package.txt 进行编译
#
#
#     2.2 mysql
#
#              使用系统自带的mysql即可, 可以使用 yum install mysql-server 进行安装 5.0版本以上即可
#
#              mysql需要进行数据库初始化操作:
#
#              请执行SQL脚本 http://10.3.13.254/sqlscript.tgz 或 http://192.168.10.88/sqlscript.tgz
#
#              启动mysql服务: root账户执行: service mysql start
#     2.3 redis
#
#             目前使用的版本为2.8.21 可直接使用编译好的: http://10.3.13.254/redis.tgz 或 http://192.168.10.88/redis.tgz
#
#             若需要自己编译请直接参考: http://redis.io/
#     2.4 nginx
#
#             对于个人开发环境nginx模块为选装模块, 可以不安装, 不影响具体的业务服务
#
#             可使用编译好的 http://10.3.13.254/nginx.tgz 或 http://192.168.10.88/nginx.tgz
#
#             若开发机需要向外部提供80端口的登录接入服务(不需要加端口号登录)时,
#
#             需要nginx进行端口转发, 将80端口的请求转发至我们的pypy HTTP进程服务
#
#             具体的nginx配置, 请到百度搜索"nginx 配置"自行调整
#     2.5 第三方环境依赖
#
#             需要gcc, java, mysql-devel, openssl-devel, svn
#
#             可使用root账户执行: yum install gcc  java mysql-devel mysql-server openssl-devel svn -y
#     2.6 一键环境安装脚本
#
#             下载脚本: http://10.3.13.254/install.sh 或 http://192.168.10.88/install.sh
#
#              以root用户运行install.sh, 即可直接将上述所需内容一键安装完成
#     2.7 启动依赖服务
#
#             以root账户执行:
#
#                 MYSQL服务: service mysql start
#
#                 REDIS服务: cd  /usr/local/redis-2.8.21 (注: 此处的启动以http://10.3.13.254/redis.tgz为基础, 若自行编译的请到网上自行搜索如何启动)
#
#                                     mkdir data
#
#                                     ./newredis.sh  6379  (注: 可以用其他端口号, 会生成不同端口的启动脚本)
#
#                                     ./master-6379.sh
# 3. 服务启动配置
#     3.1. 标准的服务目录结构
#
#             注: 以tyhall用户为例, 以下所有的路径相关的说明和例子均以tyhall用户为例
#
#             目录结构:
#
# /home/tyhall/
#
# ├── hall0                            老框架服务目录 (在新老框架(估计会很长时间)交替期间, 需要老版本框架提供SDK登录功能和其他未升级框架的插件游戏服务)
#
# │   ├── action.log               启动日志文件(自动生成)
#
# │   ├── backup                   启动备份目录(自动生成)
#
# │   ├── bin                          可执行的pyc文件目录(自动生成)
#
# │   ├── bireport                   BI日志目录(自动生成)
#
# │   ├── hotfix                      热更新脚本目录(自动生成)
#
# │   ├── logs                        游戏日志目录(自动生成)
#
# │   ├── script                      编译生成的可执行脚本目录(自动生成)
#
# │   ├── source                    工程源代码目录
#
# │   │   ├── test.json            服务启动配置文件
#
# │   │   ├── tyframework      老版本框架工程
#
# │   │   ├── tygame-hall       老版本大厅游戏混合工程
#
# │   │   └── tygame-sdk       老版本SDK工程
#
# │   ├── s.sh                         服务启动脚本
#
# │   └── webroot                  HTTP服务的静态资源目录(自动生成)
#
# ├── hall37                           新框架37服务目录
#
# │   ├── mgr.sh                    后台开发用WEB界面控制台
#
# │   ├── run                         编译输出,运行目录
#
# │   │   ├── backup             启动备份目录(自动生成)
#
# │   │   ├── bin                    可执行的pyc文件目录(自动生成)
#
# │   │   ├── log                    游戏日志目录(自动生成)
#
# │   │   └── webroot            HTTP服务的静态资源目录(自动生成)
#
# │   └── source                                工程源代码目录
#
# │       ├── config                              配置工程
#
# │       ├── freetime-trunk                 FreeTime工程
#
# │       ├── tuyoo-trunk                     Poker工程
#
# │       ├── tygame-dizhu-trunk        游戏斗地主工程(示例工程)
#
# │       ├── tygame-hall-trunk           大厅工程
#
# │       └── tywebmgr                       启动管理脚本工程 (svn地址: newsvn/hall-py/branches/tywebmgr)
#
#             可以下载 http://192.168.10.88/hall-20150906.tgz 直接获取所有的工程代码
#
#             此tag包中, hall0使用的是0901的线上分支代码, hall37使用的是trunk代码, 因此请不要随意提交任何代码
#
#             解包后, 可自行切换至自己需要的分支
#     3.2 启动依赖服务
#
#             REDIS: 启动端口8000的数据服务
#
#             MYSQL: 启动标准端口3306即可 (mysql服务再测试服仅作为连接支撑, 没有实际的数据交互, 因此,多个服务可以共用一个mysql服务)
#     3.3 修改hall0的启动配置
#
#             打开hall0/source/test.json, 修改redis端口号和服务IP地址
#
#             修改 "redis.port" : 8000, 执行当前使用的redis数据库端口
#
#             修改 "servers"下的IP地址
#
#                 修改 "intrant" : "192.168.10.88",  当前测试服务机器的内网地址, 必须有, 且不能填写localhost, 127.0.0.1
#
#                 修改 "intrant" : "111.203.187.150",  当前测试服务机器的外网地址, 若没有,则添内网地址
#
#                 (可使用ifconfig命令, 查看当前机器的地址, 若只有一个物理网卡IP, 则内外的IP都写一个即可)
#     3.4 执行 hall0/s.sh
#
#             注意终端输出, 此时若有异常输出, 请忽略
#
#             打开hall0/action.log 找到 "Http SDK         : http://111.203.187.150:8002" 这一行,
#
#             即得到当前服务的接入地址"http://111.203.187.150:8002" 即http.sdk变量
#     3.5 启动hall37的WEB管理台
#
#             执行: hall37/mgr.sh
#
#             (注意: mgr.sh 缺省使用8037端口, 若有端口冲突, 请自行修改mgr.sh中的端口参数)
#
#             (注意: mgr.sh 中 --path参数, 指向的是配置工程中的test目录配置, 若需要使用其他的配置目录请自行修改目录指向)
#     3.6 修改hall37的启动配置
#
#             使用浏览器(推荐使用火狐浏览器) 打开 http://192.168.10.88:8037/main.html
#
#             (注意: 对于目前公司分配的测试机, 同时有内外网地址的机器, 有些可以使用内网地址访问, 有些则需要使用外网地址访问, 具体为啥? 我也不知道,
#
#                       另外, 如果都不能访问, 请先查看 hall37/source/tywebmgr/nohup.out 是否有异常, 再查看hall37/source/tywebmgr/logs/webmagr.log 是否有异常,
#
#                       如果日志没有异常, 请尝试使用root执行 service iptables stop, 停止防火墙, 重新启动mgr.sh)
#
#             修改 Poker的基本配置
#
#                 打开TAB页面: 配置管理->Poker->基本配置
#
#                     local_internet 的值到本机的外网地址 (外网地址,同hall0的外网地址一致)
#
#                     local_intranet 的值到本机的内外地址 (外网地址,同hall0的内网地址一致)
#
#                     port_redis 的值到服务使用的redis端口 (同hall0使用的redis端口一致)
#
#                     port_http 修改hall37使用的起始端口号, 避开已有服务即可, 例如: 8100
#
#                     http_sdk 修改hall37使用的SDK外网地址到hall0的http.sdk地址 (即第4步得到的"Http SDK"的地址)
#
#                     http_sdk_inner 修改hall37使用的SDK内网地址 (同http_sdk值一致即可, 或将http_sdk中的IP改为本机的内网IP)
#
#               点击页面最上方的"保存"按钮, 保存配置
#     3.7 启动hall37
#
#             打开TAB页面: 运行管理
#
#             点击"配置编译启动", 即启动hall37大厅服务, 在网页上即可看到启动的操作日志
#
#             此界面日志的功用和hall0的action.log一致
#
#             若操作界面日志无异常, 则hall37服务启动成功,
#
#             若操作界面日志显示启动失败, 则需要到hall37/run/log下查看日志, 找到具体的失败原因
#     3.8 新老服务联合
#
#             修改老服务的配置
#
#                 打开hall0/source/tygame-sdk/configure/game/game_clientid.py
#
#                 将文件中"game.branch"项目中的第一组内容,
#
#                     http_game地址, 修改为: hall37的http_game的地址 ( 可以在web控制台中的启动操作日志里面, 日志的最上面20行左右找到)
#
#                     clientIds列表, 可以控制接入hall37服务的客户端 (此列表为正则表达式列表, 缺省为将3.7版本的客户端导向hall37服务)
#
#                 打开hall0/source/test.json
#
#                     修改或添加配置项: "newtcpbridge" : "http://192.168.10.97:6390"
#
#                     HTTP地址指向hall37的http_game
#
#             重新启动hall0服务
#
#                 此时hall0服务用可以正常启动, 无异常发生才对
#
#             新老服务的通讯机制:
#
#                 hall0的CONN服务启动桥接监听端口, 端口启动后, 通过http(即: newtcpbridge配置项) 通知hall37老服务的桥接端口号
#
#                 hall37的HTTP服务,收到桥接的通知, 通知CO服务去连接hall0的桥接端口
#
#                 连接后, 双方通讯握手以后:
#
#                     hall37将未注册的gameId消息转发至hall0服务
#
#                     hall37的用户登录或离开时,通知hall0用户的在线状态, hall0记录hall37的所有用户列表
#
#                     hall37用户第一个user_info时, 会向hall0请求改用户在hall0是否需要断线重连(即: 查询用户在hall0的loc值)
#
#                     hall0将游戏产生的发送给客户端的消息, 转发至hall37, hall37再发送至真正的客户端
#     3.9 验证新老服务
#
#             客户端的登录地址一律为http_sdk, 即hall0的action.log中的sdk地址
#
#             使用新的3.7的客户端, 接入服务, TCP长链接应该接入hall37的TCP端口, 可查看 hall37/run/logs/CO001.log查看实际接入情况
#
#             使用老客户端(非3.7)客户端, 接入服务, TCP长连接应该接入hall0的TCP端口, 可查看hall0/logs/conn-*-11.log查看实际接入情况
#
#             使用3.7客户端, 玩插件游戏(例: 大丰收), 消息应该由hall37的TCP服务转发至hall0的TCP服务, 可以在日志中观察到
# 4. 配置数据
#     4.1 配置管理方式
#
#             请参考 服务端配置管理方式(2015重构) 的说明
#     4.2 配置项目说明
#
#             第一层配置 freetime
#
#                 global.json        第一层的全局配置, 主要配置内容:
#
#                                              是否H5服务, 日志级别, 日志路径, BI数据接收服务列表
#
#                 db.json             全局数据库连接配置, 主要配置内容:
#
#                                              mysql的数据连接配置, redis的数据库连接配置
#
#                 server.json       服务器进程配置
#
#             第二层配置 poker
#
#                 global.json                        第二层的全局配置, 主要配置一些单项的全局内容, 具体的请参考代码
#
#                 machine.json                    定义使用那些服务器
#
#                 project.json                       定义使用那些源代码工程
#
#                 cmd.json                           定义TCP接入的命令的基本转发方向
#
#                 oldcmd.json                      定义了老(hall0)的命令和新(hall37)命令之间的转换关系
#
#                 map.activityid.json            ACTEVENT的字符串ID到数值ID的对应关系表
#
#                 map.bieventid.json            BIEVENT的字符串ID到数值ID的对应关系表
#
#                 map.clientid.json.sample  CLIENTID的字符串ID到数值ID的对应关系表, 已经实现自动与GDSS同步
#
#                 map.giftid.json                  礼物的字符串ID到数值ID的对应关系表
#
#                 map.productid.json.sample 商品的字符串ID到数值ID的对应关系表, 已经实现自动与GDSS同步
#
#           第三层配置game
#
#                 此层次下均以gameId数值为目录名称
#
#                 例如 game/9999 为所有大厅的配置 game/6 为所有地主的配置
#     4.3 简单配置
#
#            对于简单的配置, 例如: game/6/exp/0.json 地主经验值的配置
#
#            此种配置无需区分clientId, 那么就都存放在0.json中
#
#            再代码中引用时, 使用如下代码:
#
#                from poker.entity.configure import configure
#
#                configure.getGameJson(DIZHU_GAMEID, 'exp')['level']
#     4.4 ClientId配置
#
#           对于需要区分clientId的配置项目, 切配置内容比较简单的, 那么将配置写入clientId数值为名字的json文件.
#
#           例如: game/6/share/12769.json 地主分享的配置
#
#           此目录下没有0.json, 每个clientId对应一个配置文件
#
#           再代码中引用时, 使用如下代码:
#
#               from poker.entity.configure import configure, pokerconf
#
#               intClientId = pokerconf.clientIdToNumber(clientId)
#
#               shares = configure.getGameJson(DIZHU_GAMEID, 'share', {}, intClientId)
#
#               return shares.get('shares', {})
#      4.5 复杂模板配置
#
#            对于需要区分clientId, 且配置项目比较复杂, 也许有n个clientId的内容是一样的, 基于这样的需求, 引入配置模板的概念
#
#            通常此类配置, 再读取配置后,还需要"二次加工", 才能真正使用或返给客户端
#
#            例如活动的配置:
#
#                模板配置: game/9999/gamelist/0.json
#
#                ClientId引用配置 : game/9999/gamelist/12464.json
#
#                                              game/9999/gamelist/12630.json
#
#            再代码中引用时, 使用类似代码:
#
#             def getGameListConf():
#
#                 return configure.getGameJson(HALL_GAMEID, 'gamelist', {}, configure.DEFAULT_CLIENT_ID)
#
#             def getGameListTemplateName(clientId):
#
#                 intClientId = pokerconf.clientIdToNumber(clientId)
#
#                 ftlog.debug("intClientId:", intClientId)
#
#                 if intClientId == 0:
#
#                     return 'hall_game_default'
#
#                 template = configure.getGameJson(HALL_GAMEID, 'gamelist', {}, intClientId)
#
#                 return template.get('template', 'hall_game_default')
#     4.6 配置代码接口
#
#              通常我们使用的接口是 from poker.entity.configure import configure, 此接口基本上已经能满足大多数的配置获取要求
#
#               其中包包含了标准的配置内容取得方法, 标准的模板内容取得方法, 配置变更的广播通知方法等
#
#              对于字符串<->ID之间的转换接口是 from poker.entity.configure import pokerconf, 此接口中含有各种字符串到ID的转换方法
#
#              可以参考 tygame-dizhu-2/src/dizhu/entity/dizhuconf.py 和 tygame-hall-2/src/hall/entity/hallconf.py 中的具体实现和使用方法
# 5. 进程类型和角色
#
#
# 6. 房间配置
#     6.1 房间配置和进程配置的关系(server.json)
#     6.2 关键配置项
#
#              房间类型和玩法配置项
#
#              准入和快速开始配置项
#
#              机器人配置项
# 7. 消息路由
# 8. TCP命令的处理
# 9. HTTP命令的处理
# 10. RPC远程调用处理
# 11. 用户消息队列
# 12. 用户数据操作锁
# 13. 游戏插件
# 14. 支付业务处理