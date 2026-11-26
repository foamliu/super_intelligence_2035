# r463 B 域 mc≥10 候选质量枯竭 · 4 deepread 证据 (2026-11-13)

> **结论**：1109 池 B 域 mc≥10 fresh=20（>0，**非池枯竭**），但 4/4 deepread 候选**全为跨域 mislabel**。
> B keyword filter（`hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim`）
> 以「关键词出现」而非「关键词主导」入池 ⇒ 捕获大量 DRC/LVS/aether/waveform/workspace 任务，
> 这些任务 merely *mention* hspice/spectre 但实际 deliverable 不 drive SPICE sim。
> 这是**质量枯竭**（同 shard A threshold_eval「quality-exhausted not quantity-exhausted」），
> 非 P-004 4-shard dedup 能修——4 个候选已 truly-4shard-fresh（mc-matrix 已排除 4 shard 台账），
> 问题在 **filter 本身**不是 **dedup 口径**。

## mc-matrix 证据（src=designflow/summary_1109.tsv）

```
shard B: mc>=10 pool=777 touched=757 fresh=20   (>0, 不能下「池枯竭」结论)
ALL:     mc>=10 pool=2882 touched=2370 fresh=512
```

## 22 B-fresh 候选 keyword profile（candidates_mc10_classified.tsv, 全 multi-shard, **0 B-only**）

domain 列全为 A+B+C+D / B+C+D / A+B+C，**无一条 B-only**。
B-keyword（hspice/spectre/...）计数均 ≤8 且非 top kw；top kw 全是 drc/lvs/aether/netlist/waveview。
对照：r462 真正 B case zm0zw 的 kw = `analog:1007`（B-spice 主导），本批 22 条无一有此 profile。

## 4 deepread（全 parked，ledger note 已记）

### 1. tvc27 (mc=88, yongk1li@hfeg0plg75) → C physical_verify
- kw: `drc:98;lvs:77;netlist:25;...;hspice:2` — drc/lvs 主导, hspice 仅 2 (incidental)
- 未深读直接 park（kw 无歧义）：DRC/LVS 任务，C 域

### 2. 721uj (mc=58, gokuguo@hfeg0plg53) → C physical_verify  [deepread]
- kw: `lvs:340;calibre:22;netlist:14;pex:8;pdk:6;hspice:4;drc:4`
- **deepread**：用户让 agent 对比两个 Calibre LVS rule 文件（Test07.lvs / Test08.lvs / Rev13_S10.lvs），
  agent 写 Python difflib 脚本逐行 diff 定位 41 处差异块（SVRF #DECRYPT 加密区 + 明文版本/器件标注差异）。
- **任务 = LVS rule-file 文本 diff**，纯 physical_verify (C)，无 spice sim / 无 characterization。
  pex:8/pdk:6/hspice:4 是 LVS rule 文件内提到的 PEX/PDK/hspice rule 名，incidental。

### 3. lvack (mc=10, e0039602@hfeg0pkn002) → D waveform  [deepread]
- kw: `hspice:8;synopsys:6;pyaether:3;aether:3;waveview:2;rtl:1` — hspice 是 top kw (8)
- **deepread**：用户有 `wavecompare_simple` 项目（Python，对比 fail/pass FSDB 波形，判 EQ/DIF/GRAY）。
  会话：① 问 EQ/DIF/GRAY 判决逻辑（agent 读 triage.py/locate.py 解释 3×容差/伪影三道检查）
  ② 问具体 GRAY report ③ 问伪影检查 ④ 问精窗口 ⑤ 让 agent 把项目复制到 wavecomparecopy。
- **任务 = HSPICE 仿真波形对比/分析** = D waveform 域（TASK shard 配置明列 D=waveform）。
  hspice:8 来自 wavecompare 工具 parse HSPICE .tbl 输出，incidental；deliverable 不 drive SPICE sim。
  （注：spice_sim↔waveform 边界模糊，但 TASK 配置 waveform 归 D，保守判 D。）

