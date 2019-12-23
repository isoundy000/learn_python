#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/3 22:41
# @version: 0.0.1
# @Author: houguangdong
# @File: txredisapi.py
# @Software: PyCharm


# coding: utf-8
# Copyright 2009 Alexandre Fiori
# https://github.com/fiorix/txredisapi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Credits:
#   The Protocol class is an improvement of txRedis' protocol,
#   by Dorian Raymer and Ludovico Magnocavallo.
#
#   Sharding and Consistent Hashing implementation by Gleicon Moraes.
#

import six

import bisect
import collections
import functools
import operator
import re
import warnings
import zlib
import string
import hashlib
import random

from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.tcp import Connector
from twisted.protocols import basic
from twisted.protocols import policies
from twisted.python import log
from twisted.python.failure import Failure

try:
    import hiredis
except ImportError:
    hiredis = None


class RedisError(Exception):
    pass


class ConnectionError(RedisError):
    pass


class ResponseError(RedisError):
    pass


class ScriptDoesNotExist(ResponseError):
    pass


class NoScriptRunning(ResponseError):
    pass


class InvalidResponse(RedisError):
    pass


class InvalidData(RedisError):
    pass


class WatchError(RedisError):
    pass


def list_or_args(command, keys, args):
    oldapi = bool(args)
    try:
        iter(keys)
        if isinstance(keys, six.string_types) or \
            isinstance(keys, six.binary_type):
            keys = [keys]
            if not oldapi:
                return keys
            oldapi = True
    except TypeError:
        oldapi = True
        keys = [keys]

    if oldapi:
        warnings.warn(DeprecationWarning(
            "Passing *args to redis.%s is deprecated. "
            "Pass an iterable to ``keys`` instead" % command
        ))
        keys.extend(args)
    return keys


# Possible first characters in a string containing an integer or a float.
_NUM_FIRST_CHARS = frozenset(string.digits + "+-.")


class MultiBulkStorage(object):

    def __init__(self, parent=None):
        self.items = None
        self.pending = None
        self.parent = parent

    def set_pending(self, pending):
        if self.pending is None:
            if pending < 0:
                self.items = None
                self.pending = 0
            else:
                self.items = []
                self.pending = pending
            return self
        else:
            m = MultiBulkStorage(self)
            m.set_pending(pending)
            return m

    def append(self, item):
        self.pending -= 1
        self.items.append(item)


class LineReceiver(protocol.Protocol, basic._PauseableMixin):

    callLater = reactor.callLater
    line_mode = 1
    __buffer = six.b('')
    delimiter = six.b('\r\n')
    MAX_LENGTH = 16384

    def clearLineBuffer(self):
        b = self.__buffer
        self.__buffer = six.b('')
        return b

    def dataReceived(self, data, unpause=False):
        if unpause is True:
            if self.__buffer:
                self.__buffer = data + self.__buffer
            else:
                self.__buffer += data

            self.resumeProducing()
        else:
            self.__buffer = self.__buffer + data

        while self.line_mode and not self.paused:
            try:
                line, self.__buffer = self.__buffer.split(self.delimiter, 1)
            except ValueError:
                if len(self.__buffer) > self.MAX_LENGTH:
                    line, self.__buffer = self.__buffer, six.b('')
                    return self.lineLengthExceeded(line)
                break
            else:
                linelength = len(line)
                if linelength > self.MAX_LENGTH:
                    exceeded = line + self.__buffer
                    self.__buffer = six.b('')
                    return self.lineLengthExceeded(exceeded)
                if hasattr(line, 'decode'):
                    why = self.lineReceived(line.decode())
                else:
                    why = self.lineReceived(line)
                if why or self.transport and self.transport.disconnection:
                    return why
        else:
            if not self.paused:
                data = self.__buffer
                self.__buffer = six.b('')
                if data:
                    return self.rawDataReceived(data)

    def setLineMode(self, extra=six.b('')):
        self.line_mode = 1
        if extra:
            self.pauseProducing()
            self.callLater(0, self.dataReceived, extra, True)

    def setRawMode(self):
        self.line_mode = 0

    def rawDataReceived(self, data):
        raise NotImplementedError

    def lineReceived(self, line):
        raise NotImplementedError

    def sendLine(self, line):
        if isinstance(line, six.text_type):
            line = line.encode()
        return self.transport.write(line + self.delimiter)

    def lineLengthExceeded(self, line):
        return self.transport.loseConnection()


