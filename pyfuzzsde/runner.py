#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/runner.py
# @Time:    2021/04/21 03:00:00
# @Version: 0.0.3
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE Runner
# @Changelog:
#    2021/04/21: 完成动态分析第一版，修复 BUG
#    2021/04/21: 完成动态分析的部分前置工作
#    2021/04/13: Create project

import ast
from types import FrameType, FunctionType
import coverage
from io import StringIO
import os
import random
import re
import sys
import threading
import traceback

from pyfuzzsde.ast_visitor import LineVisitor, SDEVisitor
from pyfuzzsde import SDELogger, logger

class SDERunner(object):
    def __init__(self, entry_func=None, trace_native_libs=False, ignore_filenames=None, verbose=False):
        """初始化 SDERunner

        :param target: 待执行的函数，若要执行文件，无需传入该参数，调用 load 方法即可
        :param trace_native_libs: 是否跟踪内部库，默认为 False
        :param ignore_filenames: 忽略的文件路径关键词列表，默认为 None
        :return:
        """

        self.quitting = False
        self.entry_path = None
        self.entry_compiled = None
        self.entry_dir = None

        self.curr_filename = None
        self.curr_lineno = 0
        self.curr_code = None
        self.curr_ast = None
        self.curr_sde_visitor = None

        self.curr_watch_vars = set()

        self.namespace = dict()

        # 缓存代码和 AST，key 为文件路径
        self.code_cache = dict()
        self.ast_cache = dict()
        self.visitor_cache = dict()

        # 测试数据池
        self.data_pool = list()
        self.used_data_pool = list()
        
        # 额外的 tracer (用于覆盖率或调试器)
        self.cov = coverage.Coverage(branch=True)
        self.tracer_cov = None
        self.tracer_debugger = None

        # 执行函数
        self.entry_func = None
        if isinstance(entry_func, FunctionType):
            self.entry_func = entry_func
            self.entry_path = os.path.abspath(entry_func.__code__.co_filename)
            self.set_entry_dir(os.path.dirname(entry_func.__code__.co_filename))

        # 详细模式
        if verbose:
            SDELogger.enable_debug()

        # 准备文件路径排除列表
        self.ignore_fns = []
        if not trace_native_libs:
            self.ignore_fns.extend(['site-packages', 'lib/python'])
        if ignore_filenames:
            self.ignore_fns.extend(ignore_filenames)
        logger.info("ignore_filenames set to {}".format(self.ignore_fns))
    
    def set_entry_dir(self, entry_dir):
        self.entry_dir = os.path.abspath(entry_dir)
        logger.info("entry_dir set to [{}]".format(self.entry_dir))

    def load_code(self, path):
        """读取源代码并进行缓存

        TODO: 缓存使用 LRU 等算法进行优化
        :param path: 源代码文件路径
        :return: 源代码字符串，解析后的 AST 以及 SDEVisitor 对象
        """
        code_lis = []
        curr_ast = None
        if path in self.code_cache:
            code_lis = self.code_cache[path]
            curr_ast = self.ast_cache[path]
            visitor2 = self.visitor_cache[path]
        else:
            logger.info("Detected new source file [{}]".format(path))
            with open(path, 'r') as f:
                code_src = f.read()
            code_lis = code_src.replace('\r\n', '\n').split('\n')
            self.code_cache[path] = code_lis

            logger.info("Building AST...")
            curr_ast = ast.parse(code_src, mode='exec')
            self.ast_cache[path] = curr_ast

            # 将 LineVisitor 解析的 line_node 添加到 curr_ast 对象中
            visitor = LineVisitor()
            visitor.visit(curr_ast)
            curr_ast.line_node = visitor.get_line_node()

            # 静态分析提取敏感数据
            visitor2 = SDEVisitor()
            visitor2.visit(curr_ast)
            self.visitor_cache[path] = visitor2
            new_data_pool: set = set(visitor2.get_all_const_str()) - set(self.data_pool)
            logger.debug("New data detected ({}): {}".format(len(new_data_pool), new_data_pool))
            self.data_pool.extend(new_data_pool)
            # 保存静态分析结果到 curr_ast 对象中
            # curr_ast.static_result = visitor2.analyzed_functions

            logger.info("AST line_node length = {}".format(len(curr_ast.line_node)))
            logger.info("Finished building AST")
            logger.debug(visitor2.analyzed_functions)
        return code_lis, curr_ast, visitor2
        
    def trace_dispatch(self, frame: FrameType, event: str, arg):
        """Dispatch a trace function based on the event.

        Possible events:
            - line: A new line of code is going to be executed.
            - call: A function is about to be called or another code block is entered.
            - return: A function or other code block is about to return.
            - exception: An exception has occured.
            - c_call: A C function is about to be called.
            - c_return: A C function has returned.
            - c_exception: A C function has raised an exception.
        """

        if self.quitting:
            return
        
        # logger.debug(frame.f_code.co_filename)

        # 忽略不在 self.entry_dir 文件夹中的文件
        if self.entry_dir not in frame.f_code.co_filename:
            return self.trace_dispatch
        for fn in self.ignore_fns:
            if fn in frame.f_code.co_filename:
                return self.trace_dispatch
        
        if self.tracer_cov:
            # 执行覆盖率统计 tracer
            res = self.tracer_cov(frame, event, arg)
            sys.settrace(self.trace_dispatch)
            while res is not None and res != self.tracer_cov:
                res = res(frame, event, arg)
                sys.settrace(self.trace_dispatch)

        # 更新当前代码行号
        self.curr_lineno = frame.f_lineno
        
        # 若当前源代码文件与上一个不同，则更新 self.curr_filename
        if frame.f_code.co_filename != self.curr_filename:
            self.curr_filename = frame.f_code.co_filename
            self.curr_code, self.curr_ast, self.curr_sde_visitor = self.load_code(self.curr_filename)
            logger.info("Switch to source code file [{}]".format(self.curr_filename))

        # 根据 event 类型分发处理
        if event == 'line':
            return self.dispatch_line(frame)
        
        if event == 'return' or event == 'call':
            # 函数调用和返回时清空监视变量
            self.curr_watch_vars.clear()

        return self.trace_dispatch
    
    def get_path_name_by_node(self, flag: list, node: ast.AST):
        """根据 AST 结点生成完整函数路径名称

        对于不属于函数的结点，返回空文本
        :param flag: 辅助标记，用于确认末端是否为函数结点
        :param node: 分析起始 AST 结点
        """
        if isinstance(node, (ast.Module, ast.Name)):
            return ''

        parent_node = self.curr_sde_visitor.parent_table[node]
        
        if isinstance(parent_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_dot = flag[0]
            if not flag[0]:
                flag[0] = True
            res = '{}{}{}'.format(self.get_path_name_by_node(flag, parent_node), parent_node.name, '.' if has_dot else '')
            return res
        
        if isinstance(parent_node, ast.ClassDef):
            if flag[0] is False:
                return ''
            return '{}{}.'.format(self.get_path_name_by_node(flag, parent_node), parent_node.name)
        
        return self.get_path_name_by_node(flag, parent_node)

    def get_curr_func_name(self):
        line_node = self.curr_ast.line_node[self.curr_lineno]
        func_name = self.get_path_name_by_node([False], line_node)
        return func_name

    def dispatch_line(self, frame: FrameType):
        """代码行跟踪处理

        """
        logger.debug('{}:{}\t{}\t{}'.format(
            os.path.basename(self.curr_filename),
            frame.f_lineno,
            self.curr_ast.line_node[frame.f_lineno] if len(self.curr_ast.line_node) > 0 else '',
            self.curr_code[frame.f_lineno-1])
        )

        # 监视变量值
        for var_name in self.curr_watch_vars:
            name_split = var_name.split('.')
            try:
                obj = frame.f_locals[name_split[0]]
                val = eval("obj.{}".format('.'.join(name_split[1:]))) if len(name_split) > 1 else obj
                if isinstance(val, str) and val not in self.data_pool and val not in self.used_data_pool:
                    logger.info("New str DETECTED during running: ({}:{}) {} = {}".format(
                        self.curr_filename, self.curr_lineno, var_name, val
                    ))
                    self.data_pool.append(val)
            except KeyError:
                pass
        
        # 获取当前完整函数名称
        func_name = self.get_curr_func_name()
        if func_name:
            logger.debug("FULL_FUNC_NAME: {}".format(func_name))
            var_inputs: dict = self.curr_sde_visitor.analyzed_functions.get(func_name).get('var_input')
            assert var_inputs is not None

            # 清空监视变量
            self.curr_watch_vars.clear()
            for _, vars in var_inputs.items():
                self.curr_watch_vars.update(vars)
            logger.debug("NEXT_WATCH_VARS: {}".format(self.curr_watch_vars))

        
        return self.trace_dispatch

    # def handle_exception(self):
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     res = {
    #         'type': 'exception',
    #         'exception_type': exc_type,
    #         'exception_msg': str(exc_obj),
    #         'filename': exc_tb.tb_frame.f_code.co_filename,
    #         'lineno': exc_tb.tb_frame.f_lineno,
    #         'time': time.time(),
    #     }
    #     logger.error(json.dumps(res))

    def add_sys_path(self, path):
        """将路径添加到运行环境的 sys.path 中

        :param path: 路径字符串或列表
        :return:
        """
        if isinstance(path, list):
            sys.path.extend(path)
        elif isinstance(path, str):
            sys.path.append(path)
        else:
            logger.error("Path should be a string or list")
    
    def load(self, entry_path, entry_dir=None):
        """加载包含主函数的文件，并设置 entry_dir

        :param entry_path: 包含主函数的文件路径
        :param entry_dir: 待分析的根目录，若不设置则默认为 entry_path 对应的文件夹
        :return:
        """
        self.entry_path = os.path.abspath(entry_path)
        if entry_dir is None:
            self.set_entry_dir(os.path.dirname(self.entry_path))
        else:
            self.set_entry_dir(entry_dir)

        with open(self.entry_path, 'r') as f:
            self.entry_compiled = compile(
                source=f.read(),
                filename=self.entry_path,
                mode='exec'
            )
        self.namespace.clear()
        self.namespace['__file__'] = self.entry_path
        self.namespace['__name__'] = '__main__'
    
    def run_once(self, one_input):
        if self.entry_func is not None:
            target = self.entry_func
        elif self.entry_compiled is not None:
            target = self.entry_compiled
        else:
            raise RuntimeError("Must set entry before run")

        self.quitting = False

        run_out = StringIO()
        run_err = StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        sys.stdout = run_out
        sys.stderr = run_err

        # sys.settrace(self.trace_dispatch)
        # threading.settrace(self.trace_dispatch)
        try:
            if isinstance(target, FunctionType):
                logger.info("Start running with function mode")
                target(one_input)
            else:
                self.namespace['__oneinput__'] = one_input
                logger.info("Start running with compile mode")
                exec(self.entry_compiled, self.namespace)
        except Exception as e:
            logger.error("Execution failed with exception")
            self.quitting = True
            logger.error(traceback.format_exc())
        finally:
            pass
            # self.cov.stop()
            # sys.settrace(self.tracer_debugger)
            # threading.settrace(self.tracer_debugger)
        
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        with open('fuzz_out.log', 'a+') as f:
            f.write(run_out.getvalue())
        with open('fuzz_err.log', 'a+') as f:
            f.write(run_err.getvalue())

        if not self.quitting:
            logger.info("Execution finished")

    def collect(self, times=300, corpus=[]):
        """执行指定次数，收集初始测试用例

        :param times: 运行次数，默认为 10 次
        :param corpus: 用户指定的初始测试用例
        """

        self.data_pool.clear()
        self.data_pool.extend(corpus)

        # 静态分析阶段，提取主程序字符串常量
        self.curr_code, self.curr_ast, self.curr_sde_visitor = self.load_code(self.entry_path)
        # visitor = SDEVisitor()
        # visitor.visit(self.curr_ast)
        # self.data_pool.update(set(visitor.get_all_const_str()))
        
        if len(self.data_pool) < 1:
            self.data_pool.append('a')
        logger.debug("Initial data_pool = {}".format(self.data_pool))
        cnt = 0
        
        self.tracer_debugger = sys.gettrace()
        self.cov.start()
        self.tracer_cov = sys.gettrace()
        
        sys.settrace(self.trace_dispatch)
        threading.settrace(self.trace_dispatch)

        while cnt < times and len(self.data_pool) > 0:
            selected_idx = random.randint(0, len(self.data_pool) - 1)
            selected_ipt = self.data_pool[selected_idx]
            logger.info("Using input [{}] to run the test program".format(selected_ipt))
            self.run_once(selected_ipt)

            # 先执行，后 pop 掉本次执行使用的数据，避免重复
            self.data_pool.pop(selected_idx)
            if not self.quitting:
                self.used_data_pool.append(selected_ipt)
            else:
                logger.error("Input data [{}] caused a crash!".format(selected_ipt))
            cnt += 1
        
        self.cov.stop()
        self.cov.save()
        self.cov.report()

        sys.settrace(self.tracer_debugger)
        threading.settrace(self.tracer_debugger)
