#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/6 11:51
# Mac下安装Memcache

# 我是使用 brew 来安装的，让我们再回顾一下整个过程吧。如果你没有装 brew ,先看步骤一，否则直接看步骤二。
# 步骤一：安装 Homebrew
# 先看看是否满足下面条件：
# Intel 的 CPU
# OS X 10.5 或者更高
# 安装了XCode 或者 XCode命令行工具

# 满足了，就可以安装 Homebrew，命令如下：
# $ ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"
# 具体的homebrew下载地址可查看下面

# 有一个网址会给出最新的
# 安装地址： the URL is：  http://brew.sh/index_zh-cn.html
# 在网站的最下面给出了通过terminal下载 homebrew的最新的下载地址：
# 我下载的最新的路径是：
# ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# 步骤二：安装 memcached
# 安装前，可以先查找一下，看看有没有：
# brew search memcache
# libmemcached    memcache-top    memcached   memcacheq

# 说明和关键字memcache相关的有上面这四个，这样就确认了，有我们需要的东西，第一个是客户端，第三个是服务器。
# 那么安装吧！
# 先装服务器：
# brew install memcached

# 从上面安装日志，可以看出:
# 安装 memcached 前，先安装了其所依赖的 libevent 库
# 下载的libevent和memcached，被安装到/usr/local/Cellar下面，但是又自动在/usr/local/bin下面建立了软连接，方便使用。
# 安装后可以查看安装的结果：

# $ which memcached
# $ memcached -h

# 步骤二：安装 libmemcached
# 继续安装客户端库：

# 步骤三：启动服务器
# 先默认参数启动吧：
# $ /usr/local/bin/memcached -d
# 1、启动Memcache 常用参数
# -p <num>      设置TCP端口号(默认设置为: 11211)
# -U <num>      UDP监听端口(默认: 11211, 0 时关闭)
# -l <ip_addr>  绑定地址(默认:所有都允许,无论内外网或者本机更换IP，有安全隐患，若设置为127.0.0.1就只能本机访问)
# -c <num>      max simultaneous connections (default: 1024)
# -d            以daemon方式运行
# -u <username> 绑定使用指定用于运行进程<username>
# -m <num>      允许最大内存用量，单位M (默认: 64 MB)
# -P <file>     将PID写入文件<file>，这样可以使得后边进行快速进程终止, 需要与-d 一起使用

# 更多可以使用者 memcached -h
# 在linux下：./usr/local/bin/memcached -d -u root  -l 192.168.1.197 -m 2048 -p 12121
# 在window下：d:\App_Serv\memcached\memcached.exe -d RunService -l 127.0.0.1 -p 11211 -m 500
# 在windows下注册为服务后运行：
# sc.exe create Memcached_srv binpath= “d:\App_Serv\memcached\memcached.exe -d RunService -p 11211 -m 500″start= auto
# net start Memcached

# 客户端
# 大多数操作系统都提供了内置的 telnet 客户机，但如果您使用的是基于 Windows 的操作系统，则需要下载第三方客户机。我推荐使用 PuTTy


# 结束
# kill `cat /tmp/memcached.pid`

# 获取运行状态
# echo stats | nc 192.168.1.123 11200
# watch "echo stats | nc 192.168.1.123 11200" (实时状态)

# 步骤四：测试
# 清单 3. 启动 memcached
# ./memcached -d -m 2048 -l 10.0.0.40 -p 11211
# 这会以守护程序的形式启动 memcached（-d），为其分配 2GB 内存（-m 2048），并指定监听 localhost，即端口 11211。您可以根据需要修改这些值，但以上设置足以完成本文中的练习。接下来，您需要连接到 memcached。您将使用一个简单的 telnet 客户机连接到 memcached 服务器。
# 大多数操作系统都提供了内置的 telnet 客户机，但如果您使用的是基于 Windows 的操作系统，则需要下载第三方客户机。我推荐使用 PuTTy。
# 安装了 telnet 客户机之后，执行清单 4 中的命令：
# 清单 4. 连接到 memcached  2、连接和退出
# telnet localhost 11211
# quit

