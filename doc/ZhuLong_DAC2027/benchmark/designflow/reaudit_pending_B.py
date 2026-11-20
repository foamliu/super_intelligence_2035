#!/usr/bin/env python3
"""11-15 reaudit Part 二: re-judge pool_reaudit_B.tsv 待定 rows under new standard.
New standard (2026-11-15 用户令): only two exclusions remain —
  (1) no real / inaccessible trace  (2) cannot write check() with teeth (no verifiable deliverable).
analysis-Q&A / doc-search / debug-Q&A / env-config / setup / retrieval / explain / produce
all revive to 可造. Wrong-shard-for-B (non-spice_char dominant) and dup clusters stay 不可造-for-B.
Genuinely ambiguous (empty hint, raw-number hint, old-rule-only reject reason) stay 待定.
"""
import csv, sys

SRC = "designflow/pool_reaudit_B.tsv"
OUT = "designflow/pool_reaudit_B.tsv"  # rewrite in place (keep original rows, flip col7/col8 for resolved)
LOG = "designflow/.reaudit_tmp/reaudit_pending_log.tsv"

# (substring, judgment, reason) — ordered; first match wins. Applied to col6 (旧判定 hint).
# judgment in {可造, 不可造}
RULES = [
    # ---- 不可造: no accessible trace / phantom / file gone / unreachable ----
    ("phantom", "不可造", "无真实 trace: session 文件在可达主机上找不到 (criterion 1)"),
    ("unreachable", "不可造", "无真实 trace: 主机不可达/无文件 (criterion 1)"),
    ("file gone", "不可造", "无真实 trace: session 文件已消失 (criterion 1)"),
    ("file not found on .75", "不可造", "无真实 trace: .75 上文件不存在 (criterion 1)"),
    ("file deleted by active user", "不可造", "无真实 trace: 用户已删除文件 (criterion 1)"),
    ("session file GC'd", "不可造", "无真实 trace: session 文件被 GC (criterion 1)"),
    ("session NOT FOUND", "不可造", "无真实 trace: session 文件不存在 (criterion 1)"),
    ("unlocatable on recorded host", "不可造", "无真实 trace: 记录主机上定位不到 (criterion 1)"),
    ("not readable by e0031982", "不可造", "无真实 trace: e0031982 身份不可读 (criterion 1)"),
    ("inaccessible host", "不可造", "无真实 trace: 主机不可达 (criterion 1)"),
    ("prior-rejected old+software-dev", "不可造", "非 EDA: 软件开发非设计流任务"),
    # ---- 不可造: trivial / greeting / no user text / meta ----
    ("no_user_text", "不可造", "无真实用户意图: 无用户文本输入"),
    ("no-user-text", "不可造", "无真实用户意图: 无用户文本输入"),
    ("trivial-hi", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("trivial hello", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("trivial: USER", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("trivial: hello", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("trivial greeting", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("trivial hello+paste", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("hello/speak-chinese trivial", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("裸hi问候", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("裸问候", "不可造", "无真实用户意图: 问候/琐碎会话"),
    ("'你可以干什么'", "不可造", "无真实用户意图: 能力询问(meta)"),
    ("what model are you", "不可造", "无真实用户意图: meta 测试会话"),
    ("meta/test session", "不可造", "无真实用户意图: meta 测试会话"),
    ("meta-exploration", "不可造", "无真实用户意图: agent 自省 meta 会话"),
    ("meta/infra: skill-creator", "不可造", "无真实用户意图: meta-skill 编写"),
    ("meta-skill writing", "不可造", "无真实用户意图: meta-skill 编写"),
    ("skill-authoring", "不可造", "无真实用户意图: skill 编写(meta)"),
    ("skill-authoring-meta", "不可造", "无真实用户意图: skill 编写(meta)"),
    ("skill-loading: aether hello world", "不可造", "无真实用户意图: skill hello-world 加载"),
    ("skill-loading: virtuoso hello world", "不可造", "无真实用户意图: skill hello-world 加载"),
    ("skill-loading cimi-kb-search", "不可造", "无真实用户意图: skill 加载"),
    ("skill-loading: dqtool", "不可造", "无真实用户意图: skill 加载"),
    ("context-engineering skill-loading", "不可造", "无真实用户意图: skill 加载"),
    ("TCAD deck setup skill-loading", "不可造", "无真实用户意图: skill 加载"),
    ("kanban app session", "不可造", "无真实用户意图: kanban app 非 cline coding 会话"),
    ("session history meta", "不可造", "无真实用户意图: meta 会话"),
    ("aether bridge meta trivial", "不可造", "无真实用户意图: meta 会话"),
    ("agent-policy writableRoot write-test", "不可造", "无真实用户意图: 策略测试"),
    ("eval-user", "不可造", "无真实用户意图: eval/scout 用户"),
    ("scout_1108_20", "不可造", "无真实用户意图: scout/eval 会话"),
    ("scout_1111", "不可造", "无真实用户意图: advisory 非 design_flow"),
    ("scout__", "不可造", "无真实用户意图: scout/eval 会话"),
    ("REJECT eval user", "不可造", "无真实用户意图: scout/eval 会话"),
    ("sagequan@hfeg0pnd002 meta-testing", "不可造", "无真实用户意图: harness meta 测试非 EDA"),
    ("demo not real need", "不可造", "无真实用户意图: 模板触发/演示非真实需求"),
    ("模板触发, 非真实需求", "不可造", "无真实用户意图: 模板触发/演示非真实需求"),
    ("first_user=00 续指垃圾", "不可造", "无真实用户意图: 续指垃圾会话"),
    ("context-paste", "不可造", "无真实用户意图: 上下文粘贴首轮非任务"),
    ("context-setting", "不可造", "无真实用户意图: 上下文设置非任务"),
    ("首消息非任务轮", "不可造", "无真实用户意图: 首消息非任务轮"),
    ("raw SKILL cckExplore log, not cline session", "不可造", "无真实用户意图: 非 cline session"),
    ("tool discovery", "不可造", "无真实用户意图: 工具发现(which)非任务"),
    ("fresh-kw0 trivial", "不可造", "无真实用户意图: 琐碎会话"),
    ("low-quality scatter", "不可造", "无真实用户意图: 低质量散点会话"),
    ("trivial small session", "不可造", "无真实用户意图: 琐碎小会话"),
    ("trivial: 10msgs", "不可造", "无真实用户意图: 琐碎小会话无 spice"),
    ("trivial: 4msgs", "不可造", "无真实用户意图: 琐碎小会话无 spice"),
    ("trivial: 5msgs", "不可造", "无真实用户意图: 琐碎小会话无 spice"),
    ("trivial-file-ops", "不可造", "无真实用户意图: 琐碎文件操作"),
    ("1109cron-diff", "不可造", "无真实用户意图: cron-diff 琐碎/无用户文本"),
    ("11-11 fresh spice>=5: trivial 1msg", "不可造", "无真实用户意图: 琐碎单消息"),
    (" SpiceAgent-skill-session-run-sim-trivial", "不可造", "无真实用户意图: skill run-sim 琐碎"),
    ("SpiceAgent-skill-session-run-sim-trivial", "不可造", "无真实用户意图: skill run-sim 琐碎"),
    ("trivial: launch sim scenario", "不可造", "无真实用户意图: 模板触发场景非真实需求"),
    ("non-task (wnyu", "不可造", "无真实用户意图: chit-chat/作业抱怨非任务"),
    ("greeting/meta test session", "不可造", "无真实用户意图: 问候/meta 测试"),
    ("单字符菜单选择, 无意图", "不可造", "无真实用户意图: 单字符菜单选择无意图"),
    ("peek GUI open virtuoso run SKILL reject", "不可造", "无真实用户意图: GUI skill 执行"),
    ("automate SKILL execution", "不可造", "无真实用户意图: skill 自动化执行(meta)"),
    ("GUI task (tkinter xval_tool)", "不可造", "非 EDA: tkinter GUI 工具开发"),
    ("trivial-GUI-launch", "不可造", "无真实用户意图: 琐碎 GUI 启动"),
    ("GUI trivial: open virtuoso", "不可造", "无真实用户意图: 琐碎 GUI 启动"),
    ("GUI trivial: connect virtuoso", "不可造", "无真实用户意图: 琐碎 GUI 启动"),
    ("AnaSim工具启动", "不可造", "无真实用户意图: 琐碎工具启动"),
    ("sysadmin: adjust display", "不可造", "无真实用户意图: 系统管理非 EDA"),
    ("续指垃圾", "不可造", "无真实用户意图: 垃圾会话"),
    # ---- 不可造: no verifiable deliverable / no golden (criterion 2) ----
    ("no verifiable deliverable", "不可造", "无 check() 牙: 无可验证交付物 (criterion 2)"),
    ("no file deliverable", "不可造", "无 check() 牙: 无文件交付物 (criterion 2)"),
    ("deliverable un-verif", "不可造", "无 check() 牙: 交付物不可验证 (criterion 2)"),
    ("no computational golden", "不可造", "无 check() 牙: 无计算 golden (criterion 2)"),
    ("env build/run reconstruction, no computational golden", "不可造", "无 check() 牙: 无计算 golden (criterion 2)"),
    ("synthesis_attempted_A档不达", "不可造", "无 check() 牙: trace 中运行全失败无 golden (criterion 2)"),
    ("trace incomplete: ends at clarifying ask_question, no accepted golden", "不可造", "无 check() 牙: trace 不完整无 golden (criterion 2)"),
    ("ended mid binary-format reverse-engineering", "不可造", "无 check() 牙: trace 不完整无 golden (criterion 2)"),
    ("incomplete: assistant asked question, session terminated", "不可造", "无 check() 牙: trace 不完整无结论 (criterion 2)"),
    ("incomplete trace: 5 user prompt strings only", "不可造", "无 check() 牙: trace 不完整 (criterion 2)"),
    ("kw=2 text-summarization", "不可造", "无 check() 牙: 文本摘要无 EDA 交付物 (criterion 2)"),
    ("text-summarization", "不可造", "无 check() 牙: 文本摘要无 EDA 交付物 (criterion 2)"),
    ("vague FineSim write-leveling stimulus guidance no verifiable deliverable", "不可造", "无 check() 牙: 含糊无交付物 (criterion 2)"),
    ("vague-opener", "不可造", "无真实用户意图: 含糊开场"),
    ("过于含糊", "不可造", "无真实用户意图: 含糊意图"),
    ("premise-missing", "不可造", "无真实用户意图: 裸路径/缺前提"),
    ("裸文件路径", "不可造", "无真实用户意图: 裸路径缺前提"),
    ("裸路径", "不可造", "无真实用户意图: 裸路径缺前提"),
    ("U0 skill_instructions paste no explicit user produce-turn", "不可造", "无真实用户意图: 粘贴 skill 说明无任务轮"),
    ("U0 find .lib files file-op", "不可造", "非 EDA: 纯文件操作"),
    ("U0 git init file-op", "不可造", "非 EDA: 纯文件操作"),
    ("U0 gvim edit task not design-flow", "不可造", "非 EDA: 编辑器操作非设计流"),
    ("devops desktop-cleanup", "不可造", "非 EDA: devops 清理"),
    ("devops netlist-cleanup", "不可造", "非 EDA: devops 清理"),
    ("disk-scanner", "不可造", "非 EDA: 磁盘扫描工具"),
    ("file-management-movedesktop", "不可造", "非 EDA: 文件管理"),
    ("file split generic linux", "不可造", "非 EDA: 通用 linux 文件操作"),
    ("gzip-cmd trivial file-op", "不可造", "非 EDA: 文件操作"),
    ("workspace upload ops", "不可造", "非 EDA: 工作区上传操作"),
    ("cleanup_py_sh", "不可造", "非 EDA: 脚本清理"),
    ("post-snap fresh: desktop-file-move", "不可造", "非 EDA: 桌面文件移动"),
    ("post-snap fresh: LLM-review-code refactor", "不可造", "非 EDA: 代码重构"),
    ("post-snap fresh: status-check", "不可造", "无真实用户意图: 状态检查非任务"),
    ("post-snap fresh: handoff-context-restore", "不可造", "无真实用户意图: 上下文恢复非任务"),
    ("qt cpp jobmonitor", "不可造", "非 EDA: cpp 软件开发"),
    ("interactive job-polling", "不可造", "无真实用户意图: 作业监控非任务"),
    ("job-polling/monitoring", "不可造", "无真实用户意图: 作业监控非任务"),
    ("lsf live job monitoring", "不可造", "无真实用户意图: 作业监控非任务"),
    ("bsub作业监控", "不可造", "无真实用户意图: 作业监控非任务"),
    ("ops btop job-submit", "不可造", "无真实用户意图: 作业提交监控"),
    ("git版本排障", "不可造", "非 EDA: git 排障"),
    ("shell命令检查", "不可造", "非 EDA: shell 命令检查"),
    ("wrong-type", "不可造", "无真实用户意图: skill 执行非 design_flow"),
    ("cell_list_no_need", "不可造", "无真实用户意图: 用户明确表示不需要"),
    ("env probing", "不可造", "无真实用户意图: 环境探测非任务"),
    # ---- 不可造: wrong-shard-for-B (non-spice_char dominant) / cross-domain ----
    ("non-B-dominant", "不可造", "wrong-shard-for-B: 非 spice_char 主导"),
    ("Aether-setup session (non-B", "不可造", "wrong-shard-for-B: aether 主导属 C 域"),
    ("waveview waveform open (cross-domain shard D)", "不可造", "wrong-shard-for-B: waveview 属 D 域"),
    ("waveform compare_wave -reuse edit = shard D", "不可造", "wrong-shard-for-B: waveform 属 D 域"),
    ("DRC shardC resume", "不可造", "wrong-shard-for-B: DRC 属 C 域"),
    ("fails-strict-filter", "不可造", "wrong-shard-for-B: spice 关键词占比极低非 B 主导"),
    ("not B-domain", "不可造", "wrong-shard-for-B: 非 B 域"),
    ("waveform-image-merge-iwave-not-B-produce", "不可造", "wrong-shard-for-B: waveform 属 D 域"),
    ("waveform-toggle-read-ncsim-trn-not-B-produce", "不可造", "wrong-shard-for-B: ncsim 波形属 D 域"),
    ("ddr-lpddr-regression-run-verify-not-B-produce", "不可造", "wrong-shard-for-B: regression verify 属 A 域"),
    ("non-B mislabel: SKILL/PDK code-reading", "不可造", "wrong-shard-for-B: 纯 skill 代码阅读无 sim"),
    ("async_fifo_rtl", "不可造", "wrong-shard-for-B: RTL 属 A 域(digital)"),
    ("bensonh:waveform GUI", "不可造", "wrong-shard-for-B: waveform 属 D 域"),
    ("Python xval_tool debug, not B-domain", "不可造", "wrong-shard-for-B: Python 工具调试非 B 域"),
    # ---- 不可造: dup cluster ----
    ("P-004 joeyl WCK cluster sibling", "不可造", "dup: joeyl WCK cluster 已有 case"),
    ("P-004 joeyl WCK bias", "不可造", "dup: joeyl WCK cluster 已有 case"),
    ("jiangbaol P-004 cluster sibling", "不可造", "dup: P-004 cluster 已有 case"),
    ("P-004 repeat", "不可造", "dup: P-004 cluster 已有 case"),
    ("joeyl:file gone", "不可造", "无真实 trace + dup: joeyl cluster 文件消失"),
    ("joeyl:file not found", "不可造", "无真实 trace + dup: joeyl cluster 文件消失"),
    # ---- 不可造: archive / non-EDA ----
    ("archive-JSONL", "不可造", "非 EDA: 归档操作"),
    ("r533 daily-log NEW; USER#0=你好", "不可造", "无真实用户意图: 问候"),
    ("non-produce session (cd ~/.agents)", "不可造", "无真实用户意图: cd ~/.agents 非任务"),
    ("non-produce: 'hello'", "不可造", "无真实用户意图: hello 测试会话"),
    ("gui task (tkinter xval_tool)", "不可造", "非 EDA: tkinter GUI 工具开发"),
    ("handoff resume context summary", "不可造", "无真实用户意图: 上下文恢复摘要非任务"),
    ("handoff-resume", "不可造", "无真实用户意图: 上下文恢复非任务"),
    # ---- 可造: debug-Q&A (revived) ----
    ("debug finesim", "可造", "debug-Q&A: finesim 报错根因诊断(11-15 新标准恢复)"),
    ("debug IR-result-missing", "可造", "debug-Q&A: IR 结果缺失诊断(11-15 新标准恢复)"),
    ("debug power-meas-inst", "可造", "debug-Q&A: power-meas inst 修复迭代诊断(11-15 新标准恢复)"),
    ("debug optimize报错", "可造", "debug-Q&A: optimize 报错根因诊断(11-15 新标准恢复)"),
    ("debugging optimize报错", "可造", "debug-Q&A: optimize 报错根因诊断(11-15 新标准恢复)"),
    ("SiliconSmart char hspice rc=1", "可造", "debug-Q&A: SiliconSmart characterization 报错诊断(11-15 新标准恢复)"),
    ("gxrc error-paste", "可造", "debug-Q&A: gxrc error-paste 根因诊断(11-15 新标准恢复)"),
    ("hspice waveform hierarchy debug", "可造", "debug-Q&A: hspice 波形层级调试(11-15 新标准恢复)"),
    ("netlist compare debug", "可造", "debug-Q&A: netlist 对比调试(11-15 新标准恢复)"),
    ("netlist-creation error debug", "可造", "debug-Q&A: ADE netlister 报错诊断(11-15 新标准恢复)"),
    ("simulation-output-not-found debug", "可造", "debug-Q&A: 仿真输出缺失诊断(11-15 新标准恢复)"),
    ("grep netlist vblhh debug", "可造", "debug-Q&A: netlist debug(11-15 新标准恢复)"),
    ("run_dc_fail_diag", "可造", "debug-Q&A: DC 仿真失败诊断(11-15 新标准恢复)"),
    ("perm_denied_diag", "可造", "debug-Q&A: 权限拒绝诊断(11-15 新标准恢复)"),
    ("why_no_folder_diag", "可造", "debug-Q&A: 文件夹缺失诊断(11-15 新标准恢复)"),
    ("why_current_diff_diag", "可造", "debug-Q&A: 电流差异根因诊断(11-15 新标准恢复)"),
    ("verdi_diag", "可造", "debug-Q&A: Verdi 调试诊断(11-15 新标准恢复)"),
    ("root-cause", "可造", "debug-Q&A: 根因诊断(11-15 新标准恢复)"),
    ("rootcause", "可造", "debug-Q&A: 根因诊断(11-15 新标准恢复)"),
    ("root cause", "可造", "debug-Q&A: 根因诊断(11-15 新标准恢复)"),
    ("RON opt root-cause", "可造", "debug-Q&A: RON 单调性根因诊断(11-15 新标准恢复)"),
    ("why sim exited", "可造", "debug-Q&A: 仿真退出根因诊断(11-15 新标准恢复)"),
    ("file_not_found", "可造", "debug-Q&A: file-not-found 诊断(11-15 新标准恢复)"),
    ("aether W/L min constraint + sim error", "可造", "debug-Q&A: W/L 约束+sim error 修复诊断(11-15 新标准恢复)"),
    ("PrimeSim version output paste, debug", "可造", "debug-Q&A: PrimeSim 版本/报错诊断(11-15 新标准恢复)"),
    ("报错原因是什么", "可造", "debug-Q&A: 报错根因问答(11-15 新标准恢复)"),
    # ---- 可造: env-config / setup / troubleshooting (revived) ----
    ("env-setup", "可造", "env-config: 环境配置(11-15 新标准恢复)"),
    ("env-setup(swb-python-api-config)", "可造", "env-config: swb python api 配置(11-15 新标准恢复)"),
    ("swb-python-api配置", "可造", "env-config: swb python api 配置(11-15 新标准恢复)"),
    ("troubleshooting: Virtuoso未连接排查", "可造", "env-config: Virtuoso 连接排查(11-15 新标准恢复)"),
    ("IT troubleshooting", "可造", "env-config: IT/csh/module 排障(11-15 新标准恢复)"),
    ("lsf_sched_check", "可造", "env-config: LSF 调度检查(11-15 新标准恢复)"),
    ("sim-report-writer skill输出格式配置", "可造", "env-config: skill 输出格式配置(11-15 新标准恢复)"),
    # ---- 可造: doc-search / retrieval / knowledge-Q&A (revived) ----
    ("PDF manual reading", "可造", "doc-search: RedHawk-SC 手册检索(11-15 新标准恢复)"),
    ("DDR6 spec translation", "可造", "retrieval: DDR6 spec 翻译(11-15 新标准恢复)"),
    ("knowledge-Q", "可造", "knowledge-Q&A: .meas 科学计数法配置问答(11-15 新标准恢复)"),
    ("advisory 'which CAD tools", "可造", "retrieval/Q&A: CAD 工具咨询(11-15 新标准恢复)"),
    # ---- 可造: analysis-Q&A / explain / code-reading (revived) ----
    ("analyze_circuit_func", "可造", "explain-Q&A: 电路功能分析(11-15 新标准恢复)"),
    ("查看电路图结构", "可造", "explain-Q&A: 电路图结构讲解(11-15 新标准恢复)"),
    ("teaching", "可造", "explain-Q&A: 仿真目的讲解(11-15 新标准恢复)"),
    ("code-reading+flowchart", "可造", "analysis-Q&A: IddFlow 代码阅读+流程图(11-15 新标准恢复)"),
    ("AutoDebug code-reading", "可造", "analysis-Q&A: AutoDebug 代码阅读+对比报告(11-15 新标准恢复)"),
    ("code review runModelQA", "可造", "analysis-Q&A: runModelQA 重构 code review(11-15 新标准恢复)"),
    ("compare runModelQA.pl vs refactored", "可造", "analysis-Q&A: 多仿真器脚本对比(11-15 新标准恢复)"),
    ("lvlshft skill sizing/code-reading", "可造", "analysis-Q&A: level-shifter sizing 代码阅读(11-15 新标准恢复)"),
    ("non-B mislabel: PDK HL_hspice model library usage guide", "可造", "explain-Q&A: PDK hspice 模型库用法(11-15 新标准恢复, hspice 存在)"),
    ("open ddgoa circuit exploration", "可造", "explain-Q&A: 电路探索讲解(11-15 新标准恢复)"),
    ("lacaa 6T SRAM view circuit diagram", "可造", "explain-Q&A: SRAM 电路图讲解(11-15 新标准恢复)"),
    ("waveform recognition question", "可造", "Q&A: 波形识别问答(11-15 新标准恢复)"),
    ("deepread: wavecompare_simple", "可造", "analysis: HSPICE 波形对比 EQ 分析(11-15 新标准恢复)"),
    # ---- 可造: produce (real spice/char deliverable) ----
    ("CLEAN spice_sim multi-deck LDO", "可造", "produce: LDO SPEC 对比生成(spice_sim 干净 B 产出)"),
    ("char_paste_inst", "可造", "produce/char: characterization 器件粘贴任务"),
    ("run existing RC flow", "可造", "produce: RC flow 运行(11-15 新标准恢复)"),
    ("run-regression skill 模板替换", "可造", "produce: regression 模板替换生成"),
    ("skill-invocation-tran-sim-gen", "可造", "produce: tran-sim 生成"),
    ("perl script edit", "可造", "produce: perl 脚本编辑(EDA 脚本生成)"),
    ("noise_00", "可造", "produce/debug: spice noise 分析(.meas noise 任务)"),
    ("115msg 45-corner tr0 measure", "可造", "produce: 45-corner tr0 measure deck 任务"),
    ("incomplete trace: USER0='修改aging代码", "可造", "produce: aging 仿真分目录(意图真实, reframe 可造)"),
    ("finesim matrix sleep+exec scheduling", "可造", "produce/env: finesim matrix 调度配置(11-15 新标准恢复)"),
]

def classify(hint):
    if not hint or not hint.strip():
        return ("待定", "无 hint: 需深读 trace 判定")
    # raw-number-only hint
    if hint.strip().isdigit():
        return ("待定", "hint 为纯数字(疑似截断): 需深读 trace 判定")
    for sub, jud, why in RULES:
        if sub in hint:
            return (jud, why)
    return ("待定", "hint 无法按规则决断: 需深读 trace 判定")

rows = []
with open(SRC, newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for row in r:
        # pad
        while len(row) < 8:
            row.append("")
        rows.append(row)

flipped = []
stats = {"可造":0, "不可造":0, "待定":0}
with open(LOG, "w") as logf:
    logw = csv.writer(logf, delimiter="\t")
    logw.writerow(["line","session","user","host","mc","domain","旧col6","旧col7","新判定","理由"])
    for i, row in enumerate(rows, start=2):
        col6, col7, col8 = row[5], row[6], row[7]
        if col7 != "待定":
            stats[col7] = stats.get(col7, 0) + 1
            continue
        jud, why = classify(col6)
        stats[jud] = stats.get(jud, 0) + 1
        if jud in ("可造", "不可造"):
            row[6] = jud
            row[7] = why
            flipped.append((i, row[0], jud, why))
        logw.writerow([i, row[0], row[1], row[2], row[3], row[4], col6, col7, jud, why])

with open(OUT, "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\")
    w.writerow(header)
    for row in rows:
        w.writerow(row)

print("=== reaudit pending 待定 rows ===")
print("resolved flips:", len(flipped))
print("new stats (whole file):", stats)
# count whole-file final
from collections import Counter
final = Counter(r[6] for r in rows)
print("final col7 distribution:", dict(final))
print("log:", LOG)
print("sample flips (first 15):")
for ln, sid, jud, why in flipped[:15]:
    print(f"  L{ln} {sid} -> {jud} | {why[:60]}")
