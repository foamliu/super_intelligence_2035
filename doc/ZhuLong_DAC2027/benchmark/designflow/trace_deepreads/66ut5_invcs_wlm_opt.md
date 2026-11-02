# 深读：1791960706202_66ut5 — invCSx1_test W/L/M 联合优化 + FineSim 仿真

- **session**: `1791960706202_66ut5.messages.json` · user `haifengf` · host `hfeg0pkn002` · mc=301
- **keywords**: waveview:860;netlist:570;synopsys:283;schematic:268;hspice:82;virtuoso:81;cellview:57;pyaether
- **trace 位置**: `/home/haifengf/.cline/data/sessions/1791960706202_66ut5/`（401 msgs）
- **真实产物**（`/home/haifengf/opt_invcs/`，已 scp 关键文件到沙盒 `art66/`）:
  - `optimizer.py` 9KB（grid + coordinate descent + 报告）
  - `netlist_gen.py` 4.5KB（FineSim/HSPICE .sp testbench 生成：PULSE 源 + .tran + .measure delay/power/duty）
  - `finesim_runner.py` 8.4KB（批量跑 + .mt0 解析）
  - `invcs_config.py` 5.4KB（所有参数集中：VDD=1.1, CLOAD=10fF, 5GHz/200ps, 20-80%rise=20ps→33.33ps full-swing, LMIN=39nm, delay<20ps, power<100uA, duty 50±5%）
  - `optimization_results.csv` / `optimization_summary.txt`（**真实 FineSim 跑全部 rc=1 失败**「No feasible design found」——环境/license 问题，非 harness bug）
  - `runs/cand00..cand37/`（38 个候选目录，均仿真失败）
  - `invCS_apply_design.il` 2.9KB（SKILL 回写最优解到原理图）

## 用户真实意图（A 档逐字，仅掩码）

1. U[0]「电路优化」
2. U[23]「drvsa_haifengf/invCSx1_test/schematic」
3. U[49]「/proj/drvsa/V0/workdir/haifengf/drvsa_haifengf」
4. U[91]「1. W/L/M一起调  2. 优化延迟小于20ps，功耗小于100uA，用Fineim来跑」← **核心需求轮**
5. U[173]「LMIN=39nm, VDD=1.1V, CLOAD=10fF,把duty cycle也优化到50%附近」
6. U[229]「输入为5GHz方波，20%～80%上升下降沿为20ps」
7. U[241]「1、/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim  2、ntn/ptn」
8. U[399]/U[400]「aether环境中怎么回写最优解至真实原理图」

> A 档任务说明候选 = U[91]+U[173]+U[229]+U[241]（提出需求/给约束，未指出根因）。本轮做 B 档（synthesized）。

## assistant 工具链（真实）

- list_allowed_files / read_files 探测项目 + sch.oa（提取实例 I0/TECHLIB/inv WP=1.48 WN=0.74 LP=0.075 LN=0.07；Iinv_0/invPF；I_invCS_0/invCS）
- 读 FineSim 模型 `V2_HK_Model_D5_v0d5_Rev07_relia.sp`（corner mosra_mos_tt/ff/ss/fs/sf，器件 ntn_mra/ptn_mra）
- 读现成 MatrixRun 模板 + getIDD_DRGQA.pl（学习 .measure delay/power 写法）
- 写 Python harness：netlist_gen（.sp 生成）+ finesim_runner（批量跑 + .mt0 解析）+ optimizer（grid+coord descent）+ invcs_config（参数集中）
- selfcheck + mock_run 验证（mock 下找到 feasible: Wp=0.455um Wn=0.300um L=28nm M=8 delay=19.88ps power=90.55uA）
- **真实 FineSim 跑全失败 rc=1**（环境/license），故真实 csv 全空，summary 报「No feasible design」
- 写 SKILL 脚本 invCS_apply_design.il 回写最优解

## 关键事实（断言只对这些）

- **设计**：CMOS 反相器 testbench（PMOS MP1: vdd-Y-A-vdd；NMOS MN1: Y-A-0-0），输出节点 Y，负载 CL
- **.sp 结构**：`.option search=<model_dir>` + `.lib '<MODEL_SP>' <corner>` + VDD/VSS + VIN PULSE + CL + MP1/MN1 + `.tran` + 6 条 `.measure`（t_hl/t_lh/t_max/i_vdd/t_high/t_per/duty_pct/delay_ps/idd_ua）
- **20-80% rise=20ps → full-swing TRISE=20ps/0.6=33.333ps**（关键换算）
- **5GHz 方波 → TPERIOD=200ps，PULSE 高电平=100ps**
- **delay = max(t_hl, t_lh)，50% VDD(=0.55V) trig/targ**
- **power = avg I(VDD) over [PWR_START, PWR_STOP] × 1e6 → uA**
- **duty = (t_high/t_per)*100，t_high=Y 在 50%VDD 上一周期的 high 脉宽，t_per=两连续 rise 间隔**
- **约束**：delay<20ps, idd<100uA, |duty-50|≤5%；LMIN=39nm
- **gold harness = netlist_gen.py + finesim_runner.py + optimizer.py + invcs_config.py**（结构正确；真实 sim 失败是环境问题，harness 本身经 mock 验证逻辑正确）

