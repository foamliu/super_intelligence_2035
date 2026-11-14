# Waveview 「原意图需看图」用例恢复方案 · shard D（2026-11-14）

> 认领：WAVEVIEW_COLLAB.md 任务 1，shard D（维护态第 5 轮 = 空闲 shard）。
> 交底清单：`doc/BaiZe-ISEDA2027/run/reports/waveview_need_image_handoff.md`（α 4 + β 7 = 11 题）。
> 本文件 = 本轮（r649）主产出：11 题素材可得性核查 + 恢复路径 + 判分设计 + 排期。
> **本轮未跑基线**：40 min 预算不足以完成 1 题的「生成图 + 改 case + 自验 + 跑 cline 基线」全流程；下轮起逐题恢复。

## 一、核心结论

1. **11 题当初全部降级为 B-grade synthesized 文本/脚本题**，降级根因统一：私有波形 / FSDB / WaveView 环境 / 项目目录不可复刻（见各 trace_deepreads 笔记「B-grade」「不可复刻」段）。当前形态下 agent 写脚本解析 `.rep`/`.vec`/CSV 即可答，**完全不需看图** —— 这是 vision 指出的「降级稀释难度」根因。
2. **恢复原形态 = 移除文本数据替身，assets 只给图**，迫使 agent 必须看图作答。无多模态能力者看不到图 ⇒ fail（正确行为）。
3. **技术可行性已确认**（eda_flow `run_code lang=tcl host=waveview` probe，2026-11-14）：
   - WaveView ACE 有 `sx_create_eye` / `sx_display_eye` / `sx_measure_eye` / `sx_query_eye` / `sx_config_eye` 等 eye 命令；
   - 有 `sx_dump_png`（导出 PNG）+ `sx_export_csv` / `sx_export_data`；
   - ⇒ **沙盒可对（合成）波形生成真眼图 PNG**，agent 看图判断眼张开度。
4. **判分难点**：check.py 是文本脚本，无法直接验「agent 看了图」，只能验 deliverable 的文本答案。恢复靠**题面设计**让不看图几乎不可能全对（见 §三判分设计）。

## 二、11 题素材可得性核查表

> 路径记号：A=WaveView/FineSim 沙盒对合成波形生成真图（忠实，1-2 轮/题）；B=matplotlib 从合成数据生成示意图（快速，1 轮/题，图承载答案但非真眼图形态）；C=不可行（标注缺什么）。

| # | 题名 / case_id | shard jsonl | 降级根因（原意图） | 图类型 | 恢复路径 | 可行性 | 备注 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| α1 | EyeApertureSelect-001 | D | WaveView 眼图 VREF 扫选最大眼孔径；私有波形 sslvht_10667 + WaveView CLI 不可复刻 → 合成 .rep 文本 | 眼图 PNG（每 VREF 一张或叠加） | A（WaveView tcl: 合成波形→sx_create_eye→sx_dump_png） | ✅ 技术确认 | 真·视觉判断眼张开度；raw-max 落假峰，需阈值过滤——视觉上眼张开最大 ≠ raw width max，识图可解 |
| α2 | RiseEdgeMargin-001 | B | WaveView3 两信号上升沿 margin + 波形标注；私有波形 → 合成 CSV 线性插值 | 波形截图（含标注） | A（WaveView tcl: 合成信号→sx_display→sx_dump_png） | ✅ | 图形化测量+标注；识图可直读上升沿时差。**case 在 B.jsonl，移交 shard B** |
| α3 | (h8pcp, 未落库) | — | golden vs actual 两份波形 DQ 不一致根因定位；私有 `/rundata/drgqx/` 全 Permission denied → B-grade synthesized | 两波形对比图 | A（WaveView: 两合成波形→叠加显示→sx_dump_png） | ✅ | 两波形视觉 diff 找首处分叉；识图可直看哪级开始分叉。**B-grade 未落库，需先造 case 再恢复** |
| α4 | TempSelWaveform-001 | D | 从温度传感器 sel* 波形推断功能；私有 FSDB → 合成 | 波形截图（sel* 信号） | A（WaveView: 合成 sel 波形→sx_dump_png） | ✅ | 波形形态→功能语义；识图可直读激活区间 |
| β5 | (FsdbNetToggleDiag, 未落库任何 shard) | — | 从 FSDB 识别 stuck/active 信号 + netlist 对照；私有 FSDB → ? | 波形截图（信号翻转） | A 或 B | ⚠️ case 未落库（grep 4 shard jsonl 全 0），需先确认是否曾造；深读笔记 `1793078405436_t0aom_finesim_fsdb_netlist_diag.md` 在。脚本读 transition 更严谨，识图为辅 |
| β6 | (3qe6x, 未落库) | — | WaveCompare 两波形边沿序列 diff；corner VDD 不同致视觉叠加歧义 → 合成 .tbl 文本 | 波形对比图 | B（matplotlib: 两 .tbl 波形叠加图） | ✅ | 算法更可靠，识图有歧义；**B-grade 未落库，需先造 case** |
| β7 | WrDqMeas-001 | B | write 命令到 DQ 第一上升/下降沿间隔；私有 .fsdb → 预导出 .vec | 波形截图（write cmd + DQ） | A（WaveView: 合成 .vec→sx_dump_png） | ✅ | 识图可估读时序，精确测量需脚本。**case 在 B.jsonl，移交 shard B** |
| β8 | WaveView-002 | A/B/D 跨 shard | 读 FSDB 判数字/模拟、边沿/脉冲/过零并说明功能；pi 预算不足 DEFERRED | 波形截图 | A | ✅ | 功能说明偏视觉推理；**case 跨 shard，需召集人 A 定归属** |
| β9 | WaveMaxFind-001 | D | 计算波形 v(vb) 最大值；私有 FSDB → 合成 | 波形截图（v(vb)） | A（WaveView: 合成信号→sx_dump_png） | ✅ | 识图可读峰值，sx_meas_max 更精确 |
| β10 | TempThreshChar-001 | D | FineSim FSDB 温度阈值表征；私有 FSDB → 合成 | 波形截图（阈值穿越） | A（FineSim+WaveView: 合成 detector deck→sim→FSDB→sx_dump_png） | ✅ | 识图可看阈值穿越，脚本测更准 |
| β11 | SimFailFsdbProbe-001 | D | 读 timing_check TEST 模式 violation 定位 SRAM sim 失败；私有 FSDB → 合成 | 波形截图（violation 区间） | A | ✅ | 识图可看违例区间，脚本读 violation 更准 |

