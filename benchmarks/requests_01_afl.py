#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests_01_afl.py
# @Time:    2021/04/21 00:47:00
# @Version: 0.0.2
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests_01) AFL Adapter
# @Ref:     https://github.com/psf/requests/commit/961790f95c7c06dc073d882acb28810a22d27b77
# @Changelog:
#    2021/04/21: Create benchmark

import afl
import os
import sys
import coverage

from http.cookies import SimpleCookie
import requests

def requests_01_afl():
    # cov = coverage.Coverage(auto_data=True)
    # cov.start()
    try:
        ipt_data = sys.stdin.read()
    except UnicodeDecodeError:
        sys.exit(0)
    C = SimpleCookie(ipt_data)
    for morsel in C.values():
        cookie = requests.cookies.morsel_to_cookie(morsel)
        print(cookie)
    # cov.stop()
    # cov.save()

if __name__ == '__main__':
    afl.init()
    requests_01_afl()
