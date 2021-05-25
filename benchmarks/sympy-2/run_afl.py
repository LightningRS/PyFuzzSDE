#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/sympy-2/run_afl.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.5
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (sympy-2) AFL Adapter
# @Ref:     https://github.com/psf/requests/commit/ed9a550fad6205b74270a0ec530413b3661e8372
# @Changelog:
#    2021/05/18: Create benchmark

import afl
import os
import sys

base_path = os.path.join(os.path.dirname(__file__), "sympy")
sys.path.append(base_path)

from sympy.parsing.sympy_parser import TokenError
from sympy.core.sympify import SympifyError
from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.latex import latex

afl.init()
try:
    ipt_data = str(sys.stdin.read())
    expr = parse_expr(ipt_data, evaluate=False)
except UnicodeDecodeError:
    os._exit(0)
except SympifyError:
    os._exit(0)
except SyntaxError:
    os._exit(0)
except TokenError:
    os._exit(0)
print(latex(expr))
os._exit(0)
