#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/handmade-1/run_afl.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.4
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Handmade Benchmark 01 AFL Adapter
# @Changelog:
#    2021/05/18: Create benchmark

import afl
import os
import sys

base_path = os.path.dirname(__file__)
sys.path.append(base_path)

from handmade1 import handmade_1

def handmade_1_sde(one_input):
    try:
        ipt_data = str(one_input)
    except UnicodeDecodeError:
        sys.exit(0)
    handmade_1(one_input)

if __name__ == '__main__':
    afl.init()
    handmade_1_sde()
