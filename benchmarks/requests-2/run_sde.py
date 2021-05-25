#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests-2/run_sde.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.5
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests-2) PyFuzzSDE Adapter
# @Ref:     https://github.com/psf/requests/commit/c2b307dbefe21177af03f9feb37181a89a799fcc
# @Changelog:
#    2021/05/18: Create benchmark

import os
import sys
from pyfuzzsde.runner import SDERunner

base_path = os.path.join(os.path.dirname(__file__), "requests")
sys.path.append(base_path)

from http.cookies import SimpleCookie
from requests.cookies import morsel_to_cookie

def requests_2_sde(one_input):
    try:
        ipt_data = str(one_input)
    except UnicodeDecodeError:
        sys.exit(0)
        
    C = SimpleCookie(ipt_data)
    for morsel in C.values():
        cookie = morsel_to_cookie(morsel)
        print(cookie)

    ipt_data2 = "{}={}; path=/; domain=.test.com".format(ipt_data, ipt_data)
    C = SimpleCookie(ipt_data2)
    for morsel in C.values():
        cookie = morsel_to_cookie(morsel)
        print(cookie)

if __name__ == "__main__":
    runner = SDERunner(entry_func=requests_2_sde, trace_native_libs=False, 
        verbose=False, max_len=32,
        black_filenames=['PyFuzzSDE/pyfuzzsde'],
        white_filenames=['urllib', 'http']
    )
    # runner.set_entry_dir(base_path)
    runner.set_entry_dir('/')
    corpus = [
        'sid=1; path=/; domain=.yahoo.com',
        'PHPSESSID=aaa; path=/; domain=.yahoo.com',
        'UID=123; path=/; domain=.yahoo.com',
    ]
    runner.collect(times=500, corpus=corpus)

    print(runner.used_data_pool)
    print(runner.data_pool)

    # final_pool = runner.data_pool + runner.used_data_pool
    final_pool = runner.used_data_pool

    all_input = './output/requests-2-allinput'
    os.makedirs(all_input, exist_ok=True)

    f_dict = open('./output/requests-2.dict', 'w')
    for i in range(len(final_pool)):
        src: str = final_pool[i]
        trans = src.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '')
        with open(os.path.join(all_input, 'input{}.txt'.format(i)), "w") as f:
            f.write(src)
        if len(trans) > 0 and trans.isprintable():
            f_dict.write('input{}="{}"\n'.format(i, trans))
    f_dict.close()

    one_input = './output/requests-2-input1'
    os.makedirs(one_input, exist_ok=True)
    for i in range(len(corpus)):
        src = corpus[i]
        with open(os.path.join(one_input, 'input{}.txt'.format(i)), 'w') as f:
            f.write(src)

    runner.cov.report()
