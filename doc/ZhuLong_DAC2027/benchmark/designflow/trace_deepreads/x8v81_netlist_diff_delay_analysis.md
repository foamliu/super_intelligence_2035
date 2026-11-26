# Deepread: x8v81 — Netlist Diff + Post-Sim Delay Root-Cause Analysis

**trace_source**: session `1793945103405_x8v81` / user `dsgao` / host `hfhds201` (10.129.32.75 = .75 local) / mc `?` (parked reaudit REVIVABLE_QA)
**cline session file**: `/home/dsgao/.cline/data/sessions/1793945103405_x8v81/1793945103405_x8v81.messages.json` (596 KB, 99 msgs, 8 user turns, persists on .75)
**domain**: eda_other (A-shard). Netlist-level post-sim delay analysis on DRAM digital blocks (drcpa_digital / drcoa_digital R_trimEqOff).
**deepread round**: r636 (2026-11-16). DEBT 1 (fresh deepread, synthesis next round).

---

## 1. User Intent (verbatim, trace-faithful A-档)

**Turn 0 (primary task — the case)**:
> `@/proj/drcpa/V0/workdir/dsgao/simulation/drcpa_digital_R_trimEqOff_schematic_ALPS/drcpa_digital_R_trimEqOff_schematic.netlist` 和 `/proj/drcoa/V0/workdir/dsgao/simulation/drcoa_digital_R_trimEqOff_schematic_ALPS/drcoa_digital_R_trimEqOff_schematic.netlist` 有区别吗，为什么后仿真 delay 有差异

= 比较两份 post-sim netlist (drcpa_digital vs drcoa_digital, R_trimEqOff) + 解释后仿真 delay 差异根因。**analysis-Q&A, 非产脚本**。

**Turn 6 (secondary — natural hidden-B variant)**:
> `@/proj/drcoa/.../drcoa_digital_R_tOCTrim_schematic_ALPS/...netlist` 和 `@/proj/drcpa/.../drcpa_digital_R_tOCTrim_schematic_ALPS/...netlist` 有差异吗，仿真出现了 delay 的差异

= 同一任务模式，不同 trim 变体 (tOCTrim vs trimEqOff) 的 netlist pair。

**Other turns (NOT in scope of this case)**:
- Turn 2/3/4/5: GIDL array ctrl tb 修改 (fngidl 恒为 vwlp / fngidlmode 前后半程 / 步长 10p / 跑波形) — FineSim sim-config 任务，不同子题。
- Turn 7/8: 抓 si.inp corner 电压值 + 编变量文件 — 另一子题。

**Case 聚焦 turn 0** (单一交付物 = netlist-diff + delay root-cause 报告)。Turn 6 的 tOCTrim pair 作为 hidden-B 候选 (同任务不同 pair，需 synthesis 轮验证 tOCTrim diff 与 trimEqOff diff 确实不同)。

---

## 2. Agent Tool Chain (99 msgs, 8 user turns)

| tool | count | purpose |
|---|--:|---|
| read_files | 15 | 读两份 netlist 各段 (1-60, 60-140, 200-340, 360-459/462) + tb 文件 + pt0 波形 + si.inp |
| list_allowed_files | 9 | 列 sim dir / Desktop / GidlAryCtrl run dir |
| run_approved_command | 7 | ls -l symlink / python diff_netlists.py / launch_v2 sim / wait / plot |
| editor | 8 | 写 diff_netlists.py / 改 tb v2.sp / 写 plot_v2_waveforms.py |
| search_codebase | 6 | 搜 SUBCKT mx2LVSx2 / invDS / fngidl / vwlp / GidlMode |
| get_agent_policy_status | 1 | — |

**关键路径 (turn 0 分析)**: list_allowed (两个 sim dir) → 发现 netlist 是 symlink → read_files 1-60 (两份) → run ls -l symlink → write diff_netlists.py → run diff → read_files 360-459/462 (顶层 R_trimEqOff) → read_files 200-340 (mx2LVSx2 subckt def) → search mx2LVSx2/invDS → **结论 [msg 25]**。

---

## 3. Agent Conclusion (msg 25, 全文要点)

**结论：两份 netlist 确实有区别，功能上多了一个反相器级，这就是 delay 差异的来源。**

两份 netlist 是两个不同顶层模块 (`drcpa_digital/R_trimEqOff` 和 `drcoa_digital/R_trimEqOff`)，共享同一套 stdcell (invDS/invDSx1/dlybias_gut/mx2LVSx2/dlybiasn250ps/dlybiasn500ps 子电路定义完全一致)，开头 90% 内容相同，**只有顶层 R_trimEqOff 的控制通路接线不同**。

### 具体差异 (1 处功能差异 + 2 处无害差异)

**功能差异 — trim mux (mx2LVSx2) 选通信号生成通路多了 1 级反相器：**

mx2LVSx2 子电路 (两文件一致): `.SUBCKT mx2LVSx2 A0 A1 S SN Y ...` → S/SN 是 2:1 选择器选通信号。

顶层接线对比 (已从 trace 抽取验证, 见 staged_assets)：

