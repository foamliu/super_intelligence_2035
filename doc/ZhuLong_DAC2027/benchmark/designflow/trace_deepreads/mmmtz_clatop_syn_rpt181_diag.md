# Deep-read: mmmtz — cla_top DC synthesis RPT-181 / vt_group_details.json debug-Q&A

**Trace**: `1793786351814_mmmtz.messages.json` · e0046913 (yutingq) @ hfeg0plg90 (10.129.2.10) · mc169
**Keywords**: icc2:345;rtl:276;netlist:256;drc:173;verilog:138;synopsys:74;pt_shell:52;synthesis;dc_shell
**Size**: 1130820 bytes · 213 msgs · 20 user turns · 30 read_files · 32 run_approved_command · 22 editor
**Ledger**: claimed r661 (digital, A-shard). **DEBT 1**: deepread done r661, synthesis planned r662.

## 用户原话（逐字, 20 turns）
- U#1: `/proj/lacaa/TV1_digital/simdir/yutingq/1103_clatop_syn/flow_cla_top 分析cla_top的综合情况`
- U#3: `1.分析RPT-181报错原因。`
- U#4/U#5: `我想知道vt_group_details.json为什么没能正常生成？`
- U#6: `我通过注释掉 dc.tcl中对于ulvt比例的判断限制（30%以下，防止边界判定问题）；修改约束，使得各种vt都被使用到的方法，已解决上述报错问题。针对最新综合结果进行分析。`
- U#7: `1.在LVT使用比例也很低的情况下，为什么会使用ULVT? 我希望禁用ulvt，尽量用lvt替代svt来解决时序问题，应如何操作？2.为了解决新增的DRC问题，我是否可以通过在约束脚本中设置set_max_trans/cap来让综合工具更加智能化，从而避免DRC问题？`
- U#8: `分析最新综合log:/proj/lacaa/.../flow_cla_top/logs`
- U#10: `如何判断出现了fanout DRC违例？`
- U#11: `至此，我认为综合迭代可以达标了。告诉我.../flow_cla_top 目录下各文件目录及内部文件分别指向什么信息、我应该重点关注什么。`
- U#12: `1.results/cla_top.mapped.sdc与输入的data/cla_top.sdc有何区别？...2.解释何为cla_top.elab.ddc,它与cla_top.first_compile.ddc有什么区别？3.ICC2_files/cla_top.v 与results/cla_top.mapped.v有何区别？4.compare_qor_data 如何用网页打开查看？`
- U#14: `接下来，我想运行formality来验证综合情况。告诉我需要的配置以及运行FM的指令`
- U#16: `接下来，我想运行sta来进行静态时序分析。告诉我需要的配置以及运行STA的指令`
- U#18-20: `分析本次STA情况` / `分析最新STA结果` / `如何补hold约束？`

## A-faithful 选轮判定
U#1 + U#3 + U#4 = 提出需求/表达目标（分析综合情况 + 分析RPT-181报错 + 为何 vt_group_details.json 没生成），未给根因/修复 → **A-faithful 合规**。U#6 给了修复（注释 ULVT 30% 限制），但 U#3/U#4 在前且独立可判分 → 取 U#1/U#3/U#4 为忠实子片（debug-Q&A），U#6 修复事实作 evidence 验证。

## cline 工具链
- list_allowed_files (18) / get_agent_policy_status: policy engine (writableRoots 限制)
- read_files (30): 读 dc.log / *.qor.rpt / check_timing.rpt / mapped.sdc / syn_filelist.f / cla_top.v / mapped.v / qor_summary.json / report_qor.rpt / report_threshold_voltage_groups.rpt / mapped.threshold.voltage.group.rpt / cla_top.sdc / mapped.v / report_constraints.rpt / dbc_psh_syn_dont_use.tcl / link_library.tcl / compare_qor_data/index.html / fm.tcl / fmv_unmatched_points.rpt / pt.tcl / global_timing.report / check_constraints.report / report_power.report
- run_approved_command (32): python-runner 跑 log 统计/行号定位/grep RPT-181/manifest/qor_data tree/LOWEST_VTH_PERCENTAGE/set_attribute threshold_voltage_group
- editor (22): 写分析报告（受 policy 限制）

## 关键事实（verbatim evidence）

### RPT-181 报错定位（dc.log, run_approved_command msg42/56）
- **line 1390**: `Information: Running write_qor_data for label 'compile' and report 'report_threshold_voltage_groups'  (RPT-190)`
- **line 1391**: `Error: Errors occurred during write_qor_data while running the 'report_threshold_voltage_groups' report.  (RPT-181)`
- **line 1709**: 第二次（label `compile_incremental`）同错 → **共 2 次**
- Error summary: `RPT-181: 2, SEC-51: 1 (license Design-Compiler-NXT-FuSa not licensed), UID-101: 2, UID-348: 1`