class ReplyQueue(defer.DeferredQueue):
    """
    Subclass defer.DeferredQueue to maintain consistency of
    producers / consumers in light of defer.cancel
    """
    def _cancelGet(self, d):
        # rather than remove(d), the default twisted behavior
        # we need to maintain an entry in the waiting list
        # because the reply code assumes that every call
        # to transport.write() generates a corresponding
        # reply value in the queue.
        # so we will just replace the cancelled deferred
        # with a noop
        i = self.waiting.index(d)
        self.waiting[i] = defer.Deferred()


def _blocking_command(release_on_callback):
    """
    Decorator used for marking protocol methods as `blocking` (methods that
    block connection from being used for sending another requests)
    release_on_callback means whether connection should be automatically
    released when deferred returned by method is fired
    """
    def decorator(method):
        method._blocking = True
        method._release_on_callback = release_on_callback
        return method

    return decorator


class BaseRedisProtocol(LineReceiver, policies.TimeoutMixin):
    """
    Redis client protocol.
    """
    def __init__(self, charset="utf-8", errors="strict"):
        self.charset = charset
        self.errors = errors

        self.bulk_length = 0
        self.bulk_buffer = bytearray()

        self.post_proc = []
        self.multi_bulk = MultiBulkStorage()

        self.replyQueue = ReplyQueue()

        self.transactions = 0
        self.inTransaction = False
        self.inMulti = False
        self.unwatch_cc = lambda : ()
        self.commit_cc = lambda : ()

        self.script_hashes = set()

        self.pipelining = False
        self.pipelined_commands = []
        self.pipelined_replies = []

    @defer.inlineCallbacks
    def connectionMade(self):
        if self.factory.password is not None:
            try:
                response = yield self.auth(self.factory.password)
                if isinstance(response, ResponseError):
                    raise response
            except Exception as e:
                self.factory.continueTrying = False
                self.transport.loseConnection()

                msg = "Redis error: could not auth: %s" % (str(e))
                self.factory.connectionError(msg)
                if self.factory.isLazy:
                    log.msg(msg)
                defer.returnValue(None)

        if self.factory.dbid is not None:
            try:
                response = yield self.select(self.factory.dbid)
                if isinstance(response, ResponseError):
                    raise response
            except Exception as e:
                self.factory.continueTrying = False
                self.transport.closConnection()

                msg = "Redis error: could not set dbid=%s: %s" % \
                      (self.factory.dbid, str(e))
                self.factory.connectionError(msg)
                if self.factory.isLazy:
                    log.msg(msg)
                defer.returnValue(None)

        self.connected = 1
        self.factory.addConnection(self)

    def connectionLost(self, why):
        self.connected = 0
        self.script_hashes.clear()
        self.factory.delConnection(self)
        LineReceiver.connectionLost(self, why)
        while self.replyQueue.waiting:
            self.replyReceived(ConnectionError("Lost connection"))

    def lineReceived(self, line):
        """
        Reply types:
          "-" error message
          "+" single line status reply
          ":" integer number (protocol level only?)
          "$" bulk data
          "*" multi-bulk data
        """
        if line:
            self.resetTimeout()
            token, data = line[0], line[1:]
        else:
            return

        if token == "$":    # bulk data
            try:
                self.bulk_length = int(data)
            except ValueError:
                self.replyReceived(InvalidResponse("Cannot convert data"
                                                   "'%s' to integer" % data))
            else:
                if self.bulk_length == -1:
                    self.bulk_length = 0
                    self.bulkDataReceived(None)
                else:
                    self.bulk_length += 2       # 2 == \r\n
                    self.setRawMode()

        elif token == "*":  # multi-bulk data
            try:
                n = int(data)
            except (TypeError, ValueError):
                self.multi_bulk = MultiBulkStorage()
                self.replyReceived(InvalidResponse(
                    "Cannot convert "
                    "multi-response header "
                    "'%s' to integer" % data
                ))
            else:
                self.multi_bulk = self.multi_bulk.set_pending(n)
                if n in (0, -1):
                    self.multiBulkDataReceived()

        elif token == "+":  # single line status
            if data == "QUEUED":
                self.transactions += 1
                self.replyReceived(data)
            else:
                if self.multi_bulk.pending:
                    self.handleMultiBulkElement(data)
                else:
                    self.replyReceived(data)

        elif token == "-":  # error
            reply = ResponseError(data[4:] if data[:4] == "ERR" else data)
            if self.multi_bulk.pending:
                self.handleMultiBulkElement(reply)
            else:
                self.replyReceived(reply)

        elif token == ":":  # integer
            try:
                reply = int(data)
            except ValueError:
                reply = InvalidResponse(
                    "Cannot convert data '%s' to integer" % data
                )
            if self.multi_bulk.pending:
                self.handleMultiBulkElement(reply)
            else:
                self.replyReceived(reply)

    def handleMultiBulkElement(self, element):
        self.multi_bulk.append(element)

        if not self.multi_bulk.pending:
            self.multiBulkDataReceived()

    def multiBulkDataReceived(self):
        """
        Receipt of list or set of bulk data elements.
        """
        while self.multi_bulk.parent and not self.multi_bulk.pending:
            p = self.multi_bulk.parent
            p.append(self.multi_bulk.items)
            self.multi_bulk = p

        if not self.multi_bulk.pending:
            reply = self.multi_bulk.items
            self.multi_bulk = MultiBulkStorage()

            reply = self.handleTransactionData(reply)

            self.replyReceived(reply)

    def handleTransactionData(self, reply):
        if self.inTransaction and isinstance(reply, list):
            # watch or multi has been called
            if self.transactions > 0:
                # multi: this must be an exec [commit] reply
                self.transactions -= len(reply)
            if self.transactions == 0:
                self.commit_cc()
            if not self.inTransaction:  # multi: this must be an exec reply
                tmp = []
                for f, v in zip(self.post_proc[1:], reply):
                    if callable(f):
                        tmp.append(f(v))
                    else:
                        tmp.append(v)
                    reply = tmp
            self.post_proc = []
        return reply

    def replyReceived(self, reply):
        """
        Complete reply received and ready to be pushed to the requesting
        function.
        """
        self.replyQueue.put(reply)

    @staticmethod
    def handle_reply(r):
        if isinstance(r, Exception):
            raise r
        return r

    def _encode_value(self, arg):
        if isinstance(arg, six.binary_type):
            return arg
        elif isinstance(arg, six.text_type):
            if self.charset is None:
                try:
                    return arg.encode()
                except UnicodeError:
                    pass
                raise InvalidData("Encoding charset was not specified")
            try:
                return arg.encode(self.charset, self.errors)
            except UnicodeEncodeError as e:
                raise InvalidData(
                    "Error encoding unicode value '%s': %s" % (repr(arg), e)
                )
        elif isinstance(arg, float):
            return format(arg, "f").encode()
        elif isinstance(arg, bytearray):
            return bytes(arg)
        else:
            return str(arg).format().encode()

    def _build_command(self, *args, **kwargs):
        # Build the redis command.
        cmds = bytearray()
        cmd_count = 0
        for s in args:
            cmd = self._encode_value(s)
            cmds.extend(six.b("$"))
            for token in self._encode_value(len(cmd)), cmd:         # for token in 3, 4: print token
                cmds.extend(token)
                cmds.extend(six.b("\r\n"))
            cmd_count += 1

        command = bytes(six.b("").join([six.b("*"), self._encode_value(cmd_count), six.b("\r\n")]) + cmds)
        if not isinstance(command, six.binary_type):
            command = command.encode()
        return command

    def execute_command(self, *args, **kwargs):
        if self.connected == 0:
            raise ConnectionError("Not connected")
        else:
            command = self._build_command(*args, **kwargs)
            print(command)
            # When pipelining, buffer this command into our list of
            # pipelined commands. Otherwise, write the command immediately.
            if self.pipelining:
                self.pipelined_commands.append(command)
            else:
                self.transport.write(command)

            # Return deferred that will contain the result of this command.
            # Note: when using pipelining, this deferred will NOT return
            # until after execute_pipeline is called.
            r = self.replyQueue.get().addCallback(self.handle_reply)

            # When pipelining, we need to keep track of the deferred replies
            # so that we can wait for them in a DeferredList when
            # execute_pipeline is called.
            if self.pipelining:
                self.pipelined_replies.append(r)

            if self.inMulti:
                self.post_proc.append(kwargs.get("post_proc"))
            else:
                if "post_proc" in kwargs:
                    f = kwargs["post_proc"]
                    if callable(f):
                        r.addCallback(f)
            return r

    ##
    # REDIS COMMANDS
    ##

    # Connection handling
    def quit(self):
        """
        Close the connection
        """
        self.factory.continueTrying = False
        return self.execute_command("QUIT")

    def auth(self, password):
        """
        Simple password authentication if enabled
        """
        return self.execute_command("AUTH", password)

    def ping(self):
        """
        Ping the server
        """
        return self.execute_command("PING")

    # Commands operating on all value types
    def exists(self, key):
        """
        Test if a key exists
        """
        return self.execute_command("EXISTS", key)

    def delete(self, keys, *args):
        """
        Delete one or more keys
        """
        keys = list_or_args("delete", keys, args)
        return self.execute_command("DEL", *keys)

    def type(self, key):
        """
        Return the type of the value stored at key
        """
        return self.execute_command("TYPE", key)

    def keys(self, pattern="*"):
        """
        Return all the keys matching a given pattern
        """
        return self.execute_command("KEYS", pattern)

    @staticmethod
    def _build_scan_args(cursor, pattern, count):
        """
        Construct arguments list for SCAN, SSCAN, HSCAN, ZSCAN commands
        """
        args = [cursor]
        if pattern is not None:
            args.extend(("MATCH", pattern))
        if count is not None:
            args.extend(("COUNT", count))

        return args

    def scan(self, cursor=0, pattern=None, count=None):
        """
        Incrementally iterate the keys in database
        """
        args = self._build_scan_args(cursor, pattern, count)
        return self.execute_command("SCAN", *args)

    def randomkey(self):
        """
        Return a random key from the key space
        """
        return self.execute_command("RANDOMKEY")

    def rename(self, oldkey, newkey):
        """
        Rename the old key in the new one,
        destroying the newname key if it already exists
        """
        return self.execute_command("RENAME", oldkey, newkey)

    def renamenx(self, oldkey, newkey):
        """
        Rename the oldname key to newname,
        if the newname key does not already exist
        """
        return self.execute_command("RENAMENX", oldkey, newkey)

    def dbsize(self):
        """
        Return the number of keys in the current db
        """
        return self.execute_command("DBSIZE")

    def expire(self, key, time):
        """
        Set a time to live in seconds on a key
        """
        return self.execute_command("EXPIRE", key, time)

    def persist(self, key):
        """
        Remove the expire from a key
        """
        return self.execute_command("PERSIST", key)

    def ttl(self, key):
        """
        Get the time to live in seconds of a key
        """
        return self.execute_command("TTL", key)

    def select(self, index):
        """
        Select the DB with the specified index
        """
        return self.execute_command("SELECT", index)

    def move(self, key, dbindex):
        """
        Move the key from the currently selected DB to the dbindex DB
        """
        return self.execute_command("MOVE", key, dbindex)

    def flush(self, all_dbs=False):
        warnings.warn(DeprecationWarning(
            "redis.flush() has been deprecated, "
            "use redis.flushdb() or redis.flushall() instead"
        ))
        return all_dbs and self.flushall() or self.flushdb()

    def flushdb(self):
        """
        Remove all the keys from the currently selected DB
        """
        return self.execute_command("FLUSHDB")

    def flushall(self):
        """
        Remove all the keys from all the databases
        """
        return self.execute_command("FLUSHALL")

    def time(self):
        """
        Returns the current server time as a two items lists: a Unix timestamp
        and the amount of microseconds already elapsed in the current second
        """
        return self.execute_command("TIME")

    # Commands operating on string values
    def set(self, key, value, expire=None, pexpire=None, only_if_not_exists=False, only_if_exists=False):
        """
        Set a key to a string value
        """
        args = []
        if expire is not None:
            args.extend(("EX", expire))
        if pexpire is not None:
            args.extend(("PX", expire))
        if only_if_not_exists and only_if_exists:
            raise RedisError("only_if_not_exists and only_if_exists "
                             "cannot be true simultaneously")
        if only_if_not_exists:
            args.append("NX")
        if only_if_exists:
            args.append("XX")
        return self.execute_command("SET", key, value, *args)

    def get(self, key):
        """
        Return the string value of the key
        """
        return self.execute_command("GET", key)