| | drcpa (`drcpa_digital`) | drcoa (`drcoa_digital`) |
|---|---|---|
| 一级反相 | `XI7<x> cm1_ro_EqOffWlOn<x> → cm1_ro_EqOffWlOnN<x>` | `XI7<x> cm1_ro_EqOffWlOn<x> → trimN<x>` |
| 二级反相 | **无** | **`XI13<x> trimN<x> → trim<x>` (新增 invDSx1)** |
| mux 选通 | XI4/XI6/XI3 用 `cm1_ro_EqOffWlOn<x>` / `cm1_ro_EqOffWlOnN<x>` | XI4/XI6/XI3 用 `trim<x>` / `trimN<x>` |

- drcpa: 选通真信号直接用 `cm1_ro_EqOffWlOn` (源码)，仅反相信号经 1 级 invDSx1。
- drcoa: `trim` 进 mux 前经 XI7 + XI13 两级 invDSx1，`trimN` 经 1 级。逻辑电平等价 (trim = cm1_ro_EqOffWlOn, trimN = cm1_ro_EqOffWlOnN)，但**选通信号到达时刻比 drcpa 晚约 1 个 invDSx1 传播延时** → mux 切换滞后 → delay 差异。多出的 XI13 也给 3 个控制网加了栅电容负载。

**无害差异:**
1. 文件头 Top Design 名 + 时间戳 (drcpa_digital 14:02 vs drcoa_digital 14:04) — 注释。
2. dlybiasn500ps 内部 switch_open/switch_close 实例排列顺序不同 (~375-422 行) — 纯顺序，集合一致，无功能影响。

**行数差异 +3 (459 vs 462) = 新增的 3 个 XI13<2:0>。**

### 为什么后仿真 delay 有差异
drcoa 在 trim/cm1_ro_EqOffWlOn 到 mux 选通的路径上多插入一级 invDSx1 (XI13) 缓冲/重定时反相器。delay (R_trimEqOff) 仿真测量路径 (EqSa→EqSafastN→dlyg/dlybias→mux 选择的 trim 网络→EqSaOut) 里 mux 选通信号 trim/trimN 到达边缘被额外推迟约一个反相器延时 → mux 切换瞬态不同 → prop delay 差异。

---

## 4. Staged Assets (trace-embedded, asset_fidelity=original)

从 trace read_files tool_results 抽取，行号剥离还原，按原行号重建 (gaps = trace 未读段, 多在共享 stdcell 定义区, 不影响 diff)。

**.75 workdir** (`shardA_20261116-r636_deepread-x8v81_0`): `clean_assets/` 下 4 文件：
- `drcpa_trimEqOff.netlist` (17943 B, 301/459 lines recovered, top-level R_trimEqOff 完整)
- `drcoa_trimEqOff.netlist` (18447 B, 243/462 lines recovered, top-level R_trimEqOff 完整, 含 XI13)
- `drcpa_tOCTrim.netlist` (14878 B, 160/409 lines, top-level 需 synthesis 轮验证)
- `drcoa_tOCTrim.netlist` (16440 B, 416/432 lines, top-level 需 synthesis 轮验证)

**本地 staging**: `designflow/trace_deepreads/x8v81_staged_assets/` (synthesis 轮从 .75 workdir 或 trace 重抽落盘)。

**diff 核实** (grep 已确认):
- `drcoa_trimEqOff.netlist` 含 `XI13<2:0> trimN→trim invDSx1` (3 行, line 445-447)
- `drcpa_trimEqOff.netlist` **不含** XI13 (grep -c = 0)
- 两份顶层 mux: drcpa 用 `cm1_ro_EqOffWlOn/cm1_ro_EqOffWlOnN`, drcoa 用 `trim/trimN`
- mx2LVSx2 subckt def (两文件一致): `.SUBCKT mx2LVSx2 A0 A1 S SN Y inh_vbn inh_vbp inh_vcc inh_vss`

**注意**: /rundata/... /proj/... 原路径 Permission denied (属 dsgao)，故必须 trace-embedded (同 r631/r634 模式)。

---

## 5. Synthesis Plan (下轮 r637 执行)

### Case
- **case_id**: `EDA-Eval-DesignFlow-NetlistDiffDelayAnalyze-001`
- **template**: C-A analysis-Q&A (netlist-diff + delay-root-cause)
- **domain**: eda_other
- **A 档**: trace-faithful, 用户原话逐字 (turn 0)
- **交付物**: `netlist_diff_delay_analysis_report.json` (zip 内单文件, 结构化 JSON 报告)

### A (visible, 进 SUT 沙箱)
- `drcpa_digital_R_trimEqOff_schematic.netlist` (drcpa_trimEqOff)
- `drcoa_digital_R_trimEqOff_schematic.netlist` (drcoa_trimEqOff)
- prompt = 用户原话 turn 0 逐字 + 路径换成 asset 文件名

