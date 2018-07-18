# -*- encoding: utf-8 -*-
'''
Created on 2018年5月30日

@author: houguangdong
'''
import reimport

reimport.reimport()


from datetime import datetime


def qian_tao_han_shu(a, b):
    def tmp_han_shu(c, d=a, f=b):
        return c + a + b
    return tmp_han_shu


z = {
    1: qian_tao_han_shu(1, 2),
    2: None
}


collect_func = z[1]
if not collect_func:
    print '111111'
    pass
else:
    start_now = datetime.now()
    print collect_func(3)
    end_now = datetime.now()
    cha_time = end_now - start_now
    print cha_time.seconds + cha_time.microseconds / 1000000.0, cha_time.microseconds