# 如果一切正常，则应该得到一个 telnet 响应，它会指示 Connected to localhost（已经连接到 localhost）。如果未获得此响应，则应该返回之前的步骤并确保 libevent 和 memcached 的源文件都已成功生成。
# 您现现已经登录到 memcached 服务器。此后，您将能够通过一系列简单的命令来与 memcached 通信。9 个 memcached 客户端命令可以分为三类：
# 基本 memcached 客户机命令
# 您将使用五种基本 memcached 命令执行最简单的操作。这些命令和操作包括：
# 前三个命令是用于操作存储在 memcached 中的键值对的标准修改命令。它们都非常简单易用，且都使用清单 5 所示的语法：
# 清单 5. 修改命令语法
# command <key> <flags> <expiration time> <bytes>
# <value>
#
# 参数说明如下：
# command set/add/replace
# key           key 用于查找缓存值
# flags         可以包括键值对的整型参数，客户机使用它存储关于键值对的额外信息
# expiration time     在缓存中保存键值对的时间长度（以秒为单位，0 表示永远）
# bytes     在缓存中存储的字节点
# value     存储的值（始终位于第二行）

# 3.1 set
# set 命令用于向缓存添加新的键值对。如果键已经存在，则之前的值将被替换。
# 注意以下交互，它使用了 set 命令：
# set userId 0 0 5
# 12345
# 如果使用 set 命令正确设定了键值对，服务器将使用单词 STORED 进行响应。本示例向缓存中添加了一个键值对，其键为userId，其值为12345。并将过期时间设置为 0，这将向 memcached 通知您希望将此值存储在缓存中直到删除它为止。

# 3.2 add
# 仅当缓存中不存在键时，add 命令才会向缓存中添加一个键值对。如果缓存中已经存在键，则之前的值将仍然保持相同，并且您将获得响应 NOT_STORED。
# 下面是使用 add 命令的标准交互：
# set userId 0 0 5
# STORED
# add userId 0 0 5
# NOT_STORED
# add companyId 0 0 3
# STORED

# 3.3 replace
# 仅当键已经存在时，replace 命令才会替换缓存中的键。如果缓存中不存在键，那么您将从 memcached 服务器接受到一条 NOT_STORED 响应。
# 下面是使用 replace 命令的标准交互：
# replace accountId 0 0 5
# NOT_STORED
# set accountId 0 0 5
# STORED
# replace accountId 0 0 5
# STORED

# 最后两个基本命令是 get 和 delete。这些命令相当容易理解，并且使用了类似的语法，如下所示：
# command <key>
# 接下来看这些命令的应用。
# 3.4 get
# get 命令用于检索与之前添加的键值对相关的值。您将使用 get 执行大多数检索操作。
# 下面是使用 get 命令的典型交互：
# set userId 0 0 5
# STORED
# get userId
# VALUE userId 0 5
# END
# get bob
# END
# 如您所见，get 命令相当简单。您使用一个键来调用 get，如果这个键存在于缓存中，则返回相应的值。如果不存在，则不返回任何内容。

# 3.5 delete
# 最后一个基本命令是 delete。delete 命令用于删除 memcached 中的任何现有值。您将使用一个键调用delete，如果该键存在于缓存中，则删除该值。如果不存在，则返回一条NOT_FOUND 消息。
# 下面是使用 delete 命令的客户机服务器交互：
# set userId 0 0 5
# STORED
# delete bob
# NOT_FOUND
# delete userId
# DELETED
# get userId
# END

# 可以在 memcached 中使用的两个高级命令是 gets 和 cas。gets 和cas 命令需要结合使用。您将使用这两个命令来确保不会将现有的名称/值对设置为新值（如果该值已经更新过）。我们来分别看看这些命令。
# 3.6 gets
# gets 命令的功能类似于基本的 get 命令。两个命令之间的差异在于，gets 返回的信息稍微多一些：64 位的整型值非常像名称/值对的 “版本” 标识符。
# 下面是使用 gets 命令的客户机服务器交互：
# set userId 0 0 5
# STORED
# get userId
# VALUE userId 0 5
# END
# gets userId
# VALUE userId 0 5 4
# END
# 考虑 get 和 gets 命令之间的差异。gets 命令将返回一个额外的值 — 在本例中是整型值 4，用于标识名称/值对。如果对此名称/值对执行另一个set 命令，则gets 返回的额外值将会发生更改，以表明名称/值对已经被更新。显示了一个例子：
# set userId 0 0 5
# STORED
# gets userId
# VALUE userId 0 5 5
# END
# 您看到 gets 返回的值了吗？它已经更新为 5。您每次修改名称/值对时，该值都会发生更改。

