# -*- encoding: utf-8 -*-
'''
Created on 2017年3月21日

@author: ghou
'''
import re
from functools import reduce

# (1)
print ('hello python')
name = raw_input('what is your name?')
if name.endswith('hou'):
    print 'Hello hou'
elif name.endswith('guang'):
    print 'Hello guang'
else:
    print 'Hello dong'

# (2)
text = "JGood is a handsome boy, he is cool, clever, and so on..."
print re.sub(r'\s', '-', text) 

# (3)
def pre_edit(string_items):    
    def reducer(acc, y):
        print acc, y
        for i in acc:  
            acc.pop()
        acc.append(y)                                                                                   
        return acc
    result = reduce(reducer,string_items,[])      
    return result
