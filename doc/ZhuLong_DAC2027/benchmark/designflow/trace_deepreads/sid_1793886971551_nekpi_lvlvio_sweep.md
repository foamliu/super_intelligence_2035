# Deepread: 1793886971551_nekpi (yifansun @ hfeg0pkn001) — LvLvioSweep

**trace_source**: user=yifansun, host=hfeg0pkn001, session=1793886971551_nekpi.messages.json
**size**: 1.34MB, 291 msgs, 743 spice-tool mentions (hspice/finesim)
**选料轮**: msg#0 USER — clean A-档 提出需求 (无根因/无方案)
**mtime**: 2026-11-05 22:11 (fresh, found via targeted rescan newer than 19:2x last scan)

## 用户原话 (msg#0, verbatim)
评估 lv vs lvio 管子对 DPmux8 block 速度与功耗的影响。给 input.sp + netlist 路径。
- (a) 添加4项 .measure：信号延迟(1.157u→net36<7>第一次翻转)、动态读电流(1.19u-1.36u XI_LVIO)、动态写电流(0.868u-1.05u XI_LVIO)、静态电流(192n-559n XI_LVIO)
- (b) 三维度扫描建60变体：Width ×{0.9,1.0,1.1,1.17,1.25}5档 × Length 46nm→{42,46,50,55,64,70}6档 × 类型 _lvio↔_lv 2档 = 60
- 约束：①参数引用(如 w='WP1')不改 ②真实width=width/nf 夹[150nm,2um] ③仅46nm管替换长度，64nm/42nm不管 ④.alter拆独立文件丢 fqueue2h 队列 bsub 并行 ⑤结果整理 sim_result.txt

## assistant 工具链 (68 editor / 35 read_files / 32 run_approved_command)
- read_files: input.sp, netlist (DpMuxTop_2), stimulus, force_power.inc
- grep 分析: ntn_lvio/ptn_lvio/ntn_lv/ptn_lv 器件, l= 分布(46nm 为主, 少量42/143/200nm)
- 多版迭代: analyze_sim_netlist.py → generate_sim_variants.py → gen_v1.py → gen_v2.py → gen_all.py / gen_clean.py
- 核心函数 tr(net, ws, ln, dt): type swap + width scale(ispr 参数跳过) + 46nm-only length subst

## 金标准 (msg#286 用户接受的生成产物, sim 未跑 results/空)
- **measurements** (每个 input.sp):
  `.measure tran t_delay TRIG v(net36<7>) VAL='pvcc/2' RISE=1 TD=1.157e-6`
  `.measure tran i_dyn_read AVG i(vcc!) FROM=1.19e-6 TO=1.36e-6`
  `.measure tran i_dyn_write AVG i(vcc!) FROM=0.868e-6 TO=1.05e-6`
  `.measure tran i_static AVG i(vcc!) FROM=192e-9 TO=559e-9`
  (+ i_peak_read / i_peak_write MAX)
- **transform**: `_lvio`→`_lv`(type=lv时); Wxx=/w= 数值按 ws 缩放, ispr(WP1 等字母/表达式)跳过; Lxx=/l= 仅 46e-9 替换为目标长度
- **变体命名**: `w{int(ws*100):03d}_l{ln}_{dt}` (如 w090_l42_lvio)
- **deck**: .option + .lib model + .temp + .param pvcc/pvbn/pvbp + .include netlist + .include stimulus + .tran 1p 1621.73n + .probe + .measure×6 + .end (60变体×10 PVT=600 deck)
- **run_all.sh**: `bsub -q fqueue2h finesim -i <input> -o <results> -np 4` ×600
- **variant_summary.txt** + **parse_results.py**(解析 finesim.mt0 → sim_result.txt)
- 注意: 用户要求的 width/nf clamp[150nm,2um] 在 summary 声称实现，本案 reference 强制实现并作断言点

## 用户后续 (msg#287-290): 问"跑子集vs跑全部区别" / "跑全部步骤" — assistant 解释 run_all(600 job)/run_subset(120 job) 流程。未实际跑 sim。

## case 落地
`EDA-Eval-DesignFlow-LvLvioSweep-001` (spice_sim, A-faithful L2)
交付 `gen_variants.py <netlist> <out_dir> <config.json>`: 变体网表(type swap+width scale+clamp+46nm length subst+参数跳过) + 含.measure deck + run_all.sh + variant_summary.txt
check.py k=14 (a-n), hidden B=不同 netlist(nor2GT/neta<3>/不同尺寸/64nm+200nm 非46/w1.8e-6+w120e-9 触发钳位) + 不同 sweep(4×4×2=32) + 不同 measure 信号/窗口
