# Deepread: vxffh (zhiyong1h, hfeg0plg80, mc24, lvs:157/calibre:24) — physical_verify

## trace_source
- user: zhiyong1h, host: hfeg0plg80 (10.129.8.120), session_file: 1795161052764_vxffh.messages.json
- match_count: 24 (lvs:157, calibre:24)
- 13 msgs, 1 user turn (single intent)

## 真实意图 (U#1)
"分析一下/proj/drgpa/V0/ver/lvs/T7/Task3_AF_AryDecCtrl2/Task3_AF_AryDecCtrl2.lvs.report 中invLx4为什么LVS不过"
→ 给定一个 Calibre LVS report 和一个目标 cell 名(invLx4),定位该 cell LVS 不过的根因。

## assistant 工具链
1. read_files lvs.report → 拿到 OVERALL=INCORRECT banner + Error/Warning 行 + CELL SUMMARY + invLx4 段(Initial Numbers: Ports 6v5*/Nets 7v5*/Inst MN2v1 MP2v1; Statistics 4 mos reduced to 2; Extra Ports=4; Isolated Nets=vss!; INCORRECT NETS 段)
2. read_files lvs.report (续读) → 拿到 INCORRECT NETS: net vcc! (layout 2 conn vs source 3), M2 MP(ptn) pin s=6(layout) ↔ s=vcc!(source) 即 PMOS source 悬浮在网"6"而非 vcc!; net 6 (layout only)
3. list_allowed_files → 看到 .cdl/.sp/.gds/runlvs.log 等
4. read_files .cdl + .sp → 对比 source CDL(inv subckt, PMOS source=vcc!) vs layout SP(invLx4 4 mos, PMOS source=网"6")
5. 输出根因分析: layout invLx4 有 4 mos(2N+2P) 中间网"5""6", PMOS source 接到额外端口网"6"而非 vcc!, 导致 extra port + net mismatch + connectivity error

## 合成 (reframe debug-Q&A → generative)
抽「解析 Calibre LVS report + 目标 cell → 结构化 JSON 诊断」可交付意图:
- overall_verdict (CORRECT/INCORRECT banner 解析)
- error_categories / warning_categories (Error:/Warning: 行)
- cell_summary (Result/Layout/Source 表)
- 目标 cell 段: ports/nets/instances (layout vs source + mismatch *), extra_ports, isolated_nets, correspondence_ports, incorrect_nets (net 级 pin mismatch + layout-only net)

## 自包含 fixtures
- visible A: lvs_report_A.txt (Calibre-style 简化报告, 3 cell: invLx4 INCORRECT + 2 CORRECT), _gen_assets.py 生成
- hidden B: check.py 内嵌 _gen_b() 生成不同报告(5 cell: 3 INCORRECT + 2 CORRECT, 不同 cell 名/端口数/网名/器件/不匹配模式)
- reference_solution: lvs_diag_ref.py (regex 解析报告 → JSON)
- check.py 19 条独立断言, return True/False 严守判分契约
- negative: empty_stub / print_only / delete_core 三假 + negative_selftest.py

## 判分要点
- 真跑候选: subprocess 跑 lvs_diag.py on B report, 解析 JSON 字段比较(非文本相似)
- 随机化: 3 个 INCORRECT cell 跑 3 次, 结果与 spec 一致
- 反硬编: lvs_diag.py 不含 A 的 cell 名 "invLx4"
- §4.9 三假全 FAIL
