# r638 深读：cuij / 1792459904666_ajszr — PG fill summary log 按坐标数量排序

## trace_source
- user: cuij
- host: hfeg0plg36 (10.129.32.46)
- session: 1792459904666_ajszr.messages.json
- match_count: 23 (drc:25;lvs:24;pyaether:5;aether:4)
- domain: physical_verify (PG fill 输出汇总日志处理)
- nmsgs: 34 / 2 real user turns

## 用户真实意图（逐字）
- U#0（msg[0]）：`你能读取这个文件吗 /rundata/dscqa/V0_20261015_FullChip_LVSClean/ver/drc/dscqa_top/Channel/genPowerFill/bf/test5/Channel_auto_pgfill_output_summary.log`
- U#1（msg[29]）：`帮我写一段代码，每一行都按照空格分列，可以分成三列，计算第三列的坐标数量，根据坐标数量的大小重新对log的行进行排序，数量由小到大排序。`

两轮都是「提出需求 / 表达目标」型用户轮，未给出根因或修复方案 → 符合 A 档选轮规则；U#1 是核心 produce-task。

## 文件与结构
- `Channel_auto_pgfill_output_summary.log`：727 MB（726,960,782 字节），3507 行，单行最长 308 MB，平均 ~207 KB/行。
- 每行格式（agent 分析得出）：
  ```
  column:<n>/<方向>/row:<n>/xspace:<v>/yspace:<v> <数量> <X:Y,X:Y,...>
  ```
  - 方向：`horizontal` 或 `vertical`（vertical 把 `vertical` 放在 `row:` 后）
  - 第一列：元数据前缀（无空格，用 `/` 分隔）
  - 第二列：声明的坐标数量（如 210）
  - 第三列：逗号分隔的 `X:Y` 坐标对
- 示例：
  - `column:8.0/horizontal/row:1.0/xspace:0.351/yspace:0.351 210 -20359.6274:16055.2505,19093.2126:16134.4555,...`
  - `column:8.0/row:1.0/vertical/xspace:0.351/yspace:0.351 210 10704.2014:15266.1300,...`
- 文件无 ERROR/WARNING/FAIL/PASS/SUMMARY 等状态行，纯坐标数据。
- 用途：Channel 自动 Power/Ground Fill（PG Fill）输出汇总日志，记录 PG rail/strip 填充坐标，用于 DRC 验证前的 PG fill 生成。

## agent 工具链
- read_files（727MB 超限空返）→ run_commands（被 policy 禁）→ run_approved_command（shell-runner 需 filePath）→ list_allowed_files（确认可读）→ editor 写 `read_log_chunk.py` / `search_log.py` / `analyze_log.py` → run_approved_command python-runner 分段读取 + 搜索 + 分析结构 → 回答文件结构总结 → U#1 → editor 写 `sort_log_by_coord_count.py` → run_approved_command 跑该脚本（**code_sidecar_sigterm 超时，727MB 处理超 sidecar 时限，未跑完**）。

## gold 算法（/home/cuij/sort_log_by_coord_count.py 逐字提取）
1. 逐行读 INPUT_FILE，`line.rstrip('\n')`，跳过空行
2. `parts = line.split()`（空格分列）
3. `if len(parts) < 3: 跳过并记录警告`
4. `coord_str = parts[2]`
5. `coord_count = coord_str.count(',') + 1`（空串则 0）
6. `lines_with_counts.append((line, coord_count))`
7. `lines_with_counts.sort(key=lambda x: x[1])`（稳定升序）
8. 写出排序后日志到 OUTPUT_FILE（每行原文 + `\n`，1MB buffer）
9. 打印统计：min/max/avg + 10 个分桶（0~100 … >1,000,000）+ 最小 10 行 + 最大 10 行预览

关键点：
- 坐标数量按**逗号数 + 1**计算，**不**用第二列声明的 `<数量>` 字段（声明值常为 210，与实际坐标数无关）。
- 稳定排序（Python `list.sort` 默认稳定），相同 count 保持原相对顺序。

## case 合成
- task_id: `EDA-Eval-DesignFlow-SortPgfillLogByCount-001`
- 档：B 档（synthesized，真实 727MB 日志不可达沙盒 → 合成小规模同构日志作 asset）
- deliverable: `sort_pgfill_log.py <input.log> <output.log> <stats.json>`（读入→空格分三列→第三列逗号数+1 计数→稳定升序排序→写出排序日志 + 统计 JSON）
- asset A（可见）: `assets/SortPgfillLogByCount-001/pgfill_summary_a.log`（10 行，同构真实格式）
- 隐藏 B: `hidden/pgfill_summary_b.log`（14 行，含一条 declared=210/actual=5 测逗号计数非声明字段）
- 隐藏 B2（反硬编）: `hidden/pgfill_summary_b2.log`（12 行，含 1 条 <3 列畸形行测 skip + 1 条 declared=999/actual=2 测逗号计数，与 B 计数集不相交）
- check: 17 条 a-p(+m2)，subprocess 跑 candidate 于 B/B2，与 reference 比对 + 反硬编 + 确定性
- 自验：ref 17/17 PASS；3 neg(naive/print_expected/deleted_core) 全 FAIL；§4.9(a)(b)(c) 三假全 FAIL；embedded test==disk roundtrip PASS；k_rationale==k_check==17≥8 ✓

## 同 trace_group
`ajszr-pgfill-log-sort-by-coord-count`（cap-1）。新子型 `pg-fill-summary-log-coord-count-sort`。