### report_threshold_voltage_groups.rpt（read_files msg48, verbatim）
```
Report : threshold voltage group  -analysis_effort low
Design : cla_top   Version: V-2023.12-SP5   Date: Wed Nov 4 14:02:00 2026
Vth Group   All cells          Blackbox cells    Non-blackbox cells
svt         16 (100.00%)       0 (0.00%)         16 (100.00%)
ulvt         0   (0.00%)       0 (0.00%)          0 (0.00%)  L
Low vth groups  0 (0.00%)      0 (0.00%)          0 (0.00%)
[area section: svt 2.64 (100%), ulvt 0.00, Low vth 0.00]
```
→ **只有 SVT 16 cells (100%), ULVT 0, LVT 0**。report .rpt 生成成功（2175 字节）。

### vt_group_details.json missing 机制（run_approved_command msg46/63/67 + .manifest）
- qor_data/compile/.manifest (1255 字节) **声明**应生成 `tables/vt_group_details.json`，但该文件**实际未生成**
- panel_properties.json line 101: `"vt_group_details": {"title": "Vt Group Details", "columns": ["VtGroup","VtGroupType",...]}`
- write_qor_data 两步：① 跑 report 命令 → 写 `reports/*.rpt`（**成功**）；② 从该 report 解析/查询结构化数据 → 写 `tables/*.json`（**失败**）
- **本案例**：① report_threshold_voltage_groups.rpt 成功生成（svt 100%/ulvt 0/lvt 0）；② vt_group_details.json 表数据提取失败 → RPT-181
- 根因推断：当只有单一 VT 组（仅 SVT，ULVT/LVT 均为 0）时，write_qor_data 的表提取器在处理"Low vth groups = 0"的退化分布时失败（与 LOWEST_VTH_PERCENTAGE=30 限制 + set_multi_vth 配置交互）

### dc.tcl 关键行（run_approved_command msg52/73）
- **line 102**: `set LOWEST_VTH_PERCENTAGE 30`  ← ULVT 比例上限 30%
- **line 571**: `set_attribute [get_libs *_LVT_*] -type string default_threshold_voltage_group lvt`
- **line 573/574**: `set_attribute [get_libs *_SVT_*] ... svt` ; `set_attribute [get_libs *_ULVT_*] ... ulvt` (UID-186: 2 objects each)
- **TARGET_LIBRARY (common_setup.tcl msg91/95)**: `DBCP51H180L6W25T5_BASE_{ULVT,LVT,SVT}_ssgnp_v0p675_0c_ccs.db` (3 VT 库)

### 用户修复（U#6, 验证 run_approved_command msg73/77/95/108）
- 注释掉 dc.tcl 中 ULVT 比例 30% 判断限制 + 修改约束使各 VT 都被使用
- 修复后 dc.log: `RPT-181: 0`（消失）, 仅剩 `SEC-51:1, UID-101:2, UID-348:1`（line 2137/2143/2152 多次确认）
- vt_group_details.json 生成成功

### 设计（cla_top.v, read_files msg17, verbatim）
```verilog
// Top-Level 2^N-bit CLA - parameterized by WIDTH (default 16, must be power of 2)
module cla_top #(parameter WIDTH = 16) (input [WIDTH-1:0] a,b, input cin, output [WIDTH-1:0] sum, output cout);
  wire unused_G, unused_P;
  cla_recursive #(.WIDTH(WIDTH)) u (.a(a),.b(b),.cin(cin),.sum(sum),.cout(cout),.G(unused_G),.P(unused_P));
endmodule
```
→ 16-bit CLA, 递归 (cla_top→cla_recursive(16)→4×cla4→cla2/full_adder), 纯组合逻辑无时序单元。Synopsys Design Compiler **V-2023.12-SP5**, wire load 模式。

## 合成方案（r662 落地计划）

### Case: EDA-Eval-DesignFlow-DcRpt181VtGroupDiag-001 (C-A debug-Q&A, digital, A-shard)
- **任务形态**: 用户给 DC 综合目录，要求分析综合情况 + RPT-181 报错根因 + vt_group_details.json 未生成原因。交付 = `dc_rpt181_vtgroup_diagnosis_report.json` (structured diagnosis report only)
- **A-faithful**: 用 U#1/U#3/U#4 原话作 prompt；A 资产 = trace-embedded verbatim 文件（dc.log RPT-181 段 + report_threshold_voltage_groups.rpt + .manifest + dc.tcl vt 段 + cla_top.v + common_setup.tcl 库段）
- **Generator**: `gen_dc_rpt181_diag.py --assets <dir> --outdir <dir>` 产出 report.json

