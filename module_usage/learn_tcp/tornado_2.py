# -*- encoding: utf-8 -*-
'''
Created on 2018年5月2日

@author: houguangdong
'''

# Tornado是很优秀的非阻塞式服务器，我们一般用它来写Web 服务器，据说知乎就是用Tornado写的。
# 为了更好的用Tornado来编写程序，用了点时间把它的源码详细阅读了一下。主要关注的是Tornado如何实现的异步Server和异步Client。这里我先把分析异步client时跟踪源码的记录整理之后放上来，便于以后回忆和翻阅。
#  
# 读者可以通过我这篇文章作为阅读Tornado源码的一个参考，如果你希望比较透彻的了解Tornado，切记不要放过任何你觉得有疑问的地方，实在不懂的部分，可以先放过，之后再回头儿看。
#  
# 如果对tornado源码不是很了解，可以先看一下另一篇文章：
# http://yunjianfei.iteye.com/blog/2185476
# 
#  
# 通过详细阅读理解Tornado的源码，你将会获得以下收获：
# 1. 这是一个绝佳的学习python的机会，你会接触到generator/yield , with statment, functools.partial,  concurrent.futures 等等很多平时较少接触到的只是
# 2. 可以更好的通过tornado来编写异步Server以及client
# 3. 更好的理解epoll，ET/LT相关知识
#  
# 本文可以协助更好的去阅读理解tornado的源码，提供一个跟踪理解源码的思路和顺序。
#  
# 从一个例子开始
# 
#  
# 注意：在源码跟踪过程中，一共有51个步骤，请务必按照步骤，打开你手中对应的源码，进行跟踪分析。
#  
# 以下是一个异步客户端的例子，作用是获取www.baidu.com首页的内容。那么开始我们的源码跟踪之旅。
# 在开始跟踪前，请准备好tornado源码，本文中的源码均只截取了部分关键性的代码。
#  
# 文件名： async.py
#  
# Python代码  收藏代码
# #!/usr/bin/env python2.7  
# # -*- coding: utf-8 -*-  
# from tornado import ioloop, httpclient, gen  
# from tornado.gen import Task  
# import pdb, time, logging  
# #Init logging  
# def init_logging():  
#     logger = logging.getLogger()  
#     logger.setLevel(logging.DEBUG)  
#     sh = logging.StreamHandler()  
#     formatter = logging.Formatter('%(asctime)s -%(module)s:%(filename)s-L%(lineno)d-%(levelname)s: %(message)s')  
#     sh.setFormatter(formatter)  
#   
#     logger.addHandler(sh)  
#     logging.info("Current log level is : %s", logging.getLevelName(logger.getEffectiveLevel()))  
#   
# init_logging()  
#   
# #pdb.set_trace()  
#  
# @gen.coroutine #注意这里是一个装饰器，是实现异步client的关键  
# def download(url):  
#     http_client = httpclient.AsyncHTTPClient()  
#   
#     #6. 执行http_client.fetch(url)，然后退出download函数，等待下次步骤5中的gen.next或者gen.send调用  
#     #51. 获取从www.baidu.com返回的响应,赋值给response  
#     response = yield http_client.fetch(url)   
#     print 'response.length =', len(response.body)  
#     ioloop.IOLoop.instance().stop()  
#   
# future = download("http://www.baidu.com/")  #0. 开始源码分析  
# print future  
# logging.info("****start ioloop*************")  
# ioloop.IOLoop.instance().start() #18. 启动ioloop  
#  
#  
#    gen.py:
# Python代码  收藏代码
# def coroutine(func):  
#     @functools.wraps(func)  
#     def wrapper(*args, **kwargs):  
#         future = TracebackFuture()  
#           
#         #1.返回download函数入口点（函数类型为generator）  
#         result = func(*args, **kwargs)    
#         if isinstance(result, types.GeneratorType):  
#             def final_callback(value):  
#                 deactivate()  
#                 future.set_result(value)  
#             runner = Runner(result, final_callback)  
#               
#             #2.启动generator调用http_client.fetch(url)  
#             runner.run()   
#             return future  
#     return wrapper  
#   
# class Runner(object):  
#     def set_result(self, key, result):  
#         self.results[key] = result  
#         self.run() #47. 调用run  
#       
#     def is_ready(self, key):  
#         if key not in self.pending_callbacks:  
#             raise UnknownKeyError("key %r is not pending" % (key,))  
#         #48.2 因46.步中调用set_result设定了对应的result，所以返回True  
#         return key in self.results   
#           
#     def result_callback(self, key):  
#         def inner(*args, **kwargs):  
#             if kwargs or len(args) > 1:  
#                 result = Arguments(args, kwargs)  
#             elif args:  
#                 result = args[0]  
#             else:  
#                 result = None  
#             self.set_result(key, result) #46. 调用set_result  
#         return wrap(inner)  #这里的wrap是stack_context.py中的wrap  
#       
#     def register_callback(self, key):  
#         if key in self.pending_callbacks:  
#             raise KeyReuseError("key %r is already pending" % (key,))  
#         self.pending_callbacks.add(key)  
#           
#     def run(self):  
#         while True:  
#             #3.第一次调用的是_NullYieldPoint中的is_ready，返回True  
#             #48. 此时的yield_point是17.2步中self.yield_point = yielded设置的，返回True，参照48.1  
#             if not self.yield_point.is_ready():                          
#                 return  
#             #4.第一次调用的是_NullYieldPoint中的get_result，返回None  
#             #49. 获取46步中设定的result（即从www.baidu.com返回的响应）  
#             next = self.yield_point.get_result()   
#                                                    
#             try:  
#             #5.开始执行generator函数（即download），执行http_client.fetch(url)后跳出download，等待下一次调用gen.send或者gen.next  
#             #50.给第6步的response变量设置从www.baidu.com返回的响应  
#                 yielded = self.gen.send(next)                           
#             except StopIteration:  
#                 return  
#                   
#             if isinstance(yielded, list):  
#                 yielded = Multi(yielded)  
#             elif isinstance(yielded, Future): #注意：这里的yielded是7.1返回的Future对象  
#                 #17.1  生成YieldFuture对象，参数为7.1返回的Future对象  
#                 yielded = YieldFuture(yielded)      
#               
#             if isinstance(yielded, YieldPoint): #YieldFuture的父类是YieldPoint  
#                 self.yield_point = yielded  
#                 #17.2 调用start函数，注册result_callback（注意17.2.1和17.2.2）  
#                 self.yield_point.start(self)   
#                   
# class YieldFuture(YieldPoint): #YieldFuture的父类是YieldPoint  
#     def __init__(self, future, io_loop=None):  
#         self.future = future  
#         self.io_loop = io_loop or IOLoop.current()  
#   
#     def start(self, runner):  
#         self.runner = runner  
#         self.key = object()  
#         #17.2.1 将YieldFuture对象key追加到pending_callbacks中  
#         runner.register_callback(self.key)  
#           
#         #17.2.2 在ioloop中注册一个future，调用concurrent.py中add_done_callback，用于最终返回www.baidu.com的响应，请查看17.2.3  
#         self.io_loop.add_future(self.future, runner.result_callback(self.key))  
#              
#     def is_ready(self):  
#         #48.1 调用runner中的is_ready， key为YieldFuture对象key，参照48.2  
#         return self.runner.is_ready(self.key)   
#   
#     def get_result(self):  
#         return self.runner.pop_result(self.key).result()  
#  
# httpclient.py
# Python代码  收藏代码
# class AsyncHTTPClient(Configurable):  
#     def fetch(self, request, callback=None, **kwargs):  
#         request.headers = httputil.HTTPHeaders(request.headers)  
#         #根据参数"http://www.baidu.com/"生成request对象  
#         request = _RequestProxy(request, self.defaults)  
#           
#         #初始化一个Future对象，Future参照：https://docs.python.org/3/library/concurrent.futures.html  
#         future = Future()   
#           
#         #将http://www.baidu.com/返回的消息设置给download函数中的response参数  
#         def handle_response(response):  
#             if response.error:  
#                 future.set_exception(response.error)  
#             else:  
#                 #44. 通过set_result来给第6步中的response变量赋值， 参照44.1  
#                 future.set_result(response)   
#                   
#         self.fetch_impl(request, handle_response)   #7.调用fetch的实现函数  
#         return future  #7.1 注意fetch返回的是Future对象，这里需要特别关注  
#  
#  simple_httpclient.py
# Python代码  收藏代码
# class SimpleAsyncHTTPClient(AsyncHTTPClient):  
#     def fetch_impl(self, request, callback):  
#         self.queue.append((request, callback))  
#         self._process_queue()  
#   
#     def _process_queue(self):  
#         with stack_context.NullContext():  
#             while self.queue and len(self.active) < self.max_clients:  
#                 request, callback = self.queue.popleft()  
#                 key = object()  
#                 self.active[key] = (request, callback)  
#                 release_callback = functools.partial(self._release_fetch, key)  
#                 self._handle_request(request, release_callback, callback)  
#   
#     def _handle_request(self, request, release_callback, final_callback):  
#         #8.调用_HTTPConnection，准备连接http://www.baidu.com/  
#         _HTTPConnection(self.io_loop, self, request, release_callback,      
#                         final_callback, self.max_buffer_size, self.resolver)  
#                           
# class _HTTPConnection(object):  
#     def __init__(self, io_loop, client, request, release_callback,  
#                  final_callback, max_buffer_size, resolver):  
#   
#         #这里的final_callback就是步骤7中的handle_response  
#         self.final_callback = final_callback    
#         with stack_context.ExceptionStackContext(self._handle_exception):  
#             #9.调用Resolver中的resolve函数，参见后面的代码介绍  
#             self.resolver.resolve(host, port, af, callback=self._on_resolve)   
#       
#     def _on_resolve(self, addrinfo):  
#         self.stream = self._create_stream(addrinfo)  
#         timeout = min(self.request.connect_timeout, self.request.request_timeout)  
#         if timeout:  
#             self._timeout = self.io_loop.add_timeout(  
#                 self.start_time + timeout,  
#                 stack_context.wrap(self._on_timeout))  #设置timeout的callback：_on_timeout  
#         self.stream.set_close_callback(self._on_close) #设置close时的callback: _on_close  
#         sockaddr = addrinfo[0][1]  
#           
#         #20. 调用iostream中的connect函数，建立和www.baidu.com的连接  
#         self.stream.connect(sockaddr, self._on_connect,    
#                             server_hostname=self.parsed_hostname)  
#     def _on_connect(self):  
#         self._remove_timeout()  
#         if self.request.request_timeout:  
#             self._timeout = self.io_loop.add_timeout(  
#                 self.start_time + self.request.request_timeout,  
#                 stack_context.wrap(self._on_timeout))  
#         ##这里都是生成request的相关代码，省略  
#         if self.request.body is not None:  
#             request_str += self.request.body  
#         self.stream.set_nodelay(True)  
#         self.stream.write(request_str)   
#           
#         #29. 调用iostream.py中的write函数，将request数据追加到_write_buffer中，并发送请求（查看29.1和29.2）  
#         #30.调用iostream.py中的read_until_regex函数，主要完成以下几件事儿：  
#             1. 设置_read_callback为_on_headers函数 （参照30.1和30.2）  
#             2. 设置_read_regex参数  
#         self.stream.read_until_regex(b"\r?\n\r?\n", self._on_headers)      
#                                                                    
#                                                                    
#     def _on_headers(self, data):  
#         if self.headers.get("Transfer-Encoding") == "chunked":  
#             self.chunks = []  
#               
#             #34. iostream.py中的read_until，设置_read_callback为_on_chunk_length  
#                  参照34.1和34.2  
#             self.stream.read_until(b"\r\n", self._on_chunk_length)    
#                                                                            
#         elif content_length is not None:  
#             self.stream.read_bytes(content_length, self._on_body)  
#         else:  
#             self.stream.read_until_close(self._on_body)      
#               
#     def _on_chunk_length(self, data):  
#         length = int(data.strip(), 16)  
#         if length == 0:  
#             #42. 调用_on_body函数，查看42.1， 42.2等  
#             self._on_body(b''.join(self.chunks))    
#         else:  
#             self.stream.read_bytes(length + 2,  # chunk ends with \r\n  
#                          self._on_chunk_data) #38. 注册_on_chunk_data回调到ioloop          
#     def _on_chunk_data(self, data):  
#         assert data[-2:] == b"\r\n"  
#         chunk = data[:-2]  
#         if self._decompressor:  
#             chunk = self._decompressor.decompress(chunk)  
#         if self.request.streaming_callback is not None:  
#             self.request.streaming_callback(chunk)  
#         else:  
#             self.chunks.append(chunk)  
#               
#         #40. 注册_on_chunk_length回调到ioloop      
#         self.stream.read_until(b"\r\n", self._on_chunk_length)      
#           
#     def _run_callback(self, response):  
#         logging.info("--in _run_callback")  
#         self._release()  
#         if self.final_callback is not None:  
#             final_callback = self.final_callback  
#             self.final_callback = None  
#             self.io_loop.add_callback(final_callback, response)  
#               
#     def _on_body(self, data):  
#         self._remove_timeout()  
#         response = HTTPResponse(original_request,  
#                                 self.code, reason=self.reason,  
#                                 headers=self.headers,  
#                                 request_time=self.io_loop.time() - self.start_time,  
#                                 buffer=buffer,  
#                                 effective_url=self.request.url)  
#         #42.1 将final_callback添加到ioloop（final_callback是第9步之前设定的AsyncHTTPClient中的handle_response）  
#         self._run_callback(response)    
#         #42.2 资源回收、释放fd，并将_on_close注册到ioloop  
#         self._on_end_request()      
#       
#     def _on_end_request(self):  
#         self.stream.close()         
#  
# netutil.py
# Python代码  收藏代码
# class Resolver(Configurable):  
#     @classmethod  
#     def configurable_default(cls):  
#         return BlockingResolver  #这里设置默认的Resolver为BlockingResolver  
#           
# class BlockingResolver(ExecutorResolver): #BlockingResolver继承了ExecutorResolver  
#     def initialize(self, io_loop=None):  
#         super(BlockingResolver, self).initialize(io_loop=io_loop)  
# class ExecutorResolver(Resolver):  
#     @run_on_executor  #run_on_executor装饰resolve  
#     def resolve(self, host, port, family=socket.AF_UNSPEC):#第9步中调用的resolve是这里的resolve  
#         addrinfo = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)  
#         results = []  
#         for family, socktype, proto, canonname, address in addrinfo:  
#             results.append((family, address))  
#         return results  #12. 执行resolve，并返回addrinfo结果  
#  
# concurrent.py
# Python代码  收藏代码
# class _DummyFuture(object):  
#     #13. 将步骤12中返回的results设定给future，并设定该future为完成  
#     def set_result(self, result):   
#         self._result = result  
#         self._set_done() #44.1  设置该Future为完成状态，请查看44.2  
#           
#     def _set_done(self):  
#         self._done = True  #设定该future为已经完成  
#           
#         #44.2  _callbacks中存在17.2.3中注册的ioloop中的add_callback 参照44.3  
#         for cb in self._callbacks:   
#             # TODO: error handling  
#             cb(self)  #44.3 运行ioloop中add_callback，参数是gen.py中的result_callback  
#         self._callbacks = None  
#           
#     def add_done_callback(self, fn):  
#         if self._done:  
#             #17. 调用ioloop中的add_callback，将第9步中的_on_resolve函数（参数为步骤12返回的results）注册到callback中  
#             fn(self)  #注意，在看18之前，必须先看17.1    
#         else:  
#             #17.2.3 在Future的_callbacks中追加ioloop中的add_callback(callback, future)函数，  
#               （add_callback中注册的是gen.py中的result_callback）  
#             self._callbacks.append(fn)  
#           
# class DummyExecutor(object):  
#     def submit(self, fn, *args, **kwargs):  
#         future = TracebackFuture()  
#         try:  
#             future.set_result(fn(*args, **kwargs)) #11. fn(*args, **kwargs)#执行的是ExecutorResolver中的resolve函数  
#         except Exception:  
#             future.set_exc_info(sys.exc_info())  
#         return future  # 14.返回future  
#   
# dummy_executor = DummyExecutor()  
#   
# def run_on_executor(fn):  
#     @functools.wraps(fn)  
#     def wrapper(self, *args, **kwargs):  
#         callback = kwargs.pop("callback", None)  #将第9步中的_on_resolve函数作为callback  
#           
#         #10.调用DummyExecutor中的submit函数，提交resolve  
#         future = self.executor.submit(fn, self, *args, **kwargs)   
#         if callback:  
#             #15. 将步骤14中返回的future，和第9步中的_on_resolve作为参数注册到io_loop中的add_future  
#             #注意：future.result()可获取步骤12返回的results  
#             self.io_loop.add_future(future,   
#                                     lambda future: callback(future.result()))   
#         return future  
#     return wrapper  
#  
# ioloop.py
# Python代码  收藏代码
# class PollIOLoop(IOLoop):  
#     def add_future(self, future, callback):  
#         callback = stack_context.wrap(callback)  
#         future.add_done_callback(  #16. 调用future中的add_done_callback函数  
#             lambda future: self.add_callback(callback, future))  
#               
#     def add_callback(self, callback, *args, **kwargs):  
#         with self._callback_lock:  
#             if self._closing:  
#                 raise RuntimeError("IOLoop is closing")  
#             list_empty = not self._callbacks  
#             self._callbacks.append(functools.partial(  
#                 stack_context.wrap(callback), *args, **kwargs))  
#         if list_empty and thread.get_ident() != self._thread_ident:  
#             self._waker.wake()  
#       
#     #23. 添加IOStream中的_handle_events回调，在epoll对象中注册WRITE事件      
#     def add_handler(self, fd, handler, events):   
#         self._handlers[fd] = stack_context.wrap(handler)   
#         self._impl.register(fd, events | self.ERROR)    
#           
#     def start(self):  
#         while True:  
#             poll_timeout = 3600.0  
#   
#             with self._callback_lock:  
#                 callbacks = self._callbacks  
#                 self._callbacks = []  
#             for callback in callbacks:  
#                 #19. 调用17步中注册的simple_httpclient.py中的_on_resolve函数（参数为步骤12返回的results）  
#                 #28.调用27步中注册的simple_httpclient.py 中_on_connect函数  
#                 #33. 调用32中注册的simple_httpclient.py 中的_on_headers函数  
#                 #37. 调用34中注册的simple_httpclient.py 中的_on_chunk_length函数  
#                 #39. 调用38中注册的simple_httpclient.py 中的_on_chunk_data函数    
#                 #41. 调用40中注册的simple_httpclient.py 中的_on_chunk_length函数  
#                 #43. 调用42.1中注册的AsyncHTTPClient.py中的handle_response  
#                 #45. 调用44.3中注册的gen.py中的result_callback  
#                 self._run_callback(callback)    
#   
#                   
#             if self._timeouts:  
#                 now = self.time()  
#                 while self._timeouts:  
#                     if self._timeouts[0].callback is None:  
#                         # the timeout was cancelled  
#                         heapq.heappop(self._timeouts)  
#                         self._cancellations -= 1  
#                     elif self._timeouts[0].deadline <= now:  
#                         timeout = heapq.heappop(self._timeouts)  
#                         self._run_callback(timeout.callback)  
#                     else:  
#                         seconds = self._timeouts[0].deadline - now  
#                         poll_timeout = min(seconds, poll_timeout)  
#                         break  
#                 if (self._cancellations > 512  
#                         and self._cancellations > (len(self._timeouts) >> 1)):  
#                     self._cancellations = 0  
#                     self._timeouts = [x for x in self._timeouts  
#                                       if x.callback is not None]  
#                     heapq.heapify(self._timeouts)  
#                       
#             if self._callbacks:  
#                 poll_timeout = 0.0  
#   
#             if not self._running:  
#                 break  
#             try:  
#                 #24. epoll为水平触发模式，且23步中注册了WRITE事件，poll函数会返回可写事件  
#                 #31. 29.3中注册了READ，29步向www.baidu.com发送请求，接收到响应，触发Read事件  
#                 #35. www.baidu.com继续发送数据，触发Read事件  
#                 event_pairs = self._impl.poll(poll_timeout)   
#                                            
#             except Exception as e:  
#                 if (getattr(e, 'errno', None) == errno.EINTR or  
#                     (isinstance(getattr(e, 'args', None), tuple) and  
#                      len(e.args) == 2 and e.args[0] == errno.EINTR)):  
#                     continue  
#                 else:  
#                     raise  
#             self._events.update(event_pairs)  
#             while self._events:  
#                 fd, events = self._events.popitem()  
#                 try:  
#                     #25. 调用23步中注册的IOStream中的_handle_events函数，events为WRITE  
#                     self._handlers[fd](fd, events)   
#                 except (OSError, IOError) as e:  
#                     if e.args[0] == errno.EPIPE:  
#                         # Happens when the client closes the connection  
#                         pass  
#  
# iostream.py
# Python代码  收藏代码
# class IOStream(BaseIOStream):  
#     def connect(self, address, callback=None, server_hostname=None):  
#         self._connecting = True  #注意：该参数设定为True  
#         try:  
#             self.socket.connect(address) #21.建立和www.baidu.com的连接  
#         except socket.error as e:  
#             if e.args[0] not in (errno.EINPROGRESS, errno.EWOULDBLOCK):  
#                 gen_log.warning("Connect error on fd %d: %s",  
#                                 self.socket.fileno(), e)  
#                 self.close(exc_info=True)  
#                 return  
#         #这里的callback是步骤20的simple_httpclient.py 中_on_connect函数  
#         self._connect_callback = stack_context.wrap(callback)    
#         self._add_io_state(self.io_loop.WRITE)  
#           
#     def _add_io_state(self, state):  
#         if self._state is None:  
#             self._state = ioloop.IOLoop.ERROR | state  
#             with stack_context.NullContext():  
#                 self.io_loop.add_handler(  #22. 在ioloop对象中注册事件回调函数  
#                     self.fileno(), self._handle_events, self._state)  
#         elif not self._state & state:  
#             self._state = self._state | state  
#             self.io_loop.update_handler(self.fileno(), self._state)  
#   
#     def _handle_connect(self):  
#         err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)  
#         if err != 0:  
#             self.close()  
#             return  
#         if self._connect_callback is not None:  
#             #这里的callback是步骤20的simple_httpclient.py 中_on_connect  
#             callback = self._connect_callback   
#             self._connect_callback = None  
#             self._run_callback(callback)   
#         self._connecting = False  #注意： 这里将_connecting设置成为了False  
#      
#   
#     def _run_callback(self, callback, *args):  
#         def wrapper():  
#             self._pending_callbacks -= 1  
#             try:  
#                 callback(*args)  
#             except Exception:  
#                 raise  
#             self._maybe_add_error_listener()  
#   
#         with stack_context.NullContext():  
#             self._pending_callbacks += 1  
#               
#             #27.将simple_httpclient.py 中_on_connect注册到ioloop中的_callbacks中  
#             #32.2.2 将simple_httpclient.py 中的_on_headers函数注册到ioloop中的_callbacks  
#             #34.2.2 将simple_httpclient.py 中的_on_chunk_length函数注册到ioloop中的_callbacks  
#             self.io_loop.add_callback(wrapper)   
#                                                  
#     def _handle_events(self, fd, events):  
#         try:  
#             if events & self.io_loop.READ:  
#                 self._handle_read()  #32. 读取www.baidu.com发送的响应（查看32.1和32.2）  
#                                      #36. 读取www.baidu.com发送的数据  
#             if self.closed():  
#                 return  
#             if events & self.io_loop.WRITE:  
#                 if self._connecting:#注意：21步的时候，将_connecting设为True  
#                     #26.将simple_httpclient.py 中_on_connect注册到ioloop中的_callbacks中  
#                     self._handle_connect()   
#                 self._handle_write() #这里_write_buffer是空的，所以什么也没有写  
#         except Exception:  
#             self.close(exc_info=True)  
#             raise  
#               
#     def _handle_read(self):  
#         try:  
#             try:  
#                 self._pending_callbacks += 1  
#                 while not self.closed():  
#                     #32.1 通过socket.recv函数接收消息，并存入_read_buffer  
#                     if self._read_to_buffer() == 0:   
#                         break  
#             finally:  
#                 self._pending_callbacks -= 1  
#         except Exception:  
#             gen_log.warning("error on read", exc_info=True)  
#             self.close(exc_info=True)  
#             return  
#         #32.2将30.1中设置的_read_callback注册到ioloop中的_callbacks（simple_httpclient.py 中的_on_headers函数）  
#         if self._read_from_buffer(): #32.2 参照32.2.1 32.2.2    
#             return                     
#         else:  
#             self._maybe_run_close_callback()  
#               
#     def write(self, data, callback=None):  
#         self._check_closed()  
#         if data:  
#             WRITE_BUFFER_CHUNK_SIZE = 128 * 1024  
#             if len(data) > WRITE_BUFFER_CHUNK_SIZE:  
#                 for i in range(0, len(data), WRITE_BUFFER_CHUNK_SIZE):  
#                     self._write_buffer.append(data[i:i + WRITE_BUFFER_CHUNK_SIZE])  
#             else:  
#                 #29.1  将29步中的数据追加到_write_buffer  
#                 self._write_buffer.append(data)   
#         self._write_callback = stack_context.wrap(callback)  
#         if not self._connecting:  
#             #29.2  调用write_to_fd，将数据通过socket.send发送给www.baidu.com  
#             self._handle_write()    
#             if self._write_buffer:  
#                 self._add_io_state(self.io_loop.WRITE)  
#               
#             #29.3 注意：这个函数调用_add_io_state(ioloop.IOLoop.READ)注册了READ事件  
#             self._maybe_add_error_listener()    
#               
#     def read_until_regex(self, regex, callback):  
#         self._set_read_callback(callback)  #30.1 设置_read_callback为simple_httpclient.py 中的_on_headers函数  
#         self._read_regex = re.compile(regex) #30.2 设置读取http响应的header的正则表达式  
#         self._try_inline_read()  
#           
#     def read_until(self, delimiter, callback):  
#         self._set_read_callback(callback)  #34.1 设置_read_callback为simple_httpclient.py 中的_on_chunk_length  
#         self._read_delimiter = delimiter   #34.2 设置读取数据的分隔符 参照34.2.1和34.2.2  
#         self._try_inline_read()      
#           
#     def _read_from_buffer(self):  
#         if self._read_bytes is not None and self._read_buffer_size >= self._read_bytes:  
#             num_bytes = self._read_bytes  
#             callback = self._read_callback  
#             self._read_callback = None  
#             self._streaming_callback = None  
#             self._read_bytes = None  
#             self._run_callback(callback, self._consume(num_bytes))  
#             return True  
#         elif self._read_delimiter is not None:  
#             if self._read_buffer:  
#                 while True:  
#                     loc = self._read_buffer[0].find(self._read_delimiter)  
#                     if loc != -1:  
#                         callback = self._read_callback  #34.2.1 simple_httpclient.py 中的_on_chunk_length  
#                         delimiter_len = len(self._read_delimiter)  
#                         self._read_callback = None  
#                         self._streaming_callback = None  
#                         self._read_delimiter = None  
#                         self._run_callback(callback,  
#                                            self._consume(loc + delimiter_len))  
#                         return True  
#                     if len(self._read_buffer) == 1:  
#                         break  
#                     _double_prefix(self._read_buffer)  
#         elif self._read_regex is not None:  
#             if self._read_buffer:  
#                 while True:  
#                     m = self._read_regex.search(self._read_buffer[0])  
#                     if m is not None:  
#                         callback = self._read_callback #32.2.1 simple_httpclient.py 中的_on_headers函数  
#                         self._read_callback = None  
#                         self._streaming_callback = None  
#                         self._read_regex = None  
#                         self._run_callback(callback, self._consume(m.end()))   
#                         return True  
#                     if len(self._read_buffer) == 1:  
#                         break  
#                     _double_prefix(self._read_buffer)  
#         return False  