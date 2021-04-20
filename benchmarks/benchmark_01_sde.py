#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/benchmark_01_sde.py
# @Time:    2021/04/21 00:47:00
# @Version: 0.0.2
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Benchmark 01 PyFuzzSDE Adapter
# @Changelog:
#    2021/04/21: Create benchmark

import os
import sys

from pyfuzzsde.runner import SDERunner
from pyfuzzsde.util import FlagRecorder
from benchmarks.benchmark_01 import benchmark_01, FLAGS_COUNT

def benchmark_01_sde(one_input):
    flag_recorder = FlagRecorder('benchmark_01_sde', FLAGS_COUNT)
    try:
        ipt_data = str(one_input)
    except UnicodeDecodeError:
        sys.exit(0)

    ret_code = benchmark_01(ipt_data)
    flag_recorder.update_flag(ret_code)

runner = SDERunner(entry_func=benchmark_01_sde, verbose=True, ignore_filenames=['_sde.py', '.vscode'])
runner.collect()

print(runner.used_data_pool)
print(runner.data_pool)

final_pool = runner.data_pool + runner.used_data_pool

afl_inputs = './output/benchmark_01_afl-inputs'
afl_outputs = './output/benchmark_01_afl-outputs'
atheris_corups = './output/benchmark_01_atheris-corpus'

os.makedirs(afl_inputs, exist_ok=True)
os.makedirs(afl_outputs, exist_ok=True)
os.makedirs(atheris_corups, exist_ok=True)

f_dict = open('./output/benchmark_01.dict', 'w')
for i in range(len(final_pool)):
    with open(os.path.join(afl_inputs, 'input{}.txt'.format(i)), "w") as f:
        f.write(final_pool[i])

    with open(os.path.join(atheris_corups, 'input{}.txt'.format(i)), "w") as f:
        f.write(final_pool[i])

    f_dict.write('input{}="{}"\n'.format(i, final_pool[i]))
f_dict.close()