class HiredisProtocol(BaseRedisProtocol):

    def __init__(self, *args, **kwargs):
        BaseRedisProtocol.__init__(self, *args, **kwargs)
        self._reader = hiredis.Reader(protocolError=InvalidData,
                                      replyError=ResponseError)

    def dataReceived(self, data, unpause=False):
        self.resetTimeout()
        if data:
            self._reader.feed(data)
        res = self._reader.gets()
        while res is not False:
            if isinstance(res, (six.text_type, six.binary_type, list)):
                res = self.tryConvertData(res)
            if res == "QUEUED":
                self.transactions += 1
            else:
                res = self.handleTransactionData(res)

            self.replyReceived(res)
            res = self._reader.gets()

    def _convert_bin_values(self, result):
        if isinstance(result, list):
            return [self._convert_bin_values(x) for x in result]
        elif isinstance(result, dict):
            return dict((self._convert_bin_values(k), self._convert_bin_values(v)) for k, v in six.iteritems(result))
        elif isinstance(result, six.binary_type):
            return self.tryConvertData(result)
        return result

    def commit(self):
        r = BaseRedisProtocol.commit(self)
        return r.addCallback(self._convert_bin_values)

    def scan(self, cursor=0, pattern=None, count=None):
        r = BaseRedisProtocol.scan(self, cursor, pattern, count)
        return r.addCallback(self._convert_bin_values)

    def sscan(self, key, cursor=0, pattern=None, count=None):
        r = BaseRedisProtocol.sscan(self, key, cursor, pattern, count)
        return r.addCallback(self._convert_bin_values)


