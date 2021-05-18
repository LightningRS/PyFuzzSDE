#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests-1/run_afl.py
# @Time:    2021/04/28 02:45:00
# @Version: 0.0.3
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests_01) AFL Adapter
# @Ref:     https://github.com/psf/requests/commit/961790f95c7c06dc073d882acb28810a22d27b77
# @Changelog:
#    2021/04/28: Create benchmark

import afl
import os
import sys

base_path = os.path.join(os.path.dirname(__file__), "requests")
sys.path.append(base_path)

from requests.utils import get_auth_from_url
from requests.compat import quote

def requests_1_afl():
    try:
        ipt_data = str(sys.stdin.read())
    except UnicodeDecodeError:
        sys.exit(0)
    url = "http://{}:{}@test.com/test".format(
        quote(ipt_data), quote(ipt_data)
    )
    usr, pwd = get_auth_from_url(url)
    assert usr == ipt_data and pwd == ipt_data

if __name__ == '__main__':
    afl.init()
    requests_1_afl()