## 合成方案（B 档 synthesized · L1 离线 .sp 解析 + subprocess 候选）

- **任务说明**：B 档 task_brief——为 invCSx1_test 构建 W/L/M 优化 harness（gen_opt_deck.py 生成 FineSim .sp + parse_meas.py 解析 .mt0 + optimize_invcs.py 网格搜索 + best_design.json + report）
- **A 附件**：`design_spec_A.json`（spec: delay<20ps power<100uA duty50±5 VDD=1.1 CLOAD=10fF 5GHz 20-80%rise=20ps LMIN=39nm models）+ `example_deck_A.sp`（参考 .sp 样例，真）+ `example_mt0_A.txt`（参考 .measure 报告样例，A 真值: delay=18.5ps idd=92uA duty=49.2）+ `task_brief.md` + `prompt.txt`
- **隐藏 B**（不进 SUT 沙箱）：`design_spec_B.json`（结构性不同: delay<15ps power<80uA 10GHz CLOAD=5fF VDD=0.9 20-80%rise=15ps→25ps full-swing）+ `example_mt0_B.txt`（B 真值: delay=12.3ps idd=68uA duty=48.7）+ `hidden_manifest.json`
- **交付契约**：`outputs/submit.zip` 含 `gen_opt_deck.py` + `parse_meas.py` + `optimize_invcs.py` + `best_design.json` + `optimization_report.txt`
- **check.py 17 条独立标签 (a)-(q)**：
  - (a) zip 5 文件齐全
  - (b) py_compile 三个 .py
  - (c) gen_opt_deck CLI 跑通产出 .sp 文本
  - (d) .sp PULSE 源 20-80%→33.33ps full-swing rise/fall（容差）
  - (e) .sp 5GHz→TPERIOD=200ps（PULSE 高电平=100ps）
  - (f) .sp VDD=1.1
  - (g) .sp CLOAD=10fF
  - (h) .sp .measure delay t_hl/t_lh 50%VDD=0.55 trig/targ
  - (i) .sp .measure i_vdd AVG I(VDD)
  - (j) .sp .measure duty t_high/t_per→duty_pct
  - (k) .sp L≥39nm（A design point l_nm=39）+ .tran 存在
  - (l) .sp .measure delay_ps/idd_ua 派生量
  - (m) parse_meas subprocess 跑 example_mt0_A → 提取 delay/idd/duty 容差内
  - (n) parse_meas subprocess 跑 example_mt0_B → 提取 B 值容差内（跨输入）
  - (o) gen_opt_deck 跨输入 B spec → .sp 含 TPERIOD=100ps / VDD=0.9 / CL=5fF / rise=25ps（杀 A 硬编码）
  - (p) best_design.json 结构字段齐全 + feasible=True + delay<20 + idd<100 + duty∈[45,55]
  - (q) 随机化: gen_opt_deck 同参 3 次输出一致（确定性）+ parse_meas 打乱 .mt0 行序 3 seed 提取值一致
- **negative**：3 §4.9 假 + 2 naive
  - fake_empty_shell → a
  - fake_print_expected（硬编码 A 的 best_design.json + 打印 example_deck_A.sp 文本）→ o（B spec 下 deck 仍是 A 的 200ps/1.1V）
  - fake_core_deleted（gen_opt_deck 返回空串）→ d/h
  - naive_no_duty_measure（缺 .measure duty）→ j
  - naive_hardcode_a_period（硬编码 TPERIOD=200ps）→ o
- **L1 判分**：offline 静态 .sp 文本解析 + subprocess 跑候选 gen_opt_deck/parse_meas（无 EDA 工具，无需真实 FineSim）。难度由 20-80%→full-swing 换算 + 5GHz 周期 + 跨输入 B + duty 测量语义拉到合理水平。

## 难度（B 档目标 20–30%）

L1 但 EDA 知识密集（FineSim .measure 语法、20-80% rise 换算、duty 测量拓扑）+ 跨输入 B + 随机化 + ≥17 独立条件。A 档试点另轮。