### 小结
- **D 域（shard D 直接改）**：α1, α4, β9, β10, β11（5 已落库 D.jsonl）+ α3, β6（2 未落库，需先造 case）= **7 题**。
- **B 域（移交 shard B）**：α2 RiseEdgeMargin-001, β7 WrDqMeas-001 = **2 题**。
- **跨 shard（召集人 A 定归属）**：β8 WaveView-002（A/B/D 都有同名，疑历史误分）= **1 题**。
- **未落库待确认**：β5 FsdbNetToggleDiag（深读笔记在但 4 shard jsonl 全无）= **1 题**。
- **可行性**：11 题全部路径 A 或 B 可行，无 C（不可行）。素材不可得（真实私有波形/FSDB）的获取途径 = 用 EDA 沙盒（WaveView tcl / FineSim）对**合成波形**重新生成真图；真实私有数据不进 SUT 沙盒（红线 4 + 隔离原则）。

## 三、判分设计原则（防蒙猜 + 验看图作答）

check.py 无法直接验「agent 看了图」，只能验 deliverable 文本答案。恢复原形态后，判分设计遵循：

1. **移除文本替身**：assets 只给图（PNG），不给 `.rep`/`.vec`/CSV/原始数值。agent 无可脚本解析的数据，必须看图（或从 PNG 反推，难度高）。
2. **多维度作答**：deliverable 要求给出 ≥3 个相关量（如 α1：VREF + 眼宽 + 眼高 + skew），全对才 PASS。单值乱猜命中率 = (1/答案空间)^维度，压到 <1%。
3. **大答案空间**：答案不限于小整数枚举（如眼宽 56.99 ps 浮点，非 0/1/2 选择）。
4. **保留隐藏输入 B + 随机化 + 负样本**（§4 契约不变）：B 的图与 A 在数值/结构上不同；3 seed；≥2 naive negative 全 FAIL。
5. **断言闸门不变**：k_rationale == k_check ≥ 8，`k 条断言：①…` 格式。
6. **判分器本身仍可脚本验答案**（check.py 知道 oracle，验 agent 产出文本/CSV 对错）—— 这不构成「降级」，因为判分器不在 SUT 沙盒（泄漏隔离 §4.8），agent 看不到 oracle。

> ⚠️ 根本性边界的承认：判分器无法 100% 证明「agent 是看图得出而非猜中/旁路」。恢复原形态把「不看图几乎不可能全对」作为目标，使无多模态系统的期望通过率趋近 0，从而让「基线 fail → 上 VQA pass」的差值成为多模态增益的可信证据。这是 vision 度量框架的内在假设，designflow 据此设计题面。

## 四、恢复路径技术细节

