# Shard D §4.9 Anti-Hardcode 静态普查报告（r1170）

> 普查范围：`EDA-Eval-DesignFlow_D.jsonl` 全部 560 条 case
> 方法：静态扫描 `reference/<id>/check.py` + jsonl 内联 `test` 字段 + `metadata.test_rationale` 的 k 值
> 产出：`designflow/anti_hardcode_audit_D.tsv`（560 行）
> 普查轮次：r1170（stop-loss 转向：高 mc D 候选池耗尽，连续 3 轮 0 case 后转 anti-hardcode 自查）
> 普查日期：2026-11-23

## 一、总量与判定分布

| 判定 | 数量 | 占比 |
|:--|--:|--:|
| PASS | 472 | 84.3% |
| PASS(inline) | 0 | — |
| GAP | 88 | 15.7% |
| **合计** | **560** | 100% |

> 80 条「无 reference 目录」的 case 实为 check.py 内联在 jsonl `test` 字段（test_len 12k–23k，含 `def check` + subprocess），属合法设计变体，**不计 GAP**。

## 二、GAP 原因分布（一条 case 可叠加多个原因）

| GAP 原因 | 数量 | §条款 | 严重度 |
|:--|--:|:--|:--|
| no-negative | 71 | §4.4（≥2 负样本 + selftest） | 中（缺回归闸门） |
| no-hidden-B | 15 | §4.1（check 只跑 hidden B） | 高（可能跑 A） |
| no-subprocess | 10 | §4.2（真跑候选） | 高（静态误报待核） |
| print_only-risk | 3 | §4.9(b) | 极高（可能假提交 PASS） |

> k_check 全部 ≥8（用 `test_rationale` 的「N 条断言」+ check.py 的 assert/raise/cond/accumulator 计数取 max）。无 k<8 GAP。

## 三、Top 风险题（需优先 runtime 复核）

### 3.1 print_only-risk（3 条，1 确认 + 2 待 runtime 复核）

| case_id | k | gaps | 静态判定 | 复核结论 |
|:--|:--|:--|:--|:--|
| **EDA-Eval-DesignFlow-VddSensTDCRootCause-001** | 12 | no-subprocess;no-hidden-B;print_only-risk | 极高风险 | **确认 GAP**：check.py 只从 submit.zip 读 `analysis.json` 校验内容，**不跑候选脚本**，hardcode 的 analysis.json 可 PASS。无 hidden B 引用。 |
| EDA-Eval-DesignFlow-TrMatchHelper-001 | 14 | no-subprocess;print_only-risk | 待核 | 静态误报可能：用 `importlib`/`exec` 跑候选 helper（非 subprocess），有 `HIDDEN` 目录。需 runtime 跑 fake_print_only 验证。 |
| EDA-Eval-DesignFlow-WvEdgeTiming-001 | 17 | no-subprocess;print_only-risk | 待核 | 静态误报可能：`_load_candidate` 用 importlib 加载候选模块，有 `HIDDEN`。需 runtime 验证。 |

### 3.2 no-subprocess（10 条，部分为 importlib 误报）

`ParasiticsAnnotDiag-001`(k=9)、`OpenDmViewsProduce-001`、`IddMeasPostProcess-001`、`IddTreeAnalyze-001`、`IrunLogNetlistMissingModDiagQA-001`、`LvsConcatDiagQA-001`、`MosfetBlockInventoryQA-001` 等。
> 静态只搜 `subprocess|os.system|os.popen`，未覆盖 `importlib`/`exec`/`popen2`。下轮应用 runtime 跑 fake_print_only 区分「真不跑候选」vs「用 importlib 跑」。

### 3.3 no-hidden-B（15 条，§4.1 风险）

`EDA-Eval-DesignFlow-Analog-001`(k=25)、`EDA-Eval-DesignFlow-Characterization-001`(k=26)、`EDA-Eval-DesignFlow-CABufDiffPairOPCheck-001`、`StdcellFullAdderBuild-001`、`StdcellRerunCollect-001`、`StdcellStatusPartition-001`、`TbFamilyMergeConverted-001`、`TbFamilyResultVerify-001`、`TsCodeComp3bitLogicDiffQA-001` 等。
> check.py 未出现 `hidden` 字样。需逐条核：是否用了别的 B 输入命名（如 `B_`/`b_input`/`assets/<id>/b/`），还是真在 A 上跑。前者改名即可，后者是真 §4.1 GAP。

### 3.4 no-negative（69 条，§4.4 缺口）

k 分布：16(15条)/14(10)/15(8)/12(7)/13(6)/18(4)/21(3)/17(2)/34(2)/其它。
> 这些 case 有 check.py 但缺 `negative/` + `negative_selftest.py` 回归闸门。§4.9(a)(b)(c) 三假无法批量自跑。修复方式：每条补 ≥2 假提交 + selftest。工作量较大，建议分批（每轮补 5–10 条）。

## 四、静态普查的局限（下轮改进）

1. **subprocess 检测不全**：未覆盖 `importlib.util`/`exec`/`popen2`/`runpy`。下轮加 `importlib|exec\(|runpy|popen2` 正则，降误报。
2. **hidden-B 检测粗**：只搜 `hidden` 字样，漏了 `B_`/`b_input`/`assets/<id>/b/` 等命名。下轮扩正则。
3. **print_only-risk 判据粗**：`in` 操作符占比≥60% 且无 subprocess 即判 risk，误报高。应改用 runtime 跑 fake_print_only。
4. **静态无法判 only_b / core_deleted / hardcode_a**：这三列标 `static-skip`，必须 runtime 跑三假提交。

## 五、处置分工（守职责边界）

- **D 自己的 case（560 条）**：本普查已落 TSV。下轮起按风险序修复：先 VddSensTDCRootCause-001（确认 GAP，直接重写 check.py），再 runtime 复核 2 条 print_only 待核 + 10 条 no-subprocess + 15 条 no-hidden-B，最后分批补 69 条 no-negative。
- **别的 shard（A/B/C）**：🚫 不直接改。本普查仅覆盖 D。A/B/C 由各自 shard 自查（参见 2026-11-21 用户令「全 bench §4.9 anti-hardcode 普查」）。
- **复现命令**：
  ```bash
  cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark
  python3 designflow/anti_hardcode_audit_D_static.py
  # TSV: designflow/anti_hardcode_audit_D.tsv
  ```

## 六、结论

D shard 560 条中 **88 条 GAP（15.7%）**，其中 **1 条确认高危（VddSensTDCRootCause-001，print_only 可 PASS）**，2 条 print_only 待 runtime 复核，15 条 no-hidden-B + 10 条 no-subprocess 需 runtime 区分真 GAP vs 静态误报，69 条 no-negative 为 §4.4 回归闸门缺口（分批补）。**k_check 全部 ≥8**，§4.3 闸门达标。下轮起按风险序修复 D 自己的 case，并同步本普查结论至 `discuss/D.md`。