### B (hidden, 不进 SUT)
- **候选**: tOCTrim pair (drcpa_tOCTrim + drcoa_tOCTrim) — 同任务不同 trim 变体。
- **synthesis 轮先验证**: tOCTrim pair 的 diff 是否与 trimEqOff 确实不同 (≥6 anti-hardcode 维度)。若 tOCTrim diff 与 trimEqOff 太相似或 tOCTrim 顶层不完整，回退到合成 B (构造一个 drcpa-vs-drcoa 变体, diff = 不同位置/不同实例, 如 XI13 改为 XI14 或 mux 选通改用 net 名变体)。
- B 的正确答案必须与 A 在以下维度全异: top_design 名 / 差异实例名 (XI13 vs 其他) / 差异实例类型 (invDSx1 vs invGSx2 等) / 受影响 mux 实例 / 选通信号 net 名 / 行数差 / 根因描述。

### check() 结构 (k≥8, ①②… markers)
1. **content-correctness (a-n, ~12-14 条)**:
   - zip 内单文件 report.json
   - report 顶层段齐全 (netlist_overview / structural_diff / delay_root_cause / evidence / conclusion)
   - netlist_overview: 两 netlist 是不同 top design (drcpa_digital vs drcoa_digital), 共享 stdcell
   - structural_diff: 唯一功能差异 = drcoa 顶层 R_trimEqOff 多 1 级 invDSx1 (XI13<2:0>)
   - XI13 实例: trimN→trim, 类型 invDSx1
   - drcpa 侧: XI7→cm1_ro_EqOffWlOnN, 无 XI13
   - drcoa 侧: XI7→trimN + XI13→trim
   - mux (mx2LVSx2) 选通: drcpa 用 cm1_ro_EqOffWlOn/cm1_ro_EqOffWlOnN, drcoa 用 trim/trimN
   - mx2LVSx2 = 2:1 mux, S/SN = select
   - 无害差异 ≥1 (header timestamp / switch ordering)
   - 行数差 +3 = 3 个 XI13<2:0>
   - delay_root_cause: 选通信号到达推迟约 1 invDSx1 延时 + 栅电容加载 → mux 切换瞬态不同 → prop delay 差异
   - failure_category = structural_difference (非 sim_error / non_convergence)
2. **evidence-verification (o)**: report 中 evidence 段引用的 token 必须是 A netlist 原文子串 (XI13/trimN/trim/cm1_ro_EqOffWlOn/mx2LVSx2/invDSx1 等, ≥10 token)
3. **B judge-self-check (p)**: 内嵌 `_parse_b` 独立解析 tOCTrim pair (或合成 B), 断言 A report 与 B truth 在 ≥6 anti-hardcode 维度全异 (top_design / diff 实例名 / 实例类型 / mux net 名 / 行数差 / 根因)
4. **3-seed (q)**: 随机抽 net 子集 (3 seed) 结论一致

### 自验
- ref 解 (基于 msg 25 结论) 跑 check() PASS (k 条全过)
- ≥4 neg FAIL distinct: empty→a / print-no-evidence→o / wrong-rootcause (说 sim convergence)→delay_root_cause 条 / b_overfit (硬编码 trimEqOff 答案套到 B)→p
- §4.9 三假 (空壳 / 只 print 期望 / 删核心) 全 FAIL
- e2e: jsonl test field 抽出独立跑 PASS

### 资产落盘 (synthesis 轮)
- `benchmarks/EDA-Eval-DesignFlow/assets/EDA-Eval-DesignFlow-NetlistDiffDelayAnalyze-001/`: 2 netlist (A) + hidden/ (B pair + hidden_manifest.json)
- `benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-NetlistDiffDelayAnalyze-001/`: check.py + reference_submit.zip + negative/ + negative_selftest.py
- A_FILES 内联进 check.py (自包含)

---

## 6. Ledger

- `parked_reaudit_A.tsv` x8v81 行: revivable=yes, trace_avail=EXISTS
- 本轮: `trace_ledger.py --shard A claim --session 1793945103405_x8v81 --user dsgao --host hfhds201 --match ? --domain eda_other`
- 下轮合成后: `mark --session ... --status case --case-id EDA-Eval-DesignFlow-NetlistDiffDelayAnalyze-001`
- 11-15 mandate Part 二 复活队列: 70 → 69 (本条 deepread 闭合, 合成在下轮)

---

## 7. 风险 / 待验证 (synthesis 轮)

1. **tOCTrim B 验证**: tOCTrim pair 的 top-level R_tOCTrim 是否在抽取片段里完整？diff 是否与 trimEqOff 确实不同？若不行 → 回退合成 B (构造变体 netlist)。
2. **netlist gaps**: drcpa_trimEqOff 缺 60-200/340-360, drcoa_trimEqOff 缺 141-359 — 都在共享 stdcell 定义区 (两份一致), 不影响 diff 判分。check() 只验顶层 R_trimEqOff 段 (完整)。
3. **match_count**: parked 文件无 mc 列, ledger claim 时从 summary.tsv 查或标 n/a。
4. **domain**: parked 标 eda_other, 内容偏 digital post-sim。两者皆 A-shard, 保持 eda_other (与 parked 一致)。
