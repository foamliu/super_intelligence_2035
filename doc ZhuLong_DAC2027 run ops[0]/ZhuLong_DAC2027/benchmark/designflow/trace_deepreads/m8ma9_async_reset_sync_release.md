# 深读笔记 · session 1793843537860_m8ma9 (e0045128 @ hfeg0pkn005 / 10.129.2.14)

- trace_source: user=e0045128, host=hfeg0pkn005 (10.129.2.14), session=1793843537860_m8ma9.messages.json, mc=22
- agent: zhulong (lead), model=deepseek-v4-flash, cwd=/home/e0045128/sandbox
- 22 msgs, 61580 bytes (从 .snapshot/hourly-new.2026-11-06_1300 取，live sessions 已清理)
- 关键词: genus:160;cadence:39;rtl:17;aether:13;innovus:9;verilog:8;tempus:5;synthesis:4
- tools: 3 innovus, 2 pyAether, 1 synthesis, 1 netlist, 1 "lang":"tcl" (注：均为概念讨论中提及，未真跑工具)

## 用户轮（逐字原文）

- USER#0 (msg0, ts=1793843538290): `<user_input mode="act">Hi</user_input>` — 打招呼，弃。
- USER#2/#3 (msg2/3): `请使用中文和我沟通` — 语言偏好，弃。
- USER#5/#7 (msg5/7, ts=1793843761614/1793843931853): **`异步复位同步释放电路是什么样的`** — 核心问题轮（重复发一次因 msg6 assistant thinking 空回复）。gold 答复=msg8：异步复位同步释放电路详解（recovery/removal 时序→亚稳态→2 级 DFF 串联 D 接高→异步生效/同步释放→Verilog 实现 reset_sync module with posedge clk or negedge rst_n）。
- USER#9 (msg9, ts=1793856677958): `Genus legacy是什么版本` — 概念问题，gold=msg17（Genus legacy 模式 = RC 兼容模式，legacy_ui_mode 变量，genus -legacy_ui 启动）。
- USER#18 (msg18, ts=1793856833782): `Genus for Legacy UI` — 概念问题，gold=msg21（Legacy UI vs Common UI 命令对比表）。

## 本轮取材决策

- 取 USER#5/#7 `异步复位同步释放电路是什么样的` 作 A 档 faithful 任务说明（用户提出需求/目标轮，未指出根因/未给修复方案，符合 A 档选轮规则）。
- domain=digital（异步复位同步释放是数字 IC 设计经典电路）。
- level=L1-static（行为模型 + 原理说明，无需真跑 EDA 工具）。
- gold 答复关键事实（来自 msg8）：
  1. 2 级 D 触发器串联（two-stage DFF chain）
  2. D 输入端接高电平（D=1'b1）
  3. 原始 rst_n 接两个 FF 的异步复位端
  4. 两个 FF 同一时钟 clk 驱动
  5. 异步生效（assert）：rst_n=0 时两 FF 立即拉低，无需等时钟
  6. 同步释放（deassert）：rst_n=1 后第 1 个时钟沿 FF1<=1，第 2 个时钟沿 FF2<=FF1=1，输出才释放
  7. 亚稳态防护：FF2 给 FF1 一个时钟周期稳定
  8. recovery time（恢复时间）/ removal time（移除时间）约束
  9. Verilog: `always @(posedge clk or negedge rst_n)`, reset 分支 `<= 0`, 非reset分支 `ff1<=1'b1; ff2<=ff1;`, output `rst_sync_n=ff2`

## 交付设计

- 契约: mode=design_flow, entry_point=outputs/submit.zip, test=check(deliverable, workdir)
- 交付件: submit.zip 内含 `reset_sync_model.py`（Python 行为模型）+ `explanation.md`（原理说明）
- 接口（task_brief ≤3 行，只写交付接口与文件位置）:
  - `reset_sync_model.py` 提供函数 `simulate(rst_n_seq: list[int]) -> list[int]`，输入每时钟周期的 rst_n 值（0=有效/低，1=释放/高），返回每周期的 rst_sync_n 输出值（0=有效，1=释放）。
  - 电路=2 级异步复位同步释放（async assert / sync deassert），SUT 须自行从问题理解行为。
- 隐藏 B: 不同 rst_n 时序序列（含中途重新 assert、长保持、边沿对齐等），check 跑候选模型在 B 上验行为。
- check ≥8 conds: zip 结构 / py_compile / 模型可调用 / [A] 基本时序(3 周期 assert→2 周期释放延迟) / [B] 中途重新 assert 异步立即归 0 / [B2] 长释放保持 / explanation 关键术语(亚稳态/recovery-removal/两级/D=1/异步生效同步释放) / 反硬编(源码不含 A 的硬编输出序列) / 2-FF 延迟(释放后输出恰 2 沿后变 1)

## 弃用轮

- USER#9 (Genus legacy) / USER#18 (Genus Legacy UI): 同会话内独立概念问题，不构成本轮任务（可作为未来 case 的 trace 复用线索，但与本电路问题无关）。
- USER#0/#2/#3: 寒暄/语言偏好，弃。
