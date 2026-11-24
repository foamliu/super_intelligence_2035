# Deep-read: 1788936621788_d52pq — jiaqis DRC rule deck scan

## Trace metadata
- **session**: 1788936621788_d52pq
- **user**: jiaqis
- **host**: hfeg0plg77 (10.129.8.121)
- **match_count**: 29
- **keywords**: drc:326;calibre:5;gdsii:1
- **scan_source**: /home/t0002965/log/ssh_eda_search_20261124_023802/summary.tsv
- **cached_file**: /tmp/d52pq.messages.json (49KB, 9 messages)
- **model**: glm-5.2 via cxmt-glm52

## User intent (real task summary)
jiaqis 在 `/home/jiaqis/work/DRC/zlworking` 目录下工作，要求 agent 扫描 `../V05_coding` 文件夹。该文件夹包含 99 个 Calibre DRC（设计规则检查）命令/规则文件，对应 CXMT 35H 工艺平台，版本 V0.1_Rev13。文件按数字编号命名（1_1_environment.drc, 1_2_layer_define.drc, 3_7_grid.drc, 4_5_*.rules 等），涵盖：
- 开关/选项定义（DBC, FRONT_END, BACK_END, FULL_CHIP, WITH_SEALRING, MIM, 电压档位）
- GDS layer map 与派生层定义（DNW, NW, PW, SLZ 等）
- 变量定义、连接关系、网格规则、金属/通孔设计规则
agent 用 ls/find/head 扫描后给出分类总结，用户要求切换中文，agent 重新总结。

## Assistant toolchain
1. `run_commands`: ls -la, find, head, wc -l 扫描 V05_coding 文件夹
2. `read_files`: 读取 1_2_layer_define.drc, voltage.rules, ts_auto 等
3. 生成结构化总结（文件分类表 + 各类别说明）

## Key artifacts (from trace)
- `1_1_environment.drc` (5KB): switch/option definitions + environment settings
- `1_2_layer_define.drc` (244KB): GDS layer map + derived layer definitions
- `1_3_variable.drc` (0KB): variable placeholder
- `1_4_global_layer_*.drc`: global layer diff/same
- `1_5_connection.drc` (21KB): connection definitions
- `3_7_grid.drc` (1.4MB): grid rule checks
- `4_5_*.rules` / `4_6_*.drc` / `4_8_*.rules`: design rules (metal, via, etc.)
- `ts_auto`: batch driver script

Calibre SVRF syntax observed:
- `LAYER MAP <gds_num> DATATYPE <dt> <internal_num>`
- `LAYER <name> <internal_num>`
- `VARIABLE <name> <value>`
- `$<switch> = <value>`
- Rule blocks: `@ comment` + keyword checks

## Reframe note
A-faithful reframe: 基于真实 trace 中 V05_coding DRC deck 的文件结构和 Calibre SVRF 语法，reframe 为纯 stdlib 文件解析+JSON 报告 produce-task。SUT 须编写 solve.py 解析 DRC 规则文件目录，提取 switches/layer_map/layer_names/variables/rule_count 等结构化信息，输出 JSON 审计报告。track=C (physical_verify)；hidden B 使用不同 switch/layer/variable/rule 内容。
