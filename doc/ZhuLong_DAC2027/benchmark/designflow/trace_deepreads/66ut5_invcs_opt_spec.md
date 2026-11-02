# Deepread: 66ut5 — invCSx1 自定义反相器 W/L/M 优化（FineSim tran 表征 + spec 合规）

- **session**: 1791960706202_66ut5.messages.json
- **user/host**: haifengf @ hfeg0pkn002 (mc=301, hspice:16/netlist:260/schematic:35)
- **agent**: cline (lead), model deepseek-v4-flash, 401 msgs / 9 用户轮 / 208 tool_use
- **domain**: spice_sim → case `EDA-Eval-DesignFlow-InvOptSpec-001` (L2, track B synthesized)
- **status**: session failed (terminal_marker failed_external_process_exit) — 但工具链与 spec 完整可复现

## 用户意图（9 轮真实需求演进）
1. U[0]（原话）:「电路优化」(提出需求轮 ✓ A档候选)
2. U[23]: 「drvsa_haifengf/invCSx1_test/schematic」(指向自定义反相器 invCSx1 原理图)
3. U[49]: 「/proj/drvsa/V0/workdir/haifengf/drvsa_haifengf」(工作目录)
4. U[91]: **「1. W/L/M一起调  2. 优化延迟小于20ps，功耗小于100uA，用Fineim来跑」**(核心 spec：delay<20ps / power<100uA / FineSim / W/L/M 联调)
5. U[173]: **「LMIN=39nm, VDD=1.1V, CLOAD=10fF,把duty cycle也优化到50%附近」**(关键参数：LMIN=39nm / VDD=1.1 / CL=10fF / duty~50%)
6. U[229]: **「输入为5GHz方波，20%～80%上升下降沿为20ps」**(激励：5GHz 方波 / 20-80% 边沿 20ps)
7. U[241]: 「1、/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim  2、ntn/ptn」(FineSim 路径 + ntn/ptn 模型)
8. U[399]/U[400]: aether 环境回写最优解至原理图（后处理，不进 case）

## 助手工具链
editor（构建 invcs_config.py / netlist_gen.py / finesim_runner.py / optimizer.py / selfcheck.py / mock_run.py / single_check.py / fs_check.py / explore_env.py / find_new_stdcpp.py / check_fs_stdcpp.py）+ run_approved_command（python-runner 跑 selfcheck/mock/compile）+ read_files/list_allowed_files（读 /rundata 真实 FineSim 仿真目录 + /apps/synopsys FineSim 安装）。真实流用 CXMT foundry ntn_mra/ptn_mra MOSRA FMI 模型 + FineSim V-2023.12（不可移植 .75：foundry 模型权限不可读 + FineSim GLIBCXX_3.4.26 libstdc++ 冲突 agent 环境）。

## 真实流核心（金标准 = agent 构建的 harness 设计 + spec）
- **DUT**: CMOS 反相器 invCSx1（PMOS Wp/L Mp 并联 + NMOS Wn/L Mn 并联），ntn_mra/ptn_mra 模型
- **激励**: 5GHz 方波（200ps period），20-80% 边沿 20ps → **全摆幅 PULSE 边沿 = 20ps/0.6 = 33.333ps**（20-80 跨 60% 摆幅）
- **measure**:
  - delay: 50%→50% 传播延时（`tpd`）
  - power: 平均 VDD 电流 `i_vdd AVG I(VDD) FROM=valid_start TO=tstop` → idd_ua = i_vdd×1e6
  - duty: `t_high TRIG V(Y) RISE=1 TARG V(Y) FALL=1`、`t_per TRIG V(Y) RISE=1 TARG V(Y) RISE=2`（**FineSim 不支持 `.measure type=PER`，必须 TRIG/TARG**）→ duty_pct=(t_high/t_per)×100
  - 测量窗口须在第一周期稳定后（valid_start）才能拿稳态 duty/power
- **优化**: W/L/M 网格扫 + 坐标下降，找 feasible（delay<20ps & idd<100uA & duty~50%）中 idd 最小
- **输出**: optimization_results.csv（per-point）+ optimization_summary.txt（best feasible）

## case 合成（B 档，L2 真跑 SPICE）
- 真实流用 FineSim + foundry ntn/ptn（不可移植）→ 取可复现子技能=**自包含 level-1 MOS 反相器 + HSPICE tran 表征 + W/L/M 网格 spec 合规筛选**（.75 HSPICE V-2023.12 可跑）
- A（公开）/ B（hidden）：VDD / CL / L / kp / vto / spec / grid 全不同 → best_design 与 feasible profile 不同（跨输入守卫）
- 核心陷阱烤进 check.py：(1) 20-80% 边沿 20ps → 全摆幅 33.333ps（/0.6），naive 用 20ps 必败；(2) duty 用 TRIG/TARG RISE→FALL / RISE→RISE+1（非 .measure PER）；(3) power 窗口须 valid_start 之后（非 0）；(4) 50%→50% tpd；(5) 真跑 HSPICE（subprocess .lis/.mt0），非 print；

## 复用与去重
- 独立于现有 shard B case：InvPVTchar（PVT 最坏角，非优化）、OpampACSpec（运放 AC）、PFDdeadZone（死区测量）、DelayChainEdgeMeas（链传播）、PVTalterChar（NAND2 PVT）、Tr0TrTfMeas（tr0 解析）、Vcc2scTranGen（VCCS testbench）、AOI21ArcChar（std-cell arc）、StimPWL（PWL 激励）、SramSNM（SRAM SNM）。本 case 独特点=**W/L/M 网格优化 + delay/power/duty 三 spec 联合合规筛选**（优化驱动，非单点表征）。
