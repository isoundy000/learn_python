#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask

app = Flask(__name__)

@app.route('/demo', methods=['GET'])
def demo():
    return "gunicorn and flask demo."