class ConnectionHandler(object):

    def __init__(self, factory):
        self._factory = factory
        self._connected = factory.deferred

    def disconnect(self):
        self._factory.continueTrying = 0
        self._factory.disconnectCalled = True
        for conn in self._factory.pool:
            try:
                conn.transport.loseConnection()
            except:
                pass
        return self._factory.waitForEmptyPool()

    def __getattr__(self, method):
        def wrapper(*args, **kwargs):
            protocol_method = getattr(self._factory.protocal, method)
            blocking = getattr(protocol_method, '_blocking', False)
            release_on_callback = getattr(protocol_method, '_release_on_callback', True)

            d = self._factory.getConnection(peek=not blocking)

            def callback(connection):
                log.msg("connection:", connection)
                try:
                    d = protocol_method(connection, *args, **kwargs)
                except Exception as _:
                    if blocking:
                        self._factory.connectionQueue.put(connection)
                    raise

                def put_back(reply):
                    self._factory.connectionQueue.put(connection)
                    return reply

                if blocking and release_on_callback:
                    d.addBoth(put_back)
                return d

            d.addCallback(callback)
            return d

        return wrapper

    def __repr__(self):
        try:
            cli = self._factory.pool[0].transport.getPeer()
        except:
            return "<Redis Connection: Not connected>"
        else:
            return "<Redis Connection: %s:%s - %d connection(s)>" % \
                   (cli.host, cli.port, self._factory.size)


