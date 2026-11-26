# r824 调查笔记 — q1589 跨 shard 碰撞 + ec2jo 领先候选

## 本轮背景
r823 (sr0ca) 后接 r824。本轮目标 1 条 case。eda_flow session r824 open。
扫描快照: `ssh_eda_search_20261119_172105/summary.tsv` (11-19, shard A mc≥5 口径)。

## 候选搜索过程
1. mc≥5 A-domain keywords 过滤 (verilog/systemverilog/rtl/sdc/vcs/verdi/synthesis/
   dc_shell/primetime/pt_shell/formality/yosys/openroad), 排除 drc/gds/virtuoso 主导(C域)。
2. mc 8-60 区间 dedup by session → ~40 候选。
3. 交叉比对全 shard 台账 (`trace_ledger_{A,B,C,D}.tsv` 并集 3941 条 claimed)。

## 命中: q1589 (cliu @ hfhds227 / 10.129.32.111, mc59)
- keywords: lvs:760;verilog:332;transistor:42;analog:17;cadence:10 — verification 域
- trace ALIVE @ subdir-path `/home/cliu/.cline/data/sessions/1794549895955_q1589/1794549895955_q1589.messages.json` (428KB, 82 msgs, agent=lead)
- path-bug revival 第四例 (r821 4i1w4 / r822 yseg9 / r823 sr0ca / r824 q1589)
- **用户意图 (UT#5, msg78)**: 粘贴 xcelium 中断日志
  (`Simulation interrupted at 0 FS + 0` / `simlib_stdcells_ac.sv:18764` /
   `SIGTERM from ... sbatchd` / `total: 13:50:45` / `SHM limit reached` /
   `PRQASL: Queue probe ... dft_table limited`) 问「仿真不结束是什么原因」
- **trace agent 诊断 (msg79, ground truth)**:
  1. `0 FS + 0` + 13h50m45s wall → 仿真时间冻结在 0, delta 周期空转
  2. `simlib_stdcells_ac.sv:18764` → 卡在标准单元 AC(模拟)行为模型, 零延迟组合反馈环
  3. `SIGTERM from sbatchd` + `total: 13:50:45` → LSF 墙钟上限强杀, 非设计 $finish
  4. `SHM limit reached` / `PRQASL dft_table` → 次要噪音, 非不结束原因
  5. 根因: stdcell AC 模型零延迟组合反馈环 → 事件驱动仿真器 0fs 无限空转
  6. 修复: 打断组合环加 #1 延迟 / xrun 报 comb loop 选项 / 加时间上限兜底 / 检查误映射自振荡
- **判定**: 完美 S5 analysis-Q&A 料 (verification 域, 单轮, 静态报告 + specificity oracle)

## 碰撞 (关键)
- `trace_ledger.py --shard A claim` REFUSED: q1589 已在台账
- 全 shard 查: **shard D 已造 case `EDA-Eval-DesignFlow-SimFailTimeoutDiagQA-001` (2026-11-16)**
  + shard B 2026-11-14 parked (note: cross-domain shard A)
- 即同一 session 同一意图(仿真不结束/timeout 诊断)已被 D 线占用。
  🚫 不重复造。**放弃 q1589**。
- 教训: 选料前必须先全 shard 台账并集查重 (本机 `cat trace_ledger_*.tsv|cut -f1|sort -u`),
  不能只查本 shard。q1589 在 A 台账为空但 D 台账已 case。

## mc 8-60 A-domain 候选饱和度
- 40 候选交叉全 shard 台账: **绝大多数已 claimed** (A/B/C/D 并集 3941 条)
- 未 claimed 仅 4 条, 全部跨域 (B/C 主导):
  - ec2jo (chengk@hfeg0pkn002, mc58): pyaether:213;rtl:135;aether:85 — 混合 A/C, rtl 偏 digital
  - 4w3lo (e0039786@hfeg0pkn005, mc58): pyaether:109;netlist:90 — C 域
  - qlvo2 (kevin3d@hfeg0pkn004, mc56): netlist:356;analog:109;hspice:19 — B 域 spice
  - vyxnz (chuanqiz@hfeg0pnd001, mc55): analog:375;netlist:171 — B 域 spice
- 结论: mc≥8 60 上限区间 A-pure 候选确证枯竭 (与 r761/r760 A-pure 枯竭终证一致,
  本轮用 11-19 新快照 + 全 shard 并集复查再次确证)。

## ec2jo 领先候选 (下轮 lead)
- session: `1795068626907_ec2jo` (chengk @ hfeg0pkn002 / 10.129.2.11, mc58)
- trace ALIVE @ **flat-path** `/home/chengk/.cline/data/sessions/1795068626907_ec2jo.messages.json`
  (非 subdir, ls 确认 flat 路径存在)
- keywords: pyaether:213;rtl:135;aether:85;cellview:40;virtuoso:23 — rtl:135 是 A 域 digital 信号
- 未在任一 shard 台账 → 可 claim
- **下轮**: claim ec2jo → 深读 (rtl:135 + pyaether:213 混合, 需判断用户意图是否 A 域 digital
  还是 C 域 layout-driven-RTL; 若 A 域则造, 若 C 域则 park 交 C 线)
- 注意: pyaether/aether/cellview/virtuoso 占比不低, 可能实为 C 域 (layout) 任务。
  若深读后确为 C 域, 不可强造 A 域 case (违任务初衷第 1 条)。

## 本轮处置
- 0 case 产出 (q1589 碰撞放弃 + mc≥8 A-pure 枯竭 + 时间预算耗尽)
- DEBT: 下轮 (a) ec2jo 深读判定 A/C 域归属 → 若 A 则造题;
  (b) 若 ec2jo 仍 C 域, 转向 mc≥5 全 shard 并集未 claimed 候选扫一遍 A 域 keywords 主导者;
  (c) r528 subdir-path parked 剩余 A-pure (06htj 4.8MB pnr / w4uy2 1.5MB pnr) 续审 (pnr=A域)
- eda_flow session r824 待 close
- 不强行用跨域候选凑 A 域 case (守任务初衷第 1 条: 真实意图 = 唯一来源)
