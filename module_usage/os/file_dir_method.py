# -*- encoding: utf-8 -*-
'''
Created on 2017年3月20日

@author: houguangdong
'''

import os, sys, stat


# Python OS 文件/目录方法
# os 模块提供了非常丰富的方法用来处理文件和目录。常用的方法如下表所示：

# 1 os.access(path, mode) # 方法使用当前的uid/gid尝试访问路径。大部分操作使用有效的 uid/gid, 因此运行环境可以在 suid/sgid 环境尝试。
# 检验权限模式 
# 以下实例演示了 access() 方法的使用：
# 假定 /tmp/foo.txt 文件存在，并有读写权限
# os.F_OK: 作为access()的mode参数，测试path是否存在。
ret = os.access("/tmp/foo.txt", os.F_OK)
print "F_OK - 返回值 %s"% ret
# os.R_OK: 包含在access()的mode参数中 ， 测试path是否可读。 
ret = os.access("/tmp/foo.txt", os.R_OK)
print "R_OK - 返回值 %s"% ret
# os.W_OK 包含在access()的mode参数中 ， 测试path是否可写。
ret = os.access("/tmp/foo.txt", os.W_OK)
print "W_OK - 返回值 %s"% ret
# os.X_OK 包含在access()的mode参数中 ，测试path是否可执行。
ret = os.access("/tmp/foo.txt", os.X_OK)
print "X_OK - 返回值 %s"% ret

# 2 os.chdir(path)  方法用于改变当前工作目录到指定的路径。
# 改变当前工作目录
path = "C:\\Users\\ghou.VMWAREM\\workspace\\network_data_collection"
# 查看当前工作目录
retval = os.getcwd()
print "当前工作目录为 %s" % retval
# 修改当前工作目录
os.chdir(path)
# 查看修改后的工作目录
retval = os.getcwd()
print "目录修改成功 %s" % retval

# 3 os.chflags(path, flags)　# 方法用于设置路径的标记为数字标记。多个标记可以使用 OR 来组合起来。 只支持在 Unix 下使用。
# 设置路径的标记为数字标记。
path = "/tmp/foo.txt"
# 为文件设置标记，使得它不能被重命名和删除
# flags = stat.SF_NOUNLINK
# retval = os.chflags( path, flags)
# print "返回值: %s" % retval

# 4 os.chmod(path, mode)　 # 方法用于更改文件或目录的权限。
# 更改权限 
# 假定 /tmp/foo.txt 文件存在，设置文件可以通过用户组执行
os.chmod("/tmp/foo.txt", stat.S_IXGRP)
# 设置文件可以被其他用户写入
os.chmod("/tmp/foo.txt", stat.S_IWOTH)

# 5 os.chown(path, uid, gid) #　os.chown() 方法用于更改文件所有者，如果不修改可以设置为 -1, 你需要超级用户权限来执行权限修改操作。只支持在 Unix 下使用。
# 更改文件所有者
# 假定 /tmp/foo.txt 文件存在.
# 设置所有者 ID 为 100 
# os.chown("/tmp/foo.txt", 100, -1)

# 6 os.chroot(path) # 方法用于更改当前进程的根目录为指定的目录，使用该函数需要管理员权限。
# 改变当前进程的根目录 
# 设置根目录为 /tmp
# os.chroot("/tmp")

# 7 os.close(fd) # 方法用于关闭指定的文件描述符 fd。
# 关闭文件描述符 fd
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
#  写入字符串
os.write(fd, "This is test")
# 关闭文件
os.close( fd )

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
# 返回包含文件描述符fd的文件的文件系统的信息，像 statvfs() Unix上可用。
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 获取元组
info = os.fstatvfs(fd)
print "文件信息 :", info
# 获取文件名最大长度
print "文件名最大长度 :%d" % info.f_namemax
# 获取可用块数
print "可用块数 :%d" % info.f_bfree
# 关闭文件
os.close(fd)

# 19 os.fsync(fd)
# 强制将文件描述符为fd的文件写入硬盘。
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 写入字符串
os.write(fd, "This is test")
# 使用 fsync() 方法.
os.fsync(fd)
# 读取内容
os.lseek(fd, 0, 0)
str = os.read(fd, 100)
print "读取的字符串为 : ", str
# 关闭文件
os.close(fd)

