#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Created on 7/28/2017

@author: houguangdong
'''
# 由于El Capitan引入了SIP机制(System Integrity Protection)，默认下系统启用SIP系统完整性保护机制，无论是对于硬盘还是运行时的进程限制对系统目录的写操作。 这也是我们安装ipython失败的原因….
# 现在的解决办法是取消SIP机制，具体做法是：
# 重启电脑，按住Command+R(直到出现苹果标志)进入Recovery Mode(恢复模式)
# 左上角菜单里找到实用工具 -> 终端
# 输入csrutil disable回车
# 重启Mac即可
# 如果想重新启动SIP机制重复上述步骤改用csrutil enable即可
# 我们现在再看看sip的状态, 这样再安装ipython、gevent再也不会提示无法写入的权限提示了/
# csrutil status
# sudo pip install --upgrade ipython --ignore-installed six
# pip install gevent
# pip install Pillow