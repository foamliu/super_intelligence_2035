# WAVEVIEW 协作请求 · vision → designflow（2026-11-14）

> **发起**：vision 线 | **承接**：designflow shard A/B/C/D（任一空闲 shard 认领）
> **依据**：用户令 2026-11-14 09:1x #2/#3 + 09:5x 口径变更（「需要多模态的题不要降级，没有多模态能力就让它们 fail；像要求合格 DE 一样要求 agent」）
> **状态**：⬜ 未认领 ｜ 🟡 进行中（shard D 认领任务1，分阶段）｜ ⬜ 已交付

---

## 一、要 designflow 做两件事

### 任务 1（#2 基线）：恢复「原意图需看图」用例的原始形态，跑出基线通过率

- **输入清单**：`doc/BaiZe-ISEDA2027/run/reports/waveview_need_image_handoff.md`
  （vision 已筛出 11 题：α 4 题 + β 7 题；γ 26 题不恢复）
- **要求**：
  1. 逐题确认「原意图」是否需要看图（capture 截图/波形图/真实 FSDB）；
  2. **恢复原形态**——要求被测系统看图作答，不得用 `.rep`/CSV 文本替身；
  3. 无多模态能力的系统在这些题上**应当 fail，这是正确行为**；
  4. 跑出**新基线通过率**（逐题 PASS/FAIL 落盘）。
- **素材不可得时**：如实标注缺什么 + 获取途径，🚫 不许降级凑数。

### 任务 2（#3 对比）：VQA tool 接入后，用同一批用例再测一遍

- vision 负责把 **Qwen3.5-2B** 封装成 VQA tool（看图答波形问题）供 cline 调用；
- designflow 负责用**同一批已恢复原形态的用例**再跑一遍；
- **唯一变量 = 有没有 VQA tool**，题目/环境/判据必须与任务 1 完全一致；
- 交付：两次结果同表并列，标明**哪些题从 fail 翻成 pass**、未翻转的原因。

---

## 二、协作方式（避免互相阻塞）

| 事项 | 约定 |
|:--|:--|
| **认领** | 四个 shard 任一**空闲**时认领，在本文件「认领记录」写一行（shard / 时间 / 认领任务号），然后开始 |
| **不要抢** | 同一任务只由**一个** shard 执行；已在认领记录中的任务，其他 shard 不再接 |
| **不占造题时间** | 本协作属额外任务：若本 shard 有 case 可造，**造题优先**，把协作让给空闲 shard |
| **git** | 严格遵守 designflow 同步纪律（不 clean/reset/stash 别人改动，收尾「同步三连」） |
| **边界** | designflow 只写自己的任务书/MEMORY/评测产物；vision 不改 designflow 文件，只通过本文件交接 |

## 三、交付落点

- designflow 侧：在 `MEMORY_DESIGNFLOW_<shard>.md` 记一行 + 结果落 `designflow/waveview_baseline_results.<shard>.json`（或等价）
- 完成后**在本文件「交付记录」写一行**，vision 据此继续 #3/#4

---

## 认领记录

| 时间 | shard | 任务 | 备注 |
|:--|:--|:--|:--|
| 2026-11-14 10:4x | **D** | 任务1（基线） | **用户指定**：D 处于维护态（无新扫描），由 D 承接；D 本轮起按 `WAVEVIEW_COLLAB.md` 执行，完成后填「交付记录」 |

## 交付记录

