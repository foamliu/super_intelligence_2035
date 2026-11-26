# 深读笔记 · sykbg (1794901251428_sykbg)

- **session**: `1794901251428_sykbg` · **user**: e0030760 · **host**: hfeg0pkn001 (10.129.2.10)
- **mc**: 138 · **size**: 1,227,522 B (1.2MB) · **msgs**: 159 · **日期**: 2026-11-17 ~ 11-18
- **trace_source**: 1119 扫描 (`ssh_eda_search_20261119_172105/summary.tsv`)，B shard fresh 池 mc>=10
- **keywords**: hspice:253;netlist:140;.def:57;spectre:44;synopsys:39;cadence:25;mixed-signal:24;analog:14
- **domain**: spice_sim (B shard)
- **claim**: r901 (2026-11-20) · **status**: parked（asset 可访问性阻塞，见下）

## 用户原始意图（4 个 user_input，逐条溯源）

### Task A (MSG 0, mc 主体) — MC sigma 定义链路追踪（Q&A/investigation）
> `/proj/lacaa/V0/workdir/e0039809/testbench/CH252_FS_6T_SRAM_single_Bitcell.sp 这个testbench中调用的netlist和ttg lib中是如何定义MC仿真sigma数的？`

agent 追出的完整链路（trace tool_results 实证）：
1. **testbench** (`CH252_FS_6T_SRAM_single_Bitcell.sp`)：第 3-6 行 `.include` option_hspice.sp / pwr.sp / switch.sp；第 62 行 `.include` netlist；**第 114 行 `.LIB ... ttg_sram_fs`**（注释 `tt global with MC local`）。
2. **netlist** (`HD_CH252_6T_SRAM_FS_Single_Bitcell_20261109.netlist`, AETHER-SE 导出, 2026-11-09)：`.SUBCKT HD_CH252_6T_SRAM_Bitcell BL BLB Q QB VDD VSS WL`，每个器件（XPU2/XPU1 hd_pu_fs, XPD2/XPD1 hd_pd_fs, …）传 `u0mult/ids0mult/delvtrand/dtemp/totalfactor/globalfactor/localfactor/cctdmod/cctsmod/rctdmod/rctsmod/rgtmod` 等参数（**netlist 本身不写 sigma 数字，只传缩放开关**）。
3. **lib** (`35H_DBCFS_Model_SRAM_v0d1_Rev06.lib`)：`.lib` 段定义共 24 个段（pre_sim_dbc/tt_sram_dbc/…/pre_sim_fs/tt_sram_fs/…/**ttg_sram_fs@line1277**/…）。`ttg_sram_fs` 段 `.lib './sram_setup.lib' hc_default/hd_default/…/sram_hc_fs/sram_hd_fs/…` + `.lib './sram/cor/hd_cor_fs.lib' hd_tt`。
4. **MC sigma 真身**：`rnd_mis_0..8 = agauss(0,1,1)`（1σ 标准正态随机源）；失配量 = `da_<参数>_<器件>`(σ 系数) × `geo_fac` × `rnd_mis_N` × `mismod` × `localfactor`；`totalmod_*/globalmod_*` 默认全 0（全局角关闭，只剩 local MC）。`geo_fac` 与 `da*` σ 系数定义在 `.mdl` 顶部 `.inc './def/hd_pu_fs.def'` 引用的 **.def 文件（HSPICE 加密，`.UNPROT` 标志，读到乱码）**。
5. **结论**（MSG 36）：MC sigma **不在 netlist 写死**，结构是「lib 提供 1σ 标准正态随机源 + 每管独立 σ 灵敏度系数，netlist 只传缩放开关（默认全 1 = 1σ MC）」。`ttg_sram_fs` = tt global（全局典型角）+ MC local（局部失配蒙特卡洛）。

### Task B (MSG 37) — NanoSpice 安装排查（env-config Q&A）
> `寻找该环境是否配置nanospice安装包`
结论：**已配置**。`NANOSPICE_HOME=/apps/proplus/nano_release` → `nano.v4.26.2.8.r71725.nw.r232688.x86_64_cus_rel_20261109`（2026-11-09 发布），PATH 含 `bin/`，配套 `NS_FMT_LIB_PATH`/`NW_LIC_TIMEOUT=3600`。