if hiredis is not None:
    RedisProtocol = HiredisProtocol
else:
    RedisProtocol = BaseRedisProtocol


class PeekableQueue(defer.DeferredQueue):
    """
    A DeferredQueue that supports peeking, accessing random item without
    removing them from the queue.
    """
    def __init__(self, *args, **kwargs):
        defer.DeferredQueue.__init__(self, *args, **kwargs)
        self.peekers = []

    def peek(self):
        if self.pending:
            return defer.succeed(random.choice(self.pending))
        else:
            d = defer.Deferred()
            self.peekers.append(d)
            return d

    def remove(self, item):
        self.pending.remove(item)

    def put(self, obj):
        for d in self.peekers:
            d.callback(obj)
        self.peekers = []

        defer.DeferredQueue.put(self, obj)


class RedisFactory(protocol.ReconnectingClientFactory):

    maxDelay = 10
    protocol = RedisProtocol

    def __init__(self, uuid, dbid, poolsize, isLazy=False,
                 handler=ConnectionHandler, charset="utf-8", password=None,
                 replyTimeout=None, convertNumbers=True):

        if not isinstance(poolsize, int):
            raise ValueError("Redis poolsize must be an integer, not %s" % repr(poolsize))

        if not isinstance(dbid, (int, type(None))):
            raise ValueError("Redis dbid must be an integer, not %s" % repr(dbid))

        self.uuid = uuid                # (host, port)
        self.dbid = dbid
        self.poolsize = poolsize
        self.isLazy = isLazy
        self.charset = charset
        self.password = password
        self.replyTimeout = replyTimeout
        self.convertNumbers = convertNumbers

        self.idx = 0
        self.size = 0
        self.pool = []
        self.deferred = defer.Deferred()
        self.handler = handler(self)
        self.connectionQueue = PeekableQueue()
        self._waitingForEmptyPool = set()
        self.disconnectCalled = False

    def buildProtocol(self, addr):
        if hasattr(self, 'charset'):
            p = self.protocol(self.charset)
        else:
            p = self.protocol()
        p.factory = self
        p.timeOut = self.replyTimeout
        return p

    def addConnection(self, conn):
        if self.disconnectCalled:
            conn.transport.loseConnection()
            return

        self.connectionQueue.put(conn)
        self.pool.append(conn)
        self.size = len(self.pool)
        if self.deferred:
            if self.size == self.poolsize:
                self.deferred.callbacks(self.handler)
                self.deferred = None

    def delConnection(self, conn):
        try:
            self.pool.remove(conn)
        except Exception as e:
            log.msg("Could not remove connection from pool: %s" % str(e))

        self.size = len(self.pool)
        if not self.size and self._waitingForEmptyPool:
            deferreds = self._waitingForEmptyPool
            self._waitingForEmptyPool = set()
            for d in deferreds:
                d.callback(None)

    def _cancelWaitForEmptyPool(self, deferred):
        self._waitingForEmptyPool.discard(deferred)
        deferred.errback(defer.CancelledError())

    def waitForEmptyPool(self):
        """
        Returns a Deferred which fires when the pool size has reached 0.
        """
        if not self.size:
            return defer.succeed(None)
        d = defer.Deferred(self._cancelWaitForEmptyPool)
        self._waitingForEmptyPool.add(d)
        return d

    def connectionError(self, why):
        if self.deferred:
            self.deferred.errback(ValueError(why))
            self.deferred = None

    @defer.inlineCallbacks
    def getConnection(self, peek=False):
        if not self.continueTrying and not self.size:
            raise ConnectionError("Not connected")

        while True:
            if peek:
                conn = yield self.connectionQueue.peek()
            else:
                conn = yield self.connectionQueue.get()

            if conn.connected == 0:
                log.msg("Discarding dead connection")
                if peek:
                    self.connectionQueue.remove(conn)
            else:
                defer.returnValue(conn)


