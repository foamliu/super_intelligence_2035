# deepread: 1793341440302_sqm07 (tongni@hfeg0pkn001) — Vcc2scAct SPEC-driven deck 生成

## trace meta
- source: `.75` ssh 10.129.2.10 `/home/tongni/.cline/data/sessions/1793341440302_sqm07/1793341440302_sqm07.messages.json` (827KB, 184 msgs, agent=lead, model=cline)
- spice 计数: spice=945 / 总=1431 (66%) → spice_sim
- mtime 2026-10-30 (≥10-28 窗口 ⇒ fresh)
- 11-06 07:37 本轮 claim（mc=223, domain=spice_sim）

## USER#0 原话（A-档逐字，唯一需求轮；无根因/无方案）
`/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scAct_sim_sp 根据文件夹下的文件跑仿真，把对应的结果放到/proj/dscqa/V0/simdir/hspice/tongni/00_AI_test/`
（口语指令：根据该文件夹下的文件跑仿真，结果放到指定目录。未给根因/方案 ⇒ 合格 A-档 need 轮）

## assistant 工具链（read_files + editor + run_approved_command + skills）
1. list_allowed_files 列 Vcc2scAct_sim_sp/ → read_files 读 SPEC.sp + tongni_DSCQA_2nd_sim_AG_Vcc2scALDOAct_sim_schematic.netlist（含 830-1347 行）
2. skills sim-sp-gen 引导 → 读 skill references (Vcc2scstdby_tran.sp / ac.sp / SPEC.md / gen_vcc2sc_act_tb.py / tran_utils.py / tran_mcp.py)
3. editor 写 gen_vcc2sc_act_all.py（读 SPEC 5 段 + netlist → 生成 5 deck + 拷 netlist）；run_approved python-runner 执行 → 产出 5 个 .sp
4. editor 写 submit_vcc2scact.sh（bsub 提交 fqueue3_analog 队列）→ 首次全 EXIT（LD_PRELOAD libstdc++ GLIBC_2.18 缺失）→ unset LD_PRELOAD/LD_LIBRARY_PATH 重提 → 5 job DONE
5. read .mt0/.ma0/.ms0 → editor 写 analyze_vcc2scact.py / analyze2.py / write_report.py 做 SPEC PASS/FAIL 分析报告落盘
6. trace 末尾(msg183) assistant 总结：5 deck 全跑完，结果全在 00_AI_test/ → **用户接受态**（任务闭环）

## SPEC.sp（5 段，逐字）
```
********ac_load*********  Vcc2sc_Gain_load1mA>40dB  Vcc2sc_PM_load1mA>30d  Vcc2sc_GM_load1mA>5dB  Vcc2sc_GBW_load1mA>1MHz  Vcc2sc_f_3db_load1mA dont care
********ac*********      Vcc2sc_Gain>40dB  Vcc2sc_PM>30d  Vcc2sc_GM>5dB  Vcc2sc_GBW>1MHz  Vcc2sc_f_3db dont care
*******dc_capbi********  IVcc2sc>2.5mA
*******tran_mc********   Vcc2sc_unload_mc 3sigma<10mV  Vcc2sc_1mA_mc 3sigma<10mV
*******tran***********   Vcc2sc_unload 0.9V<10mV  Vcc2sc_load1mA 0.9V<10mV  Vcc2sc_undershot>0.87  Vcc2sc_undrmag<30mV  Vcc2sc_overshot<0.93  Vcc2sc_Rspon<100ns  Vcc2sc_tsetting dont care  ring_ratio<0.01
```

## 金标准（=assistant 实际产物，本 case 验收对象）—— 5 个 SPEC-driven hspice/finesim deck
通用结构（每 deck，********section********** 分块）：
- option: `.inc '<hspiceconfig>'`
- netlist: `.inc '<out>/<netlist>'`
- power parameters: `.inc '<power_tran>'`
- stimulus: `.GLOBAL vcc! vcc2sc! vdd1! vss!` + 5 控制脚固定 pvss（Vcc2scActDis/Vcc2sc2Vcc/cm1_ag_Vcc2scActBias<0>/<1>/cm1_ag_Vcc2scActPrime）+ Vcc2scRef 0.9 ramp pwl(0 0 17.92u 0 19.22u 0.5643 23.59u 0.9) + Vcc2scActEn + iload
- analysis + measurement（每 deck 不同）：
  - **tran**: `.tran 1n 300u` + .ic v(vcc2sc!)=0 + 13 .meas（Vcc2sc_unload/load1mA AVG, undershot MIN, undrmag PARAM, overshot MAX, overmag PARAM, tvalley WHEN, Rspon PARAM, trecover WHEN, tsetting PARAM, pp_front/pp_back PP, ring_ratio PARAM）
  - **ac (light 0.05mA)**: `.ac DEC 100 1 10G` + `.lstb vcc2sc mode=single vsource=V0` + 5 .meas（Vcc2sc_Gain max DB / PM find P when DB=0 cross=last / GM find DB when P=0 / GBW when DB=0 / f_3db when DB=Gain-3）—— 无 _load1mA 后缀
  - **ac_load (1mA)**: 同 ac 但 meas 名带 `_load1mA` 后缀 + iload=1mA
  - **dc_capbi**: `.dc pvalue 0.7 0.95 0.002` + `.meas dc IVcc2sc find i(vvcc2sc) at=0.87`
  - **tran_mc**: `.tran 1n 300u sweep monte=500` + 2 .meas（Vcc2sc_unload_mc / Vcc2sc_1mA_mc find v at 70u/120u）+ pvt 段（cthin/cthick/cgatein/capo=0.4f + .TEMP 85 + .LIB volt typ + .LIB corner ttt + tcpres_flag=1 mis_flag=1）
