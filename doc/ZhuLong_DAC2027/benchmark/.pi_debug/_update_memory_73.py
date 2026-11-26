import pathlib
p = pathlib.Path('agent_workspace/MEMORY_DESIGNFLOW.md')
lines = p.read_text(encoding='utf-8').split('\n')

new_curr = ("- **当前动作**: 第73轮——**pnr_signoff 扩量第 3 条 PnRSignoff-003 (PrimeTime STA cshell launcher 审计 · csh -f "
            "module-bootstrap 陷阱) 落盘 + reference 在 .75 waveview CHECK_PASS (run_design_flow.py TCL-case-OK, 6 cases/52 "
            "asserts)；naive always-ok impl 实测 FAIL (caught at A has_module_bootstrap eq 0) 证 teeth；pi-SUT 后台跑中**。"
            "经 eda_flow open_session(BENCH-MINE,20261029-pnr3)+run_commands 从 .75 awk summary.tsv 按 primetime 命中数排序找 "
            "primetime-rich 会话。MEMORY 旧候选 thomas1w/1792056947936_36yj3 实为 netlist:805/cmos:474/analog:132/primetime:4 "
            "(netlist-rich 非 primetime-rich，描述有误)→改挖 e0046913/1792401589701_f9heo @ hfeg0plg46 (primetime:111 synopsys:649 "
            "pdk:47 hspice:12, 185 msgs)：scp messages.json 到 .75 workdir→python3 解析。真实任务=构建完整 PrimeTime STA flow "
            "(cshell launcher run_sta.csh → pt_shell -f sta_main.tcl -x \"<preset>\"，编号 tcl 1_setup..10_rpt，corner/mode 选项传参，"
            "RUN_TAG <design>_<corner>_<mode> 后缀防并行 corner 撞名，common_setup.tcl 用 `if {![info exists]}` 尊重 -x 预设)。"
            "**真实陷阱（mined agent 现场纠正，editor msg 116）**：launcher 以 `#!/bin/csh -f` 起（跳 .cshrc），tcsh 在 csh -f 下**不继承** "
            "bash 导出的 `module` 函数/别名→直接 `module purge`/`module load ds/pt/<ver>` 运行时报 'module: Command not found'。"
            "修复=在首个 module 调用**之前**定义 module alias (`alias module 'eval .../modulecmd csh !*'`) 或 `source .../modules.csh`；"
            "bash launcher 无需 bootstrap（.bashrc 已导出 module 函数）。建 pnr_signoff_audit_pt_launcher(launcher)→dict"
            "{shebang_csh_f,has_module_bootstrap,bootstrap_before_first_module_call,has_module_load_pt,has_pt_shell_x_preset,"
            "x_preset_has_design_corner_mode,has_run_tag_suffix,verdict,fail_reasons}，tcl/waveview（纯文本分析，绕 skill/aether blocker）。"
            "4 critical rules: R1(csh-f+有 module 调用须 bootstrap-before-first-call) R2(module load ds/pt) R3(pt_shell -f -x) "
            "R4(-x 预设含 set DESIGN/PT_CORNER/MODE)。test **6 cases/52 asserts**：A csh-f 无 bootstrap→broken R1（真实陷阱）；"
            "B csh-f alias-before-purge→ok（真实修复）；C csh-f source-modules.csh→ok（替代 bootstrap）；D csh-f bootstrap-在-purge-之后→"
            "broken R1（顺序 teeth）；E bash 无 bootstrap→ok（bash-无需-bootstrap teeth）；F csh-f 预设漏 set MODE→broken R4（x-preset teeth）。"
            "reference impl（POSIX [[:space:]] 类避开 waveview-Tcl 不支持的 \\b；line-index 扫描判 bootstrap-before-first-module_call；"
            "XVAR/-x 行扫描判 preset vars；`${DESIGN}_${(PT_)?CORNER}_${MODE}` tag regex）经框架 run_design_flow.py 在 .75 waveview → "
            "**TCL-case-OK / PASSED**。naive always-ok impl 实测 **FAIL**（A has_module_bootstrap assert 即被捕获）证 teeth。"
            "**test 用 @D@/@B@ 占位 + global $::dch/$::btk + string map mk helper** 绕 Tcl {} brace 内 ${...}/backtick 限制（首轮 mk "
            "proc 作用域漏 $dch 报 'can't read dch' 已修为 global）。reference 落 reference/ 目录（持久化，便于复现）。"
            "**pi-SUT (deepseek-v4-pro-cloud, bg, 自验证模式: pi 调 eda_flow MCP open_session→run_code tcl/waveview 跑 checker→"
            "close_session→print DESIGN_FLOW_VERDICT) running**。36 用例/16 PASS 1 FAIL 2 draft 1 running/16 jsonl（PnRSignoff 现 3 条）。"
            "三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。")

new_next = ("- **下一步**: 第73轮 PnRSignoff-003 ref-validated PASS 已落盘，pi-SUT 后台跑（待回收结果判 pi+ref 双 PASS）。"
            "继续扩量，下轮候选：analog_context 第三条挖 hspice AC opamp 第二场景；waveform 第 6 条挖 sx_display/measure 值提取；"
            "innovus_netlist 第 4 条；physical_verify 第三条。pi 实跑 Sch-001/Digital-008/Analog-001（draft 类待沙盒修复）。")

for i, ln in enumerate(lines):
    if ln.startswith("- **当前动作**:"):
        lines[i] = new_curr
    elif ln.startswith("- **下一步**:"):
        lines[i] = new_next

p.write_text('\n'.join(lines), encoding='utf-8')
print("updated 当前动作 + 下一步; file bytes:", p.stat().st_size)
