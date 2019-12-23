# -*- encoding: utf-8 -*-
'''
Created on 2019年11月10日

@author: houguangdong
'''

# Mac上scrapy环境搭建踩坑记录
# 直接上问题

# There was a problem confirming the ssl certificate:[SSL: TLSV1_ALERT_PROTOCOL_VERSION]tlsv1 alert protocol version(_ssl.c:590)- skipping
# pip install --upgrade pip不能升级自己
# curl https://bootstrap.pypa.io/get-pip.py | sudo python快
# 升级后pip 18.1
# 原因pip版本太低，python.org已经不支持TLSv1.0和TLSv1.1
# 升级后pip install scrapy
# incremental无法安装
# sudo pip install --upgrade incremental  -i http://pypi.douban.com/simple/ --trusted-hostpypi.douban.com
# 一定要用sudo，豆瓣的设置为信任
# pyasn1-modules 0.2.2 has requirement pyasn1<0.5.0,>=0.4.1,but you'll have pyasn1 0.2.3 which is incompatible
# 安装完成后pyasn1版本又不对
# sudo pip install pyasn1-modules
# 还是需要sudo，不然不能升级
# 再安装
# Found existing installation: zope.interface 4.1.1
#     Uninstalling zope.interface-4.1.1:
# Could not install packages due to an EnvironmentError:[('/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/zope/__init__.py’…….
# 我去的大爷，怎么卸载都不行，sudo完全无效
# 只能解释为系统内置package，无法升级，只能ignore
# sudo pip install Scrapy --upgrade --ignore-installed zope.interface
# 中间还安装了setuptools
# sudo -H pip install -U setuptools  去安装了setuptools
# 总算完成，问题千人千面，只是本人当前mac电脑上出现，如果为了方便，建议还是用官方推荐的方式，先安装virtualenv，和当前环境隔离，可能碰到的坑就少了。