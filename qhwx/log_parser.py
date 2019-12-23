#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/10 15:33

import os
import os.path
import json


pwork_dir = os.path.split(os.path.abspath(__file__))[0]
mtalog_file_path = os.path.join(pwork_dir, 'mta-log.log')


for parent, pdirname, pfilenames in os.walk(pwork_dir, followlinks=True):
    for filename in pfilenames:
        if filename == 'mta-log_read.py' or filename == 'mta-log.log':
            continue
        file_path = os.path.join(parent, filename)
        with open(mtalog_file_path, 'a+') as fsb:
            with open(file_path, mode='r') as f:
                for line in f.readlines():
                    json_line = json.loads(line)
                    json_line = eval(json_line)
                    if json_line['ctgr'] == 'GameOnlineAmountEvent':
                        fsb.write(line)
                        fsb.write('\n')