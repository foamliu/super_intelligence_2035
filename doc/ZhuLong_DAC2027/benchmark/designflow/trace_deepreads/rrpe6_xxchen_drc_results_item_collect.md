# Deepread — 1795316615041_rrpe6 (xxchen @ hfeg0plg19, physical_verify)

- **session**: `/home/xxchen/.cline/data/sessions/1795316615041_rrpe6/` (cwd `/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1`)
- **files**: `1795316615041_rrpe6.messages.json` (dict, 375 msgs) + `1795316615041_rrpe6.messages.archive.json` (JSONL, 2 msgs) = 377 total
- **mc=703** (drc:3427;calibre:2457;.gds:366;pdk:17;pex:11;rtl:8;.lef:7;netlist:2) — pure C域 physical_verify
- **model**: deepseek-v4-flash; started 2026-11-22, ended 2026-11-23
- **与前案关系**: 同一用户/项目 (DRC_pattern_tool/0.6/device_rule1) 的延续会话，前案 wqxmx (r1040 EncloseSide2SimpleGen-001) 做 enclose_side2 pattern 生成；本会话转向 QA 验证页的 results 解析与 item 收集。trace_source 独立。

## 真实任务流（按 MSG 顺序）

### Phase 1 (MSG 2, context-summary resume): 优化 QA 验证页 + rewrite merge_results.py
- Goal: 修 QaRunner run-crash（PyQt5 signal 必须 `.emit()`）、layout/precision 调整、merge/calibre-open bug、加 "load 验证目录" 自动回填、**让 DRC-report 合并产出合法 Calibre RVE results 文件**。
- 关键: 旧 `merge_results.py` 把每个 per-cell `second_check.drc.results` 拼接，首行放 `=====cell=====` → RVE 把文件误判成 spice netlist。新格式: 单 header `<top> <precision>`（无 `=====` 分隔、无 `Rule File Pathname:` 绝对路径）、per-cell check 限定为 `<cell>_<CHECK>`、多边形 `p <seq> <n>` + `CN <cell> c 1 0 0 1 0 0 0` + 坐标。参考 `/proj/dqcop/PV/cworkdir/xxchen/GDS/drvsa/drc.res...`

### Phase 2 (MSG 3): 去掉 load 验证目录组件，只在 run 按钮后加 load 按钮
（GUI 微调，非本 case 取材点）

### Phase 3 (MSG 43): 合并 report 方式不行，改为 items 列表页 + RVE 联动
- 用户: "合并report的方式不行，会有语法错误，只能单独显示和加载各自的second_check.drc.results"
- 1) 点 open 后除 calibredrv 打开 GDS，还需弹页面列出报错 item（waive/error 两类可显隐）
- 2) 点 item 用 calibre rve 自动打开对应 second_check.drc.results
- 3) 可在 calibredrv 命令行输入 tcl 交互: `set wb [find objects -class cwbWorkBench]` + `$wb runMultiRveOnRveOutput layout.drc.results`
- **agent 设计**: 新增 `drcpv/generate/qa_results.py`（无 Qt 纯函数）`collect_items(report_dir)` 扫描各 cell results 抽 Item（cell/check/kind/count/results_path/precision），kind=check 名以 `_waive` 结尾→waive 否则 error，**只保留 count>0**。

### Phase 4 (MSG 173-174, 202): calibredrv 打开报错修复 + 推进
- crash: `QPushButton.clicked` 信号发射 bool 当成 QModelIndex 传进 `_open_selected_rve` → `'bool' object has no attribute 'row'`。修复: 按钮连无参槽 + 参数防御。

### Phase 5 (MSG 205-237): 查 calibredrv 手册，推翻 stdin 注入方案
- 手册核实: `runMultiRveOnRveOutput` 是 cwbWorkBench 方法，须在已运行 GUI 交互环境；calibredrv GUI 的 Tcl prompt 是内部 Tk 终端**不吃进程 stdin**；无 socket/fifo 注入机制。
- 5 种调用模式表；`-rve` 启动模式 `calibredrv gds -rve a.results b.results` 可一次载多结果。
- 最终方案: 点「calibre open」→ 弹按 cell 多选列表（默认隐藏 pass，显 waive/fail/error）→ 勾选多个后 `calibredrv <QA.gds> -rve <r1> <r2> ...` 一次打开。
- 新增 `parse_sum_report()` 解析 sum 报告 resultTable + skip 段 → {cell: result_type}；`collect_cells()` 把每个 cell 的 results 与 sum 类型对上。

## 真实数据格式（从 QA_RUN 真实文件确认）

