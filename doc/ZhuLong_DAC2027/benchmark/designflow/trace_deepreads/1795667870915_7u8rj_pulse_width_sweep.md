# deepread — 1795667870915_7u8rj (hhao, hfeg0plg101) — swept 波形脉宽提取

- trace: `1795667870915_7u8rj.messages.json` (199 msgs, 4 real user_input blocks)
- host: hfeg0plg101 (fresh pool; summary.tsv stale=hfeg0plg07)
- user: hhao
- mc: 215 (hspice:513 / netlist:368 / spectre:138 / waveview:91)
- claim → case: `EDA-Eval-DesignFlow-PulseWidthSweepExtract-001` (shard B, spice_sim)
- 状态: case done (r1408)

## 真实任务
hhao 在 hfeg0plg101 上用 WaveView Tcl ACE 从 HSPICE `.tr0` swept transient 波形里
提取信号脉宽。两条 Copy：
- **CopyA** `pcaoutt` — `long1` mode, vddq=1.1, threshold=0.55, tck=300ps, **starts LOW**,
  稳定 HIGH 宽度=300ps, offset=80, sweep n=2..10。
- **CopyB** `net028` — `long0` mode, vddq=1.2, threshold=0.6, tck=400ps, **starts HIGH**,
  稳定 LOW 宽度=280ps, offset=60, sweep n=2..10。

助手工具链：waveview-fsdb-reader 读 `.tr0` → 按阈值检测上升/下降沿 → 按信号起始电平
配对 HIGH/LOW 脉宽 → 输出每 sweep 宽度/周期/占空比。

## reframe（可移植抽象）
纯 Python 从 swept 波形 CSV（`sweep,time,voltage`）+ spec.json 提取脉宽，无
WaveView/HSPICE 二进制依赖。judge host 直接 subprocess 跑候选于隐藏 B（CopyB）与
公开 A（CopyA），逐条件比对 start_state / 宽度 / 周期 / 占空比。

- L1 judge-run（pure-python，无 EDA simulator）
- LIVE-NA（无 live eval）
- judge_layers = [L0, L1]

## 核心有牙 gotcha
**信号起始电平决定 HIGH/LOW 配对**：
- starts LOW（首采样 < threshold）：沿序 rise→fall ⇒ HIGH = fall[k]-rise[k],
  LOW = rise[k+1]-fall[k]。
- starts HIGH（首采样 >= threshold）：沿序 fall→rise ⇒ LOW = rise[k]-fall[k],
  HIGH = fall[k+1]-rise[k]。

朴素「默认 starts LOW」的解法在 CopyB（starts HIGH）上 start_state 报错 + HIGH/LOW
配对互换 ⇒ cond d (start_state=="high") + e/f (宽度) 双重 FAIL。

## A/B 全不同（token-structurally 不相交）
| 维度 | A (CopyA) | B (CopyB) |
|---|---|---|
| mode | long1 | long0 |
| vddq | 1.1 | 1.2 |
| threshold | 0.55 | 0.6 |
| tck | 300ps | 400ps |
| 起始电平 | LOW | HIGH |
| 稳定边 | HIGH=300ps | LOW=280ps |
| offset | 80 | 60 |
| n=2 period | 600 | 800 |
| n=2 duty_high | 50.0% | 65.0% |

## 判分器（check.py, 16 断言）
- a 静态 zip 顶层含 pulse_width.py + py_compile
- c L1 B 跑出 report.json + n_sweeps==9（**c 先于 sa**：空壳 -> c）
- sa 静态源码含 threshold 跨阈比较([<>]) + 'high'/'low' start_state 分支（only-add, OR；
  has_cmp 用 `[<>]` 排除 `__name__=="__main__"` 的 `==`；has_thr/has_cmp 在
  string-stripped src 上审以排除 docstring `->` 与 dict-key 污染；has_high/has_low 在
  comment-stripped src 上审以保留 start_state 字面量）
- d L1 B n=2 start_state=="high" [neg]
- e/f/g/h/i/j L1 B 宽度/周期/占空比 [neg]
- k/l L1 cross-input A start_state=="low" + high_width≈300 [neg]
- m L1 anti-leak B report 无 A-only 宽度 300.0 [neg]
- n L1 anti-hardcode 源码(剥注释/字符串)无 A-only 字面量 [neg]
- o L1 确定性 B 重跑字节一致
- p L1 fallback 空 CSV -> rc!=0 或 n_sweeps==0 [neg]

## §4.9 三假 first-fail distinct（negative_selftest.py 验证 PASS）
| negative | first-fail | 原因 |
|---|---|---|
| naive_empty | c | 空壳不产 report.json |
| naive_print_gold | sa | 罐头打印 B 无真实 threshold 跨阈比较（docstring `->` 已被 string-strip 排除） |
| naive_core_deleted | d | 解析波形但硬编 starts low，在 B(starts high) start_state 错 |
| naive_hardcode_a (extra) | d | smart-hardcode：解析波形(过 sa)但覆写 A-style starts low+300.0 |

trio = {c, sa, d} distinct ✓

## 资产
- `assets/<CID>/waveform_A.csv` (6571 行) + `spec_A.json` + `task_brief.md`
- `assets/<CID>/hidden/waveform_B.csv` (8713 行) + `spec_B.json` + `hidden_manifest.json`
- GT 生成脚本：`/nasdata/app.e0031982/.cache/scratch/gen_pulse.py`（含 B_GT/A_GT 表）
- reference: `solve.py` (= pulse_width.py) + `reference_submit.zip` + 4 negatives + selftest
