# Deepread: 1793078405436_t0aom — FineSim post-sim FSDB + netlist analysis / optimization / diff

- **trace**: `1793078405436_t0aom` · user `easont` @ `hfhds207` · mc=650 · 415 msgs · domain=spice_sim
- **context**: DDGOA DDR6 `ddgoa_cmos_digital_TempHalfWL_schematic_ALPS_sim` co-sim (FineSim ALPS digital sim, tt0.94v45c, vdd2h corner). Foundry PDK + huge DRAM netlist → NOT portable as-is → B档 synthesized reframe.
- **claimed**: 2026-11-05 shard B (deepread, DEBT:1).

## User intent flow (逐字, A档选轮评估)
- U0: `can you read .../tt0.94v45c.vdd2h/finesim.fsdb`
- U8: `有fsdb相关的MCP server吗` → agent 发现 `~/.cline/skills/waveview-fsdb-readerV2-2` (WaveView ACE 读 FSDB)
- U17: `使用上面的skill读取...finesim.fsdb；根据波形说明signal的功能` ← **A档候选需求轮**（提需求，未给根因/方案）
- U63: `读取.../netlist_AI,结合上面的fsdb分析，说明模块功能`
- U97: `分析当前netlsit是最简逻辑吗，是否有优化方案，直接输出优化后的网表...命名为netlist_pro` ← **A档候选**（优化需求，未给方案）
- U204: `仿真波形有问题，自己分析后迭代netlist` ← **A档候选**（诊断+迭代需求）
- U234: `结构参考这个来，你生成的都是错的 .../netlist_AI` ← 🚫 用户指出根因（agent 输出错误），不可作 A档任务说明（可作 hint）
- U278: `你理解下这个网表，然后分析是否有可优化的点，然后直接在netlist上修改`
- U383: `对比修改后的网表和原先的网表，生成markdown形式的报告`
- U392/U401/U412/U414: 分析 cosim 文件夹整体仿真流程 / 分析 fsdb 输出 markdown / 读另一 fsdb 分析 RowControl

**trace 末尾用户未明确接受**（agent 多版本 fix_netlist_pro_v{2,3} 被指 "都是错的"）→ **B档 synthesized** 子技能忠实重述（不可用 trace 末产物作金标准）。

## Assistant 工具链
read_files(79) · run_approved_command(59) · editor(39) · list_allowed_files(21) · search_codebase(7) · run_commands(3) · skills(2)。
**关键 skill**: `~/.cline/skills/waveview-fsdb-readerV2-2/waveview-fsdb-readerV2-2.py` → 生成 `wv_tmp/wv_s_*.tcl` → WaveView ACE (`wv -ace_no_gui`) 读 FSDB → 提取 signal list + transitions。
**关键产物**: `gen_netlist_pro.py` / `fix_netlist_pro_v{2,3}.py` / `compare_nl.py` / `clean_header.py` / `final_clean*.py` / `netlist_pro{,_clean,_final,_optimized}/` — netlist 生成→修复→清洗→对比 pipeline。

## 可便携子技能（B档 synthesized, L2 真跑 WaveView ACE + FineSim）
**"FineSim post-sim FSDB 波形诊断器"**: 给定 FineSim netlist + FineSim 仿真产出的 FSDB → (1) 用 **WaveView ACE Tcl** (`wv -ace_no_gui`) 读 FSDB 提取 signal list + per-signal toggle/transition 摘要 (2) 解析伴随 netlist 的信号/net (3) 识别 **stuck 信号(从不翻转)** + **unexpected-active 信号** + netlist 中声明但 fsdb 缺失的信号 (4) 产结构化诊断报告 (json+markdown)。

**distinct ✓**（vs 已有 shard B case）:
- WvFmFreqExtract(qb1ua)=FM 瞬时频率提取(RISE 扫描+阈值+1/(t2-t1))，本条=**FSDB signal-list 枚举 + per-signal toggle 诊断 + netlist 交叉对照 + stuck/missing 信号识别**（无 FM/频率计算）。
- MeasExtractCornerTrace(1fxvk)=.meas 静态提取+多 corner .mt0，本条=FSDB 波形级 signal-toggle 诊断（无 .meas/.mt0）。
- PostsimPortAudit(7bqzr)=netlist-vs-SPF 端口对应审计+FineSim log 反标，本条=FSDB 波形 vs netlist signal 对应诊断（无 SPF/端口）。
- NetlistLintHsp(l7aol)=网表 lint+HSPICE elaboration，本条=波形级诊断（有 FSDB 读取）。

