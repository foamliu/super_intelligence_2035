# r999 deepread — 627cp WL monitor logic-view analyze

## trace meta
- sid: `1795230004243_627cp.messages.json`
- user: lein @ hfeg0pkn005
- mc: 272 (verilog:1287;netlist:1113;drc:218;analog:58;systemverilog:50 — verilog dominant, A-pure verification)
- 228 msgs total, 18 user text msgs all act mode about LPDDR6 verification platform analysis
- scp 1.67MB via e0031982 identity, 子目录 <sid>/<sid>.messages.json

## 用户意图
U#0 (逐字): 「analyze the WL monitor logic view for the proj_monitor platform:
- what monitor type, data structs, probe module, $clog2 decode, bind targets, exp-gen, compare loop, error messages?
- produce a structured report.」

session 主线: LPDDR6 dejoa/V0 验证平台 monitor 代码学习/分析。18 turns 覆盖
WL monitor logic-view / netlist probe / hier_ary / refresh/pump monitors 等多主题。
本 case 提炼 U#0 WL monitor logic-view 分析。

## trace gold (msg#53)
助手交付 `project_wl_monitor_analysis.md`，完整 logic-view 报告，三段式架构:

### 1. 期望生成 (expected generation)
- `exp_wl_gen` 函数 (monitor_package.sv:64) 接收 logic_addr/red/bk
- 调用 `array_table_generate` 查 `array_table[32]` 表 (array_table.v) 得 sec + wl_idx
- red=1 时 wl_idx += 1344 (red_offset)
- 组装 `TYPE_WL_INFO` struct (sc/bg/ba/sec/wl_idx) push 到 `exp_wl_q`

### 2. 网表探针 (netlist probe)
- `real_wl_gen` module (proj_special_wl.sv:3844), parameter WLBITS=688 (1376/2)
- 监听 WLeL/WLoL 信号, `$clog2` 解码: `wl_idx = 2*$clog2(WLeL)` (even) / `2*$clog2(WLoL)+1` (odd)
- `hier_ary` 函数 (proj_special_wl.sv:764) 从层次路径解析 sc/bg/ba/sec (string_find "rray2G")
- `bind` 挂到 array11Meg 实例 (proj_special_wl.sv:4791): 6 bind statements (E_Top/O_Top/E_Top_sec0/E_Bot/O_Bot/E_Bot_sec0)
- push 到 `real_wl_q`

### 3. 比对报错 (compare & report)
- forever 循环 (project_wl_monitor.sv:358/404) 比对 `real_wl_q` vs `exp_wl_q`
- 匹配则 delete, 不匹配则报错:
  - "WL Error :SC:%0d,BG:%0d,BA:%0d, Expect WL was not Probe: %0p, at %0t" (期望但未探到)
  - "WL Error :SC:%0d,BG:%0d,BA:%0d, Fired WL was not Expected: %0p, at %0t" (探到但未期望)
- report cap: wl_rpt_nu < 10000
- compare delay: #10ps

## case 提炼
archetype: analysis-Q&A → produce-task (parse SV monitor files → structured JSON logic-view report)

- case_id: EDA-Eval-DesignFlow-WlMonitorLogicViewAnalyze-001
- domain: verification
- mode: design_flow
- task: 写 `analyze_wl_monitor.py` 接收 5 参 `<monitor_sv> <package_sv> <table_v> <special_sv> <output_json>`
  通用正则解析 SV 文件, 提取 15 个 JSON 字段 (monitor_type/type_info_struct/real_queue_name/
  exp_queue_name/probe_module/clog2_decode/hier_ary_function/bind_statements/exp_gen_function/
  array_table/compare_loop/error_messages/monitor_interface_class/logic_flow/positioning)

## fixtures
### A (real LPDDR6 WL monitor, trace-faithful trimmed)
- project_wl_monitor.sv (9102B) — 主 monitor 逻辑 (exp gen + compare loop + error report)
- monitor_package.sv (3038B) — TYPE_WL_INFO struct + exp_wl_gen + array_table_generate
- array_table.v (1816B) — 32 entries row→sec+wl_idx 映射表
- proj_special_wl.sv (5108B) — real_wl_gen module + hier_ary + 6 bind statements

