# 深读笔记：1793012967002_19y5l — HSPICE 瞬态支路电流测量 deck 生成器

- trace: 1793012967002_19y5l.messages.json
- user: thqu @ hfeg0plg99
- match_count: 78, domain: spice_sim
- 交付 case: **EDA-Eval-DesignFlow-InstCurrentMeasGen-001**（spice_sim, B档 synthesized, L2 真跑 HSPICE, k=15）
- 关联旧探索笔记：`1793012967002_19y5l_probesyntax_xprobe.md`（早期 reframing 候选 ProbeSyntaxFix-001，最终未采用——本笔记为最终交付版本）

## 真实流（trace 摘要）
- thqu 单轮纯 spice 意图：「HSPICE 瞬态仿真里 `.probe i(*)` 只会给出电压源的电流，拿不到电阻/MOS 器件支路电流，怎么测每个器件的支路电流」
- agent 给出方案：用 `.measure tran <name> avg i(<具名器件>)` 而非 `.probe i(*)` 抽取支路电流
- A 档合规（用户提出需求未给修复方向），但 trace 末轮无显式用户接受 → B 档 synthesized（提取「支路电流测量 deck 生成器」子技能为可运行 artifact）

## 子技能（distinct ✓）
- **instance-branch-current measurement deck generator/runner**
- shard B 首个此子技能：
  - CmdEdgeMeasGen = edge 时间测量（.measure when v() rise=N）
  - McFailModeDiag = MC run 失败分类（静态日志）
  - FineSimWorkflow = 多分析运行器（DC/Tran/AC）
  - NetlistTranDeck = 网表 + .measure 拼接静态生成（无 per-instance i(inst) 支路电流抽取）
  - 本条 = **per-instance `i(<inst>)` .measure 合成（反 `.probe i(*)` v-src-only 陷阱）+ HSPICE 实跑 + .mt0/.lis 解析 + name-agnostic 跨 DUT 复用**

## 便携 reframe
- trace 原 hspice 痛点直接可便携 .75 HSPICE V-2023.12-SP1-1
- DUT 用 level-1 Shichman-Hodges 偏置/参考网络（命名电阻 r_* + MOS mn_*，.model nch_a nmos level=1 vto=0.7 kp=50u nsub=1e16 u0=600 tpg=1 lambda=0.05 防 nsub<=ni abort）

## .75 可行性 probe（已验证）
- `.measure tran <name> avg i(<inst>)` 在 HSPICE V-2023.12-SP1-1 可用，产干净 .mt0（deterministic，重跑 byte-identical）
- `.probe i(*)` 对照实测：只产独立电压源电流，电阻/MOS 器件支路电流缺失 → 印证 trace 痛点

## GT 标定（.75 HSPICE, deterministic）
- **A**（vdd=1.2, 5 insts: r_vdd_div_a/r_gnd_div_a/r_bleed_a/mn_drv_a/mn_sw_a, vgg pulse nga v0=0/v1=1.2/td=1n/tr=100p/tf=100p/pw=2n/per=5n, tran tstep=10p tstop=5n, measure_type=avg）
  - r_vdd_div_a = 100.0000u
  - r_gnd_div_a = 100.0000u
  - r_bleed_a   = 24.0000u
  - mn_drv_a    = 59.365u
  - mn_sw_a     = 35.7046u
- **B**（hidden, vdd=1.5, 4 insts: r_pull_b/r_sink_b/r_load_b/mn_act_b, 不同拓扑/命名/数值/supply_node/gate_node）
  - r_pull_b  = 83.3333u
  - r_sink_b  = 83.3333u
  - r_load_b  = 45.4545u
  - mn_act_b  = 144.3875u

## 候选 inst_current_meas_gen_ref.py
- CLI: `<dut_netlist.sp> <spec.json> <out_dir>`
- 流程：build_tb（`.inc <dut>` + vdd vsource + vgg pulse from spec + `.tran` + per-target `.measure tran <name> avg i(<inst>)`）→ subprocess `hspice -i tb.sp -o run` → parse .lis .measure 表 + .mt0 header/数值行 → currents_report.json + currents.csv
- report schema: {analysis, measure_type, instances[{name,current,measure_type}], converged, hspice_ran, mt0_path, sim_log_path, deck_path, n_targets}
- zip arcname = `inst_current_meas_gen.py`（disk 文件名 inst_current_meas_gen_ref.py）

## check.py 15 条（a-n + c-concluded）
- (a) zip 含 inst_current_meas_gen.py
- (b) py_compile 通过
- (c) hspice_ran=true
- (c-concluded) run.log 含 'job concluded'（反仿真未结束/被中断）
- (d) converged=true 且无 'job aborted'
- (e) 4 insts 全非空
- (f) r_pull_b = 83.3333u ±5%
- (g) r_sink_b = 83.3333u ±5%
- (h) r_load_b = 45.4545u ±5%
- (i) mn_act_b = 144.3875u ±8%（MOS 脉冲平均，容差更宽）
- (j) deck 含 `.measure tran avg i(r_pull_b)` 或 `i(mn_act_b)` 非 .probe i(*)(**trace 痛点核心断言**)
- (k) name-agnostic: B 名齐且 A 名不泄
- (l) 跨输入守卫: rerun A, r_bleed_a = 24u ±5%
- (m) 确定性: rerun B, 各器件电流 2% 内
- (n) 物理合理: 0 < I ≤ 0.5mA（vdd_B=1.5, min_R=3k）

## 6 negatives + §4.9 三假（全 FAIL, distinct 6/6）
- naive_empty → b
- naive_print_expected → c-concluded
- naive_no_rerun → c
- naive_hardcode_a → f
- naive_probe_star → j（用 `.probe i(*)` 代替 `.measure i(inst)`，正是 trace 痛点反例）
- fake_core_deleted → e
- §4.9 三假：空壳=naive_empty / print-expected=naive_print_expected / 删核心=fake_core_deleted，全 FAIL

## .75 端到端 selftest 结果
- ref **PASS 15/15** + 6 neg 全 FAIL 互异（distinct 6/6）
- 断言闸门 k_rationale=k_check=15 ≥ 8 GATE PASS
- test==disk check.py byte-synced（6518B）
- jsonl_B 69→70 行

## 教训
1. HSPICE `.probe i(*)` 只产独立电压源电流，电阻/MOS 器件支路电流必须 `.measure tran avg i(<具名器件>)`（trace 痛点 → check.py (j) 核心断言）
2. level-1 MOS 须 nsub=1e16+u0=600+tpg=1 防 `nsub<=ni` abort
3. .mt0 表头/数值行两行格式 + .lis .measure 表双重解析冗余防伪造
4. MOS 脉冲平均电流容差 ±8%（比电阻 ±5% 宽，因 pulse avg 对 trap 数值敏感）
5. naive_probe_star 用 `.probe i(*)` 代替 `.measure i(inst)` 被 (j) 捕获——正是 trace 痛点的反例，case 设计闭环