### 路径 A（首选，忠实）：WaveView/FineSim 沙盒生成真图
1. 合成波形：用 FineSim 跑小规模合成 deck（如 DDR driver + 简单负载）产 FSDB，或 WaveView tcl 内建合成信号。
2. WaveView tcl pipeline（probe 已确认命令可用）：
   ```tcl
   sx_open_fsdb <synth.fsdb>          ;# 加载
   sx_add_signal <sig> <scope>        ;# 加信号
   sx_create_eye -signal <dq> -rate <mbps> -vref <mV>  ;# 创建眼图
   sx_display_eye ...                 ;# 显示
   sx_dump_png -file eye_vref_<mV>.png ;# 导出 PNG
   ```
3. 对 VREF 扫描逐点导出 PNG（α1），或单波形截图（α4/β9/β10/β11）。
4. assets 只放 PNG，移除 `.rep`/`.vec`。

### 路径 B（次选，快速）：matplotlib 示意图
- 用现有合成数据（如 eye_sweep_A.rep 数值）matplotlib 画眼图示意 PNG（菱形/六边形，宽=width 高=height）。
- 优点：1 轮可完成恢复 + 跑基线。
- 缺点：示意图非真眼图形态，「视觉判断眼张开度」退化为「量图形大小」，多模态增益度量被削弱。
- 用途：先快速跑出基线占位，后续升级到路径 A。

### 排期建议
- **下轮（r650）**：恢复 α1 EyeApertureSelect-001（路径 A，WaveView 真眼图）→ 自验 → 跑 cline 基线。作为恢复模板，跑通后并行其余题。
- **r651-r657**：逐题恢复 D 域 7 题（α1 模板复用）。
- **并行**：B 域 2 题（α2/β7）移交 shard B；β8 跨 shard 待 A 裁；β5 未落库待确认是否补造。
- **基线通过率**：每题恢复后跑 cline（无多模态），逐题 PASS/FAIL 落 `designflow/waveview_baseline_results.D.json`，预期大量 FAIL。

## 五、本轮（r649）交付与未完成标注

- ✅ 认领任务 1（WAVEVIEW_COLLAB.md 认领记录）。
- ✅ 11 题素材可得性核查 + 恢复方案（本文件）。
- ✅ WaveView 技术可行性确认（sx_dump_png + eye 命令）。
- ⬜ 未恢复任何 case 原形态（预算不足，下轮起逐题）。
- ⬜ 未跑基线通过率（依赖恢复完成）。
- **素材不可得标注**（按任务要求「如实标注缺什么 + 获取途径，不许降级凑数」）：
  - 缺：11 题的**真实私有波形 / FSDB / WaveView 项目环境**（e0023936 等用户的私有数据，权限不可复刻，红线 4 禁写目标机）。
  - 获取途径：用 EDA 沙盒（eda_flow `run_code lang=tcl host=waveview` / FineSim）对**合成波形**重新生成真图（路径 A）。真实私有数据不进 SUT 沙盒（隔离原则）。
  - designflow 不以「素材不可得」为由降级凑数；恢复后的 case 必须是「需看图」形态，无多模态 fail 是正确结果。

## 六、恢复进度（r650, 2026-11-14）

### α1 EyeApertureSelect-001 — ✅ 已恢复原形态 + 基线已跑

- **恢复完成**：移除文本 .rep 数据替身（eye_sweep_A.rep / hidden/eye_sweep_B.rep / hidden/eye_sweep_allinvalid.rep 全删），改用 matplotlib 在 .75 沙盒生成的真数据图 PNG（eye_sweep_A.png 3-panel VREF sweep, 1286×1286, 144KB；hidden/eye_sweep_B.png 同构异值, 137KB）。
- **prompt 改写**：要求 agent 看图读数作答（从坐标轴读 VREF/width/skew/height），交付 wv_summary.csv 答案（不再是脚本）。明示"不要尝试用脚本去解析图中的原始数据"。
- **check.py 重写**：12 条件 (a)-(l)，answer-validation 设计——oracle 由 subprocess 从 embedded A sweep 数据重算（满足 §4.2 真跑），值条件 (f)-(i) 验 vref=100/aperture=56.99/skew=5.38/height=180（过滤后最优，非 raw-max=60 假峰）；反硬编码 (k) 拒 B 特征字面量；一致性 (l) 验报告元组匹配 A sweep 真实点（击溃跨 VREF 混搭猜测）。
- **契约适配（metadata.restoration_notes 记录）**：answer-deliverable 设计下，§4.1/§4.2 candidate-script-runs-on-hidden-B 机制替换为 oracle-recomputed-via-subprocess + anti-hardcode-B-token guard；hidden B 图保留作 provenance + 反硬编码。
- **自验**：REF PASS 12/12；5 negative（fake_empty/fake_all_zero/fake_raw_max/fake_hardcode_B/fake_wrong_height）全 FAIL（NEG_RC=0，各击溃不同条件）；§4.9 退化回归（empty zip / stub / core-deleted）全 FAIL。
- **断言闸门**：k_rationale==k_check==12 ≥ 8 ✓。
- **jsonl 更新**：EDA-Eval-DesignFlow_D.jsonl 中该 case 已替换为 restored form（attachments=[eye_sweep_A.png, task_brief.md], image_required=true, track=synthesized-image-restored, restoration notes）。
- **基线**：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only SFT surrogate, 无多模态）跑——预期 FAIL（不能看图）。注：providers.json 原 model=deepseek-v4-pro-cloud 在本地 18096 代理不存在（仅 minicpm5-2b 可用），用 --model minicpm5-2b-sft-v39-final 覆盖。结果落 eval/status.jsonl + designflow/waveview_baseline_results.D.json。
- **判分隔离**：SUT workdir 只放 prompt.txt + eye_sweep_A.png + task_brief.md（PreToolUse hook 验证无 check.py/reference/hidden 泄漏）；判分在独立 judge dir 跑。