- pvt: `.inc '<pvt_vcc2sc>'`（tran/ac/ac_load/dc_capbi）
- `.END`

## 资产 fetch 状况
- SPEC.sp：trace read_files tool_result 逐字提取（28 行）✓
- netlist：trace read_files 含头部 60 行（.subckt switch_close/open, AG_CXcap2S60x71, AG_ComSwitch2d7, AG_Vcc2scALDOActCom ...）→ 作 asset A（代表头，deck 只 .inc 不解析内容）
- 5 gold deck：trace read_files(msg57) 逐字提取 ✓（存 .75 workdir gold_deck_*.sp）
- gen_vcc2sc_act_all.py：trace editor(msg49) 全文提取 ✓（依赖 tran_utils，参考解将自包含重写）

## case 设计（track=A-faithful, spice_sim L2）
- case_id: `EDA-Eval-DesignFlow-Vcc2scActDeckGen-001`
- prompt = USER#0 原话逐字（A-档）
- task_brief.md ≤3 行（只写交付接口 `gen_decks.py <spec> <netlist> <sim_params.json> <out_dir>` + outputs/submit.zip）
- assets A: SPEC.sp + netlist（代表头）+ sim_params_A.json（ref=0.9/load_light=0.05mA/load_heavy=1mA/monte=500/dc 0.7-0.95 step 0.002 point 0.87/控制脚/global/ref_ramp pwl/tran pwl/act_en timing）
- hidden B: 同 SPEC + netlist + sim_params_B.json（ref=1.0/load_light=0.02mA/load_heavy=2mA/monte=300/dc 0.6-0.9 step 0.005 point 0.82/不同 tran pwl）→ 跨输入护栏
- 交付: 通用 `gen_decks.py <spec> <netlist> <sim_params.json> <out_dir>` 读 SPEC(段+meas 名)+netlist(.inc)+sim_params(数值/脚/时序) → out_dir 下 5 子目录 5 deck + 拷 netlist；打包 submit.zip（gen_decks.py + 5 deck + netlist）
- reference: gen_decks_ref.py + check.py **k≥12 断言**:
  a zip 含 gen_decks.py + 5 deck(tran/ac/ac_load/dc_capbi/tran_mc 子目录) + netlist
  b gen_decks.py py_compile OK
  c tran deck 含 `.tran` + SPEC tran meas 名（Vcc2sc_unload/load1mA/undershot/overshot/Rspon/ring_ratio）
  d ac deck 含 `.ac DEC` + `.lstb` + Vcc2sc_Gain/PM/GM/GBW（无 _load1mA 后缀）+ iload=0.05mA
  e ac_load deck 含 _load1mA 后缀 meas + iload=1mA
  f dc_capbi deck 含 `.dc` sweep + `.meas dc IVcc2sc ... at=0.87`
  g tran_mc deck 含 `sweep monte=500` + Vcc2sc_unload_mc/1mA_mc meas
  h 所有 deck `.inc` netlist + power + hspiceconfig + pvt
  i 控制脚固定 pvss + Vcc2scActEn pvcc/pwl + Vcc2scRef ramp 0.9
  j L2 真跑：hspice parse tran deck（rewrite .inc → 本地 stub netlist+corner）→ 无 syntax/parse error（subprocess 结构断言）
  k 跨输入：check 跑 gen_decks.py 于 sim_params_B → B deck 含 monte=300/ref=1.0/load_heavy=2mA/dc 0.6-0.9，且与 A 串不同（无硬编码）
  l SPEC-faithful：deck 数=SPEC 段数(5)，每 deck 分析类型对应段（tran→.tran / ac→.ac / dc_capbi→.dc / tran_mc→.tran sweep monte）
  + 5 negative stubs + negative_selftest 全 FAIL + §4.9 三假提交全 FAIL
- 金标准 = trace 中 assistant 实际创建的 5 deck（已存 gold_deck_*.sp）
- 判分只跑 hidden B；判分器不进 SUT workdir
- L2 hspice stub：reference/hspice_stubs/ 含 minimal netlist（被动件 R/V/I + .GLOBAL 节点）+ 空 corner stub，check rewrite .inc 后 `hspice -i` 验 syntax

## 备注
- mspice 在目标机不存在，trace 实跑 hspice（tran/ac/ac_load/dc_capbi）+ finesim（tran_mc）→ check.py L2 用 hspice（.75 /apps/synopsys/.../hspice）
- trace 的 LSF 提交/实际 sim 运行属环境特定（队列不可移植）→ case 验收对象 = deck 生成（结构 + SPEC-faithful + hspice parse），非 sim 数值正确性
- tran_utils 依赖：参考解自包含重写 build_ref_ramp/build_fixed_level/build_rail_timing/build_pwl_source（输出从 gold deck 反推）