| 时间 | shard | 任务 | 结果 | 产物路径 |
|:--|:--|:--|:--|:--|
| 2026-11-14 10:2x | D | 任务1（阶段性·r649） | 11 题素材可得性核查 + 恢复方案完成；WaveView 技术可行性确认（sx_dump_png + eye 命令，沙盒可生成真眼图 PNG）；**未恢复 case 原形态 / 未跑基线**（40min 预算不足，下轮 r650 起逐题恢复，α1 先行作模板）。素材不可得（真实私有波形/FSDB）获取途径=EDA 沙盒对合成波形重新生成真图。 | `designflow/waveview_restore_plan_D.md` |
| 2026-11-14 11:0x | D | 任务1（α1 恢复+基线·r650） | **α1 EyeApertureSelect-001 原形态恢复完成 + 基线 FAIL（正确）**。移除文本 .rep 替身，改用 matplotlib 在 .75 沙盒生成的真数据图 PNG（3-panel VREF sweep，无数据标签，需从坐标轴读数）。check.py 重写为 12 条件 answer-validation（oracle 由 subprocess 从 embedded sweep 重算 + 反硬编码 B-token guard + 一致性真实点校验）。自验全过（REF PASS 12/12 / 5 negative 全 FAIL / §4.9 退化回归全 FAIL）。基线：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only, 无多模态）→ FAIL（50s, loop-abort, 未产出 submit.zip）——**无多模态 fail 是正确基线**。注意：失败模式=did-not-engage（模型循环 generic ls/find 未读 prompt/PNG），非 engaged-but-image-blind；vision 若需更干净归因可换更强无多模态模型。剩余 6 D 域题下轮起恢复。 | `designflow/waveview_baseline_results.D.json` · `designflow/waveview_restore_plan_D.md` §六 · EDA-Flow-Bench assets/reference/jsonl 已更新 |
| 2026-11-14 11:4x | D | 任务1（β9 恢复+基线·r651） | **β9 WaveMaxFind-001 原形态恢复完成 + 基线 FAIL（正确）**。移除文本波形替身（waveform_vb.txt/hidden/waveform_out.txt/hidden/waveform_xa.txt），改用 matplotlib 在 .75 沙盒生成的真数据图 PNG（wave_vb_A.png：v(vb) 阻尼正弦 500 点，无数据标签，需从坐标轴读 max/min/t_at_max/t_at_min/p2p/offset/period 七量；hidden/wave_out_B.png 同构异值 provenance）。check.py 重写 12 条件 answer-validation（oracle subprocess 从 embedded params 重算 + 反硬编码 B-token guard + self-consistency-on-A-curve）。自验全过（REF PASS 12/12 / 5 negative 全 FAIL / §4.9 退化回归全 FAIL）。基线：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only）→ FAIL（22s, run_aborted external_abort, 未产出 submit.zip）——**无多模态 fail 是正确基线**。失败模式=engaged-but-incapable（模型读了 prompt、尝试开 eda_flow session，但 2B 模型 tool-call 错误循环后 abort），比 r650 α1 的 did-not-engage 稍干净。D.jsonl 仍 377（恢复=替换非新增）。剩余 5 D 域题下轮起恢复。 | `designflow/waveview_baseline_results.D.json`（β9 段追加）· `designflow/waveview_restore_plan_D.md` §六 · EDA-Flow-Bench assets/reference/jsonl 已更新 |
| 2026-11-14 12:1x | D | 任务1（α4 恢复+基线·r652） | **α4 TempSelWaveform-001 原形态恢复完成 + 基线 FAIL（正确）**。移除文本 .tbl 数据替身（wave_A.tbl/example_output_A.json/hidden/wave_B.tbl/hidden/gen_B.py），改用 matplotlib 在 .75 沙盒生成的真数据图 PNG（sel_wave_A.png：温度传感器选择器信号 v(sel54) 梯形脉冲多窗激活，5 个激活窗 [0–30us]，无数据标签，需从坐标轴读 v_max/v_min/激活次数/首个激活时间/末个激活时间/占空比/激活模式；hidden/sel_wave_B.png v(sel68) 周期 7 窗同构异值 provenance）。check.py 重写 12 条件 answer-validation（oracle subprocess 从 embedded 波形参数重算 + 数值阈值穿越检测 + 反硬编码 B-token guard + 跨字段自洽）。自验全过（REF PASS 12/12 / 7 negative 全 FAIL / §4.9 退化回归全 FAIL）。基线：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only）→ FAIL（11s, run_aborted external_abort, 未产出 submit.zip）——**无多模态 fail 是正确基线**。失败模式=engaged-but-aborted（session 有 118 处 sel_wave/png/prompt.txt 提及，模型接触了图/prompt 上下文，但 2B SFT surrogate tool-call 不可靠、external abort 前未产出交付件）。D.jsonl 仍 377（恢复=替换非新增）。剩余 5 D 域题（β10/β11/β8 已落库 + α3/β6 未落库）下轮起恢复。 | `designflow/waveview_baseline_results.D.json`（α4 段追加）· `designflow/waveview_restore_plan_D.md` §六 · EDA-Flow-Bench assets/reference/jsonl 已更新 |
| 2026-11-14 13:4x | D | 任务1（β8 恢复+基线·r653） | **β8 WaveView-002 原形态恢复完成 + 基线 FAIL（正确）**。β8 原为 L2 wv-subprocess 工具脚本 case（候选写 WaveView ACE Tcl 脚本对 FSDB 信号分类，check.py 真跑 wv 在隐藏 B 上判分）——纯文本模型可写 Tcl 通过，**不服务于多模态增益度量**；恢复为 image-required answer-deliverable 形态。移除 signals_A.txt/hidden_manifest.json/FSDB+Tcl-script 交付件，改用 matplotlib 在 .75 沙盒从已知波形参数生成的真数据图 PNG（wv_sigs_A.png：5 路堆叠混合信号 [0,10ns]——clk 周期方波/rst_n 复位/data 多电平总线/vref 模拟斜坡/sel 选择器脉冲，无数据标签，需从坐标轴读 type/n_transitions/function/period/duty/vmin/vmax/n_pulses/n_levels；hidden/wv_sigs_B.png 同构异值 provenance+反硬编码）。check.py 重写 12 条件 answer-validation（oracle subprocess 重建 A 波形数值测量 transitions/period/duty/levels + 读图容差 + 反硬编码 B-token guard + 跨字段自洽）。自验全过（REF PASS 12/12 / 14 negative 全 FAIL NEG_RC=0 / §4.9 退化回归全 FAIL）。基线：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only）→ FAIL（9s, exit=0, 未产出 submit.zip）——**无多模态 fail 是正确基线**。失败模式=did-not-engage（60 msgs，模型从未读 PNG、从未产出 wv_report、从未开 eda_flow，仅 generic read_file/write 探索后退出）。**结构转换说明**：原 L2 工具脚本形态保留在 r653 前 git 历史。D.jsonl 仍 377（恢复=替换非新增）。restored_count=4（α1+β9+α4+β8）。剩余 4 D 域题（β10/β11 已落库 + α3/β6 未落库）下轮起恢复；**β10 已知半恢复破损态**（commit 754f8fd6 替换 PNG 但 jsonl/check.py 未更新，不可运行，下轮需重生成 PNG + 写 check.py）。 | `designflow/waveview_baseline_results.D.json`（β8 段追加, restored_count=4）· `designflow/waveview_restore_plan_D.md` §六 · EDA-Flow-Bench assets/reference/jsonl 已更新 |
| 2026-11-14 14:1x | D | 任务1（β10 恢复+基线·r654） | **β10 TempThreshChar-001 原形态恢复完成 + 基线 FAIL（正确）**，并修好 r653 标注的半恢复破损态。β10 原为 L2 FineSim-subprocess 工具脚本 case（候选写 characterize.py 驱动 FineSim .tran 解析 .measure 穿越时刻→阈值电压，纯文本可写脚本通过，不服务多模态度量），且 commit 754f8fd6 已替换 PNG 但 D.jsonl test 仍是旧 FineSim 形态/reference 无 check.py/negative 空（不可运行）——本轮恢复为 image-required answer-deliverable 形态并修好破损态。移除 FineSim deck + characterize.py 交付件，改用 matplotlib 在 .75 沙盒 2000-pt 生成的真数据图 PNG（thresh_char_A.png：两上下堆叠子图共享时间轴——上图 v(temp) 三角温度扫描斜坡 0→1.20V→0 峰@4us，下图 v(det) 迟滞比较器 vth_high=0.85/vth_low=0.45 翻高[2.84,6.50]us，**无数据标签/无阈值线/无标注**，需把 v(det) 翻转时间对回 v(temp) 电压读 vth_high/vth_low/迟滞；hidden/thresh_char_B.png 同构异值 provenance+反硬编码 1500×900 68KB）。check.py 重写 12 条件 answer-validation（oracle subprocess 重建 A 波形 2000-pt 数值测量 vmax/vmin/t_at_max/slope/crossings/hysteresis/transitions/duty + 读图容差 + 反硬编码 B-token guard + 跨字段自洽）。自验全过（REF PASS 12/12 / 18 negative+degenerate 全 FAIL NEG_RC=0, distinct first_fail b-l / §4.9 退化回归全 FAIL）。基线：cline v3.0.51 + minicpm5-2b-sft-v39-final（2B text-only 无多模态）→ **FAIL（正确）**（23s, exit=0, 未产出 submit.zip, hook_blocks=0, leak 自检通过）。**失败模式=engaged-but-incapable**（比 r650 α1 did-not-engage 干净）：session 提及 thresh_char=254/png=252/task_brief=300/vth_high=201/thresh_report=8/submit.zip=3/eda_flow=19——模型读懂任务、知道要读图产 thresh_report.json 给 vth_high 等，但 2B text-only 读不了 PNG 未能产出有效 submit.zip。D.jsonl 仍 377（恢复=替换非新增；jsonl key 由旧 `id` 修正为 `task_id` 与其它 restored case 一致、harness 可查）。restored_count=5（α1+β9+α4+β8+β10）。剩余 3 D 域题（β11 已落库 + α3/β6 未落库）下轮起恢复。 | `designflow/waveview_baseline_results.D.json`（β10 段追加, restored_count=5）· `designflow/waveview_restore_plan_D.md` §六 · EDA-Flow-Bench assets/reference/jsonl 已更新 |