### per-cell `second_check.drc.results` (Calibre RVE DRC results)
```
<top_cell> <precision>          # 首行; 有的文件首行只有精度数字(无 cell 名)
<CHECK_NAME>                    # CHECK1 / CHECK1_waive / CHECK2 / CHECK2_waive
<origins> <results> <num_drc> <Mon DD HH:MM:SS YYYY>   # 计数摘要, 如 "15 15 1 Nov 22 16:13:27 2026"; 无违规 "0 0 1 ..."
Rule File Pathname: <abs .drc path>
p <seq> <n_vertices>            # 多边形块头
<x1> <y1>                       # n_vertices 行坐标
...
p <seq2> <n2>
...
<NEXT_CHECK_NAME>
```
- 真实样例: DNW_F_012_00 (fail, precision 10000): CHECK1=15 polygons (12/12/12/18/18/18/12/12/12/4/8/10/4/4/4 verts), CHECK1_waive=15 polygons (同 CHECK1), CHECK2=0, CHECK2_waive=0
- pass cell (PW_W_000_00_p): 全 CHECK 都是 `0 0 1 ...` 无 p 块
- CoreM0C_ENC_005_01_c: CHECK2=3 polygons (4 verts each)

### sum 报告 `drcWithPatternQa.report`
```
************************drcWithPattern*****************************
failCount=1
errorCount=0
passCount=47
patternNotFoundCount=0
notCheckCount=0
waivedCount=7
skipCount=1
unusedCellCount=2166

resultTable:
+------------------+------------------+--------+
| drc              | cell             | result |
+------------------+------------------+--------+
| DNW_F_012_00     | DNW_F_012_00     | fail   |
+------------------+------------------+--------+
| DNW_W_000_00     | DNW_W_000_00     | pass   |
...
| PW_S_016_00_c    | PW_S_016_00_c    | waive  |
...
skip(1):
	PW_SKIP_00
```
- result ∈ {pass, fail, waive, error}; `skip(n):` 块下 tab 缩进 cell 名 → result_type=skip

## 本 case 取材（DrcResultsItemCollect-001, physical_verify）

取 Phase 3 + Phase 5 的**纯函数后端**子意图：per-cell DRC results 解析 + 违规 item 收集 + sum 报告 cell 级判定对齐。reframe 为离线 Python 合成（real qadrc/calibredrv env 不可达），交付 `qa_results.py` 实现:
- `Item` namedtuple(cell/check/kind/count/results_path/precision)
- `find_results_files(report_dir)` 递归扫描 + 排序绝对路径
- `parse_results(text)` 解析首行 cell/precision + CHECK 块(name/counts_line/polygons)
- `collect_items(report_dir)` 抽 count>0 item (kind=_waive→waive 否则 error; cell 首行有就用否则父目录名回退)
- `parse_sum_report(sum_path)` 解析 resultTable + skip 块 → {cell: result_type}
- `collect_cells(report_dir, sum_path)` 把 results 与 sum 判定对上, 按 path 排序
- `is_pass(result_type)` pass/n/a/""/None→True, fail/waive/error/skip→False
- CLI `collect <report_dir> [sum_path]` → JSON {items, cells}

## 判分设计
- 公开 A: sample_a/ (3 cells: DNW_F_012_00 fail / PW_S_016_00_c waive / PW_W_000_00_p pass, precision 10000) + sum.report (含 skip(1) PW_SKIP_00)
- 隐藏 B (主判分): hidden/report_dir/M2/ 4 cells (M2_ENC_008_00_c / M2_HA_014_00 / M2_S_003_00_p / M2_W_009_00), precision 1000 (≠A 10000); M2_HA_014_00 首行只精度需回退父目录名; sum 报告含 error 类型 + skip(2)
- **k=13**: ① 含可导入 qa_results.py+8 符号 ② find_results_files(B) 4 文件排序绝对 ③ parse_results cell/precision/check 名顺序 ④ 多边形计数+顶点数 ⑤ collect_items(B) 4 条全 count>0 ⑥ kind 分类含 error+waive ⑦ item results_path/precision/cell 非空 ⑧ 指定 item 存在(含 M2_HA_014_00 回退) ⑨ parse_sum_report 含 resultTable+skip(≥6 条) ⑩ collect_cells 4 条排序+result_type+precision ⑪ is_pass 双向 ⑫ subprocess CLI 3 种子子集 exit 0+合法 JSON ⑬ collect_items 子集逐条匹配+CLI count 一致(防硬编)
- §4.9 三假: empty_shell[cond2/缺符号 cond1] / print_only[cond2] / delete_core[cond3 cell 解析] 全 FAIL (negative_selftest 5 neg 全 FAIL distinct)

## 区别
- 与 DrcResultsCornerExtract-001 (laryu/scouo, DRC results 四角坐标抽取 EXTENTS+CN 变换): 本 case 解析 per-cell results 的 CHECK 块/多边形计数 + sum 报告 resultTable/skip + item 收集, 产物/断言/trace 全不同
- 与 EncloseSide2SimpleGen-001 (同 xxchen/wqxmx, enclose_side2 pattern 生成): 本 case 是 results 解析而非 pattern 生成, 子意图不同

## 状态
- reference/ + assets/ + cases/C/EDA-Eval-DesignFlow-DrcResultsItemCollect-001.json 全齐
- ref solve.py → check.py PASS (13/13); 5 neg 全 FAIL distinct
- ledger C: rrpe6 已 marked case (case_id=EDA-Eval-DesignFlow-DrcResultsItemCollect-001, 2026-11-23 07:26) — 之前 round 建了 reference/assets 但未落 case JSON (dangling), 本轮 r1041 补齐 case JSON 收口
