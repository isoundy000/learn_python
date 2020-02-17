#!/usr/bin/env python
# -*- coding:utf-8 -*-



# python2如何使用M2Crypto对接口请求的数据加密，对接口请求的数据解密
# RSA加密算法是一种强大的公钥加密算法,安全性很高,这里我们来看一下Python使用Pycrypto库进行RSA加密的方法详解
#
# Python密码库--Pycrypto
# Python良好的生态，对于加密解密技术都有成熟的第三方库。大名鼎鼎的M2Crypto和Pycrypto，前者非常容易使用，可是安装却非常头疼，不同的系统依赖软件的版本还有影响。后者则比较方面，直接使用pip安装即可。
#
# 安装  （切记只可在mac系统或者linux系统上安装，win系统不支持该库）
#
# pip install pycrypto
#
# 安装成功后：pip list


# 测试环境以上参数分别为渠道Id：000****，apiKey：0000****, 公匙：
# FwwDQY************JAAQ==  
#   
#
# 所有接口需要在请求头中添加sign头信息，以验证此次请求的身份，sign的制作规则如下 ： 
#
# 1、请求的所有非空参数按照自然序排序后以key=value的形式&连接，如：String sign = key1=value1&key2=value2&key3=value3。
#
# 2、将1中得到的字符串最后拼接上apiKey，如：sign = sign + "&apiKey=" + apiKey(申请得到)。
#
# 3、将2中得到的sign值用RSA算法的公匙加密进行加密，将得到的加密字符作为sign头信息的value值，加密注意事项见下一条。
#
# RSA加密注意事项：
#
# 1、加解密方式按照RSA非对称算法进行。加解密用的byte[]应该用java.util.Base64进行运算，加密时将加密得到的byte[]进行
#   Base64.getEncoder().encodeToString后得到密文；解密时将要解密的密文Base64.getDecoder().decode后得到的byte[]进行解密。  
# 2、加解密的方式采用分段加解密，一次编码的方式。
#      接口返回数据已用RSA私匙加密以保证数据的安全，如果渠道Id不符合或者sign头信息没有，默认不是我们的用户，会返回明       文的错误信息，其他情况错误情况返回的也是密文。
#
# 接口的统一域名为：待定。
#
# 返回状态码：200正常，500系统错误，其他均为业务异常流程。
#
# 下面就是我对接口请求的数据进行加密和对接口返回的数据进行解密：（敏感数据已经用****代替）
# encoding=utf-8
import requests
import json
import RSA


class game_api(object):
    def __init__(self, userid, channel, is_apikey=True):
        self.uapi = "http://172.17.2.***:***"
        self.userid = userid
        self.channelId = channel
        if is_apikey:
            self.mining_rocketapiKey = 'A4H1DE239DGE5C***********'  # 这是apikey值
        else:
            self.mining_rocketapiKey = '690KKDD11L585A3************'

    def getuser_currency(self, currency):  # 1、通过userHashId获取用户币种账户信息
        # self.currency = currency
        b = "channelId=" + self.channelId + "&currencySymbol=" + currency + "&from=COGAME&userHashId=" + self.userid
        # b= "channelId=" + self.channelId + "&currencySymbol=%s&from=COINGAME&userHashId="%(currency) + self.userid
        bb = b + "&apiKey=" + self.mining_rocketapiKey
        #   实例化对象
        a = RSA
        s = a.rsa_encrypt(bb)
        header = {'Content-Type': 'application/x-w*********',
                  'sign': s,
                  'origin': 'http://*************.com'}

        url = self.uapi + "/third-api/***/user**/balance?" + b
        r = requests.get(url, headers=header)
        result = r.text
        # print(result)
        data_result = a.rsa_decrypt(result)
        print data_result


if __name__ == '__main__':
    a = game_api('U-V**888', '09005', is_apikey=False)  #
    a.getuser_currency('ETC')



# 下面的代码就是加密和解密的代码了：（敏感数据已经用****代替）
# encoding:utf-8
from M2Crypto import BIO, RSA
import base64


def rsa_encrypt(content):
    mining_publickey = "MCccDQY***JKoZIhvc******************************************=="
    rocket_publickey = "MCccDQYJKoZ***cNAQEBB***********TQzYCp**********************=="
    text = content.encode('utf-8')  # 明文
    pub_bio = BIO.MemoryBuffer(
        '-----BEGIN PUBLIC KEY-----\n%s\n-----END PUBLIC KEY-----'.encode('utf-8') % (rocket_publickey))  # 公钥字符串
    pub_rsa = RSA.load_pub_key_bio(pub_bio)  # 加载公钥
    default_size = 53
    len_content = len(text)
    # print len_content
    if len_content < default_size:
        secret = pub_rsa.public_encrypt(text, RSA.pkcs1_padding)  # 公钥加密
        sign = base64.b64encode(secret)  # 密文base64编码
        return sign
    offset = 0
    params_list = []
    while len_content - offset > 0:
        if len_content - offset > default_size:
            params_list.append(pub_rsa.public_encrypt(text[offset:offset + default_size], RSA.pkcs1_padding))
        else:
            params_list.append(pub_rsa.public_encrypt(text[offset:], RSA.pkcs1_padding))
        offset += default_size
    target = ''.join(params_list)
    # print(base64.b64encode(target))
    return base64.b64encode(target)


def rsa_decrypt(content):
    mining_publickey = "MCccDQY***JKoZIhvc******************************************=="
    newkey = "MCccDQYJKoZ***cNAQEBB***********TQzYCp********************************=="

    text = base64.b64decode(content)
    print(type(text))
    pub_bio = BIO.MemoryBuffer(
        '-----BEGIN PUBLIC KEY-----\n%s\n-----END PUBLIC KEY-----'.encode('utf-8') % (newkey))  # 公钥字符串
    pub_rsa = RSA.load_pub_key_bio(pub_bio)  # 加载公钥
    default_size = 64
    len_content = len(text)
    print len_content
    if len_content < default_size:
        secret = pub_rsa.public_decrypt(text, RSA.pkcs1_padding)  # 公钥加密
        sign = base64.b64encode(secret)  # 密文base64编码
        return sign
    offset = 0
    params_list = []
    while len_content - offset > 0:
        if len_content - offset > default_size:
            params_list.append(pub_rsa.public_decrypt(text[offset:offset + default_size], RSA.pkcs1_padding))
        else:
            params_list.append(pub_rsa.public_decrypt(text[offset:], RSA.pkcs1_padding))
        offset += default_size
    target = ''.join(params_list)
    return target