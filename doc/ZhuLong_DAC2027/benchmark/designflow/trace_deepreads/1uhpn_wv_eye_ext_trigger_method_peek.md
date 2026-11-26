# Deepread peek · 1uhpn · WaveView eye-diagram external trigger method Q&A

**session**: 1793779123814_1uhpn.messages.json
**user/host**: qiang3xu @ hfeg0pgn094 (10.129.35.193)
**mc**: 22 (kw: waveview:26;schematic:18;virtuoso:5;aether:4;netlist:2;cadence:2;synopsys:1)
**shard**: D · domain=waveform
**ledger history**: parked 2026-11-15 03:02 「Q&A/teaching: eye-diagram trigger setup + marker font size how-to + aborted circuit summarize (SIGKILL); no produce-task deliverable」 → 2026-11-15 reaudit §r733 判定「可造(待深peek定形态)」→ r929 revival re-peek

## Trace summary (16 msgs, agent=lead)

| idx | role | content (excerpt) |
|---|---|---|
| 0 | U | `<user_input mode="act">waveview eye-diagram external trigger,how to set?</user_input>` |
| 1 | A | skill ask-eda → query "WaveView eye-diagram external trigger setup" |
| 2 | U | command invocation ask-eda |
| 3 | A | run_approved_command python-runner → ask_eda.py "WaveView eye-diagram external trigger how to set" |
| 4 | U | tool result (AskEDA Dify API answer) |
| 5 | A | **GOLD** — full "WaveView 眼图（Eye Diagram）外部触发（External Trigger）设置方法" guide |
| 6,7,8 | U | (repeated) "waveview怎么设置marker点的字体大小" (separate sub-task, not used) |
| 9 | U | "/proj/m2701/V0_DDR2/workdir/qiang3xu/MPW_xuq/PRBS_TM总结一下这个电路" (aborted) |
| 10-15 | A/U | aborted (SIGKILL on ask-eda; user_abort on read_files) |

## A-faithful selection (§A档选轮规则①)

✅ **U#0 = msg[0]** = 首条 user turn = 提出需求（"waveview eye-diagram external trigger,how to set?"）— 非 mid-conv，符 A档合规（同 r922 ArgparseWaveviewFixQA-001 precedent）。

🚫 不选 U#6/7/8（marker font size，已重发 3 次但本会话无 gold 答复，A 未回应该子任务）。
🚫 不选 U#9（给出路径，请求"总结电路"，被 SIGKILL，无 gold）。

## GOLD answer (A#5, full text preserved)

```
## WaveView 眼图（Eye Diagram）外部触发（External Trigger）设置方法

在 Custom WaveView 工具中设置眼图的外部触发，主要步骤如下：

### 1. 准备工作（DDR3 测量）
setenv CX_DRTAB_FILE <derating_table_file>

### 2. 绘制眼图
- 在波形浏览器中，选择信号（地址/命令/数据）
- 绘制该信号的眼图

### 3. 设置外部触发信号
- 眼图面板右下角有外部触发信号放置区域（提示框/虚线框）
- 从波形浏览器拖拽触发信号（如 DDR3 的 CLK 或 DQS）到眼图面板右下角
- 出现提示框时松开鼠标

### 4. 调整外部触发参数（可选）
- 眼图面板右键 → Eye Diagram Settings
- External Trigger 选项卡
- Trigger Signals 表格：触发信号 + 触发值
- 修改触发条件（触发沿/电压阈值）→ Apply

### 5. 其他相关设置
- Auto-Width
- User Width
- User Data Rate
- Same as UI / 0.5UI
- Eye Shift
- Center at Eye Opening
- Show Overshoot and Undershoot Lines

### 总结
先绘制眼图 → 将触发信号拖放到眼图面板右下角 → 在设置中微调触发参数

--- AskEDA Knowledge Base ---
- wv_ug.pdf (score: 0.99)
```

## Buildable assessment

