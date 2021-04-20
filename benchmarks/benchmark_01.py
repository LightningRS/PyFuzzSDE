#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/benchmarks/benchmark_01.py
# @Time:    2021/04/21 00:47:00
# @Version: 0.0.2
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Benchmark 01
# @Changelog:
#    2021/04/21: Create benchmark

FLAGS_COUNT = 11

def benchmark_01(s: str):
    suffix = s[7:]
    if s == 'bad':
        raise RuntimeError("Badness")
    if s == 'branch1':
        print('branch1')
        return 0
    if s.startswith('branch2'):
        if suffix == '_1':
            return 1
        if suffix.upper() == '_SECOND':
            return 2
        if suffix.lower() == '_third':
            return 3
        if suffix.endswith('_4'):
            return 4
    if s.capitalize() == 'Branch3':
        return 5
    if s.find('branch4') != -1:
        return 6
    if s.rfind('branch5') != -1:
        return 7
    if s.isalpha():
        return 8
    if s.isnumeric():
        return 9
    return 10
