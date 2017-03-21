# -*-coding:utf-8-*-
'''
@author: ghou
'''

import re
# 转义模式 
# regex list for unescaped patterns.    
unescaped_quote_regex_list=[re.compile(r"([^\\](\\\\)*')")]


def validate(value,escaper='\\'):
    locate_index=()
    count = value.count(escaper)
    print value
    for regex_item in unescaped_quote_regex_list:
        print value, '000000000000'
        m=regex_item.search(value)    
        if m:
            print '111111111', m.span()
            locate_index= m.span()
            break
    return locate_index    


def escape(value, escaper='\\'):
 
    locate_index=validate(value)
    
    while locate_index:
        start, end = locate_index
        print value[:end-1],'3333333', value[end-1:]
        value=value[:end-1]+ escaper +value[end-1:]
        print '22222222222', value
        locate_index=validate(value)
    return value
    
    
            
if __name__=="__main__":
    sampleStr="a\\\'1\\'2\'3'd'e"
    print escape(sampleStr)
    

    

            
        
        
    