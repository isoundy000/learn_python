#!/usr/bin/env python
# -*- coding:utf-8 -*-
import urlparse
import traceback
from Source.Log.Write import Log
from config import
import urllib


def URLRoute(env, start_response):
    """请求接口"""
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    try:
        params = {}
        path_info = env["PATH_INFO"]
        query_string = env["QUERY_STRING"]
        if request_body_size:
            request_body = env['wsgi.input'].read(request_body_size)
            Log.Write("request_body", request_body)
            Log.Write("request_body", request_body)
            params["__request_body"] = request_body
            d = urlparse.parse_qs(request_body)
            for k, v in d.items():
                params[k] = v[0]

    except Exception, e:
        # traceback.print_exc()
        Log.Write(e)
        Log.Write(traceback.format_exc())