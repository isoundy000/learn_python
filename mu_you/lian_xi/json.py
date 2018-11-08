#! /usr/bin/env python # coding:utf8
'''
Created on 09/11/2016

@author: ghou
'''

import re
import os

import simplejson
from collections import OrderedDict
# from l10nparser.base import parser
# from l10nparser.base.stringitems import StringItems
# from l10nparser.base import hashcodegen
from simplejson import JSONDecodeError
import codecs


class JsonParser():

    def __init__(self, file_path):
        sepCharRe = r'%(key)s\"\s*:\s*\"'
        self.valueReg = re.compile(r'(.*)\"')
        self.dupKey = {}                                  # duplicate key corresponding value
        self.sepType = [int, bool, long]                  # types that do not require parsing
        self.dupKeyPosition = 0                           # position can only take zero
        self.noTranslateKeyList = []                      # do not need to parse the list key
        # parser.Parser.__init__(self,file_path, sepCharRe, None, None)

    def _open_resource_file(self, file_name):
        file_stream = codecs.open(file_name, 'r', encoding='utf-8')
        return file_stream

    def load(self, file_name):
        """ Load properties_old from an open file stream """
        stream = self._open_resource_file(file_name)
        lines = stream.read()
        self._parse(lines)
        # self._add_prev_next_hashcode()

    def my_obj_pairs_hook(self, lst):
        """
        find duplicate key and value
        """
        result = {}
        count = {}
        for key, val in lst:
            if key in count:
                count[key] = 1 + count[key]
            else:
                count[key] = 1
            if key in result:
                if count[key] > 2:
                    result[key].append(val)
                else:
                    result[key]=[result[key], val]
            else:
                result[key]=val

        for key, val in result.iteritems():
            if type(val) == list and len(result.get(key)) > 1:
                if key not in self.dupKey:
                    self.dupKey[key] = val
                else:
                    self.dupKey[key].extend(val)

    def _parse(self, lines):
        """
        parse json data
        params: lines source data
        """
        try:
            jsonObject = simplejson.loads(lines, object_pairs_hook=OrderedDict)
        except JSONDecodeError, e:
            message = "%s %s" % ("json file format is incorrect!!!", e)
            raise Exception(message)

        # duplicate key
        simplejson.loads(lines, object_pairs_hook=self.my_obj_pairs_hook)

        dupKeyList = []
        for key, value in jsonObject.iteritems():
            keyPrefix = ''
            keyPrefix = keyPrefix + key
            if type(value) == OrderedDict:
                if keyPrefix in self.noTranslateKeyList:
                    continue
                lines, dupKeyList = self.recursive_dict(value, lines, keyPrefix, dupKeyList)
            elif type(value) == list:
                if keyPrefix in self.noTranslateKeyList:
                    continue
                lines, dupKeyList = self.recursive_list(value, lines, keyPrefix, dupKeyList)
            elif type(value) in self.sepType or value == None or value == "":
                continue
            else:
                if key in self.noTranslateKeyList:
                    continue
                # processing string values to repeat the first
                if key in self.dupKey and keyPrefix not in dupKeyList:
                    dupKeyValue = self.dupKey.get(key)[self.dupKeyPosition]
                    if dupKeyValue:
                        value = dupKeyValue
                    dupKeyList.append(keyPrefix)

                brp = self._sep_char_re % ({'key': re.escape(key)})
                block_reg_pattern = re.compile(brp)
                m1 = block_reg_pattern.search(lines)
                end = m1.span()[1]
                block = lines[:end]
                newLine = lines[end:]
                m2 = self.valueReg.search(newLine)
                value = m2.group(1)
