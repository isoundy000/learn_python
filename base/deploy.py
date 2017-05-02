#-*-coding:utf-8-*-
'''
Created on 3/1/2017

@author: xuli
'''
from constants import configConstants as CON
from get_config import getConfig
import os
import pexpect
import time


class Deploy(object):
    '''
    This class is specified for GRM deploy
    '''
    def __init__(self):
        
        self.con = getConfig(CON.CONFIG_FILE_PATH)
        self.dest_home_front = self.con.get_dest_path()[CON.FRONT]
        self.source_home_front = self.con.get_source_path()[CON.FRONT]
        self.source_home_back = self.con.get_source_path()[CON.BACK]
        self.dest_home_back = self.con.get_dest_path()[CON.BACK]
        self.l10n = self.con.get_mapping_path()[CON.L10N]
        self.config_release_path = self.con.get_mapping_path()[CON.CONFIG_RELEASE_PATH]
        self.config_data_path = self.con.get_mapping_path()[CON.CONFIG_DATA_PATH]
        self.script_path = self.con.get_mapping_path()[CON.SCRIPTS_PATH]
        self.passwd = self.con.get_sudo_password()
        self.backup_path = self.con.get_backup_path()

    def empty_backup_file(self,backup_file_path):
        cmd = "sudo rm -rf %s"%backup_file_path
        # print 'empyty backup file:%s'%cmd
        if os.path.exists(backup_file_path):
            child = pexpect.spawn(cmd)
            index = child.expect(["(?i)password",pexpect.EOF,pexpect.TIMEOUT])
            # print '[**]empty index %d'%index
            if not index:
                child.sendline(self.passwd)
            else:
                child.sendline(self.passwd)
            if not os.path.exists(backup_file_path):
                print "[*] Backup file has been deleted:%s"%backup_file_path
                return
            else:
                raise Exception("File can not be deleted:%s"%backup_file_path)

              
    def delete_file(self,file_path):
        # print 'filepath:%s'%file_path
        filename = file_path.split('/')[-1]
        backup_filename = os.path.join(self.backup_path,filename)
        self.empty_backup_file(backup_filename)
        # print 'filename:%s'%filename
        # print 'backUp:%s'%self.backup_path
        # print 'backup_path:%s'%os.path.join(self.backup_path,filename)
        cmd = 'sudo mv %s %s'%(file_path,self.backup_path)
        # print 'delete cmd: %s'%cmd
        password = self.passwd
        if not os.path.exists(file_path):
            return
        else:
            child = pexpect.spawn(cmd)
            index = child.expect(["(?i)password",pexpect.EOF,pexpect.TIMEOUT])
            # print 'delete index:{}'.format(index)
            if not index:
                child.sendline(password)
            else:
                child.sendline(self.passwd)
            # time.sleep(5)
            if not os.path.exists(file_path):
                print "[*] Deleted file: %s"%file_path
                return
            else:
                raise Exception("%s can not be deleted!" % file_path)
                   
    def copy_file(self,source_path,dest_path):
        cmd = 'sudo cp -r %s %s'%(source_path,dest_path)
        # print "copy cmd: %s"%cmd

        password = self.passwd

        child = pexpect.spawn(cmd)
        index = child.expect(["(?i)password",pexpect.EOF,pexpect.TIMEOUT])
        if not index:
            child.sendline(password)
        else:
            child.sendline(password)
        if os.path.exists(dest_path):
            print '==>Copied file: %s'%dest_path
            return      
    
    def get_final_list(self,home_path):
        dest_content_list = os.listdir(home_path)
        exclude_list = self.con.get_exclude_list()
        for i in exclude_list:
            if i in dest_content_list:
                dest_content_list.remove(i) 
        return  dest_content_list 
    
    def modify_config_file(self,config_file_path, pattern=None ,targetstring=None):
        targetstring = "xuli,"
        import re 
        pattern = re.compile(".*?(dupkey_receiver_list|l10nverify_receiver_list)\s*=\s*(.*).*?")
        with open(config_file_path,'r') as r:
            lines = r.readlines()
        with open(config_file_path,'w') as w:
            for content in lines:
                if re.match(pattern, content):
                    m = re.match(pattern, content)
                    content = content.replace(m.group(2),targetstring)
                w.write(content)
                
        print "[*] File modified: %s"%config_file_path
    
    def mapping_file(self,release_base_source,release_base_target,source_release_number, target_release_number):
        self.delete_file(release_base_target.format(target_release_number))
        self.copy_file(release_base_source.format(source_release_number), release_base_target.format(target_release_number))
        
    def config_mapping(self,release_base_source,release_base_target):
        config_dic = self.con.get_mapping_dic()[CON.CONFIG_DIC]
        for key in config_dic.keys():
            self.mapping_file(release_base_source,release_base_target,key,config_dic[key])
            if  '/releases/' in release_base_source:
                self.modify_release_file(release_base_target, key, config_dic[key])
            
    def deploy_setting_file(self,field):
        '''
        field only get value 'back_end' or 'front_end'
        '''
        settings_template_dic = self.con.get_settings_template_path()
        settings_dic = self.con.get_settings_path()
        
        self.delete_file(settings_dic[field])
        self.copy_file(settings_template_dic[field], settings_dic[field])
        print "[[*]] Settings file has been deployed to code path."
     
    def copy_settings_to_template(self,field): 
        settings_template_dic = self.con.get_settings_template_path()
        settings_dic = self.con.get_settings_path()
        if os.path.exists(settings_dic[field]):
            self.delete_file(settings_template_dic[field])
            self.copy_file(settings_dic[field],settings_template_dic[field])
            if os.path.exists(settings_template_dic[field]):
                print '===>Settings file copied succefully for file : %s'%settings_template_dic[field]
            else:
                raise Exception("Settings file can not copy to %s"%settings_template_dic[field])
              
    def script_mapping(self,release_base_source,release_base_target): 
        script_dic =  config_dic = self.con.get_mapping_dic()[CON.SCRIPT_DIC]
        for key in script_dic.keys():
            self.mapping_file(release_base_source,release_base_target,key,script_dic[key])
        
    def service_restart(self):
        kill_supervisor_cmd = "ps -aux| grep 'supervisor'|awk '{print $2}'|sudo xargs kill -9"
        kill_celery_cmd = "ps -aux| grep 'celery'|awk '{print $2}'|sudo xargs kill -9"
        restart_supervisor_cmd = "sudo supervisord -c /etc/supervisor/supervisord.conf"
        restart_apache_cmd = "sudo service apache2 restart"
        time.sleep(1)
        child = pexpect.spawn(kill_supervisor_cmd)
        index = child.expect(["(?i)password",pexpect.EOF,pexpect.TIMEOUT])
        if not index:
            child.sendline(self.passwd)
        time.sleep(1)
        child = pexpect.spawn(kill_celery_cmd)
        index = child.expect(["(?i)password",pexpect.EOF,pexpect.TIMEOUT])
        if not index:
            child.sendline(self.passwd)
        time.sleep(2)
        child = pexpect.spawn(restart_supervisor_cmd)
        index = child.expect(["(?i)password",pexpect.EOF,pexpect.TIMEOUT])
        if not index:
            child.sendline(self.passwd)
        time.sleep(2)
        child = pexpect.spawn(restart_apache_cmd)
        index = child.expect(["(?i)password",pexpect.EOF,pexpect.TIMEOUT])
        if not index:
            child.sendline(self.passwd)
        time.sleep(3)
        print "Services restart successfully" 

    def front_end_deploy(self):
        field = CON.FRONT
        self.copy_settings_to_template(field)
        deploy_list = self.get_final_list(self.dest_home_front)
        for i in deploy_list:
            file_path = os.path.join(self.dest_home_front,i)
            print 'file path:',file_path
            backup_filename = os.path.join(self.backup_path, i)
            self.empty_backup_file(backup_filename)
            self.delete_file(file_path)
            self.copy_file(os.path.join(self.source_home_front,i), file_path)
        self.deploy_setting_file(field)
        if self.con.is_need_mapping():
            config_data_base_source = os.path.join(self.source_home_front,self.l10n,self.config_data_path)
            config_data_base_target = os.path.join(self.dest_home_front,self.l10n,self.config_data_path)
            #config_release_base_source = os.path.join(self.source_home_front,self.l10n,self.config_release_path)
           # config_release_base_target = os.path.join(self.dest_home_front,self.l10n,self.config_release_path)
            self.config_mapping(config_data_base_source, config_data_base_target)
           # self.config_mapping(config_release_base_source, config_release_base_target)
            
            script_base_source = os.path.join(self.source_home_front,self.l10n,self.script_path)
            script_base_target = os.path.join(self.dest_home_front,self.l10n,self.script_path)
            self.script_mapping(script_base_source, script_base_target)
            
        self.service_restart()
        print "*"*20+"Front-end has been deployed successfully"+"*"*20

    def back_end_deploy(self):
       
        field = CON.BACK

        self.copy_settings_to_template(field)
        deploy_list = self.get_final_list(self.dest_home_back)
        for i in deploy_list:
            file_path = os.path.join(self.dest_home_back,i)
            self.delete_file(file_path)
            self.copy_file(os.path.join(self.source_home_back,i), file_path)
        self.deploy_setting_file(field)
        if self.con.is_need_mapping():
            config_data_base_source = os.path.join(self.source_home_back,self.config_data_path)
            config_data_base_target = os.path.join(self.dest_home_back,self.config_data_path)
            self.config_mapping(config_data_base_source, config_data_base_target)
        for parpath, dirinfo, files in os.walk(os.path.join(self.dest_home_back,"config","data")):
            for file in files:
                if file == "Configuration.ini":
                    self.modify_config_file(os.path.join(parpath,file))
            
        print "*" * 20 + "Back-end has been deployed successfully" + "*" * 20

    def both_deploy(self):
        self.front_end_deploy()
        self.back_end_deploy()   
            
        
    
    
if __name__ =='__main__':
    import os
    print os.getcwd()
    release_base = '/var/www/g11nRepository/l10n/config/releases/release_{}.py'
    source_number = 158
    target_number = 143
    de = Deploy()
    de.modify_release_file(release_base=release_base,source_release_number=source_number,target_release_number=target_number)

    
    
    
    
    
    