# 20 os.ftruncate(fd, length)
# 裁剪文件描述符fd对应的文件, 所以它最大不能超过文件大小。
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 写入字符串
os.write(fd, "This is test - This is test")
# 使用 ftruncate() 方法
os.ftruncate(fd, 10)
# 读取内容
os.lseek(fd, 0, 0)
str = os.read(fd, 100)
print "读取的字符串是 : ", str
# 关闭文件
os.close( fd)

# 21 os.getcwd()
# 返回当前工作目录 
# 切换到 "/var/www/html" 目录
os.chdir("/var/www/html" )
# 打印当前目录
print "当前工作目录 : %s" % os.getcwd()
# 打开 "/tmp"
fd = os.open( "/tmp", os.O_RDONLY )
# 使用 os.fchdir() 方法修改目录
os.fchdir(fd)
# 打印当前目录
print "当前工作目录 : %s" % os.getcwd()
# 关闭文件
os.close(fd)

# 22 os.getcwdu()
# 返回一个当前工作目录的Unicode对象
# 切换到 "/var/www/html" 目录
os.chdir("/var/www/html" )
# 打印当前目录
print "当前工作目录 : %s" % os.getcwdu()
# 打开 "/tmp"
fd = os.open( "/tmp", os.O_RDONLY )
# 使用 os.fchdir() 方法修改目录
os.fchdir(fd)
# 打印当前目录
print "当前工作目录 : %s" % os.getcwdu()
# 关闭文件
os.close(fd)

# 23 os.isatty(fd)
# 如果文件描述符fd是打开的，同时与tty(-like)设备相连，则返回true, 否则False。
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 写入字符串
os.write(fd, "This is test")
# 使用 isatty() 查看文件
ret = os.isatty(fd)
print "返回值: ", ret
# 关闭文件
os.close(fd)

# 24 os.lchflags(path, flags)
# 设置路径的标记为数字标记，类似 chflags()，但是没有软链接
# 打开文件
path = "/var/www/html/foo.txt"
fd = os.open( path, os.O_RDWR|os.O_CREAT )
# 关闭文件
os.close( fd )
# 修改文件标记
ret = os.lchflags(path, os.UF_IMMUTABLE )
print "修改文件标记成功!!"

# 25 os.lchmod(path, mode) 
# 修改连接文件权限 只支持在 Unix 下使用。
# 打开文件
path = "/var/www/html/foo.txt"
fd = os.open( path, os.O_RDWR|os.O_CREAT )
# 关闭文件
os.close( fd )
# 修改文件权限
# 设置文件可以通过组执行
os.lchmod( path, stat.S_IXGRP)
# 设置文件可以被其他用户写入
os.lchmod("/tmp/foo.txt", stat.S_IWOTH)

# 26 os.lchown(path, uid, gid)
# 更改文件所有者，类似 chown，但是不追踪链接。 只支持在 Unix 下使用。
# 打开文件
path = "/var/www/html/foo.txt"
fd = os.open( path, os.O_RDWR|os.O_CREAT )
# 关闭打开的文件
os.close( fd )
# 修改文件权限
# 设置文件所属用户 ID
os.lchown( path, 500, -1)
# 设置文件所属用户组 ID
os.lchown( path, -1, 500)

# 27 os.link(src, dst)
# 创建硬链接，名为参数 dst，指向参数 src 该方法对于创建一个已存在文件的拷贝是非常有用的。 src -- 用于创建硬连接的源地址  dst -- 用于创建硬连接的目标地址 
# 打开文件
path = "/var/www/html/foo.txt"
fd = os.open( path, os.O_RDWR|os.O_CREAT )
# 关闭文件
os.close( fd )
# 创建以上文件的拷贝
dst = "/tmp/foo.txt"
os.link( path, dst)

# 28 os.listdir(path)
# 返回path指定的文件夹包含的文件或文件夹的名字的列表。 
# 打开文件
path = "/var/www/html/"
dirs = os.listdir( path )
# 输出所有文件和文件夹
for file in dirs:
   print file

