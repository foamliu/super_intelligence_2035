# Deepread · z4swx · xuelianf @ hfeg0plg102 · waveform

**session**: `1794206448451_z4swx.messages.json` (242 msgs, 873KB)
**trace_source**: user xuelianf, host hfeg0plg102, mc=214 (waveform/bisec/PrimeSim markers)
**domain**: waveform (shard D)

## 用户意图
- 用户有一批 PrimeSim-SPICE 做 bisection 仿真跑出的结果目录树，每个 corner 目录下产出 `Input_D0.bisec_mt0` 与 `Input_D1.bisec_mt0` 两个结果文件。
- 每个 `.bisec_mt0` 为 4 行文本：
  ```
  $DATA1 SOURCE='PrimeSim SPICE' VERSION='U-2023.03-SP1' PARAM_COUNT=1
  .TITLE '*********************************************************PVT*********************************************************'
          vtarget        maxvout         temper         alter#
       3.4277e-01     9.2918e-01    -4.0000e+01     1.0000e+00
  ```
  **vtarget = 第 4 行第 1 列**。
- 用户要写一个 python 程序遍历整棵结果树，对每个 corner：
  - 从 `Input_D1.bisec_mt0` 取 `vtarget_D1`，从 `Input_D0.bisec_mt0` 取 `vtarget_D0`；
  - 计算 sensing margin：
    - `SM1 = (0.93*1000 - vtarget_D1*1000) * 0.156 - 36.43`
    - `SM0 =  vtarget_D0*1000 * 0.156 - 37.69`
  - 输出 CSV：`directory,vtarget_D1,vtarget_D0,SM1,SM0`（directory 相对树根，不含末尾 `/RESULT`）。
- 注意：用户原始消息里把 SM1 的 vtarget 写成 D0（笔误），但实际交付脚本 `calc_sm.py` 用的是 vtarget_D1（D1 才是 sensing margin 1 的对应条件）。本案以交付脚本为准：SM1 用 vtarget_D1。

## 真实工具链 / 产物
- agent 读取 host 上的真实 bisec_mt0 样本与目录结构（240 个 corner 目录）。
- 交付：
  - `calc_sm.py` — os.walk 遍历树，每个含 `RESULT/Input_D0.bisec_mt0`+`RESULT/Input_D1.bisec_mt0` 的目录取 vtarget（line 4 col 1），算 SM1/SM0，写 CSV（3 位小数）。
  - `calc_sm.sh` — bash 版本（awk 取第4行第1列，bc 算 SM）。
  - `calc_sm_output.csv` — 240 行结果。

## 不可复刻性 → B-grade synthesized
- 真实树在 hfeg0plg102 私有 `/rundata/...` 下（240 个 corner，真实 PVT 仿真产物），沙盒不可复刻。
- B-grade 自包含合成：
  - **可见 A 树** `sim_tree_A/`：`C_SmCC_{0,100,200}aF/group{1,2}_BL{0-3}_<8位pattern>/RESULT/Input_D{0,1}.bisec_mt0`，3 cap × 2 group × 4 BL（跳 200aF/group2/BL0）= 23 个完整 corner，全 valid。vtarget 用 `random.Random(20261110)` 生成 0.30-0.65V。
  - **隐藏 B 树** `hidden/sim_tree_B/`：`C_Sense_{50,150,250,350}fF/grp{1-3}_WL{0-3}_<8位pattern>/RESULT/Input_D{0,1}.bisec_mt0`，4 cap × 2-3 group × 4 WL = 34 完整 + 3 不完整（缺 D0 / D0 损坏 / 缺双文件），vtarget 用 `random.Random(424242)` 生成 0.25-0.70V。
  - 反硬编码：cap 前缀(C_SmCC vs C_Sense)、单位(aF vs fF)、group 命名(group vs grp)、BL/WL、pattern 集、vtarget 范围、完整/不完整分布全不同。

## 判分设计（check.py, k_check=14）
check.py 子进程真跑 SUT 脚本 on 隐藏 B + 内嵌**独立** `extract_vtarget`/`expected_for` 从 B 的 bisec_mt0 重推导期望 CSV（不信任 SUT 输出），14 条独立可分别 FAIL 的断言：
- a: submit.zip 可解压非空
- b: 含 .py/.sh + py_compile/bash -n 通过
- c: 在 B 上跑出含表头的 CSV
- d: 表头精确 `directory,vtarget_D1,vtarget_D0,SM1,SM0`
- e: 34 完整目录无遗漏
- e2: 无多余目录
- f: vtarget_D1 逐目录一致 (TOL=5e-3)
- g: vtarget_D0 逐目录一致
- h: SM1 公式逐目录一致
- i: SM0 公式逐目录一致
- j: 3 个不完整 corner 未泄漏
- k: 反硬编码 — 在 A 上重跑得 A 正确结果 + SM1 逐目录一致
- k2: A/B 输出目录名不重叠
- l: 3-seed byte-stable

## 自验
- ref solution PASS 14/14（selftest）
- §4.9 三假全 FAIL：empty→b / print_only_expected→k2 / core_deleted→c
- 4 negatives 全 FAIL：neg_empty→c / neg_print_only→e / neg_hardcode_a→e / neg_wrong_formula→h
- NEG_RC=0

## 交付记录
- case id: `EDA-Eval-DesignFlow-SmBisecMarginCalc-001`
- D.jsonl 277→278
- byte-sync sha `011ea22383` size `3562`
- 🧾 断言: k_rationale=k_check=14 ✓