✅ **真实 trace** (messages.json scp'd from 10.129.35.193, 16 msgs)
✅ **revival 合规** (U#0=msg[0], A档选轮规则①, park 早于 r922 precedent 确立)
✅ **D-domain** (waveform: WaveView 工具眼图设置，kw waveview:26 + schematic:18 dominant)
✅ **k≥10 有牙 check** (manual-grounded howto produce reframe，套 r928 SpiceIbisConvMethodQA-001 proven pattern：candidate 读 knowledge doc + 问题 → 结构化操作指南 JSON {methods/prerequisites/steps/parameters/cited_sections/primary_method}，check 真跑 B subprocess 断言 JSON 结构 + cited 真实 + 反硬编码 + 3-seed 幂等)
✅ **资产 synthesized-reframe** (knowledge doc 从 A#5 GOLD 合成，自包含，无 /proj 依赖)
✅ **A-faithful** (U#0=msg0 提出需求 verbatim)

## 拟造 r929 (本轮)

- **case_id**: EDA-Eval-DesignFlow-WvEyeDiagExtTrigMethodQA-001
- **domain**: waveform
- **grade**: A (trace-faithful)
- **l1_subgrade**: L1-realrun-python (续标第 12 case)
- **asset_fidelity**: synthesized-reframe (D 域第 4 例，承 r921/r924/r928 范式)
- **k**: 12 断言 a-l

**资产 A** (从 A#5 GOLD 合成):
- `wv_eye_ext_trigger_method_A.md` — WaveView eye-diagram external trigger 知识手册：
  - §1 Overview (Custom WaveView eye-diagram concept)
  - §2 Method 1: GUI Manual Setup
    - §2.1 准备工作 (DDR3 derating table `setenv CX_DRTAB_FILE`)
    - §2.2 绘制眼图 (信号选择 + 眼图绘制)
    - §2.3 设置外部触发信号 (拖拽到右下角)
    - §2.4 调整外部触发参数 (Eye Diagram Settings → External Trigger tab)
  - §3 Method 2: SKILL/TCL Script Setup (Custom WaveView SKILL commands)
  - §4 External Trigger Parameters Reference (table: parameter/value/description)
  - §5 Other Eye Diagram Settings (Auto-Width/User Width/User Data Rate/Same as UI 0.5UI/Eye Shift/Center at Eye Opening/Show Overshoot Undershoot Lines)
  - §6 AskEDA Knowledge Base citation (wv_ug.pdf)
- `question_A.txt` — verbatim U#0: "waveview eye-diagram external trigger,how to set?"

**hidden B** (平行场景，反硬编码 A-only token):
- `wv_jitter_measurement_method_B.md` — WaveView Jitter Measurement 知识手册（B-only 主题）：
  - §1 Overview (jitter measurement concept)
  - §2 Method 1: GUI Manual Measurement
    - §2.1 准备工作 (jitter measurement license)
    - §2.2 选择 jitter 类型 (period jitter / cycle-to-cycle jitter / N-cycle jitter)
    - §2.3 设置 jitter 测量 (Jitter Measurement panel)
    - §2.4 调整 jitter 参数 (RJ/DJ/TJ separation)
  - §3 Method 2: SKILL Script Measurement (Custom WaveView SKILL jitter commands)
  - §4 Jitter Parameters Reference (table)
  - §5 Other Jitter Settings (histogram / bathtub / BER / eye-contour)
  - §6 AskEDA Knowledge Base citation (wv_jitter_ug.pdf)
- `question_B.txt` — "waveview jitter measurement how to setup and analyze"
- `hidden_manifest.json`

**A-only tokens (反硬编码)**: {eye-diagram, external_trigger, Eye_Diagram_Settings, External_Trigger, Trigger_Signals, derating_table, CX_DRTAB_FILE, Auto-Width, User_Width, Eye_Shift, Center_at_Eye_Opening, Overshoot_Undershoot, wv_ug.pdf, DQS, DDR3}

**B-only tokens**: {jitter, period_jitter, cycle_to_cycle, N-cycle_jitter, Jitter_Measurement, RJ, DJ, TJ, histogram, bathtub, BER, eye_contour, wv_jitter_ug.pdf}

**candidate_ref.py** = `wv_method_guide.py`:
- Markdown 手册解析（##/### sections + 方法分类 GUI_MANUAL_MARKERS/SCRIPT_MARKERS + 步骤 ### 子标题/数字项 + 参数表 `| param | value | desc |` + cited_sections 段标题 + primary_method 由问题关键词决定）
- 输出 JSON {question, methods[{name,tools[],steps[],description}], prerequisites[], parameters[], cited_sections[], primary_method, overall}
- 同时输出 report.txt + stdout JSON

**check.py 12 断言 a-l**:
- a: zip + wv_method_guide.py + out_A.json 存在
- b: py_compile candidate
- c: A out_A.json 合法 JSON + 7 顶层键
- d: B stdout 合法 JSON + 7 键
- e: B methods 覆盖 gui_manual + script_based
- f: B primary_method 与 question 匹配（gui_manual 优先 for "how to setup"）
- g: B cited_sections 全在 B 手册
- h: B parameters 非空 + table format (param/value/desc 列)
- i: B prerequisites 非空
- j: report.txt 含 method/step/parameter
- k: 反硬编码 B stdout 0 个 A-only token
- l: 3-seed md5 一致（幂等）

## 0-case 合规

本轮 peek + synth ~35min（在 40min 预算内，单轮交付）。

## References

- r928 SpiceIbisConvMethodQA-001 (proven pattern: manual-grounded howto produce reframe)
- r922 ArgparseWaveviewFixQA-001 (A-faithful U#0=msg0 precedent for parked revival)
- pool_reaudit_D.tsv §r733 条目（1uhpn 可造判定）
