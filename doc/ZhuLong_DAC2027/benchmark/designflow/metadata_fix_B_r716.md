# metadata_fix_B_r716.md — r713 audit 方法学复检的 metadata-fix 落地分析（r716, 2026-11-17）

> 本文件是 r713 spotcheck（designflow/intent_audit_B_r713_spotcheck.tsv）的**落地前置分析**：
> 把 r713 标记的两类 metadata 待修项逐条验到可执行级别（含 check.py 证据 + 正确取值 + reframe_note 文案），
> 待 EDA-Flow-Bench 仓的 cases/ 重构落定后，apply 到 cases/B/*.json（新 source of truth）或 jsonl（旧 source）。
>
> **为什么本轮(r716)没有直接 apply 到文件**：EDA-Flow-Bench 工作树正处另一 shard 驱动的**重构中期**——
> `cases/<shard>/<case>.json` 成为新 source of truth、`EDA-Eval-DesignFlow_<shard>.jsonl` 降为 `scripts/build_jsonl.py`
> 的 build 产物。当前 cases/B/ 仅 394 case（旧 jsonl 407，13 case 未迁移，含 SiOutDiag-001），
> build_jsonl.py / cases/ / .gitignore 均为 untracked/in-flight。按 AGENTS.md 同步纪律
> （「🚫 不 clean / reset / stash 别人的改动；陌生未提交文件是别线在途」）本轮**不动 EDA-Flow-Bench 工作树**，
> 仅在此落盘分析，待重构落定后下一轮 apply。

## 1. layer="spice_sim" metadata bug（3 题，应 L2）

r618 audit 的 template-C 标记 3 题 `metadata.layer="spice_sim"`（应为 L1/L2/L3 之一）。本轮 r716 逐题读
`reference/<id>/check.py` 证实三题 check 均 **subprocess 真跑 Synopsys HSPICE V-2023.12-SP1-1（.75 EDA 沙盒
/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice）于隐藏 netlist B**，独立解析 .lis measure 作
ground truth + 跨输入 A guard ⇒ 符合 TASK §5 L2「真跑沙盒工具…经 eda_flow/.75」定义，**非离线 Python 复刻（L1）**，
也非多工具链路+修复+回归（L3）。与同族 deck-generation case（ProbeTrim/SramSNM/StimPWL/InvPVTchar/
InvTripDelay/StdLibCharTmpl/PulseStimTbGen/... 全 L2）口径一致。

| task_id | check.py 证据（subprocess hspice） | 正确 layer | layer_rationale（拟写入） |
|---|---|---|---|
| EDA-Eval-DesignFlow-DelaySigma-001 | check.py L40 `HSPICE=...`；L166 `subprocess.run([HSPICE,"-i","gt_tb.sp",...])`；cond g「HSPICE really runs...converged+concluded」；cond h「baseline slowest == independent GT HSPICE run on B」；14 断言 a..n | **L2** | L2：check() 在隐藏 B（20 stages/vcc=1.1/PCHB/NCHAB/STD0..STD19，与公开 A 的 16 stages/vcc=0.9/PCH/NCHA 全异）上经 subprocess 真跑 Synopsys HSPICE V-2023.12-SP1-1（.75 沙盒），独立解析 .lis measure 作 ground truth，跨输入 A guard。符合 §5 L2『真跑沙盒工具』定义，非离线 Python 复刻。 |
| EDA-Eval-DesignFlow-SpGen-001 | check.py L54 `HSPICE=...`；L169-171 `run_hspice` → `subprocess.run([HSPICE,"-i",...])`；cond j「hspice_runs_converges_B」；cond k「measures_match_hspice_and_ground_truth」；15 断言 | **L2** | L2：check() 在隐藏 B（AG_VddqRefBuf，与公开 A 的 AG_VwlpRefAnalog 端口/时序/拓扑全异）上经 subprocess 真跑 Synopsys HSPICE V-2023.12-SP1-1（.75 沙盒），独立解析 .lis 的 .measure tran AVG V(<load_output>) 作 ground truth，跨输入 A guard。符合 §5 L2『真跑沙盒工具』定义，非离线 Python 复刻。 |
| EDA-Eval-DesignFlow-SpiceSim-001 | check.py docstring 首行即「spice_sim domain, L2: real hspice run on hidden netlist B」；L172 `subprocess.run(cmd,...)`；10 断言 a..j | **L2** | L2：check() 在隐藏 netlist B（不同 stage count/vdd/node names/device sizes/period 与公开 A 全异，不进 SUT 沙箱）上把候选生成的 .measure deck 拼到 B，经 subprocess 真跑 Synopsys HSPICE V-2023.12-SP1-1（.75 沙盒），独立解析 .lis measure 校验结构+spec+order-independence。符合 §5 L2『真跑沙盒工具』定义，非离线 Python 复刻。 |

**apply 操作**（待重构落定）：对 3 题 metadata：`layer: "spice_sim"` → `layer: "L2"`，新增 `layer_rationale`（上表末列）。
当前 layer 分布（旧 jsonl 407 行）：L2=76 / L1=65 / None=263 / spice_sim=3 → 修后 L2=79 / spice_sim=0。

## 2. reframe_note 标注（5 题 keep_reframe_for_teeth，r713 spotcheck）

r713 抽样 12 题逐题比对 real_task_summary vs prompt vs check.py，判 5 题为 `keep_reframe_for_teeth`
（用户意图是 how-to/Q&A/diagnose/explain，因 §4.2 subprocess + §4.1 hidden-B 使纯 Q&A 无法「有牙」，
重构为 produce 形态入库——意图有偏移但 §4 结构性必要，保留）。r713 建议「对 50 嫌疑 case 加 reframe_note
字段（本轮不批量改 319 行 jsonl，留增量做）」。本轮 r716 落地这 5 题的 reframe_note 文案（增量第一批）：

| task_id | r713 判定 | reframe_note（拟写入 metadata） | cases/B/ 中存在？ |
|---|---|---|---|
| EDA-Eval-DesignFlow-InstCurrentMeasGen-001 | keep_reframe_for_teeth | how-to Q&A→produce (§4 有牙必要, r713 spotcheck): 用户问怎么测器件支路电流(how-to)，重构为产测量脚本以使 check 满足 §4.2 subprocess + §4.1 hidden-B 有牙要求；意图有偏移但 §4 结构性必要，保留。 | ✓ |
| EDA-Eval-DesignFlow-SiOutDiag-001 | keep_reframe_for_teeth | diagnose Q&A→produce (§4 有牙必要, r713 spotcheck): 用户问仿真时间变长/memory 变大原因(diagnose)，重构为产诊断工具 siout_diag.py 输出 JSON；工具产出诊断结论即交付诊断，§4 有牙结构性必要，保留。 | ✗（未迁移，13 case 之一） |
| EDA-Eval-DesignFlow-FineSimOomDiag-001 | keep_reframe_for_teeth | diagnose→produce (§4 有牙必要, r713 spotcheck): 用户在诊断 FineSim OOM，重构为产 OOM 内存诊断报告生成器；报告即诊断交付物，check 有牙 ⇒ 重构必要，保留。 | ✓ |
| EDA-Eval-DesignFlow-StackedMOSOpAnalysis-001 | keep_reframe_for_teeth | OP 仿真看结果→produce (§4 有牙必要, r713 spotcheck): 用户跑五管 OTA 静态工作点仿真看结果，重构为产串联堆叠 MOS OP 分析工具；check 有牙 ⇒ 重构必要，保留。 | ✓ |
| EDA-Eval-DesignFlow-TrimMarginSpec-001 | keep_reframe_for_teeth | explain→produce (§4 有牙必要, r713 spotcheck): 用户要讲解/verify delay-trim 链(explain)，重构为产 trim 表征测量；check 有牙 ⇒ 重构必要，保留。 | ✓ |

**apply 操作**（待重构落定）：对上表 5 题 metadata 新增 `reframe_note` 字段（值见上表）。
SiOutDiag-001 待 cases/ 重构迁移后再 apply（当前仅在旧 jsonl）。

## 3. 未落地项（后续轮次增量）

- **~110 legacy 题 task_id=None**（r618 template-B）：trace-faithful 非意图问题，需补 task_id；量大留后续轮次批量做。
- **r713 剩余 ~45 嫌疑 case**（50 Q&A→produce 嫌疑 − 已 spotcheck 12 − 本轮 reframe_note 5）：需逐题 spotcheck
  后决定是否标 reframe_note；留后续轮次。
- **apply 本文件 §1+§2 到 cases/B/**：待 EDA-Flow-Bench 仓 cases/ 重构落定（cases/B/ 全量 407 + .gitignore +
  build_jsonl.py 入 git）后，下一轮第一件事 apply 7 题（§1 三题 + §2 六题中 cases/B/ 已有的，SiOutDiag-001 待迁移）。

## 5. r717 apply 落地（2026-11-17，本轮完成）

r716 因 cases/ 重构在途未 apply；本轮 r717 复核发现重构已落定——
EDA-Flow-Bench commit `487667419`「feat: per-case 文件方式 — jsonl 降级为 build 产物 (gitignored)」已入 git，
`scripts/build_jsonl.py` 已 tracked，`cases/B/` = 394 = `EDA-Eval-DesignFlow_B.jsonl` 行数（jsonl 现为 gitignored build 产物）。
新 source of truth = `cases/B/<case>.json`。本轮把 §1 + §2 的 7 题 apply 到 cases/B/：

| task_id | 修复 | 旧值 → 新值 |
|---|---|---|
| DelaySigma-001 | layer + layer_rationale | `spice_sim` → `L2` + rationale |
| SpGen-001 | layer + layer_rationale | `spice_sim` → `L2` + rationale |
| SpiceSim-001 | layer + layer_rationale | `spice_sim` → `L2` + rationale |
| InstCurrentMeasGen-001 | reframe_note | `<none>` → how-to→produce note |
| FineSimOomDiag-001 | reframe_note | `<none>` → diagnose→produce note |
| StackedMOSOpAnalysis-001 | reframe_note | `<none>` → OP→produce note |
| TrimMarginSpec-001 | reframe_note | `<none>` → explain→produce note |

**未 apply**：SiOutDiag-001（reframe_note）—— cases/B/ 未迁移（13 case 之一，旧 jsonl 407→cases/B 394 时被剔除），待迁移后补。

## 6. r718 跨 shard 迁移复核（2026-11-17，本轮完成）

r717 假设 SiOutDiag-001「待迁移到 cases/B/」后由 B 补 apply reframe_note。本轮 r718 复核 cases/ 实际分布发现
**该假设不成立**——SiOutDiag-001 已被 cases/ 重构正确放入 **cases/D/**（按 `metadata.domain=schematic_netlist`
归 D 域），而非 cases/B/。这是**正确的**域归属：schematic_netlist 是 D 域，SiOutDiag-001 用户 `kli` 在
hfhds206 上做 FineSim/PrimeSim DDR5 fullchip transient 仿真诊断，本质是网表/仿真日志分析（D 域 schematic_netlist），
非 B 域 spice_sim/characterization。旧 B jsonl 含此 case 是历史合并口径遗留，cases/ 重构已修正。

**实证**（r718 本轮跑）：
```
cases/ per shard: {'A': 348, 'B': 394, 'C': 435, 'D': 455} total: 1632
B cases domain distribution: {'spice_sim': 330, 'characterization': 64}  # 全 B 域, 干净
SiOutDiag-001: shard=D domain=schematic_netlist reframe_note=False
```
B cases/ 394 全部 spice_sim/characterization（B 域），SiOutDiag-001 不在其中；它在 cases/D/ 且 domain=schematic_netlist（D 域）。

**结论**：
- B 的 r713 spotcheck 当时因 SiOutDiag-001 在 B 旧 jsonl 内而抽样审，判 `keep_reframe_for_teeth` 成立（reframe
  必要性判断与域归属无关，§4 有牙结构性必要）。该判断**仍有效**——SiOutDiag-001 的 diagnose-Q&A→produce 重构
  确为 §4.2 subprocess + §4.1 hidden-B 有牙所必需，无论 case 落哪个 shard。
- 但 **apply reframe_note 到文件是 D 的职责**（case 在 cases/D/，B 依同步纪律 🚫 不改 D shard 文件）。
- B 的 metadata-fix 工作收口：**7/8 已 apply 到 cases/B/（r717），第 8 条（SiOutDiag-001 reframe_note）
  连同 reframe_note 文案移交 D 线 apply**。

**移交 D 线的 reframe_note 文案**（D 线 apply 到 `cases/D/EDA-Eval-DesignFlow-SiOutDiag-001.json` metadata）：
```
reframe_note: "diagnose Q&A→produce (§4 有牙必要, r713 spotcheck): 用户问仿真时间变长/memory 变大原因(diagnose)，重构为产诊断工具 siout_diag.py 输出 JSON；工具产出诊断结论即交付诊断，§4 有牙结构性必要，保留。"
```
依据：r713 spotcheck（designflow/intent_audit_B_r713_spotcheck.tsv）+ r716 §2 文案定稿 + r718 本节域归属复核。
D 线 apply 后 B 线 r713 audit 的 5 条 keep_reframe_for_teeth 全部闭合。

**自验**：① 7 文件 JSON 合法（json.load 全过）② `python3 scripts/build_jsonl.py --check` 通过（cases/ 总计 1631，B=394）③ `--shard B` 重建 jsonl = 394 行 ④ test 字段未动 ⇒ test_rationale k 不变，670/670 断言达标不受影响 ⑤ 仅 stage 本轮 7 文件，别线在途（RonMono 资产删除等）未碰。
**commit**：EDA-Flow-Bench master `326751e5a`「designflow shard B #r717: apply r716 metadata-fix to 7 cases...」已 push。

**layer 分布修后**（cases/B 394）：L2 = 76+3 = 79 / spice_sim = 0（旧 spice_sim=3 已清零）。

## 4. r716 0-case 证据（mc≥10 硬规则）

```
python3 designflow/trace_ledger.py --shard B mc-matrix --src designflow/summary_1115_081559.tsv
# 阈值          池总量   已动过   未动过(可做)
# mc>=10         943      943        0     ← 第 92 轮 re-confirm
```
四快照结构性饱和（1109/1113/1114/1115_081559）+ 复活池 r712 host-verify 实质性耗尽（9 real-trace 候选 0 干净 B 域可造）⇒ 符合 mc≥10 硬规则 0-case 判据。
