#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests_01_atheris.py
# @Time:    2021/04/21 00:47:00
# @Version: 0.0.2
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests_01) Atheris Adapter
# @Ref:     https://github.com/psf/requests/commit/961790f95c7c06dc073d882acb28810a22d27b77
# @Changelog:
#    2021/04/21: Create benchmark

import coverage
import atheris
import os
import sys

from http.cookies import SimpleCookie
import requests

def requests_01_atheris(one_input):
    try:
        ipt_data = str(one_input)
    except UnicodeDecodeError:
        sys.exit(0)
        
    cov = coverage.Coverage(auto_data=True)
    cov.start()
    C = SimpleCookie(ipt_data)
    try:
        for morsel in C.values():
            cookie = requests.cookies.morsel_to_cookie(morsel)
            print(cookie)
    except ValueError:
        pass
    cov.stop()
    cov.save()

if __name__ == '__main__':
    atheris.Setup(sys.argv, requests_01_atheris)
    atheris.Fuzz()
