# -*- encoding: utf-8 -*-
'''
Created on 2017年2月27日

@author: houguangdong
'''

# 得到N以内的所有的质数
import string


def isPrime(num):
    i = 2
    while(i < num):
        if (num % i ==0):
            return False
        else:
            i = i + 1
    return True


if __name__=='__main__':
    input1 = raw_input("Assign a number N:")
    input1 = string.atoi(input1)
    for j in range(1, input1+1):
        if(isPrime(j)):
            print j