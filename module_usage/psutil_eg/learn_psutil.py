# -*- coding: utf-8-*-
# win/linux 下使用 psutil 获取进程 CPU / memory / IO 占用信息
# 1. 安装
# pip 安装即可。
#
# windows 下需要安装 vs2008，否则报错： Unable to find vcvarsall.bat
#
# 如果已经安装 vs2010 / vs2012 则需要设置环境变量，VS90COMNTOOLS 指向已有的 vs 变量。
#
# vs2010 设置如下：
#
# VS90COMNTOOLS = %VS100COMNTOOLS%
# 2. 获取特定进程对象
# 根据进程 ID 创建进程对象
# 获取所有进程对象，过滤出目标进程


# import psutil
#
#
# def get_proc_by_id(pid):
#     return psutil.Process(pid)
#
#
# def get_proc_by_name(pname):
#     """ get process by name
#
#     return the first process if there are more than one
#     """
#     for proc in psutil.process_iter():
#         try:
#             if proc.name().lower() == pname.lower():
#                 return proc  # return if found one
#         except psutil.AccessDenied:
#             pass
#         except psutil.NoSuchProcess:
#             pass
#     return None
#
#
# if '__main__' == __name__:
#     print get_proc_by_name("chrome.exe")
#     print get_proc_by_id(4364)

# 3. 获取进程信息
# 3.1 需要特别注意异常保护，尤其是  psutil.AccessDenied
#
# 不同的进程，权限等信息可能不同，遍历所有进程取信息时，需要对每一个进程单独进程异常保护。
#
# 3.2 获取所有进程
#
# 大多数 demo 代码中，都是使用  psutil.get_process_list ，但该方法在源码中已经标记为废弃。
#
# 新推荐的是  psutil.process_iter 迭代器。
#
# 根据下面的源码可知实现原理：获取所有进程 ID，然后根据 ID 创建进程对象。

# _pmap = {}
#
# def process_iter():
#     """Return a generator yielding a Process class instance for all
#     running processes on the local machine.
#
#     Every new Process instance is only created once and then cached
#     into an internal table which is updated every time this is used.
#
#     Cached Process instances are checked for identity so that you're
#     safe in case a PID has been reused by another process, in which
#     case the cached instance is updated.
#
#     The sorting order in which processes are yielded is based on
#     their PIDs.
#     """
#     def add(pid):
#         proc = Process(pid)
#         _pmap[proc.pid] = proc
#         return proc
#
#     def remove(pid):
#         _pmap.pop(pid, None)
#
#     a = set(get_pid_list())
#     b = set(_pmap.keys())
#     new_pids = a - b
#     gone_pids = b - a
#
#     for pid in gone_pids:
#         remove(pid)
#     for pid, proc in sorted(list(_pmap.items()) + \
#                             list(dict.fromkeys(new_pids).items())):
#         try:
#             if proc is None:  # new process
#                 yield add(pid)
#             else:
#                 # use is_running() to check whether PID has been reused by
#                 # another process in which case yield a new Process instance
#                 if proc.is_running():
#                     yield proc
#                 else:
#                     yield add(pid)
#         except NoSuchProcess:
#             remove(pid)
#         except AccessDenied:
#             # Process creation time can't be determined hence there's
#             # no way to tell whether the pid of the cached process
#             # has been reused. Just return the cached version.
#             yield proc
# @_deprecated()
# def get_process_list():
#     """Return a list of Process class instances for all running
#     processes on the local machine (deprecated).
#     """
#     return list(process_iter())
#
# 3.3 进程的内存信息 -- VSS/RSS/PSS/USS
#
# VSS 是剩余的可访问内存。
#
# 进程占用内存包括 2 部分，自身 + 共享库。不同的算法产生了 3 个不同的内存指标，分别是：RSS / PSS / USS。
#
# 一般来说内存占用大小有如下规律：VSS >= RSS >= PSS >= USS
#
# proc = psutil.Process(4364)
#
# total = psutil.virtual_memory().total
# rss, vss = proc.memory_info()
# percent = proc.memory_percent()
#
# print "rss: %s Byte, vss: %s Byte" % (rss, vss)
# print "total: %.2f(M)" % (float(total)/1024/1024/1024)
# print "percent: %.2f%%, calc: %.2f%%" % (percent, 100*float(rss)/total)