### Task C (MSG 52) — NanoSpice user guide 定位（doc-search Q&A）
> `nanospice user guide在哪个文件夹？`
结论：`/apps/proplus/nano_release/simulator/doc/`（16 份 PDF）。

### Task D (MSG 56) — NanoSpice 文档解析 + High Sigma MC 总结成 MD（produce-doc-summary）
> `详细解析上面这些nanospice文档，分析关于high sigma MC分析相关的内容，另外总结nanospice的使用方法，总结一个md文件`
**交付物**：`/home/e0030760/NanoSpice_HighSigma_MC_summary.md`（383 行，20,199 B，7 大章节 + 附录）：
- §1 文档清单（16 份 PDF 页数/主题索引）
- §2 产品家族（`nanospice` 单一可执行 + `+giga/+pro/+sram=t|p/+simmode=spicexN|proxN` 模式切换、`simlvl/rcrlvl`、license）
- §3 标准 MC（Hspice 风格 `sweep monte`/`GAUSS/AGAUSS/UNIF/AUNIF/LIMIT`、Spectre 风格 `.variation`/`montecarlo`、`mc_sampling/mc_autostop/mc_variation`、`-mp/-mt/-dp` 并行）
- §4 **High Sigma MC（重点 12 小节）**：算法 Mixed Importance Sampling 两阶段（Phase1 定位失效区→Phase2 重要性采样，~1万次，参考 Kanj/Joshi IBM SRAM 论文）；两类分析 `target=`(求良率) vs `target_sigma=`(求σ边界)；`.highsigma` 完整语法（`TARGET_SWEEP/dut/ignore/var_scope/failcenter/randomMean/dump_corner`）；18 个控制选项（`hslvl/hs_autostop/hs_range/hs_output/mc_probe`…）；输出文件 + 术语（Failure Sigma/Equivalent MC/Speedup）；官方实测 6T SRAM 写失败 3.483σ 仅 948 次仿真（230×加速）、NOR 6σ 5120 次（4575万×加速）；失效 corner 复验、LSF 分布式、NanoWave Histogram/QQ plot、已知限制
- §5 其余 App Note 速览；§6 结合本环境 35H SRAM 库（`agauss×localfactor` 结构可直接识别）的 MC/HighSigma 实操命令；§7 快速参考表
- 关键提示：HighSigma 不支持 AC measure target；单 target；默认不输出波形（`mc_probe=1` 开启）；license 走 Primarius `ppds_lic`（本环境用户级未配置）

### Task E (MSG 108+，session 后段) — Solido HSV 运行失败诊断（diagnosis，非 clean produce）
诊断一个 Solido High-Sigma Verification 运行：`Ordered samples ran: 0`、`binomial_initial_not_converged`、171/2500 样本 "Failed simulation"、ordering model 5 轮都 `Models do not seem ready` → 一直初始采样到 2500 退出，ordered sampling 从未启动。根因：每个失败样本 HSPICE stdout 末尾 `wnmr= failed`（`.MEASURE DC WNMR` 求交叠点失败，无数值），样本 164 还有 DC 收敛问题。**分析/诊断类，无 clean produce artifact**。

## 可造 case 评估（produce-generator reframe，harness-for-teeth）

