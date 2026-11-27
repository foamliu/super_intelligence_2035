# 深读笔记：1795138311750_tahks (cyrusrao @ hfhds201, mc=259)

**trace_source**: user=cyrusrao, host=hfhds201, session_file=1795138311750_tahks.messages.json, match_count=259
**keywords**: schematic:871; netlist:412; verilog:356; analog:209; pyaether:178; dscqa:96; array:84
**domain**: schematic_netlist (D shard)
**trace 获取**: .75 ssh→hfhds201, snapshot per-session path `/home/cyrusrao/.snapshot/daily-new.2026-11-26_2230/.cline/data/sessions/1795138311750_tahks/1795138311750_tahks.messages.json` (673KB, 165 msgs)

## 用户真实意图（多轮迭代）

用户 cyrusrao 在 DSCQA DDR6 项目中需要确认一条 **testmode 信号能否经多级 schematic hierarchy 下传并影响目标模块的指定输出**——这是典型的「testmode 传播路径 trace + 影响域判定」任务，纯 schematic/netlist 域，无仿真依赖。

### 信号与层次结构
- **源信号**：`cm0_ro_BLCom`（高电平使能型 testmode 信号），从顶层 `DDR6TOP` 出发。
- **下传 hierarchy 链**（8 级）：
  `DDR6TOP → DDR6TOP_R → Array32GTop → Array16G_PSD0 → Array2G_PSD0_BGAB → Array2G_PSD0_BGTopX2 → Array0p5G_Up_L_DSCQA → XdecGapTop_DSCQA`（目标模块）。
- **派生点 1**：在 `BnkGTopx1_BG0` 处，`cm0_ro_BLCom` 经缓冲派生为 `cm0_ro_BLComEn`。
- **派生点 2**：在目标模块 `XdecGapTop_DSCQA` 处，`cm0_ro_BLComEn` 扇出为 **48 路 section 使能**：`cm0_ro_BLComEnSec0..47`（外加 `cm0_ro_BLComEnBot` / `cm0_ro_BLComEnTop`）。
- **独立 combining 信号族**（不来自源信号，是 step 控制信号）：
  - `cm1_ro_StepPreSec*`（48 路，驱动 PreEq）
  - `cm1_ro_StepIsoSec*`（48 路，驱动 Iso）
- **输出**：48 路 section 使能 与对应 step 控制信号经 **AND 门**驱动：
  - 48 路 `PreEqSec*`（precharge/equalization 输出组）
  - 48 路 `IsoSec*`（isolation 输出组）

### 用户的工作方式
用户用 pyAether / strings / grep 在 OA 数据库中逐层 trace 信号派生关系：找 instance 的连接、找 net 的 driver/sink、确认 enable 信号是否真的连到 AND 门输入、确认 combining 信号是否独立。最终结论：**`cm0_ro_BLCom` 能影响 `XdecGapTop_DSCQA` 的 PreEq 输出与 Iso 输出**（经 48 路 section 使能 + step 控制信号 AND）。

## case 合成 plan（已落库）

- **task_id**: `EDA-Eval-DesignFlow-TmSignalPropagateAnalyze-001`
- **判定**: **LIVE-NA**（deliverable=analyze_propagation.py 脚本，check 跑候选 + 独立传递闭包复算断言，无真实 EDA 工具二进制依赖；OA 数据库不在 .75 不强求 L2.live；纯结构化 JSON 判分）
- **judge_layers**: `[L0, L1]`，无 check_live
- **reframe**: 通用「testmode 信号传播影响分析器 `analyze_propagation.py(spec)->report.json` + hidden-B 反硬编码」。把「在 OA 数据库里 trace」reframe 为「读结构化连接关系 spec JSON 做传递闭包」。

### A (visible) spec_A.json
真实源自 DSCQA 项目：source=`cm0_ro_BLCom`，8 级 hierarchy，target=`XdecGapTop_DSCQA`，派生族 `cm0_ro_BLComEnSec`（48 section），combining 族 `cm1_ro_StepPreSec` / `cm1_ro_StepIsoSec`，2 个受影响输出组 precharge(48 PreEqSec) / isolation(48 IsoSec)。

### hidden B spec_B.json（token-structurally 不同）
完全不同命名/结构：SRAM5 项目，source=`cm0_ts_FltWl`，target=`SaCtrolArray_S5`，32 section（A=48），3 个输出组 `sense_amp_eq` / `iso_ctrl` / `row_select`，其中 **`row_select` 是诱饵组**（其 enable_family 不来自源信号派生族，须被排除为 unaffected）。命名全换 ⇒ A 硬编码分析器在 B 全错。

### check.py 13 conds(a-m)
- a submit.zip 可解压且含 analyze_propagation.py
- b analyze_propagation.py 可编译(py_compile)
- c 在 spec_A 上运行 exit0 并写出合法 report_A.json
- d A 报告 affects==True
- e A 报告 target_module==XdecGapTop_DSCQA
- f A 报告 derived_signals_at_target 非空且含 cm0_ro_BLComEnSec 族
- g A 报告 affected_output_groups==[precharge,isolation]
- h A 报告 precharge 输出 48 个且前缀 PreEqSec
- i A 报告 isolation 输出 48 个且前缀 IsoSec
- j A 报告 combining_signal_families 含 cm1_ro_StepPreSec 与 cm1_ro_StepIsoSec
- k 在隐藏 spec_B 上运行 exit0 并写出合法 report_B.json
- l B 报告 affected==[sense_amp_eq,iso_ctrl] 且 unaffected==[row_select]（诱饵组排除）
- m 反硬编码：analyze_propagation.py 源码不含 A 专属 token（cm0_ro_BLCom/XdecGapTop/PreEqSec/IsoSec/DSCQA/StepPreSec/StepIsoSec/BnkGTopx1/DDR6TOP）

### 核心算法（reference analyze_propagation.py）
逐条派生链做**传递闭包**：从 source 出发，沿 derive_rules 把信号名按 family 前缀展开，得到目标模块处派生出的信号族前缀集合。一个输出组受影响 ⟺ 它的 `enable_family` 出现在目标模块派生族前缀里；`combine_family` 是独立 combining 信号（不参与传播判定）。report 含 affects / propagation_path / derived_signals_at_target / derived_families_at_target / affected_output_groups / affected_outputs / unaffected_output_groups / combining_signal_families。

## 自验（全绿）
- ref check.py on reference_submit.zip → PASS（13/13）
- negative_selftest 5 neg ALL-FAIL distinct first-fail {c, c, e, k, g}：
  - empty→c / print_only→c / core_deleted→e（§4.9 trio full）
  - hardcode_a→k / all_affected→g（2 extra，all_affected 把诱饵组也标 affected → l/g fail）
- SKIP_RUN=1 eval/run_one.sh：workdir leak 自检通过（无 check.py/reference/hidden 泄漏）
- 3-way sha sync：disk == JSON test == metadata.check_sha256 = `659b2602ccc5322f843d1361b305eb8ef926dca180deae6d69d71db7793b24d4`（size 7638）
- k_check=13 = k_rationale=13

## 台账
- trace_ledger mark: `1795138311750_tahks` → case(EDA-Eval-DesignFlow-TmSignalPropagateAnalyze-001)
