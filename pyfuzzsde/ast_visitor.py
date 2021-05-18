#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Project: PyFuzzSDE
# @File:    pyfuzzsde/ast_visitor.py
# @Time:    2021/04/21 03:00:00
# @Version: 0.0.3
# @Author:  LightningRS
# @Email:   me@ldby.site
# @Desc:    PyFuzzSDE AST Analyzer
# @Changelog:
#    2021/04/21: 调整数据结构，增加 parent_table，修复 BUG
#    2021/04/21: 针对赋值语句的复杂目标识别进行优化
#    2021/04/13: Create project

import ast
import astunparse
from typing import Dict, List
from pyfuzzsde import logger

class LineVisitor(ast.NodeVisitor):
    """用于构建代码行到 AST 结点映射关系的 Visitor 类
    """

    def __init__(self):
        self._last_lineno = 0
        self._line_node = dict()
    
    def generic_visit(self, node: ast.AST):
        if hasattr(node, 'lineno'):
            if node.lineno not in self._line_node:
                self._last_lineno = node.lineno
                self._line_node[node.lineno] = node
        return super().generic_visit(node)
    
    def get_line_node(self):
        return self._line_node

class SDEVisitor(ast.NodeVisitor):
    """用于提取敏感数据的 AST Visitor
    """

    def __init__(self):
        """SDEVisitor 构造函数
        """
        # 父结点表
        self.parent_table = dict()
        self.parent_ok = False

        # 保存所有已分析的函数
        self.analyzed_functions = dict()

        self.curr_class = None          # 当前类名
        self.var_input_maps: List[Dict] = [dict()]     # 当前函数中与输入参数有关的变量名
        self.str_input_maps: List[Dict] = [dict()]     # 当前函数中与输入参数有关的字符串常量

        # 分析阶段标记
        self.in_compare = False
        self.in_call = False

        self.related_input_name = None
        self.related_str_constant = None
    
    def get_all_const_str(self) -> list:
        """获取当前所有分析得到的字符串常量
        """

        str_set = set()
        for func in self.analyzed_functions.values():
            for _, str_values in func['str_input'].items():
                str_set.update(set(str_values))
        return list(str_set)
    
    @staticmethod
    def parse_subscript_name(root: ast.Subscript):
        flag = False
        if not isinstance(root, ast.Subscript):
            return False
        
        parsed_name = ''
        curr = root
        while isinstance(curr, ast.Subscript):
            s = curr.slice
            if isinstance(s, ast.Subscript):
                res = SDEVisitor.parse_subscript_name(s)
                if res is False:
                    return False
                parsed_name = '[{}]{}'.format(res, parsed_name)
            elif isinstance(s, ast.Str):
                parsed_name = '[{}]{}'.format(s.s, parsed_name)
            elif isinstance(s, ast.Num):
                parsed_name = '[{}]{}'.format(s.n, parsed_name)
            elif isinstance(s, ast.Name):
                parsed_name = '[{}]{}'.format(s.id, parsed_name)
            elif isinstance(s, ast.Constant):
                parsed_name = '[{}]{}'.format(s.value, parsed_name)
            
            # Add support for Python < 3.8
            elif isinstance(s, ast.Index):
                temp = s.value
                if isinstance(temp, ast.Str):
                    parsed_name = '[{}]{}'.format(temp.s, parsed_name)
                elif isinstance(temp, ast.Num):
                    parsed_name = '[{}]{}'.format(temp.n, parsed_name)
                elif isinstance(temp, ast.Name):
                    parsed_name = '[{}]{}'.format(temp.id, parsed_name)
                else:
                    logger.warning("Unsupported Index type: {}".format(s.value.__class__.__name__))
                    return False
            # elif isinstance(s, ast.UnaryOp):
            # TODO: 一元运算（负数下标处理）
            else:
                logger.warning("Unsupported slice type: {}".format(s.__class__.__name__))
                return False
            curr = curr.value
        name_lis = list()
        other = SDEVisitor.parse_local_name(curr, name_lis)
        if other is False:
            return False
        parsed_name = '{}{}'.format(name_lis[0], parsed_name)
        return parsed_name

    @staticmethod
    def parse_local_name(target, name_lis: list):
        if hasattr(target, 'id'):
            # 赋值目标为简单变量
            name_lis.append(target.id)

        elif isinstance(target, ast.Attribute):
            # 赋值目标为类对象属性，构建完整的赋值目标名称
            real_target = [target.attr]
            parent_node = target.value
            while isinstance(parent_node, ast.Attribute):
                real_target.append(parent_node.attr)
                parent_node = parent_node.value
            real_target.append(parent_node.id)
            real_target.reverse()
            name_lis.append('.'.join(real_target))
        
        elif isinstance(target, ast.Subscript):
            res = SDEVisitor.parse_subscript_name(target)
            if res is False:
                return False
            name_lis.append(res)

        else:
            # 尚未支持的赋值目标类型
            logger.warning("Unsupported assign target type [{}]".format(target.__class__.__name__))
            return False
        return True
    
    def get_path_name_by_node(self, flag: list, node: ast.AST):
        """根据 AST 结点生成完整函数路径名称

        对于不属于函数的结点，返回空文本
        :param flag: 辅助标记，用于确认末端是否为函数结点
        :param node: 分析起始 AST 结点
        """
        if isinstance(node, (ast.Module, ast.Name)):
            return ''

        parent_node = self.parent_table[node]
        
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_dot = flag[0]
            if not flag[0]:
                flag[0] = True
            res = '{}{}{}'.format(self.get_path_name_by_node(flag, parent_node), node.name, '.' if has_dot else '')
            return res
        
        if isinstance(node, ast.ClassDef):
            if flag[0] is False:
                return ''
            return '{}{}.'.format(self.get_path_name_by_node(flag, parent_node), node.name)
        
        return self.get_path_name_by_node(flag, parent_node)

    def visit(self, root: ast.AST):
        """AST 任意类型结点的访问入口
        为所有的结点添加 visited 属性，若已访问过则跳过
        """

        # 构建父结点表
        if not self.parent_ok:
            for node in ast.walk(root):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.expr_context, ast.boolop, ast.unaryop, ast.cmpop, ast.operator)):
                        continue
                    if child not in self.parent_table:
                        self.parent_table[child] = node
                    try:
                        assert self.parent_table[child] == node
                    except AssertionError:
                        print("CHILD: {}".format(child))
                        print("PARENT: {}".format(self.parent_table[child]))
                        print("NODE: {}".format(node))
                        raise
            logger.debug("Build parent table OK")
            self.parent_ok = True

        if not hasattr(root, 'visited'):
            super().visit(root)
            root.visited = True
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """AST ClassDef 类型结点访问入口
        更新 self.curr_class 标记
        """

        if self.curr_class is not None:
            # 适配多级类名
            classes = self.curr_class.split('.')
            classes.append(node.name)
            self.curr_class = '.'.join(classes)
            logger.debug("Get into class [{}]".format(self.curr_class))
            
            self.generic_visit(node)

            classes.pop()
            self.curr_class = '.'.join(classes)
        else:
            self.curr_class = node.name
            self.generic_visit(node)
            self.curr_class = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """AST FunctionDef 类型结点访问入口
        扫描输入参数
        """
        curr_func = self.get_path_name_by_node([False], node)
        # -1 += 1

        # 清空结果
        self.var_input_maps.append(dict())
        self.str_input_maps.append(dict())

        # 扫描输入参数
        args = node.args.args
        for arg in args:
            # 忽略类方法中的 self 参数
            if self.curr_class is not None and arg.arg == 'self':
                continue
                
            # 将当前参数作为关注对象，参数名称作为首个字符串类型敏感值
            self.var_input_maps[-1][arg.arg] = set([arg.arg])
            self.str_input_maps[-1][arg.arg] = set([arg.arg])
            
        self.generic_visit(node)

        logger.debug("Current function is <{}>, with params {}".format(
            curr_func, list(self.var_input_maps[-1].keys()))
        )
        logger.debug("Current function var_input_map: {}".format(self.var_input_maps[-1]))
        logger.debug("Current function str_input_map: {}".format(self.str_input_maps[-1]))

        # 记录函数扫描结果
        self.analyzed_functions[curr_func] = {
            # "name": curr_func,
            "input_names": list(self.var_input_maps[-1].keys()),
            "var_input": dict((key, list(val)) for key, val in self.var_input_maps[-1].items()),
            "str_input": dict((key, list(val)) for key, val in self.str_input_maps[-1].items()),
        }
        self.var_input_maps.pop()
        self.str_input_maps.pop()

    def visit_AugAssign(self, node: ast.AugAssign):
        """AST AugAssign 类型结点访问入口
        暂时按照与普通赋值语句相同的方式处理
        """
        node.targets = [node.target]
        self.visit_Assign(node)
        del node.targets

    def visit_Assign(self, node: ast.Assign):
        """AST Assign 类型结点访问入口
        """

        # 若当前不存在与输入相关的变量，则跳过分析
        if len(self.var_input_maps[-1]) < 1:
            return
        
        # 辅助访问函数
        def _visit(target_node: ast.AST):
            self.related_input_name = None
            self.visit(target_node)
            if self.related_input_name and len(assign_targets_ids) > 0:
                logger.debug("Assign targets {} may related to input '{}'".format(assign_targets_ids, self.related_input_name))
                self.var_input_maps[-1][self.related_input_name] |= set(assign_targets_ids)

        assign_targets_ids = list()

        # 判断赋值目标类型
        for target in node.targets:
            if isinstance(target, (ast.Name, ast.Subscript, ast.Attribute)):
                self.parse_local_name(target, assign_targets_ids)
            elif isinstance(target, ast.Tuple):
                if not hasattr(target, 'elts'):
                    raise RuntimeError("Tuple target does not have attribute 'elts' (line {})".format(target.lineno))
                for i in range(0, len(target.elts)):
                    dim = target.elts[i]
                    self.parse_local_name(dim, assign_targets_ids)
            else:
                logger.error("Unsupported assign target type: {}".format(target.__class__.__name__))
        
        # 判断赋值来源类型
        value = node.value
        if isinstance(value, ast.Tuple):
            if not hasattr(value, 'elts'):
                raise RuntimeError("Tuple value does not have attribute 'elts' (line {})".format(value.lineno))
            for i in range(0, len(value.elts)):
                dim = value.elts[i]
                _visit(dim)
        else:
            _visit(value)
        
    def visit_Name(self, node: ast.Name):
        """AST Name 类型结点访问入口
        """

        # 若当前不存在与输入相关的变量，则跳过分析
        if len(self.var_input_maps[-1]) < 1:
            return
        
        # 判断当前 Name 结点的 id 是否出现在输入参数中
        # 若存在则更新 self.related_input_name 标记
        for ipt_name, var_names in self.var_input_maps[-1].items():
            if node.id in var_names:
                self.related_input_name = ipt_name
                return

    def visit_Call(self, node: ast.Call):
        """AST Call 类型结点访问入口
        需要重点关注：函数调用时传递的参数是否存在与输入相关的字符串常量
        """

        self.in_call = True
        
        self.related_input_name = None
        if hasattr(node.func, 'value') and isinstance(node.func.value, ast.Name):
            func_value_name = node.func.value.id
            for ipt_name, var_names in self.var_input_maps[-1].items():
                if func_value_name in var_names:
                    self.related_input_name = ipt_name
        self.related_str_constant = None
        self.generic_visit(node)

        if self.related_str_constant and self.related_input_name:
            logger.debug("   call: str constant '{}' related to input '{}'".format(self.related_str_constant, self.related_input_name))
            self.str_input_maps[-1][self.related_input_name].add(self.related_str_constant)

        self.in_call = False

    def visit_Compare(self, node: ast.Compare):
        """AST Compare 类型结点访问入口
        需要重点关注：比较的目标中是否存在与输入相关的字符串常量
        """

        self.in_compare = True

        self.related_input_name = None
        self.related_str_constant = None
        self.generic_visit(node)

        if self.related_str_constant and self.related_input_name:
            logger.debug("compare: str constant '{}' related to input '{}'".format(self.related_str_constant, self.related_input_name))
            self.str_input_maps[-1][self.related_input_name].add(self.related_str_constant)

        self.in_compare = False

    def visit_Constant(self, node: ast.Constant):
        """AST Constant 类型结点访问入口
        若当前处于 Compare 或 Call 结点中，则表明该 Constant 存在与输入相关的可能性
        先记录该 Constant 的值，后续再做进一步检验
        """

        # 若当前不存在与输入相关的变量，则跳过分析
        if len(self.var_input_maps[-1]) < 1:
            return
        
        # 忽略非字符串常量
        if not isinstance(node.value, str):
            return
        
        # 检查是否在 Compare 或 Call 结构中
        if self.in_compare or self.in_call:
            self.related_str_constant = node.value
