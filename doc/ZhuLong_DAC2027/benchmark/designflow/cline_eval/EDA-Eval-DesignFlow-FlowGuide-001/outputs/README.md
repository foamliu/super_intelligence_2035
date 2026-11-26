# flow_extractor.py — EDA 设计流程会话抽取器

`flow_extractor.py` 用于从一次 EDA 设计流程 Agent 会话的记录转储
（`session_dump.json`）和工作目录文件清单（`workdir_listing.txt`）中，
自动抽取出一个结构化的 JSON manifest，帮助梳理本轮设计流程的
**进展、工具启动方式、以及关键文件的位置**。

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `scripts/flow_extractor.py` | 抽取器主程序（纯 Python 3 标准库实现） |
| `README.md` | 本说明文档 |

## 依赖

- Python 3（无需第三方库，仅使用 `json` / `re` / `os` / `sys` / `collections`）

## 用法（工具如何启动）

```bash
python3 scripts/flow_extractor.py <session_dump.json> <workdir_listing.txt>
```

例如：

```bash
python3 scripts/flow_extractor.py session_dump.json workdir_listing.txt
# 或重定向到文件
python3 scripts/flow_extractor.py session_dump.json workdir_listing.txt > manifest.json
```

运行后，一个 JSON 对象会打印到 **stdout**，始终包含 16 个字段：

```json
{
  "design": "mac_top",
  "workdir": "/path/to/workdir",
  "process": "28nm",
  "num_cells": 152384,
  "num_nets": 167201,
  "innovus_version": "Innovus v21.15-s110_1",
  "starrc_version": "StarRC XT v2021.1",
  "tools_launched": ["innovus", "starrc", "pt_shell"],
  "key_scripts": ["scripts/run_innovus.tcl"],
  "key_result_files": ["results/timing.rpt", "results/mac_top.spef"],
  "timing_wns": -0.1234,
  "timing_tns": -45.67,
  "spef_coverage_pct": 98.75,
  "num_violations": 3,
  "crit_path_levels": 42,
  "crit_path_endpoint": "mac_top/u_core/acc_reg[31]/D"
}
```

## 输入文件（关键文件在哪里）

1. `session_dump.json`
   - Agent 会话转储，可接受多种布局：JSON 对象、消息列表、嵌套的
     `content` 字段等。即使不是合法 JSON（纯文本日志），也可降级解析。

2. `workdir_listing.txt`
   - 工作目录的文件清单，兼容 `ls -lR`、`find`、`tree` 以及扁平文件列表等格式。
   - 脚本会从中推断 `workdir`，并识别关键脚本（`key_scripts`）与结果文件
     （`key_result_files`）。

> 关键脚本与结果文件的产生规则：脚本后缀（`.tcl` `.sh` `.py` `.sdc` 等）归入
> `key_scripts`；结果/中间产物后缀（`.rpt` `.spef` `.sdf` `.v` `.def` `.gds` 等）
> 归入 `key_result_files`。

## 输出字段说明

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `design` | `str \| null` | 顶层设计 / 模块名 |
| `workdir` | `str \| null` | 工作目录绝对路径 |
| `process` | `str \| null` | 工艺节点（如 `28nm`） |
| `num_cells` | `int \| null` | 单元 / 实例数 |
| `num_nets` | `int \| null` | 线网数 |
| `innovus_version` | `str \| null` | Innovus 版本 |
| `starrc_version` | `str \| null` | StarRC 版本 |
| `tools_launched` | `list[str]` | 本轮启动的 EDA 工具 |
| `key_scripts` | `list[str]` | 关键脚本（相对路径） |
| `key_result_files` | `list[str]` | 关键结果文件（相对路径） |
| `timing_wns` | `float \| null` | 最坏负 Slack（WNS，ns） |
| `timing_tns` | `float \| null` | 总负 Slack（TNS，ns） |
| `spef_coverage_pct` | `float \| null` | SPEF 寄生抽取覆盖率（%） |
| `num_violations` | `int \| null` | DRC / 违例数量 |
| `crit_path_levels` | `int \| null` | 关键路径逻辑级数 |
| `crit_path_endpoint` | `str \| null` | 关键路径终点 pin |

- 所有字段**始终存在**；无法检测到的字段输出 `null`（列表字段输出 `[]`）。
- 抽取逻辑是「容错」设计：优先读取结构化字段，再用正则从原始文本兜底。

## 复现步骤

1. 准备 `session_dump.json` 与 `workdir_listing.txt` 两个输入文件。
2. 运行：

   ```bash
   python3 scripts/flow_extractor.py session_dump.json workdir_listing.txt
   ```

3. 将 stdout 的 JSON 保存为 `manifest.json`，即可查看设计名、工艺、
   规模、工具、时序、覆盖率、违例与关键文件等关键信息。