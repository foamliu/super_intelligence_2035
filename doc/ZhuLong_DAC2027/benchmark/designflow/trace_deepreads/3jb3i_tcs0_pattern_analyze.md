# Deepread: 3jb3i — tCS0 pattern analysis (memory array)

- **session**: 1793177016543_3jb3i (t0002616@hfeg0plg101, mc27, 23 msgs)
- **domain**: analog_context (memory cell SPICE sim timing analysis)
- **U#0 (verbatim, A-faithful 提需求轮, 未指出根因 ✓)**:
  「在使用第一个文件的netlist和后面的多个激励文件仿真计算tcs0的过程中，发现All0和Iso1的tcs0相较于其他的pattern格外小，分析其原因」
  附件: netlist + Ckb0.sp/Ckb1.sp/Dck0.sp/Dck1.sp/All0.sp/All1.sp/Iso0.sp/Iso1.sp (来自 session 1yxo6 uploads)

## Trace flow
- U#0 提需求 → agent read_files 读 netlist(12793行 hspice/FeRAM-like 32-cell memory array `Mat_Testbench_new2`) + 8 个 .sp 激励
- agent 写 python 分析脚本(an_net.py/summarize_patterns.py)经 python-runner profile 跑：
  - 解析 netlist `.IC V( CCxx )=KCBGyy` 行 → 8 背景 group(AA-HH)×4 cell = 32 cell 映射 (KCBGAA→CC0X ... KCBGHH→CC7X)
  - 解析 `.IC V( CCxx )=KCTyy` → target group
  - 解析每个 .sp 的 `.param KCBGxx='pvblh'`(H) / `='0'`(L) → 每 pattern 的 8 group 取值
  - target measured node = CC32 (group DD)
- 关键发现 (summarize_patterns.py 输出)：
  - **每 pattern 的 #H(高背景 group 数)**: All0=0, Iso1=1, Ckb0/Ckb1/Dck0/Dck1=4, Iso0=7
  - **tCS0 ∝ #H**: 高背景 cell 多 → 耦合电荷多 → target cell 充电到位时间短? 实为 #H 越少 tCS0 越小(All0/Iso1 是低 H 端点→格外小，非异常而是物理预期)
  - root cause: target cell 与背景 cell 间电容耦合；高背景少→耦合扰动少→settle 快→tCS0 小
- U#21「这几个pattern中最worst的该是什么情况」→ agent 答: **Iso0(7H) 最 worst(最大 tCS0)**

## Pattern 定义 (背景 KCBG，H=pvblh L=0)
| pattern | AA BB CC DD EE FF GG HH | #H |
|---|---|---|
| All0  | 0  0  0  0  0  0  0  0  | 0 |
| Iso1  | 0  0  0  H  0  0  0  0  | 1 |
| Ckb0  | H  0  H  0  H  0  H  0  | 4 |
| Ckb1  | 0  H  0  H  0  H  0  H  | 4 |
| Dck0  | H  H  0  0  H  H  0  0  | 4 |
| Dck1  | 0  0  H  H  0  0  H  H  | 4 |
| Iso0  | H  H  H  0  H  H  H  H  | 7 |
| All1  | (无 KCBG 行，跳过) | - |

target node CC32 → group DD(3)。Iso1 的 DD=H 即 target 自身背景组为 H(#H=1)。

## 金标
config-driven 通用 tcs0 分析脚本 tcs0_analyze.py：
1. 解析 netlist `.IC V( CCxx )=KCBGyy`/`=KCTyy` → cell→group 映射 + group→cells
2. 解析 stimuli `*.sp` 的 `.param KCBGxx='pvblh'|'0'` → 每 pattern 的 group H/L
3. 从 target_node(如 CC32) → group(DD)
4. 每 pattern 计算 n_high = count(H groups)
5. 按 n_high 排序 → smallest = 最小 tCS0, largest = worst
6. report: root_cause = tCS0 ∝ n_high(电容耦合), smallest/worst pattern, patterns 表
7. plan: target_node/target_group/n_groups/pattern_count/n_high_map/smallest/worst

L1-boundary: 离线静态解析(netlist+stimulus 文本)，不跑真实 FineSim，降级为通用脚本+report+plan。

## 合成计划
- **case-id**: EDA-Eval-DesignFlow-Tcs0PatAnalyze-001
- **A 档 trace-faithful**, analog_context, L1-boundary
- **资产 A**: config_A.json(8 group AA-HH, 4 cell/group, target CC32/group DD, 5 pattern: All0/Iso1/Ckb0/Ckb1/Iso0) + netlist_A(synthetic .IC lines) + stimuli_A/*.sp + prompt.txt(U#0逐字) + task_brief.md
- **hidden B**: config_B.json(6 group AA-FF, target CC50/group EE, 6 pattern: ZeroAll/IsoLow/ChkA/ChkB/IsoHigh/DiagA, 结构/取值不同) + netlist_B + stimuli_B/ + hidden_manifest.json
- **reference**: tcs0_analyze_ref.py(通用解析脚本) + build_assets.py(从 config 生成 netlist+stimuli) + reference_submit.zip(含 tcs0_analyze.py)
- **check.py 15 条件 a-o**: 见合成实现
- **negatives 5**: fake_empty(空→c) / fake_print_fixed_A(硬编 A report→h/i/j/k/n) / fake_core_deleted(删 netlist .IC 解析→d/g) / naive_no_stimulus_parse(不解析 .sp→e/f) / naive_count_wrong(只数 target group→f/i)
