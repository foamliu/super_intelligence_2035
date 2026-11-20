# r4cdh — PVT-config HSPICE sim-harness refactor (shanliny)

- session: `1795075473970_r4cdh.messages.json`
- user: shanliny @ hfeg0pkn003 (10.129.8.239 in summary; trace log host hfeg0pkn003)
- mc=395, keywords: aether:682;netlist:498;hspice:326;.def:80;synopsys:54;mosfet:25
- workdir: `/proj/train/V0_NCG_HF_Aether/workdir/shanliny/funchk_trainning_for_shanlin/racing_check/9_autosim/racing_hd1p`
- agent: lead, 299 msgs, 131 tool_use (read_files 58, editor 21, run_approved_command 35)

## 真实任务 (verbatim user intents)
- U0: 「帮我看 .../racing_hd1p」
- U17: 「告诉我PVT_LIST在这套系统里是如何运作的」
- U19: 「你每仿真一个例子就要把网表复制一遍...几十GB的大网表不是徒费空间？」→ 用 symlink 接网表，不要 copy
- U47: sp 文件中声明网表会随工艺角变化，实则不会变 → 修
- U103 (核心重构): 用 `config_pvt.txt` 格式代替 PVT_LIST 传参；sp 文件变量用 `<<>>` 格式；网表名 `<规模名>.dspf.<条件名>`；0_run.py 加网表规模名参数(不传→不仿真/具体名(可多个)→只仿该前缀/`*`→全前缀)；config_pvt.txt 中 RC_CORNER 和 RC_TEMP 约束网表后缀；sp 文件名形如 `<INST>_fs_fs_1.02_1.02_1.02_125_CMAX_ccworst_-40.sp`，后缀数字意义顺序与 config_pvt.txt 变量一致；`<<temperature>>` 已换成 `<<TEMP>>`
- U172: config_pvt.txt 注释功能(`#`)+ 多个网表前缀名如何输入
- U174: log 文件单独丢到 `logs/` 文件夹，不要堆主目录
- U188: 已生成的 log 也丢进去
- U196: 并行提交 + 旧数据残留清理
- U222/U248: 跑仿真没启动 / 总数显示为？
- U285: 流程全通了

## 真实资产 (从 trace tool_result 提取，保真)
- `config_pvt.txt` (新格式, 23 数据行): 8 列 `BITCELL_PROCESS LOGIC_PROCESS VDD VDDP VDDC TEMP RC_CORNER RC_TEMP`，空白行分组，tt/ss/ff/sf/fs × 0.6/0.75/1.02 × -40/25/75/125 × TYPICAL_25/CMAX_ccworst_-40/CMIN_ccbest_125
- `racing_m4b2.sp` (模板, `<<>>` 占位): `<<LOGIC_PROCESS>>` `<<BITCELL_PROCESS>>` `<<spf_path>>` `<<INST>>` `<<DSPF_RC>>` `<<VDDP>>` `<<VDDC>>` `<<TEMP>>` `<<SIM_TIME>>`
- 生成 sp: `CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS_ss_ss_0.6_0.6_0.6_-40_CMAX_ccworst_-40.sp` — 占位全替换, spf_path=`.`, DSPF_RC=`CMAX_ccworst_-40`
- 网表命名: `<INST>.dspf.<RC_CORNER>_<RC_TEMP>` (e.g. `.dspf.CMAX_ccworst_-40` + `.xtop`)

## case 设计: EDA-Eval-DesignFlow-PvtConfigDeckGen-001
- reframe harness-for-teeth: one-off 0_run.py 重构 → produce 参数化 `pvt_deck_gen.py`
- CLI: `--config --template --spf-path --scale --sim-time --out [--sim-cmd --jobs]`
- A 档 trace-faithful: A 用真实 config_pvt.txt + 真实 racing_m4b2.sp (shanliny 原文)
- checkable WITHOUT hspice: 用 stub `--sim-cmd` 或省略；纯文件系统断言
- hidden B: 异 prefix/异 config 行/异 RC corner/异 sim-time；含 `#` 注释行+空行+缺网表的 row(须 skip)
- hidden B2 (anti-stub): 同结构异值
- k=13 断言 (a-m): zip/py_compile/exit0/配置解析计数/sp文件名编码/`<<>>`替换无残留+正确映射/symlink非copy/scale过滤/RC后缀过滤缺网表skip/log路由logs/+master计数/确定性3seed/anti-stub B2/anti-hardcode-A 源码无A前缀
- ref 13/13 PASS; NEG 4 (empty/print/hardcode_b/deleted_core=§4.9三假) 全 FAIL
- 域 spice_sim (B)；非 near-dup: 既有 shanliny B case (MonteMt0Stats/MeaNetPathDiag/RcVizTreeAnalyzer/WmMt0Diag/Mt0MeasDiag/GenXtopCliUpgrade/MosComparaExtractGen) 均 mt0/meas/DSPF-extract/xtop-CLI 领域，无 PVT-config-deck-gen 结构

## claim
- ledger_B: claim 2026-11-20 (r929)
