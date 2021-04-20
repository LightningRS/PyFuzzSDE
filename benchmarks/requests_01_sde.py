#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/requests_01_sde.py
# @Time:    2021/04/21 00:47:00
# @Version: 0.0.2
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (requests_01) PyFuzzSDE Adapter
# @Ref:     https://github.com/psf/requests/commit/961790f95c7c06dc073d882acb28810a22d27b77
# @Changelog:
#    2021/04/21: Create benchmark

import os
import sys
import coverage

from pyfuzzsde.runner import SDERunner
from http.cookies import SimpleCookie
import requests

def requests_01_sde(one_input):
    # cov = coverage.Coverage(auto_data=True)
    # cov.start()
    try:
        # ipt_data = sys.stdin.read()
        ipt_data = str(one_input)
    except UnicodeDecodeError:
        sys.exit(0)
    C = SimpleCookie(ipt_data)
    for morsel in C.values():
        cookie = requests.cookies.morsel_to_cookie(morsel)
        print(cookie)
    # cov.stop()
    # cov.save()

runner = SDERunner(entry_func=requests_01_sde, trace_native_libs=True, verbose=False, ignore_filenames=['pyfuzzsde', '.vscode', 'lib/python3.9'])
runner.set_entry_dir('/')
runner.collect(times=50, corpus=[
    'sid=1; expires=0; path=/; domain=.yahoo.com',
    'PHPSESSID=aaa; expires=0; path=/; domain=.yahoo.com',
    'UID=123; expires=0; path=/; domain=.yahoo.com',
])

print(runner.used_data_pool)
print(runner.data_pool)

final_pool = runner.data_pool + runner.used_data_pool

afl_inputs = './output/requests_01_afl-inputs'
afl_outputs = './output/requests_01_afl-outputs'
atheris_corpus = './output/requests_01_atheris-corpus'

os.makedirs(afl_inputs, exist_ok=True)
os.makedirs(afl_outputs, exist_ok=True)
os.makedirs(atheris_corpus, exist_ok=True)

f_dict = open('./output/requests_01.dict', 'w')
for i in range(len(final_pool)):
    with open(os.path.join(afl_inputs, 'input{}.txt'.format(i)), "w") as f:
        f.write(final_pool[i])

    with open(os.path.join(atheris_corpus, 'input{}.txt'.format(i)), "w") as f:
        f.write(final_pool[i])

    f_dict.write('input{}="{}"\n'.format(i, final_pool[i]))
f_dict.close()
