# trace_deepread: 8n60f — TSPC setup/hold/tCLK2Q native bisection testbench

- **session**: `1792135941514_8n60f.messages.archive.json` (587 msgs, 2.2MB)
- **user/host**: adaml @ hfeg0pkn002 (same user/host as g48nq/SpBisecDeckGen-001, but 8n60f is the actual WORK session, g48nq was the skill-CREATION session)
- **mc**: summary mc=1 (archive), keywords hspice:1834/netlist:1397/schematic:577 — heavy spice
- **domain**: spice_sim (flip-flop timing characterization)
- **prior park note (11-07)**: "skill-authoring-meta-SKILL.md" — shallow; re-peel推翻

## 用户原话链（real user turns）
- **U#1/U#10**「`.../netlist/` 这个电路是 TSPC 电路，你需要生成 spice 仿真激励，通过 hspice 仿真 check 这个电路的 setup/hold time，以及 tCLK2Q。并且优化电路内部的晶体管的尺寸，使得性能最优，且面积不变。」= **CLEAN produce-task**（提需求，未给根因）✓
- **U#28**「提取方法用 bisection 的仿真方法来做。根据仿真的结果指出电路内部的晶体管的尺寸的问题，给出优化方案」= 补充 bisection 方法约束，仍是 produce-task
- **U#133**「我强调一遍，hspice 自带 bisection 的仿真优化方案。」= **给出根因/修复方向** → 按 §A-② 排除 A 档；走 B-synthesized
- **U#317** 电压 0.82–0.92V / 温度 -40~130C / worst-case 优化（后续优化阶段，非本轮取材点）
- **U#481/U#541** 调用 ai-skill-optimizer 元技能（meta，非 produce-task）

## assistant 真实产物
6 个 testbench + 辅助脚本（落 `/home/adaml/Projects/m2701/Presim/`，现已被清理）：
- `tb_func.sp`（功能验证：RST 高有效、D 捕获、Q 升降）
- `tb_tclk2q.sp`（tCLK2Q 测量，基线 tt/25C/1.087V/1fF：rise=25.2ps / fall=23.5ps）
- `tb_setup_rise.sp` / `tb_setup_fall.sp` / `tb_hold_rise.sp` / `tb_hold_fall.sp`（4 个 setup/hold bisection testbench）
- `measure_chk.sp`（measure include）
- `parse_mt0.py`（mt0 结果解析，MEASFORM=3 列式格式）
- `gen_netlist_opt.py`（参数化网表生成，每管 w 独立参数，as/ad/ps/pd/nrs/nrd 随 w 联动，ΣW 面积约束）
- `bisect.sh` / `bisect_all.sh` / `launch_bisect.sh`（初期外部 bash/LSF 循环，被 U#133 纠正后弃用）

## 关键转折：外部循环 → 原生 bisection
assistant 初版用 bash + LSF 逐点循环跑 bisection。U#133「hspice 自带 bisection」后，assistant 查 hspice V-2023.12 手册 `timing_analysis_using_bisection` 章节，改写为**原生 hspice bisection**（tb_setup_rise.sp idx 152 final 版）：
```
.param tsu=Opt1(200p, 0, 400p)   $BISECTION param: D(50%) = CK_edge - tsu
.param t_meas='8.5*tck+tr/2'     $target CK edge = 9th rising 50% crossing
.param t_chk='t_meas+0.8*tck'
.meas tran q_chk  FIND v(Q) AT='t_chk' GOAL='pvcc/2'
.meas tran tq_del TRIG v(CK) VAL='pvcc/2' RISE=9 TARG v(Q) VAL='pvcc/2' RISE=1
.tran 1p 't_chk+0.5*tck' sweep optimize=Opt1 results=q_chk model=optmod
.MODEL optmod OPT METHOD=BISECTION Relin=0.005 Itropt=25
```

## gold deliverable（B-synthesized 取材点）
取 `tb_setup_rise.sp` idx 152 的 native bisection testbench **生成结构**。真实 .sp 已被清理（不可读）+ check 环境无 hspice license → 按文档化 13-section 结构 + 确定性 spec→deck 渲染规则合成资产。deliverable = `tspc_timing_bisec_tb_gen.py`（CLI `<spec.json> <out_tb.sp>`，stdlib only）。

## 与既有 case 区别
- **SpBisecDeckGen-001 (g48nq)**：同 user 的 skill-CREATION session，deliverable = 通用 bisection/optimization deck 生成器（spec.json → 8-section deck，.param/opt1/goal/.model opt 结构），**无 clock/data 激励语义、无时序测量语义**。
- **本 case (8n60f)**：实际 WORK session，deliverable = flip-flop 时序表征 testbench 生成器，带 **clock/data/reset 激励**（VCK/VD/VRST pulse）+ **捕获 .meas GOAL**（q_chk FIND v(Q) AT=t_chk GOAL=pvcc/2）+ **目标沿公式**（t_meas=(idx-0.5)*tck+tr/2）+ **setup/hold 符号**（t_tgt=t_meas∓param）+ **tCLK2Q 测量**（tq_del TRIG/TARG RISE）。结构判据不同，非重叠。

## 教训
11-07 浅 peek 把 8n60f 当 "skill-authoring-meta" park 掉；本轮深 peek archive（587 msgs）发现 U#1/U#10 是 CLEAN produce-task、U#133 给根因排除 A 档、native bisection testbench 结构可判分且与 SpBisecDeckGen 不重叠 → 推翻 park，交付 case。**对 skill-author 用户的高 mc session，archive 文件常含真实 WORK（非 skill 元任务），须深 peek archive 才能定论。**
