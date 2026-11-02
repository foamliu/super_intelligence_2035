# deepread: aq0vc — Vcc2sc standby regulator tran testbench generator

- **trace**: `1792375390057_aq0vc` (tongni @ hfeg0pfn119, mc=254, deepseek-v4-flash, cxmt-deepseek)
- **session**: 301 msgs / 157 user / 144 assistant, 2026-10-19..10-23, cwd=/home/tongni/Desktop
- **tool_use**: run_approved_command 59 (python-runner/shell-runner) · read_files 14 · editor 112 · list_allowed_files 5 · skills 1 · search_codebase 1
- **real task**: 用户给 `1_Vcc2sc_stdby/Vcc2scstdby_tran.sp`（testbench netlist），要 agent 学习其结构后能"根据 testbench netlist 产生仿真文件"；后续补：measure 按自然语言生成 `.MEASURE` 语句、瞬态响应参数 + 功耗、未归类信号兜底 vss、固化成 skill `tran-sim-gen`。
- **gold**: agent 产出 `gen_vcc2sc_tb.py`（参数化 .sp 生成器，复现学的分段结构）+ skill `/home/tongni/.cline/skills/tran-sim-gen/SKILL.md`；自验 default 输出与原 `Vcc2scstdby_tran.sp` 逐行一致；variant 输出（自定义 measure/load）跑通。

## 真实 testbench 结构（Vcc2scstdby_tran.sp，1391B）

固定分段顺序（agent generator 把它固化，msg[30-60] 初版把分段顺序写乱、pwl 丢 `0.9` DC 值、低网名 `vv` 前缀翻倍——三个真 bug 都修了）：

```
*******option**********          .inc 'hspiceconfig.sp'          (global opts: PARHIER/measform/finesim_mode)
********netlist**************    .inc '<schematic.netlist>'      (DUT + subckts, top inst XI_AG_Vcc2scStdby_0)
********power parameters*****    .inc 'power_tran.sp'            (power-rail PWL ramp: vvdd1!/vvcc!/vvss!/vvwlp!/vvpcsg!/vvkb!)
                                 .param res_sn=1 res_pa=3 res_cp=3 res_sw=3   (power resistor selectors)
********stimulus*************    .GLOBAL vdd1! vcc! vpcsg! vwlp! vss! vkb!
                                 vVcc2scRef  Vcc2scRef 0 0.9 pwl(0 0 17.92u 0 19.22u 0.565 23.59u 0.9)  (ref ramp → 0.9V)
                                 vVdleqStdbyDis ... 0 pvss       (standby disable → vss)
                                 vcm1_ag_*Bias<0..2> 0 pvss      (testmode bias → vss)
                                 iload Vcc2sc! 0 1mA pwl(0 0mA 50u 0mA 50.001u 0.1mA 100u 0.1mA 100.001u 1mA 150u 1mA 150.001u 0.1mA)  (load current steps)
                                 .tran 1n 300u
                                 .ic v(vcc2sc!)=0
                                 .probe v(*) i(*)
********measurement**********    .MEASURE TRAN Vcc2sc_unload  AVG V(Vcc2sc!) FROM=60u TO=70u    (no-load window)
                                 .MEASURE TRAN Vcc2sc_load1mA AVG V(Vcc2sc!) FROM=110u TO=120u  (1mA-load window)
********pvt******************    .inc 'pvt_vcc2sc.sp'            (PVT corner .lib)
.END
```

SPEC.sp: `Vcc2sc_unload Variation<5mV` / `Vcc2sc_load1mA Variation<5mV`（负载调整率 < 5mV 验收）。

## 真陷阱（烤进 case）

1. **分段顺序硬契约**：option→netlist→power→stimulus→.tran→.ic→.probe→measure→pvt→.END。乱序（如 .tran 在 stimulus 前、measure 在 .tran 前）→ HSPICE 报错或 .measure 全 failed。agent 初版 insert-line 把分段写乱是 msg[30-60] 主线 bug。
2. **ref PWL 完整性**：`vVcc2scRef ... 0.9 pwl( 0 0 17.92u 0 19.22u 0.565 23.59u 0.9 )`——DC 值 `0.9` 在 `pwl(` 之前，pwl 点列在括号内。agent bug：丢 `0.9` DC + 丢 `pwl(` 关键字（msg[60]）。
3. **.measure 窗口须落在 load PWL 稳态区**：load PWL `50u 0mA / 50.001u 0.1mA / 100u 0.1mA / 100.001u 1mA / 150u 1mA / 150.001u 0.1mA`。unload 窗口 60-70u（稳态 0mA 区，50.001u 跳变后已稳）✓；load1mA 窗口 110-120u（稳态 1mA 区，100.001u 跳变后已稳）✓。窗口落在跳变点（如 49-51u）→ AVG 含暂态 → 量错。
4. **.measure `failed` 处理**：HSPICE `.measure` 找不到 cross/when → `failed`，.lis 解析须当 null 不当 0 不崩。
5. **功耗 = avg i(vdd) × vdd**：不是 V·I 瞬时乘积；按窗口 AVG 电流再乘 vdd。
6. **未归类信号兜底 vss**：cm1_*/\*Dis/ACTEN 等默认 pvss；\*Ref 默认 pwl 斜坡。
7. **.probe v(\*) i(\*) 默认**：不写则 .measure V(node) 仍可算，但 i(vdd) 功耗量不到。
8. **.ic v(vcc2sc!)=0**：输出轨初值 0，让上电斜坡从 0 起；缺则收敛慢/振荡。
9. **res_sn/res_pa/res_cp/res_sw 参数**：power_tran.sp 内部用这些 .param 选电阻值；generator 须保留 `.param` 行。
10. **跨输入守卫**：A 设计 gm 大 → load_reg<5mV PASS；B 设计 gm 小 → load_reg>5mV FAIL。hardcode A 的 measure 值在 B 上败。

## 可复现子技能（本 case 取这个）

真实流用 CXMT foundry 网表 + /proj/dscqa/ + /rundata/dsjqa/（permission denied 不可读）。取可复现子技能 = **从结构化 characterization spec（DUT + power ramp + ref ramp + load-step PWL + 自然语言 measure 请求 + PVT 角）合成完整 HSPICE tran deck（分段顺序契约）→ 真跑 HSPICE → 解析 .lis .measure → 报负载调整率 + 功耗**。DUT 用自包含线性模型（VCCS pass + Rb + Cout），保留真实 testbench 的全部分段/陷阱。L2（真跑 .75 HSPICE）。

## case 规划

- **id**: EDA-Eval-DesignFlow-Vcc2scTranGen-001
- **domain**: spice_sim · **tier**: L2 · **track**: faithful (B档 synthesized, 子技能 faithful)
- **assets A**: vcc2sc_reg.sp（DUT subckt）+ spec.json（power ramp/ref ramp/load steps/measure requests NL/pvt）+ tb_contract.md（分段顺序契约）
- **hidden B**: spec_B.json + vcc2sc_reg_B.sp（gm/vdd/ref/load 全不同，load_reg 跨 B FAIL）
- **reference**: vcc2sc_tran_gen_ref.py + check.py + negatives
- **k 断言** ≥ 12
