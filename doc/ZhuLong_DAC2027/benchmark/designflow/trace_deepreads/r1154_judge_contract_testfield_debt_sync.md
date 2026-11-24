# r1154 — judge-contract test-field 半提交债 sync 轮 (2026-11-24)

## 背景

11-24 运维令（判分契约修复）进行中。本会话唤醒时发现**并发 shard B worker**
在同一 loop 内已提交 r1153（binop 类别 16 case，commit `a36ee2b2d`），并更新了
MEMORY_B。为避免与并发 worker 冲突，本轮做**补充性、非冲突的债治理**：
r1149-r1152 遗留的 **cases/B JSON `test` 字段半提交债**。

## 问题

判分器跑的是 `cases/B/<id>.json` 的 `test` 字段（不是 `reference/<id>/check.py`）。
r1149-r1152 修了 reference/check.py 的返回值形状（→ `{'pass':...}` / `return True`），
但**忘记同步** cases/B JSON 的 `test` 字段。分类扫描发现 **40 case** 的
`test != reference/check.py`。细分为：

| 类别 | 数量 | 性质 |
|---|---|---|
| 真债（ref 合规, cases/B 非合规） | **18** | 评估器跑 broken test ⇒ 正确交付被误判 FAIL |
| 双方合规但形状不同 | 12 | 不影响判分（如 ref=True, cases/B=dict-pass-ok） |
| ref 也非合规 | 10 | 属于并发 worker 剩余违规队列，未碰 |

本轮只治理 **18 真债**（其余两类不动，避免与并发 worker 冲突）。

## 18 真债明细

- **6 stub**（test 字段 27-36 字符的 no-op）：AetherAutoloadDiag /
  CmlMirrorSweepAnalysis / DumWLDeckExplainQA / FineSimMetricCornerDiag /
  OpcModelExtract / ResistorTrimNetlistExplain
- **4 near-stub / broken**：HspiceAcMergeDiag / HspiceSweepWatchRender /
  OpampDummyCheckProduce / PowerSupplyDcTypeGenProduce /
  RunsimScriptDiffProduce / WvModalPopupTclFix
- **old-shape**（variable / NO_RETURN / ternary / call）：OpampACSpec /
  PFDdeadZone / ProbeTrim / SramSNM / StimPWL / CompressNetlist

## 修法

对每个 case：`cases/B/<id>.json` 的 `test` 字段 ← `reference/<id>/check.py` 全文。
仅改 `test` 字段，**不动** prompt / assets / metadata / attachments / 断言逻辑 /
断言条数 / 判分严格度（json.dump 保留所有原键，diff 验证仅 test 行变）。

## 验证

- **audit**（scripts/audit_check_returns.py --shard B）：
  OK 414→430(+16) / NO_CHECK 12→6 / NO_RETURN 52→47 / VIOL 119→114
- **18 ref py_compile** 全 OK（test 字段 == reference，同代码）
- **test==check.py 三方 sync** 验证：18 case 全部 test==reference
- **JSON 字段保留**：抽样 AetherAutoloadDiag 验证 attachments/entry_point/
  metadata/mode/prompt/task_id 全 SAME，仅 test CHANGED
- **negative_selftest**（OpampACSpec）：3 negs（empty_shell/print_expected/
  ref_no_core）全 FAILs_check=True（§4.9 trio intact）
- **SramSNM pre-existing 失败**：SramSNM negative_selftest 显示 ref 自身 cond k/n
  FAIL。git diff 证明本轮**未碰** SramSNM 的 reference/check.py → 失败是
  pre-existing reference-solution bug，非本轮引起。留待后续轮治理。

## 冲突隔离

- 并发 worker r1153 修 16 case（binop），本 r1154 修 18 case（test-field 债），
  **0 重叠**。
- 并发 worker 的 13 cases/B WIP（15:28 批次，未提交）未碰。
- shards A/C 的修改文件未碰。
- 仅 `git add` 本轮 18 个 cases/B JSON，精确暂存。

## 提交

- EDA-Flow-Bench master `56780fdbe`（18 files changed, 99 insertions, 28 deletions）
- super_intelligence_2035 main：MEMORY_B r1154 行 + 本 trace_deepreads 笔记

## 剩余

- 判分契约债：VIOL 119（no_return47 > dict_other30 > var39 > helper36 >
  none_bare12 > list6 > ternary2 > compare1）— 并发 worker 后续轮续修
- working-tree 半提交债：本轮清 18；并发 worker 13 WIP 待其自行提交
- SramSNM reference-solution bug（cond k/n）— 待治
- fresh 池仍耗尽（7 轮 reconfirm）— 无新 case 产出