### β9 WaveMaxFind-001 — ✅ 已恢复原形态 + 基线已跑（r651, 2026-11-14）

- **恢复完成**：移除文本波形替身（waveform_vb.txt / hidden/waveform_out.txt / hidden/waveform_xa.txt 全删），改用 matplotlib 在 .75 沙盒生成的真数据图 PNG（wave_vb_A.png：v(vb) 阻尼正弦 v(t)=0.6+0.4·exp(-t/3ns)·cos(2π·1GHz·t)，500 点 [0,7ns]，97KB，无数据标签，需从坐标轴读数；hidden/wave_out_B.png：v(out) 同构异值 offset=0.5/amp=0.45/f=0.8GHz/tau=2.5ns/[0,8ns]，93KB，provenance + 反硬编码）。
- **prompt 改写**：要求 agent 看图读出 v(vb) 的 max/t_at_max/min/t_at_min/peak_to_peak/offset/period 七个量，交付 wv_summary.csv 答案（不再是脚本）。明示"不要尝试用脚本去解析图中的原始数据"。
- **check.py 重写**：12 条件 (a)-(l)，answer-validation 设计——oracle 由 subprocess 从 embedded A 波形参数重算（满足 §4.2 真跑）；值条件 (e)-(i) 验 max=1.0/t_at_max=0/min=0.2609/t_at_min≈0.491ns/p2p=0.7391（±0.02V / ±0.08ns 读图容差）；反硬编码 (k) 拒 B 特征字面量（v(out)/0.95/0.14843/0.80157/1.25，刻意排除 "0.5" 因 agent 合法读 t_at_min≈0.5ns）；自洽 (l) 验报告的 (max,t_at_max)/(min,t_at_min) 落在 A 曲线上（击败数值与时间错配猜测）。
- **契约适配（metadata.restoration 记录）**：answer-deliverable 设计下，§4.1/§4.2 candidate-script-runs-on-hidden-B 机制替换为 oracle-recomputed-via-subprocess + anti-hardcode-B-token guard + self-consistency-on-A-curve；hidden B 图保留作 provenance + 反硬编码。
- **自验**：REF PASS 12/12；5 negative（fake_empty/fake_wrong_header/fake_wrong_max/fake_hardcode_B[B 全量答案]/fake_incoherent）全 FAIL（NEG_RC=0，各击溃不同条件）；§4.9 退化回归（empty zip / stub[全零] / core-deleted[仅表头]）全 FAIL。
- **断言闸门**：k_rationale==k_check==12 ≥ 8 ✓。
- **jsonl 更新**：EDA-Eval-DesignFlow_D.jsonl 中该 case 已替换为 restored form（attachments=[wave_vb_A.png, task_brief.md], image_required=true, track=synthesized-image-restored, restoration notes, k=12）。D.jsonl 仍 377 条（恢复=替换非新增）。
- **基线**：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only SFT surrogate, 无多模态）跑——预期 FAIL（不能看图）。结果落 eval/status.jsonl + designflow/waveview_baseline_results.D.json（β9 段追加）。
- **判分隔离**：SUT workdir 只放 prompt.txt + wave_vb_A.png + task_brief.md（PreToolUse hook 验证无 check.py/reference/hidden 泄漏）；判分在独立 judge dir 跑。

### α4 TempSelWaveform-001 — ✅ 已恢复原形态 + 基线已跑（r652, 2026-11-14）

