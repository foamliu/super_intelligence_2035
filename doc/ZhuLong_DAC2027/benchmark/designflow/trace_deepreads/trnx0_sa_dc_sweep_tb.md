# trace_deepread: 1794290579357_trnx0 — CXSA sense-amp DC sweep testbench

- **session**: `1794290579357_trnx0`
- **user / host**: t0002614 @ hfeg0plg105 (10.129.8.237)
- **mtime**: 2026-11-10 ~14:42
- **size**: 28 msgs / 2 real user turns
- **match_count**: 35 (spice keyword 命中)

## 用户意图（逐字）
- U#1 (msg#0): 「根据网表 netlist 和参考的测试网表 test.sp 帮我写仿真测试。测试设置：TT 工艺角，温度 125 摄氏度，直流仿真，vad2!=1.4V，Iso 管关闭，sel 管的栅压固定为 1.77V，OC 管和 PreEq 管的栅压扫描 1.17-1.77V，看 BL 上的电压。」
- U#2 (msg#9): 「继续完成刚刚的工作」（仅续作，未给根因）

**判定**：CLEAN produce-task ✓（提需求未给根因/修复方案）。spice_sim 域（HSPICE/FineSim 直流扫描 deck）。

## 工作目录与资产
- `/home/t0002614/workspace/ZhuLong/TestSA/`
  - `netlist`（~140K 行，扁平顶层，含 CXSA1x4_1C2A subckt、XI_msaq_fBCC_29 实例）
  - `netlistHeader` / `netlistFooter`
  - `test.sp`（参考 deck：.lib 模型库 ss corner、.inc netlist+PEX、.param pvad2=pvblh/2、.tran 10p 60n sweep Optimize）
  - `test.sp~`

## assistant 行为（28 msgs，未产出最终 deck）
- msg#1-8: 读取 netlist/test.sp，识别 CXSA 结构
- msg#10-26: 写 search_netlist.py / search3.py / search4.py 反复搜索网表顶层、CXSA 端口、PEX 文件、模型库 .lib 段
- 关键发现（msg#16）：CXSA 内部 OC 管（ntnlvio_oc）接 SaBlb↔Bla_local（栅=OcEn），PreEq 管（ntnlvio_preeq）接 SaBla/SaBlb↔inh_vad2（栅=PreEq）；Iso 关断时 BL→Sel→Bla_local→OC 管→SaBlb→PreEq 管→vad2(1.4V) 构成直流通路
- msg#26 仍在提取 XI_msaq_fBCC_29 完整实例语句 → session 结束时**未产出最终 testbench**

## 金标准（B-synthesized）
trace 未产出最终 deck ⇒ 按 trace 文档化的需求 + 参考 test.sp 结构 **B-synthesized** 复刻：
- 交付物 = `sa_dc_sweep_tb_gen.py`（读 ref_test.sp 提取 model_lib/inc_lib/netlist_inc + 读 spec.json 生成直流扫描 deck）
- 生成的 out_tb.sp：6 条 .lib（corner + corner_Array + bjt/res/nicap/diode_<corner>）、.inc netlist、.temp、vad2/Iso/Sel/扫描栅压源、.dc vOcPreeq <start> <stop> <step>、.print dc v(BL)、.measure dc、.end；不含 .tran
- 资产 A: ref_test.sp（提取自 trace 的 .lib/.inc 结构）+ spec.json（A: tt/125/1.4/0/1.77/1.17-1.77/61pts）+ netlist_stub.sp（CXSA 简化网表）+ output_format_spec.txt + task_brief.md
- 隐藏 B1: ff/-40/1.2/0/1.5/1.0-1.6/31pts；B2: ss/85/1.6/0/1.9/1.3-1.9/41pts（反硬编码）
- check.py 15 断言 a-o（zip 含脚本/py_compile/B1 exit0/corner/temp/vad2/iso/sel/sweep/print/no-tran/measure/report-json/反硬编码B2/确定性）

## 自验
- ref PASS 15/15（negative_selftest __reference__ PASS）
- 6 neg（naive_empty/hardcoded_a/only_print/empty_shell/ref_core_deleted/tran_not_dc）全 FAIL NEG_RC=0
- §4.9 三假（empty_shell→d / only_print→d / ref_core_deleted→d）全 FAIL
- 断言门 k_rationale = k_check = 15 ≥ 8 ✓
- test 字段与盘上 check.py 字节同步 sha1=3ebc87cb6a99fa486bf8b2cde03a7867d3d8b376 (8325B)
