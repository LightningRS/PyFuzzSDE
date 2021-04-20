# PyFuzzSDE 更新日志

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
