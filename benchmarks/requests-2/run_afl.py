#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests-2/run_afl.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.5
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests-2) AFL Adapter
# @Ref:     https://github.com/psf/requests/commit/c2b307dbefe21177af03f9feb37181a89a799fcc
# @Changelog:
#    2021/05/18: Create benchmark

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