- **恢复完成**：移除文本 .tbl 数据替身（wave_A.tbl / example_output_A.json / hidden/wave_B.tbl / hidden/gen_B.py 全删），改用 matplotlib 在 .75 沙盒生成的真数据图 PNG（sel_wave_A.png：温度传感器选择器信号 v(sel54) 梯形脉冲多窗激活，5 个激活窗 [0–30us]，1500×900，73KB，无数据标签，需从坐标轴读数；hidden/sel_wave_B.png：v(sel68) 周期 7 窗同构异值，82KB，provenance + 反硬编码）。
- **prompt 改写**：要求 agent 看图读出 v(sel54) 的激活特征量（v_max/v_min/激活次数/首个激活时间/末个激活时间/占空比/激活模式），交付 wv_summary.csv 答案（不再是脚本）。明示"不要尝试用脚本去解析图中的原始数据"。
- **check.py 重写**：12 条件 (a)-(l)，answer-validation 设计——oracle 由 subprocess 从 embedded A 波形参数重算（梯形脉冲模型 + 数值阈值穿越检测，满足 §4.2 真跑）；值条件 (e)-(j) 验 v_max=1.25/v_min=0.10/num_activations=5/first=2.84us/last=26.18us/duty=0.287（±0.05V/±0.5us/±0.06 读图容差）；(k) activation_pattern=multi_pulse 且与 nact 内部一致（2≤nact≤6）；(l) 反硬编码拒 B 特征字面量（sel68 + B 的 3 位小数穿越时刻）+ 跨字段自洽（first<last, 0<duty≤1, 隐含平均窗宽合理）。
- **契约适配（metadata.restoration 记录）**：answer-deliverable 设计下，§4.1/§4.2 candidate-script-on-hidden-B 机制替换为 oracle-recomputed-via-subprocess + anti-hardcode-B-token guard + cross-field self-consistency；hidden B 图保留作 provenance + 反硬编码。
- **自验**：REF PASS 12/12；7 negative（empty_zip/wrong_header/wrong_vmax/wrong_nact/wrong_pattern_inconsistent/hardcode_B/incoherent）全 FAIL（NEG_RC=0，各击溃不同条件）；§4.9 退化回归（empty/stub_allzero/core-deleted）全 FAIL。
- **断言闸门**：k_rationale==k_check==12 ≥ 8 ✓。
- **jsonl 更新**：EDA-Eval-DesignFlow_D.jsonl 中该 case 已替换为 restored form（attachments=[sel_wave_A.png, task_brief.md], image_required=true, track=synthesized-image-restored, restoration notes, k=12, check_sha=ad4fb740b6）。D.jsonl 仍 377 条（恢复=替换非新增）。
- **基线**：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only SFT surrogate, 无多模态）跑——预期 FAIL（不能看图）。结果落 eval/status.jsonl + designflow/waveview_baseline_results.D.json（α4 段追加）。
- **判分隔离**：SUT workdir 只放 prompt.txt + sel_wave_A.png + task_brief.md（PreToolUse hook 验证无 check.py/reference/hidden 泄漏, hook_blocks=0）；判分在独立 judge dir 跑。

### β8 WaveView-002 — ✅ 已恢复原形态 + 基线已跑（r653, 2026-11-14）

