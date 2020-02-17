#!/usr/bin/env python
# -*- coding:utf-8 -*-

def app(environ, start_response):
    data = b'Hello World ghou!\n'
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])

    return iter([data])