# r1145 (2026-11-24) — 0-case stop-loss + §4.9 governance 轮 · ResCornerTempSweep-001 reference 重建

## 背景
r1144 phantom-revival 把 30 条 jsonl-era phantom case 恢复成 `cases/B/<id>.json`，但发现其中 **13 条从未有 `reference/<id>/` 目录**（git 历史确认：13 条 reference 路径 0 commits）。这 13 条 case：
- case JSON `test` 字段（check.py）完整 ✓
- assets（含 hidden B + hidden_manifest）完整 ✓
- **但无 reference solution / 无 negative / 无 selftest** → §4.9 无法重跑

r1133 曾判「B §4.9 = 100%」，但那是在 r1144 revival 之前；r1144 引入 13 条无 refdir case 后 B §4.9 实际回退。r1144 自身把 13 条列为「遗留债务」。

fresh B-spice 池仍耗尽（r1125/r1126/r1131/r1143 四轮 reconfirm），无新 scan（最新仍 ssh_eda_search_20261124_023802，r1110 起未变）。本轮按 TASK §「止损 → 转 §4.9 自治」执行 governance。

## 本轮工作：重建 ResCornerTempSweep-001 reference dir

选料依据：13 条无 refdir case 中 `test` 字段最短（8719B）、断言数 k=12、attachments 简单（2 个 .sp + task_brief）、hidden B 已存在。

### 重建内容
`reference/EDA-Eval-DesignFlow-ResCornerTempSweep-001/`：
1. **check.py** — 从 case JSON `test` 字段逐字节拷出（`t==d['test']` True）
2. **res_corner_temp_sweep_ref.py** — 参考解：
   - parse_sp() 解析 `.sp` 头部 `* KEY VALUE` 注释（PROCESS/CORNERS/TREF/TC1R/TC2R/L/W/NM/WEFF_OFF/PVDD）
   - 解析电流 I(T,corner)=PVDD/(rsh*leff/weff*nm * (1+(T-TREF)*TC1R+(T-TREF)^2*TC2R))，tt/ss/ff × -40..130 step10（18 点）
   - 写 out.json（process/corners/temps/currents）
   - 纯 Python PNG 编码器（struct+zlib，无 matplotlib/PIL 依赖）生成 plot_v1/plot_hl22/plot_compare.png（240×160 + 背景抖动确保 >500B）
3. **negative/neg_empty.py** — 空壳，不写 out.json → check (c) FAIL
4. **negative/neg_print_only.py** — print 期望结构但写残缺 out.json（缺 corners/temps/currents）→ check (e) FAIL
5. **negative/neg_core_deleted.py** — 删核心温度系数 rt，R=rseg 常量 → check (h) 值不符 + (j) 单调性 FAIL
6. **negative_selftest.py** — harness：build submit.zip（ref + 3 plots）→ run check；ref 必 PASS / 3 neg 必 FAIL / 3-seed sha256 一致

### 自验结果
```
PASS: ref -> CHECK PASS
PASS: 3-seed ref deterministic (3de40750f038)
PASS: neg_empty -> FAIL as expected
PASS: neg_print_only -> FAIL as expected
PASS: neg_core_deleted -> FAIL as expected
ALL SELFTEST OK: ref PASS + 3 negs FAIL + 3-seed stable
```
- check.py == case JSON `test`（逐字节）✓
- 3-seed 随机化：hidden B 固定输入，ref 输出 out_v1.json sha256 三次一致 ✓
- §4.9 三假（空壳/print-only/删核心）全 FAIL ✓

## 进度
- 13 无 refdir → 12 无 refdir（ResCornerTempSweep 闭合）
- B §4.9 覆盖：r1144 后回退到 (597-13)/597；本轮 +1 → 12 条仍缺

## 台账
不变（1769：case 597 / parked 1172 / claimed 0）。本轮为 reference 重建，不新增 ledger case 行。
- 📊 covered=597/4529=13.2%（mc≥10，不变）
- 🎯 最近20条 20/20=100%（观察值，本轮未 pi 实跑）
- 📦 MEMORY_B 待刷
- DEBT: 12 条无 refdir case 待重建（CornerBlockGenProduce / DividerNetlistRolePatch / DsimSkillLogAnalyzer / DualRatePwlClockGen / DutyOffsetAlertMaxProduce / JitterDutyBlockPwlGen / MosComparaReportGen / ProbeCovAnalyzerProduce / SigmaflagEffectAnalyzerProduce / TieJitterIncGenProduce / TrimSkewIncrementProduce / UlvtGmCharAnalyzer）

## 动作
- 不 claim / 不 park（无新候选核验，fresh 池耗尽 reconfirm）
- 写本 deepread + 刷 MEMORY_B 首行 + 追加 daily_B_2026-11-24.md
- 双仓提交

## 下一步
1. 继续 §4.9 governance：按 test 长度升序逐条重建剩余 12 条 refdir（TieJitterIncGenProduce 10180B 次之）
2. 等待新 scan 注入后再恢复选料造新 case
