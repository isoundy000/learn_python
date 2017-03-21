# -*-coding:utf-8-*-
'''
Created on 12/5/2016

@author: ghou
'''

import redis
  
  
r = redis.Redis(host="10.117.171.148", port='6300', db=0)
r.set('a', 'bb')
print r.get('a')
r.set('cc', 'houguangdong')
r.set('ddd', 'fff')
print r.keys()

a = 'aaa\rbbb\ncccc\r\ndddd\teeeee"fffffff\\ngg\ggggg'
c = a.replace('\\', '\\\\')
print c
b = c.replace('\r', '\\r').replace('\r\n', '\\r\\n').replace('\t', '\\t').replace('\"', '\\"').replace('\n', '\\n')
print b