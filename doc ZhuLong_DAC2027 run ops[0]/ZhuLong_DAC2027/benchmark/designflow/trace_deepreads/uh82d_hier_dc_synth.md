# 深读笔记 — uh82d 层次保留 DC 综合 flow（shard A 轮 56）

## trace
- session: `1790219837415_uh82d.messages.json`（johnl @ hfeg0pfn119 / 10.129.33.245）
- mc=41 netlist + 23 synthesis（daily eda_trace_20261101.log）；NMSG=13（短，continuation 会话）
- 真实资产可读：`/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/`
  - synth.tcl(3776B)、run_dc.sh(164B)、rtl/{addr_to_rowcol_region.v, addr_to_rowcol_region_v7.v}、out/reports/{timing_post,area_post,qor_post,references_post,...}.rpt
- 设计：`addr_to_rowcol_region`（组合地址解码器，6 个层次子模块：addr_region0_calc/1_calc/2_calc/3_calc/addr_region_decode/addr_rowcol_mux；PrimeLib-characterized stdcells library；LVS-only cell 过滤；组合电路；虚拟时钟 vclk + IO delay）

## 用户意图（A 档②）
- 该会话是上一会话（1f34q，已 anchor）的 continuation：用户粘入先前 glm-5.2 对话转录 + 「继续」+「注意要保留层次进行综合」+「你看下生存到报考我没看到时序报告」
- 真实需求（从转录）：给定 addr_to_rowcol_region Verilog + PrimeLib stdcells library，做**层次保留**的 DC 综合，生成 synth.tcl + SDC + run_dc.sh，跑综合
- 关键 bug（转录内）：先前脚本对子模块 `set_dont_touch` → 子模块保持 hierarchical & unmapped（GTECH/`h` 属性，references_post 显示 6 个 `h` 子模块未映射）→ 修复 = 移除子模块 dont_touch，让 compile_ultra 映射子模块，但**仍保留层次**（不 ungroup/flatten）
- A 档②判定：用户轮表达目标「保留层次进行综合」= 提需求；但会话主体是 continuation（"继续" + 报告检查），build 发生在上一会话 → 本轮取 B 档 synthesized（合成 faithful：真实设计结构 + LVS-only 过滤 + 层次保留 + dont_touch-on-submodule GTECH bug）

## 真实 synth.tcl 结构（提取要点，作 reference gold 依据）
- `set TOP / set RTL / set LIB` 三行可编辑头
- `set_app_var target_library/link_library`
- `define_design_lib WORK -path out/work`
- `analyze -format verilog $RTL` + `elaborate $TOP` + `current_design $TOP` + `link`
- 组合电路守卫：`if {[sizeof_collection [all_registers]] != 0} { error "Sequential..." }`
- LVS-only cell 过滤：`get_lib_cells -quiet */*LVS*` → 收集 LVS_LIB_NAMES → 对 non-LVS cells `set_dont_use`
- 约束：`set_units -time ns ...` + `set_max_transition` + `set_max_area 0` + `set_load -pin_load` + `set_input_transition` + `set_max_delay -from [all_inputs] -to [all_outputs]`
- 真实脚本用 `ungroup -all -flatten` + `set_flatten true`（**反面教材**，违反"保留层次"）→ 本 case 的判分点：候选必须**不**含 ungroup/flatten
- `compile_ultra`（真实 buggy 版用 `-area_high_effort_script`）
- unmapped 守卫：`get_cells -hierarchical -filter "is_unmapped == true"` error
- non-LVS ref 守卫：`get_cells -hierarchical -filter "is_hierarchical == false"` 检 ref_name
- reports：redirect check_design/timing/area/qor/references/constraints
- `change_names -rules verilog -hierarchy` + `write -format verilog -hierarchy -output out/mapped.v` + `write_sdc out/mapped.sdc`

## 合成计划（B 档）
- case_id: `EDA-Eval-DesignFlow-HierDcSynth-001`（digital, L2, B 档 synthesized）
- verb: `hier-preserving-dc-synth-flow`（生成层次保留 DC synth.tcl；与 DcDontuseGen-001=lib→dont_use allowlist / DcUpfDiag-001=UPF 诊断 互斥）
- 交付: submit.zip { `gen_synth_tcl.py`（通用层次保留 DC synth.tcl 生成器, CLI `--spec <spec.json> -o <out.tcl>`, 纯 stdlib 读 JSON spec→emit synth.tcl）, `synth_A.tcl` }
- A 可见 bundle: `spec_A.json`（top=addr_dec_A, 4 子模块 [reg0_calc_A, reg1_calc_A, decode_A, mux_A], lib=stdcells_A.db, LVS-only=true, clock={name=vclk,period=1.0ns}, max_delay=0.5, combinational_only=true, preserve_hierarchy=true）+ `rtl_A.v`（组合地址解码器, 4 子模块实例, 无寄存器）
- B 隐藏 bundle（异构 cross-input guard）: `spec_B.json`（top=addr_map_B, 3 子模块 [sel_b, encode_b, arb_b], lib=stdcells_B.db, clock={name=ick,period=1.6ns}, max_delay=0.8）→ 5 维全异击破硬编 A
- 判分纯 stdlib python3 + tclsh `info complete`（无 DC license）：check.py 19 条 a-s 独立断言
- 5 negatives + §4.9 三假
- 关键判分点：候选必须**不**含 `ungroup -all`/`set_flatten`（层次保留）+ **不**对子模块 `set_dont_touch`（GTECH bug）+ 含 LVS-only 过滤 + 组合守卫 + 时钟/IO 约束 + reports + write
