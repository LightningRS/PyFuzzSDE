#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests-1/run_sde.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.4
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Handmade Benchmark 01 PyFuzzSDE Adapter
# @Changelog:
#    2021/05/18: 调整文件结构

import os
import sys
from pyfuzzsde.runner import SDERunner

base_path = os.path.dirname(__file__)
sys.path.append(base_path)

from handmade1 import handmade_1

def handmade_1_sde(one_input):
    try:
        ipt_data = str(one_input)
    except UnicodeDecodeError:
        sys.exit(0)
    handmade_1(one_input)

if __name__ == "__main__":
    runner = SDERunner(entry_func=handmade_1_sde, trace_native_libs=False, 
        verbose=False, max_len=32,
        black_filenames=['PyFuzzSDE/pyfuzzsde']
    )
    # runner.set_entry_dir(base_path)
    runner.set_entry_dir('/')
    runner.collect(times=500, corpus=['test'])

    print(runner.used_data_pool)
    print(runner.data_pool)

    # final_pool = runner.data_pool + runner.used_data_pool
    final_pool = runner.used_data_pool

    all_input = './output/handmade-1-allinput'
    os.makedirs(all_input, exist_ok=True)

    f_dict = open('./output/handmade-1.dict', 'w')
    for i in range(len(final_pool)):
        src: str = final_pool[i]
        trans = src.replace('\\', '\\\\').replace('"', '\\"')
        with open(os.path.join(all_input, 'input{}.txt'.format(i)), "w") as f:
            f.write(src)
        f_dict.write('input{}="{}"\n'.format(i, trans))
    f_dict.close()
