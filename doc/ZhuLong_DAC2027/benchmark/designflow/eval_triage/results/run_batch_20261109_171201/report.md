# Batch failure triage — triage_batch_20261109_171201

> 由 `05_batch_triage.py` v1.0.0 自动生成（2026-11-10T21:23:53+0800）。所有判定都带证据路径，可直接回查。

## 1. 输入与发现

- batch 目录: `/nasdata/app.e0031982/.cache/triage_batch_20261109_171201`
- cases jsonl: `/nasdata/app.e0031982/.cache/triage_cases_696.jsonl`（696 条，id 键=`task_id`，domain 键=`domain`）
- domain 来源: `field:domain`
- 目录布局命中: `.`x690
- 找到 case 目录 690/696；缺失 6（判为 ABSENT）

## 2. 总体结果

| PASS | FAIL | ERROR | ABSENT | Total |
| --- | --- | --- | --- | --- |
| 62 | 558 | 70 | 6 | 696 |

- **Pass%（本工具口径）= PASS/(PASS+FAIL) = 62/620 = 10.00%**
- PASS/(PASS+FAIL+ERROR) = 62/690 = 8.99%（ERROR 记 non-pass）
- PASS/非 ABSENT = 62/690 = 8.99%
- PASS/Total = 62/696 = 8.91%
- Ground-truth 对照（2026-11-09 全量批次）：62 PASS / 558 FAIL / 70 ERROR / 6 ABSENT / 696，即 62/620 = 10.0%、62/626 = 9.9%。若本报告计数与之一致，说明目录发现与判定口径都对得上。

## 3. 逐域状态矩阵

| Domain | PASS | FAIL | ERROR | ABSENT | Total | Pass% |
| --- | --- | --- | --- | --- | --- | --- |
| analog_context | 4 | 39 | 12 | 0 | 55 | 9.3 |
| characterization | 5 | 21 | 2 | 0 | 28 | 19.2 |
| digital | 5 | 40 | 6 | 0 | 51 | 11.1 |
| eda_other | 6 | 27 | 4 | 1 | 38 | 18.2 |
| layout_aether | 1 | 33 | 4 | 0 | 38 | 2.9 |
| layout_virtuoso | 4 | 35 | 0 | 1 | 40 | 10.3 |
| pg_layout | 4 | 24 | 0 | 0 | 28 | 14.3 |
| physical_verify | 2 | 66 | 4 | 1 | 73 | 2.9 |
| pnr_signoff | 5 | 19 | 0 | 1 | 25 | 20.8 |
| schematic_netlist | 13 | 100 | 18 | 0 | 131 | 11.5 |
| spice_sim | 8 | 87 | 7 | 2 | 104 | 8.4 |
| verification | 3 | 30 | 5 | 0 | 38 | 9.1 |
| waveform | 2 | 37 | 8 | 0 | 47 | 5.1 |
| **Total** | 62 | 558 | 70 | 6 | 696 | 10.0 |

## 4. 失败类别分布（FAIL + ERROR 细分）

| Class | Count | % of FAIL+ERROR |
| --- | --- | --- |
| NO_SUBMIT | 70 | 11.1 |
| FORMAT_CONTRACT | 2 | 0.3 |
| ASSERT_RUNTIME | 132 | 21.0 |
| ASSERT_SEMANTIC | 305 | 48.6 |
| UNKNOWN | 119 | 18.9 |

Top 3: ASSERT_SEMANTIC=305, ASSERT_RUNTIME=132, UNKNOWN=119

## 5. UNKNOWN 与 coverage（显式披露，不藏进别的类）

- UNKNOWN = 119 例，占 FAIL+ERROR 的 **18.95%**（119/628），占全批 17.10%
- coverage：找到判分证据的 case = 690/696 = 99.14%（非 ABSENT 口径 100.00%）
- coverage_warning：无（每个非 ABSENT case 都找到了判分证据）

## 7. 随机抽样 case 的证据路径（10 例，seed=20261109）

### `EDA-Eval-DesignFlow-AddCellPin-001` — FAIL / ASSERT_SEMANTIC

- 判定依据: `tier1_fail_verdict: 失败条件编号 1 @check.log`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-AddCellPin-001`
- tier1 结构化判定: `judge_result.json`:verdict=FAIL→FAIL
- tier2 日志摘要: `check.log`(pass=0,fail=3,err=0), `cline_stderr.log`(pass=0,fail=0,err=0)
- tier3 交付物: `submit.zip`(openable=True,entries=2,issue=None)
- 证据文件清单: `check.log`, `judge_result.json`, `submit.zip`

### `EDA-Eval-DesignFlow-CosimStimFolderGen-001` — ERROR / UNKNOWN

- 判定依据: `tier1_error_verdict: 有 ERROR 标记但无 infra/timeout 签名`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-CosimStimFolderGen-001`
- tier1 结构化判定: `judge_result.json`:verdict=ERROR→ERROR
- tier2 日志摘要: `check.log`(pass=0,fail=0,err=1)
- 证据文件清单: `check.log`, `judge_result.json`

### `EDA-Eval-DesignFlow-IfElsePairFix-001` — FAIL / ASSERT_SEMANTIC