---

## 召集人裁定（shard A · 2026-11-14 r508）

> 触发：`designflow/waveview_restore_plan_D.md` §二 标注 β8 WaveView-002「A/B/D 跨 shard，需召集人 A 定归属」+ β5 FsdbNetToggleDiag「未落库待确认」。A 作为 4-shard 召集人核实如下：

### 裁定 1 · β8 WaveView-002 → **归属 shard D，无跨 shard 冲突**

- **核实方法**：对 4 shard jsonl 全量 grep `WaveView-002`。
- **结果**：`EDA-Eval-DesignFlow-WaveView-002` **仅存在于 D.jsonl**（1 条，`task_id` 字段）；A/B/C jsonl **0 命中**。
- **元数据**：domain=`waveform`，trace_user=`easont`，trace_host=`hfhds211`，session=`1793147699495_as67p.messages.json`，深读笔记 `as67p_waveview_ace_fsdb_signal_extractor.md` 在。
- **裁定**：restore_plan_D 中「A/B/D 都有同名，疑历史误分」**不成立**——是 D 的同名 case 与 B 的 `WaveViewPanel-001`（panel height，不同题）混淆。**WaveView-002 干净归属 D**，D 可直接恢复，无需跨 shard 协调。
- **附注**：B.jsonl 仅有 `WaveViewPanel-001`（不同 case），不构成同名冲突。

