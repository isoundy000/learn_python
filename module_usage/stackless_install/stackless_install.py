#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/15

# python-stackless-安装
# 1.下载stackless
#
# 以python 2.65 为例，版本不同的可相应修改
#
#
# # cd /usr/src
#
# # wget http://www.stackless.com/binaries/stackless-265-export.tar.bz2
#
# # tar jxvf stackless-265-export.tar.bz2
#
#
# 2.编译python-2.6.5-stackless，安装到/opt目录
#
#
# # cd /usr/src/python-2.6.5-stackless/
#
# # ./configure --prefix=/opt/stackless --with-readline --with-zlib=/usr/include
#
# # make
#
# # make install
#
#
# 3.生效
#
# # export PATH=/opt/stackless/bin:"$PATH"
#
#
#
# import stackless # 导入stackless模块   >>> def show(): # 定义show函数   ... print 'Stackless Python'   ...   >>> st = stackless.tasklet(show)() # 调用tasklet添加函数，第2个括号为函数参数   >>> st.run() # 调用run方法，执行函数   Stackless Python   >>> st = stackless.tasklet(show)() # 重新生成st   >>> st.alive # 查看其状态   True   >>> st.kill() # 调用kill方法结束线程   >>> st.alive # 查看其状态   False   >>> stackless.tasklet(show)() # 直接调用tasklet   <stackless.tasklet object at 0x011DD3F0>   >>> stackless.tasklet(show)()   <stackless.tasklet object at 0x011DD570>   >>> stackless.run() # 调用模块的run方法   Stackless Python
#
# 以上就是对Stackless Python安装的详细介绍。希望大家有所收获。