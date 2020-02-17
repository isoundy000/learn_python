#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Tornado 4.3文档翻译: web框架-RequestHandler和Application 类
# PS:本节最好直接在https://tornado-zh.readthedocs.org或者http://tornado.moelove.info/阅读，以获得更好的阅读体验(格式支持)。原谅我没排好版QAQ
# RequestHandler 和 Application 类
#
# tornado.web 提供了一种带有异步功能并允许它扩展到大量开放连接的 简单的web 框架, 使其成为处理 长连接(long polling) 的一种理想选择.
#
# 这里有一个简单的”Hello, world”示例应用:
# import tornado.ioloop
# import tornado.web
#
# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world")
#
# if __name__ == "__main__":
#     application = tornado.web.Application([
#         (r"/", MainHandler),
#     ])
#     application.listen(8888)
#     tornado.ioloop.IOLoop.current().start()
#
# 查看 用户指南 以了解更多信息.
# 线程安全说明
#
# 一般情况下, 在 RequestHandler 中的方法和Tornado 中其他的方法不是 线程安全的. 尤其是一些方法, 例如 write(), finish(), 和 flush() 要求只能从 主线程调用. 如果你使用多线程, 那么在结束请求之前, 使用 IOLoop.add_callback 来把控制权传送回主线程是很重要的.
# Request handlers
# class tornado.web.RequestHandler(application, request, **kwargs)
#
# HTTP请求处理的基类.
#
# 子类至少应该定义以下”Entry points” 部分中被定义的方法其中之一.
# Entry points
# RequestHandler.initialize()
#
# 子类初始化(Hook).
#
# 作为url spec的第三个参数传递的字典, 将作为关键字参数提供给 initialize().
#
# 例子:
# class ProfileHandler(RequestHandler):
#     def initialize(self, database):
#         self.database = database
#
#     def get(self, username):
#         ...
#
# app = Application([
#     (r'/user/(.*)', ProfileHandler, dict(database=database)),
#     ])
# RequestHandler.prepare()
#
# 在每个请求的最开始被调用, 在 get/post/等方法之前.
#
# 通过复写这个方法, 可以执行共同的初始化, 而不用考虑每个请求方法.
#
# 异步支持: 这个方法使用 gen.coroutine 或 return_future 装饰器来使它异步( asynchronous 装饰器不能被用在 prepare). 如果这个方法返回一个 Future 对象, 执行将不再进行, 直到 Future 对象完成.
#
# 3.1 新版功能: 异步支持.
# RequestHandler.on_finish()
#
# 在一个请求结束后被调用.
#
# 复写这个方法来执行清理, 日志记录等. 这个方法和 prepare 是相 对应的. on_finish 可能不产生任何输出, 因为它是在响应被送 到客户端后才被调用.
#
# 执行后面任何的方法 (统称为HTTP 动词(verb) 方法) 来处理相应的HTTP方法. 这些方法可以通过使用下面的装饰器: gen.coroutine, return_future, 或 asynchronous 变成异步.
#
# 为了支持不再列表中的方法, 可以复写类变量 SUPPORTED_METHODS:
# class WebDAVHandler(RequestHandler):
#     SUPPORTED_METHODS = RequestHandler.SUPPORTED_METHODS + ('PROPFIND',)
#
#     def propfind(self):
#         pass
# RequestHandler.get(*args, **kwargs)
# RequestHandler.head(*args, **kwargs)
# RequestHandler.post(*args, **kwargs)
# RequestHandler.delete(*args, **kwargs)
# RequestHandler.patch(*args, **kwargs)
# RequestHandler.put(*args, **kwargs)
# RequestHandler.options(*args, **kwargs)
# Input
# RequestHandler.get_argument(name, default=[], strip=True)
#
# 返回指定的name参数的值.
#
# 如果没有提供默认值, 那么这个参数将被视为是必须的, 并且当 找不到这个参数的时候我们会抛出一个 MissingArgumentError.
#
# 如果一个参数在url上出现多次, 我们返回最后一个值.
#
# 返回值永远是unicode.
# RequestHandler.get_arguments(name, strip=True)
#
# 返回指定name的参数列表.
#
# 如果参数不存在, 返回一个空列表.
#
# 返回值永远是unicode.
# RequestHandler.get_query_argument(name, default=[], strip=True)
#
# 从请求的query string返回给定name的参数的值.
#
# 如果没有提供默认值, 这个参数将被视为必须的, 并且当找不到这个 参数的时候我们会抛出一个 MissingArgumentError 异常.
#
# 如果这个参数在url中多次出现, 我们将返回最后一次的值.
#
# 返回值永远是unicode.
#
# 3.2 新版功能.
# RequestHandler.get_query_arguments(name, strip=True)
#
# 返回指定name的参数列表.
#
# 如果参数不存在, 将返回空列表.
#
# 返回值永远是unicode.
#
# 3.2 新版功能.
# RequestHandler.get_body_argument(name, default=[], strip=True)
#
# 返回请求体中指定name的参数的值.
#
# 如果没有提供默认值, 那么这个参数将被视为是必须的, 并且当 找不到这个参数的时候我们会抛出一个 MissingArgumentError.
#
# 如果一个参数在url上出现多次, 我们返回最后一个值.
#
# 返回值永远是unicode.
#
# 3.2 新版功能.
# RequestHandler.get_body_arguments(name, strip=True)
#
# 返回由指定请求体中指定name的参数的列表.
#
# 如果参数不存在, 返回一个空列表.
#
# 返回值永远是unicode.
#
# 3.2 新版功能.
# RequestHandler.decode_argument(value, name=None)
#
# 从请求中解码一个参数.
#
# 这个参数已经被解码现在是一个字节字符串(byte string). 默认情况下, 这个方法会把参数解码成utf-8并且返回一个unicode字符串, 但是它可以 被子类复写.
#
# 这个方法既可以在 get_argument() 中被用作过滤器, 也可以用来从url 中提取值并传递给 get()/post()/等.
#
# 如果知道的话参数的name会被提供, 但也可能为None (e.g. 在url正则表达式中未命名的组).
# RequestHandler.request
#
# tornado.httputil.HTTPServerRequest 对象包含附加的 请求参数包括e.g. 头部和body数据.
# RequestHandler.path_args
# RequestHandler.path_kwargs
#
# path_args 和 path_kwargs 属性包含传递给 HTTP verb methods 的位置和关键字参数. 这些属性被设置, 在这些方法被调用之前, 所以这些值 在 prepare 之间是可用的.
# Output
# RequestHandler.set_status(status_code, reason=None)
#
# 设置响应的状态码.
#
# 参数:
# status_code (int) – 响应状态码. 如果 reason 是 None, 它必须存在于 httplib.responses.
# reason (string) – 用人类可读的原因短语来描述状态码. 如果是 None, 它会由来自 httplib.responses 的reason填满.
# RequestHandler.set_header(name, value)
# 给响应设置指定的头部和对应的值.
#
# 如果给定了一个datetime, 我们会根据HTTP规范自动的对它格式化. 如果值不是一个字符串, 我们会把它转换成字符串. 之后所有头部的值 都将用UTF-8 编码.
# RequestHandler.add_header(name, value)
#
# 添加指定的响应头和对应的值.
#
# 不像是 set_header, add_header 可以被多次调用来为相同的头 返回多个值.
# RequestHandler.clear_header(name)
#
# 清除输出头, 取消之前的 set_header 调用.
#
# 注意这个方法不适用于被 add_header 设置了多个值的头.
# RequestHandler.set_default_headers()
#
# 复写这个方法可以在请求开始的时候设置HTTP头.
#
# 例如, 在这里可以设置一个自定义 Server 头. 注意在一般的 请求过程流里可能不会实现你预期的效果, 因为头部可能在错误处 理(error handling)中被重置.
# RequestHandler.write(chunk)
#
# 把给定块写到输出buffer.
#
# 为了把输出写到网络, 使用下面的flush()方法.
#
# 如果给定的块是一个字典, 我们会把它作为JSON来写同时会把响应头 设置为 application/json. (如果你写JSON但是设置不同的 Content-Type, 可以调用set_header 在调用write()之后 ).
#
# 注意列表不能转换为JSON 因为一个潜在的跨域安全漏洞. 所有的JSON 输出应该包在一个字典中. 更多细节参考 http://haacked.com/archive/2009/06/25/json-hijacking.aspx/ 和 https://github.com/facebook/tornado/issues/1009
# RequestHandler.flush(include_footers=False, callback=None)
#
# 将当前输出缓冲区写到网络.
#
# callback 参数, 如果给定则可用于流控制: 它会在所有数据被写到 socket后执行. 注意同一时间只能有一个flush callback停留; 如果另 一个flush在前一个flush的callback运行之前发生, 那么前一个callback 将会被丢弃.
#
# 在 4.0 版更改: 现在如果没有给定callback, 会返回一个 Future 对象.
# RequestHandler.finish(chunk=None)
#
# 完成响应, 结束HTTP 请求.
# RequestHandler.render(template_name, **kwargs)
#
# 使用给定参数渲染模板并作为响应.
# RequestHandler.render_string(template_name, **kwargs)
#
# 使用给定的参数生成指定模板.
#
# 我们返回生成的字节字符串(以utf8). 为了生成并写一个模板 作为响应, 使用上面的render().
# RequestHandler.get_template_namespace()
#
# 返回一个字典被用做默认的模板命名空间.
#
# 可以被子类复写来添加或修改值.
#
# 这个方法的结果将与 tornado.template 模块中其他的默认值 还有 render 或 render_string 的关键字参数相结合.
# RequestHandler.redirect(url, permanent=False, status=None)
#
# 重定向到给定的URL(可以选择相对路径).
#
# 如果指定了 status 参数, 这个值将作为HTTP状态码; 否则 将通过 permanent 参数选择301 (永久) 或者 302 (临时). 默认是 302 (临时重定向).
# RequestHandler.send_error(status_code=500, **kwargs)
#
# 给浏览器发送给定的HTTP 错误码.
#
# 如果 flush() 已经被调用, 它是不可能发送错误的, 所以这个方法将终止 响应. 如果输出已经被写但尚未flush, 它将被丢弃并被错误页代替.
#
# 复写 write_error() 来自定义它返回的错误页. 额外的关键字参数将 被传递给 write_error.
# RequestHandler.write_error(status_code, **kwargs)
#
# 复写这个方法来实现自定义错误页.
#
# write_error 可能调用 write, render, set_header,等 来产生一般的输出.
#
# 如果错误是由未捕获的异常造成的(包括HTTPError), 三个一组的 exc_info 将变成可用的通过 kwargs["exc_info"]. 注意这个异常可能不是”当前(current)” 目的或方法的异常就像 sys.exc_info() 或 traceback.format_exc.
# RequestHandler.clear()
#
# 重置这个响应的所有头部和内容.
# RequestHandler.data_received(chunk)
#
# 实现这个方法来处理请求数据流.
#
# 需要 stream_request_body 装饰器.
# Cookies
# RequestHandler.cookies
#
# self.request.cookies 的别名.
# RequestHandler.get_cookie(name, default=None)
#
# 获取给定name的cookie值, 如果未获取到则返回默认值.
# RequestHandler.set_cookie(name, value, domain=None, expires=None, path='/', expires_days=None, **kwargs)
#
# 设置给定的cookie 名称/值还有其他给定的选项.
#
# 另外的关键字参数在Cookie.Morsel直接设置. 参见 http://docs.python.org/library/cookie.html#morsel-objects 查看可用的属性.
# RequestHandler.clear_cookie(name, path='/', domain=None)
#
# 删除给定名称的cookie.
#
# 受cookie协议的限制, 必须传递和设置该名称cookie时候相同的path 和domain来清除这个cookie(但是这里没有方法来找出在服务端所使 用的该cookie的值).
# RequestHandler.clear_all_cookies(path='/', domain=None)
#
# 删除用户在本次请求中所有携带的cookie.
#
# 查看 clear_cookie 方法来获取关于path和domain参数的更多信息.
#
# 在 3.2 版更改: 添加 path 和 domain 参数.
# RequestHandler.get_secure_cookie(name, value=None, max_age_days=31, min_version=None)
#
# 如果给定的签名过的cookie是有效的,则返回，否则返回None.
#
# 解码后的cookie值作为字节字符串返回(不像 get_cookie ).
#
# 在 3.2.1 版更改: 添加 min_version 参数. 引进cookie version 2; 默认版本 1 和 2 都可以接受.
# RequestHandler.get_secure_cookie_key_version(name, value=None)
#
# 返回安全cookie(secure cookie)的签名key版本.
#
# 返回的版本号是int型的.
# RequestHandler.set_secure_cookie(name, value, expires_days=30, version=None, **kwargs)
#
# 给cookie签名和时间戳以防被伪造.
#
# 你必须在你的Application设置中指定 cookie_secret 来使用这个方法. 它应该是一个长的, 随机的字节序列作为HMAC密钥来做签名.
#
# 使用 get_secure_cookie() 方法来阅读通过这个方法设置的cookie.
#
# 注意 expires_days 参数设置cookie在浏览器中的有效期, 并且它是 独立于 get_secure_cookie 的 max_age_days 参数的.
#
# 安全cookie(Secure cookies)可以包含任意字节的值, 而不只是unicode 字符串(不像是普通cookie)
#
# 在 3.2.1 版更改: 添加 version 参数. 提出cookie version 2 并将它作为默认设置.
# RequestHandler.create_signed_value(name, value, version=None)
#
# 产生用时间戳签名的字符串, 防止被伪造.
#
# 一般通过set_secure_cookie 使用, 但对于无cookie使用来说就 作为独立的方法来提供. 为了解码不作为cookie存储的值, 可以 在 get_secure_cookie 使用可选的value参数.
#
# 在 3.2.1 版更改: 添加 version 参数. 提出cookie version 2 并将它作为默认设置.
# tornado.web.MIN_SUPPORTED_SIGNED_VALUE_VERSION = 1
#
# 这个Tornado版本所支持的最旧的签名值版本.
#
# 比这个签名值更旧的版本将不能被解码.
#
# 3.2.1 新版功能.
# tornado.web.MAX_SUPPORTED_SIGNED_VALUE_VERSION = 2
#
# 这个Tornado版本所支持的最新的签名值版本.
#
# 比这个签名值更新的版本将不能被解码.
#
# 3.2.1 新版功能.
# tornado.web.DEFAULT_SIGNED_VALUE_VERSION = 2
#
# 签名值版本通过 RequestHandler.create_signed_value 产生.
#
# 可通过传递一个 version 关键字参数复写.
#
# 3.2.1 新版功能.
# tornado.web.DEFAULT_SIGNED_VALUE_MIN_VERSION = 1
#
# 可以被 RequestHandler.get_secure_cookie 接受的最旧的签名值.
#
# 可通过传递一个 min_version 关键字参数复写.
#
# 3.2.1 新版功能.
# Other
# RequestHandler.application
#
# 为请求提供服务的 Application 对象
# RequestHandler.check_etag_header()
#
# 针对请求的 If-None-Match 头检查 Etag 头.
#
# 如果请求的ETag 匹配则返回 True 并将返回一个304. 例如:
# self.set_etag_header()
# if self.check_etag_header():
#     self.set_status(304)
#     return
#
# 这个方法在请求结束的时候会被自动调用, 但也可以被更早的调用 当复写了 compute_etag 并且想在请求完成之前先做一个 If-None-Match 检查. Etag 头应该在这个方法被调用前设置 (可以使用 set_etag_header).
# RequestHandler.check_xsrf_cookie()
#
# 确认 _xsrf cookie匹配 _xsrf 参数.
#
# 为了预防cross-site请求伪造, 我们设置一个 _xsrf cookie和包含相同值的一个non-cookie字段在所有 POST 请求中. 如果这两个不匹配, 我们拒绝这个 表单提交作为一个潜在的伪造请求.
#
# _xsrf 的值可以被设置为一个名为 _xsrf 的表单字段或 在一个名为 X-XSRFToken 或 X-CSRFToken 的自定义 HTTP头部(后者被接受为了兼容Django).
#
# 查看 http://en.wikipedia.org/wiki/Cross-site_request_forgery
#
# 发布1.1.1 之前, 这个检查会被忽略如果当前的HTTP头部是 X-Requested-With: XMLHTTPRequest . 这个异常已被证明是 不安全的并且已经被移除. 更多信息请查看 http://www.djangoproject.com/weblog/2011/feb/08/security/ http://weblog.rubyonrails.org/2011/2/8/csrf-protection-bypass-in-ruby-on-rails
#
# 在 3.2.2 版更改: 添加cookie 2版本的支持. 支持版本1和2.
# RequestHandler.compute_etag()
#
# 计算被用于这个请求的etag头.
#
# 到目前为止默认使用输出内容的hash值.
#
# 可以被复写来提供自定义的etag实现, 或者可以返回None来禁止 tornado 默认的etag支持.
# RequestHandler.create_template_loader(template_path)
#
# 返回给定路径的新模板装载器.
#
# 可以被子类复写. 默认返回一个在给定路径上基于目录的装载器, 使用应用程序的 autoescape 和 template_whitespace 设置. 如果应用设置中提供了一个 template_loader , 则使用它来替代.
# RequestHandler.current_user
#
# 返回请求中被认证的用户.
#
# 可以使用以下两者之一的方式来设置:
#
# 子类可以复写 get_current_user(), 这将会在第一次访问 self.current_user 时自动被调用. get_current_user() 在每次请求时只会被调用一次, 并为 将来访问做缓存:
# def get_current_user(self):
#     user_cookie = self.get_secure_cookie("user")
#     if user_cookie:
#         return json.loads(user_cookie)
#     return None
#
# 它可以被设置为一个普通的变量, 通常在来自被复写的 prepare():
# @gen.coroutine
# def prepare(self):
#     user_id_cookie = self.get_secure_cookie("user_id")
#     if user_id_cookie:
#         self.current_user = yield load_user(user_id_cookie)
#
# 注意 prepare() 可能是一个协程, 尽管 get_current_user() 可能不是, 所以如果加载用户需要异步操作后面的形式是必要的.
#
# 用户对象可以是application选择的任意类型.
# RequestHandler.get_browser_locale(default='en_US')
#
# 从 Accept-Language 头决定用户的位置.
#
# 参考 http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
# RequestHandler.get_current_user()
#
# 复写来实现获取当前用户, e.g., 从cookie得到.
#
# 这个方法可能不是一个协程.
# RequestHandler.get_login_url()
#
# 复写这个方法自定义基于请求的登陆URL.
#
# 默认情况下, 我们使用application设置中的 login_url 值.
# RequestHandler.get_status()
#
# 返回响应的状态码.
# RequestHandler.get_template_path()
#
# 可以复写为每个handler指定自定义模板路径.
#
# 默认情况下, 我们使用应用设置中的 template_path . 如果返回None则使用调用文件的相对路径加载模板.
# RequestHandler.get_user_locale()
#
# 复写这个方法确定认证过的用户所在位置.
#
# 如果返回了None , 我们退回选择 get_browser_locale().
#
# 这个方法应该返回一个 tornado.locale.Locale 对象, 就像调用 tornado.locale.get("en") 得到的那样
# RequestHandler.locale
#
# 返回当前session的位置.
#
# 通过 get_user_locale 来确定, 你可以复写这个方法设置 获取locale的条件, e.g., 记录在数据库中的用户偏好, 或 get_browser_locale, 使用 Accept-Language 头部.
# RequestHandler.log_exception(typ, value, tb)
#
# 复写来自定义未捕获异常的日志.
#
# 默认情况下 HTTPError 的日志实例作为警告(warning)没有堆栈追踪(在 tornado.general logger), 其他作为错误(error)的异常带有堆栈 追踪(在 tornado.application logger).
#
# 3.1 新版功能.
# RequestHandler.on_connection_close()
#
# 在异步处理中, 如果客户端关闭了连接将会被调用.
#
# 复写这个方法来清除与长连接相关的资源. 注意这个方法只有当在异步处理 连接被关闭才会被调用; 如果你需要在每个请求之后做清理, 请复写 on_finish 方法来代替.
#
# 在客户端离开后, 代理可能会保持连接一段时间 (也可能是无限期), 所以这个方法在终端用户关闭他们的连接时可能不会被立即执行.
# RequestHandler.require_setting(name, feature='this feature')
#
# 如果给定的app设置未定义则抛出一个异常.
# RequestHandler.reverse_url(name, *args)
#
# Application.reverse_url 的别名.
# RequestHandler.set_etag_header()
#
# 设置响应的Etag头使用 self.compute_etag() 计算.
#
# 注意: 如果 compute_etag() 返回 None 将不会设置头.
#
# 这个方法在请求结束的时候自动调用.
# RequestHandler.settings
#
# self.application.settings 的别名.
# RequestHandler.static_url(path, include_host=None, **kwargs)
#
# 为给定的相对路径的静态文件返回一个静态URL.
#
# 这个方法需要你在你的应用中设置 static_path (既你 静态文件的根目录).
#
# 这个方法返回一个带有版本的url (默认情况下会添加 ?v=<signature>), 这会允许静态文件被无限期缓存. 这可以被 禁用通过传递 include_version=False (默认已经实现; 其他静态文件的实现不需要支持这一点, 但它们可能支持其他选项).
#
# 默认情况下这个方法返回当前host的相对URL, 但是如果 include_host 为true则返回的将是绝对路径的URL. 如果这个处理函数有一个 include_host 属性, 该值将被所有的 static_url 调用默认使用, 而不需要传递 include_host 作为一个关键字参数.
# RequestHandler.xsrf_form_html()
#
# 一个将被包含在所有POST表单中的HTML <input/> 标签.
#
# 它定义了我们在所有POST请求中为了预防伪造跨站请求所检查的 _xsrf 的输入值. 如果你设置了 xsrf_cookies application设置, 你必须包含这个HTML 在你所有的HTML表单.
#
# 在一个模板中, 这个方法应该使用 {% module xsrf_form_html() %} 这种方式调用
#
# 查看上面的 check_xsrf_cookie() 了解更多信息.
# RequestHandler.xsrf_token
#
# 当前用户/会话的XSRF-prevention token.
#
# 为了防止伪造跨站请求, 我们设置一个 ‘_xsrf’ cookie 并在所有POST 请求中包含相同的 ‘_xsrf’ 值作为一个参数. 如果这两个不匹配, 我们会把这个提交当作潜在的伪造请求而拒绝掉.
#
# 查看 http://en.wikipedia.org/wiki/Cross-site_request_forgery
#
# 在 3.2.2 版更改: 该xsrf token现在已经在每个请求都有一个随机mask这使得它 可以简洁的把token包含在页面中是安全的. 查看 http://breachattack.com 浏览更多信息关于这个更改修复的 问题. 旧(版本1)cookies 将被转换到版本2 当这个方法被调用 除非 xsrf_cookie_version Application 被设置为1.
#
# 在 4.3 版更改: 该 xsrf_cookie_kwargs Application 设置可能被用来 补充额外的cookie 选项(将会直接传递给 set_cookie). 例如, xsrf_cookie_kwargs=dict(httponly=True, secure=True) 将设置 secure 和 httponly 标志在 _xsrf cookie.
# 应用程序配置
#
# class tornado.web.Application(handlers=None, default_host='', transforms=None, **settings)
# 组成一个web应用程序的请求处理程序的集合.
#
# 该类的实例是可调用的并且可以被直接传递给HTTPServer为应用程序 提供服务:
# application = web.Application([
#     (r"/", MainPageHandler),
# ])
# http_server = httpserver.HTTPServer(application)
# http_server.listen(8080)
# ioloop.IOLoop.current().start()
#
# 这个类的构造器带有一个列表包含 URLSpec 对象或 (正则表达式, 请求类)元组. 当我们接收到请求, 我们按顺序迭代该列表 并且实例化和请求路径相匹配的正则表达式所对应的第一个请求类. 请求类可以被指定为一个类对象或一个(完全有资格的)名字.
#
# 每个元组可以包含另外的部分, 只要符合 URLSpec 构造器参数的条件. (在Tornado 3.2之前, 只允许包含两个或三个元素的元组).
#
# 一个字典可以作为该元组的第三个元素被传递, 它将被用作处理程序 构造器的关键字参数和 initialize 方法. 这种模式也被用于例子中的 StaticFileHandler (注意一个 StaticFileHandler 可以被自动挂载连带下面的static_path设置):
# application = web.Application([
#     (r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
# ])
#
# 我们支持虚拟主机通过 add_handlers 方法, 该方法带有一个主机 正则表达式作为第一个参数:
# application.add_handlers(r"www\.myhost\.com", [
#     (r"/article/([0-9]+)", ArticleHandler),
# ])
#
# 你可以提供静态文件服务通过传递 static_path 配置作为关键字 参数. 我们将提供这些文件从 /static/ URI (这是可配置的通过 static_url_prefix 配置), 并且我们将提供 /favicon.ico 和 /robots.txt 从相同目录下. 一个 StaticFileHandler 的 自定义子类可以被指定, 通过 static_handler_class 设置.
# settings
#
# 传递给构造器的附加关键字参数保存在 settings 字典中, 并经常在文档中被称为”application settings”. Settings被用于 自定义Tornado的很多方面(虽然在一些情况下, 更丰富的定制可能 是通过在 RequestHandler 的子类中复写方法). 一些应用程序 也喜欢使用 settings 字典作为使一些处理程序可以使用应用 程序的特定设置的方法, 而无需使用全局变量. Tornado中使用的 Setting描述如下.
# 一般设置(General settings):
#
# autoreload: 如果为 True, 服务进程将会在任意资源文件 改变的时候重启, 正如 Debug模式和自动重载 中描述的那样. 这个选项是Tornado 3.2中新增的; 在这之前这个功能是由 debug 设置控制的.
# debug: 一些调试模式设置的速记, 正如 Debug模式和自动重载 中描述的那样. debug=True 设置等同于 autoreload=True, compiled_template_cache=False, static_hash_cache=False, serve_traceback=True.
# default_handler_class 和 default_handler_args: 如果没有发现其他匹配则会使用这个处理程序; 使用这个来实现自 定义404页面(Tornado 3.2新增).
# compress_response: 如果为 True, 以文本格式的响应 将被自动压缩. Tornado 4.0新增.
# gzip: 不推荐使用的 compress_response 别名自从 Tornado 4.0.
# log_function: 这个函数将在每次请求结束的时候调用以记录 结果(有一次参数, 该 RequestHandler 对象). 默认实现是写入 logging 模块的根logger. 也可以通过复写 Application.log_request 自定义.
# serve_traceback: 如果为true, 默认的错误页将包含错误信息 的回溯. 这个选项是在Tornado 3.2中新增的; 在此之前这个功能 由 debug 设置控制.
# ui_modules 和 ui_methods: 可以被设置为 UIModule 或UI methods 的映射提供给模板. 可以被设置为一个模块, 字典, 或一个模块的列表和/或字典. 参见 UI 模块 了解更多 细节.
# 认证和安全设置(Authentication and security settings):
#
# cookie_secret: 被 RequestHandler.get_secure_cookie 使用, set_secure_cookie 用来给cookies签名.
# key_version: 被requestHandler set_secure_cookie 使用一个特殊的key给cookie签名当 cookie_secret 是一个 key字典.
# login_url: authenticated 装饰器将会重定向到这个url 如果该用户没有登陆. 更多自定义特性可以通过复写 RequestHandler.get_login_url 实现
# xsrf_cookies: 如果true, 跨站请求伪造(防护) 将被开启.
# xsrf_cookie_version: 控制由该server产生的新XSRF cookie的版本. 一般应在默认情况下(这将是最高支持的版本), 但是可以被暂时设置为一个较低的值, 在版本切换之间. 在Tornado 3.2.2 中新增, 这里引入了XSRF cookie 版本2.
# xsrf_cookie_kwargs: 可设置为额外的参数字典传递给 RequestHandler.set_cookie 为该XSRF cookie.
# twitter_consumer_key, twitter_consumer_secret, friendfeed_consumer_key, friendfeed_consumer_secret, google_consumer_key, google_consumer_secret, facebook_api_key, facebook_secret: 在 tornado.auth 模块中使用来验证各种APIs.
# 模板设置:
#
# autoescape: 控制对模板的自动转义. 可以被设置为 None 以禁止转义, 或设置为一个所有输出都该传递过去的函数 name . 默认是 "xhtml_escape". 可以在每个模板中改变使用 {% autoescape %} 指令.
# compiled_template_cache: 默认是 True; 如果是 False 模板将会在每次请求重新编译. 这个选项是Tornado 3.2中新增的; 在这之前这个功能由 debug 设置控制.
# template_path: 包含模板文件的文件夹. 可以通过复写 RequestHandler.get_template_path 进一步定制
# template_loader: 分配给 tornado.template.BaseLoader 的一个实例自定义模板加载. 如果使用了此设置, 则 template_path 和 autoescape 设置都会被忽略. 可 通过复写 RequestHandler.create_template_loader 进一步 定制.
# template_whitespace: 控制处理模板中的空格; 参见 tornado.template.filter_whitespace 查看允许的值. 在Tornado 4.3中新增.
# 静态文件设置:
#
# static_hash_cache: 默认为 True; 如果是 False 静态url将会在每次请求重新计算. 这个选项是Tornado 3.2中 新增的; 在这之前这个功能由 debug 设置控制.
# static_path: 将被提供服务的静态文件所在的文件夹.
# static_url_prefix: 静态文件的Url前缀, 默认是 "/static/".
# static_handler_class, static_handler_args: 可 设置成为静态文件使用不同的处理程序代替默认的 tornado.web.StaticFileHandler. static_handler_args, 如果设置, 应该是一个关键字参数的字典传递给处理程序 的 initialize 方法.
# listen(port, address='', **kwargs)
# 为应用程序在给定端口上启动一个HTTP server.
#
# 这是一个方便的别名用来创建一个 HTTPServer 对象并调用它 的listen方法. HTTPServer.listen 不支持传递关键字参数给 HTTPServer 构造器. 对于高级用途 (e.g. 多进程模式), 不要使用这个方法; 创建一个 HTTPServer 并直接调用它的 TCPServer.bind/TCPServer.start 方法.
#
# 注意在调用这个方法之后你仍然需要调用 IOLoop.current().start() 来启动该服务.
#
# 返回 HTTPServer 对象.
#
# 在 4.3 版更改: 现在返回 HTTPServer 对象.
# add_handlers(host_pattern, host_handlers)
#
# 添加给定的handler到我们的handler表.
#
# Host 模式将按照它们的添加顺序进行处理. 所有匹配模式将被考虑.
# reverse_url(name, *args)
#
# 返回名为 name 的handler的URL路径
#
# 处理程序必须作为 URLSpec 添加到应用程序.
#
# 捕获组的参数将在 URLSpec 的正则表达式被替换. 如有必要它们将被转换成string, 编码成utf8,及 网址转义(url-escaped).
# log_request(handler)
#
# 写一个完成的HTTP 请求到日志中.
#
# 默认情况下会写到python 根(root)logger. 要改变这种行为 无论是子类应用和复写这个方法, 或者传递一个函数到应用的 设置字典中作为 log_function.
# class tornado.web.URLSpec(pattern, handler, kwargs=None, name=None)
#
# 指定URL和处理程序之间的映射.
#
# Parameters:
#
# pattern: 被匹配的正则表达式. 任何在正则表达式的group 都将作为参数传递给处理程序的get/post/等方法.
# handler: 被调用的 RequestHandler 子类.
# kwargs (optional): 将被传递给处理程序构造器的额外 参数组成的字典.
# name (optional): 该处理程序的名称. 被 Application.reverse_url 使用.
# URLSpec 类在 tornado.web.url 名称下也是可用的.
#
# 装饰器(Decorators)
# tornado.web.asynchronous(method)
# 用这个包装请求处理方法如果它们是异步的.
#
# 这个装饰器适用于回调式异步方法; 对于协程, 使用 @gen.coroutine 装饰器而没有 @asynchronous. (这是合理的, 因为遗留原因使用两个 装饰器一起来提供 @asynchronous 在第一个, 但是在这种情况下 @asynchronous 将被忽略)
#
# 这个装饰器应仅适用于 HTTP verb methods; 它的行为是未定义的对于任何其他方法. 这个装饰器不会 使 一个方法异步; 它告诉框架该方法 是 异步(执行)的. 对于这个装饰器, 该方法必须(至少有时)异步的做一 些事情这是有用的.
#
# 如果给定了这个装饰器, 当方法返回的时候响应并没有结束. 它是由请求处理程序调用 self.finish() 来结束该HTTP请求的. 没有这个装饰器, 请求会自动结束当 get() 或 post() 方法返回时. 例如:
# class MyRequestHandler(RequestHandler):
#     @asynchronous
#     def get(self):
#        http = httpclient.AsyncHTTPClient()
#        http.fetch("http://friendfeed.com/", self._on_download)
#
#     def _on_download(self, response):
#        self.write("Downloaded!")
#        self.finish()
#
# 在 3.1 版更改: 可以使用 @gen.coroutine 而不需 @asynchronous.
#
# 在 4.3 版更改: 可以返回任何东西但 None 或者一个 可yield的对象来自于被 @asynchronous 装饰的方法是错误的. 这样的返回值之前是默认忽略的.
# tornado.web.authenticated(method)
#
# 使用这个装饰的方法要求用户必须登陆.
#
# 如果用户未登陆, 他们将被重定向到已经配置的 login url.
#
# 如果你配置login url带有查询参数, Tornado将假设你知道你正在 做什么并使用它. 如果不是, 它将添加一个 next 参数这样登陆 页就会知道一旦你登陆后将把你送到哪里.
# tornado.web.addslash(method)
#
# 使用这个装饰器给请求路径中添加丢失的slash.
#
# 例如, 使用了这个装饰器请求 /foo 将被重定向到 /foo/ . 你的请求处理映射应该使用正则表达式类似 r'/foo/?' 和使用装饰器相结合.
# tornado.web.removeslash(method)
#
# 使用这个装饰器移除请求路径尾部的斜杠(slashes).
#
# 例如, 使用了这个装饰器请求 /foo/ 将被重定向到 /foo . 你的请求处理映射应该使用正则表达式类似 r'/foo/*' 和使用装饰器相结合.
# tornado.web.stream_request_body(cls)
#
# 适用于 RequestHandler 子类以开启流式body支持.
#
# 这个装饰器意味着以下变化:
#
# HTTPServerRequest.body 变成了未定义, 并且body参数将不再被 RequestHandler.get_argument 所包含.
# RequestHandler.prepare 被调用当读到请求头而不是在整个请求体 都被读到之后.
# 子类必须定义一个方法 data_received(self, data):, 这将被调 用0次或多次当数据是可用状态时. 注意如果该请求的body是空的, data_received 可能不会被调用.
# prepare 和 data_received 可能返回Futures对象(就像通过 @gen.coroutine, 在这种情况下下一个方法将不会被调用直到这些 futures完成.
# 常规的HTTP方法 (post, put, 等)将在整个body被读取后被 调用.
# 在 data_received 和asynchronous之间有一个微妙的互动 prepare: data_received 的第一次调用可能出现在任何地方 在调用 prepare 已经返回 或 yielded.
# 其他(Everything else)
# exception tornado.web.HTTPError(status_code=500, log_message=None, *args, **kwargs)
#
# 一个将会成为HTTP错误响应的异常.
#
# 抛出一个 HTTPError 是一个更方便的选择比起调用 RequestHandler.send_error 因为它自动结束当前的函数.
#
# 为了自定义 HTTPError 的响应, 复写 RequestHandler.write_error.
#
# 参数:
# status_code (int) – HTTP状态码. 必须列在 httplib.responses 之中除非给定了 reason 关键字参数.
# log_message (string) – 这个错误将会被写入日志的信息(除非该 Application 是debug模式否则不会展示给用户). 可能含有 %s-风格的占位符, 它将填补剩余的位置参数.
# reason (string) – 唯一的关键字参数. HTTP “reason” 短语 将随着 status_code 传递给状态行. 通常从 status_code, 自动确定但可以使用一个非标准的数字代码.
# exception tornado.web.Finish
#
# 一个会结束请求但不会产生错误响应的异常.
#
# 当一个 RequestHandler 抛出 Finish , 该请求将会结束(调用 RequestHandler.finish 如果该方法尚未被调用), 但是错误处理方法 (包括 RequestHandler.write_error)将不会被调用.
#
# 如果 Finish() 创建的时候没有携带参数, 则会发送一个pending响应. 如果 Finish() 给定了参数, 则参数将会传递给 RequestHandler.finish().
#
# 这是比复写 write_error 更加便利的方式用来实现自定义错误页 (尤其是在library代码中):
# if self.current_user is None:
#     self.set_status(401)
#     self.set_header('WWW-Authenticate', 'Basic realm="something"')
#     raise Finish()
#
# 在 4.3 版更改: 传递给 Finish() 的参数将被传递给 RequestHandler.finish.
# exception tornado.web.MissingArgumentError(arg_name)
#
# 由 RequestHandler.get_argument 抛出的异常.
#
# 这是 HTTPError 的一个子类, 所以如果是未捕获的400响应码将被 用来代替500(并且栈追踪不会被记录到日志).
#
# 3.1 新版功能.
# class tornado.web.UIModule(handler)
#
# 一个在页面上可复用, 模块化的UI单元.
#
# UI模块经常执行附加的查询, 它们也可以包含额外的CSS和 JavaScript, 这些将包含在输出页面上, 在页面渲染的时候自动插入.
#
# UIModule的子类必须复写 render 方法.
# render(*args, **kwargs)
#
# 在子类中复写以返回这个模块的输出.
# embedded_javascript()
#
# 复写以返回一个被嵌入页面的JavaScript字符串.
# javascript_files()
#
# 复写以返回这个模块需要的JavaScript文件列表.
#
# 如果返回值是相对路径, 它们将被传递给 RequestHandler.static_url; 否则会被原样使用.
# embedded_css()
#
# 复写以返回一个将被嵌入页面的CSS字符串.
# css_files()
#
# 复写以返回这个模块需要的CSS文件列表.
#
# 如果返回值是相对路径, 它们将被传递给 RequestHandler.static_url; 否则会被原样使用.
# html_head()
#
# 复写以返回一个将被放入<head/>标签的HTML字符串.
# html_body()
#
# 复写以返回一个将被放入<body/>标签最后的HTML字符串.
# render_string(path, **kwargs)
#
# 渲染一个模板并且将它作为一个字符串返回.
# class tornado.web.ErrorHandler(application, request, **kwargs)
#
# 为所有请求生成一个带有 status_code 的错误响应.
# class tornado.web.FallbackHandler(application, request, **kwargs)
#
# 包装其他HTTP server回调的 RequestHandler .
#
# fallback是一个可调用的对象, 它接收一个 HTTPServerRequest, 诸如一个 Application 或 tornado.wsgi.WSGIContainer. 这对于在相同server中同时使用 Tornado RequestHandlers 和WSGI是非常有用的. 用法:
# wsgi_app = tornado.wsgi.WSGIContainer(
#     django.core.handlers.wsgi.WSGIHandler())
# application = tornado.web.Application([
#     (r"/foo", FooHandler),
#     (r".*", FallbackHandler, dict(fallback=wsgi_app),
# ])
# class tornado.web.RedirectHandler(application, request, **kwargs)
#
# 将所有GET请求重定向到给定的URL.
#
# 你需要为处理程序提供 url 关键字参数, e.g.:
# application = web.Application([
#     (r"/oldpath", web.RedirectHandler, {"url": "/newpath"}),
# ])
# class tornado.web.StaticFileHandler(application, request, **kwargs)
#
# 可以为一个目录提供静态内容服务的简单处理程序.
#
# StaticFileHandler 是自动配置的如果你传递了 static_path 关键字参数给 Application. 这个处理程序可以被自定义通过 static_url_prefix, static_handler_class, 和 static_handler_args 配置.
#
# 为了将静态数据目录映射一个额外的路径给这个处理程序你可以在你应用程序中 添加一行例如:
# application = web.Application([
#     (r"/content/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
# ])
#
# 处理程序构造器需要一个 path 参数, 该参数指定了将被服务内容的本地根 目录.
#
# 注意在正则表达式的捕获组需要解析 path 参数的值给get()方法(不同于 上面的构造器的参数); 参见 URLSpec 了解细节.
#
# 为了自动的提供一个文件例如 index.html 当一个目录被请求的时候, 设置 static_handler_args=dict(default_filename="index.html") 在你的应用程序设置中(application settings), 或添加 default_filename 作为你的 StaticFileHandler 的初始化参数.
#
# 为了最大限度的提高浏览器缓存的有效性, 这个类支持版本化的url(默认情 况下使用 ?v= 参数). 如果给定了一个版本, 我们指示浏览器无限期 的缓存该文件. make_static_url (也可作为 RequestHandler.static_url) 可以被用来构造一个版本化的url.
#
# 该处理程序主要用户开发和轻量级处理文件服务; 对重型传输,使用专用的 静态文件服务是更高效的(例如nginx或Apache). 我们支持HTTP Accept-Ranges 机制来返回部分内容(因为一些浏览器需要此功能是 为了查找在HTML5音频或视频中).
#
# 子类注意事项
#
# 这个类被设计是可以让子类继承的, 但由于静态url是被类方法生成的 而不是实例方法的方式, 继承模式有点不同寻常. 一定要使用 @classmethod 装饰器当复写一个类方法时. 实例方法可以使用 self.path self.absolute_path, 和 self.modified 属性.
#
# 子类应该只复写在本节讨论的方法; 复写其他方法很容易出错. 最重要的 StaticFileHandler.get 问题尤其严重, 由于与 compute_etag 还有其他方法紧密耦合.
#
# 为了改变静态url生成的方式(e.g. 匹配其他服务或CDN), 复写 make_static_url, parse_url_path, get_cache_time, 和/或 get_version.
#
# 为了代替所有与文件系统的相互作用(e.g. 从数据库提供静态内容服务), 复写 get_content, get_content_size, get_modified_time, get_absolute_path, 和 validate_absolute_path.
#
# 在 3.1 版更改: 一些为子类设计的方法在Tornado 3.1 被添加.
# compute_etag()
#
# 设置 Etag 头基于static url版本.
#
# 这允许高效的针对缓存版本的 If-None-Match 检查, 并发送正确的 Etag 给局部的响应(i.e. 相同的 Etag 为完整的文件).
#
# 3.1 新版功能.
# set_headers()
#
# 设置响应的内容和缓存头.
#
# 3.1 新版功能.
# should_return_304()
#
# 如果头部表明我们应该返回304则返回True.
#
# 3.1 新版功能.
# classmethod get_absolute_path(root, path)
#
# 返回 path 相对于 root 的绝对路径.
#
# root 是这个 StaticFileHandler 配置的路径(在大多数情 况下是 Application 的 static_path 设置).
#
# 这个类方法可能在子类中被复写. 默认情况下它返回一个文件系统 路径, 但其他字符串可以被使用, 只要它们是独特的并且被 子类复写的 get_content 理解.
#
# 3.1 新版功能.
# validate_absolute_path(root, absolute_path)
#
# 验证并返回绝对路径.
#
# root 是 StaticFileHandler 配置的路径,并且 path 是 get_absolute_path 的结果.
#
# 这是一个实例方法在请求过程中被调用, 所以它可能抛出 HTTPError 或者使用类似 RequestHandler.redirect (返回None在重定向到停止进一步处理之后) 这种方法. 如果丢失文件将会生成404错误.
#
# 这个方法可能在返回路径之前修改它, 但是注意任何这样的 修改将不会被 make_static_url 理解.
#
# 在实例方法, 这个方法的结果对 self.absolute_path 是可用的.
#
# 3.1 新版功能.
# classmethod get_content(abspath, start=None, end=None)
#
# 检索位于所给定绝对路径的请求资源的内容.
#
# 这个类方法可以被子类复写. 注意它的特征不同于其他可复写 的类方法(没有 settings 参数); 这是经过深思熟虑的以 确保 abspath 能依靠自己作为缓存键(cache key) .
#
# 这个方法返回一个字节串或一个可迭代的字节串. 对于大文件 后者是更优的选择因为它有助于减少内存碎片.
#
# 3.1 新版功能.
# classmethod get_content_version(abspath)
#
# 返回给定路径资源的一个版本字符串.
#
# 这个类方法可以被子类复写. 默认的实现是对文件内容的hash.
#
# 3.1 新版功能.
# get_content_size()
#
# 检索给定路径中资源的总大小.
#
# 这个方法可以被子类复写.
#
# 3.1 新版功能.
#
# 在 4.0 版更改: 这个方法总是被调用, 而不是仅在部分结果被请求时.
# get_modified_time()
#
# 返回 self.absolute_path 的最后修改时间.
#
# 可以被子类复写. 应当返回一个 datetime 对象或None.
#
# 3.1 新版功能.
# get_content_type()
#
# 返回这个请求使用的 Content-Type 头.
#
# 3.1 新版功能.
# set_extra_headers(path)
#
# 为了子类给响应添加额外的头部
# get_cache_time(path, modified, mime_type)
#
# 复写来自定义缓存控制行为.
#
# 返回一个正的秒数作为结果可缓存的时间的量或者返回0标记资源 可以被缓存一个未指定的时间段(受浏览器自身的影响).
#
# 默认情况下带有 v 请求参数的资源返回的缓存过期时间是10年.
# classmethod make_static_url(settings, path, include_version=True)
#
# 为给定路径构造一个的有版本的url.
#
# 这个方法可以在子类中被复写(但是注意他是一个类方法而不是一个 实例方法). 子类只需实现签名 make_static_url(cls, settings, path); 其他关键字参数可 以通过 static_url 传递, 但这不是标准.
#
# settings 是 Application.settings 字典. path 是被请求的静态路径. 返回的url应该是相对于当前host的.
#
# include_version 决定生成的URL是否应该包含含有给定 path 相对应文件的hash版本查询字符串.
# parse_url_path(url_path)
#
# 将静态URL路径转换成文件系统路径.
#
# url_path 是由去掉 static_url_prefix 的URL组成. 返回值应该是相对于 static_path 的文件系统路径.
#
# 这是逆 make_static_url .
# classmethod get_version(settings, path)
#
# 生成用于静态URL的版本字符串.
#
# settings 是 Application.settings 字典并且 path 是请求资源在文件系统中的相对位置. 返回值应该是一个字符串 或 None 如果没有版本可以被确定.
#
# 在 3.1 版更改: 这个方法之前建议在子类中复写; get_content_version 现在是首选因为它允许基类来处理结果的缓存.
#
# 作者：TaoBeier
# 链接：https://www.jianshu.com/p/61ae342efac6
# 来源：简书
# 著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。