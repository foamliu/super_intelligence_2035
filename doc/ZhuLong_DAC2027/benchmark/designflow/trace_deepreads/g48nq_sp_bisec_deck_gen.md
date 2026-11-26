# trace_deepread — g48nq (adaml@hfeg0pkn002, mc=192, spice_sim)

**session**: `/home/adaml/.cline/data/sessions/1792131744105_g48nq/1792131744105_g48nq.messages.json`（707KB, 102 msgs, dict schema `{version,updated_at,agent,sessionId,messages,system_prompt}`）

## 选轮（用户原话）
- **U#1** (i=0): `<user_input mode="act">[skill-creator] 帮我生成一个skill，把生成的skill保存到～/.cline/skills/ 目录内。以下为具体要求：参考并且总结 /proj/drvsa/V0/workdir/adaml/drgqa_simulation/Lbx_sim_DQ_TX_schematic_ALPS/Postsim/DR9500_woCH_woFFE.sp, /proj/drvsa/V0/workdir/adaml/drgqa_simulation/Curry_tes_DL_CDL_schematic_ALPS/Pre_IOlib/*.sp /proj/drvsa/V0/workdir/adaml/drgqa_simulation/Lbx_DL_CPAMP_TB_schematic_ALPS/Postsim/*sp 等目录下撰写的电路spice仿真激励文件，生成由于撰写电路testbench spice仿真激励的skill，要求：1.激励文件高度结构化，可复用。2.仿真激励包括：仿真器的option, spice model的工艺corner，电源的电压，温度，designer在netlist或在激励中定义的pamameters，netlist, 后仿用的spf文件（如有），analysis，仿真波形或者分析输出结...`
- **U#2** (i=40): `对于项目m2701, 其spice model的文件目录是/proj/m2701/V0_DDR4/model/current/，仔细阅读里面的文件，更新skill里面关于model的内容。`
- **U#3** (i=64): `调用这个skill的时候，发现存在skill没有充分考虑EDA仿真器自身的能力来做仿真分析。比如仿真器自带bisection优化，调用后没有用这个方案，反而用sh脚本做分析。针对这个情况，更新skill，要求写激励和做分析的时候，首先检查仿真器是否有内建的功能来实现需求。`

## 选轮裁定
- **A 档不可用**：U#3 已指出根因（"skill 没充分考虑仿真器自身能力"）+ 给出修复方向（"首先检查仿真器是否有内建功能"），按红线 §A-②「凡用户已指出根因或给出修复方案的轮不得作 A 档任务说明」⇒ 用 **B 档 synthesized**。
- U#1 是提需求轮（生成 skill），但需求对象是 skill markdown 本身（L1 文本/模板），且与既有 FifoStimulusGen-001（同 skill 的 USAGE，curryxu/z7n9b）在"13-section testbench 生成"上重叠。
- **nrep6 教训应用**：对 skill-creator meta-task，应继续挖到它要自动化的**具体 EDA 输出**。g48nq 的 skill 自动化的具体 EDA 输出 = 用仿真器内建 bisection/optimization 写的 `.sp` 分析 deck（U#3 的核心诉求）。该角度**与既有 case 不重叠**（BisecMt0SmCalc 是 bisec 结果后处理，非 deck 生成；SaDcSweepTbGen 是 DC sweep deck，无 bisection/optimization；FifoStimulusGen 是端口驱动的 testbench，非内建搜索 deck）。

## assistant 工具链（102 msgs）
- editor 29 / list_allowed_files 17 / read_files 17 / search_codebase 2 / skills 1 / get_agent_policy_status 1
- 产出 `/home/adaml/.cline/skills/spice_tb_stimulus/`：SKILL.md(18725B,13-section 骨架+9 验收标准+19 已知陷阱) + 00_INDEX.md + references/{builtin_analysis.md(5096B),template_tran_io.sp(4593B),template_analog.sp(3788B),template_measure.sp(2403B),model_libraries.md(5009B),simulator_options.md(3200B),corner_run_helpers.md(3143B)}

## 金标准（具体 EDA 输出 = 内建 bisection/optimization deck）
来自 `references/builtin_analysis.md`（经官方 demo `demo/hspice/bisect/dff_top.sp`、`ciropt/ampopt.sp` 验证语法）：

**bisection（单临界值）**：
```spice
.param DelayTime = opt1 ( 0.0n, 0.0n, 5.0n )
.tran 0.1n 8n sweep optimize=opt1 result=maxvout model=optmod
.measure tran maxvout MAX v(d_output) goal='v(vdd)'
.model optmod opt method=bisection relin=1e-4 relout=1e-4
```
**optimization（多目标）**：
```spice
.param wm1=opt1(60u,20u,100u) wm5=opt1(40u,20u,100u)
.tran 2.5n 300n sweep optimize=opt1 results=delayr,tot_power,area_min model=opt
.model opt opt itropt=40 close=10 relin=1e-5 relout=1e-5
.measure delayr trig at=0 targ v(voutr) val=2.5 rise=1 goal=100ns weight=10
.measure tot_power avg power goal=10mw weight=5
.measure area_min min par(area) goal=1e-9 minval=100n
```
原则：`.sp` 激励本身是"分析程序"，**不写外部 sh/python 搜索循环**。

## case 合成
**EDA-Eval-DesignFlow-SpBisecDeckGen-001** (spice_sim/B-synthesized/L1/k=16)
- deliverable = `bisec_deck_gen.py`（CLI `<spec.json> <out_deck.sp>`，stdlib only）→ 8-section 结构化 .sp deck
- 资产 A=spec_a.json(bisection: DelayTime/maxvout/top_tt/25)+netlist_stub.sp+task_brief+output_format_spec
- 隐藏 B1=spec_b1.json(bisection 泛化: ClkSkew/vout_half/top_ff/-40) / B2=spec_b2.json(optimization 反硬编码+异型: wm1+wm5, results=delayr,tot_power,area_min, goal+weight, itropt/close, 无 method=bisection)
- reference=bisec_deck_gen_ref.py（standalone）+ gen_assets.py（spec source of truth + render_deck）
- check.py 16 断言(a-p, subprocess 真跑 B1+B2, 正则验内建 optimize 构造 + 反硬编码 + 无外部循环 + 确定性)
- 自验: ref PASS 16/16 + 6neg(naive_empty 3/16 / hardcoded_a 9/16 / sh_loop 5/16 / only_measure 7/16 / ref_core_deleted 14/16 / bisection_for_opt 12/16)全 FAIL NEG_RC=0 + §4.9 三假(empty_shell 3/16 / only_print 2/16 / ref_core_deleted 14/16)全 FAIL + k=16>=8 ✓ + test 字段与盘上 check.py 字节同步(sha1 ac0e8f75)

## 教训
- g48nq 首轮(00:22)被 park 为"skill-creator meta-task not produce-task"，与 nrep6 首轮"meta-skill DOE reject"同模式。**对 skill-creator meta-task，必须挖到它要自动化的具体 EDA 输出**（这里=bisection/optimization deck，非 skill markdown 本身）。
- 区分 skill-CREATION（g48nq，造 skill 骨架+内建分析原则）vs skill-USAGE（FifoStimulusGen/z7n9b，用 skill 造具体 testbench）：前者 gold=skill 自动化的 EDA 输出结构，后者 gold=具体网表的 testbench。
- U#3 的"内建优先 vs 外部 sh 循环"是该 skill 最具区分度、可判分、且不与既有 case 重叠的角度——成为本案的核心断言（j: 无外部 sh 循环 + e: sweep optimize 构造）。
