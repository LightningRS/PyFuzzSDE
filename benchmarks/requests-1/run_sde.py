#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests-1/run_sde.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.4
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests-1) PyFuzzSDE Adapter
# @Ref:     https://github.com/psf/requests/commit/ac4e05874a1a983ca126185a0e4d4e74915f792e
# @Changelog:
#    2021/05/18: Create benchmark

import os
import sys
from pyfuzzsde.runner import SDERunner

base_path = os.path.join(os.path.dirname(__file__), "requests")
sys.path.append(base_path)

from requests.utils import get_auth_from_url
from requests.compat import quote

def requests_1_sde(one_input):
    try:
        ipt_data = str(one_input)
    except UnicodeDecodeError:
        sys.exit(0)
    url = "http://{}:{}@test.com/test".format(
        quote(ipt_data), quote(ipt_data)
    )
    usr, pwd = get_auth_from_url(url)
    assert usr == ipt_data and pwd == ipt_data

if __name__ == "__main__":
    runner = SDERunner(entry_func=requests_1_sde, trace_native_libs=False, 
        verbose=False, max_len=32,
        black_filenames=['PyFuzzSDE/pyfuzzsde'],
        white_filenames=['urllib', 're.py']
    )
    # runner.set_entry_dir(base_path)
    runner.set_entry_dir('/')
    runner.collect(times=500, corpus=['test'])

    print(runner.used_data_pool)
    print(runner.data_pool)

    # final_pool = runner.data_pool + runner.used_data_pool
    final_pool = runner.used_data_pool

    all_input = './output/requests-1-allinput'
    os.makedirs(all_input, exist_ok=True)

    f_dict = open('./output/requests-1.dict', 'w')
    for i in range(len(final_pool)):
        src: str = final_pool[i]
        trans = src.replace('\\', '\\\\').replace('"', '\\"')
        with open(os.path.join(all_input, 'input{}.txt'.format(i)), "w") as f:
            f.write(src)
        f_dict.write('input{}="{}"\n'.format(i, trans))
    f_dict.close()