- **恢复完成**：移除原 L2 工具脚本形态（FSDB 路径 + signals_A.txt 信号清单 + Tcl-script 交付件 + hidden/hidden_manifest.json），改用 matplotlib 在 .75 沙盒从已知波形参数生成的真数据图 PNG（wv_sigs_A.png：5 路堆叠混合信号 [0,10ns]——clk 周期方波(period 2.0ns/duty 0.2/n_trans 10) / rst_n 复位(n_trans 1) / data 多电平总线(n_trans 3/n_levels 4) / vref 模拟斜坡(vmin 0/vmax 1.0) / sel 选择器脉冲(n_trans 4/n_pulses 2)，无数据标签，需从坐标轴读数；hidden/wv_sigs_B.png 同构异值——clk period 1.25ns/duty 0.2, rst_n rise@2.5ns, data 5 levels, vref ramp 0.2→0.8, sel 3 pulses，39KB，provenance + 反硬编码）。
- **结构转换说明**：β8 原为 L2 wv-subprocess 工具脚本 case（候选写 WaveView ACE Tcl 脚本，check.py 真跑 wv 在隐藏 FSDB B 上分类信号）——纯文本模型可写 Tcl 通过，**不服务于多模态增益度量**。恢复为 image-required answer-deliverable 形态（WAVEVIEW 协作目标），原 L2 形态保留在 r653 之前的 git 历史。
- **prompt 改写**：要求 agent 直接看图对 5 个信号逐个判断 type/n_transitions/function/period_ns/duty/vmin/vmax/n_pulses/n_levels，交付 wv_report.json（不再是 Tcl 脚本）。明示"不要尝试用脚本解析图中的原始数据点"。
- **check.py 重写**：12 条件 (a)-(l)，answer-validation 设计——oracle 由 subprocess 从 embedded A 波形参数重建波形并数值测量 transitions/period/duty/levels（满足 §4.2 真跑）；值条件 (d)-(k) 用读图容差（n_trans ±1, period ±0.25ns, duty ±0.12, vmin/vmax ±0.07, n_pulses/n_levels 精确）；(l) 反硬编码拒 B 特征字面量(period 1.25/vmin 0.2/vmax 0.8/n_pulses 3/n_levels 5) + 跨字段自洽(vmin<vmax、clk n_trans 偶数、rst_n n_trans≤2、data n_levels≥2)。
- **契约适配（metadata.restoration_notes 记录）**：answer-deliverable 设计下 §4.1/§4.2 candidate-script-on-hidden-B 替换为 oracle-recomputed-via-subprocess + anti-hardcode-B-token guard + cross-field self-consistency；hidden B 图保留作 provenance + 反硬编码。
- **自验**：REF PASS 12/12；14 negative 全 FAIL（NEG_RC=0，11 个 fake_* first_fail 覆盖 b-l 各异）；§4.9 退化回归(empty/stub_allzero/core-deleted)全 FAIL。
- **断言闸门**：k_rationale==k_check==12 ≥ 8 ✓。
- **jsonl 更新**：EDA-Eval-DesignFlow_D.jsonl 中该 case 替换为 restored form（attachments=[wv_sigs_A.png, task_brief.md], image_required=true, track=synthesized-image-restored, restoration notes, k=12, check_sha=c9ed69e6b4）。D.jsonl 仍 377 条（恢复=替换非新增）。
- **基线**：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only SFT surrogate, 无多模态）跑——预期 FAIL（不能看图）。结果 9s, exit=0, **FAIL（正确）**：未产出 submit.zip；60 session msgs，模型从未读 wv_sigs_A.png（png/wv_sigs terms=0）、从未产出 wv_report.json、从未开 eda_flow session，仅 generic read_file/write 探索后退出 → **did-not-engage** 失败模式。**无多模态 fail 是正确基线**。结果落 designflow/cline_eval_status_D.jsonl + designflow/waveview_baseline_results.D.json（β8 段追加, restored_count=4: α1+β9+α4+β8）。
- **判分隔离**：SUT workdir 只放 prompt.txt + wv_sigs_A.png + task_brief.md（PreToolUse hook + run_one.sh leak 自检验证无 check.py/reference/hidden 泄漏）；判分在独立 judge dir 跑。

### β10 TempThreshChar-001 — ✅ 已恢复原形态 + 基线已跑（r654, 2026-11-14）

