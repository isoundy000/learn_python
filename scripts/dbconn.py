'''
Created on Jun 13, 2016

@author: xuli
'''
import logging
import logging.config
import psycopg2
import ConfigParser
import os

LOG_FILENAME = 'logging.conf'
LOG_CONTENT_NAME = 'pg_log' 

#Read the configuration file and get the value
config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))
host = config.get('global', 'host')
db = config.get('global','database')
usr = config.get('global', 'user')
passwd = config.get('global', 'password')
# def log_init(log_config_filename, logname):
#     logging.config.fileConfig(log_config_filename)
#     logger = logging.getLogger(logname)
#     return logger

#operate database method, need return value
def operate_postgre(sql):
    print 'Enter funtion %s...'%operate_postgre.__name__
#     pgdb_logger.debug("operate_postgre enter...")
    try:
        conn = psycopg2.connect(host = host, database = db,user = usr, password = passwd)
        cur = conn.cursor()
        cur.execute(sql)
        data_fileter = cur.fetchall()
        return data_fileter
    except Exception, e:
        print e
# sequence l should be a list with turple and strings. SQL result list        
def list_trans(l, m, n):
    print 'Enter funtion %s...'%list_trans.__name__
    l2 = l[m][n].split(',')
    return l2

#l1 should be the latest query result , and l2 should be the last but one
def sqlResult_compare(l1, l2):
    print 'Enter funtion %s...'%sqlResult_compare.__name__
    for i in l1:
        if i in l2:
            l1.remove(i)
            continue
    return l1  

def main():
    table_name = 'l10n_files'
    column_name = 'nodes'
    releaseid = 154
    sql_locpool = "select %s from %s where relativepath=\"%s\""%(column_name,table_name,releaseid)
    data_before = operate_postgre(sql_locpool)
    print "====>lines number:%d"%len(data_before)
    md5_list = []
    for i in data_before:
        strings = ''.join(i)
        md5_list.append(strings)
    final_string = ' '.join(md5_list)
        
    with open('data.txt','a')as f:
        f.write(final_string+'\n')
        
def verify_md5():
    with open('data.txt','r') as f:
        file_path = r"\\10.117.170.58\WSdisk\locpool"
        diff_list = []
        list_line = []
        file_verify_list = []
        lines = f.readlines()
        for line in lines:
#             print lines.index(line)
            locals()["list_%d"%lines.index(line)]=line.split(' ')
            list_line.append(locals()["list_%d"%lines.index(line)])
#             print list_line
            
#         for i in list_line[0]:
#             if i not in list_line[1]:
#                 diff_list.append(i)
#                 
#         print len(diff_list)
#         print "===>",diff_list
#         count = 0
#         for i in diff_list:
#             if os.path.exists(os.path.join(file_path,i)):
#                 count+=1
#                 print '[*]issue file:%s'%i
#                 print count
#             else:
#                 print '[@]%s'%i
            
#             print list_0
#         for i in list_1:
#             if i not in list_2:
#                 diff_list.append(i)
#         print diff_list
            
        for line in lines:
            strings_dic = {}
            count = 0
            strings = line.split(' ')
            for i in strings:
                if i not in strings_dic:
                    strings_dic[i]=1
                else:
                    strings_dic[i]+=1
                     
            for i in strings_dic:
                if strings_dic[i]!=1:
                    count+=1
                    print i+'===>%d'%strings_dic[i] 
                    print count
                
         
                
            
        
