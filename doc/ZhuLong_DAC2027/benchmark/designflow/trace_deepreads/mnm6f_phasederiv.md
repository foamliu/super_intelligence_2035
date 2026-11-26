# deepread: mnm6f (xflin@hfeg0pkn004) — phase-derivative / group-delay TB modify

**trace**: `/home/xflin/.cline/data/sessions/1794817079726_mnm6f/1794817079726_mnm6f.messages.json` (93148B, 19 msgs)
**session.json**: provider cxmt-mwemirldxhchys, model deepseek-v4-flash, cwd /home/xflin/Desktop, status failed (stale_session_reconciler), interactive
**scan kw** (1118 pool): hspice:68;virtuoso:7;lib.defs:5;cadence:5;synopsys:4;netlist:4;verilog:3;rtl:3 → spice dominant (ratio 0.61), mc=20
**user**: xflin (NEW-user, not in B ledger prior)

## 用户真实意图（逐轮 user_input 原文）
- msg0/1: `<user_input mode="act">修改这个文件，对相位曲线求导` + 附 `T_coil1x.sp`
- msg2/3: `解析下这个tb，给出解释`（仍附 T_coil1x.sp）
- msg17: `把完整的tb给到我`

## 关键产物 / assistant 工具链
- read_files T_coil1x.sp（uploads，3125B FineSim AC 小信号 S 参数 TB）
- skills (spice stimulus view/modify) + get_agent_policy_status + list_allowed_files
- 生成 `T_coil1x_phasederiv.sp`（修改后 TB，msg18 给出完整内容）

## 原 TB 结构（T_coil1x.sp, verbatim）
- .option 区：PARHIER=LOCAL, scale=1, finesim_mode=spicehd, finesim_output=fsdb, finesim_model=4, finesim_speed=0, finesim_dvmax=0.1, finesim_subckt_dup_rule=0, measdgt=3, measform=3 measfile=1, finesim_spred=1, (注释 `* .option finesim_tunit=0.0`)
- .include `/proj/m2701/V0_DDR4/workdir/xflin/simulation/S11_with_T_coil2/hspiceD/schematic/netlist/netlist`
- .lib `model.sp top_tt` + `model_thick.sp tt_vodka`, .temp 25
- .param: VVDD=0.88, VVDDQ=0.5, l11=60p, l22=240p, k=0.3, M=k*sqrt(l11*l22), L1=(l11+M), L2=(l22+M), CB=10f
- ZQ vsource ZqPd5..0 (dc='0/1*VVDD'), vvddq vddq! 0 0.5, vvss vss! 0 0
- VVin Vin 0 DC 0.5 AC 1
- `.ac lin 200 0.1G 20G SWEEP l22 60p 600p 20p`
- .probe ac vdb(*), vp(DQ<7>), vp(DQ_RX<7>), Gain='vdb(DQ<1>) - vdb(SOC<1>)', Gain='vdb(DQ_RX<1>) - vdb(SOC<1>)', Gain2='vdb(DQ<7>) - vdb(SOC<1>)', Gain3='vdb(DQ_RX<7>) - vdb(SOC<1>)'
- .end

## 修改后 TB（msg18, 参考行为 — 只两处改动）
1. **`+ .option unwrap=1`** — AC 相位解卷绕（避免 ±180° 折叠致求导假尖峰），注入在 option 区（finesim_spred 行后、finesim_tunit 注释前）
2. **新增 12 条 `.probe ac`**（插在原 .probe 块后、RST 段前）：
   - 6 条相位求导 `dPhi_<name> = par('DER(vp(<expr>))')`，deg/Hz：
     - `dPhi_DQ<7> = par('DER(vp(DQ<7>))')`
     - `dPhi_DQRX<7> = par('DER(vp(DQ_RX<7>))')`
     - `dPhi_Gain = par('DER(vp(DQ<1>) - vp(SOC<1>))')`
     - `dPhi_GainRX = par('DER(vp(DQ_RX<1>) - vp(SOC<1>))')`
     - `dPhi_Gain2 = par('DER(vp(DQ<7>) - vp(SOC<1>))')`
     - `dPhi_Gain3 = par('DER(vp(DQ_RX<7>) - vp(SOC<1>))')`
   - 6 条群时延 `GrpDelay_<name> = par('-DER(vp(<expr>))/360')`，秒：
     - 同 6 个 expr，`-DER(...)/360`
- 算法说明（assistant msg12）: `DER()` 波形内建数值求导，AC 扫描下对频率 f(Hz) 求导；相位 vp 单位 degree；群时延 τg = -dφ/dω = -d(φ_deg)/df / 360（单位秒）
- 节点/表达式枚举来自用户原 vp() 探针 + Gain 差分曲线（vdb→vp 差分）

## reframe 决策（harness-for-teeth）
- 真任务 = "修改这个 .sp 文件，对相位曲线求导（即求群时延）" + "解析解释" + "给完整 tb" → 单文件修改 + Q&A
- 不可便携点：原 .include/.lib 路径仅 xflin 环境可读，FineSim 二进制不可在 SUT 跑
- reframe → **produce 参数化脚本 `add_phase_deriv.py`**：`--sp <in.sp> --out <out.sp> --probes <probes.txt>`，probes.txt 每行 `<name> <vp_expr>`；脚本注入 `.option unwrap=1`（option 区，幂等）+ 为每个 probe 生成 `dPhi_<name>=par('DER(<vp_expr>)')` 与 `GrpDelay_<name>=par('-DER(<vp_expr>)/360')`（插在 .end 前），保留原 .sp 所有结构/注释
- L1（纯 python 文本解析，无 EDA 二进制）；track=faithful；asset A=T_coil1x.sp verbatim 自 trace uploads + probes_A.txt（trace 6 对 name/expr）

## case 设计
- case_id: EDA-Eval-DesignFlow-PhaseDerivGroupDelay-001
- asset A (SUT 看): design_A/T_coil1x.sp (verbatim) + design_A/probes_A.txt
- hidden B (check 跑): hidden/TB_B.sp (结构性差异: 不同 include/lib corner ss/.temp 85/不同 .param l11=80p l22=400p k=0.4 CB=15f/不同 .ac dec sweep/不同 probe 节点 DQ_tx<0> CLK_RX<3> STB<5>/含 `* .probe ac vp(TRAP_NODE<9>)` 注释 trap) + hidden/probes_B.txt (4 probe) + hidden_manifest.json
- check 真跑 SUT add_phase_deriv.py 于 B+probes_B，解析 out.sp，14 条独立断言 (a-n)
- 5 neg: empty_shell / print_only / hardcode_a / unwrap_only / core_deleted(DER 删)
- anti-hardcode-A: B 输出不得含 A 专属 token (DQ<7>/DQ_RX<7>/SOC<1>/proj/m2701/V0_DDR4/workdir/xflin/tt_vodka/l22=240p)
