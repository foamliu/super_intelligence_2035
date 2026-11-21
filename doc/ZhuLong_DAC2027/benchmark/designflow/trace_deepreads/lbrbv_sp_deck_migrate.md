# Deepread: 1794475206189_lbrbv — willz @ hfeahpc501 (mc65, spice_sim, FineSim .sp deck migrate)

> r982 DEBT deepread (budget-gated, non-external). Claimed 2026-11-21 21:5x.
> Source: `/home/willz/.cline/data/sessions/1794475206189_lbrbv/1794475206189_lbrbv.messages.json` (577KB, 113 msgs, 62 user/51 asst).
> Fetched via .75 scp (10.129.33.24 hfeahpc501). 本线直 SSH .75:22 仍超时, eda_flow MCP open_session 正常 (同 r981 INFRA).

## 真实用户意图 (5 个 user 请求, U1-U5)

willz 在做 DDR5 RCV CaPad 的 duty/sensitivity/RJ FineSim 仿真, 工作目录
`/proj/ddgot/V0/workdir/willz/simulation/sim_result_261112/` (旧 `sim_result_251202`)。
agent-policy-engine 强制 (list_allowed_files / run_approved_command profile=python-runner / editor 限 writableRoots)。

- **U1 [msg0]**: copy duty/sensitivity/RJ 相关 .sp 文件 `sim_result_251202`→`sim_result_261112`, 保持相对目录结构, 排除 `deck_*`/`result_*` 自动生成目录 + `bk` 备份。→ 88 文件复制, 0 失败, 大小校验通过 (~645KB)。
- **U2 [msg39]**: "删除 sp 文件中所有关于 model 的引用, 包括 alt_pst"。→ 34 文件, 421 行删除:
  - `.lib '/proj/ddgot/V0/model/current/model.sp' <corner>` (model.sp / model_thick.sp, 含注释 `*.lib`/`**.lib`)
  - `.inc '.../ALT_pst'` / `ALT_tsf` / `ALT_FULL_gating` (验证: 内容全是 .lib 模型库加载的 .alter 文件)
  - `.inc '.../corner_dejoa/<mosTT|mosSS|mosFF|mosFS|mosSF|alt_worst>'` 模型角
  - `.lib '/apps/imctf/extpdk/...'` PDK 模型库
  - **保留**: netlist .inc / spf 寄生 .include / hspice 配置 .include / `.alter` 块头(仅 .temp) / `.END`
  - 兜底检查: 211 行含 alt/model 字样但不匹配删除规则的行 = `.alter` 块头 + 注释横幅 + option 注释, 已确认 .alter 块内无 model 引用, 保留
- **U3 [msg71]**: 替换 netlist 路径 旧`/proj/ddgot/V0/workdir/willz/simulation/CaPad_sim2_hspeedonly/hspiceD/schematic/netlist/netlist` → 新`/proj/ddgot/V0_Lay_20260723/simdir/finesim/workdir/willz/simulation/CaPad_sim2_hspeedonly/hspiceD/schematic/netlist/netlist`。**用户原话写 `schemetic`(笔误), agent 验证 `schemetic` 路径不存在、`schematic` 存在, 用 `schematic`**。→ 仅 `02_HSCA_pst/duty_high_8800.sp` L52 一处 `.inc '旧'` → `.inc '新'`, 旧路径全目录 0 残留。
- **U4 [msg91]**: (a) `.option finesim_mode=spicemd` → `spicead` (19 处, 全是 `.option finesim_mode=spicemd $ high precision analog circuits` 形式, 只改模式名保留行尾 `$ ...` 注释); (b) `.include 'CaPad.spf.TYP_98_RCC'` → `.inc /proj/ddgot/V0/workdir/willz/ddgot_willz/modify/SPF_HL_1112/CaPad/CaPad.spf.TYP_25_RCC` (1 处, duty_high_8800.sp L53, 新路径已验证存在)。→ spicemd 残留 0, TYP_98_RCC 残留 0。
- **U5 [msg104]**: 批量生成 PVT corner 文件 (TT 0.8V/0.5V 45C; SS 0.8V -40/-33/88/130C; FF 0.875V -40/-33/88/130C) 模板 `PVT/tt45`。**= r964 PvtCornerDeckGen-001 (同 user willz 同模板同 corner, 已落库)**。

## 选料判断 & 去重

- **U5 = r964 已落库** → 本 case **不动 U5**, 聚焦 U1-U4 (FineSim .sp deck 内容变换工具链)。
- U1 (文件 copy) 单独 check 牙弱 → 折进 "migrate .sp tree" 上下文, 核心 checkable = U2-U4。
- 非 r948 SpDeckPvtMigrate (witterfu HSPICE deck PVT 迁移, 单步 PVT): 本 case 是 FineSim .sp **多步内容 patcher** (strip model refs + netlist path 重写 + finesim_mode swap + SPF include swap), 4 个独立可断言变换, 形态不同。
- 非 r941 LibMismatchFix (诊断 nrvt/prvt vs V1_HKMG 库错配): 本 case 是确定性 deck 迁移, 非诊断。

## 合成 reframe (next round, 已设计)

**case_id**: `EDA-Eval-DesignFlow-SpDeckModelStripMigrate-001`
**form**: 参数化 FineSim .sp deck migrate/patch 工具 (`sp_deck_migrate.py --config <json> --src <dir> --out <dir>`, 打包 submit.zip)。produce, A-faithful, layer L1 (纯 Python 文本处理, 无 EDA 二进制)。
**trace 原意图**: willz 把旧 sim tree 的 .sp 迁到新目录并做 4 类内容变换 (strip model refs / 重写 netlist 路径 / swap finesim_mode / swap SPF include) 以适配新 PDK 路径与精度模式。

