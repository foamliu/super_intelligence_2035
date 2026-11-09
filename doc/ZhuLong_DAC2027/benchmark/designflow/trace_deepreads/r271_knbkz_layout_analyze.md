# 深读笔记 · 1793842357080_knbkz (legendd @ hfeg0pkn002/10.129.2.12)

- **trace**: 1793842357080_knbkz.messages.json (1.3MB, 277 msgs, 10 real user turns)
- **user**: legendd — **NEW (0 case in ledger_C)**；agent=lead pyAether 代码工程师
- **mc/tools**: tot=688, pyAether593 + dbGet421 + dbShape45 + virtuoso40 + schematic105 + netlist66 + cellview? ; layout-dominant (lay612 sim76)
- **workspace**: /ai_sandbox/drvqa/V0/agentdir/legendd (空，需经 pyAether aeGetCurDesign 连真实 OA)
- **claimed**: r271 (2026-11-09)，DEBT:1 deepread-done synthesis-pending → r272 出 case

## 两个候选任务

### 任务①（推荐种子）— U0：「分析一下当前版图的大小，统计layer 信息」
- **A-faithful eligible ✓**：提出需求，未给根因/修复方向。
- **agent 真实产物**：`/home/legendd/.cline/skills/eda_agent/analyze_layout.py` (6504 bytes)
  - 经 SandBox run_code 写入；read_files 回读确认；run_code 实跑产报告。
  - 功能：aeGetCurDesign() → drvqa_array_core/Ary16G/layout → 遍历 layer/purpose →
    die size(bbox) + per-(layer_num,purpose_num) shape 计数 + area + 报告。
  - 关键 API：ae.dbGetPurposeNameByLayerId / dbGetPurposeNumByLayerId / layer mapping。
  - 真实报告输出（U#127 print_log）：
    ```
    AETHER LAYOUT ANALYSIS REPORT
    drvqa_array_core/Ary16G/layout
    [1] DIE SIZE (Bounding Box) ...
    [layer/purpose 表 ...]
    ```
- **离线重定义（B 档）**：真实 OA 不可沙盒复现 → 重定义为离线 stdlib：
  给定 layout shape inventory JSON（layers[] + shapes[] with bbox/layer/purpose/type），
  写 Python 脚本产结构化分析报告 JSON：die bbox(所有 shape bbox 并集) +
  per-(layer,purpose) {shape_count, total_area, net_count?} + 顶层 summary。
  check.py 在 hidden B 上 subprocess 真跑候选脚本，断言报告结构（≥8 条件）。
- **DISTINCT from 现有 layout_aether 系**：
  - r264 ScmosCrossProbeCsvGen(OA inst hierarchy cross-probe)、r252 LayStructExtract(layout 结构抽取)、
    r238 LayoutFloorplanGen(floorplan)、r222 SchOaInventoryExtract(OA inventory)、
    r253 PinListPortOrderExtract(pin 顺序)、r254 EmyCdlNetlistExtract(CDL)。
  - 本案首次 ground on「layout die-bbox + per-(layer,purpose) shape 计数/面积 统计报告」。
  - 需确认与 r? 既有 "analyze_layout" 无重叠（grep ledger 未见 analyze_layout 主题 case）。

### 任务② — U129~U257：layer 显示快捷键（更复杂，不推荐作种子）
- U129「我需要一个快捷键，只显示 base layer 和 M1 M2 相关的 layer」
- U173「还要考虑 layer purpose」+ U191「加上 active layer」+ U201「layer purpose 可加入用户指定不显示的 purpose」
- U217~U257「写脚本切换两套快捷键配置，本身绑定为 tab 键」
- 偏 bindkey/LSW 配置切换，harness-adjacent，check 难定 8+ 独立条件。**不取**。

## 选料决策
- 取任务①作 r272 case 种子（A-faithful eligible，本 case 做 B 档）。
- trace 277 msgs < 600 / 1.3MB < 2MB → 不触发深读例外，r272 必须出 case（DoD）。
- r272 第一件事：合成 analyze_layout case（assets A inventory + hidden B inventory +
  reference golden analyze_layout.py + check.py ≥8 条件 + 5 negative + negative_selftest）→
  自验 → 追加 EDA-Eval-DesignFlow_C.jsonl → mark case → 日报。

## r271 选料筛选结论
- r270 DEBT 候选(d1yda/vhb6i/nwhe2)深读全判 weak(prose/diagnosis/thin) → parked。
- mc15-29 fresh 强信号 NEW-user 顶部(i6fn6/ajcab/j98ua)深读全判 weak/wrong-shard
  (env-recon / duplicate-schematic-highlight / sim-scenario) → parked。
- e0014566 fresh 4 条(ewjnc/zh4of/csrxv/uu38v)全判 weak/duplicate/vague/bridge-test → parked。
- **触发 .75 rescan**（11-06~11-09 eda_trace logs，227 fresh layout-dominant 候选）→
  顶部 knbkz(legendd NEW) 深读确认 CLEAN layout_aether 种子(任务①) → claimed，r272 出 case。
- 台账：case 259 · parked 217(+10) · claimed 1(knbkz) · 已动 477。
