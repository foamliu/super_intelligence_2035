# trace_deepread: 1795316615041_rrpe6 (xxchen @ hfeg0plg18, mc=703, physical_verify)

## 真实用户与场景
xxchen 是 DRC pattern 验证 GUI 工具 `drcpv`（PyQt5，位于 `/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1/`）的维护者。该工具用于 IC 设计中 DRC（Design Rule Check）pattern 验证：对每个 cell 跑 qadrc `-ci drcWithPattern`，产出 per-cell `second_check.drc.results` 文件 + 一份 sum 报告（`drcWithPatternQa.report`），再用 calibredrv + RVE 打开 GDS / results 查看报错。

## 用户真实意图（trace 流）
1. **rev1（msg[1]）**：去掉之前加的「load 验证目录」整行组件，只在 run 按钮后加一个 load 按钮 —— 小重构。
2. **rev4（msg[41]，核心）**：「合并 report 的方式不行，会有语法错误，只能单独显示和加载各自的 second_check.drc.results」。要求：
   - 点 open 后，除了 calibredrv 打开 GDS，还要弹一个页面列出当前报错的 item 项，waive / error 两种类型可分别显示隐藏。
   - 在页面点对应 item 后用 calibre RVE 自动打开对应的 `second_check.drc.results`。
   - 给了 TCL 交互范例：`set wb [find objects -class cwbWorkBench]` / `$wb runMultiRveOnRveOutput layout.drc.results`。
3. **后续（msg[171+]）**：calibredrv 打开报错（QGuiApplication / `index.row()` AttributeError），逐个修。

## 关键产物（agent 实现）
后端纯函数模块 `drcpv/generate/qa_results.py`（无 Qt 依赖，便于 py3.7 侧单测），是本次任务的可抽离交付核心：

- `find_results_files(report_dir)` — 递归找全部 `second_check.drc.results`，sorted。
- `read_results(path)` — 读文件，rstrip("\n")。
- `parse_results(text)` — 解析 per-cell results：
  - 首行 `<cell> <precision>`（也兼容 precision-only / cell-only 头）。
  - 每个 CHECK 块 = 名字 + counts/date 行（`<c1> <c2> 1 Mon day time year`）+ `Rule File Pathname:` 行（忽略）+ `p <seq> <nverts>` 多边形块（后跟 nverts 行 `x y` 坐标）。
  - 返回 `{cell, precision, checks:[{name, counts_line, polygons:[[(x,y),...]]}]}`。
- `_kind_of(name)` — check 名以 `_waive` 结尾 → `waive`，否则 `error`。
- `collect_items(report_dir)` — 收集 count>0 的 item（`Item(cell,check,kind,count,results_path,precision)`），sorted by path。
- `parse_sum_report(sum_path)` — 解析 sum 报告 `resultTable:` 段（`| drc | cell | result |` 行）+ `skip(n):` 段（tab 缩进 cell 名 → result_type='skip'）→ `{cell: result_type}`。
- `collect_cells(report_dir, sum_path)` — per-cell 条目 + sum 报告的 result_type（未列出 → 'n/a'），sorted by path。
- `is_pass(result_type)` — pass/n/a/"" → True，其余 False。

## 真实数据格式（从 xxchen 机器抓取确认）
`second_check.drc.results`（有违规的 cell，例 DNW_F_012_00）：
```
DNW_F_012_00 10000
CHECK1
15 15 1 Nov 22 16:13:27 2026                   
Rule File Pathname: /home/.../DNW_F_012_00_second_check.drc
p 1 12
29999 -914000
... (12 行坐标)
p 2 12
...
```
无违规的 cell（PW_W_000_00_p）：只有 CHECK 头 + counts 行 + Rule File Pathname，没有 `p` 块。

sum 报告（`drcWithPatternQa.report`）：
```
resultTable:
+------------------+------------------+--------+
| drc              | cell             | result |
+------------------+------------------+--------+
| DNW_F_012_00     | DNW_F_012_00     | fail   |
...
| PW_S_016_00_c    | PW_S_016_00_c    | waive  |
...
skip(1):
\tPW_CL_022_00
```

## 真实教训（造题要点）
- 合并 results 文件会语法错误 → 必须 per-cell 单独解析。
- item 列表只列 count>0（真正违规/waive）的项。
- cell 名可能来自文件头，也可能要 fallback 到父目录名（精度-only 头）。
- kind 由 check 名 `_waive` 后缀判定；sum 报告的 result_type 是 cell 级别独立信号。
- 真实数据里同一 cell 既有 CHECK1 也有 CHECK1_waive，二者都可能有违规。

## case 化决策
抽离 `qa_results.py` 作为交付物（打 submit.zip）。A=sample_a（3 cell，precision 10000，DNW_F_012_00/PW_S_016_00_c/PW_W_000_00_p + sum 报告含 fail/waive/pass/skip），B=hidden（4 cell，precision 1000，M2_ENC_008_00_c/M2_S_003_00_p/M2_W_009_00/M2_HA_014_00，含 precision-only 头测试 cell fallback，sum 报告含 fail/pass/error/waive/skip(2)）。check.py 13 条断言，3 seed 子集反硬编。
