# -*- encoding: utf-8 -*-
'''
Created on 2018年10月23日

@author: houguangdong
'''

import os
import simplejson
from simplejson import JSONDecodeError
from collections import OrderedDict
import codecs


def main(a, b):
    for filename in os.listdir('../bug/4/'):
        if filename.endswith('.json'):
            full_name = a + filename
            stream = codecs.open(full_name, 'r', encoding='utf-8')
            lines = stream.read()
            try:
                jsonObject = simplejson.loads(lines, object_pairs_hook=OrderedDict)
            except JSONDecodeError, e:
                message = "%s %s" % ("json file format is incorrect!!!", e)
                raise Exception(message)

            # duplicate key
            simplejson.loads(lines)
            flag = False
            for key, value in jsonObject.iteritems():
                if type(value) == OrderedDict:
                    lines, flag = recursive_dict(value, lines, b, flag)
                    if flag:
                        print filename
                        break
                else:
                    for i in b:
                        try:
                            c = str(key).find(i)
                            d = str(value).find(i)
                        except UnicodeEncodeError:
                            continue
                        if c >= 0 or d >= 0:
                            flag = True
                            break
                    if flag:
                        print filename
                        break


def recursive_dict(value, lines, b, flag):
    """
    recursive dict
    params: value      dict type
            lines      source data
            keyPrefix  key prefix
    """
    for key, valueNew in value.iteritems():
        if type(valueNew) == OrderedDict:
            lines, flag = recursive_dict(valueNew, lines, b, flag)
        else:
            for i in b:
                try:
                    c = str(key).find(str(i))
                    d = str(valueNew).find(str(i))
                except UnicodeEncodeError:
                    continue
                if c >= 0 or d >= 0:
                    flag = True
                    break
            if flag:
                break
    return lines, flag




for huan_ji, v in tmp.items():
    for server_id, value in v.items():
        for rid, num in value.items():
            print rid, num

if __name__ == '__main__':
    a = '/Users/houguangdong/Workspace/learn_python/mu_you/bug/4/'
    b = ['20004',
'20500',
'20501',
'20502',
'20503',
'20504',
'20505',
'20506',
'20359',
'20152',
'20267',
'20112',
'20113',
'20114',
'20115',
'20116',
'20117',
'20118',
'20119',
'20120',
'20121',
'20122',
'20123',
'20195',
'20775',
'20776',
'20777',
'20778',
'20779',
'20780',
'20781',
'20782',
'20783',
'20784',
'20785',
'20789',
'20790',
'20822',
'20823',
'20824',
'20830',
'20831',
'20832',
'20835']
    main(a, b)