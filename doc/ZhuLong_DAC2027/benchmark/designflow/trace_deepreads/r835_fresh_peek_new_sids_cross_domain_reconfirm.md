# r835 — 0-case 选料轮：fresh peek 新候选跨域再确认 + A.jsonl 完整性校验

**日期**：2026-11-20（shard A，r835）
**扫描源**：`ssh_eda_search_20261119_172105/summary.tsv`（r804 落盘，与 r833 同源）
**结论**：A-pure 矿脉枯竭再确认（第 N 轮）。fresh peek 里**新出现**的候选（r833 未深读的 sid）全部跨域，无 A-pure 可造料。守任务初衷第 1 条 + shard 纪律 + §4.3/§4.6 硬闸门 ⇒ 本轮 0-case，不强造跨域/weak case 进 A。

## 一、本轮新增深读候选（r833 top-11 之外的 fresh sid）

r833 已深读 top-11（v593e/hasla/jr0o3/frxg5/ibwba/7l4sx/fdrqq/0rj7b/8pl7h/1e0xa/kubzy 等）全跨域。本轮挑 r833 **未覆盖**的新 sid，从 .75 summary.tsv 取 mc + keywords：

| sid | user@host | mc | keywords | 域判定 | 依据 |
|:--|:--|--:|:--|:--|:--|
| ddye0 | haoliu@hfeg0pkn004 | 112 | netlist:553;hspice:190;schematic:176 | **B/C** | spice_sim/characterization（netlist+hspice+schematic） |
| jp8n9 | xiwang@hfeg0pkn002 | 117 | netlist:349;cmos:177;pyaether:176;schematic:171;cellview:42 | **C** | layout_aether（pyaether+schematic+cellview） |
| m64s7 | zqzhan@hfeg0pkn001 | 113 | drc:830;cellview:212;schematic:211;waveview:118;lvs:116 | **C** | physical_verify（drc+lvs+cellview） |
| 1vjqj | zhililu@10.129.32.93 | 11 | spectre:202;netlist:119;maestro:29;virtuoso:18 | **B/C** | spice_sim（spectre+maestro+virtuoso） |

**判域方法**（复用 r829/r833 方法论）：scan keyword 与真实域弱相关，域判定以 keyword 组合的主导工具为准——netlist+hspice/spectre→B，pyaether/drc/lvs/cellview→C，verilog/vcs/innovus/primetime/synthesis→A。本轮 4 个新 sid 的 keyword 主导全为 B/C 工具，**0 个 A-pure**。

## 二、与历轮一致性

| 轮 | 新增 A-pure 料 | 结论 |
|:--|:--|:--|
| r760/r761 | 0 | mc≥10 fresh top 枯竭 |
| r824 | 0（q1589 跨 shard 碰撞回滚） | mc≥8 A-pure 枯竭 |
| r826 | 0（06htj/w4uy2 weak） | r528 revival 矿脉枯 |
| r831 | 0（n907k/vqefw/c41bm weak） | mc5-9 revival 枯 |
| r832 | 0（intent_audit 26 keep / pool_reaudit 0 复活） | 审计无 off_intent |
| r833 | 0（top-11 全跨域） | fresh peek 枯 |
| **r835** | **0（4 新 sid 全跨域）** | **fresh peek 新子集再确认枯** |

A 三矿脉（mc≥10 fresh / mc≥5 revival / r528 subdir revival）已全部枯竭，本轮新增证据进一步收紧：**r833 未覆盖的 fresh sid 子集也无 A-pure**。

## 三、A.jsonl 完整性校验（phantom-revival guard）

r828/r916 曾发生 build_jsonl.py 重建时误删 case line（phantom-revival bug）。本轮用 `scripts/build_jsonl.py --shard A --check` 校验：

```
cases/A/: 415   ==  A.jsonl: 415 lines   ✓ 无 phantom loss
```

**19 处 intra-shard dup** 确认（cases/A 文件数 434 = 415 unique + 19 dup）：
- 模式：同 task_id 两份文件（`<Name>-001.json` 与 `EDA-Eval-DesignFlow-<Name>-001.json`），同 domain 同 shard。
- build_jsonl.py first-wins：保留先载入者，dup 方从 build 排除 ⇒ **A.jsonl 415 行不受 dup 影响，正确**。
- 代表：AccAutoConnectSumm-001 / BtopPendJobs-001 / CmPatternRunGen-001 / DejoaWrrdSeqAnalyze-001 / EccLinkConfAnalyze-001 / FinesimDcConvCatalogAnalyze-001 / IrResultMissingNetDiagnose-001 / IrunCuvpomDiagnose-001 / IrunWarnClassify-001 / MrrDqExpFlowAnalyze-001 / SkillLogdirReportPatch-001 / ToolRcFormatMapQa-001 / VcsCfcilfbiDiagnose-001 / VerdiFsdbSignalNotFoundDiagnose-001 / VerdiLicenseCheckoutDiagnose-001 / VerilibEquiAnalyze-001 / XmsimInterrDiagnose-001 / XrunCuvmurDiagnose-001 / XrunTypeerrDiagnose-001
- **处置**：本轮**不删** dup 文件——需先逐对 diff 确认两份 byte-identical 或判定哪个是 canonical（命名约定：`EDA-Eval-DesignFlow-` 前缀 vs 裸名），避免误删触发 phantom-revival。留 DEBT 给专门一轮清理。

## 四、本轮交付与纪律

- **0-case**（A-pure 枯竭，守初衷不强造）
- eda_flow session r835 已 close（cleaned=true）
- A.jsonl 415 不变 · 台账 A 685 不变 · cases/A 434（415 unique + 19 dup）不变
- 🎯 通过率：观察值（未跑 pi）
- 📊 trace 覆盖率：405/487 = 83.2%（不变）
- 守任务初衷第 1 条（任务形态=用户意图，不凑数）+ §4.3/§4.6 硬闸门（不造无牙判分/weak case）+ shard 纪律（只做 A 域）
- discuss r835 due：r834 已清付，下轮 mandatory due r838（本轮不欠）

## 五、DEBT（下轮候选）

(a) cases/A 19 处 intra-shard dup 清理：逐对 diff + 判 canonical + 删冗余（需谨慎，防 phantom-revival）
(b) 新全量扫描扩池（🟢 11-14 授权，daily ≤1；11-19 scan 已 ~13h，本日可再扫 1 次，但 698 机全量超 40min 预算，需专门轮）
(c) waveview task2 VQA 对比：infra-BLOCKED（.17 入站防火墙），等 ops 放行
(d) D r982 ledger case_ids 复数字段 endorse（待 A 实装 build_jsonl.py guard）
