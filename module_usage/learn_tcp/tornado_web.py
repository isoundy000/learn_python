# -*- encoding: utf-8 -*-
'''
Created on 2018年5月2日

@author: houguangdong
'''

# 这篇文章的目的在于对Tornado这个异步服务器软件的底层进行一番探索。我采用自底向上的方式进行介绍，从轮询开始，向上一直到应用层，指出我认为有趣的部分。
# 
# 所以，如果你有打算要阅读Tornado这个web框架的源码，又或者是你对一个异步web服务器是如何工作的感兴趣，我可以在这成为你的指导。
# 
# 通过阅读这篇文章，你将可以：
# 
# 自己写一个 Comet 架构程序的服务器端部分，即使你是从拷贝别人的代码开始。
# 如果你想在Tornado框架上做开发，通过这篇文章你将更好的理解Tornado web框架。
# 在Tornado和Twisted的争论上，你将更有见解。
#  
# 
# 介绍
# 假设你还不知道Tornado是什么也不知道为什么应该对它感兴趣，那我将用简短的话来介绍Tornado这个项目。如果你已经对它有了兴趣，你可以跳去看下一节内容。
# 
# Tornado 是一个用Python编写的异步HTTP服务器，同时也是一个web开发框架。该框架服务于 FriendFeed 网站，最近Facebook也在使用它。FriendFeed网站有用户数多和应用实时性强的特点，所以性能和可扩展性是很受重视的。由于现在它是开源的了（这得归功于Facebook），我们可以彻底的对它是如何工作的一探究竟。
# 
# 我觉得对非阻塞IO (nonblocking IO)或异步IO (asynchronous IO, AIO)很有必要谈一谈。如果你已经完全知道他们是什么了，可以跳去看下一节。我尽可能的使用一些例子来说明它们是什么。
# 
# 让我们假设你正在写一个需要请求一些来自其他服务器上的数据（比如数据库服务，再比如新浪微博的open api）的应用程序，然后呢这些请求将花费一个比较长的时间，假设需要花费5秒钟。大多数的web开发框架中处理请求的代码大概长这样：
# 
# def handler_request(self, request):
#     answ = self.remote_server.query(request) # this takes 5 seconds
#     request.write_response(answ)
# 如果这些代码运行在单个线程中，你的服务器只能每5秒接收一个客户端的请求。在这5秒钟的时间里，服务器不能干其他任何事情，所以，你的服务效率是每秒0.2个请求，哦，这太糟糕了。
# 
# 当然，没人那么天真，大部分服务器会使用多线程技术来让服务器一次接收多个客户端的请求，我们假设你有20个线程，你将在性能上获得20倍的提高，所以现在你的服务器效率是每秒接受4个请求，但这还是太低了，当然，你可以通过不断地提高线程的数量来解决这个问题，但是，线程在内存和调度方面的开销是昂贵的，我怀疑如果你使用这种提高线程数量的方式将永远不可能达到每秒100个请求的效率。
# 
# 如果使用AIO，达到每秒上千个请求的效率是非常轻松的事情。服务器请求处理的代码将被改成这样：
# 
# def handler_request(self, request):
#     self.remote_server.query_async(request, self.response_received)
# 
# def response_received(self, request, answ): # this is called 5 seconds later
#     request.write(answ)
# AIO的思想是当我们在等待结果的时候不阻塞，转而我们给框架一个回调函数作为参数，让框架在有结果的时候通过回调函数通知我们。这样，服务器就可以被解放去接受其他客户端的请求了。
# 
# 然而这也是AIO不太好的地方：代码有点不直观了。还有，如果你使用像Tornado这样的单线程AIO服务器软件，你需要时刻小心不要去阻塞什么，因为所有本该在当前返回的请求都会像上述处理那样被延迟返回。
# 
# 关于异步IO，比当前这篇过分简单的介绍更好的学习资料请看 The C10K problem 。
# 
# 源代码
# 该项目由 github 托管，你可以通过如下命令获得，虽然通过阅读这篇文章你也可以不需要它是吧。
# 
# $ git clone git://github.com/facebook/tornado.git
# 在 tornado 的子目录中，每个模块都应该有一个.py文件，你可以通过检查他们来判断你是否从已经从代码仓库中完整的迁出了项目。在每个源代码的文件中，你都可以发现至少一个大段落的用来解释该模块的doc string，doc string中给出了一到两个关于如何使用该模块的例子。
# 
# IOLoop模块
# 让我们通过查看 ioloop.py 文件直接进入服务器的核心。这个模块是异步机制的核心。它包含了一系列已经打开的文件描述符和每个描述符的处理器（handlers）。它的功能是选择那些已经准备好读写的文件描述符，然后调用它们各自的处理器（一种IO多路复用的实现，其实就是socket众多IO模型中的select模型，在Java中就是NIO，译者注）。
# 
# 可以通过调用 add_handler() 方法将一个socket加入 IOLoop 中：
# 
# def add_handler(self, fd, handler, events):
#     """Registers the given handler to receive the given events for fd."""
#     self._handlers[fd] = handler
#     self._impl.register(fd, events | self.ERROR)
# _handlers 这个字典类型的变量保存着文件描述符到当该文件描述符准备好时需要调用的方法的映射（在Tornado中，该方法被称为处理器）。然后，文件描述符被注册到epoll列表中。Tornado关心三种类型的事件： READ ， WRITE和 ERROR 。正如你所见， ERROR 是默认为你自动添加的。
# 
# self._impl 是 select.epoll() 和 selet.select() 两者中的一个。我们稍后将看到Tornado是如何在它们之间进行选择的。
# 
# 现在让我们来看看实际的主循环，不知何故，这段代码被放在了 start() 方法中：
# 
# def start(self):
#     """Starts the I/O loop.
#     The loop will run until one of the I/O handlers calls stop(), which
#     will make the loop stop after the current event iteration completes.
#     """
#     self._running = True
#     while True:
# 
#     [ ... ]
# 
#         if not self._running:
#             break
# 
#         [ ... ]
# 
#         try:
#             event_pairs = self._impl.poll(poll_timeout)
#         except Exception, e:
#             if e.args == (4, "Interrupted system call"):
#                 logging.warning("Interrupted system call", exc_info=1)
#                 continue
#             else:
#                 raise
# 
#         # Pop one fd at a time from the set of pending fds and run
#         # its handler. Since that handler may perform actions on
#         # other file descriptors, there may be reentrant calls to
#         # this IOLoop that update self._events
#         self._events.update(event_pairs)
#         while self._events:
#             fd, events = self._events.popitem()
#             try:
#                 self._handlers[fd](fd, events)
#             except KeyboardInterrupt:
#                 raise
#             except OSError, e:
#                 if e[0] == errno.EPIPE:
#                     # Happens when the client closes the connection
#                     pass
#                 else:
#                     logging.error("Exception in I/O handler for fd %d",
#                                   fd, exc_info=True)
#             except:
#                 logging.error("Exception in I/O handler for fd %d",
#                               fd, exc_info=True)
# poll() 方法返回一个形如 (fd: events) 的键值对，并赋值给 event_pairs 变量。由于当一个信号在任何一个事件发生前到来时，C函数库中的 poll() 方法会返回 EINTR （实际是一个值为4的数值），所以"Interrupted system call"这个特殊的异常需要被捕获。更详细的请查看 man poll 。
# 
# 在内部的while循环中， event_pairs 中的内容被一个一个的取出，然后相应的处理器会被调用。pipe异常在这里默认不进行处理。为了让这个类适应更一般的情况，在http处理器中处理这个异常是一个更好的方案，但是选择现在这样处理或许是因为更容易一些。
# 
# 注释中解释了为什么使用字典的 popitem() 方法，而不是使用更普遍一点的下面这种做法：
# 
# for fd, events in self._events.items():
# 原因很简单，在主循环期间，这个 _events 字典变量可能会被处理器所修改。比如 remove_handler() 处理器。这个方法把 fd 从 _events 字典中取出，所以即使 fd 被选择到了，它的处理器也不会被调用。
# 
# def remove_handler(self, fd):
#     """Stop listening for events on fd."""
#     self._handlers.pop(fd, None)
#     self._events.pop(fd, None)
#     try:
#         self._impl.unregister(fd)
#     except OSError:
#         logging.debug("Error deleting fd from IOLoop", exc_info=True)
# （意义不大的）循环结束技巧
# 怎么让这个主循环停止是很有技巧性的。 self._running 变量被用来在运行时从主循环中跳出，处理器可以通过调用stop() 方法把它设置为 False 。通常情况下，这就能让主循环停止了，但是 stop() 方法还能被一个信号处理器所调用，所以，如果 1) 主循环正阻塞在 poll() 方法处， 2) 服务端没有接收到任何来自客户端的请求， 3) 信号没有被OS投递到正确的线程中，你将不得不等待 poll() 方法出现超时情况后才会返回。考虑到这些情况并不时常发生，还有 poll() 方法的默认超时时间只不过是0.2秒，所以这种让主循环停止的方式还算过得去。
# 
# 但不管怎样，Tornado的开发者为了让主循环停止，还是额外的创建了一个没有名字的管道和对应的处理器，并把管道的一端放在了轮询文件描述符列表中。当需要停止时，在管道的另一端随便写点什么，这能高效率的唤醒主循环在poll() 方法处的阻塞（貌似Java NIO的Windows实现就用了这种方法，译者注）。这里节选了一些代码片段：
# 
# def __init__(self, impl=None):
# 
#     [...]
# 
#     # Create a pipe that we send bogus data to when we want to wake
#     # the I/O loop when it is idle
#     r, w = os.pipe()
#     self._set_nonblocking(r)
#     self._set_nonblocking(w)
#     self._waker_reader = os.fdopen(r, "r", 0)
#     self._waker_writer = os.fdopen(w, "w", 0)
#     self.add_handler(r, self._read_waker, self.WRITE)
# 
# def _wake(self):
#     try:
#         self._waker_writer.write("x")
#     except IOError:
#         pass
# 实际上，上述代码中存在一个bug：那个只读文件描述符 r ，虽然是用来读的，但在注册时却附加上了 WRITE 类型的事件，这将导致该注册实际不会被响应。正如我先前所说的，用不用专门找个方法其实没什么的，所以我对他们没有发现这个方法不起作用的事实并不感到惊讶。我在 mail list 中报告了这个情况，但是尚未收到答复。
# 
# 定时器
# 另外一个在 IOLoop 模块中很有特点的设计是对定时器的简单实现。一系列的定时器会被以是否过期的形式来维护和保存，这用到了python的 bisect 模块：
# 
# def add_timeout(self, deadline, callback):
#     """Calls the given callback at the time deadline from the I/O loop."""
#     timeout = _Timeout(deadline, callback)
#     bisect.insort(self._timeouts, timeout)
#     return timeout
# 在主循环中，所有过期了的定时器的回调会按照过期的顺序被触发。 poll() 方法中的超时时间会动态的进行调整，调整的结果就是如果没有新的客户端请求，那么下一个定时器就好像没有延迟一样的被触发（意思是如果没有新的客户端的请求， poll() 方法将被阻塞直到超时，这个超时时间的设定会根据下一个定时器与当前时间之间的间隔进行调整，调整后，超时的时间会等同于距离下一个定时器被触发的时间，这样在 poll() 阻塞完后，下一个定时器刚好过期，译者注）。
# 
# self._running = True
# while True:
#     poll_timeout = 0.2
# 
#     [ ... ]
#     if self._timeouts:
#         now = time.time()
#         while self._timeouts and self._timeouts[0].deadline <= now:
#             timeout = self._timeouts.pop(0)
#             self._run_callback(timeout.callback)
#         if self._timeouts:
#             milliseconds = self._timeouts[0].deadline - now
#             poll_timeout = min(milliseconds, poll_timeout)
# 
# [ ... poll ]
# 选择select方案
# 让我们现在快速的看一下poll和select这两种select方案的实现代码。Python已经在版本2.6的标准库中支持了epoll，你可以通过在 select 模块上使用 hasattr() 方法检测当前Python是否支持epoll。如果python版本小于2.6，Tornado将用它自己的基于C的epoll模块。你可以在 tornado/epoll.c 文件中找到它源代码。如果最后这也不行（因为epoll不是每个Linux都有的），它将回退到select。 _Select 和 _EPoll 类是模拟 select.epoll API的封装。在你做性能测试之前，请确定你能使用 epoll ，因为 select 在有大量文件描述符情况下的效率非常低。
# 
# # Choose a poll implementation. Use epoll if it is available, fall back to
# # select() for non-Linux platforms
# if hasattr(select, "epoll"):
#     # Python 2.6+ on Linux
#     _poll = select.epoll
# else:
#     try:
#         # Linux systems with our C module installed
#         import epoll
#         _poll = _EPoll
#     except:
#         # All other systems
#         import sys
#         if "linux" in sys.platform:
#             logging.warning("epoll module not found; using select()")
#         _poll = _Select
# 通过上述阅读，我们的介绍已经涵盖了大部分 IOLoop 模块。正如广告中介绍的那样，它是一段优雅而又简单的代码。
# 
# 从sockets到流
# 让我们来看看 IOStream 模块。它的目的是提供一个对非阻塞sockets的轻量级抽象，它提供了三个方法：
# 
# read_until() ，从socket中读取直到遇到指定的字符串。这为在读取HTTP头时遇到空行分隔符自动停止提供了方便。
# read_bytes() ，从socket中读取指定数量的字节。这为读取HTTP消息的body部分提供了方便。
# write() ，将指定的buffer写入socket并持续监测直到这个buffer被发送。
# 所有上述的方法都可以通过异步方式在它们完成时触发回调函数。
# 
# write() 方法提供了将调用者提供的数据加以缓冲直到 IOLoop 调用了它的处理器的功能，因为到那时候就说明socket已经为写数据做好了准备：
# 
# def write(self, data, callback=None):
#     """Write the given data to this stream.
#     If callback is given, we call it when all of the buffered write
#     data has been successfully written to the stream. If there was
#     previously buffered write data and an old write callback, that
#     callback is simply overwritten with this new callback.
#     """
#     self._check_closed()
#     self._write_buffer += data
#     self._add_io_state(self.io_loop.WRITE)
#     self._write_callback = callback
# 该方法只是用 socket.send() 来处理 WRITE 类型的事件，直到 EWOULDBLOCK 异常发生或者buffer被发送完毕：
# 
# def _handle_write(self):
#     while self._write_buffer:
#         try:
#             num_bytes = self.socket.send(self._write_buffer)
#             self._write_buffer = self._write_buffer[num_bytes:]
#         except socket.error, e:
#             if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
#                 break
#             else:
#                 logging.warning("Write error on %d: %s",
#                                 self.socket.fileno(), e)
#                 self.close()
#                 return
#     if not self._write_buffer and self._write_callback:
#         callback = self._write_callback
#         self._write_callback = None
#         callback()
# 读数据的方法和上述过程正好相反。读事件的处理器持续读取数据直到缓冲区被填满为止。这就意味着要么读取指定数量的字节（如果调用的是 read_bytes() ），要么读取的内容中包含了指定的分隔符（如果调用的是 read_util()）:
# 
# def _handle_read(self):
#     try:
#         chunk = self.socket.recv(self.read_chunk_size)
#     except socket.error, e:
#         if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
#             return
#         else:
#             logging.warning("Read error on %d: %s",
#                             self.socket.fileno(), e)
#             self.close()
#             return
#     if not chunk:
#         self.close()
#         return
#     self._read_buffer += chunk
#     if len(self._read_buffer) >= self.max_buffer_size:
#         logging.error("Reached maximum read buffer size")
#         self.close()
#         return
#     if self._read_bytes:
#         if len(self._read_buffer) >= self._read_bytes:
#             num_bytes = self._read_bytes
#             callback = self._read_callback
#             self._read_callback = None
#             self._read_bytes = None
#             callback(self._consume(num_bytes))
#     elif self._read_delimiter:
#         loc = self._read_buffer.find(self._read_delimiter)
#         if loc != -1:
#             callback = self._read_callback
#             delimiter_len = len(self._read_delimiter)
#             self._read_callback = None
#             self._read_delimiter = None
#             callback(self._consume(loc + delimiter_len))
# 如下所示的 _consume() 方法是为了确保在要求的返回值中不会包含多余的来自流的数据，并且保证后续的读操作会从当前字节的下一个字节开始：
# 
# def _consume(self, loc):
#     result = self._read_buffer[:loc]
#     self._read_buffer = self._read_buffer[loc:]
#     return result
# 还值得注意的是在上述 _handle_read() 方法中read buffer的上限—— self.max_buffer_size 。默认值是100MB，这似乎对我来说是有点大了。举个例子，如果一个攻击者和服务端建立了100个连接，并持续发送不带头结束分隔符的头信息，那么Tornado需要 10GB的内存 来处理这些请求。即使内存ok，这种数量级数据的复制操作（比如像上述_consume() 方法中的代码）很可能使服务器超负荷。我们还注意到在每次迭代中 _handle_read() 方法是如何在这个buffer中搜索分隔符的，所以如果攻击者以小块形式发送大量的数据，服务端不得不做很多次搜索工作。归根结底，你应该想要调整这个参数，除非你真的需要接收这么多的数据并且能满足硬件条件。
# 
# HTTP 服务器
# 有了 IOLoop 模块和 IOStream 模块的帮助，写一个异步的HTTP服务器只差一步之遥，这一步就在 httpserver.py 中完成。
# 
# HTTPServer 类它自己只负责处理将接收到的新连接的socket添加到 IOLoop 中。该监听型的socket自己也是 IOLoop 的一部分，正如在 listen() 方法中见到的那样：
# 
# def listen(self, port, address=""):
#     assert not self._socket
#     self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
#     flags = fcntl.fcntl(self._socket.fileno(), fcntl.F_GETFD)
#     flags |= fcntl.FD_CLOEXEC
#     fcntl.fcntl(self._socket.fileno(), fcntl.F_SETFD, flags)
#     self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     self._socket.setblocking(0)
#     self._socket.bind((address, port))
#     self._socket.listen(128)
#     self.io_loop.add_handler(self._socket.fileno(), self._handle_events,
#                              self.io_loop.READ)
# 除了绑定给定的地址和端口外，上述代码还设置了"close on exec"和"reuse address"这两个标志位。前者在应用程序创建子进程的时候特别有用。在这种情况下，我们不想让套接字保持打开的状态。后者用来避免在服务器重启的时候发生“该地址已被使用”这种错误时很有用。
# 
# 正如你所见到的，后备连接所允许的最大数目是128。这意味着如果有128个连接正在等待被接受，那么直到服务器有时间将前面128个连接中的某几个被接受了，新的连接都将被拒绝。我建议你在做性能测试的时候将该参数调高，因为当新的连接被抛弃的时候将直接影响你做测试的准确性。
# 
# 在上述代码中注册的 _handle_events() 处理器用来接受新连接，并创建相关的 IOStream 对象和初始化一个HTTPConnection 对象， HTTPConnection 对象负责处理剩下的交互部分：
# 
# def _handle_events(self, fd, events):
#     while True:
#         try:
#             connection, address = self._socket.accept()
#         except socket.error, e:
#             if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
#                 return
#             raise
#         try:
#             stream = iostream.IOStream(connection, io_loop=self.io_loop)
#             HTTPConnection(stream, address, self.request_callback,
#                            self.no_keep_alive, self.xheaders)
#         except:
#             logging.error("Error in connection callback", exc_info=True)
# 可以看到这个方法在一次迭代中接受了所有正在等待处理的连接。也就是说直到 EWOULDBLOCK 异常发生时 while True循环才会退出，这也就意味着当前没有需要接受的连接了。
# 
# HTTP头的部分的解析工作开始于 HTTPConnection 类的构造函数 __init__() ：
# 
# def __init__(self, stream, address, request_callback, no_keep_alive=False,
#              xheaders=False):
#     self.stream = stream
#     self.address = address
#     self.request_callback = request_callback
#     self.no_keep_alive = no_keep_alive
#     self.xheaders = xheaders
#     self._request = None
#     self._request_finished = False
#     self.stream.read_until("rnrn", self._on_headers)
# 如果你很想知道 xheaders 参数的意义，请看这段注释：
# 
#  如果 xheaders 为 True ，我们将支持把所有请求的HTTP头解析成X-Real-Ip和X-Scheme格式，而原先我们将HTTP头解析成remote IP和HTTP scheme格式。这种格式的HTTP头在Tornado运行于反向代理或均衡负载服务器的后端时将非常有用。
# _on_headers() 回调函数实际用来解析HTTP头，并在有请求内容的情况下通过使用 read_bytes() 来读取请求的内容部分。 _on_request_body() 回调函数用来解析 POST 的参数并调用应用层提供的回调函数：
# 
# def _on_headers(self, data):
#     eol = data.find("rn")
#     start_line = data[:eol]
#     method, uri, version = start_line.split(" ")
#     if not version.startswith("HTTP/"):
#         raise Exception("Malformed HTTP version in HTTP Request-Line")
#     headers = HTTPHeaders.parse(data[eol:])
#     self._request = HTTPRequest(
#         connection=self, method=method, uri=uri, version=version,
#         headers=headers, remote_ip=self.address[0])
# 
#     content_length = headers.get("Content-Length")
#     if content_length:
#         content_length = int(content_length)
#         if content_length > self.stream.max_buffer_size:
#             raise Exception("Content-Length too long")
#         if headers.get("Expect") == "100-continue":
#             self.stream.write("HTTP/1.1 100 (Continue)rnrn")
#         self.stream.read_bytes(content_length, self._on_request_body)
#         return
# 
#     self.request_callback(self._request)
# 
# def _on_request_body(self, data):
#     self._request.body = data
#     content_type = self._request.headers.get("Content-Type", "")
#     if self._request.method == "POST":
#         if content_type.startswith("application/x-www-form-urlencoded"):
#             arguments = cgi.parse_qs(self._request.body)
#             for name, values in arguments.iteritems():
#                 values = [v for v in values if v]
#                 if values:
#                     self._request.arguments.setdefault(name, []).extend(
#                         values)
#         elif content_type.startswith("multipart/form-data"):
#             boundary = content_type[30:]
#             if boundary: self._parse_mime_body(boundary, data)
#     self.request_callback(self._request)
# 将结果写回客户端的工作在 HTTPRequest 类中处理，你可以在上面的 _on_headers() 方法中看到具体的实现。HTTPRequest 类仅仅将写回的工作代理给了stream对象。
# 
# 
# def write(self, chunk):
#     assert self._request, "Request closed"
#     self.stream.write(chunk, self._on_write_complete)
# 未完待续？
# 通过这篇文章，我已经涵盖了从socket到应用层的所有方面。这应该能给你关于Tornado是如何工作的一个清晰的理解。总之，我认为Tornado的代码是非常友好的，我希望你也这样认为。
# 
# Tornado框架还有很大一部分我们没有探索，比如 web.py 这个实际与你应用打交道的模块，又或者是 template engine 。如果我有足够兴趣的话，我也会介绍这些部分。可以通过订阅我的 RSS feed 来鼓励我。