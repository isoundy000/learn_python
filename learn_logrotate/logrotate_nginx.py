#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/6 14:39

# Nginx日志切割之Logrotate篇
# 　　不管是什么日志文件，都是会越来越大的，大到一定程度就是个可怕的事情了，所以要及早的做处理，方法之一就是按时间段来存储，不过linux系统提供了Logrotate的日志管理工具，很好用，不用写计划任务脚本了，不过弊端是转储后的日志文件放入指定的目录，必须和当前日志文件再同一个系统，下面是摘录别人的。记录下以备不时之需。
# Logrotate是Linux下一款日志管理工具，可用于日志文件的转储（即删除旧日志文件，创建新日志文件）。可以根据日志大小或者按照某时段间隔来转储，内部使用cron程序来执行。Logrotate还可以在压缩日志，并发送到指定E - mail。
# Logrotate默认配置文件是 / etc / logrotate.conf, 其中第一行是：
# include /etc/logrotate.d
# 说明包含了该目录下的配置，普通用户的配置也在这里，比如nginx日志切割 /etc/logrotate.d/nginx。Logrotate有许多可配置参数，也可使用man命令来查询：
# compress                        通过gzip压缩转储以后的日志
# nocompress                      不压缩
# copytruncate                    用于还在打开中的日志文件，把当前日志备份并截断
# nocopytruncate                  备份日志文件但是不截断
# create mode owner group         转储文件，使用指定的文件模式创建新的日志文件
# nocreate                        不建立新的日志文件
# delaycompress 和 compress       一起使用时，转储的日志文件到下一次转储时才压缩
# nodelaycompress                 覆盖 delaycompress 选项，转储同时压缩。
# errors address                  转储时的错误信息发送到指定的Email 地址
# ifempty                         即使是空文件也转储，这个是 logrotate 的缺省选项。
# notifempty                      如果是空文件的话，不转储
# mail address                    把转储的日志文件发送到指定的E-mail 地址
# nomail                          转储时不发送日志文件
# olddir directory                转储后的日志文件放入指定的目录，必须和当前日志文件在同一个文件系统
# noolddir                        转储后的日志文件和当前日志文件放在同一个目录下
# prerotate/endscript             在转储以前需要执行的命令可以放入这个对，这两个关键字必须单独成行
# postrotate/endscript            在转储以后需要执行的命令可以放入这个对，这两个关键字必须单独成行
# daily                           指定转储周期为每天
# weekly                          指定转储周期为每周
# monthly                         指定转储周期为每月
# rotate count                    指定日志文件删除之前转储的次数，0 指没有备份，5 指保留5个备份
# tabootext [+] list 让logrotate   不转储指定扩展名的文件，缺省的扩展名是：.rpm-orig, .rpmsave, v, 和 ~
# size size                       当日志文件到达指定的大小时才转储，bytes(缺省)及KB(sizek)或MB(sizem)

# 先看看centOS安装后的logrotate.conf部分内容：
# /var/log/wtmp {             //用户登录和持续时间日志
#     monthly                 //按周切割
#     minsize 1M              //最小达到1M
#     create 0664 root utmp   //切割后日志文件属性
#     rotate 1                //保留副本
# }

# 简单明了。如您所料，include可以批量指定配置文件，典型应用都包含在/etc/logrotate.d/目录下，有：apache、linuxconf、syslog等。注意：include引入配置会覆盖同名默认配置
# 若干要点：
# 每个部分首括号可与其他语句同行，尾行括号必须单独成行
# prerotate和postrotate可指定转储前后（即切割前后）执行的linux脚本（endscript结束），如
# /var/log/messages {
#     prerotate                               //转储之前脚本
#     /usr/bin/chattr -a /var/log/messages    //去掉该文件-a属性
#     endscript                               //脚本结束
#     postrotate                              //转储后脚本
#     /usr/bin/kill -HUP syslogd              //重新初始化系统日志守护程序 syslogd
#     /usr/bin/chattr +a /var/log/messages    //添加-a属性，防止文件被覆盖
#     endscript
# }

# 3 Logrotate的备份策略（以两个备份来说明，即rotate 2，文件error.log）：原始文件error.log，经过一次转储，会生成error.log.1；第二次转储，生成error.log.2；第三次转储，error.log.n命名为error.log.n+1，同时生成新的error.log.1，删除error.log.n+1文件。

# 4 转储可以通过强制执行来观察工作过程
# logrotate -vf /etc/logrotate.d/nginx

# 5 日志切割的执行时间是由cron程配置决定的，可查看/etc/crontab文件（cron时间戳格式：分时日月周）， 我的测试：针对10.47.*.*上的nginx日志进行按日切割，配置如下（/etc/logrotate.d/nginx文件）：
# /var/log/nginx/*.log {      //注意：具体请以自己的nginx日志为准
#     daily                   //每天切割
#     dateext                 //%Y%m%d作为后缀
#     missingok               //日志不存在，分析下一个
#     rotate 2                //保留两个备份
#     compress                //转储之后压缩.tar.gz
#     notifempty              //空文件不转储
#     create 640 nginx adm    //新日志文件模式
#     sharedscripts           //整个日志组运行一次的脚本
#     postrotate
#             [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
#                             //重启nginx，重新加载日志文件，防止不写
#             `cp -f /var/log/nginx/*.* /var/log/nginx/backup`
#                             //自定义脚本，将旧日志copy到backup文件夹（backup要存在）
#     endscript
# }

# 7 默认logrotate是通过crontab定期执行的，我们也可以手动执行查看结果
# logrotate -vf /data/log/nginx/access.log
# 验证是否执行，查看cron的日志即可
# grep logrotate /var/log/cron

# 8 使用logrotate管理nginx的日志，优点在于：
# 1、不需要担心日志文件会将目录塞满，logrotate会保留特定个数文件；
# 2、每天的日志放在一个文件中，不需要一直往前翻，方便查阅；