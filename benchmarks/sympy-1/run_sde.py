#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/sympy-1/run_sde.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.4
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (sympy-1) PyFuzzSDE Adapter
# @Ref:     https://github.com/sympy/sympy/commit/5d243ba19133a0f5b9532435fdcf742608731342
# @Changelog:
#    2021/05/18: Create benchmark

import os
import sys
from pyfuzzsde.runner import SDERunner

base_path = os.path.join(os.path.dirname(__file__), "sympy")
sys.path.append(base_path)

from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.latex import latex

def sympy_1_sde(one_input):
    try:
        ipt_data = str(one_input)
    except UnicodeDecodeError:
        sys.exit(0)
    
    # try:
    expr = parse_expr(ipt_data, evaluate=False)
    print(latex(expr))
    # except SyntaxError:
    #     pass

if __name__ == "__main__":
    runner = SDERunner(entry_func=sympy_1_sde, trace_native_libs=False, 
        verbose=False, max_len=32,
        black_filenames=['PyFuzzSDE/pyfuzzsde', 'sympy_tokenize.py', 'sympy_parser.py'],
        white_filenames=['re.py']
    )
    # runner.set_entry_dir(base_path)
    runner.set_entry_dir('/')
    runner.collect(times=500, corpus=['5/1'])

    print(runner.used_data_pool)
    print(runner.data_pool)

    # final_pool = runner.data_pool + runner.used_data_pool
    final_pool = runner.used_data_pool

    all_input = './output/sympy-1-allinput'
    os.makedirs(all_input, exist_ok=True)

    f_dict = open('./output/sympy-1.dict', 'w')
    for i in range(len(final_pool)):
        src: str = final_pool[i]
        trans = src.replace('\\', '\\\\').replace('"', '\\"')
        with open(os.path.join(all_input, 'input{}.txt'.format(i)), "w") as f:
            f.write(src)
        f_dict.write('input{}="{}"\n'.format(i, trans))
    f_dict.close()

    runner.cov.report()
