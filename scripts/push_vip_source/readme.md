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


===============================================================================================================
push bundle of environment

push source
1 centos7需要安装图形化界面，因为需要用bcompare，
第一种形式是在收集的机器上，直接安装图形化界面     1 GUI
第二种是单独一台管理机器，在其上安装图形化界面
安装命令如下
              在命令行下 输入下面的命令来安装Gnome包。
    yum groupinstall "GNOME Desktop" "Graphical Administration Tools"
              更新系统的运行级别。
    ln -sf /lib/systemd/system/runlevel5.target /etc/systemd/system/default.target
             重启机器。启动默认进入图形界面。
    reboot
2 bcompare的安装
    wget http://www.scootersoftware.com/bcompare-4.2.2.22384.x86_64.rpm
    su
    rpm --import http://www.scootersoftware.com/RPM-GPG-KEY-scootersoftware
    yum install bcompare-4.2.2.22384.x86_64.rpm
3 讲讲具体的脚本