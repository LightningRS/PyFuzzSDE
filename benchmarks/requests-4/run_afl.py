#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests-4/run_afl.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.5
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests-4) AFL Adapter
# @Ref:     https://github.com/psf/requests/commit/c2b307dbefe21177af03f9feb37181a89a799fcc
# @Changelog:
#    2021/05/18: Improve performance
#    2021/05/18: Create benchmark

import afl
import os
import sys

base_path = os.path.join(os.path.dirname(__file__), "requests")
sys.path.append(base_path)

from requests.utils import get_auth_from_url
from requests.compat import quote

afl.init()
try:
    ipt_data = str(sys.stdin.read())
except UnicodeDecodeError:
    os._exit(0)
url = "http://{}:{}@test.com/test".format(
    quote(ipt_data), quote(ipt_data)
)
usr, pwd = get_auth_from_url(url)
print(str((usr, pwd)))
assert usr == ipt_data and pwd == ipt_data
os._exit(0)
