#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests-1/run_afl.py
# @Time:    2021/04/28 02:45:00
# @Version: 0.0.5
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests-1) AFL Adapter
# @BugAt:   https://github.com/psf/requests/commit/3bb13f8fbb9d4ed1a20bd33495cdc087eb062ca0
# @Fixed:   https://github.com/psf/requests/commit/961790f95c7c06dc073d882acb28810a22d27b77
# @Changelog:
#    2021/05/18: Improve performance
#    2021/04/28: Create benchmark

import afl
import os
import sys

base_path = os.path.join(os.path.dirname(__file__), "requests")
sys.path.append(base_path)

from http.cookies import SimpleCookie
import requests

afl.init()
try:
    ipt_data = sys.stdin.read()
except UnicodeDecodeError:
    os._exit(0)
C = SimpleCookie(ipt_data)
for morsel in C.values():
    cookie = requests.cookies.morsel_to_cookie(morsel)
    print(cookie)
os._exit(0)
