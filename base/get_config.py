#-*-coding:utf-8-*-
'''
Created on 2017.2.10

@author: xuli
'''
from ConfigParser import ConfigParser as config
from configobj import ConfigObj
from constants import configConstants as CON

import os
class getConfig(object):
    '''
    This is for getting information from configuration file
    '''

    def __init__(self, config_path):
        '''
        Constructor
        '''
        self.config_path = config_path
        self.config_dic = ConfigObj(self.config_path)
#         print self.config_dic
    def get_source_path(self):
        if CON.SOURCEHOME in self.config_dic.keys():
            source_home_dic = self.config_dic[CON.SOURCEHOME] 
            return source_home_dic
        else:
            raise Exception('Can not find session: %s'%CON.SOURCEHOME)
        
    def get_dest_path(self):
        if CON.DESTHOME in self.config_dic.keys():
            source_home_dic = self.config_dic[CON.DESTHOME]    
            return source_home_dic
        else:
            raise Exception('Can not find session: %s'%CON.DESTHOME)
    def is_need_mapping(self):
        '''
        This is for config and script mapping module
        '''
        if CON.NEEDMAPPING in self.config_dic.keys():
            source_home_dic = self.config_dic[CON.NEEDMAPPING]
            if CON.NEEDMAPPING in source_home_dic.keys():    
                return eval(source_home_dic[CON.NEEDMAPPING])
            else:
                raise Exception('Can not find key: %s'%CON.NEEDMAPPING)
        else:
            raise Exception('Can not find session: %s'%CON.NEEDMAPPING)
        
    def get_mapping_path(self):
        mapping_path_dic = self.config_dic[CON.MAPPING_FILE_PATH]
        return mapping_path_dic
    
    def get_mapping_dic(self):
        dic = {}
        mapping_dic = self.config_dic[CON.MAPPINGDIC]
        for key in mapping_dic.keys():
            dic[key] = eval(','.join(mapping_dic[key]))
        return dic
        
    def get_exclude_list(self):
        exlude_file_list = []
        exclude_dic = self.config_dic[CON.EXCLUDE_FOLDER]
        for key in exclude_dic.keys():
            exlude_file_list.append(exclude_dic[key])
            
        return exlude_file_list
    
    def get_sudo_password(self):
        return self.config_dic[CON.SUDO_PASSWORD][CON.SUDO_PASSWORD]
    
    def get_settings_template_path(self):
        # print 'settings_template: %s'%self.config_dic[CON.SETTINGS_TEMPLATE_PATH]
        return self.config_dic[CON.SETTINGS_TEMPLATE_PATH]

    def get_settings_path(self):
        return self.config_dic[CON.SETTINGS_PATH]

    def get_backup_path(self):
        backup_path = self.config_dic[CON.BACKUP_PATH][CON.BACKUP_PATH]
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)

        return backup_path
if __name__ =="__main__":
    con = getConfig(CON.CONFIG_FILE_PATH)
    print con.get_source_path()
    print con.get_dest_path()
    print con.is_need_mapping()
    print type(con.is_need_mapping())
    print con.get_mapping_dic()
    print con.get_exclude_list()
    print con.get_mapping_path()
    print con.get_sudo_password()
    print con.get_settings_template_path()