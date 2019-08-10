#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'
import urlparse
import traceback
import urllib

URL_CONFIG = {}

def URLRoute(env, start_response):
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
            print "request_body", request_body
            print"request_body", request_body
            params["__request_body"] = request_body
            d = urlparse.parse_qs(request_body)
            for k, v in d.items():
                params[k] = v[0]
        print "PATH", path_info
        print "QUERY_STRING", query_string
        #print"QUERY_STRING ulrdecode ",urllib.unquote(query_string))
        path_array = path_info.split('/')
        #printpath_array)
        if len(path_array) < 3:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return ['<h1>Not Found 1 </h1>']
        model = path_array[1]
        api = path_array[2]
        #print"model:%s api:%s"%(model, api))
        try:
            get_param = urlparse.parse_qs(query_string, True)
        except Exception, e:
            print e
            print traceback.format_exc()
            start_response('200 OK', [('Content-Type', 'application/json;charset=UTF-8')])
            return [r'{"status":"fail", "errmsg":"param parse error"}']
        for k, v in get_param.items():
            params[k] = v[0]
        params["_query_string_"] = query_string
        if URL_CONFIG.has_key(model):
            start_response('200 OK', [('Content-Type', 'application/json;charset=UTF-8')])
            return URL_CONFIG[model](api, params)
        else:
            start_response('404 Not Found', [('Content-Type', 'text/html;charset=UTF-8')])
            return ['<h1>Not Found 2 </h1>']
    except Exception,e:
        #traceback.print_exc()
        print e
        print traceback.format_exc()