# 3.7 cas
# cas（check 和 set）是一个非常便捷的 memcached 命令，用于设置名称/值对的值（如果该名称/值对在您上次执行 gets 后没有更新过）。它使用与 set 命令相类似的语法，但包括一个额外的值：gets 返回的额外值。
# 注意以下使用 cas 命令的交互：
# set userId 0 0 5
# STORED
# gets userId
# VALUE userId 0 5 6
# END
# cas userId 0 0 5 6
# STORED
# 如您所见，我使用额外的整型值 6 来调用 gets 命令，并且操作运行非常顺序。现在，我们来看看中的一系列命令：
# 使用旧版本指示符的 cas 命令
# set userId 0 0 5
# STORED
# gets userId
# VALUE userId 0 5 8
# END
# cas userId 0 0 5 6
# EXISTS
# 注意，我并未使用 gets 最近返回的整型值，并且 cas 命令返回 EXISTS 值以示失败。从本质上说，同时使用gets 和cas 命令可以防止您使用自上次读取后经过更新的名称/值对。

# 缓存管理命令
# 最后两个 memcached 命令用于监控和清理 memcached 实例。它们是 stats 和 flush_all 命令。

# 3.8 stats
# stats 命令的功能正如其名：转储所连接的 memcached 实例的当前统计数据。在下例中，执行 stats 命令显示了关于当前 memcached 实例的信息：
# 此处的大多数输出都非常容易理解。我们先来看看输出，然后再使用新的键来运行一些 set 命令，并再次运行stats 命令，注意发生了哪些变化。
# STAT pid 22459                             进程ID
# STAT uptime 1027046                        服务器运行秒数
# STAT time 1273043062                       服务器当前unix时间戳
# STAT version 1.4.4                         服务器版本
# STAT libevent 2.0.21-stable
# STAT pointer_size 64                       操作系统字大小(这台服务器是64位的)
# STAT rusage_user 0.040000                  进程累计用户时间
# STAT rusage_system 0.260000                进程累计系统时间
# STAT curr_connections 10                   当前打开连接数
# STAT total_connections 82                  曾打开的连接总数
# STAT connection_structures 13              服务器分配的连接结构数
# STAT reserved_fds 20
# STAT cmd_get 54                            执行get命令总数
# STAT cmd_set 34                            执行set命令总数
# STAT cmd_flush 3                           指向flush_all命令总数
# STAT get_hits 9                            get命中次数
# STAT get_misses 45                         get未命中次数
# STAT delete_misses 5                       delete未命中次数
# STAT delete_hits 1                         delete命中次数
# STAT incr_misses 0                         incr未命中次数
# STAT incr_hits 0                           incr命中次数
# STAT decr_misses 0                         decr未命中次数
# STAT decr_hits 0                           decr命中次数
# STAT cas_misses 0                          cas未命中次数
# STAT cas_hits 0                            cas命中次数
# STAT cas_badval 0                          使用擦拭次数
# STAT touch_hits 0
# STAT touch_misses 0
# STAT auth_cmds 0
# STAT auth_errors 0
# STAT bytes_read 15785                      读取字节总数
# STAT bytes_written 15222                   写入字节总数
# STAT limit_maxbytes 67108864               分配的内存数（字节）
# STAT accepting_conns 1                     目前接受的链接数
# STAT listen_disabled_num 0
# STAT time_in_listen_disabled_us 0
# STAT threads 4                             线程数
# STAT conn_yields 0
# STAT hash_power_level 16
# STAT hash_bytes 524288
# STAT hash_is_expanding 0
# STAT malloc_fails 0
# STAT conn_yields 0
# STAT bytes 0                               存储item字节数
# STAT curr_items 0                          item个数
# STAT total_items 34                        item总数
# STAT expired_unfetched 0
# STAT evicted_unfetched 0
# STAT evictions 0                           为获取空间删除item的总数
# STAT reclaimed 0
# STAT crawler_reclaimed 0
# STAT crawler_items_checked 0
# STAT lrutail_reflocked 0


# stats items
# 执行stats items，可以看到STAT items行，如果memcached存储内容很多，那么这里也会列出很多的STAT items行。
# STAT items:1:number 3
# STAT items:1:age 1698
# STAT items:1:evicted 0
# STAT items:1:evicted_nonzero 0
# STAT items:1:evicted_time 0
# STAT items:1:outofmemory 0
# STAT items:1:tailrepairs 0
# STAT items:1:reclaimed 0
# STAT items:1:expired_unfetched 0
# STAT items:1:evicted_unfetched 0
# STAT items:1:crawler_reclaimed 0
# STAT items:1:crawler_items_checked 0
# STAT items:1:lrutail_reflocked 0
# END

