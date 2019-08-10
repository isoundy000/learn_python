# -*- coding: utf-8 -*-
'''
Created on 2017年3月21日

@author: ghou
'''
import re

pattern = re.compile("([0-9]{20}).tag$")
str1 = "http://1920221212121212122112112122112121212.tag"

print pattern.search(str1).group(1)

fruits = ['Banana', 'Apple', 'Lime']
print list(enumerate(fruits))

a = ['2', '37', '38']
b = ['vRA', 'VIO', 'Marvin2.0.0']
dictionary = dict(zip(a, b))
print dictionary