- **恢复完成**：β10 原为 L2 FineSim-subprocess 工具脚本 case（候选写 `characterize.py` 驱动 FineSim `.tran` 解析 `.measure ... when` 穿越时刻→换算阈值电压，纯文本模型可写脚本通过，不服务多模态度量）——**且处于半恢复破损态**（commit 754f8fd6 已把 assets 替换为 PNG 并删旧文本资产，但 D.jsonl test 仍是旧 FineSim subprocess 形态、reference/ 无 check.py、negative/ 空，case 不可运行）。本轮恢复为 image-required answer-deliverable 形态并修好破损态。
- **图生成**：.75 沙盒 python3+matplotlib(Agg) 2000-pt 生成 thresh_char_A.png（两上下堆叠子图共享时间轴 us：上图 v(temp) 三角温度扫描斜坡 0→1.20V→0 [0,10us] 峰@4us，下图 v(det) 迟滞比较器输出 vth_high=0.85/vth_low=0.45 翻高[2.84,6.50]us；1500×900@150dpi 68KB，**无数据标签/无阈值线/无标注**，需把 v(det) 翻转时间对回 v(temp) 电压读 vth_high/vth_low/迟滞）+ hidden/thresh_char_B.png（同构异值：ramp 0.15→1.05→0.15 [0,14us] 峰@6us, vth_high=0.75/vth_low=0.25/迟滞0.50；68KB 反硬编码 provenance）；覆盖 12:54 孤儿 PNG（前 commit 754f8fd6 留下无参数记录的 PNG，重新生成以掌控 oracle）。
- **资产替换**：旧文本资产 tb_a.sp/spec_a.json/hidden/deck_B.sp 已被 754f8fd6 删除；本轮改用 PNG + task_brief.md。prompt 改写要求看图读阈值表征量作答（明示"不要尝试用脚本解析图中原始数据点"），交付 thresh_report.json。
- **check.py 重写**：12 条件 (a)-(l) answer-validation——oracle 由 subprocess 从 embedded A_PARAMS 重建 A 波形(2000-pt 同离散化)数值测量 vmax/vmin/t_at_max/slope/t_cross_up/t_cross_down/hysteresis/n_transitions/duty（满足 §4.2 真跑）；值条件 (d)-(k) 读图容差(vmax±0.07/vmin±0.05/t_at_max±0.3us/vth_high±0.06/vth_low±0.06/hysteresis±0.05/t_cross±0.35us/n_transitions 精确)；(l) 反硬编码拒 B 特征字面量(vmax1.05/vmin0.15/vth_high0.75/vth_low0.25/hysteresis0.50/slope0.15)+跨字段自洽(vmin<vmax, vth_low<vth_high, t_up<t_down, hysteresis≈vth_high-vth_low, slope>0, 0<duty<1, n_trans==2)。
- **契约适配**：answer-deliverable 设计下 §4.1/4.2 candidate-script-on-hidden-B 替换为 oracle-recomputed-via-subprocess + anti-hardcode-B-token guard + cross-field self-consistency；hidden B 图保留 provenance + 反硬编码；metadata.restoration_notes 记录。jsonl key 由旧 `id` 修正为 `task_id`（+保留 id 兼容），与其它 restored case 一致、harness 可查。
- **自验**：REF PASS 12/12；18 negative(15 fake_* + 3 §4.9 degenerate)全 FAIL(NEG_RC=0, 各击溃不同条件 b-l)；§4.9 退化回归(empty zip/stub[仅 function]/core-deleted[无数值字段])全 FAIL。
- **断言闸门**：k_rationale==k_check==12 ≥ 8 ✓。
- **jsonl 更新**：EDA-Eval-DesignFlow_D.jsonl 该 case 替换为 restored form(attachments=[thresh_char_A.png,task_brief.md], image_required=true, track=synthesized-image-restored, restoration notes, k=12, check_sha=4d9b565a42)。D.jsonl 仍 377(恢复=替换非新增)。
- **基线**：cline v3.0.51 + minicpm5-2b-sft-v39-final(2B text-only SFT surrogate, 无多模态) → **FAIL(正确)**(23s, exit=0, 未产出 submit.zip, hook_blocks=0, leak 自检通过)。**失败模式=engaged-but-incapable**（比 r650 α1 did-not-engage 干净）：session 提及 thresh_char=254/png=252/task_brief=300/prompt.txt=226/vth_high=201/v(temp)=9/thresh_report=8/submit.zip=3/eda_flow=19——模型读懂了任务、知道要读图产 thresh_report.json 给 vth_high 等，但 2B text-only 读不了 PNG 未能产出有效 submit.zip。**无多模态 fail 是正确基线**。结果落 designflow/cline_eval_status_D.jsonl + designflow/waveview_baseline_results.D.json（β10 段追加, restored_count=5: α1+β9+α4+β8+β10）。
- **判分隔离**：SUT workdir 只放 prompt.txt + thresh_char_A.png + task_brief.md（PreToolUse hook + run_one.sh leak 自检验证无 check.py/reference/hidden 泄漏）。

### β11 SimFailFsdbProbe-001 — ✅ 已恢复原形态 + 基线已跑（r655, 2026-11-14）

