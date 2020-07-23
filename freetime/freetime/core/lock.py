# -*- coding=utf-8 -*-
# Author:        zipxing@hotmail.com, zhouhao@tuyoogame.com
# Created:       2015.3.28
 
from contextlib import  contextmanager
import functools
import inspect
import stackless
import time
import uuid
from functools import wraps

from freetime.aio.redis import doRedis
import freetime.util.log as ftlog
from twisted.internet import reactor

_NEED_TIMEOUT = 1

class FTLockTimeOutException(Exception):
    pass

class FTLock(stackless.channel):
    def __init__(self, lockkey, relockKey=None):
        stackless.channel.__init__(self)
        self.lockkey = lockkey
        self._islock = False
        self._fttask = None
        self.relock = 0
        self.relockKey = relockKey

    @property
    def isLocked(self):
        return self._islock

    def lock(self, relockKey=None, lockTimeout=60): # 添加60秒无法锁定的超时控制，重点爆出那些死锁问题
        if self._islock == True :
            if self._fttask == stackless.getcurrent() :
                self.relock += 1
                return
            if self.relockKey != None and self.relockKey == relockKey :
                self.relock += 1
                return
            if _NEED_TIMEOUT :
                handle = reactor.callLater(lockTimeout, self._timeOut)
            r = self.receive()
            if _NEED_TIMEOUT :
                try:
                    handle.cancel()
                except:
                    pass
                if isinstance(r, Exception) :
                    raise r
        self._islock = True
        self._fttask = stackless.getcurrent()


    def _timeOut(self):
        self.send(FTLockTimeOutException())
        
    def unlock(self):
        if self.relock > 0 :
            self.relock -= 1
            return 1
        self._fttask = None
        self._islock = False
        if self.balance < 0 :
            self.send(0)
            return 1
        return 0


def locked(func):
    '''Decorator of object locker 
       only used for object method
       
       e.g :
        
        class Room(object) : 
            def __init__(self):
                self.locker = FTLock(self.__class__.__name__ + "_%d" % id(self))
                
            @locked
            def syncChooseTableAndSit(self, userId):
                pass
    '''
    @wraps(func)
    def syncfunc(*args, **argkw):
        objself = args[0] 
        if not hasattr(objself, 'locker') :
            objself.locker = FTLock(objself.__class__.__name__ + "_%d" % id(objself))

        with lock(objself.locker) :
            ftlog.debug("locked func:", func.__name__)
            return func(*args, **argkw)

    return syncfunc


@contextmanager
def lock(locker):
    '''e.g.
        with lock(room.locker) :
            ...
    '''
    ftlog.debug("locker %s isLocked:%s" %(locker.lockkey, locker._islock))
    locker.lock()
    try:
        ftlog.debug("locker %s locked" %(locker.lockkey))
        yield
    except:
        raise
    finally:
        ftlog.debug("locker %s unlock" %(locker.lockkey))
        locker.unlock()
        
    
class FTRedLockException(Exception):
    pass


class FTRedLock:
    UNLOCK_LUA = '''if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end
    '''
    UNLOCK_SHA = None

    def __init__(self, lockname, timeout=150.0):
        self.lockname = lockname
        self.timeout = timeout
        self._fttask = None
        self._random = ''
        self._islock = 0


    def lock(self):
        self._fttask = stackless.getcurrent()._fttask
        _start = time.time()
        self._random = str(uuid.uuid4())
        while True:
            if FTRedLock.UNLOCK_SHA == None:
                FTRedLock.UNLOCK_SHA = doRedis('locker', 'SCRIPT', 'load', FTRedLock.UNLOCK_LUA)
            ret = doRedis('locker', 'SET', self.lockname, self._random, 'NX', 'PX', int(self.timeout * 1000))
            if ret:
                self._islock = 1
                return True
            else:
                self._fttask.sleepNb(0.05)
                if time.time() - _start > self.timeout:
                    raise FTRedLockException('lock timeout of ' + str(self.lockname))


    def unlock(self):
        if self._islock :
            doRedis('locker', 'EVALSHA', FTRedLock.UNLOCK_SHA, 1, self.lockname, self._random)
            self._islock = 0


def ftredlock(lock_name_head, lock_name_tails=[], timeout=150.0):
    '''Decorator of FTRedLock 
       
       e.g : 
        @ftredlock('table_data_lock', ['gameid', 'roomid', 'tableid'], 3.0)
        def syncChooseTableAndSit(self, gameid, roomid, tableid, userid):
    '''
    assert(isinstance(lock_name_head, (str, unicode)))
    assert(isinstance(lock_name_tails, (list, tuple)))
    assert(isinstance(timeout, (int, float)))


    def decorating_function(method):
        _timeout = timeout
        _lock_name_head = lock_name_head
        _lock_param_indexs = []

        paramkeys, _, __, ___ = inspect.getargspec(method)
        for lname in lock_name_tails :
            i = -1
            for x in xrange(len(paramkeys)) :
                if lname == paramkeys[x] :
                    i = x
                    break
            if i >= 0 :
                _lock_param_indexs.append(i)
            else:
                raise FTRedLockException('can not find the param name of :' + lname)


        @functools.wraps(method)
        def funwarp(*args, **argd):
            locker_name = _lock_name_head
            for i in _lock_param_indexs :
                locker_name = locker_name + ':' + str(args[i])
            locker = FTRedLock(locker_name, _timeout)
            try:
                locker.lock()
                return method(*args, **argd)
            finally:
                locker.unlock()
        return funwarp
    return decorating_function

