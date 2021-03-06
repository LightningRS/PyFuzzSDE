#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/sympy-1/run_afl.py
# @Time:    2021/05/18 16:00:00
# @Version: 0.0.5
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Real Project Benchmark (sympy-1) AFL Adapter
# @BugAt:   https://github.com/sympy/sympy/commit/5d243ba19133a0f5b9532435fdcf742608731342
# @Fixed:   https://github.com/sympy/sympy/commit/a531dfdf2c536620fdaf080f7470dde08c257e92
# @Changelog:
#    2021/05/18: Improve performance
#    2021/05/18: Create benchmark

import afl
import os
import sys

base_path = os.path.join(os.path.dirname(__file__), "sympy")
sys.path.append(base_path)

from sympy.parsing.sympy_tokenize import TokenError
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