# 29 os.lseek(fd, pos, how)
# 设置文件描述符 fd当前位置为pos, how方式修改: SEEK_SET 或者 0 设置从文件开始的计算的pos; SEEK_CUR或者 1 则从当前位置计算; os.SEEK_END或者2则从文件尾部开始. 在unix，Windows中有效
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 写入字符串
os.write(fd, "This is test")
# 所有 fsync() 方法
os.fsync(fd)
# 从开始位置读取字符串
os.lseek(fd, 0, 0)
str = os.read(fd, 100)
print "Read String is : ", str
# 关闭文件
os.close( fd )

# 30 os.lstat(path)
# 像stat(),但是没有软链接 
# 打开文件
path = "/var/www/html/foo.txt"
fd = os.open( path, os.O_RDWR|os.O_CREAT )
# 关闭打开的文件
os.close( fd )
# 获取元组
info = os.lstat(path)
print "文件信息 :", info
# 获取文件 uid
print "文件 UID  :%d" % info.st_uid
# 获取文件 gid
print "文件 GID :%d" % info.st_gid

# 31 os.major(device)
# 从原始的设备号中提取设备major号码 (使用stat中的st_dev或者st_rdev field)。
path = "/var/www/html/foo.txt"
# 获取元组
info = os.lstat(path)
# 获取 major 和 minor 设备号
major_dnum = os.major(info.st_dev)
minor_dnum = os.minor(info.st_dev)
print "Major 设备号 :", major_dnum
print "Minor 设备号 :", minor_dnum


# 32 os.makedev(major, minor)
# 以major和minor设备号组成一个原始设备号
path = "/var/www/html/foo.txt"
# 获取元组
info = os.lstat(path)
# 获取 major 和 minor 设备号
major_dnum = os.major(info.st_dev)
minor_dnum = os.minor(info.st_dev)
print "Major 设备号 :", major_dnum
print "Minor 设备号 :", minor_dnum
# 生成设备号
dev_num = os.makedev(major_dnum, minor_dnum)
print "设备号 :", dev_num

# 33 os.makedirs(path[, mode])
# 递归文件夹创建函数。像mkdir(), 但创建的所有intermediate-level文件夹需要包含子文件夹。
# 创建的目录
path = "/tmp/home/monthly/daily"
os.makedirs( path, 0755 );

# 34 os.minor(device)
# 从原始的设备号中提取设备minor号码 (使用stat中的st_dev或者st_rdev field )。
path = "/var/www/html/foo.txt"
# 获取元组
info = os.lstat(path)
# 获取 major 和 minor 设备号
major_dnum = os.major(info.st_dev)
minor_dnum = os.minor(info.st_dev)
print "Major 设备号 :", major_dnum
print "Minor 设备号 :", minor_dnum

# 35 os.mkdir(path[, mode])
# 以数字mode的mode创建一个名为path的文件夹.默认的 mode 是 0777 (八进制)。 
# 创建的目录
path = "/tmp/home/monthly/daily/hourly"
os.mkdir( path, 0755 );

# 36 os.mkfifo(path[, mode])
# 创建命名管道，mode 为数字，默认为 0666 (八进制) 
# 创建的目录
path = "/tmp/hourly"
os.mkfifo( path, 0644 )
print "路径被创建"

# 37 os.mknod(filename[, mode=0600, device])
# 创建一个名为filename文件系统节点（文件，设备特别文件或者命名pipe）。
filename = '/tmp/tmpfile'
mode = 0600|stat.S_IRUSR
# 文件系统节点指定不同模式
os.mknod(filename, mode)

# 38 os.open(file, flags[, mode])
# 打开一个文件，并且设置需要的打开选项，mode参数是可选的
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
# 写入字符串
os.write(fd, "This is test")
# 关闭文件
os.close( fd )

# 39 os.openpty()
# 打开一个新的伪终端对。返回 pty 和 tty的文件描述符。
# 主 pty, 从 tty
m,s = os.openpty()
print m
print s
# 显示终端名
s = os.ttyname(s)
print m
print s

