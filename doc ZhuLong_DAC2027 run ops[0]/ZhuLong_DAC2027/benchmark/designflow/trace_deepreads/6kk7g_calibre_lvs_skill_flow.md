# trace_deepread: 6kk7g — adaml calibre-lvs skill flow-driving

**session**: 1793849646244_6kk7g.messages.json
**user**: adaml @ hfeg0plg49 (10.129.8.86), also seen at hfeg0plg05/plg07
**mc**: 15 (aether:78;lvs:58;netlist:41;virtuoso:27;calibre:20;schematic:12;.cdl:9;dbopencellviewbytype:8)
**domain**: physical_verify (Calibre LVS via LSF pv queue)
**snapshot**: ssh_eda_search_20261119_172105

## trace 结构
- total_msgs: 13 (1 user_input turn + 6 assistant turns + 6 tool_results)
- user_input turns: 1 (U#0 = `<skill_instructions name="calibre-lvs">` 完整 skill spec, 不是自然语言请求)
- agent: "lead"

## U#0 真实意图 (skill spec 完整内容)
adaml 通过 calibre-lvs skill 在 HLMC HLMC_CL022UL 22nm 工艺、LSF pv 队列上跑 Calibre LVS v2020.1_36.18 (aoi 变体), 对标准单元做 GDS 版图 vs CDL 源网表一致性检查, 产出 lvs.rep, 判定 CORRECT/INCORRECT/NOT COMPARED.

skill spec 含:
- **目标与边界**: 只跑 Calibre LVS; 不在沙箱本地跑 calibre; 一律走 LSF
- **验收标准 4 条**: (1) pv 队列 DONE + STANDARD VERIFICATION RULE FILE COMPILATION MODULE COMPLETED + HLVS/LVS license acquired; (2) OVERALL COMPARISON RESULTS 给 CORRECT/INCORRECT/NOT COMPARED; (3) source 含顶层 .SUBCKT + layout 含完整器件层 → CORRECT/INCORRECT 而非 "Nothing in layout"/"Subcircuit not found"; (4) lvs.rep + sv_extract.sp + svdb/ 落盘
- **硬约束**: Calibre `/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18`; LSF `bsub -q pv`; env MGC_VCO=aoi VCO=aoi SKIP_CALIBRERC=1 MGLS_LICENSE_FILE=17000@hl01:17000@hl02 + unset LD_LIBRARY_PATH/LD_PRELOAD; PDK `/apps/imctf/extpdk/HL22/LAGAT/22HK_V0P5_0D10_for_vodka/0.0.9/Calibre/LVS/`
- **方法论**: 判输入完整 → runset 占位替换 (LAYOUT PRIMARY/PATH, SOURCE PRIMARY/PATH, MASK SVDB DIRECTORY; 保留 LAYOUT PRECISION 10000 + PRECISION 20000 勿删) → 命令行 `calibre -lvs -turbo 2 -hier -nowait <runset>` (禁 -spice/-log/-hspice) → bsub -q pv 提交 → 轮询 bjobs → tail lvs.out/err/rep
- **已知陷阱 8 行**: Usage 打印 (命令行含 -log); undefined layer psub (缺顶部 runset); precision inconsistent; Subcircuit X not found (CDL 缺顶层 .SUBCKT, .cdl.raw 常只有子电路库); Nothing in layout (GDS 只有 CT/M4); Duplicate subckt switch_* (良性); GLIBC 报错 (LD_LIBRARY_PATH 污染); Y 顶层金属 open (删 PRECISION 20000 或 -spice 传旧网表)
- **参考实现**: `scripts/run_lvs.py --cell <name> [--cell-dir <OA>] [--gds] [--cdl] [--project] [--runset] [--run]` 已在 blcnand2PFx4 验证 CORRECT, blcnand3GFx1 如实暴露 Y open INCORRECT

## assistant 行为
- idx=1: get_agent_policy_status + SandBox_MCP_Server__run_code (printf "hello, check bridge alive") — 桥接活着
- idx=4: run_approved_command ($HOME/get-username.sh — not regular file) + SandBox_MCP_Server__run_code (autoload check: auCdl defined=t, netlistRun/si/nlSetExportOptions/netlist = nil, dbOpenCellViewByType=t) — SI 框架未 attach
- idx=7: list_allowed_files (/ai_sandbox/m2701/V0_DDR4/agentdir/adaml — 列出 adaml_env_probe.txt/adaml_skill_desc.txt/backup_simreport_skill.py/backup_spice_skill.py/clean_pycache.sh/cleanup_skills.sh...) + SandBox_MCP_Server__run_code (attempt SI attach via hiGetCurrentWindow — *Error* eval: not a function - (symbol->string))
- idx=10: read_files (adaml_env_probe.txt) + SandBox_MCP_Server__run_code (list libraries — *Error* eval: undefined function - ddGetObjList)
- trace 在环境探测阶段中断, **未产出 lvs.rep / sv_extract.sp / svdb/**, 未到达 bsub calibre -lvs 步骤

## 根因 (trace 中断)
virtuoso-cli 桥接的执行上下文与交互 CIW 主内核隔离, auCdl/netlist/netlistRun/nlSetExportOptions/si 在桥接侧始终 undefined; 即使同 PID GUI 开 ADE L 跑 File→Export→CDL, SI/CDL-out 转换器也不 attach 到桥接后端. → skill spec §OpenAccess 库→GDS/CDL 第 2 条明确: "不要在桥接侧脚本化 auCdl; 这种情况直接请用户手动导 CDL."

## reframe 决策 (r835)
- **A 档 gold = live calibre-lvs skill 跑出 lvs.rep** → SUT 沙箱不可访问 (无 live Calibre install/无 LSF pv 队列/无 HLMC PDK/无 698 机 ssh) → 必须 reframe
- **reframe 算法核心 = skill spec 4 条验收标准的判分步骤** (从 lvs.rep 抽 verdict + compilation_completed + license_acquired + svdb_present + errors + missing_inputs) → 纯 stdlib lvs_rep_parser.py 可完整捕获, 无需 live Calibre
- **visible A = blcnand2PFx4 CORRECT** (spec 参考实现已验证)
- **hidden B = blcnand3GFx1 INCORRECT (Y-open in pull-down chain)** (spec 参考实现已验证, 与 A 不同 cell/不同 verdict/不同 errors)
- **hidden B2 = invGFx2_Ck NOT COMPARED (source CDL .cdl.raw 缺顶层 .SUBCKT)** (spec 已知陷阱 Subcircuit X not found)
- **三输入三 verdict 路径反硬编彻底** (CORRECT/INCORRECT/NOT COMPARED + A/B/B2 cell 标识符全异)
- **2026-11-15 重审令**: run-existing-skill/flow-driving 为合法用户意图, 本 case 为该政策 physical_verify 首例 (calibre-lvs skill flow-driving reframe)

## 与既有 case 区分
- distinct vs r834 SvrfDeckStructureAnalyze-001 (SVRF deck 结构抽离) = Calibre LVS report verdict 解析
- distinct vs r830 CalibreVcoResolve-001 (calibre wrapper 脚本 VCO 环境解析) = LVS report 判分
- distinct vs LvsSeedPromoDetect-001 (7rzyf, LVS seed-promotion root-cause) = 通用 verdict parser vs 具体异常检测
- distinct vs ErcRulecheckStatsScan-001 (nmanu, ERC rulecheck stats) = LVS report vs ERC stats

## 意图审计
**keep**: adaml 真实意图 (通过 calibre-lvs skill 跑 LVS 拿 verdict) 完全保留; reframe 把 skill spec 4 条验收标准的判分核心沉淀成可判分纯 stdlib parser, 是 grounding 非加难; r582 peek 拒为 "run-existing-skill not produce-task" 是旧规则口径, 2026-11-15 重审令后 run-existing-skill/flow-driving 为合法用户意图, 本 case 复活正当.
