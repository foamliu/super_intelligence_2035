# r1147 (2026-11-24) — §4.9 governance 轮 · DutyOffsetAlertMaxProduce-001 reference 重建

## 背景
r1144 phantom-revival 恢复 30 条 jsonl-era phantom case → `cases/B/<id>.json`，其中 13 条从未有 `reference/EDA-Eval-DesignFlow-<id>/` 目录（git 历史 0 commits 确认）。r1145 重建 ResCornerTempSweep-001（13→12），r1146 重建 TieJitterIncGenProduce-001（12→11）。本轮按 `test` 字段长度升序重建下一条：**DutyOffsetAlertMaxProduce-001**（test=10790B，11 条中最短）。

fresh B-spice 池仍耗尽（r1125/r1126/r1131/r1143/r1145/r1146 六轮 reconfirm），最新 scan 仍 ssh_eda_search_20261124_023802（r1110 起未变）。按 TASK §「止损 → 转 §4.9 自治」执行 governance。

## case 概要
- task_id: EDA-Eval-DesignFlow-DutyOffsetAlertMaxProduce-001
- domain: spice_sim / L1 纯 Python 复刻
- trace_source: terrytao @ hfeg0plg74 / session 1794813983875_1xu8a / mc9 / scan ssh_eda_search_20261121_151844
- 真实任务: terrytao 在 DDR PHY cspad timing 仿真后处理，要求把 `cspad_duty.mt0` 中 dutyout 列按 pduty 减去对应 offset（pduty=0.3→减0.7，0.5→减0.5，0.7→减0.3，即 offset=1-pduty），取绝对值，按 alter# 分组取每 alert 最大值，乘 multiplier。本 case 取 sub-task 1（msgs 0-45）做 Python L1 复刻。
- A spec: pduty ∈ {0.3, 0.5, 0.7}, offset_map {0.3:0.7, 0.5:0.5, 0.7:0.3}, multiplier=454, 9 alters
- B spec（hidden）: pduty ∈ {0.4, 0.6}, multiplier=300, 7 alters
- check(): 12 条独立断言 (a-l)，oracle-based，只跑 B
  - (a) zip+size>200+py_compile  (b) B exit0+JSON 产生  (c) 顶层键 {alerts,multiplier,n_alerts}
  - (d) n_alerts==B 实际 alter 数(7)  (e) 每 alert 含 {alter,temper,max_raw,max_multiplied,max_row}+max_row 子字段
  - (f) max_raw==oracle 复算(abs(dutyout-offset_map[pduty]) per alter 取 max, 容差 1e-9)
  - (g) max_multiplied==max_raw×mult_B(300)  (h) max_row 一致(offset==spec_B[pduty] 且 |dutyout-offset|==max_raw)
  - (i) 所有 max_raw>=0  (j) anti-hardcode: A 的 pduty(0.3/0.5/0.7)+A 的 multiplier(454) 缺席; B 的 pduty(0.4/0.6)+B 的 multiplier(300) 在场
  - (k) 分组正确: 每 alert 的 max_row.index 在原始 .mt0 中属于该 alter  (l) 3-seed(PYTHONHASHSEED=1/2/3) 输出 sha256 一致

## 重建内容
`reference/EDA-Eval-DesignFlow-DutyOffsetAlertMaxProduce-001/`：
1. **check.py** — 从 case JSON `test` 字段逐字节拷出（Python `t==d['test']` True；10790 chars）
2. **duty_offset_alert_max_ref.py** — 参考解：
   - `parse_mt0()` 跳过 `$DATA1`/`$.tri` 等 `$` 头行，找列名行后读数据行
   - `fmt_pduty()` `%.1f` 规范化 pduty 字符串（匹配 spec key 形式）
   - `compute()` 对每行：`offset = pduty_offset_map[fmt_pduty(pduty)]`, `processed = abs(dutyout - offset)`；按 alter# 分组取 max(processed)；输出 alerts（按 alter 升序）+ multiplier + n_alerts
   - CLI: `--mt0 <path> --spec <path> --out <path>`
   - 纯 stdlib，确定性
3. **negative/neg_empty.py** — 空壳（仅 pass）→ 不写 .py 实质内容 → (a)/(b) FAIL
4. **negative/neg_print_only.py** — 硬编码 A 结果（5 alters/pduty 0.3,0.5,0.7/multiplier 454）写 JSON → (d) n_alerts=5≠7 + (j) A pduty 在场+multiplier=454 FAIL
5. **negative/neg_core_deleted.py** — 删核心：正确 parse .mt0 但取 max(dutyout) 直接，无 offset 减法无 abs → (f) max_raw != oracle FAIL
6. **negative_selftest.py** — top-level harness：build submit.zip（ref / 3 neg）→ run check（returncode==0 为 PASS，check.py raise 即 FAIL）；ref 必 PASS / 3 neg 必 FAIL / 3-seed(PYTHONHASHSEED=1/2/3) ref 输出 JSON sha256 一致

## 自验结果
```
PASS: ref -> CHECK PASS
PASS: 3-seed ref deterministic (dd25e29fdf91)
PASS: neg_empty -> FAIL as expected
PASS: neg_print_only -> FAIL as expected
PASS: neg_core_deleted -> FAIL as expected

ALL SELFTEST OK: ref PASS + 3 negs FAIL + 3-seed stable
```
- check.py == case JSON `test`（Python str ==，逐字符）✓
- 3-seed 随机化：hidden B 固定输入，ref 输出 JSON sha256 三次一致（dd25e29fdf91...）✓
- §4.9 三假（空壳/print-only/删核心）全 FAIL ✓
  - neg_empty → FAIL@b（output JSON not produced）
  - neg_print_only → FAIL@d（n_alerts=5≠7）+ FAIL@j（A pduty+multiplier 454）
  - neg_core_deleted → FAIL@f（max_raw != oracle）
- 退化提交回归：三种假提交全部 FAIL ✓

## 进度
- 11 无 refdir → 10 无 refdir（DutyOffsetAlertMaxProduce 闭合）
- 剩余 10 条：CornerBlockGenProduce(12587B) / DividerNetlistRolePatch(11438B) / DsimSkillLogAnalyzer(16552B) / DualRatePwlClockGen(14074B) / JitterDutyBlockPwlGen(11849B) / MosComparaReportGen(12451B) / ProbeCovAnalyzerProduce(12306B) / SigmaflagEffectAnalyzerProduce(13565B) / TrimSkewIncrementProduce(12251B) / UlvtGmCharAnalyzer(13786B)
- B §4.9 覆盖：本轮 +1 → 10 条仍缺

## 台账
不变（1769：case 597 / parked 1172 / claimed 0）。本轮为 reference 重建，不新增 ledger case 行。
- 📊 covered=597/4529=13.2%（mc≥10，不变）
- 🎯 最近20条 20/20=100%（观察值，本轮未 pi 实跑）
- 📦 MEMORY_B 待刷
- DEBT: 10 条无 refdir case 待重建

## 动作
- 不 claim / 不 park（无新候选核验，fresh 池耗尽 reconfirm）
- 写本 deepread + 刷 MEMORY_B 首行 + 追加 daily_B_2026-11-24.md
- 双仓提交

## 下一步
1. 继续 §4.9 governance：按 test 长度升序逐条重建剩余 10 条 refdir（DividerNetlistRolePatch 11438B 次之，其次 JitterDutyBlockPwlGen 11849B）
2. 等待新 scan 注入后再恢复选料造新 case
