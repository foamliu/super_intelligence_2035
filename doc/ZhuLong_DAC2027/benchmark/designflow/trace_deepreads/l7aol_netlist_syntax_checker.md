# l7aol — SPICE netlist syntax/format checker (jason17w)

- trace: `1790563683904_l7aol.messages.json` @ hfeg0pnd002, user `jason17w`, mc=288
- size 745KB / 226 msgs (118 user / 108 asst) / tools: editor 58, run_approved_command 31, read_files 15, list_allowed_files 8
- 单条 user_input: "这个模型能吃下多大的上下文，100万行的netlist可以直接吃吗，我想对netlist文件的一些语法、格式做检查"
- 目标网表: `/home/jason17w/0925/vcap_controller_0923/netlist` (vcap_controller, 大文件)
- agent 自驱迭代 33 版 `netlist_checker.py` (58 editor ops)：流式 .subckt/.ends 配对+嵌套、X 实例 pin 数 vs 定义、MOSFET w=/l= 必参、`+` 续行校验、dot-command 校验、格式(tab/trailing/long-line) + summary 报告
- 用户抓 bug 模式 (同 1i0em): `+` 续行不拼接 → X 卡 cell 名/pin 数取错
- 合成 case: EDA-Eval-DesignFlow-NetlistChk-001 (schematic_netlist 扩量#4, **L1** 补牙)
- 判分 discriminator: 隐藏 B (bufB/invB/nor2B/vcap_top_B/danglingB, 结构全不同) + Xn0 跨 `+` 续行 (line20+21) + 前向引用 + danglingB 未闭合 + 缺 w/l 的 MOSFET；硬编 A 名/行号或逐行不拼接均败
- ref 本地 14/14 PASS + §4.9 三假 (empty/print_expected/ref_core_deleted) 全 FAIL + 2 naive 全 FAIL
- 台账: l7aol → case (28 covered / schematic_netlist×4)
- ⚠️ §5 L1：本轮为补牙 L1（mc>=150 <2MB 新用户池中无可自包含复现的 L2 trace，L2 候选均 >2MB / GUI pyAether / 集群 LSF 依赖巨大外部 /rundata 文件）。下轮优先 L2。
