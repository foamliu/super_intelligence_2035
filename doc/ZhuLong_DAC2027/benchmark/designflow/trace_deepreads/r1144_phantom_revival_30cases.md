# r1144 — Phantom Case Revival (30 cases) — 2026-11-24

## 背景：推翻 r1143「dangling gap=0」错误结论

r1143 MEMORY 写「cases/B JSON 568 == ledger case 568 gap=0」。r1144 实测：
- `awk -F'\t' '$6=="case"' designflow/trace_ledger_B.tsv | wc -l` = **597**
- `ls cases/B/*.json | wc -l` = **568**
- gap = **30**（r1143 用错口径，漏数 30 条 ledger case 行）

30 phantom = ledger 标 `case` 但 cases/B 无对应 JSON。全部是 jsonl-era（r1046–r1074）落库的真实 case：当时直接 append 到 `EDA-Eval-DesignFlow_B.jsonl`，未写 per-case JSON。2026-11-23 运维令物理删除 jsonl 后，这 30 条只剩 ledger 记录，case 内容丢失。

## 根因
运维令切换 source-of-truth 从 jsonl → `cases/<shard>/<id>.json`，但 jsonl-era 的 30 条 case 从未写成 per-case JSON，jsonl 删除后即变 phantom。

## scan 核验
eda_flow open_session → run_commands `ls -1dt /home/t0002965/log/ssh_eda_search_*`：
最新 scan 仍 `ssh_eda_search_20261124_023802`（r1110 起未变）。fresh 池仍耗尽（r1125/r1126/r1131/r1143 四轮 reconfirm）。无新 trace 可造新 case。

## 恢复方法
git log 显示 B.jsonl 在 commit `27e5ff3fe`（r1074，最后内容提交）前一直 tracked，`3d8511e9f` untrack。
```
git show 27e5ff3fe:benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_B.jsonl > /tmp/old_B.jsonl  # 554 行
```
该版本含全部 30 phantom（schema 不一致：部分用 `id`=全名+`task_id`=短名，部分只有 `task_id`=全名）。脚本按 `id`/`task_id` 双索引匹配 30 phantom，规范化 `id`=`task_id`=全名，写入 `cases/B/<id>.json`。

## 校验
1. **结构校验（30/30 通过）**：JSON 可解析；`id`/`task_id`/`mode`=design_flow/`entry_point`=outputs/submit.zip/`test`/`prompt`/`attachments`/`metadata` 齐全；`metadata.trace_source`{user,host,session_file,match_count} 完整；`test_rationale` 存在；attachments 路径全部存在。
2. **test==check.py（逐字节）**：case JSON `test` 字段 == `reference/<id>/check.py` 内容（抽样 FinesimMt0ParserProduce-001 确认 `t==c` True）。
3. **selftest 抽样 2 条**：
   - `FinesimMt0ParserProduce-001`：REF 15/15 PASS + 3 neg（neg_empty/neg_print_only/neg_no_classify）全 FAIL + 3-seed sha256 一致。
   - `SubcktUnclosedDiagProduce-001`：REF 15/15 PASS + 3 neg（neg_empty/neg_print_only/neg_count_only）全 FAIL。
4. **gap 闭合**：cases/B 568→598，ledger case 597，phantom 30→0（+1 为正常 dangling case：cases/ 有但 ledger 无，运维令#4 明确为正常状态）。

## 30 phantom 列表
C2cCornerAmplifierAudit, CompressNetlist, CornerBlockGenProduce, DelvtoNetlistModifier, DividerNetlistRolePatch, DsimSkillLogAnalyzer, DualRatePwlClockGen, DutyMidvalMeasRewrite, DutyOffsetAlertMaxProduce, FinesimMt0ParserProduce, FinesimWarnAnalyzeProduce, JitterDutyBlockPwlGen, LatchFomSweepFineSim, LatchResetFomSweep, MeasTranSamplerGen, MissingRefDiagnose, MosComparaReportGen, MosToxeClassify, NetlistStructDiff, OcsaTr0AsymAnalyze, ProbeCovAnalyzerProduce, PumpcoreAgingDeckGen, PvtMt0ThreeLevelAggregate, ResCornerTempSweep, SigmaflagEffectAnalyzerProduce, SubcktUnclosedDiagProduce, TieJitterIncGenProduce, TrimSkewIncrementProduce, UlvtGmCharAnalyzer, Vvdd2cStimRewriteProduce（均 -001）。

## 遗留债务
- 30 revived case 的 `test_rationale` 多为旧格式（非「k 条断言：①…」），属遗留债务，非本轮新建。后续可批量改写。
- 13 条无 `reference/<id>/` 目录（CornerBlockGenProduce 等），无法重跑 selftest；但 case JSON `test` 字段完整 + assets 存在，evaluator 可用。原 §4.9 在创建时已验（见 ledger note）。

## 台账
不变（1769：case 597 / parked 1172 / claimed 0）。covered=597/4529=13.2%。本轮为文件恢复，不新增 ledger case 行。