def makeConnection(host, port, dbid, poolsize, reconnect, isLazy,
                   charset, password, connectTimeout, replyTimeout,
                   convertNumbers):
    uuid = "%s:%d" % (host, port)
    factory = RedisFactory(uuid, dbid, poolsize, isLazy, ConnectionHandler,
                           charset, password, replyTimeout, convertNumbers)
    factory.continueTrying = reconnect
    for x in range(poolsize):
        reactor.connectTCP(host, port, factory, connectTimeout)

    if isLazy:
        return factory.handler
    else:
        return factory.deferred


def Connection(host='localhost', port=6379, dbid=None, reconnect=True,
                charset="utf-8", password=None,
                connectTimeout=None, replyTimeout=None, convertNumbers=True):
    return makeConnection(host, port, dbid, 1, reconnect, False,
                          charset, password, connectTimeout, replyTimeout,
                          convertNumbers)


def lazyConnection(host='localhost', port=6379, dbid=None, reconnect=True,
                   charset="utf-8", password=None,
                   connectTimeout=None, replyTimeout=None, convertNumbers=True):
    return makeConnection(host, port, dbid, 1, reconnect, True,
                          charset, password, connectTimeout, replyTimeout,
                          convertNumbers)


def ConnectionPool(host='localhost', port=6379, dbid=None,
                   poolsize=10, reconnect=True, charset="utf-8", password=None,
                   connectTimeout=None, replyTimeout=None,
                   convertNumbers=True):
    return makeConnection(host, port, dbid, poolsize, reconnect, False,
                          charset, password, connectTimeout, replyTimeout,
                          convertNumbers)


def lazyConnectionPool(host='localhost', port=6379, dbid=None,
                       poolsize=10, reconnect=True, charset="utf-8",
                       password=None, connectTimeout=None, replyTimeout=None,
                       convertNumbers=True):
    return makeConnection(host, port, dbid, poolsize, reconnect, True,
                          charset, password, connectTimeout, replyTimeout,
                          convertNumbers)