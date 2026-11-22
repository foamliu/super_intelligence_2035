# sample_a/task_brief.md

## 背景（来自真实 trace）

用户 e0039602 维护一个 Verilog 网表（`netlist`），其中有些被实例化的 cell 在参考库 `simlib_base.sv` 中不存在，导致仿真器无法直接读取。用户编写了一个确定性 Python 解析器来从网表中提取所有"缺失 cell"实例（cell 名不在 simlib 中），作为后续 AI 驱动 cell 替换流程的输入。

## 你的任务

编写一个 Python 脚本 `netlist_missing_cell_extract.py`，给定一个 Verilog 网表文件和一个 simlib 库文件，输出结构化 JSON 报告，列出所有"缺失 cell"实例（即 cell 名不在 simlib 中定义的实例）。

## 输入

- `netlist` — Verilog 网表文件路径（命令行第一个位置参数）
- `simlib` — simlib 库文件路径（命令行第二个位置参数，Verilog/SystemVerilog 语法）

## 输出

脚本必须将 JSON 报告打印到 stdout（且只打印 JSON，不要其他输出），结构如下：

```json
{
  "missing_instances": [
    {
      "line": <int, 1-based 起始行号>,
      "cell": "<cell 名>",
      "instance": "<instance 名>",
      "ports": {"<port名>": "<net表达式>", ...}
    },
    ...
  ],
  "summary": {
    "total_instances": <int, 网表中所有实例总数>,
    "missing_count": <int, 缺失实例数>,
    "available_count": <int, cell 在 simlib 中的实例数>,
    "missing_cells": ["<缺失 cell 名去重升序>", ...],
    "available_cells_used": ["<被实例化的可用 cell 名去重升序>", ...]
  }
}
```

## 解析规则

1. **simlib 模块名提取**：扫描 simlib 文件中所有 `module <name>` 声明（匹配正则 `^\s*(?:`celldefine\s*\n\s*)?module\s+(\w+)`），收集所有已定义模块名集合。
2. **网表实例提取**：扫描网表文件中的 cell 实例化语句。一个实例化语句形如：
   ```
   <cell_name> [#(...)] <instance_name> (.port(net), .port(net), ...);
   ```
   - 实例可能跨多行（端口连接可换行）。
   - `#(...)` 参数块可选；若有，跳过不解析。
   - `instance_name` 是紧跟 cell_name 的标识符。
   - 端口连接 `.port(expr)` 中，`port` 是端口名，`expr` 是连接表达式（net 名、位与 &、或 |、取反 ~、常量等）。
   - 忽略 Verilog 关键字声明的行（input/output/wire/parameter/assign/reg/inout 等）。
   - 忽略 `//` 注释行和 `/* */` 块注释。
   - 忽略 specify/endspecify 块内的内容。
3. **缺失判定**：若实例的 `cell_name` 不在 simlib 模块名集合中，则该实例为"缺失"。
4. **行号**：`line` 是该实例化语句在网表文件中的 1-based 起始行号（cell_name 所在行）。
5. **端口映射**：`ports` 字典的 key 是端口名（去掉前导 `.`），value 是连接表达式（去掉外层括号和前导 `.`，保留原始文本如 `S & net16` 或 `inh_vcc`）。

## 约束

- 只用 Python 3 标准库（re, json, sys, os 等），不依赖任何第三方 EDA 工具。
- 脚本以 `netlist_missing_cell_extract.py` 为文件名放进 `outputs/submit.zip`。
- 入口：`python netlist_missing_cell_extract.py <netlist> <simlib>` → stdout 输出 JSON。

## 参考

- sample_a/netlist_a.v 和 sample_a/simlib_a.sv 是一组示例输入（A 组，SUT 可见）。
- 隐藏的 B 组输入（结构不同、cell 名不同、规模不同）将用于实际判分。
