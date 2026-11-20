# trace_deepread: 1793701477122_z5wxj (alan3zh@hfeg0pkn001, pnr_signoff)

- **session**: `1793701477122_z5wxj.messages.json` (1.75MB, 190 msgs, 117 user / 73 assistant)
- **source**: daily eda_trace_20261103.log + 11/04; innovus:537, synthesis:7, mc=2327 ( Innovus APR full-flow )
- **user**: alan3zh, workspace `/home/alan3zh/workspace/test_chip/test_chip_v1/` (e0031982 ssh 10.129.2.10 可读，非 owner-only)
- **flow**: test_chip_v1 Innovus APR (HL22 PDK, Au22_basic_lvt); apr/ 含 innovus_fp.tcl(842L)+innovus_pr.tcl(328L)+Makefile; logs/inv_fp.log(1430L)+inv_route.log(2103L); 真跑 INNOVUS FP DONE + PR DONE (both passed)
- **user instructions (all `<user_input>`)**: 全为 debug/根因-指向型 → A档规则②禁用:
  - msg[1] 「进入./apr/logs查看inv_fp.log，其中有告警 **WARN: (IMPSR-1253) VDD_PM ... 查询问题原因」
  - msg[66] 「读取./apr/logs/inv_fp.log，查找失败原因」
  - msg[94] 「使用方案B修改脚本」
  - msg[132] 「inv_route.log有 INNOVUS PR DONE 但 cmd 提示 route FAILED」
  - msg[181] 「报错 floorplan FAILED，且无route的log」
  - ⇒ 归 **B档 (synthesized)**：从真实工作抽取可复用 build 意图 = 通用 Innovus APR 日志审计器
- **assistant work**: editor 改 innovus_fp.tcl/innovus_pr.tcl；run_approved_command 跑 bsub Innovus；建 `_grep_invfp.py` 日志分析脚本；调试 IMPSR-1253 (VDD_PM power routing) → globalNetConnect+addStripe 修复；最终 fp+route 均 DONE
- **assets 可取**: inv_fp.log / inv_route.log 真实可 scp；innovus_fp.tcl/pr.tcl 可读 (但 Innovus 不在 .75 PATH，无法真跑 → 选日志审计 scope)
- **case scope**: B档 L2 日志审计 — deliverable = `audit_apr.py` (通用审计器, CLI `audit_apr.py <log_dir>`) + `audit_A.json`; A 可见=inv_fp.log+inv_route.log; B 隐藏=合成异构日志 (top=v2, fp FAILED, VDD_IO, IMPSR-1253:3, route DONE)
- **judgment**: check.py 23 条 a-w 独立断言 (zip 件/py_compile/subprocess 跑 A+B/与 oracle 逐码比对 status+top+warn_codes+error_codes+power_routing/跨输入守卫 B top!=A & B codes!=A)；oracle 独立解析同日志；本地自验 ref PASS 23/23 + 5 negatives 全 FAIL (NEG_RC=0) + §4.9(a)(b)(c)三假全 FAIL
- **k**: k_rationale=k_check=23 ≥8 GATE PASS