### hidden-B (parallel DDR5 BL monitor, all concrete values different)
- project_bl_monitor.sv (6085B) — BL monitor logic
- monitor_package_bl.sv (2002B) — TYPE_BL_INFO + exp_bl_gen
- array_table_bl.v (982B) — 16 entries (A=32)
- proj_special_bl.sv (4642B) — real_bl_gen + 4 bind (A=6)

### B concrete differences from A (anti-hardcode anchors)
| field | A (WL) | B (BL) |
|---|---|---|
| monitor_type | wl | bl |
| struct name | TYPE_WL_INFO | TYPE_BL_INFO |
| struct field | wl_idx | bl_idx |
| probe module | real_wl_gen | real_bl_gen |
| param | WLBITS=688 | BLBITS=512 |
| signals | WLeL/WLoL | BLeL/BLoL |
| bind target | array11Meg | array8Meg |
| exp gen | exp_wl_gen | exp_bl_gen |
| error expect | Expect WL was not Probe | Expect BL was not Probe |
| error fired | Fired WL was not Expected | Fired BL was not Expected |
| iface class | wlmonitors | blmonitors |
| queues | real_wl_q/exp_wl_q | real_bl_q/exp_bl_q |
| array_table entries | 32 | 16 |
| red_offset | 1344 | 768 |
| bind count | 6 | 4 |
| compare delay | 10ps | 20ps |
| report cap | 10000 | 8000 |

## check.py (21 assertions)
①zip含analyze_wl_monitor.py ②py_compile通过 ③B运行exit0+有效JSON ④JSON含全部15必需key
⑤monitor_type=bl(反wl) ⑥type_info_struct.name=TYPE_BL_INFO(反TYPE_WL_INFO)
⑦fields含bl_idx(反wl_idx) ⑧probe_module.name=real_bl_gen(反real_wl_gen)
⑨param BLBITS=512(反WLBITS=688) ⑩signals BLeL/BLoL(反WLeL/WLoL)
⑪clog2 even_formula含$clog2(BLeL)(反WLeL) ⑫bind全含array8Meg(反array11Meg)
⑬exp_gen=exp_bl_gen(反exp_wl_gen) ⑭error expect含BL非WL ⑮error fired含BL非WL
⑯iface=blmonitors(反wlmonitors) ⑰queues real_bl_q/exp_bl_q(反wl_q)
⑱确定性3次md5一致 ⑲§4.9空壳<15key FAIL ⑳§4.9 print-only无def FAIL ㉑§4.9 core-deleted无re import/<200B FAIL

## self-test
- reference: 21/21 PASS (exit 0) ✅
- neg_empty: 8/21 FAIL (exit 1) ✅
- neg_print_only: 2/21 FAIL (exit 1) ✅
- neg_core_deleted: 8/21 FAIL (exit 1) ✅
- §4.9 三假全 FAIL ✅
- end-to-end: jsonl test field 提取 check.py → 21/21 PASS ✅

## ledger
- 627cp claimed in trace_ledger_A.tsv (lein/hfeg0pkn005, mc=272)
- marked: case EDA-Eval-DesignFlow-WlMonitorLogicViewAnalyze-001
- 627cp verified absent from all 4 shard ledgers before claim (r998 lesson)
- lein 同户已有 r966 yk8qc + r982 vpmdl + r997 udmg8, 不同 session 不同子任务, 无 intent-dup

## A.jsonl
456 → 457 (append r999 entry)

## 选料注
r998 fix sid 规范化后 30 fresh, r999 直接从 r995 新扫 ssh_eda_search_20261122_172249 A-pure filter
选 627cp (lein mc272 verilog:1287 A-pure verification, NEW fresh candidate verified absent from all 4 shard ledgers)
U#0 WL monitor logic-view 分析最 clean (明确 I/O 4 SV files → JSON, 三段式架构可正则提取,
WL/BL 可分离构造 hidden-B 全 concrete 值不同)
