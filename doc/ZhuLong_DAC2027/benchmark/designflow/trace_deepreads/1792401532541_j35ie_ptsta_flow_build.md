# Trace 深读：1792401532541_j35ie（e0046913 / hfeg0pkn003 / mc=11）

## 0. trace_source（落 jsonl 用）
- user: e0046913
- host: hfeg0pkn003 (10.129.2.12)
- session_file: 1792401532541_j35ie (dir: `1792401532541_j35ie/1792401532541_j35ie.messages.json`, 178KB)
- match_count: 11 (innovus/icc2/primetime/floorplan/synthesis keywords)
- real_task_summary: 用户(yutingq 工作目录)要求在 /rundata/lacaa/TV1_digital/simdir/yutingq/STA 构建 PrimeTime STA flow：run/ 下 cshell 运行脚本（支持 -corner/-mode 传参），scr/ 下 sta_main.tcl + 1_setup.tcl…10_rpt.tcl 编号 Tcl 脚本按序 source；enable 环境配置/工具选型/子模块 lib 读入/corner-mode 适配；参考 /apps/imctf/cad/script/digital_flow/feint 的 synopsys pt reference flow；工具 /apps/synopsys/primetime（需 module load）。

## 1. 对话流（15 msgs: 8 user / 5 assistant + tool_results）
- **U#0**（A-faithful 候选，逐字原文，规则②✓：纯提出需求「构建 STA flow + demo 跑通」，未给根因/修复方案）：见 prompt.txt 全文。
- A#1–A#13：助手仅做上下文采集——run_commands 被策略禁用(raw shell disabled)，改 list_allowed_files 探测：/home/e0046913 可读根 + /apps/imctf/.../feint 可读 + /rundata/.../yutingq/STA 可读（已含 log/rpt/run/scr/sdc/session 子目录）；read_files 读 feint/scripts/pt.tcl + setup/common_setup.tcl + Makefile + scripts/dc.tcl。
- **助手未完成实际构建**（trace 在读参考脚本后结束，无 editor/write 工具调用，无可接受交付件）→ **无金标准** → 本 case 用 **B 档（synthesized gold）**：金标准 = 按用户规格合成的完整 STA flow 脚手架（run/run_sta.csh + scr/sta_main.tcl + 1..10 编号 Tcl），不真跑 PT，判分静态校验结构 + 参数化 + 跨输入守卫。

## 2. case 合成（EDA-Eval-DesignFlow-PTStaFlowBuild-001，pnr_signoff / L1 静态结构校验）
- **A（SUT 可见）**：prompt.txt（U#0 逐字）+ task_brief.md（≤3 行交付接口）+ fixtures/{feint_ref_filelist.txt, corners.def(3 corners: tt_0p75_25c/ss_0p81_125c/ff_0p69_-40c, modes func/scan), submodule_libs.txt(CORE+IO), sample.sdc}。
- **B（隐藏）**：B_corners.def(2 corners: tt_0p80_85c/ss_0p88_125c, modes func/mbist) + B_submodule_libs.txt(LOGIC+MEM) + hidden_manifest.json。结构与取值全异于 A（corner 数/电压/mode 集/lib 子模块名/run_dir）。
- **check.py**（14 条断言 a-n，自包含内嵌 B 证据）：(a)zip 含 run/+scr/ (b)cshell shebang (c)pt_shell 调用 (d)module load (e)sta_main.tcl (f)1..10 连续编号 (g)main 按序 source (h)1_setup search_path+CORNER/MODE (i)read_sdc (j)read_lib+link/target_library (k)10_rpt 生成报告 (l)-corner/-mode 参数化 (m)跨输入守卫(scr/ 不硬编 A corner/lib token + B 经 CORNER/MODE 变量可达，击破 fake_print_expected/naive_hardcode_a) (n)mkdir -p + 按 corner/mode 分日志。
- **自验全过**：① ref check.py 跑 reference_submit.zip = PASS(True)；② negative_selftest 5 错解全 FAIL(NEG_RC=0: fake_empty→a / fake_print_expected→m[scr/ 硬编 A corner token] / fake_core_deleted→f,g,k / naive_hardcode_a→m[硬编 CORE+tt_0p75_25c] / naive_no_corner_param→l,m[runner 无 -corner/-mode])；③ §4.9 三假回归（空壳/只硬编/删核心）全 FAIL；④ 断言闸门 k_rationale==k_check==14≥8 ✓。
- **落库**：台账 mark --status case（covered=45）；追加 EDA-Eval-DesignFlow_A.jsonl（46 行/46 unique id，test==disk sha roundtrip ✓）。
