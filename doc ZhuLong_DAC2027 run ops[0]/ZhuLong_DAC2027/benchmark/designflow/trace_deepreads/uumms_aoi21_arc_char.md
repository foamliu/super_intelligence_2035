# trace_deepread: 1792380576403_uumms — AOI21 标准单元 input-arc timing 表征（Maestro/ADE AMS 流）

- **trace**: e0029308 @ hfeg0pkn001, session 1792380576403_uumms, deepseek-v4-flash, 323 msgs / 7 user turns, status=failed（无 accepted gold result）, mc=343.
- **真实任务**: 用户在 CXMT foundry 环境下为一块 AIOI21 标准单元做 input-arc timing 表征。通过 Maestro/ADE 驱动 AMS 仿真（FineSim + xrun）逐条 input→output arc 测传播延时（tpd），目标是填 cell-library timing 表。trace 里还夹了一段 verilog cell-library extraction + PEX 的前置工作，但核心仿真流是 standard-cell input-arc timing characterization。
- **关键用户轮**:
  - msg[0] 初始环境/工具说明（FineSim/maestro/ADE/PEX 都是 CXMT foundry 工具）
  - msg[~40] AIOI21 cell 接入 + AMS netlist 结构（subckt + testbench + stim）
  - msg[~120] 跑 FineSim → **GLIBCXX_3.4.21 not found**（libstdc++ 版本冲突），FineSim 始终没跑起来
  - msg[~180] 切换到 xrun（AMS），用 Verilog-AMS + SPICE view 跑通
  - msg[~260] 收集测量数据 + 调试 .measure
  - msg[~310] 收尾（session 最终 failed，没有 accepted gold）
- **真实产物**: AMS netlist（AIOI21 SPICE view + Verilog-AMS testbench + stim）、Maestro/ADE test config、137 次 spectre/FineSim 调用（全因 GLIBCXX 失败）、最终 xrun 跑通的延时数据。
- **不可移植部分**: 真实流用 CXMT foundry 工具链——FineSim（spectre 兼容）、Maestro/ADE（ADE Explorer/Assembler GUI driver）、PEX（寄生提取）、foundry specific AOI21 .lib 模型——全部 .75 上不可用。FineSim 因 GLIBCXX 库冲突在 trace 里自始至终没跑通。
- **可复现子技能 (本 case 取的)**: standard-cell input-arc timing characterization 的核心算法——枚举 AOI21（ZN = ~((A1 & A2) | B））的 7 条 input→output timing arc（6 条有效 + 1 条 degenerate），对**非切换输入**给正确的静态 conditioning 让输出真的翻转，逐 (arc, corner, load) 生成 `.alter` 块、真跑 HSPICE、从 `.lis` 按 alter 顺序抠 `tpd`（`failed` → null）、per-arc worst + overall_pass 报告。该子技能不依赖 FineSim/Maestro/ADE，可在 .75 用 HSPICE level-1 MOS 复现。
- **真实陷阱（烤进 case）**:
  1. **conditioning 是核心陷阱**：AOI21 的 A1 arc 必须 A2=1,B=0（或 A2 arc 必须 A1=1,B=0）输出才会翻转。如果 A1 切换时 A2=B=0，输出 ZN 永远不动 → `.measure t_out` `failed` → tpd null。这条 degenerate arc（`a1_rise_deg`）必须显式报 null，不能当 0、不能崩。trace 里 agent 反复在 conditioning 上踩坑。
  2. **FineSim GLIBCXX 冲突**：trace 里 137 次 spectre 调用全失败（libstdc++ 版本不够）。本 case 改用 HSPICE 规避，但"仿真器起不来"的真实失败模式值得记忆——case 里 check.py 会真跑 HSPICE 并校验 baseline 数值，跳过仿真必败。
  3. **`.measure` `failed` 语义**：degenerate arc 或 conditioning 错误时 `t_out` 永不触发 → `tpd = failed`，必须映射 null（not_met），不能当 0（会让 worst_arc 错位）也不能崩（会让 report 缺失）。
  4. **`.alter` 顺序 ↔ arc/corner/load 关联**：`.lis` 按 `job concluded` 分块，第 i 块 ↔ 第 i 个生成的 (arc,corner,load)。错序 → arc↔tpd 错配。
- **distinctness vs 既有 case**: 已有 ClkBufTran-001（单 buffer 上升/下降延时单 deck）、PVTalterChar-001（NAND2 多 alter PVT 角点表征求 tpd，单脉冲第 2 穿越必 failed）、TempThreshChar-001（温度阈值表征）、InvPVTchar-001（INV PVT）。本 case 独特点 = **多输入标准单元的 input-arc 枚举 + 静态 conditioning**——AOI21 是 3 输入（A1/A2/B），每条 arc 需要正确 condition 另两个输入，且存在 degenerate arc（A1 切换但 A2=B=0 → 输出不翻转），这是 ClkBufTran（单输入）和 PVTalterChar（NAND2 双输入但无 degenerate arc 概念）都未覆盖的子技能。
- **去向**: EDA-Eval-DesignFlow-AOI21ArcChar-001 (spice_sim, B档, track faithful, L2, k=13). 自验：ref 13/13 PASS，3 negative 全 FAIL，§4.9 三条假提交全 FAIL。
