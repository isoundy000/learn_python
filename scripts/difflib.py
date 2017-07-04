# -*- coding: utf-8 -*-
'''
Created on 7/4/2017

@author: ghou
'''

import difflib
import sys

try:
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
except Exception, e:
    print "Error " + str(e)
    print "Usage: %s filename1 filename2" % str(sys.argv)
    sys.exit()

def readfile(filename):
    try:
        newfile = open(filename, 'rb')
        text = newfile.read().splitlines()
        newfile.close()
        return text
    except IOError as error:
        print "Read file Error: " + str(error)
        sys.exit()

if filename1 == '' or filename2 == '':
    print "Usage: %s filename1 filename2" % str(sys.argv)
    sys.exit()

test1_line = readfile(filename1)
test2_line = readfile(filename2)
d = difflib.HtmlDiff()
print d.make_file(test1_line, test2_line)