#                 value = value.replace('\\', '\\\\').replace('\r', '\\r').replace('\r\n', '\\r\\n').replace('\t', '\\t').replace('\"', '\\"').replace('\n', '\\n')
                lines = lines[end+len(value):]
                hashcode = hashcodegen.getHashCode(value)
                self._generate_item('', keyPrefix, value, block, hashcode)

        self._generate_item('','','',lines,'')
        return

    def recursive_dict(self, value, lines, keyPrefix, dupKeyList):
        """
        recursive dict
        params: value      dict type
                lines      source data
                keyPrefix  key prefix
        """
        key_list = []
        for key, valueNew in value.iteritems():
            if type(valueNew) == OrderedDict:
                keyNew = keyPrefix + key
                if keyNew in self.noTranslateKeyList:
                    continue
                lines, dupKeyList = self.recursive_dict(valueNew, lines, keyNew, dupKeyList)
            elif type(valueNew) == list:
                keyNew = keyPrefix + key
                if keyNew in self.noTranslateKeyList:
                    continue
                lines, dupKeyList = self.recursive_list(valueNew, lines, keyNew, dupKeyList)
            elif type(valueNew) in self.sepType or valueNew == None or valueNew == "":
                continue
            else:
                if key in self.noTranslateKeyList:
                    continue
                # processing string values to repeat the first
                if key in self.dupKey and keyPrefix not in dupKeyList and keyPrefix+key in key_list:
                    depKeyValue = self.dupKey.get(key)[self.dupKeyPosition]
                    if depKeyValue:
                        valueNew = depKeyValue
                    dupKeyList.append(keyPrefix)

                brp = self._sep_char_re % ({'key': re.escape(key)})
                block_reg_pattern = re.compile(brp)
                m = block_reg_pattern.search(lines)
                end = m.span()[1]
                block = lines[:end]
                newLine = lines[end:]
                m2 = self.valueReg.search(newLine)
                valueNew = m2.group(1)
#                 valueNew = valueNew.replace('\\', '\\\\').replace('\r', '\\r').replace('\r\n', '\\r\\n').replace('\t', '\\t').replace('\"', '\\"').replace('\n', '\\n')
                lines = lines[end+len(valueNew):]
                hashcode = hashcodegen.getHashCode(valueNew)
                key = keyPrefix + key
                key_list.append(key)
                self._generate_item('', key, valueNew, block, hashcode)
        return lines, dupKeyList

    def recursive_list(self, value, lines, keyPrefix, dupKeyList):
        """
        recursive list
        params: value      list type
                lines      source data
                keyPrefix  key prefix
        """
        for idx, item in enumerate(value):
            if type(item) == OrderedDict:
                lines, dupKeyList = self.recursive_dict(item, lines, keyPrefix, dupKeyList)
            elif type(item) == list:
                keyNew = keyPrefix + str(idx)
                if keyNew in self.noTranslateKeyList:
                    continue
                lines, dupKeyList = self.recursive_list(item, lines, keyNew, dupKeyList)
            elif type(item) in self.sepType or item == None or item == "":
                continue
            else:
                item = str(item)
                if item in self.noTranslateKeyList:
                    continue
                item = item.replace('\\', '\\\\').replace('\r', '\\r').replace('\r\n', '\\r\\n').replace('\t', '\\t').replace('\"', '\\"').replace('\n', '\\n')
                if item.endswith("\'"):
                    itemRep = item.replace("\'", "\\'")
                    itemIndex = lines.find(itemRep)
                    if itemIndex < 0:
                        raise Exception("this value is not found in list %s" % item)
                    block = lines[:itemIndex]
                    lines = lines[len(block)+len(itemRep):]
                elif item.endswith('\"'):
                    itemRep = item.replace('\"', '\\"')
                    itemIndex = lines.find(itemRep)
                    if itemIndex < 0:
                        raise Exception("this value is not found in list %s" % item)
                    block = lines[:itemIndex]
                    lines = lines[len(block)+len(itemRep):]
                else:
                    reg = re.compile(item)
                    m = reg.search(lines)
                    end = m.span()[0]
                    block = lines[:end]
                    lines = lines[end+len(item):]
                hashcode = hashcodegen.getHashCode(item)
                key = keyPrefix + str(idx)
                
                self._generate_item('', key, item, block, hashcode)
        return lines, dupKeyList


if __name__=="__main__":
    rootdir = r"/Users/houguangdong/Workspace/learn_python/mu_you/bug/4/"
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            if not filename.endswith(".json"):
                continue
            par_type = JsonParser(os.path.join(parent,filename))
            par_type.load()
            targetList = []
            print '*'*20+'Loading successfully'+'*'*20
            for item in par_type._string_item_list:
                sitem=StringItems()
                sitem.comment=item.comment
                sitem.block=item.block
                sitem.value='$$$$$'+item.value+'#####'
                targetList.append(sitem)
            # new_parent = parent.replace('source', 'target')
            # if not os.path.exists(new_parent):
            #     os.makedirs(new_parent)
            # tg_path = new_parent + "\\" + filename
            # print tg_path, '33333'
            # par_type.store(targetList, tg_path)