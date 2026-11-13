# r522 deepread: 1794538757522_mku3e — JSON→GDS→DRC 自动化校验流水线 (physical_verify L2) · 2026-11-13

**状态**: CLAIMED (r522, physical_verify, mc=603) — **首个 fresh C 域 produce-task 候选**，refutes 92-round high-mc fresh pool saturation。

## session 元数据
- **session_id**: 1794538757522_mku3e · user=e0047488 · host=hfeg0plg97 (10.129.8.229)
- **model**: glm-5.3-flash · **status**: failed (exit_code=1) · interactive=true
- **cwd**: /home/e0047488/QA_pattern_repo_linux
- **title**: "我们项目当前的输出文件是out下的JSON文件…需要打通从我们的产物文件直接到GDS到DRC check返回结果的路径"
- **runs**: 156 checkpoints · 359 msgs · 1.5MB messages.json · 9 real user_input turns
- **keywords**: drc:1887;calibre:1519;pyaether:754;aether:208;.gds:121;gdsii:107;lvs:36

## 用户意图（逐轮）
- **U#0**: 建自动化校验流水线：JSON产物 → GDS → DRC check → 结果返回。核心 produce-task。
- **U#1**: Argus(华大九天DRC) vs calibre；LD_LIBRARY_PATH 污染；test_vco.py 卡住 → 换方法
- **U#3**: Argus 链路脚本总卡住 → **请生成 calibre 脚本**，用户自己在服务器上跑
- **U#4**: 用户跑了 `calibre -drc -hier .../deck.cal` (timeout=600s)，返回 `[DRC] M1_A_1_bad`
- **U#6**: **ERROR: Rule file precision 1000 ≠ database precision 10000** in GDS（关键真实 bug）
- **U#7**: DRC 结果解析 — `M1_W_1_good total=0`，summary parsed
- **U#8**: 请写 md 文档说明此功能（跨平台协作）

## 资产清单（已 scp 到 .75 workdir mku3e_assets/）
| 文件 | 大小 | 用途 |
|:--|--:|:--|
| input_DR_m1/bad_M1.A.1.json | 3792 | A-input: bad area pattern (M1.A.1 面积<0.00368) |
| input_DR_m1/good_M1.A.1.json | 2289 | A-input: good area pattern |
| input_DR_m1/bad_M1.S.20.json | 13903 | **B-input(hidden)**: bad mark1-space pattern (M1.S.20) |
| input_DR_m1/good_M1.S.20.json | 11029 | **B-input(hidden)**: good mark1-space pattern |
| drc_run/gds/M1_A_1_{bad,good}.gds | 758/503 | GDS (dbu=0.0001um, precision 10000) |
| drc_run/gds/M1_S_20_{bad,good}.gds | 2359/1848 | B-input GDS |
| drc_run/drc_report.json | 5130 | **金标准**: 8 patterns × per-pattern verdict |
| deck/m1_qa_deck.cal | 2258 | Calibre SVRF deck (4 checks) |
| deck/qa_drc.layermap | 686 | layer map (88/651→M1, 88/51→M1_mark1) |

## 金标准 drc_report.json 结构
```
{ "generated_at", "json_dir", "gds_dir", "deck", "layermap", "verdict_mode":"per-rule",
  "patterns": [ { pattern, cell, gds, kind(bad/good), rule, expected_check,
    check_counts: {M1_W_1, M1_S_1, M1_S_20, M1_A_1},
    own_violations, cross_check_counts, total_violations,
    verdict(PASS/FAIL), reason, run_dir } × 8 ] }
```
- bad pattern: own_violations > 0 for expected_check → verdict=PASS (bad correctly triggered)
- good pattern: own_violations == 0 → verdict=PASS (good is clean)
- cross_check_counts: violations from OTHER rules (info, not fail)

## calibre deck (m1_qa_deck.cal) — 4 SVRF checks
- M1_W_1: INTernal M1 < 0.014 (width)
- M1_S_1: EXTernal M1 < 0.014 (space)
- M1_S_20: EXTernal M1_mark1 < 0.14 (mark1 space)
- M1_A_1: AREA M1 < 0.00368 (min area)
- PRECISION 10000 (match GDS dbu; 1000 会 snap 0.0139→0.014 把 bad 变 good)
- LAYER MAP 88 DATATYPE==651 → 1 (M1); 88 DATATYPE==51 → 2 (M1_mark1)

## sandbox 可行性 ✓
- **calibre on .75**: `/apps/mentor/calibre/2020.1_36/.../bin/calibre` v2020.1_36.18 ✓
- **argus on .75**: `/apps/empyrean/tools/argus/bin/argus` 2025.06.sp1 ✓
- 资产全部经 ssh 可读 (e0031982 → 10.129.8.229, file -rw-rw-r-- other-r) ✓

## case 合成计划（next round 执行）
- **case_id**: EDA-Eval-DesignFlow-DrcQaAutoPipe-001 (physical_verify, L2)
- **A-input (SUT 可见)**: bad/good_M1.A.1.json + M1_A_1_{bad,good}.gds + deck.cal + layermap
- **B-input (hidden, check.py 只跑 B)**: bad/good_M1.S.20.json + M1_S_20_{bad,good}.gds + 同 deck（deck 含 4 checks，B 用 S.20 rule）
- **任务**: 给定 M1 QA pattern JSON + GDS + calibre deck，跑 calibre -drc 生成 drc_report.json（per-rule verdict）
- **deliverable**: outputs/submit.zip 内含 drc_report.json
- **check.py ≥8 条件（草案）**:
  ① drc_report.json 存在且是合法 JSON
  ② patterns 数组长度 == B 的 pattern 数（good/bood × rule）
  ③ 每个 pattern 有 verdict/kind/rule/expected_check/check_counts 字段
  ④ bad pattern 的 own_violations > 0（对应 expected_check）
  ⑤ good pattern 的 own_violations == 0
  ⑥ check_counts 含全部 4 个 check 名 (M1_W_1/M1_S_1/M1_S_20/M1_A_1)
  ⑦ verdict == "PASS" for all（bad 触发预期 check = pass；good 干净 = pass）
  ⑧ reason 非空且含 kind 关键词（"bad pattern triggered" / "own check ... clean"）
  ⑨ total_violations == own_violations + sum(cross_check_counts.values())
  ⑩ DRC 真跑：run_dir 下有 drc.results 文件（subprocess 跑 calibre 验证）
  ⑪ B 的 expected_check == M1_S_20（非 A 的 M1_A_1，防硬编码）
  ⑫ PRECISION 10000 在 deck 中（precision 1000 会 silent pass bad as good）
- **negatives**: empty stub / print-expected-json(hardcoded A) / always-PASS-verdict / swap-good-bad
- **test_rationale**: `12 条断言：①…②…` (k=12 ≥8 ✓)

## 为什么前 92 轮漏掉此候选
- r404-r521 的 peek 集中在 **low-mc [10,100)** 候选（r507 深读 5 条 mc 97-98 全 REJECT）
- 本候选 mc=603（high-mc），不在 low-mc peek 范围
- `next` awk 排除 723 台账 session 后，此候选在 top-50 unique 第 6 位（fresh）
- **结论**: high-mc fresh 池未被系统性深扫；r507「全 mc 段 C 域饱和」结论 **仅适用于 low-mc 段**，high-mc 段有可造 case（本候选为证）

## 台账动作
- claim 1794538757522_mku3e (physical_verify, mc=603) ✓
- 下轮：合成 case → mark --status case → 追加 EDA-Eval-DesignFlow_C.jsonl