### A 资产 (visible, trace-faithful)
- `config_A.json`: {netlist_path_old, netlist_path_new, finesim_mode_old=spicemd, finesim_mode_new=spicead, spf_old="CaPad.spf.TYP_98_RCC", spf_new="<abs path>", model_ref_patterns: [.lib model.sp/model_thick.sp, ALT_pst/ALT_tsf/ALT_FULL_gating, corner_dejoa/*, PDK extpdk], preserve: [netlist .inc, spf .include, hspice cfg .include, .alter blocks, .END]}
- `sp_tree_A/`: 重建自 trace (34 .sp 文件骨架, 含 .lib model 行 / ALT .inc / corner_dejoa / PDK / netlist .inc / spf .include / .option finesim_mode=spicemd $ ... / .alter 块 / .END)
- 真实路径原值保留 (willz / /proj/ddgot/...)

### hidden B (anti-hardcode-A, 不进 SUT 沙箱)
- `config_B.json`: 全异值 — netlist 路径 `schematic`→`schematic` 但顶层目录 `V0_Lay_20261201`(异日期), spf_old=`CaPad.spf.TYP_100_RCC`/spf_new 异路径, finesim_mode_old/new 异 (如 `spicemd`→`spicefast`), model 库名异 (`model_v2.sp`/`model_thick_v2.sp`), ALT 文件名异 (`ALT_pst_v2`/`ALT_tsf_v2`), corner_dejoa 角异
- `sp_tree_B/`: 异 .sp 文件名/异目录结构/异行数, 含 A 不具备的边角 (多行续行 `+` 的 .lib, 行内 `$` 注释, 嵌套 .alter 块内 model ref 需删)

### check.py (≥12 独立条件, k_rationale=k_check)
a. zip 内含 sp_deck_migrate.py + py_compile 通过
b. CLI `--config B --src sp_tree_B --out <tmp>` 在 hidden B 上 exit 0, 产 run_report.json
c. **model-ref strip**: 输出树无 `.lib` model 行 (model_v2/model_thick_v2), 无 ALT_pst_v2/ALT_tsf_v2 .inc, 无 corner_dejoa, 无 PDK extpdk (subprocess grep 计数=0)
d. **preserve netlist/spf/cfg includes**: netlist .inc / spf .include / hspice cfg .include 计数与输入一致 (未误删)
e. **netlist path rewrite**: 旧路径 0 残留, 新路径出现 (B 的新路径)
f. **finesim_mode swap**: spicemd(或 B 的 old) 0 残留, spicead(或 B 的 new) 出现, 行尾 `$ ...` 注释保留 (正则验)
g. **SPF include swap**: 旧 spf 名 0 残留, 新 `.inc <abs path>` 出现
h. **.alter blocks + .END preserved**: .alter 块数量与输入一致, .END 存在
i. **嵌套 .alter 内 model ref 删**: B 的嵌套 .alter 块内 .lib model 行被删 (A 不具备的边角)
j. **多行续行 `+` 的 .lib 整块删**: B 的续行 .lib model 整块删除 (A 不具备)
k. **run_report.json 结构**: {files_processed, model_lines_removed, netlist_rewrites, mode_swaps, spf_swaps, preserves, errors:[]}
l. **anti-hardcode-A**: 输出树 grep 无 A-token (model.sp/model_thick.sp/ALT_pst/ALT_tsf/corner_dejoa/TYP_98_RCC/spicemd/CaPad_sim2_hspeedonly/V0_Lay_20260723) — 全用 B 值
m. **3-seed 确定性**: 3 随机种子跑, 输出树字节相同 (禁时间戳)
n. **幂等**: 对已迁移树再跑一次, 0 变更 (run_report.errors=[], changes=0)

### negatives (≥3, 全 FAIL)
- neg_empty: sp_deck_migrate.py 空壳 (只 print)
- neg_print: 只 print 期望 report 串不做事
- neg_core_removed: 参考解删 model-strip + path-rewrite 核心逻辑 (只 copy 文件)
- neg_hardcode_a: 硬编码 A 值 (model.sp/ALT_pst/TYP_98_RCC/spicemd) 不读 config B

### trace bug 转 check 齿
- ② U2 兜底检查 (.alter 块内无 model ref 才保留) → check 齿 (d)(h)(i): .alter 块结构保留 + 嵌套 .alter 内 model ref 删
- ③ U3 用户笔误 `schemetic`→agent 验证用 `schematic` → check 齿 (e): 严格按 config 给定的新路径 (B 用 config_B 的值, 不硬编码 "schematic")
- ④ U4 spicemd→spicead 保留行尾注释 → check 齿 (f): 正则验行尾 `$ ...` 注释保留

## ETA
next round (r983) 合成: 写 assets A + hidden B + reference sp_deck_migrate_ref.py + check.py(14 条) + 4 negatives + selftest, 自验 ref PASS + 三假 FAIL + neg_selftest 全 FAIL, 追加 B.jsonl, mark case。

## 心跳口径
- cases/B 501 (不变, 0-case DEBT 轮)
- B.jsonl 499 (不变)
- ledger_B: lbrbv claimed (spice_sim, mc65), 未 mark case
- fresh (mc≥5, src=summary_1120_reconstructed): 329 → 328 (claim lbrbv)
- 🧾 k_rationale: N/A (0-case DEBT, next round 14 条)
