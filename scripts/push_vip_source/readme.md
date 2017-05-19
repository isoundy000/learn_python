yum install gcc  
yum -y install gcc-c++  
yum install -y perl-Module-Install.noarch  
yum install -y net-tools

一、下载sshpass
    地址：http://sourceforge.net/projects/sshpass/
    下载最新版，此外使用sshpass-1.05.tar.gz。

二、安装
    tar zxvf sshpass-1.05.tar.gz
    cd sshpass-1.05
    make 
    make install

三、使用
    参考man或安装文件包中的INSTALL。

yum install git
ssh-copy-id -i ~/.ssh/id_rsa.pub root@远程服务器的ip/主机名/域名