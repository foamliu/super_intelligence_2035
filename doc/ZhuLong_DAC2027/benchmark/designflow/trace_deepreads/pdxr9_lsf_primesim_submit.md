# pdxr9 深读 — LSF primesim SPICE 提交流自动化

## trace
- session: 1791967220671_pdxr9.messages.json (73 msgs, 338KB)
- user: alrenc @ hfeg0pkn004 (10.129.2.13)
- mc=22, tools: 18 netlist, 9 calibre, 7 hspice, 4 spectre, 4 pyAether, 2 virtuoso, 2 innovus
- domain: eda_other (LSF 作业提交流自动化 / flow infra)

## 用户意图轮（提出目标，无根因/无修复）
- msg0: 「我在服务器上丢了两个job，可以看下排队到什么地步了吗」(查 LSF 队列状态 — ops 前置)
- msg23: 「你执行切换的操作」(bmod 切换作业队列)
- msg37: 「帮我把当前路径下的POR_Sim_FF1d3.sp丢到fqueueAry3上去，用16核跑，输出文件夹带前缀RESULT」(提交 primesim SPICE 仿真到 LSF)
- msg46: 「bsub -q fqueueAry3  primesim -spice -i ./POR_Sim_OCoffmargin_sweep_D1.sp -o ./RESULT_POR_Sweep_D1_Ary2/ -np 16 参考这个脚本，替换成POR_Sim_FF1d3.sp」(给参考 bsub 模板，要求适配替换输入文件) ← A档合格意图轮

## 助手交付链
1. precheck_ff1d3.sh — 只读检查 .sp 存在 + primesim 位置 + 现成 helper
2. inspect_submit_pattern.sh — 读 run_sim_fqueueAry3 helper + .sp head + bhist 615053
3. submit_ff1d3.sh v1 — cd workdir + sanity + `bsub -q fqueueAry3 primesim -spice -i ./POR_Sim_FF1d3.sp -o ./RESULT_POR_Sim_FF1d3/ -np 16` + bjobs verify
4. Job 678676 提交后被秒杀 (EXIT, exit1, 0sec CPU, 仅 1 slot)
5. 诊断: primesim -o outdir mkdir 处理 + esub 链 (esub.fqueue 仅精确匹配 fqueueAry 强制 -n4; esub.smallslot 只管 smallslot; etcheck/runlpe 不负责 fqueueAry 核数映射) → -np 16 未映射成 16 task
6. submit_ff1d3.sh 重构 + resubmit → Job 679570 submitted to fqueueAry3 ✓

## 金洞察 (gold insight for design_flow)
- bsub CWD = 提交时 CWD → 脚本须先 `cd "$W"`
- 输出目录命名约定: `RESULT_<input_basename>/`（参考模板的 -o 也按此命名）
- **-np 16 → 16 Task(s) 的映射依赖 esub 链，对 fqueueAry3 不生效** → 稳健提交须同时显式 LSF `-n <np>`(slot) + primesim `-np <np>`(并行)，不能只靠 primesim -np
- 提交后须捕获 JOBID + bjobs 验证；EXIT 作业须能进 diagnose 模式 (bjobs/bhist/mail-spool)

## case 设计 (B档 synthesized, eda_other, L2)
- verb: lsf-primesim-submit-flow-build
- 交付 = submit.zip{submit_sim.sh + adapt_bsub.py + README.md}
  - adapt_bsub.py: 纯 stdlib (argparse/json/re/shlex)，解析参考 bsub 行 → 适配目标 input/outdir/queue/np，输出 bsub 行 + JSON 报告
  - submit_sim.sh: bash 流程驱动，--dry-run(默认)/--submit/--diagnose <jobid> 三模式
- L2: judge env 无 LSF → check.py 用 --dry-run(--json) subprocess 真跑候选 + --diagnose 走 fixture env
- 隐藏 B: 5维全异 (queue fqueueHv1/np 32/ref input amp_dc_sweep.sp/ref outdir RESULT_amp_dc_hv/target vco_phase_noise.sp/out-prefix OUT)
- 16 条件 a-p; 5 negatives; §4.9 三假