- 判定依据: `tier1_fail_verdict: 失败条件编号 1 @check.log`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-IfElsePairFix-001`
- tier1 结构化判定: `judge_result.json`:verdict=FAIL→FAIL
- tier2 日志摘要: `check.log`(pass=0,fail=2,err=0), `cline_stderr.log`(pass=0,fail=0,err=0)
- tier3 交付物: `submit.zip`(openable=True,entries=1,issue=None)
- 证据文件清单: `check.log`, `judge_result.json`, `submit.zip`

### `EDA-Eval-DesignFlow-LvsAmbiguityDiag-001` — FAIL / ASSERT_RUNTIME

- 判定依据: `tier1_fail_verdict: 日志签名: reason=(False, [('a', True, 'ok'), ('b', True, "compile=True std=True imports: ['argparse', 'json', 're']"), ('c', False, "rc=1 json=False tb=False json load fail: [Errno 2] No suc @check.log`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-LvsAmbiguityDiag-001`
- tier1 结构化判定: `judge_result.json`:verdict=FAIL→FAIL
- tier2 日志摘要: `check.log`(pass=0,fail=1,err=0), `cline_stderr.log`(pass=0,fail=0,err=0)
- tier3 交付物: `submit.zip`(openable=True,entries=1,issue=None)
- 证据文件清单: `check.log`, `judge_result.json`, `submit.zip`

### `EDA-Eval-DesignFlow-LvsMrcBrknetDiag-001` — ERROR / UNKNOWN

- 判定依据: `tier1_error_verdict: 有 ERROR 标记但无 infra/timeout 签名`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-LvsMrcBrknetDiag-001`
- tier1 结构化判定: `judge_result.json`:verdict=ERROR→ERROR
- tier2 日志摘要: `check.log`(pass=0,fail=0,err=1)
- 证据文件清单: `check.log`, `judge_result.json`

### `EDA-Eval-DesignFlow-PorCapSweep-001` — FAIL / ASSERT_SEMANTIC

- 判定依据: `tier1_fail_verdict: 失败条件编号 1 @check.log`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-PorCapSweep-001`
- tier1 结构化判定: `judge_result.json`:verdict=FAIL→FAIL
- tier2 日志摘要: `check.log`(pass=0,fail=2,err=0), `cline_stderr.log`(pass=0,fail=0,err=0)
- tier3 交付物: `submit.zip`(openable=True,entries=2,issue=None)
- 证据文件清单: `check.log`, `judge_result.json`, `submit.zip`

### `EDA-Eval-DesignFlow-SacapSignalMissingDiagnose-001` — FAIL / UNKNOWN

- 判定依据: `tier1_fail_verdict: 有 submit 且无任何可核验的失败信号`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-SacapSignalMissingDiagnose-001`
- tier1 结构化判定: `judge_result.json`:verdict=FAIL→FAIL
- tier2 日志摘要: `check.log`(pass=0,fail=2,err=0), `cline_stderr.log`(pass=0,fail=0,err=0)
- tier3 交付物: `submit.zip`(openable=True,entries=1,issue=None)
- 证据文件清单: `check.log`, `judge_result.json`, `submit.zip`

### `EDA-Eval-DesignFlow-SpiceMeasInserter-001` — ERROR / UNKNOWN

- 判定依据: `tier1_error_verdict: 有 ERROR 标记但无 infra/timeout 签名`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-SpiceMeasInserter-001`
- tier1 结构化判定: `judge_result.json`:verdict=ERROR→ERROR
- tier2 日志摘要: `check.log`(pass=0,fail=0,err=1)
- 证据文件清单: `check.log`, `judge_result.json`

### `EDA-Eval-DesignFlow-VrefcsMrrSeq-001` — FAIL / ASSERT_SEMANTIC

- 判定依据: `tier1_fail_verdict: 失败条件编号 1 @check.log`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-VrefcsMrrSeq-001`
- tier1 结构化判定: `judge_result.json`:verdict=FAIL→FAIL
- tier2 日志摘要: `check.log`(pass=0,fail=2,err=0), `cline_stderr.log`(pass=0,fail=0,err=0)
- tier3 交付物: `submit.zip`(openable=True,entries=1,issue=None)
- 证据文件清单: `check.log`, `judge_result.json`, `submit.zip`

### `EDA-Eval-DesignFlow-WlAdjFind-001` — ERROR / UNKNOWN

- 判定依据: `tier1_error_verdict: 有 ERROR 标记但无 infra/timeout 签名`
- wall: n/a s
- case 目录: `EDA-Eval-DesignFlow-WlAdjFind-001`
- tier1 结构化判定: `judge_result.json`:verdict=ERROR→ERROR
- tier2 日志摘要: `check.log`(pass=0,fail=0,err=1)
- 证据文件清单: `check.log`, `judge_result.json`

## 8. 复现命令

```bash
python3 05_batch_triage.py --batch /nasdata/app.e0031982/.cache/triage_batch_20261109_171201 --cases /nasdata/app.e0031982/.cache/triage_cases_696.jsonl --out results/run_batch_20261109_171201 --emit-tex
```
