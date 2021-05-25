# PyFuzzSDE 更新日志

## V0.0.5: 2021-05-21
- benchmarks: 进一步规范 benchmarks 结构，确定子模块版本
- benchmarks: 根据 Python-AFL 相关文档的说明改用 os._exit(0) 方法退出，提升执行效率
- benchmarks: 调整 benchmarks 命名规则，奇数编号为存在 bug 的历史版本，偶数编号为最新的 release 版本
- benchmarks: 优化 SDE 测试用例收集过程，去除了空用例和包含不可打印字符 (printable) 的用例

## V0.0.4: 2021-05-18
- runner: 调整参数名称，引入黑白名单机制，更好地支持筛选需要跟踪的内部库文件
- runner: 由于部分情况下 Coverage 库报告耗时过长，因此将 report 语句暂时移出
- benchmarks: 调整了 benchmarks 的目录结构，以子模块的方式引入被测第三方库
- benchmarks: 新增了第三方库 sympy 的测试用例 sympy-1
- ast_visitor: 针对 Python 3.8 以下版本的下标类型 (ast.Index) 进行了部分适配
- ast_visitor: 调整变量和常量存储结构 (dict -> List\[Dict\])
- ast_visitor: 针对下标访问实现了获取完整下标访问名称的方法 parse_subscript_name
- ast_visitor: 将 runner 中的方法 get_path_name_by_node 转移到 ast_visitor 中

## V0.0.3: 2021-04-21
- benchmark_01: 微调手写的 benchmark_01，以用于验证动态分析效果
- ast_visitor: 修复了少数情况下 LineVisitor 中结点与代码行对应关系错误的 BUG
- ast_visitor: 调整 SDEVisitor 中 analyzed_function 的数据结构，使其变为一个以函数名称为 key 的字典
- ast_visitor: SDEVisitor 中新增 parent_table 用于记录父子结点关系，用于函数完整名称的推导
- runner: 实现了第一版动态分析，能够通过堆栈获取欲跟踪的变量值
- runner: 修复了因提前 pop 掉本轮执行的输入数据导致产生重复数据的 BUG

## V0.0.2: 2021-04-21
- 提交了目前版本的代码
- 微调了项目文件结构
- 修复了无法分析需要 pip 安装的第三方库的 bug
- TODO: 支持识别目标带下标的赋值语句
- TODO: 开源项目 benchmarks 的设计

## V0.0.1: 2021-04-13

- 建立本工具的开源版本仓库
