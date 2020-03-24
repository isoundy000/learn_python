#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# Mac OS X开机启动Redis

# Mac OS X开机启动Redis

# ===========  方法1 （推荐）  ==========

# 1.打开命令行
# 2.以Root身份，新建一个文件 ru root  10086                  su - 退出

# sudo nano /Library/LaunchDaemons/io.redis.redis-server.plist

# 3.粘贴以下内容（command+v），保存文件(Control+O)，退出(Control+X)

# <?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
# <plist version="1.0">
# <dict>
#   <key>Label</key>
#   <string>io.redis.redis-server</string>
#   <key>ProgramArguments</key>
#   <array>
#         <string>/usr/local/bin/redis-server</string>
#   </array>
#   <key>RunAtLoad</key>
#   <true/>
# </dict>
# </plist>

# 4. 设置自动启动
# sudo launchctl load /Library/LaunchDaemons/io.redis.redis-server.plist

# 5.尝试启动Redis，看看有没有报错
# sudo launchctl start io.redis.redis-server

# 6.重启你的烂苹果，即可。

# 7.可以用redis-cli来测试是否已经启动了Redis