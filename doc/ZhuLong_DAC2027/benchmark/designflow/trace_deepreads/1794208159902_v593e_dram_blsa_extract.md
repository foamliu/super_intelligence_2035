# trace_deepread · v593e (1794208159902_v593e) · DRAM BLSA + BL loading netlist extraction

- sid: 1794208159902_v593e | user: t0002614 | host: hfeg0pkn004 (10.129.2.13) | mc 82
- kw: aether:346;netlist:295;schematic:114;mixed-signal:51;verilog:41;analog:31;calibre:27;hspice:25
- msgs: 48 | user turns: 2 | agent: lead | glm family
- src: scp 10.129.2.13:/home/t0002614/.cline/data/sessions/1794208159902_v593e/1794208159902_v593e.messages.json (208155B)

## 真实任务（用户原话）
1. 「我想从DRAM的design中抽取一个BLSA和BL上的loading出来做仿真，怎样抽取网表最方便」
2. (追问) 「Aether中在DM界面查看view，其中config view的作用是什么」

## agent 行为
- Q&A/how-to 型，零真实 netlist 文件读写（权限/路径无关，纯 RAG + 手册检索）。
- 用 aether-tool-qa skill → search_kb.py（自写检索脚本，python-runner profile 调用，踩了 shell-runner/python-runner filePath 参数坑 2 次后修正）→ grep 群问答 + 读 part_I/II/VIII 手册章节。
- 最终回答给出 3 条路线：① 独立 tb + 等效 BL loading（Cbl 集总电容 + 1~2 真实 access 管）② File->Export->Netlist 层级控制（Stop View List / Skip Cells Below 把不需分支导成空 subckt）③ config view 绑定 mixed-mode view。
- 追问 config view：答「混合模式仿真视图配置，Global Bindings = Library/View/Stop List，Template MMSIM/RCE」。

## 交付物判定 / reframe
- 用户真实意图 = 局部网表抽取（BLSA + BL loading）做 spice 仿真。属 spice_sim 域，真实用户意图。
- agent 仅给 how-to，无脚本无真实文件 ⇒ harness-for-teeth reframe：Q&A → produce 可复用工具。
- 工具 = extract_loading.py：参数化 SPICE 层级网表解析，给定 target-inst + loading-net，抽 target subckt def + 共享 loading-net 的其余顶层实例（= loading），emit extracted.sp + report.json。纯 python 无 EDA 二进制 → layer=L1。
- asset_fidelity = format-faithful：真实 netlist 不可便携 + agent 未读真实 netlist，按 SPICE 层级网表格式 + DRAM BL slice 拓扑重建 design_A.sp（BLSA subckt + DRAMCELL access 阵列）。
- hidden B = 结构性差异：SENSEAMP_B / BITLINE_B / RAMCELLB(ports BLPIN WLB CAPB) / 5 access + 1 unresolved trap(MISSINGCELL def 缺)；B2 anti-stub 同拓扑 6 access 0 unresolved。

## 断言 k=14 (a-n)
a zip 无泄漏 b py_compile c argparse(--netlist/--target-inst/--loading-net/--outdir) d 跑B产extracted.sp+report.json e report结构 f target_subckt.name==SENSEAMP_B & def_present g target_subckt.ports==[BITLINE_B,BITLINEB_B,SAEN_B] h loading_net==BITLINE_B i total_loading==6 j unresolved==[XTRAP_B0] k loading_instances 排除 target_inst 自身(XSA_B0不在内) l extracted.sp 含 .SUBCKT SENSEAMP_B ... .ENDS SENSEAMP_B m anti-stub B2 total_loading==6 & unresolved==0(≠B) n 无 A token(BLSA/DRAMCELL/XSA0/XACC0) 且 report 不硬编 A 值 + 确定性3次一致 + 代码实质≥25行
