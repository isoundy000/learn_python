#-*-coding:utf-8-*-
'''
Created on 2017.3.2

@author: xuli
'''
from base.deploy import Deploy
import sys
import os
print os.getcwd()
de = Deploy()

def print_items():
    print '''
    Use command python excute.py -f to deploy.
    Please make sure that you have copy the settings file to /home/v/settingsForTestEnv/
    -f    only deploy front-end
    -b    only deploy back-end
    -fb   both of fron-end and back-end will be deployed
    -bf   both of fron-end and back-end will be deployed
    -h    get help information
    '''

def exexute():
    arg_dic = {'-f':de.front_end_deploy,'-b':de.back_end_deploy,'-bf':de.both_deploy,'-fb':de.both_deploy,'-h':print_items}
    if len(sys.argv) != 2 or sys.argv[1] not in arg_dic.keys():
        print "Please give the correct argument! e.g python excute.py -f!"
    else:
        arg_dic[sys.argv[1]]()
    

if __name__ == '__main__':

    exexute()