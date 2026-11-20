# 深读笔记 — 13fwy (thqu / hfeg0plg99 / mc211)

- **session**: `1792495939340_13fwy.messages.json`，264 msgs，11 user 轮
- **domain**: waveform（WaveView PWL 波形 → SPICE 激励）
- **user 真实意图**（U#45 提出需求轮，逐字原文）：
  > 我的网表路径在 /proj/ddgoa/V0/workdir/thqu/simulation/ddgoa_cmos_work_R_NegVssIdd_opt_qyh_schematic_ALPS/，我的输入信号是 GrEn，SanEn2G，SapEn2GP，Ra16L<1:0>，Ra16H<1:0>，PwrOnLsVwlp。我从 WAVEVIEW 提取出来的信号波形在 /proj/ddgoa/V0/workdir/thqu/circuit_opt/R_NegVssIdd_opt_qyh/，其中的 si1.sp，si2.sp，si3.sp，帮我写一个激励。

## 信号映射（从 trace 理清）
| 源信号（WaveView 导出名） | 目标输入引脚 | si 文件 | 激励模式 |
|---|---|---|---|
| grensec55 | GrEn | si1.sp | PWL 精确波形（71 点，0~10.9ns，0~0.6V） |
| sanen2gsec55 | SanEn2G | si1.sp | 理想脉冲（U#79/U#135：`pwl(0n 0 30n 0 30.1n pvcc 100000n pvcc)`） |
| sapen2gp | SapEn2GP | si3.sp | 理想脉冲（同上） |
| pwronlsvwlpsec55 | PwrOnLsVwlp | si3.sp | 固定直流 2.71V（U#79：pwr 有毛刺→直线固定电位 2.71） |
| ra16l<1> / ra16l<0> | Ra16L<1:0> | si2.sp | PWL 精确波形 |
| ra16h<1> / ra16h<0> | Ra16H<1:0> | si3.sp | PWL 精确波形 |

## agent 工具链（关键产物）
1. U#1 探查 waveview-fsdb-readerV2-2 skill + find *.fsdb（无 fsdb，转用 si*.sp）
2. U#45 后 read_files si1/si2/si3.sp（/proj 路径 read_files 返回空——cline read_files 对 /proj 大文件返回空，但 agent 通过 run_approved_command 跑 python 直接读盘成功）
3. editor 写 gen_stimulus.py（msg 92 成功创建）：`extract_pwl_from_text` 正则 `V<sig>\s+\S+\s+0\s+PWL\(\n(.*?)\n\+\)` 提取 PWL body → `format_pwl_lines` 重排 → ideal_pulse/dc_fixed 分支 → 写 stimulus.sp
4. run_approved_command 跑 gen_stimulus.py → stimulus.sp 761 行 35887 bytes，sha256=8e90a2e6...
5. U#135 后 editor 改 SanEn2G/SapEn2GP 为紧凑单行 `pwl(0n 0 30n 0 30.1n pvcc 100000n pvcc)`，PwrOnLsVwlp 改 `pwl(0 2.71 100u 2.71)`
6. 后续 gen_stimulus_v2.py（compact PWL + simplify_pwl 降点）—但用户接受的是 v1（U#153 "归类一下" 即收尾接受）

## 真实文件可读性
- si1/si2/si3.sp 在 /proj/ddgoa/...（e0031982 不可读，permission denied；trace read_files 也返回空）
- gen_stimulus.py / stimulus.sp 在 /home/thqu/（已被用户清理，cat 返回 No such file）
- **golden 重建**：gen_stimulus.py 从 trace editor new_text（msg 92）重建；grensec55 真实 71 点 PWL 数据从 msg[80] stimulus.sp editor new_text 逐字提取（trace 唯一保留的完整真实波形数据）

## A 档合成
- **case**: EDA-Eval-DesignFlow-WvStimExtract-001（waveform, L1-boundary, track=faithful）
- **资产 A**: si1.sp（grensec55 真实 71 点 + sanen2gsec55）、si2.sp（ra16l<1:0>）、si3.sp（ra16h<1:0> + sapen2gp + pwronlsvwlpsec55）、config.json（8 信号 source/target/file/mode 映射 + 9 电源 + pvcc=0.73）
- **hidden B**: 设计 DDRCtlrDrvClk_qyh，pvcc=0.80，信号族 DrvClk/CfgEn/Addr<2:0>/Rdyn/BiasV，dc=1.5，delay=25ns，文件 wv_a/wv_b/wv_c.sp，7 信号（5 pwl + 1 ideal + 1 dc）
- **交付**: gen_stimulus.py 读 asset_dir + config.json 输出 stimulus.sp
- **check.py**: 14 条件 a-n（zip+compile / 跑 B exit0 / .param pvcc / V 源计数 / PWL 点一致 / ideal_pulse 紧凑形式 / dc_fixed 电压 / 括号平衡 / 映射注释 / 目标名 / 跨输入护栏 / 确定性 / 时间单调 / 退化 FAIL）
- **自验**: ref PASS 14/14 · 3 negatives ALL-FAIL distinct{empty→b / print_fixed_A→c / core_deleted→e} · k_rationale=k_check=14 ✓
