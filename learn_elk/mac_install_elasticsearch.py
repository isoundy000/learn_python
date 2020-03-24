#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 在Mac平台上安装配置ELK时的一些总结
# MAC安装ELK
# 首先是安装elasticsearch，这个很简单：
# brew install elasticsearch
# 但是这里就遇到了问题，我的java是1.6的，而elasticsearch需要1.7以下版本，所以还需要安装java 1.7而要安装java 1.7，用简单的brew又不行，
# 还需要先安装cask，所以最后的步骤就变成了这样：
#
# brew install brew-cask
# brew update
# brew cask install caskroom/versions/java7
# java -version
#
# 可以看到java版本已经是1.7了。接下来：
#
# brew install elasticsearch
# elasticsearch --version
#
# 证明elasticsearch已经安装好了。以后要启动或者停止elasticsearch服务就执行以下命令：
#
# brew services start elasticsearch
# brew services stop elasticsearch
#
# 下面安装logstash:
#
# brew install logstash
# logstash --version
#
# logstash已经安装好了。然后安装kibana，kibana的安装不用brew，直接下载解压之后，进到解压目录里：
#
# ./kibana
#
# 接下来是配置logstash，在这里我遇到了大麻烦。从头说起，先要建立一个logstash的conf文件，以便于后期调试：
#
# mkdir logstash
# cd logstash
#
# 生成一个logstash.conf文件，在这里我们准备处理apache的log
#
# input {
#     file {
#         path => "/private/var/log/apache2/www.myserver.com-access_log"
#         start_position => beginning
#         ignore_older => 0
#         sincedb_path => "/dev/null"
#     }
# }
# filter {
#     grok {
#         match => { "message" => "%{IPORHOST:clientip} - %{USER:auth} \[%{HTTPDATE:timestamp}\] \"(?:%{WORD:verb} %{NOTSPACE:request}(?: HTTP/%{NUMBER:httpversion})?|%{DATA:rawrequest})\" %{NUMBER:response} (?:%{NUMBER:bytes}|-)"}
#     }
#     date {
#         match => [ "timestamp" , "dd/MMM/YYYY:HH:mm:ss +0800" ]
#     }
# }
# output {
#     elasticsearch {}
#     stdout {}
# }
#
# 为了这个配置文件，费了很大精力，网上很多教程都和我的实际情况不相符合。关键点说明如下：
# start_position => beginning告诉logstash从我的log文件的头部开始往下找，不要从半中间开始。
# ignore_older => 0告诉logstash不要管我的log有多古老，一律处理，否则logstash缺省会从今天开始，就不管老日志了。
# sincedb_path => "/dev/null"这句话也很关键，特别是当你需要反复调试的时候，因为logstash会记住它上次处理到哪儿了，如果没有这句话的话，
# 你再想处理同一个log文件就麻烦了，logstash会拒绝处理。现在有了这句话，就是强迫logstash忘记它上次处理的结果，从头再开始处理一遍。
# filter下面的grok里面的match，网上教程一般是这么写的：
#
# match => { "message" => "%{COMBINEDAPACHELOG}" }
#
# 但是当我这么写的时候，总是处理不了我的log，我的log其实就长这个样子：
#
# 127.0.0.1 - - [02/May/2016:22:11:28 +0800] "GET /assets/aa927304/css/font-awesome.min.css HTTP/1.1" 200 27466
#
# 查源代码，官方是这么写的：
#
# COMMONAPACHELOG %{IPORHOST:clientip} %{USER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] "(?:%{WORD:verb} %{NOTSPACE:request}(?: HTTP/%{NUMBER:httpversion})?|%{DATA:rawrequest})" %{NUMBER:response} (?:%{NUMBER:bytes}|-)
# COMBINEDAPACHELOG %{COMMONAPACHELOG} %{QS:referrer} %{QS:agent}
#
# 后面的combined引用前面的common，而问题就出在这个USER:ident上。
# 我在https://grokdebug.herokuapp.com/反复验证，最后发现只要把这个USER:ident改成-就行了，所以就有了我上面的写法。
# 接下来用了一个date filter，这是因为如果不用这个date filter的话，它会把处理log的时间认为是用户访问网页的时间来产生表格，
# 这样在kibana里看上去怪怪的，所以加这么一个filter，但就是加这么一个简单的filter，也出现了问题，处理失败，因为网上的教程里一般都是这么写的：
#
# date {
#     match => [ "timestamp" , "dd/MMM/YYYY:HH:mm:ss Z" ]
# }
#
# 区别就在最后一个Z上，我的时区字符串是+0800，怎么也匹配不上这个Z，索性一怒之下直接用+0800代替，也就过关了。
# 过程中不停地访问如下网址验证elasticsearch的结果：
# http://localhost:9200/logstas...
# 注意URL中那个时间，一开始的时候我们就用处理日志的时间访问就可以，但当加上date filter后就不一样了，如果你还用当前日期的话，会一无所得，改成log里的时间才会看到结果，因为index日期变了。
# 然后就是你需要一遍一遍地清空elasticsearch里的数据，进行调试：
#
# curl -XDELETE 'http://localhost:9200/_all'
#
# 清空完了以后你再执行logstash，就把新数据又灌进去了：
#
# logstash agent -f ~/logstash/logstash.conf
#
# 最后，通过kibana窗口观察你的结果：
# http://localhost:5601
# 一开始是在setting页面，要你指定访问的index，这里就用缺省的logstash-*就行了，然后就是页面右上角有个时间限制，把它改成Year to date，否则有可能什么数据也看不到。