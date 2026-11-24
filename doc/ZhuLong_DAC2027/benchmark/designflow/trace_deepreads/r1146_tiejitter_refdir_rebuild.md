# r1146 (2026-11-24) — §4.9 governance 轮 · TieJitterIncGenProduce-001 reference 重建

## 背景
r1144 phantom-revival 恢复 30 条 jsonl-era phantom case → `cases/B/<id>.json`，其中 13 条从未有 `reference/<id>/` 目录（git 历史 0 commits 确认）。r1145 已重建 ResCornerTempSweep-001（13→12）。本轮继续按 `test` 字段长度升序重建下一条：**TieJitterIncGenProduce-001**（test=10180B，13 条中最短）。

fresh B-spice 池仍耗尽（r1125/r1126/r1131/r1143/r1145 五轮 reconfirm），最新 scan 仍 ssh_eda_search_20261124_023802（r1110 起未变）。按 TASK §「止损 → 转 §4.9 自治」执行 governance。

## case 概要
- task_id: EDA-Eval-DesignFlow-TieJitterIncGenProduce-001
- domain: spice_sim / L1 纯 Python 复刻
- trace_source: joeyl @ hfeg0pkn004(10.129.2.13) / session 1794297825345_iic1c / mc8 / scan ssh_eda_search_20261122_172249
- 真实任务: joeyl 在 `/home/joeyl/Tie_jitter/` 有 Perl 程序 `Tie_jitter.pl` 读 config 生成 HSPICE/FineSim TIE-jitter(RMS) 测量 .inc（vref_tie 理想参考时钟 + trig/targ .measure 逐沿 TIE + .measure param 内部统计 de-meaned RMS）。本 case 取核心工具做 Python L1 复刻。
- A config: 4 信号 dqs_buf_r{0,1}/f{0,1}, delay=5n, speed=2E9, count=500, vthr=0.4375
- B config（hidden）: 3 信号 xi_clk.rx_clk_{n,p} / xi_dq.dq0, delay=12n, speed=4E9, count=200, vthr='vddq/2'
- check(): 12 条独立断言 (a-l)，oracle-based，只跑 B

## 重建内容
`reference/EDA-Eval-DesignFlow-TieJitterIncGenProduce-001/`：
1. **check.py** — 从 case JSON `test` 字段逐字节拷出（Python `t==d['test']` True；10180 chars / 10182 bytes，含 1 个 UTF-8 U+201D）
2. **tie_jitter_inc_gen_ref.py** — 参考解：
   - `parse_cfg()` key=value 解析（# 注释剥离）
   - `parse_number()` 支持 HSPICE 后缀 t/g/meg/k/m/u/n/p/f/a + 科学计数法
   - `is_expression()` 判 vthr 是否表达式（非数字即表达式，.param 中用单引号包裹）
   - `signame()` = signal 最后一个 '.' 段；冲突 die
   - `gen_inc()` 生成 .inc：.param vthr/tper/t0 + vref_tie n_tie_ideal pulse(… t0 … tper …) + 每信号每沿 trig v(n_tie_ideal)/targ v(<full_sig>) .measure + tie_sum/mean_tie/per-edge tiedev+tiedev2/tiedev2_sum/tie_sqsum + rms_tie(de-meaned sqrt(tiedev2_sum/count)) + rms_tie_raw(sqrt(tie_sqsum/count))
   - CLI: `gen <config> <output>` 或 `<config> [output]`
   - 纯 stdlib，确定性
3. **negative/neg_empty.py** — 空壳，不写 .inc → (b) FAIL
4. **negative/neg_print_only.py** — print 假结构 + 写残缺 stub .inc（无 .param/vref_tie/.measure）→ (c)(d)(e) FAIL
5. **negative/neg_core_deleted.py** — 删核心：保留 .param/vref_tie/per-edge trig-targ，DROP 全部 de-meaned 统计（tiedev2_sum/rms_tie/rms_tie_raw）→ (g)(h)(i) FAIL
6. **negative_selftest.py** — harness：build submit.zip（ref / 3 neg）→ run check（returncode==0 为 PASS，check.py raise 即 FAIL）；ref 必 PASS / 3 neg 必 FAIL / 3-seed sha256 一致

## 自验结果
```
[check] 12/12 PASS
  PASS a: zip+size ok
  PASS b: B exit0 + .inc 192294 bytes
  PASS c: vthr=True tper=True t0=True
  PASS d: pulse=vref_tie n_tie_ideal 0 pulse(0 vthr t0 tper/2 tper/2 tper/2 tper)
  PASS e: trig=600 expected=600
  PASS f: all B signals in targ
  PASS g: tiedev2_sum for all 3 signals
  PASS h: rms_names=['dq0','rx_clk_n','rx_clk_p'] expected=['dq0','rx_clk_n','rx_clk_p'] rms_lines=6
  PASS i: de-meaned formula present
  PASS j: vthr_param='vddq/2' A_vthr_absent=True
  PASS k: max_idx=200 B_count=200 A500_absent=True
  PASS l: unique_hashes=1
PASS: ref -> CHECK PASS
PASS: 3-seed ref deterministic (15f4b216e336)
PASS: neg_empty -> FAIL as expected
PASS: neg_print_only -> FAIL as expected
PASS: neg_core_deleted -> FAIL as expected
ALL SELFTEST OK: ref PASS + 3 negs FAIL + 3-seed stable
```
- check.py == case JSON `test`（Python str ==，逐字符）✓
- 3-seed 随机化：hidden B 固定输入，ref 输出 .inc sha256 三次一致 ✓
- §4.9 三假（空壳/print-only/删核心）全 FAIL ✓
- 退化提交回归：空壳 FAIL@b / print-only FAIL@c,d,e / 删核心 FAIL@g,h,i ✓

## 进度
- 13 无 refdir → 11 无 refdir（TieJitterIncGenProduce 闭合）
- 剩余 11 条：CornerBlockGenProduce / DividerNetlistRolePatch / DsimSkillLogAnalyzer / DualRatePwlClockGen / DutyOffsetAlertMaxProduce / JitterDutyBlockPwlGen / MosComparaReportGen / ProbeCovAnalyzerProduce / SigmaflagEffectAnalyzerProduce / TrimSkewIncrementProduce / UlvtGmCharAnalyzer
- B §4.9 覆盖：本轮 +1 → 11 条仍缺

## 台账
不变（1769：case 597 / parked 1172 / claimed 0）。本轮为 reference 重建，不新增 ledger case 行。
- 📊 covered=597/4529=13.2%（mc≥10，不变）
- 🎯 最近20条 20/20=100%（观察值，本轮未 pi 实跑）
- 📦 MEMORY_B 待刷
- DEBT: 11 条无 refdir case 待重建

## 动作
- 不 claim / 不 park（无新候选核验，fresh 池耗尽 reconfirm）
- 写本 deepread + 刷 MEMORY_B 首行 + 追加 daily_B_2026-11-24.md
- 双仓提交

## 下一步
1. 继续 §4.9 governance：按 test 长度升序逐条重建剩余 11 条 refdir（DutyOffsetAlertMaxProduce 10790B 次之）
2. 等待新 scan 注入后再恢复选料造新 case
