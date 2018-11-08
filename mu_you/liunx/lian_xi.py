#!/usr/bin/env python
#coding: utf-8

# Linux中怎么通过PID号找到对应的进程名及所在目录
# 有时候通过top命令可以看到有个别进程占用的内存比较大，但是top无法直接查看到进程名以及进程所在的目录。所以我们可以通过以下方法来定位。
# 首先需要知道PID号，可以通过top命令获取。
# ps aux | grep PID
# 通过上面的信息我们也可以找出这是一个java进程，在/opt/sonatype/nexus/bin/nexus目录下，当然可以有别的更简单直接的方法.
# 得知PID之后可以直接进入/proc/28990
# cd /proc/28990
# ls -ail
# cwd -> 进程所在目录
# exe -> /usr/local/bin/python2.7 进程类型

# 整体替换
# :%s/xxxx/new_xxxx/g