#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.httpclient import HTTPClient


def request(method, url, **kwargs):
    """使用tornado内置http客户端，其它具体参数请参考tornado文档
    args:
        url: string, URL to fetch
        method: HTTP method, e.g. "GET" or "POST"
        headers: Additional HTTP headers to pass on the request,
                `~tornado.httputil.HTTPHeaders` or `dict`
        body: HTTP body to pass on the request
        connect_timeout: Timeout for initial connection in seconds
        request_timeout: Timeout for entire request in seconds
        validate_cert: bool, For HTTPS requests, validate the server's
            certificate? default is True.
    """
    http = HTTPClient()
    response = http.fetch(url, method=method, **kwargs)

    return response.code, response.body


def get(url, headers=None, timeout=5, validate_cert=False, **kwargs):
    return request('GET', url, headers=headers, connect_timeout=timeout,
                   validate_cert=validate_cert, **kwargs)


def post(url, data=None, headers=None, timeout=5, validate_cert=False, **kwargs):
    return request('POST', url, body=data, headers=headers, connect_timeout=timeout,
                   validate_cert=validate_cert, **kwargs)


if __name__ == '__main__':
    status, html1 = get("http://www.baidu.com")
    print html1
    # print html1.content, html1.body