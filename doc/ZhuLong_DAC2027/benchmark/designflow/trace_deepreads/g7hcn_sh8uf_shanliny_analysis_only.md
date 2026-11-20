# Deepread: g7hcn + sh8uf (shanliny@hfeg0pkn001 / 10.129.2.10) — ANALYSIS-ONLY, parked

> Round r275. 两 session 均 **analysis-only**（assistant 只读+解释，0 write/edit），无可执行 golden 交付物 → 不符合 design_flow 契约 → **parked**。

## g7hcn (mc15, 1.83MB, 24 msgs)
- keywords: `systemverilog:188;verilog:86;rtl:32;analog:7;synthesis:4` (digital-lean)
- USER#0(逐字): `我需要你对这个SRAM验证程序的逻辑进行检验，无论timing_validation开没开启，monitor时钟块里的值都是时钟上升沿之后更新，并且在时钟稳定后对sv和dut的值进行检验` + 11 个 .sv 附件
  - = **分析/检验任务**（非代码产出任务）→ A-faithful 任务说明但 deliverable=分析报告(text)，不匹配 zip 契约
- USER#6: 质问 timing.vcd 为何能驱动 DUT（指出现象，hint-ish）
- USER#18/#19: `timing_validation时q_ref的输出逻辑应与非timing时相同，给我更正` / `将所有信号放在clk下降沿改变值...更正timing时的逻辑` —— **给修复方向=hint** → 非 A-faithful
- assistant: 7 read_files + 1 search + 1 run_commands，**0 write/edit**。末轮 #22 说"现在我来更正"后会话结束，**未产出修正代码**。
- 结论: trace 末尾无用户接受的代码产物 → 无 trace-faithful golden；B-档需自行合成 SV 修正(VCS 验证成本高) → **parked**（分析型 trace，非 design_flow 契约适配）

## sh8uf (mc23, 1.10MB, 44 msgs)
- keywords: `verilog:97;synopsys:13;rtl:5;aether:4;synthesis:2`
- USER#0(逐字): `这个model在启动了testmode的情况下何时会导致输出结果为x，见timing.vcd中qut_q和log文件，在有正常写和只触发了时钟长度违例的情况下，为什么后续的正常读无法读出结果？`
  - = **debug 问答**（问"为何"，非"修代码"）
- USER#27/#42/#43: 澄清/继续
- assistant: 15 read_files + 1 search + 1 run_commands + 3 list_allowed_files + 1 policy，**0 write/edit** → 纯解释，无交付物
- 结论: Q&A trace → **parked**

## 关键修正 r274（重要！）
r274 称 shanliny 的 digital 候选"未提及 purged"但实际**全部 EXISTS**（新版 cline 目录结构 `<id>/<id>.messages.json`，r274 误用 flat-file 路径查）：
- yrdts(6.1MB)/32935(6.0MB) too big >2MB
- g7hcn(1.8MB)/sh8uf(1.1MB) EXISTS 但 analysis-only（见上）
→ shanliny 的 session 不缺，只是 analysis/Q&A 型不适用 design_flow。
→ 真正可用的 digital code-fix 候选 = **lorikx pvx74**（见 pvx74 deepread note，已 deepread 排队 next round 出 case）。
