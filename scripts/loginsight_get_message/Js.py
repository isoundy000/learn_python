# -*- coding: utf-8 -*- 
'''
Created on Apr 4, 2015

@author: pengr
'''

import sys,os
import re


from l10nparser.base import stringitems
from l10nparser.base import parser

from l10nparser.js.handler.ast import Assign,String,DotAccessor
from l10nparser.js.handler.handler import Handler
from l10nparser.js.handler import nodevisitor
from l10nparser.base import hashcodegen


class JsParser(parser.Parser):
    encoding='utf-8'
    def __init__(self,file_path):

        ver_char_re=re.compile(r'^[\s]*?$')
        
        parser.Parser.__init__(self,file_path,None,ver_char_re,None)
 
    def load(self):
        """ Load properties_old from an open file stream """
        stream=self._open_resource_file()
        lines = stream.read()
        self._parse(lines)
        self._add_prev_next_hashcode()


    def _parse(self, lines):
        curr_block=""
        curr_key=""
        curr_value=""
        curr_comment=""
        block_stat_op=0
        key_count = 0
        
        tree = Handler().parse(lines)
        
        for node in nodevisitor.visit(tree):
         
            if isinstance(node, String):
#                 print node.value
#                 print node.oppos
                curr_key=key_count
                curr_value=node.value
                
                if curr_value[0]=="'" or curr_value[-1]=="'":
                    curr_value=curr_value.strip("'")
                    

                elif curr_value[0]=="\"" or curr_value[-1]=="\"":
                    curr_value=curr_value.strip("\"")
                    
                else:
                    print curr_value
                    raise Exception("Unhandled format. file name: %s format: %s" % (self._file_path,curr_value))
#                 print
                
                m2=self._ver_char_re.match(curr_value)
                if m2:
                    continue
                
                v_stat_op=int(node.oppos)


                curr_block=lines[block_stat_op:v_stat_op+1]
                block_stat_op=v_stat_op+len(curr_value)+1
                hashcode=hashcodegen.getHashCode(curr_value)
                 
                self._generate_item(curr_comment,str(curr_key),curr_value,curr_block,hashcode)
                key_count += 1 
                curr_block=""
                curr_key=""
                curr_value=""
                curr_comment=""
                 
        last_block=lines[block_stat_op:]
        hashcode=hashcodegen.getHashCode(curr_value)
        self._generate_item(curr_comment,str(curr_key),curr_value,last_block,hashcode)
                                    


 
if __name__=="__main__":
 
    rootdir = r"test\\"
    source_folder="source"
    for parent,dirnames,filenames in os.walk(rootdir+source_folder):
      
        for filename in filenames:
            if not filename.endswith(".js"):
                continue

            parser = JsParser(os.path.join(parent,filename))
        
            parser.load()
            targStringItems=[]
            for j in parser._string_item_list:
            
                sitem=stringitems.StringItems()
                sitem.comment=j.comment
            
                sitem.key=j.key
#                 print j.key
                sitem.block=j.block
                if j.value:
#                     print j.value
                    sitem.value=j.value
                sitem.hashcode=j.hashcode
                print j.hashcode    
            
                targStringItems.append(sitem)
                tg_path=rootdir+"/target/"
                if not os.path.exists(tg_path):
                    
                    os.makedirs(tg_path)
            parser.store(targStringItems, tg_path+filename)   



