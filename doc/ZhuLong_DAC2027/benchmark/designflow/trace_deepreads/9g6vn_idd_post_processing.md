# 9g6vn 深读笔记 — IDD measurement post-processing 脚本

- session: `1792579582434_9g6vn`
- user: mengfeiz @ hfeg0plg74
- mc: 10 · domain: waveform（wv_idd = waveview IDD 测量结果后处理）
- size: 999547 bytes / 205 msgs / 11 user turns
- 关键词: waveview:22; rtl:12（mc 低但 produce 干净、规格明确）
- 用户在 D.jsonl=0（fresh user）→ 非 dup user
- 资产可达性：真实 .ods/.csv 在 mengfeiz home（/home/mengfeiz/zl_prj/idd_tree_prj/kangcheng_give_me/）ssh hfeg0plg74 可达；可 scp 取真实输入做 A-grade，或合成 B-grade。下次合成时先试 ssh 取 wv_idd_meas_result.csv 真实表头与样本行。

## 任务演化（11 user turns 原文要点）

- **U#0**：读当前目录 .ods 文件，判断 F/G/H 列，任一值<0 或 >100 → 取出该行，输出含所有此类行的文件。
- **U#25**：输出两文件里这三列数值仅保留 2 位小数。
- **U#38**：toggle_task2_t1_1022 同样筛选行 + 保留小数，结果转 .ods。
- **U#53（关键 produce 规格）**：读 toggle_task2_t1_1022.ods，按列名 `ratio_ileak`/`ratio_isc`/`ratio_isw` 三列判断：任一值<0 或 >100 → 该行取出到一个 .xlsx（文件名参数化）；剩余所有行输出到另一个 .xlsx（文件名参数化）。要一个 **python 脚本**，脚本开头是路径参数定义（输入 .ods 路径 + 两个输出 .xlsx 路径）。输出两 .xlsx：首行标题加粗 + 首行冻结；把列名 ileak/isc/isw 的列标题后加 `(uA)`，这三列数据全部 ×1e6（保留 4 位小数）转 uA。
- **U#90**：脚本中文注释全改英文。
- **U#108/U#110**：rename → `post_processing.py`。修改：列名 `ileak(A)`/`isc(A)`/`itotal(A)`/`isw(A)` 4 列内容都 ×1e6，列标题里 A 改 uA；4 列顺序调为 leak, sc, sw, total；最后三列是三个 ratio，列标题末尾加单位 `(%)`。
- **U#134**：改用 `wv_idd_meas_result.csv` 作为输入生成 hit/rest 文件；hit 版本文件名 = `wv_idd_meas_result` + `_ErrData` 后缀；rest 版本输出 `wv_idd_meas_result.xlsx`。两输出文件所有列调最合适列宽、首行标题加粗、首行 freeze。
- **U#170**：instPath 那列为啥没调到合适列宽（bug 修正）。
- **U#180**：用 post_processing.py 处理当前目录 `wv_idd_meas_result_v1.csv`，生成两 .xlsx。
- **U#199**：如何运行该脚本（命令是什么）→ CLI 用法说明。

## 金标准（最终 post_processing.py 规格）

**输入**：CSV 文件 `wv_idd_meas_result.csv`，列含：`instPath`, `ileak(A)`, `isc(A)`, `itotal(A)`, `isw(A)`, `ratio_ileak`, `ratio_isc`, `ratio_isw`（真实表头需 scp 确认，可能含额外列）。

**判定**：error row ⇔ (`ratio_ileak`<0 或 >100) ∨ (`ratio_isc`<0 或 >100) ∨ (`ratio_isw`<0 或 >100)。其余为 rest row。

**输出 2 个 .xlsx**：
1. hit（error 行）→ 文件名 = `<input_stem>_ErrData.xlsx`
2. rest（剩余行）→ 文件名 = `<input_stem>.xlsx`

**变换**：
- 4 列 `ileak(A)`/`isc(A)`/`itotal(A)`/`isw(A)`：值 ×1e6，保留 4 位小数；列标题 `A`→`uA`，并重命名为 `leak`/`sc`/`sw`/`total`（顺序调整）。
- 3 列 ratio：列标题末尾加 `(%)`（值不变？需确认——U#53 说 ratio 是判定列，U#108 说 ratio 列标题加 (%)，未说改值；下次合成假定 ratio 值原样保留，只加单位后缀）。
- `instPath` 列保留。

**格式**：首行标题加粗；首行冻结（freeze）；所有列自动最合适列宽（auto-fit）。

**CLI**：参数化——输入 CSV 路径 + 两个输出 .xlsx 路径（argparse 3 个 positional/flag）。U#199 问用法 ⇒ 必须支持命令行调用。

## B-grade 合成设计（下轮 #518 偿还合成）