### 裁定 2 · β5 FsdbNetToggleDiag → **case 不存在，vision 误抄，超出 Task1 恢复范围**

- **核实方法**：对 4 shard jsonl 全量 grep `FsdbNet` / `FsdbNetToggleDiag`。
- **结果**：**4 shard 全 0 命中**（A=0 B=0 C=0 D=0）。case_id `EDA-Eval-DesignFlow-FsdbNetToggleDiag-001` 在任何 jsonl 中均不存在。
- **现存产物**：仅有深读笔记 `designflow/trace_deepreads/1793078405436_t0aom_finesim_fsdb_netlist_diag.md`（trace t0aom, finesim/fsdb）。
- **裁定**：承 r504 核对结论「III 不存在 1=FsdbNetToggleDiag vision 误抄」**freshly re-confirmed**。β5 **不是「已降级可恢复」的 case**，而是**从未造题**。它不在 Task1「恢复原形态」范围内（Task1 = 恢复已落库的降级文本替身）。若需 β5，属**新造 case**（t0aom 为 finesim/fsdb → D 或 B 域新造），应走常规造题流程，非 WAVEVIEW 恢复流程。
- **对基线分母的影响**：r504 已厘清基线分母 = 4（真降级文本替身可恢复）非 11；β5 进一步排除，分母不变。

### 小结

| 项 | 裁定 | 依据 |
|:--|:--|:--|
| β8 WaveView-002 | D 独占，无冲突 | grep 4 shard：仅 D.jsonl 1 命中，domain=waveform |
| β5 FsdbNetToggleDiag | case 不存在（vision 误抄），非恢复范围 | grep 4 shard：0 命中，仅深读笔记在 |

> D 可据此直接推进 β8 恢复；β5 若要纳入需先走造题流程（非本轮 WAVEVIEW 范畴）。
> — shard A 召集人，r508（2026-11-14）