# stats cachedump slabs_id limit_num
# slabs_id:由stats items返回的结果（STAT items后面的数字）决定的
# limit_num:返回的记录数，0表示返回所有记录
# 通过stats items、stats cachedump slab_id limit_num配合get命令可以遍历memcached的记录。
# stats cachedump 1 0
# ITEM userId [5 b; 1467903379 s]
# ITEM accountId [5 b; 1467903379 s]
# ITEM companyId [3 b; 1467903379 s]
# END
# stats cachedump 1 2
# ITEM userId [5 b; 1467903379 s]
# ITEM accountId [5 b; 1467903379 s]
# END

# stats slabs 显示各个slab的信息，包括chunk的大小、数目、使用情况等
# STAT 1:chunk_size 96
# STAT 1:chunks_per_page 10922
# STAT 1:total_pages 1
# STAT 1:total_chunks 10922
# STAT 1:used_chunks 3
# STAT 1:free_chunks 10919
# STAT 1:free_chunks_end 0
# STAT 1:mem_requested 232
# STAT 1:get_hits 9
# STAT 1:cmd_set 14
# STAT 1:delete_hits 1
# STAT 1:incr_hits 0
# STAT 1:decr_hits 0
# STAT 1:cas_hits 0
# STAT 1:cas_badval 0
# STAT 1:touch_hits 0
# STAT active_slabs 1
# STAT total_malloced 1048512

# stats sizes 输出所有item的大小和个数

# stats reset 清空统计数据

# 3.9 flush_all
# flush_all 是最后一个要介绍的命令。这个最简单的命令仅用于清理缓存中的所有名称/值对。如果您需要将缓存重置到干净的状态，则 flush_all 能提供很大的用处。下面是一个使用 flush_all 的例子：
# set userId 0 0 5
# STORED
# get userId
# VALUE userId 0 5
# END
# flush_all
# OK
# get userId
# END

# 追加与清除命令
# 3.10 append
# append 将数据追加到当前缓存数据的之后，当缓存数据存在时才存储。
# set username 0 0 8
# wayne173
# STORED
# get username
# VALUE username 0 8
# wayne173
# END
# append username 0 0 5
# _ages
# STORED
# get username
# VALUE username 0 13
# wayne173_ages
# END

# 3.11 prepend
# prepend 将数据追加到当前缓存数据的之前，当缓存数据存在时才存储。
# set username 0 0 8
# wayne173
# STORED
# get username
# VALUE username 0 8
# wayne173
# END
# prepend username 0 0 5
# name_
# STORED
# get username
# VALUE username 0 13
# name_wayne173
# END

# memcached还有很多命令，比如对于存储为数字型的可以通过incr/decr命令进行增减操作等等，这里只列出开发和运维中经常使用的命令，其他的不再一一举例说明。
# 缓存性能
# 在本文的最后，我将讨论如何使用高级 memcached 命令来确定缓存的性能。stats 命令用于调优缓存的使用。需要注意的两个最重要的统计数据是 et_hits 和 get_misses。这两个值分别指示找到名称/值对的次数（get_hits）和未找到名称/值对的次数（get_misses）。
# 结合这些值，我们可以确定缓存的利用率如何。初次启动缓存时，可以看到 get_misses 会自然地增加，但在经过一定的使用量之后，这些 get_misses 值应该会逐渐趋于平稳 — 这表示缓存主要用于常见的读取操作。如果您看到 get_misses 继续快速增加，而 get_hits 逐渐趋于平稳，则需要确定一下所缓存的内容是什么。您可能缓存了错误的内容。
# 确定缓存效率的另一种方法是查看缓存的命中率（hit ratio）。缓存命中率表示执行 get 的次数与错过 get 的次数的百分比。要确定这个百分比，需要再次运行stats 命令，如清单 8 所示：
# 现在，用 get_hits 的数值除以 cmd_gets。在本例中，您的命中率大约是 71%。在理想情况下，您可能希望得到更高的百分比 — 比率越高越好。查看统计数据并不时测量它们可以很好地判定缓存策略的效率。