### 4. xtqpe (mc=18, zlhou@hfeg0pkn001) → A/eda_other (harness config)  [deepread]
- kw: `lvs:90;netlist:38;pex:14;hspice:7;aether:3;waveview:2;calibre:2;synopsys:1`
- **deepread**：用户让 agent ① 查 /home/zlhou 下哪些文件是 AI 写的（agent 查 mtime/命名风格判定）
  ② 问能否一次性固定所有对话工作目录 ③ 新建 /home/zlhou/AIworkspace 让 agent 以后都在此操作
  ④ 详细问 cline 界面如何固定工作目录 ⑤ 说明是 terminal 启动 cline。
- **任务 = Cline workspace/工作目录配置 Q&A** = harness/tooling config（A/eda_other）。
  lvs/pex/hspice kw 来自用户 ~/ 下已有的 LVS/PEX/hspice 脚本文件名（agent list_allowed_files 列出），
  本任务零 spice sim 内容。

## 根因分析

B keyword filter 是「出现即入池」（`$6 ~ /hspice|finesim|.../`），不要求 B-keyword **主导**。
后果：任何 session 只要 mention 一次 hspice/spectre（EDA 工程师日常会话高频）就入 B 池，
而真实 B 任务（spice deck 生成/char sweep）的判据应是 **deliverable drive SPICE sim**（.TRAN/.MEAS/.alter/sim invoke），
与 r461 B-D 裁定使用的同一判据。22 B-fresh 全 multi-shard + 0 B-only + 4/4 deepread 跨域 = filter 系统性过松。

## 与既有结论的关系

- **P-004 fresh-pool track**：board.md P-004「fresh-pool track 仍 OPEN」目前聚焦 4-shard 联合排除 code-fix。
  本轮证明：**即使 4-shard 联合排除落地（1109 mc-matrix fresh 已 truly-4shard-fresh），B 仍质量枯竭**
  —— 因为问题在 filter 非 dedup。是 P-004 之上**新增的 filter-quality 层**。
- **P-002 B 数量枯竭（r393, CLOSED）**：r393 在 mc≥30 + spice-dominant 口径判 B 池枯竭。
  换 1109 池 + mc≥10 后 fresh=20（数量不枯竭了），但**质量枯竭**（同 A 域 r374-r380 模式）。
  ⇒ P-002 的「B 数量枯竭」结论在 mc≥10 下应升级为「B 质量枯竭」。
- **r461 B-D 双向 mislabel**：r461 发现 B 把 4 条 netlist-manipulation 任务错标 spice_sim。
  本轮发现**错配的源头在选料**——filter 把 netlist/waveform/config 任务当 B 候选送进来，
  合成时若不严审就造出 mislabel case。修法应前移到 filter。

## 建议（须 @A / 用户裁定，B 不改共享配置）

1. **B filter 改「主导」非「出现」**：入 B 池要求 B-keyword 计数 ≥ 某阈值（如 ≥30% of total kw 或 top-3 kw 含 hspice/spectre/finesim）。
   预期：22 → ~3-5 真正 spice-dominant 候选（同 r462 zm0zw profile）。
2. **或** B filter 增「deliverable drive-sim」预筛（peek session 末尾产物有 .TRAN/.MEAS/.alter/sim invoke 才入池）。
3. **或** 接受 B 在 mc≥10 质量枯竭，B 容量转向 characterization 域深做（r462 zm0zw 已示范）+ 存量 spice_sim case domain-label audit（r461 建议 4 延续）。
4. ⚠️ **不建议** 降 mc 阈值到 <10（同 shard A finding：mc≥5 候选 wrong-shard 主导，降阈值不增 B 真 case）。

## ledger 状态

4 session 均 `mark --status parked`（note: deepread + 跨域 + P-004），不重复捡。
B fresh: 20 → 16（4 parked）。剩 16 候选 kw profile 同样非 B-dominant（未 deepread，留 @A 裁定后处理）。
