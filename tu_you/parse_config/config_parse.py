#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import time
from openpyxl import load_workbook
import os, sys, json, copy
import collections
import re
import csv
import traceback
from multiprocessing import Queue, Process, cpu_count, freeze_support


def getOutPath(dirname, filename="0.json"):
    pass


