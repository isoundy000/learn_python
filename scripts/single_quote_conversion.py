'''
@author: ghou
'''

import re

    
unescaped_quote_regex_list=[re.compile(r"(.*[^'](')[^'].*)"),
                            re.compile(r"(^(')[^'].*)"),
                            re.compile(r"(.*[^'](')$)")]




def validate(property):
#     print property
    locate_info=()
    for _idx, regex_item in enumerate(unescaped_quote_regex_list):
        m=regex_item.search(property)
    
        if m:
            print m.span(2), '000000', _idx
            locate_info= m.span(2)
            break
    return locate_info    


def escape(property):
    
    locate_info=validate(property)
    
    while locate_info:
        print property, '11111111', locate_info
        property=property[:locate_info[0]]+"''"+property[locate_info[1]:]
        print '22222222', property
        locate_info=validate(property)
    return property
            
            
if __name__=="__main__":
    sampleStr="'c'o'u'n't' o'o'oo'cgfgfg'fgfg'f''g'{1}"
    a = escape(sampleStr)
    print a, '33333333'
    

            
        
        
    