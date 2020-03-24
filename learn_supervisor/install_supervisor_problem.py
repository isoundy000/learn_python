#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


# supervisorctl 启动客户端时候遇到问题笔记
# 问题
# 自己部署的服务器，时隔一些实践登入的时候，查看服务进程的情况的时候，经常性遇到一些问题。
# 使用：supervisorctl启动后就会报下面额错误：
# unix:///tmp/supervisor.sock no such file
# 问题可能是因为：
# 在supervisor默认配置中，其启动的sock等都会放到tmp目录，而tmp目录会自动清理导致无法使用supervisorctl命令，此时：
# 所以建议修改supervisor.conf文件，
# 把所有关于有tmp修改到其他目录下，比如：/var/run/及/var/log/目录。
# kill原来服务，然后重启supervisor服务，
# 这种情况下，再启动对应的服务端的话（即：supervisord是无法启动的）
# 对应的配置:
# 这种情况下目前我处理方式是：只能先杀掉已经创建的进程，再重启相关进程；
# 问题临时解决：
# 具体主要步骤是：
# 1:先结束supervisord的进程
# 2:再结束相关UWSGI进程服务（流程同上）
# 批量的关闭所有关于uwsgi的进程
# [root@web1 ~]# killall -9 uwsgi
# [root@web1 ~]# ps -ef | grep uwsgi
# 批量删除进程的资料参考：
# $ ps -ef | grep rtprecv | grep -v grep | awk '{print $2}' | xargs kill -91
#
# 解释一下：
# 　　ps -ef 用于获取当前系统所有进程，如上图所示。
# 　　grep rtprecv 过滤出与“rtprecv”字符相关的数据（以行为单位）。
# 　　grep -v grep 的作用是除去本次操作所造成的影响，-v 表示反向选择。
# 　　awk '{print $2}' 表示筛选出我们所关注的进程号，$2 表示每行第二个变量，在这个例子中就是进程号。所以如果你使用ps工具不一样，或者ps带的参数不一样，那需要关注的就可能不是$2，可能是$1 。
# 　　xargs kill -9 中的 xargs 命令表示用前面命令的输出结果（也就是一系列的进程号）作为 kill -9 命令的参数，-9 表示强制终止，不是必须的。
# 　　上面是用 kill 配合过滤操作来完成，实际上还有更简单的方法——使用 killall 命令。killall 通过进程名字终止所有进程，用法如下：killall <process_name> 。
# 　　在我们这个例子中，可以这么用：
#
# # killall -9 rtprecv1
# 　　当然，killall 也可以和 ps 或 pgrep 结合使用，以此来查看哪些程式正在运行。
#
# 【扩展知识】
# 　　与终止进程相关的命令有：
#
# ps ： 报告当前进程的快照
# kill ： 向一个进程发出信号
# killall ： 按名字消灭进程
# pkill ： 根据名字和其它属性查看或者发出进程信号
# skill ： 发送一个信号或者报告进程状态
# xkill ： 按照X资源消灭一个客户程序
#
# 终止一个进程或终止一个正在运行的程序，一般是通过 kill 、killall、pkill、xkill 等进行。比如一个程序已经死掉，但又不能退出，这时就应该考虑应用这些工具。
# 　　另外应用的场合就是在服务器管理中，在不涉及数据库服务器程序的父进程的停止运行，也可以用这些工具来终止。为什么数据库服务器的父进程不能用这些工具杀死呢？原因很简单，这些工具在强行终止数据库服务器时，会让数据库产生更多的文件碎片，当碎片达到一定程度的时候，数据库就有崩溃的危险。比如 mysql 服务器最好是按其正常的程序关闭，而不是用 pkill mysqld 或 killall mysqld 这样危险的动作；当然对于占用资源过多的数据库子进程，我们应该用 kill 来杀掉。
# 　　xkill 是在桌面用的杀死图形界面的程序。比如当 firefox 出现崩溃不能退出时，点鼠标就能杀死 firefox 。当xkill运行时出来和个人脑骨的图标，哪个图形程序崩溃一点就 OK 了。如果您想终止 xkill ，就按右键取消。
# 　　
# 　　另外，说一下 grep 和 pgrep 的区别：
# 　　pgrep 是通过程序的名字来查询进程的工具，一般是用来判断程序是否正在运行。在服务器的配置和管理中，这个工具常被应用。用法：pgrep 参数选项 程序名。
# 　　grep （global search regular expression(RE) and print out the line，全面搜索正则表达式并把行打印出来）是一种强大的文本搜索工具，它能使用正则表达式搜索文本，并把匹配的行打印出来。Unix 的 grep 家族包括 grep、egrep 和 fgrep。
# 　　简单来说，一个是查询程序的运行状态，一个是搜索内容。
#
#
# 其他参考
# ~~~
# 命令：ps -ef|grep keyword|grep -v grep|cut -c 9-15|xargs kill -9
#
# 批量杀死包含关键字“keyword”的进程。
#
# "ps -ef" ——查看所有进程
# "grep keyword" ——列出所有含有关键字"./amplxe-gui"的进程
# "grep -v grep" ——在列出的进程中去除含有关键字"grep"的进程（因为我们在前一步生成的grep进程也包含关键字）
# "cut -c 9-15" ——截取输入行的第9个字符到第15个字符，而这正好是进程号PID
# "xargs kill -9" ——xargs 命令是用来把前面命令的输出结果（PID）作为"kill -9"命令的参数，并执行该命令。"kill -9"会强行杀掉指定进程。
# 3：再重启一下supervisor的服务端
# [root@web1 ~]# supervisord
# 4：再进入到客户端查看对应的服务又重新拉起了！