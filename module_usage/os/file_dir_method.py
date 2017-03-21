# -*- encoding: utf-8 -*-
'''
Created on 2017年3月20日

@author: houguangdong
'''
import os, sys, stat

# 8 os.closerange(fd_low, fd_high)
# 关闭所有文件描述符，从 fd_low (包含) 到 fd_high (不包含), 错误会忽略
# os.closerange() 方法用于关闭所有文件描述符 fd，从 fd_low (包含) 到 fd_high (不包含), 错误会忽略。
# 该方法类似于：
# for fd in xrange(fd_low, fd_high):
#     try:
#         os.close(fd)
#     except OSError:
#         pass
# 打开文件
fd = os.open("foo.txt", os.O_RDWR|os.O_CREAT)
# 写入字符串
os.write(fd, "This is test")
# 关闭文件
os.closerange(fd, fd)

# 9 os.dup(fd) # os.dup() 方法用于复制文件描述符 fd。
# 复制文件描述符 fd
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 复制文件描述符
d_fd = os.dup( fd )
# 使用复制的文件描述符写入文件
os.write(d_fd, "This is test")
# 关闭文件
os.closerange( fd, d_fd)

# 10 os.dup2(fd, fd2) # os.dup2() 方法用于将一个文件描述符 fd 复制到另一个 fd2。Unix, Windows 上可用。
# 将一个文件描述符 fd 复制到另一个 fd2
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 写入字符串
os.write(fd, "This is test")
# 文件描述符为 1000
fd2 = 1000
os.dup2(fd, fd2);
# 在新的文件描述符上插入数据
os.lseek(fd2, 0, 0)
str = os.read(fd2, 100)
print "读取的字符串是 : ", str
# 关闭文件
os.close( fd )

# 11 os.fchdir(fd) # os.fchdir() 方法通过文件描述符改变当前工作目录。Unix, Windows 上可用。
# 通过文件描述符改变当前工作目录
# 首先到目录 "/var/www/html" 
os.chdir("/var/www/html" )
# 输出当前目录
print "当前工作目录为 : %s" % os.getcwd()
# 打开新目录 "/tmp"
fd = os.open( "/tmp", os.O_RDONLY )
# 使用 os.fchdir() 方法修改到新目录
os.fchdir(fd)
# 输出当前目录
print "当前工作目录为 : %s" % os.getcwd()
# 关闭打开的目录
os.close( fd )

# 12 os.fchmod(fd, mode)
# 改变一个文件的访问权限，该文件由参数fd指定，参数mode是Unix下的文件访问权限。Unix上可用。
# 打开文件 "/tmp/foo.txt"
fd = os.open( "/tmp", os.O_RDONLY )
# 设置文件可通过组执行
os.fchmod( fd, stat.S_IXGRP)
# 设置文件可被其他用户写入
os.fchmod(fd, stat.S_IWOTH)
print "修改权限成功!!"
# 关闭文件
os.close( fd )

# 13 os.fchown(fd, uid, gid)
# 修改一个文件的所有权，这个函数修改一个文件的用户ID和用户组ID，该文件由文件描述符fd指定。Unix上可用。
# 打开文件 "/tmp/foo.txt"
fd = os.open( "/tmp", os.O_RDONLY )
# 设置文件的用户 id 为 100
os.fchown( fd, 100, -1)
# 设置文件的用户组 id 为 100
os.fchown( fd, -1, 50)
print "修改权限成功!!"
# 关闭文件
os.close( fd )

# 14 os.fdatasync(fd)
# 强制将文件写入磁盘，该文件由文件描述符fd指定，但是不强制更新文件的状态信息。如果你需要刷新缓冲区可以使用该方法。Unix上可用。
# 打开文件 "/tmp/foo.txt"
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 写入字符串
os.write(fd, "This is test")
# 使用 fdatasync() 方法
# os.fdatasync(fd)
# 读取文件
os.lseek(fd, 0, 0)
str = os.read(fd, 100)
print "读取的字符是 : ", str
# 关闭文件
os.close( fd )

# 15 os.fdopen(fd[, mode[, bufsize]])
# 通过文件描述符 fd 创建一个文件对象，并返回这个文件对象
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 获取以上文件的对象
fo = os.fdopen(fd, "w+")
# 获取当前文章
print "Current I/O pointer position :%d" % fo.tell()
# 写入字符串
fo.write( "Python is a great language.\nYeah its great!!\n");
# 读取内容
os.lseek(fd, 0, 0)
str = os.read(fd, 100)
print "Read String is : ", str
# 获取当前位置
print "Current I/O pointer position :%d" % fo.tell()
# 关闭文件
os.close(fd)

# 16 os.fpathconf(fd, name)
# 返回一个打开的文件的系统配置信息。name为检索的系统配置的值，它也许是一个定义系统值的字符串，这些名字在很多标准中指定（POSIX.1, Unix 95, Unix 98, 和其它）。
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
print "%s" % os.pathconf_names
# 获取最大文件连接数
no = os.fpathconf(fd, 'PC_LINK_MAX')
print "文件最大连接数为 :%d" % no
# 获取文件名最大长度
no = os.fpathconf(fd, 'PC_NAME_MAX')
print "文件名最大长度为 :%d" % no
# 关闭文件
os.close(fd)

# 17 os.fstat(fd)
# 返回文件描述符fd的状态，像stat()。
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 获取元组
info = os.fstat(fd)
print "文件信息 :", info
# 获取文件 uid
print "文件 UID :%d" % info.st_uid
# 获取文件 gid
print "文件 GID  :%d" % info.st_gid
# 关闭文件
os.close(fd)

# 18 os.fstatvfs(fd)
# 返回包含文件描述符fd的文件的文件系统的信息，像 statvfs()