- **机制**：纯 stdlib（csv + openpyxl? 但 openpyxl 非 stdlib → 沙盒可装？或用 xlsxwriter? 均非 stdlib）。⚠️ 关键：xlsx 写出需第三方库。B-grade 合成时可：(a) SUT 用 openpyxl（沙盒 pip 可装），check.py 也用 openpyxl 读回校验；或 (b) 改输出为 CSV（保机制不变，丢弃 xlsx 格式化），check.py 校验 CSV 内容。**推荐 (b)**：保「行筛选 + 单位转换 + 列重排」核心机制，输出 CSV（hit/rest），避开 xlsx 第三方依赖；格式化（bold/freeze/autofit）降为可选不强校验。这样纯 stdlib，与既有 D case 一致。
- **task family**：`IddMeasPostProcess`（IDD 测量结果行筛选+单位换算后处理）。维度正交 vs 既有：
  - #512 IddTreeAnalyze-001（b1xgb）：IDD 电流**树** bottom-up 累加 + largest_leaf，机制不同（树遍历 vs 行筛选）✓
  - #475 FsdbPowerWindowAnalysis：FSDB 波形**窗口**功耗对比，机制不同 ✓
  - #414/#413 2StepOC/AddrRtlGateMap：网表/RTL，无关 ✓
  - 无既有 case 做「CSV 行按多列阈值筛选 split + 单位换算 + 列重排」→ 非 dup ✓
- **A/B/C 不相交**：net/列名前缀、instPath 路径前缀、数值范围全不相交反硬编码。A 可见（输入 csv_A + example_output/hit_A.csv+rest_A.csv）；B 隐藏（inputs_B/wv_idd_meas_result_B.csv 植入边界值——ratio 正好=100（不超，rest）、ratio=-0.001（负，hit）、ratio=100.01（超，hit）、全 NaN/空（rest 或 skip？）测边界）；C 反硬编码嵌入 check.py（wv_idd_meas_result_C SUT 未见过）。
- **SUT**：`idd_post_process.py <input.csv> --hit <out_hit> --rest <out_rest>`，纯 stdlib（csv 模块），禁 numpy/pandas/openpyxl/subprocess/eval/exec/禁 B 字面量。输出 CSV（首行标题，逗号分隔，4 列 ×1e6 保留 4 位小数，列序 leak/sc/sw/total + 3 ratio(%) + instPath）。
- **check.py ≥8 条件**（目标 k=10）：a zip 含 SUT+无禁 import/eval/exec/B 字面量 / b py_compile / c B 退出 0 + 两 CSV 产出 / d hit 行集==oracle（ratio<0 或 >100 的行）/ e rest 行集==oracle（其余）/ f leak/sc/sw/total 4 列值==oracle（×1e6 保留 4 位）/ g 列序==oracle（leak,sc,sw,total,ratio_ileak(%),ratio_isc(%),ratio_isw(%),instPath）/ h ratio 值原样保留==oracle / i 边界值处理（=100→rest，=100.01→hit，<0→hit）/ j 反硬编码跨输入 C / k 3-seed sha256（CSV 行序无关聚合）/ l §4.9 三假（空 zip/错名/非 zip）REJECTED。≈ 11-12 条件，k≥8 ✓。
- **负样本**：empty_shell / print_only / hardcode_A（硬编码 A 行集）/ all_rest（永远不判 hit）→ 全 FAIL。
- **L 档**：L1（离线 Python CSV 处理，无 EDA 工具运行时）。⚠️ §5 新 case 偏好 L2/L3，L1 仅补牙。但本 trace 是干净真实 produce，pool 质量枯竭（P-002 第三模式），L1 可接受；下次合成时若 ssh 能取到真实 wv_idd_meas_result.csv 且含真实 waveview 产物签名可升 L2（真跑候选条件：subprocess 跑 SUT on B 即满足 §4.2）。

## 下轮 #518 偿还计划

1. ssh hfeg0plg74 scp 真实 `wv_idd_meas_result*.csv` 表头与若干样本行（确认列名/单位/数值范围）。
2. 合成 A/B/C CSV（机制：行筛选 + ×1e6 + 列重排 + ratio(%) 后缀）。
3. 写 SUT `idd_post_process.py`（纯 stdlib csv）+ check.py（≥10 条件独立 oracle）+ 3 negative + §4.9 三假。
4. 自验：ref PASS + 3 neg FAIL + 三假 REJECTED + 3-seed sha256。
5. 追加 D.jsonl + ledger mark case + 日报。

## 深读结论

干净 single-produce（11 轮全围绕同一 post_processing.py 演进，从 .ods 筛选 → xlsx split → CSV post-processing），金标准明确（U#53+U#108+U#134），fresh user，机制正交于既有 D case。下次一轮可合成交付。
