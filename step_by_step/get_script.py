import os

config_dic = {116:121,136:129,87:87,105:92,67:67,106:112,57:57,147:138,136:129,63:63,112:114,144:137,151:142,103:91,125:128,113:113,143:136,104:103,111:119,90:90,116:121,119:105,115:126,159:146,158:143,2:2,87:87,140:133,139:132,124:122,142:135,157:145,149:140,148:139,160:144,150:141,137:130,123:127,138:131,141:134,98:96,101:100,95:93,99:97,100:98,96:94,97:95,109:117,110:115,107:118,108:116,120:84,47:47,114:125,102:102}
for product_release in config_dic.keys():
    if os.path.exists("/var/www/g11nRepository/l10n/config/data/release_{}".format(config_dic[product_release])):
        os.system("sudo rm -rf /var/www/g11nRepository/l10n/config/data/release_{}".format(config_dic[product_release]))
    if not os.path.exists("/var/www/g11nRepository/l10n/config/data/release_{}".format(config_dic[product_release])):
        print "/var/www/g11nRepository/l10n/config/data/release_{}".format(config_dic[product_release]),"has been deleted!"
        os.system("sudo cp -r /home/v/g11n-grm/g11nRepository/l10n/config/data/release_{} /var/www/g11nRepository/l10n/config/data/release_{}".format(product_release,config_dic[product_release]))
        if os.path.exists("/var/www/g11nRepository/l10n/config/data/release_{}".format(config_dic[product_release])):
            print "/var/www/g11nRepository/l10n/config/data/release_{}".format(config_dic[product_release]),"successfully"
id_dic = {116:121,136:129,111:119,112:114,123:127,124:122, 125:128, 137:130, 141:134, 144:137, 151:142, 159:146, 158:143, 104:103 }
code_home = '/var/www/g11nRepository/l10n/scripts/'
if os.path.exists(code_home):
    os.system("sudo rm -rf %s"%code_home)
if not os.path.exists(code_home):
    print "Scripts has been deleted successfully!"
    os.system("cp -r /home/v/g11n-grm/g11nRepository/l10n/scripts /var/www/g11nRepository/l10n/")
    for key in id_dic.keys():
        os.system('mv {}release_{} {}release_{}'.format(code_home,key,code_home,id_dic[key]))
        if os.path.exists('{}release_{}'.format(code_home,id_dic[key])):
            print '{}release_{}'.format(code_home,id_dic[key]),'successfully'