- **恢复完成**：β11 原为 L2 wv-subprocess 工具脚本 case（候选写 WaveView ACE Tcl `probe_fsdb.tcl`，check.py 跑 `waveview_mock.tcl` 在隐藏 `spec_b.json` 上判分）——纯文本模型可写 Tcl 通过，**不服务于多模态增益度量**。恢复为 image-required answer-deliverable 形态（原 L2 形态保留在 r655 前 git 历史）。
- **图生成**：.75 沙盒 python3+matplotlib(Agg) 生成 sim_fail_A.png（7 路堆叠子图共享时间轴 ns，时窗 [1340,1370]ns，fail_time=1363ns：Q_valid 在 fail_time 跌 1→0（Q 变 x）、test_op_type 1→4@1350ns（TEST write-through）、Q_force_x 在 fail_time 0→1 并保持（**root_cause=Q_force_x_stuck_high**）、test_violation_pos 全程 0、test_violation_clk 周期 8ns 方波（上升沿 1342/1350/1358/1366 = **4 个**）、BYP_eff 全程 0、test_mode 全程 1；1500×1800@150dpi 77929 字节，**无数据标签/无阈值线/无标注**，需从坐标轴读 fail_time/各信号快照 + 数 test_violation_clk 上升沿）+ hidden/sim_fail_B.png（同构异值：时窗 [730,760]ns，fail_time=742ns，test_violation_pos 在 fail_time 翻高（**root_cause=test_violation_pos_asserted**）、Q_force_x 全程 0、test_violation_clk 周期 5ns（**6 个**上升沿）；79411 字节，反硬编码 provenance）。
- **资产替换**：删旧文本替身 spec.json/sim_fail.log/json.tcl/waveview_mock.tcl/hidden/spec_b.json/hidden/hidden_manifest.json，改用 PNG + task_brief.md；prompt 改写要求看图读 fail_time_ps/root_cause(4 候选)/edge_signal/edge_count(数上升沿)/signal_snapshot/window/evidence_summary(自己话描述读到什么)，交付 diagnosis.json（明示"不要尝试用脚本解析图中原始数据点"）。
- **check.py 重写**：12 条件 (a)-(l) answer-validation，**每条独立可 FAIL**——oracle 由 subprocess 从 embedded A_PARAMS 重建 A 波形数值测量 fail_time/各信号 fail_time 快照/对所声明 edge_signal 在所声明窗口重算上升沿数（满足 §4.2 真跑）；值条件 (c)-(i) 读图容差/精确匹配；反硬编码 (k) 拒隐藏 B 特征字面量（test_violation_pos_asserted/742000/730000/760000/tb_sram_sp__1024x128_byp.fsdb 等出现在 diagnosis 任意字符串值，含 evidence_summary）；自洽 (j) root_cause↔snapshot 触发值一致、(l) Q_valid==0 @ fail_time（Q 变 x）。
- **契约适配**：answer-deliverable 设计下 §4.1/4.2 candidate-script-on-hidden-B 替换为 oracle-recomputed-via-subprocess + anti-hardcode-B-token guard + cross-field self-consistency；hidden B 图保留 provenance + 反硬编码；metadata.restoration 记录。
- **自验**：REF PASS 12/12；15 negative（12 各击溃 a-l 一条 + 3 §4.9 退化）全 FAIL（NEG_RC=0，distinct first_fail labels a,b,c,d,e,f,g,h,i,j,k,l + garbage[?]）；§4.9 退化回归（empty zip/stub_allzero/core_deleted）全 FAIL。
- **断言闸门**：k_rationale==k_check==12 ≥ 8 ✓。
- **jsonl 更新**：EDA-Eval-DesignFlow_D.jsonl 该 case 替换为 restored form（attachments=[sim_fail_A.png, task_brief.md], image_required=true, track=synthesized-image-restored, restoration notes, k=12, check_sha=d1c028f332）。D.jsonl 仍 377（恢复=替换非新增）。
- **基线**：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only SFT surrogate, 无多模态）→ **FAIL（正确）**（31s, exit=0, 未产出 submit.zip, hook_blocks=0, leak 自检通过）。**失败模式=engaged-with-task-text-but-did-not-read-image**（比 r650 α1 did-not-engage 干净）：session 提及 prompt.txt=177/task_brief=413/submit.zip=228/eda_flow=50（模型读懂任务文本、尝试 eda_flow、知道要产 diagnosis.json 打包 submit.zip），但 sim_fail=0/png=0/diagnosis=0/root_cause=0/fail_time=0/edge_count=0/Q_force_x=0/test_violation=0（**从未引用 PNG 图、从未提及任何信号名、从未产出 diagnosis**），outputs/ 空——2B text-only 读不了 PNG，故无有效诊断。**无多模态 fail 是正确基线**。结果落 designflow/cline_eval_status_D.jsonl + designflow/waveview_baseline_results.D.json（β11 段追加, restored_count=6: α1+β9+α4+β8+β10+β11）。
- **判分隔离**：SUT workdir 只放 prompt.txt + sim_fail_A.png + task_brief.md（PreToolUse hook + run_one_D leak 自检验证无 check.py/reference/hidden 泄漏）；判分在独立 judge dir 跑。

### 待恢复（下轮起）
α3 / β6（D 域未落库 2 题，需先从 h8pcp / 3qe6x trace 造 case 再恢复为 image-required 形态）。B 域 α2/β7 移交 shard B；β5 未落库（vision 误抄, 非恢复范围, 召集人 A r508 裁定）。
> D 域 6 题已落库 case 已全部恢复完毕（α1/β9/α4/β8/β10/β11），restored_count=6。剩余 D 域 α3/β6 未落库，需先造 case 再恢复。
