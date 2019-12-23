# -*- encoding: utf-8 -*-
'''
Created on 2019年11月6日

@author: houguangdong
'''

import signal
import os
import time
import sys
import threading
import traceback
import code

# print signal.getsignal(signal.SIGKILL)

# def receive_signal(signum, stack):
#     time.sleep(5)
#     print 'Received:', signum
#
#
# # 注册信号处理程序
# signal.signal(signal.SIGUSR1, receive_signal)
# signal.signal(signal.SIGUSR2, receive_signal)
#
# # 打印这个进程的PID方便使用kill传递信号
# print 'My PID is:', os.getpid()
#
# # 等待信号，有信号发生时则调用信号处理程序
# while True:
#     print 'Waiting...'
#     time.sleep(3)
############################################################

# def signal_usr1(signum, frame):
#     '''
#     Callback invoked when a signal is received
#     :param signum:
#     :param frame:
#     :return:
#     '''
#     pid = os.getpid()
#     print 'Received USR1 in process %s' % pid
#
#
# print 'Forking...'
# child_pid = os.fork()
# print '-----------------------'
# print os.getpid(), 'parent pid'
# print child_pid, 'child pid'
# if child_pid:
#     print '++++++++++++++++++++++++++++++++++++++++'
#     print 'PARENT: Pausing before sending signal...'
#     time.sleep(10)
#     print 'PARENT: Signaling %s' % child_pid
#     os.kill(child_pid, signal.SIGUSR1)
#     print '++++++++++++++++++++++++++++++++++++++++'
# else:
#     print 'CHILD: Setting up a signal handler'
#     signal.signal(signal.SIGUSR1, signal_usr1)
#     print 'CHILD: Pausing to wait for signal'
#     time.sleep(50)

############################################################

def do_exit(sig, stack):
    raise SystemExit('Exiting')


# 将SIGINT的默认处理程序替换为SIG_IGN
signal.signal(signal.SIGINT, signal.SIG_IGN)
signal.signal(signal.SIGUSR1, do_exit)


print 'My PID:', os.getpid()
print signal.getsignal(signal.SIGUSR1)
print signal.getsignal(signal.SIGINT)

# signal.pause()                                  # 暂停

############################################################
print '-----------------'
def received_alarm(signum, stack):
    print 'Alarm:', time.ctime()


# Call receive_alarm in seconds
# signal.signal(signal.SIGALRM, received_alarm)
# 如果time是非0，这个函数则响应一个SIGALRM信号并在time秒后发送到该进程。
# signal.alarm(10)

# print 'Before:', time.ctime()
# time.sleep(500)
# print 'After:', time.ctime()
############################################################
def dump_stacks(signal, frame):
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    print id2name, '111111', sys._current_frames().items()
    codes = []
    for threadId, stack in sys._current_frames().items():
        codes.append("\n# Thread: %s(%d)" % (id2name.get(threadId, ""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            codes.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                codes.append("  %s" % (line.strip()))


def print_stack(signal, frame):
    d = {'_frame': frame}           # Allow access to frame object.
    print frame.f_globals, '222222'
    print frame.f_locals, '33333'
    print frame.__class__, '4444'
    d.update(frame.f_globals)       # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)


signal.signal(signal.SIGUSR1, dump_stacks)
signal.signal(signal.SIGUSR2, print_stack)

# 调用方式
os.kill(43767, signal.SIGUSR1)