# 40 os.pathconf(path, name)
# 返回相关文件的系统配置信息。 
# 打开文件
fd = os.open( "foo.txt", os.O_RDWR|os.O_CREAT )
print "%s" % os.pathconf_names
# 获取文件最大连接数
no = os.fpathconf(fd, 'PC_LINK_MAX')
print "Maximum number of links to the file. :%d" % no
# 获取文件名最大长度
no = os.fpathconf(fd, 'PC_NAME_MAX')
print "Maximum length of a filename :%d" % no
# 关闭文件
os.close( fd)

# 41 os.pipe()
# 创建一个管道. 返回一对文件描述符(r, w) 分别为读和写
print "The child will write text to a pipe and "
print "the parent will read the text written by child..."
# file descriptors r, w for reading and writing
r, w = os.pipe() 
processid = os.fork()
if processid:
    # This is the parent process 
    # Closes file descriptor w
    os.close(w)
    r = os.fdopen(r)
    print "Parent reading"
    str = r.read()
    print "text =", str   
    sys.exit(0)
else:
    # This is the child process
    os.close(r)
    w = os.fdopen(w, 'w')
    print "Child writing"
    w.write("Text written by child...")
    w.close()
    print "Child closing"
    sys.exit(0)

# 42 os.popen(command[, mode[, bufsize]])
# 从一个 command 打开一个管道
# 使用 mkdir 命令
a = 'mkdir nwdir'
b = os.popen(a,'r',1)
print b

# 43 os.read(fd, n)
# 从文件描述符 fd 中读取最多 n 个字节，返回包含读取字节的字符串，文件描述符 fd对应文件已达到结尾, 返回一个空字符串。
# 打开文件
fd = os.open("f1.txt",os.O_RDWR)
# 读取文本
ret = os.read(fd,12)
print ret
# 关闭文件
os.close(fd)
print "关闭文件成功!!"

# 44 os.readlink(path)
# 返回软链接所指向的文件 
src = '/usr/bin/python'
dst = '/tmp/python'
# 创建软链接
os.symlink(src, dst)
# 使用软链接显示源链接
path = os.readlink( dst )
print path

# 45 os.remove(path)
# 删除路径为path的文件。如果path 是一个文件夹，将抛出OSError; 查看下面的rmdir()删除一个 directory。
# 列出目录
print "目录为: %s" %os.listdir(os.getcwd())
# 移除
os.remove("aa.txt")
# 移除后列出目录
print "移除后 : %s" %os.listdir(os.getcwd())

# 46 os.removedirs(path)
# 递归删除目录。
# 列出目录
print "目录为: %s" %os.listdir(os.getcwd())
# 移除
os.removedirs("/test")
# 列出移除后的目录
print "移除后目录为:" %os.listdir(os.getcwd())

# 47 os.rename(src, dst)
# 重命名文件或目录，从 src 到 dst
# 列出目录
print "目录为: %s"%os.listdir(os.getcwd())
# 重命名
os.rename("test","test2")
print "重命名成功。"
# 列出重命名后的目录
print "目录为: %s" %os.listdir(os.getcwd())

# 48 os.renames(old, new)
# 递归地对目录进行更名，也可以对文件进行更名。
print "当前目录为: %s" %os.getcwd()
# 列出目录
print "目录为: %s"%os.listdir(os.getcwd())
# 重命名 "aa1.txt"
os.renames("aa1.txt","newdir/aanew.txt")
print "重命名成功。"
# 列出重命名的文件 "aa1.txt"
print "目录为: %s" %os.listdir(os.getcwd())

# 49 os.rmdir(path)
# 删除path指定的空目录，如果目录非空，则抛出一个OSError异常。
# 列出目录
print "目录为: %s"%os.listdir(os.getcwd())
# 删除路径
os.rmdir("mydir")
# 列出重命名后的目录
print "目录为: %s" %os.listdir(os.getcwd())

# 50 os.stat(path)
# 获取path指定的路径的信息，功能等同于C API中的stat()系统调用。
# 显示文件 "a2.py" 信息
statinfo = os.stat('a2.py')
print statinfo

# 51 os.stat_float_times([newvalue])
# 决定stat_result是否以float对象显示时间戳
# Stat 信息
statinfo = os.stat('a2.py')
print statinfo
statinfo = os.stat_float_times()
print statinfo