### Asset A (trace-embedded verbatim, ~6 文件)
1. `dc_log_rpt181.txt` — dc.log line 1385-1395 (RPT-190/181 compile) + 1703-1713 (compile_incremental) + error summary
2. `report_threshold_voltage_groups.rpt` — verbatim (svt 16 100% / ulvt 0 / lvt 0)
3. `manifest_vtgroup.txt` — .manifest vt_group_details 声明段
4. `dc_tcl_vt_section.txt` — line 100-104 (LOWEST_VTH_PERCENTAGE 30) + 570-577 (set_attribute lvt/svt/ulvt)
5. `cla_top.v` — verbatim RTL header
6. `common_setup_libs.txt` — TARGET_LIBRARY 3 VT db

### Hidden B (anti-hardcode 变体, 全不同)
- B = 不同设计（8-bit CLA `cla8_top`）+ 不同 corner（ffnp_v0p75_125c）+ 不同 VT 分布（lvt 8 (100%) / svt 0 / ulvt 0 → 同样退化单 VT 组）+ 不同比例限制（LOWEST_VTH_PERCENTAGE 20）+ RPT-181 在 label `compile` 单次（非 2 次）+ 不同 DC 版本（V-2024.12-SP1）
- B2 = 第三变体（4-bit CLA, tt_v0p9_25c, svt+ulvt 双组均非零 → 表提取成功, 无 RPT-181, vt_group_details.json 正常生成）→ 反向判分（report 必须正确识别"无报错"情形）

### check.py 条件（k≥13, a-m）
a. report valid JSON + 必需键 (design/root_cause/mechanism/evidence/resolution/tool_version)
b. root_cause.error_code == "RPT-181"
c. root_cause.location == write_qor_data / report_threshold_voltage_groups
d. root_cause.occurrences == A 的次数（A=2 compile+compile_incremental, B=1 compile）← 隐藏输入驱动
e. mechanism 两步: ① report .rpt 成功 ② table .json 提取失败
f. evidence.vt_distribution: svt 100% / ulvt 0 / lvt 0（A）或 lvt 100%/svt 0/ulvt 0（B）← 隐藏输入驱动, 反硬编码
g. evidence.missing_file == "tables/vt_group_details.json"
h. evidence.manifest_declares_vt_group_details == true
i. resolution: 禁用/注释 LOWEST_VTH_PERCENTAGE 比例限制 + 调约束使各 VT 都被使用
j. design.name == cla_top (A) / cla8_top (B) + WIDTH 参数 ← 隐藏输入驱动
k. tool_version == V-2023.12-SP5 (A) / V-2024.12-SP1 (B) ← 隐藏输入驱动
l. B-judge-selfcheck: 内嵌 _parse_dc_log 解析 B 的 dc_log, 独立验证 occurrences/vt_dist/version (≥6 维全异于 A)
m. 3-seed 确定性 sha256

### 自验计划（r662）
- ref PASS 13/13 + ≥3 negatives (empty→a/hardcode_a→f/print→c/wrong_mechanism→e/naive→h) distinct first_fail + §4.9 三假 (空壳/print-only/delete-core) 全 FAIL + k_rationale==k_check==13 ✓
- check.py 自包含 (A/B_FILES base64-inlined, 无 __file__ 依赖)

## 教训
1. **infra 已恢复**: ssh as e0031982 via eda_flow run_commands 到 remote hosts (hfeg0pkn002/plg15/plg90) **成功**（r651/r654/r647 的 infra-block 已过时）。应推翻"远程全 denied"结论，重启远程 trace 抓取。
2. **`<user_input mode="act">` 是 cline UI 输入包装**，非 synthetic 标志。suz5p/mmmtz 内含真实具体任务（具体路径/多轮/真实意图）。gqt57 U#1 "启动业务场景: 数字 RTL 设计" 较泛化（已 parked）。
3. **reo1p-batch 候选重判**: wohc2(B spice_sim parked) / 7kyrv(parked wrong-domain) / lp4xw(已落 D FineSimDeckReport-001) / jju5b(C physical_verify NOFILE .75local)。**mmmtz 是该批唯一 genuine A-domain fresh 候选**。
4. **DC write_qor_data RPT-181 是 debug-Q&A 好范式**: 两步机制 (report OK / table fail) + .manifest 声明 vs 文件缺失 + VT 退化分布根因 + 用户修复验证 → 13 条件天然丰富。
5. **A-domain 池未枯竭**: mc≥10 关键词重扫发现 5 条 fresh A-domain 候选 (gqt57/suz5p/w4uy2/mmmtz/i7eyp) 均未 ledgered + 远程可读。mmmtz 选定，余 4 条待 r662+ 评估。
