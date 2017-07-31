#!/usr/bin/env python
# -*-encoding:utf-8-*-
'''
Created on 2017年7月29日

@author: houguangdong
'''
from __future__ import unicode_literals
from __future__ import division
from PIL import Image


im = Image.open('ghou.jpg')
print im.format, im.size, im.mode
im.thumbnail((200,100))
im.save('dong.png', 'PNG')


# 由于Python是由社区推动的开源并且免费的开发语言，不受商业公司控制，因此，Python的改进往往比较激进，不兼容的情况时有发生。Python为了确保你能顺利过渡到新版本，特别提供了__future__模块，让你在旧的版本中试验新版本的一些特性。
print '\'xxx\' is unicode?', isinstance('xxx', unicode)
print 'u\'xxx\' is unicode?', isinstance(u'xxx', unicode)
print '\'xxx\' is str?', isinstance('xxx', str)
print 'b\'xxx\' is str?', isinstance(b'xxx', str)

# 而在Python 3.x中，所有的除法都是精确除法，地板除用//表示：
print 10/3
print 10//3
print 10.0/3