# 52 os.statvfs(path)
# 获取指定路径的文件系统统计信息
# 显示 "a1.py" 文件的 statvfs 信息
stinfo = os.statvfs('a1.py')
print stinfo

# 53 os.symlink(src, dst)
# 创建一个软链接
src = '/usr/bin/python'
dst = '/tmp/python'
# 创建软链接
os.symlink(src, dst)
print "软链接创建成功"

# 54 os.tcgetpgrp(fd)
# 返回与终端fd（一个由os.open()返回的打开的文件描述符）关联的进程组 
# 显示当前目录
print "当前目录 :%s" %os.getcwd()
# 修改目录到 /dev/tty
fd = os.open("/dev/tty",os.O_RDONLY)
f = os.tcgetpgrp(fd)
# 显示进程组
print "相关进程组: "
print f
os.close(fd)

# 55 os.tcsetpgrp(fd, pg)
# 设置与终端fd（一个由os.open()返回的打开的文件描述符）关联的进程组为pg。
# 显示当前目录
print "当前目录 :%s" %os.getcwd()
# 修改目录到 /dev/tty
fd = os.open("/dev/tty",os.O_RDONLY)
f = os.tcgetpgrp(fd)
# 显示进程组
print "关联进程组: "
print f
# 设置进程组
os.tcsetpgrp(fd,2672)
print "done"
os.close(fd)

# 56 os.tempnam([dir[, prefix]])
# 返回唯一的路径名用于创建临时文件。 
# 前缀为 runoob 的文件
tmpfn = os.tempnam('/tmp/runoob,'runoob')
print "这是一个唯一路径:"
print tmpfn
# 执行以上程序输出结果为：
# 这是一个唯一路径:
# /tmp/runoob/runoobIbAco8

# 57 os.tmpfile()
# 返回一个打开的模式为(w+b)的文件对象 .这文件对象没有文件夹入口，没有文件描述符，将会自动删除。 
# 创建临时文件对象
tmpfile = os.tmpfile()
tmpfile.write('临时文件在这创建了.....')
tmpfile.seek(0)
print tmpfile.read()
tmpfile.close

# 58 os.tmpnam()
# 为创建一个临时文件返回一个唯一的路径
# 生成临时路径
tmpfn = os.tmpnam()
print "这是一个唯一的路径:"
print tmpfn

# 59 os.ttyname(fd)
# 返回一个字符串，它表示与文件描述符fd 关联的终端设备。如果fd 没有与终端设备关联，则引发一个异常。
# 显示当前目录
print "当前目录 :%s" %os.getcwd()
# 修改目录为 /dev/tty
fd = os.open("/dev/tty",os.O_RDONLY)
p = os.ttyname(fd)
print "关联的终端为: "
print p
print "done!!"
os.close(fd)

# 60 os.unlink(path)
# 删除文件路径 
# 列出目录
print "目录为: %s" %os.listdir(os.getcwd())
os.unlink("aa.txt")
# 删除后的目录
print "删除后的目录为 : %s" %os.listdir(os.getcwd())

# 61 os.utime(path, times)
# 返回指定的path文件的访问和修改的时间。 
# 显示文件的 stat 信息
stinfo = os.stat('a2.py')
print stinfo
# 使用 os.stat 来接收文件的访问和修改时间
print "a2.py 的访问时间: %s" %stinfo.st_atime
print "a2.py 的修改时间: %s" %stinfo.st_mtime
# 修改访问和修改时间
os.utime("a2.py",(1330712280, 1330712292))
print "done!!"

# 62 os.walk(top[, topdown=True[, onerror=None[, followlinks=False]]])
# 输出在文件夹中的文件名通过在树中游走，向上或者向下。
for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))

# 63 os.write(fd, str)
# 写入字符串到文件描述符 fd中. 返回实际写入的字符串长度
# 打开文件
fd = os.open("f1.txt",os.O_RDWR|os.O_CREAT)
# 写入字符串
ret = os.write(fd,"This is runoob.com site")
# 输入返回值
print "写入的位数为: "
print  ret
print "写入成功"
# 关闭文件
os.close(fd)
print "关闭文件成功!!"