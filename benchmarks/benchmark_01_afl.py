#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/benchmark_01_afl.py
# @Time:    2021/04/21 00:47:00
# @Version: 0.0.2
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Benchmark 01 AFL Adapter
# @Changelog:
#    2021/04/21: Create benchmark

import afl
import os
import sys

from pyfuzzsde.runner import SDERunner
from pyfuzzsde.util import FlagRecorder
from benchmarks.benchmark_01 import benchmark_01, FLAGS_COUNT

def benchmark_01_afl():
    flag_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output/benchmark_01_afl.flag')
    flag_recorder = FlagRecorder('benchmark_01_afl', FLAGS_COUNT, flag_path)
    try:
        ipt_data = sys.stdin.read()
    except UnicodeDecodeError:
        sys.exit(0)

    ret_code = benchmark_01(ipt_data)
    flag_recorder.update_flag(ret_code)

if __name__ == '__main__':
    afl.init()
    benchmark_01_afl()
