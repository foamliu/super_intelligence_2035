import pathlib, re
p = pathlib.Path('agent_workspace/MEMORY_DESIGNFLOW.md')
lines = p.read_text(encoding='utf-8').split('\n')
for i, ln in enumerate(lines):
    if ln.startswith("- **当前动作**:"):
        # Replace the entire (merged, bloated) line with a concise version.
        lines[i] = ("- **当前动作**: 第73轮收尾——**pnr_signoff 扩量第 3 条 PnRSignoff-003 (PrimeTime STA cshell "
                    "launcher 审计 · csh -f module-bootstrap 陷阱) pi+ref 双 PASS 已收**。pi-SUT (deepseek-v4-pro-cloud, "
                    "自验证模式 pi 调 eda_flow MCP open_session→run_code tcl/waveview 跑 checker→close_session→print "
                    "DESIGN_FLOW_VERDICT, exit=0 ~9min) → **CHECK_RESULT: PASS 6 cases / DESIGN_FLOW_VERDICT=PASS**。"
                    "reference 早前经 run_design_flow.py 在 .75 waveview → TCL-case-OK/PASSED。naive always-ok impl "
                    "实测 FAIL (A has_module_bootstrap) 证 teeth。mined e0046913/1792401589701_f9heo @ hfeg0plg46 "
                    "(primetime:111 synopsys:649, 185 msgs)；真实陷阱=#!/bin/csh -f 跳 .cshrc → tcsh 不继承 bash 导出的 "
                    "module 函数 → 直接 module purge/load 报 'module: Command not found'，修复=首个 module 调用前 alias "
                    "module (modulecmd csh) 或 source modules.csh；bash launcher 无需 bootstrap。task "
                    "pnr_signoff_audit_pt_launcher(launcher)→dict(9 keys)，tcl/waveview，4 critical rules R1/R2/R3/R4，"
                    "test 6 cases/52 asserts（A 无bootstrap→broken R1；B alias-before-purge→ok；C source-modules.csh→ok；"
                    "D bootstrap-after-purge→broken R1 顺序 teeth；E bash 无bootstrap→ok；F 预设漏MODE→broken R4）。"
                    "**pi+ref 双 PASS**。36 用例/17 PASS 1 FAIL 2 draft 0 running/16 jsonl（PnRSignoff 现 3 条全 PASS）。"
                    "三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。")
        break
p.write_text('\n'.join(lines), encoding='utf-8')
print("trimmed 当前动作; file bytes:", p.stat().st_size)
