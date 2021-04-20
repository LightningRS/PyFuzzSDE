#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/util.py
# @Time:    2021/04/13 15:00:00
# @Version: 0.0.1
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Utilities
# @Changelog:
#    2021/04/13: Create project

import os
from sys import flags
import time

class FlagRecorder:
    def __init__(self, name, flag_cnt=0, path=None):
        self.name = name
        if path is None:
            self.path = './output/{}.flag'.format(self.name)
        else:
            self.path = path
        
        self.flags = [0] * flag_cnt
        self.logs = ''

        if not os.path.exists(self.path):
            self.update_flag(-1)
    
    def update_flag(self, flag_id, value=1):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                flags_str = f.readline().strip()
                self.logs = f.read()
                for i in range(len(flags_str)):
                    self.flags[i] = int(flags_str[i])
        if flag_id >= 0:
            if self.flags[flag_id] == value:
                return
            self.flags[flag_id] = value
            self.logs += '{}\t{}\n'.format(int(time.time() * 1000), flag_id)
        else:
            self.logs += '{}\t{}\n'.format(int(time.time() * 1000), flag_id)
        self.dump_flags()

    def dump_flags(self):
        flags_str = [str(flag) for flag in self.flags]
        with open(self.path, 'w') as f:
            f.write(''.join(flags_str))
            f.write('\n{}'.format(self.logs))