#     before = [('0f205278487afe4e2c73a7c706337c99',), ('71d390acd5aeef2cf47c510351764b00',), ('8f2220d9c05aab82b8225afec342f7e9',), ('98e5a278e13ffe4a351c6705d67e59cf',), ('41e841a24db47fdb75c24402c80b8754',), ('3776823c8eac52217ef6a5e5a2390d83',), ('81ede206906f4055d5b451b3d6fed89d',), ('15ed3b42d07496ff7efa2d623de4ea43',), ('1001cab725260b069ae6e7b13c7440eb',), ('38515515db99f34c21a9197d0643cca6',), ('059f8688edb6576d51cebcb0428ecbe8',), ('5639f6a30b56fb819de1e6e52c7ac050',), ('44599a206de859457d8edab0923a318e',), ('462e7de711ec13e37fd3dcdb439733f0',), ('0cc457739eccd7f8a745729f4acaedc4',), ('7acc9ffb339eba92231b6d8e363da053',), ('35e4b7a7d197680b21eaa83bcfee9baf',), ('7a38ae1f8b234470c7b8ff41fb92beb3',), ('a6e64ca171352696a79bcefb85a9d475',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('639c0999f70d98813758b700e0c847d9',), ('580e3daac42f0859a7e008b4767b67aa',), ('fb6d3a34883f512955765f35252dba6a',), ('f4e43c2c37d5ea253750bd7208801da9',), ('00a5cc29496e6e33d88b93f2860ed409',), ('f41f010ed743f63b954eaca3718b485e',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('dcb9c94fe079591e931fd15071792b5a',), ('775a721b9615d1b3462934d40faad00b',), ('91722bbc529ee7cde19119a4b256a45c',), ('b10b0a5999ff735aa3667fa151d98f12',), ('4a9e71f85c6c800714c526cb745857ad',), ('ec21a6d4637530aed29beba1af316418',), ('568d66286412ec16ca9a1a29e2d47344',), ('66e666d9b06584e96ab2fed41d2977ce',), ('87bde67cc2ab2f4de3f5cf1d8804b526',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('e062b8ddf155395ec90eb37d45c8ea06',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('20d59404afc7a4b6ba67b6d0c0e8a524',), ('a29315550f82279113a74a13cc3174a8',), ('74ec2afa685cc891327f5384dd3312d6',), ('bfdb8fcb89b5469fb92b7273608892f2',), ('49fef32236b6f33a94e156d3cad59250',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('6a156f403f89c7d3edb8a6f1fc2c42bb',), ('b84c9250fcc121c993720ec216bf85d7',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('0477bf9f38c7cd1ff84998d28a49f13c',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('4983cc2f53797a77e521a49e1c6456b5',), ('174840b18680426d4e9f5abb78b2b927',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('4dfed336f754f9fa83c75c8f674195ca',), ('5057b7d2220a85a2f29c24ea37e912ec',), ('61868f76f9f6b1224bc4b1afb3fab884',), ('ed28a5d0145c685c119de3d0f5d30d14',), ('b4e5a19885cfb38f708b693ef60ce01c',), ('76df634a6a478ab9b2f44a83ffed2d10',)]
#     after = [('e7eac3124ba3f8e86f36071c4904c519',), ('0f205278487afe4e2c73a7c706337c99',), ('44599a206de859457d8edab0923a318e',), ('7acc9ffb339eba92231b6d8e363da053',), ('98e5a278e13ffe4a351c6705d67e59cf',), ('a3a754f4ddfcaca76540d65ef2ef5ac4',), ('1001cab725260b069ae6e7b13c7440eb',), ('19a9d86551c8170df2362dc084c2eeef',), ('059f8688edb6576d51cebcb0428ecbe8',), ('dcb9c94fe079591e931fd15071792b5a',), ('0c048d4c061e1f971e43ef369c2f3238',), ('91722bbc529ee7cde19119a4b256a45c',), ('5057b7d2220a85a2f29c24ea37e912ec',), ('fe03c41508f69569db0f1aeee93634fd',), ('44599a206de859457d8edab0923a318e',), ('462e7de711ec13e37fd3dcdb439733f0',), ('d69df62737b070e0e5def3d99e4bd882',), ('7acc9ffb339eba92231b6d8e363da053',), ('7a38ae1f8b234470c7b8ff41fb92beb3',), ('2a32f90f4c4d2a23074328c3a8cc06a2',), ('a6e64ca171352696a79bcefb85a9d475',), ('a6e64ca171352696a79bcefb85a9d475',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('639c0999f70d98813758b700e0c847d9',), ('639c0999f70d98813758b700e0c847d9',), ('f10462ea9e40943d38cf5e164bf1d7bf',), ('c436b67718edf7c31017eef5a8ec1100',), ('059f8688edb6576d51cebcb0428ecbe8',), ('5639f6a30b56fb819de1e6e52c7ac050',), ('38515515db99f34c21a9197d0643cca6',), ('fb6d3a34883f512955765f35252dba6a',), ('462e7de711ec13e37fd3dcdb439733f0',), ('f4e43c2c37d5ea253750bd7208801da9',), ('a2d28ee211f090ef290fd96482c62fd7',), ('35e4b7a7d197680b21eaa83bcfee9baf',), ('fb6d3a34883f512955765f35252dba6a',), ('fa46d2c677e09372d682f4aefe8f86d6',), ('9f7f1e4a406bfecc295cbc37122ddbe9',), ('4ff40f809c7a104fe35b789d356dc288',), ('691f6ea3e27c3ea0564e78acef98372b',), ('240dae4b39b138171a756eb7ddd16a64',), ('4a9e71f85c6c800714c526cb745857ad',), ('f4e43c2c37d5ea253750bd7208801da9',), ('f1e93c166aa1f65ca7581b12b26950c9',), ('d2f2cd503e0b2ceae7b5c99dbf645de5',), ('775a721b9615d1b3462934d40faad00b',), ('66e666d9b06584e96ab2fed41d2977ce',), ('e4f77de23fb17bd3e90a6abd3958ad5c',), ('1001cab725260b069ae6e7b13c7440eb',), ('caad8d23ed79a83570fc1d12c3260ea4',), ('4a9e71f85c6c800714c526cb745857ad',), ('0a9cb3e3b7b699befb09706b61013069',), ('72646a363bfb323d60cc6d0791bdf86f',), ('059f8688edb6576d51cebcb0428ecbe8',), ('f41f010ed743f63b954eaca3718b485e',), ('81ede206906f4055d5b451b3d6fed89d',), ('9b37d4ca589fb38adc36ee839828f833',), ('7b927c4159604e71d1e3646d47c61b45',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('20d59404afc7a4b6ba67b6d0c0e8a524',), ('2d96b7931acffb2e569e83797504dcbc',), ('b10b0a5999ff735aa3667fa151d98f12',), ('a29315550f82279113a74a13cc3174a8',), ('74ec2afa685cc891327f5384dd3312d6',), ('1fba494ed13dbe4f16e3c5b168d5e226',), ('ec21a6d4637530aed29beba1af316418',), ('87bde67cc2ab2f4de3f5cf1d8804b526',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('e062b8ddf155395ec90eb37d45c8ea06',), ('4983cc2f53797a77e521a49e1c6456b5',), ('4dfed336f754f9fa83c75c8f674195ca',), ('61868f76f9f6b1224bc4b1afb3fab884',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('40e5937f36575e00de4ba38127e22f44',), ('20d59404afc7a4b6ba67b6d0c0e8a524',), ('b4e5a19885cfb38f708b693ef60ce01c',), ('0e592573d0866bbf9c11515a2a7733e2',), ('d7aa12e850bb7ce267ad0b26a5783736',), ('86a118a330c25ab67ece31d23a5d3640',), ('49fef32236b6f33a94e156d3cad59250',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('6a156f403f89c7d3edb8a6f1fc2c42bb',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('b84c9250fcc121c993720ec216bf85d7',), ('ac11c2859265306c7afcaf782cf08b51',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('0477bf9f38c7cd1ff84998d28a49f13c',), ('b84c9250fcc121c993720ec216bf85d7',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('a6c2f22ee53f3566647b89c0bb5db79e',), ('174840b18680426d4e9f5abb78b2b927',), ('174840b18680426d4e9f5abb78b2b927',), ('6c37c978db3ade5e055a3360038cf9b2',), ('4dfed336f754f9fa83c75c8f674195ca',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('1746ed3673229d5ddc874cfeefeee6cb',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('4c6be1d4f6b479e7788dd1197626e710',), ('580e3daac42f0859a7e008b4767b67aa',), ('5c98c985b5f74d841ba2db35bb1bf31d',), ('114fd0d9f75f70d3d79dc42b3069204f',), ('6aa7da2262a66b13358ca34665cf0b73',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('312eaadcaef609263a9f5f8f125dbb22',), ('3776823c8eac52217ef6a5e5a2390d83',), ('ccbb5006148c9220d280a7e4db5d2f8b',), ('81ede206906f4055d5b451b3d6fed89d',), ('15ed3b42d07496ff7efa2d623de4ea43',), ('4d66f4f4b0c1405fe80d744997a0974d',), ('db2dc30e08bcc02d0ec4eccf358fe31a',), ('41e841a24db47fdb75c24402c80b8754',), ('1001cab725260b069ae6e7b13c7440eb',), ('11c5a2dc8907cec79feccd6611d28310',), ('44599a206de859457d8edab0923a318e',), ('580e3daac42f0859a7e008b4767b67aa',), ('0bc8f3804104f666f2fee05f303b71cf',), ('462e7de711ec13e37fd3dcdb439733f0',), ('4441d85ed630c05c181ebdd055d2532d',), ('7acc9ffb339eba92231b6d8e363da053',), ('a6e64ca171352696a79bcefb85a9d475',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('639c0999f70d98813758b700e0c847d9',), ('fb6d3a34883f512955765f35252dba6a',), ('ed28a5d0145c685c119de3d0f5d30d14',), ('f4e43c2c37d5ea253750bd7208801da9',), ('00a5cc29496e6e33d88b93f2860ed409',), ('aa711676e7d7661e5550c17fe7e849f0',), ('589dffd7c2ab2fab447ef88fc1068a1c',), ('2580a4afa3b237891f347ff6e3d12f94',), ('84c0aca085f8b67059a1d4bbbf878a24',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('4a9e71f85c6c800714c526cb745857ad',), ('eb4fdec202c582c6d943e0c3deeb93ea',), ('05787cf4e84dd952aff93b489dfa4db6',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('0e2e476b6b8c536661c5e7381e162a4e',), ('76df634a6a478ab9b2f44a83ffed2d10',), ('eaadd6a6d72d49de05c37fdaf63a1eb4',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('20d59404afc7a4b6ba67b6d0c0e8a524',), ('c1700a17238319a6fe09a630201601b2',), ('1001cab725260b069ae6e7b13c7440eb',), ('da53acc80683eb8229758ccdbe0fcece',), ('1d678d2146c1ea772412ca4f289b89eb',), ('059f8688edb6576d51cebcb0428ecbe8',), ('cc8918f699b66ab4539f2ff611d5d880',), ('9cdeb88255a5f19f7f2b1b2da73398f7',), ('f64937ee53e2624ba36b40f7f22f2f55',), ('66e666d9b06584e96ab2fed41d2977ce',), ('b996b3f908447ad93d32c571186b2228',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('b84c9250fcc121c993720ec216bf85d7',), ('a50955480c8d9aa95254172c221f9a94',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('8bf0c81f2cc4edd8ce15da485c726e78',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('71d390acd5aeef2cf47c510351764b00',), ('3af34576b8a524dbd884c44fc26c0be3',), ('8f2220d9c05aab82b8225afec342f7e9',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('174840b18680426d4e9f5abb78b2b927',), ('41e841a24db47fdb75c24402c80b8754',), ('4dfed336f754f9fa83c75c8f674195ca',), ('385a6ea1707050b99a4d2afa37f2c929',), ('bf9360c68f4f55267965b7a87ccf5748',), ('392bffa29bf30b6412ca5424780d306f',), ('5566dae2420b4b3d629d6164f50f3906',), ('81ede206906f4055d5b451b3d6fed89d',), ('44599a206de859457d8edab0923a318e',), ('462e7de711ec13e37fd3dcdb439733f0',), ('95f557a0c98d2a869620897897b142ae',), ('580e3daac42f0859a7e008b4767b67aa',), ('1ebbff8bc9c85d57aac043175187a65d',), ('a54a46da65bd32a95aeee62d75888683',), ('d3f5b05cca19d768c908aa59598b27c7',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('7acc9ffb339eba92231b6d8e363da053',), ('ee7273cd78937af2fe7590616047476f',), ('d25c18e210c5bdf9f3ea8cf0814cf420',), ('66e666d9b06584e96ab2fed41d2977ce',), ('58532665d4710369d04858da60b01433',), ('4ba84021f34a73db98fba0407b31f0e3',), ('5659d1563c42e04a87dc91eba4edf6ca',), ('46cd999301b5bbeae094e16853341e10',), ('3be7e0286f263118048dfe95a5a4131e',), ('41e841a24db47fdb75c24402c80b8754',), ('a6e64ca171352696a79bcefb85a9d475',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('639c0999f70d98813758b700e0c847d9',), ('fb6d3a34883f512955765f35252dba6a',), ('f4e43c2c37d5ea253750bd7208801da9',), ('6484ce51f8bae0ed3ddafbdb0e520f24',), ('f648cc4a51fe0bf196778df4d12a1e25',), ('70cd0e3cfc64f5f5d040285d18839141',), ('92e177f94bf01304841e9a8bd3d6eec0',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('4a9e71f85c6c800714c526cb745857ad',), ('6e96f4041fb6fd485d648e6cdd682954',), ('bab8b2c0a8b3de876a6f0f2dba328298',), ('56df596d4e2c6edc809546d7de07d394',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('20d59404afc7a4b6ba67b6d0c0e8a524',), ('bee91639ba176b12b69e6937af688177',), ('cdb383bfe4aec564943128557e01da96',), ('6122bf315d9231ea8b3d3549260e2e57',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('6599a5a957abd324c181f29a6b700be9',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('b84c9250fcc121c993720ec216bf85d7',), ('9ce005860ebb177f7ecdc0262737a7af',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('4e3a8ba53973789d25d4f7c027f6da8b',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('174840b18680426d4e9f5abb78b2b927',), ('4dfed336f754f9fa83c75c8f674195ca',), ('3e7cf3a46f9062b99f3714c42f0e8f10',), ('ff0e93b4eef167702d82e94f63165d3d',), ('cbc6314f2ad54cb9d37a45d2542f3975',), ('859e5a98b98303f57f38186e84b70a88',), ('1001cab725260b069ae6e7b13c7440eb',), ('81ede206906f4055d5b451b3d6fed89d',), ('3a0805e99ecc6f5408c1fa62fd3d0ccf',), ('059f8688edb6576d51cebcb0428ecbe8',), ('d46271f99bbea2c3381ed6ec8dc274d7',), ('150a7d009b576f87e17354783aed916a',), ('f02f75678045a61f3c1201ada7c5939e',), ('1001cab725260b069ae6e7b13c7440eb',), ('6f64f99224ca9e30456a16d1386f3f1d',), ('f6dc06eba32d0a48307770f04a6eb87d',), ('059f8688edb6576d51cebcb0428ecbe8',), ('74353a264c76a1f714eb0d50e1b20bce',), ('580e3daac42f0859a7e008b4767b67aa',), ('f89be3b3f60a916a92143a43fa5cbf81',), ('662f5d13458b9e79c71181d0b7a6a4eb',), ('33db5b4fd701623ea9eada0474a411ed',), ('86fa2a28202059513c85d3a835e7b14e',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('3d4cd2a4f74ac1a8fef487beb8f5592b',), ('95e56824e6a7692c5b9a0a377606060f',), ('66e666d9b06584e96ab2fed41d2977ce',), ('8d1e5484f953d76dbb6c2603aead1bcc',), ('a078adda824e92ceabc3cc4d09c41c57',), ('890c55a1129e05fe98cfd267cfb3a909',), ('41e841a24db47fdb75c24402c80b8754',), ('44599a206de859457d8edab0923a318e',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('462e7de711ec13e37fd3dcdb439733f0',), ('bf9eac19f8593f8972ff7db5b3f152ab',), ('7acc9ffb339eba92231b6d8e363da053',), ('551af053392d9106a44c450a83c5c191',), ('a6e64ca171352696a79bcefb85a9d475',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('d0dc6be95c7cd0bae8f6dffc3ae5e478',), ('639c0999f70d98813758b700e0c847d9',), ('fb6d3a34883f512955765f35252dba6a',), ('e34fb602eead1015f63fdfe87d06e9f2',), ('f4e43c2c37d5ea253750bd7208801da9',), ('4a9e71f85c6c800714c526cb745857ad',), ('ffd197806760aa5542414a7256434a27',), ('37ecc74d5dd3b5f7c0b4963f2e19adc8',), ('462e7de711ec13e37fd3dcdb439733f0',), ('06286583174c1208fba1ac9a2d0da6c8',), ('44599a206de859457d8edab0923a318e',), ('7acc9ffb339eba92231b6d8e363da053',), ('7bd9a40477703a7b76a98abd58b26284',), ('729e4a78918c2a14117449c254ef9ade',), ('7c686bc1c4fca9c094dacaf3641ea734',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('0b0be5f61284b2f3a5c936e6a9c345d8',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('20d59404afc7a4b6ba67b6d0c0e8a524',), ('9dfd7e68e0be18c5e494f884f5b62c20',), ('4dfed336f754f9fa83c75c8f674195ca',), ('174840b18680426d4e9f5abb78b2b927',), ('02ad537d614cfbff07610b2896886ba3',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('0132098c82e62489e303368e35fb2338',), ('31f854d3225d2f8a50f19fe580515125',), ('90b8ad7dc16a731ae5a859c592720d11',), ('8f39ec35d8c1babff3a2c88623a357dc',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('7cfada02406bb3cb4c8a18e57b599d19',), ('b84c9250fcc121c993720ec216bf85d7',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('9d401eb7bc4657fadab7526b49b0cdf2',), ('c2f3746af5c45aae4f787595331f893f',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('639c0999f70d98813758b700e0c847d9',), ('707b4b03a37cc9ba69f645e3def751d5',), ('a6e64ca171352696a79bcefb85a9d475',), ('f0cd56954e30a9eaf7f09fc1b9731507',), ('81ede206906f4055d5b451b3d6fed89d',), ('fb6d3a34883f512955765f35252dba6a',), ('f4e43c2c37d5ea253750bd7208801da9',), ('49730991bd1cde405a6fcbf0dfe59a97',), ('9e6a22cd7adf5e80d3ea099e3aecbbb6',), ('4a03e1ffde58194676ebe3d01ed3cf58',), ('bfb527a3866aee738db0996cb19097e8',), ('4a9e71f85c6c800714c526cb745857ad',), ('0facd929e822271e9a2e8c272b3ed543',), ('580e3daac42f0859a7e008b4767b67aa',), ('d1790c5cb7c858f6323095ca8b75e704',), ('d9947426f7f3942d51b56eb5db8df995',), ('7e6b99d676a3ddaec16de6a72189678a',), ('487459f2a4bd19419bb91f7eeb1d1423',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('20d59404afc7a4b6ba67b6d0c0e8a524',), ('c4dc3882768b5fa54b1f9d287e48829f',), ('4dfed336f754f9fa83c75c8f674195ca',), ('174840b18680426d4e9f5abb78b2b927',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('83cefd5023fd0829c6abeaf55c944ccb',), ('6e1b2419b5e500d7f23375203379db82',), ('a8a8ca075443cbc50e5ccd2a3428aa14',), ('66e666d9b06584e96ab2fed41d2977ce',), ('a8304535f872100ef9d2dc56452e8150',), ('272f7d4c5c5ad2175bf5ca70964fb776',), ('fc56b91b3900c6130e8ef7a8f9039b7f',), ('e7803c0edb77c556b5a92d2e181db428',), ('67f18772405d09915c0a2fe5d79aac51',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('c0327a5d7761ec148d041fc2783fa135',), ('5c3c82a16139a291596270e6d77da58a',), ('b84c9250fcc121c993720ec216bf85d7',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('cdb3d16b29a46a2cbee42a3d8d645432',), ('f1f8dfe306e032ec195795875e4afee3',), ('c774e13523316c3e70f54379313fea38',), ('8e92646e94983f843c38614e440d9693',), ('41e841a24db47fdb75c24402c80b8754',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('b74f7850074961570ce1eb4729a6bed9',), ('44599a206de859457d8edab0923a318e',), ('462e7de711ec13e37fd3dcdb439733f0',), ('2c545a10c7dfdba5d79e6486d45a5a27',), ('7acc9ffb339eba92231b6d8e363da053',), ('348e8c82941d96c8d98247b87303db06',), ('13675ed410af6137bf1489a1efa6852f',), ('81ede206906f4055d5b451b3d6fed89d',), ('4099f9e6d4fb3b7486da9dbc55683ab1',), ('fb6d3a34883f512955765f35252dba6a',), ('f4e43c2c37d5ea253750bd7208801da9',), ('580e3daac42f0859a7e008b4767b67aa',), ('d2a81e484fcb351089cf14d4b524a964',), ('4ca241bf44554feacf6f5fd0b0ee83da',), ('8a48917fcedaf593ea27f3d8ba5e3f03',), ('66e666d9b06584e96ab2fed41d2977ce',), ('dced84beefa220002a06040ea23faa83',), ('1d45b8ddfa4ee0f832e4271999f4d4bb',), ('6a35f0bb00ca27f53a8b7088ce03c956',), ('09aca9a64a6f0ff077c5121ef23668d8',), ('5d38e23ac7902ac8030a7201036005bd',), ('41e841a24db47fdb75c24402c80b8754',), ('44599a206de859457d8edab0923a318e',), ('462e7de711ec13e37fd3dcdb439733f0',), ('2c545a10c7dfdba5d79e6486d45a5a27',), ('7acc9ffb339eba92231b6d8e363da053',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('a6e64ca171352696a79bcefb85a9d475',), ('a3a19d679f3a4cf448bfae97a6ad9fff',), ('a3a19d679f3a4cf448bfae97a6ad9fff',), ('a6e64ca171352696a79bcefb85a9d475',), ('1f46248de3b26e119fafaeabc39f3b9b',), ('639c0999f70d98813758b700e0c847d9',), ('639c0999f70d98813758b700e0c847d9',), ('328faca64748cece35d83960cd2e7c51',), ('fb6d3a34883f512955765f35252dba6a',), ('f53e5ef664035deab0262e21f60b8c4a',), ('a1ccf4fb29b56ccb302ec3e82f64ed66',), ('90453c9a5d8b4e6f53596fe6cbdff59c',), ('4a9e71f85c6c800714c526cb745857ad',), ('9f2944872b5df15bdf6e23bbfeb7de1d',), ('f53e5ef664035deab0262e21f60b8c4a',), ('90453c9a5d8b4e6f53596fe6cbdff59c',), ('9f2944872b5df15bdf6e23bbfeb7de1d',), ('a1ccf4fb29b56ccb302ec3e82f64ed66',), ('4a9e71f85c6c800714c526cb745857ad',), ('328faca64748cece35d83960cd2e7c51',), ('cbb92c7433c76f54280b483e7005668d',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('b7e3406f7fce6116fe8f4d7e792524ae',), ('cbb92c7433c76f54280b483e7005668d',), ('7cfd8d5a7336474b0b25d2844a6ac2a9',), ('b7e3406f7fce6116fe8f4d7e792524ae',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('8e67ca712ce0fe284fb71ef86a8d4128',), ('b7fb4966f92f2b6812fbc9ad95d907a0',), ('1767662080ada0d0051add0bbc148d8c',), ('20d59404afc7a4b6ba67b6d0c0e8a524',), ('8e67ca712ce0fe284fb71ef86a8d4128',), ('9d6e4b409d9c7ff3e63bc66f65634657',), ('1767662080ada0d0051add0bbc148d8c',), ('9d6e4b409d9c7ff3e63bc66f65634657',), ('b30b0ce954475beb44631b0b9f644780',), ('5d2e0f3af23094b1d83033a6c7369428',), ('de40ab05a1e621ade85d018bb5c2ffa9',), ('1001cab725260b069ae6e7b13c7440eb',), ('c905f45d23c5e0f5754e25a7a832d8c6',), ('059f8688edb6576d51cebcb0428ecbe8',), ('3e01b17f12cd08c96c520803b213e75d',), ('b30b0ce954475beb44631b0b9f644780',), ('5d2e0f3af23094b1d83033a6c7369428',), ('c905f45d23c5e0f5754e25a7a832d8c6',), ('1001cab725260b069ae6e7b13c7440eb',), ('3e01b17f12cd08c96c520803b213e75d',), ('059f8688edb6576d51cebcb0428ecbe8',), ('de40ab05a1e621ade85d018bb5c2ffa9',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('a13190742ec8c48867f9842e4493ecfb',), ('b84c9250fcc121c993720ec216bf85d7',), ('a0fd224089ef8722fd3e85967e70dc9b',), ('a13190742ec8c48867f9842e4493ecfb',), ('b84c9250fcc121c993720ec216bf85d7',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('31c097b294e07c6d246ccd83c99f83d8',), ('b2d6e9d0e5a6f85e30900178d4e53150',), ('f30de009dc564b5f7faae37f1fe25cf7',), ('31c097b294e07c6d246ccd83c99f83d8',), ('92d00be15dec9b5e49cf09df8970adb2',), ('580e3daac42f0859a7e008b4767b67aa',), ('92d00be15dec9b5e49cf09df8970adb2',), ('580e3daac42f0859a7e008b4767b67aa',), ('174840b18680426d4e9f5abb78b2b927',), ('4dfed336f754f9fa83c75c8f674195ca',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('85303a9313de49e85ca1b7fe6df4b2a5',), ('22610efed1348c52ccb7d49b564a2b6b',), ('cef820ee7dbf3c598794993c4dcd4970',), ('81ede206906f4055d5b451b3d6fed89d',), ('174840b18680426d4e9f5abb78b2b927',), ('4dfed336f754f9fa83c75c8f674195ca',), ('85303a9313de49e85ca1b7fe6df4b2a5',), ('46b5f6f8b2e4750aa51a321bd7ddc3a8',), ('cef820ee7dbf3c598794993c4dcd4970',), ('81ede206906f4055d5b451b3d6fed89d',), ('6eaec816a08e8a0bee466add08d35edf',), ('e709b0e586b51d5cbd91da8d4e713f16',), ('e3185f36f2d54b65c1b7928f9a32f522',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('3f3d4381ce08ac2a444b24255c7904d2',), ('6eaec816a08e8a0bee466add08d35edf',), ('3f3d4381ce08ac2a444b24255c7904d2',), ('e3185f36f2d54b65c1b7928f9a32f522',), ('a1dc2b79b9c89805dca37c8a52f18bd6',), ('e709b0e586b51d5cbd91da8d4e713f16',), ('102e00f7013c14287ca80c4a81bfbce1',), ('66e666d9b06584e96ab2fed41d2977ce',), ('b5c71a0dbd63a2c4e0bfa7c27a3f5a2b',), ('9c719117620b81d047213746833260e8',), ('102e00f7013c14287ca80c4a81bfbce1',), ('66e666d9b06584e96ab2fed41d2977ce',), ('b5c71a0dbd63a2c4e0bfa7c27a3f5a2b',), ('9c719117620b81d047213746833260e8',), ('f618cae361d2b17e44ea05900b425aae',), ('15b534aa4474214c83cd4f6e1097e83b',), ('0a8f83f16a1601889cd69a28d7459285',), ('41e841a24db47fdb75c24402c80b8754',), ('f618cae361d2b17e44ea05900b425aae',), ('15b534aa4474214c83cd4f6e1097e83b',), ('41e841a24db47fdb75c24402c80b8754',), ('0a8f83f16a1601889cd69a28d7459285',)]
#     print len(after)
#     for i in after:
#         if i in before:
#             after.remove(i)
#     
#     
#     print after
#     print len(after)
#     after = 
#     relativepath_list = []
#     sql_packages_l1 = 'select filelist from l10n_packages where generatetime=(select max(generatetime) from l10n_packages)'
#     sql_packages_l2 = 'select filelist from (select * from l10n_packages order by generatetime desc limit 2) as middle order by generatetime limit 1'
#     a = operate_postgre(sql_packages_l1)
#     print a
#     list_result_a = list_trans(a, 0, 0)
#     print 'The last file list is : ', list_result_a
#     b = operate_postgre(sql_packages_l2)   
#     list_result_b = list_trans(b, 0, 0)
#     print 'The last but one file list is : ', list_result_b  
#     
#     listResult = sqlResult_compare(list_result_a, list_result_b)
#     print 'The compare result is..', listResult
#     if listResult:
#         for i in listResult:
#             i = int(i)
#             relativepath = operate_postgre('select relativepath from l10n_files where fileid=%d'%i)
# #             print relativepath
#             relativepath = relativepath[0][0]
#             relativepath_list.append(relativepath)
#             continue
# #         print relativepath_list
#         for i in relativepath_list:
#             temp = []
#             catch_globalid = operate_postgre("select globalid from l10n_globalkeys where relativepath='%s'"%i)
#             print 'globalid for file %s'%i,catch_globalid
#             for i in catch_globalid:
#                 temp.append(i[0])
#                 continue
#             catch_globalid = temp
#           
        
    
        
      
            
            
    
    
# class Dbconn(object):
#     '''
#     This class is for the database connection
#     '''
#     
# 
# 
#     def __init__(self, params):
#         '''
#         Constructor
#         '''
# main()
# verify_md5()
if __name__=="__main__":
    sql = "select nodes from l10n_files where relativepath = 'components/composition/ui/src/main/sencha/locale/en/customform.js'"
    data = operate_postgre(sql)
    print data