### 候选 1（推荐）：Task D → NanoSpice HighSigma 文档摘要 MD 生成器
- **reframe**：写 `nanospice_highsigma_summarizer.py`，读 NanoSpice 文档文本（PDF 提取），产出结构化 MD（§1-§7 + High Sigma MC 重点）。
- **asset A**：NanoSpice doc .txt 子集（HighSigma App Note + Quick Start + User Guide MC 章节）。
- **hidden B**：held-out doc 子集（Pro X Guide / 不同 HighSigma 内容）。
- **check()**：跑 summarizer on B，解析输出 MD，断言 ≥8：§1 doc 清单 / §2 产品家族 / §3 标准 MC(AGAUSS/.variation) / §4 HighSigma(Mixed IS 两阶段、target=/target_sigma=、.highsigma 语法、控制选项、speedup) / §5 / §6 / §7 / 结构（≥N 节、highsigma 关键词、语法块）。
- **near-dup 闸门**：e0030760 现有 13 case **无 NanoSpice 文档摘要类**（全 SRAM SNM/char/spice-deck-analysis）→ **genuinely new intent，过 r900 dup 闸门**。
- 🚫 **BLOCKER（本轮阻塞，park 原因）**：① NanoSpice doc 提取的 .txt 已被清理（`/home/e0030760/nanospice_docs_txt/` 空目录）；② doc 源目录 `/apps/proplus/nano_release/simulator/doc/` 从 sandbox 用户不可列举（ls 返回空，疑似权限）；③ 重新 pdftotext 16 份 PDF + 构建 hidden B + check + negatives + selftest **超出本轮 40min 预算**。需专注轮从 trace tool_results 重建 asset A。

### 候选 2（备选）：Task A → MC sigma 定义链路提取器
- **reframe**：`mc_sigma_chain_extractor.py`，解析 Hspice testbench + `.LIB` include 链，提取 MC sigma 定义结构（rnd_mis 源/AGAUSS、localfactor/mismod/globalmod/totalmod 参数、`.LIB` 段名如 ttg_sram_fs、sigma mode = local-only/global+local）。
- **near-dup 闸门**：e0030760 已有 `SpDeckStructExtract-001`(generic deck 结构提取) / `NetlistMisModCompare-001`。MC-sigma-chain 是**更窄的特化意图**（专追 MC/monte-carlo sigma 链，非通用结构），可辩护为 distinct，但 check() 须明确与 SpDeckStructExtract 差异化（断言聚焦 rnd_mis/AGAUSS/sigma-mode，非通用 .lib 段清单）。
- 🚫 **BLOCKER**：testbench `/proj/lacaa/V0/workdir/e0039809/testbench/CH252_FS_6T_SRAM_single_Bitcell.sp` 从 sandbox 用户 **Permission denied**（trace agent 以 e0030760 身份读，sandbox 不是）。asset A 须从 trace tool_results 重建（testbench 5322B + netlist 4086B + lib 段 48995B 已在 trace 内）。

### 候选 3（不推荐）：Task E — Solido HSV 失败诊断
分析/诊断类，无 clean produce artifact，且 SnmHsvFailDiag-001 已覆盖 HSV-fail-diag 意图 → near-dup 风险高。**不造**。

## 本轮处置

- **claim**：r901 已 claim（ledger_B）
- **park**：asset 可访问性阻塞（NanoSpice doc .txt 已清理 + /proj/lacaa perm-denied），本轮 40min 预算不足以从 trace tool_results 重建 asset A + 完整 §4 质量闸门（≥8 断言/hidden B/negatives/selftest）。**候选 1（NanoSpice HighSigma 摘要生成器）为下轮首选**，需专注轮从 trace 重建 doc asset。
- **park note**: `asset_accessibility_blocker: NanoSpice doc txt gone + /proj perm-denied; reframe=nanospice_highsigma_summarizer.py (Task D, new intent); needs trace-rebuild round`

## 证据（trace tool_results 关键事实，可溯源）
- testbench `.LIB ttg_sram_fs` @ line 114（MSG 4 agent 自述）/ `.LIB` 段定义 ttg_sram_fs @ line 1277（MSG 13 tool_result）
- netlist 器件传 `localfactor/globalfactor/totalfactor/mismod`（MSG 5 tool_result, XPU2/XPU1/XPD2/XPD1）
- `rnd_mis_0..8 = agauss(0,1,1)` + 失配量公式（MSG 18 agent 自述，源自 lib 扫描）
- `totalmod_*/globalmod_*` 默认 0（MSG 9 tool_result, line 426-452）
- .def 文件 HSPICE 加密 `.UNPROT`（MSG 30 agent 自述）
- NanoSpice 交付 MD 383 行 @ `/home/e0030760/NanoSpice_HighSigma_MC_summary.md`（MSG 106 agent 自述 + ls 实证 20199B Nov 18 10:19）