## 可行性 (.75 已验证)
- **WaveView ACE 读 FSDB**: .75 有 `wv -ace_no_gui` (P-2019.06-SP2)，qb1ua 已验证 WDF 读写；FSDB 是 Synopsys 格式，WaveView ACE **支持读 FSDB**（trace 实证：waveview-fsdb-reader skill 生成 Tcl 调 wv 读 fsdb）。**下轮第一件事须 probe**: .75 上 `wv -ace_no_gui` 是否真能开 `.fsdb`（备选：FineSim 产 `.tr0` 二进制，WaveView 原生支持 tr0 → 改用 tr0 介质，qb1ua 已验证 tr0/wdf 路径）。
- **FineSim 产 FSDB/tr0**: .75 FineSimPro V-2023.12-1 可跑 level-1 netlist 产 `.tr0`（二进制波形），WaveView ACE 可读。**优先用 .tr0**（避免 FSDB 格式不确定风险），候选用 WaveView ACE Tcl 读 .tr0 提取 signal list + transitions。
- **netlist 解析**: 纯文本，Python 正则即可（level-1 .subckt + 顶层实例化 + .tran）。

## DUT 设计草案 (A/B 双输入, 跨输入守卫)
- **A (visible)**: level-1 4-stage inverter chain + 一个 stuck 输入（tied DC）+ 一个 active clock → FineSim .tran 产 .tr0 → 候选读 .tr0 识别 stuck net (tied 输入端) + active net (clock) + 报告 toggle counts。
- **B (hidden)**: 不同拓扑（NAND2 chain + SR-latch），不同 vdd/period/net 名，2 个 stuck nets + 3 个 toggling nets + 1 个 netlist 声明但 .tr0 缺失的 net（trap）。
- 跨输入 diff: net 名/拓扑/stuck 数全不同防 hardcode。

## check.py 条件草案 (k≥14, a-n + o)
(a) zip+入口 (b) py_compile (c)B 真跑 wv -ace_no_gui(log banner+Successfully) (d)B 提取 signal list 非空 (e)B per-signal toggle_count (f)B 识别 stuck nets(=期望集) (g)B 识别 active/toggling nets(=期望集) (h)B 识别 netlist-declared-but-fsdb-missing net (i)B netlist 解析 .subckt+顶层实例 (j)cross-input guard rerun A stuck nets 正确 (k)name-agnostic B net 名齐 A 名不泄 (l)B report schema 完整(signals/stuck/active/missing/ts) (m)markdown 报告含 diff 表 (n)确定性 rerun B 稳定 (o)judge 独立 rerun FineSim 产 .tr0 job concluded（anti-fake guard）。

## 6 neg 草案
naive_empty→b / naive_print_expected→c / naive_no_rerun(no wv)→c / naive_hardcode_a(stuck hardcoded A)→f / naive_grep_only(正则猜 net 名不读 tr0)→d / fake_core_deleted→e。

## 下轮第一件事（合成 t0aom）
1. **probe** (.75): FineSim level-1 deck 跑出 `.tr0` → `wv -ace_no_gui -batch -source read.tcl` 读 .tr0 提取 signal list + transition times（验证 Tcl API：`sx_open_waveform_file` / `sx_get_signal_names` / `sx_fetch_x`）。备选: FSDB 直接读（若 wv 支持）。
2. 标定 A/B GT（stuck/active/missing net 集合）。
3. 合成 `EDA-Eval-DesignFlow-FsdbNetToggleDiag-001`（check.py 14+6 neg+selftest）→ 追加 EDA-Eval-DesignFlow_B.jsonl → mark t0aom case → 清 DEBT:1。
4. 教训预记：WaveView ACE Tcl API 须 probe 实际函数名（qb1ua 用 sx_create_scan/sx_set_threshold/sx_fetch_x/sx_write_open）。

## 本轮数据质量发现（报运维/merge）
- **跨 shard 重复**: trace `cpv3d`(taodu) → ConnFileNetChk-001 **同时存在于 shard A 和 shard D 的 jsonl**（2 行，同 trace 同 case_id）。建议 merge 脚本去重或 A/D 协调保留一方。shard B 已 park cpv3d 标注 "CROSS-SHARD DUP"。
- **spice 池耗尽**: shard B 在 mc≥30 的 spice-keyword 候选池已 100% 入台账（116 touched = 74 case + 40 parked + 2 deepread）。mc≥15 剩余 600 候选经首条用户意图 peek，绝大多数为 layout/netlist-DB/schematic/PEX/skill 非纯 spice_sim。本轮 park 15 条 false-positive。**建议**: 下轮考虑 (a) 降低 mc 阈值到 mc≥10 扩池，或 (b) 接受 L1 静态 case（PEX 反标 w4x70 等）以维持 shard B 产出节奏。
