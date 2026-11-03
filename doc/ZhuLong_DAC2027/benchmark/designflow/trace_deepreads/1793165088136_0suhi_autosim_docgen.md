# Deepread — 1793165088136_0suhi (e0046686 / hfeg0pkn005, mc=149)

- **session**: `/home/e0046686/.cline/data/sessions/1793165088136_0suhi/1793165088136_0suhi.messages.json` (1.92 MB, 313 msgs)
- **user / host**: e0046686 @ hfeg0pkn005 (10.129.2.14) ; model deepseek-v4-flash family
- **tools (summary.tsv markers)**: 928 netlist / 101 calibre / 29 hspice / 8 spectre / 2 virtuoso / 1 schematic / 1 innovus — markers 来自被读源码内容，非工具运行
- **shard / domain**: A / eda_other（CAD 工具文档生成）— 但**不可合成**（见下）
- **status**: parked — doc-gen trace, 不适配 design_flow 隐藏 B / 真跑候选契约

## 真实任务主线（9 条 substantive user_input）
e0046686 让 cline 为其 `autosim` 项目（SRAM 自动仿真工具：`SRAMAutoSim` Qt GUI + `autosim_script` 后端脚本）**生成标准 README + 详细设计说明文档**。
- **U[0] (msg#0, 1231c) — A-档候选 seed**:
  > @TASK_EXP_AUTOSIM.md 你现在是资深的半导体CAD软件开发工程师… 接下来我一次性给你全部项目代码和项目信息，请你一次性完成下面所有工作… 1.代码梳理 2.项目概述 3.生成标准完整 README.md（含全部章节）4.额外单独输出一份【详细设计说明文档】… 工程目录位于 /home/e0046686/autosim/；下面有两个目录：1、SRAMAutoSim 2、autosim_script；为这两个工程分别按照以上要求生成…
  - 纯需求委托轮（提出目标 + 输出规范），🚫 无根因/修复 → 合 A-档选轮规则②
- U[168] (112c): 「GUI界面上通过CPU Core选择 CPU 核数，是选取的GUI工具在本地执行任务时候的核心数，还是对应的后端脚本提交bsub时在集群中占用的核心数？」— 代码语义澄清问答（gold = 解释性回答，prose）
- U[175] (114c): 「GUI工具生成netlist或者vector时也是单进程执行吗？…」— 澄清问答
- U[189] (2681c): 「@TASK_EXP_AUTOSIM.md 有更新，按照更新后的文档重新为两个工程输出详细设计文件」+ 扩展任务清单（mermaid 架构图/流程图、模块表、≥5行/章）— 重新生成
- U[240/256/258]: 「继续」「继续执行」「继续啊？为什么不执行？」— 通用续轮，非任务
- U[302/303]: 「有几处语法错误导致无法渲染：… mermaid Parse error …」— **用户已指出根因（mermaid 语法错误 + 具体 parse error）→ A-档选轮规则② 排除**

## assistant 工具链
editor 写 markdown 设计文档（多轮 insert/edit）→ 用户在 U[302/303] 报告 mermaid 渲染语法错（`{complier}` 含大括号、`AW[6:5]...` 冒号、`I -->` 末尾）→ assistant 修 mermaid 块。**无 EDA 工具运行、无脚本产物**；全程是「读 autosim 源码 → 写 markdown 文档 → 修 mermaid 语法」。

## 不可合成理由（关键）
1. **L1 文档生成**：交付件 = markdown 设计文档（prose + mermaid 图）。§5「新建 case 只做 L2/L3」；L1 doc-gen 通过率偏高，违反难度校准。
2. **隐藏 B 机制不适配**：§4.1 要求 B（不同输入）不进 SUT 沙箱、check() 只跑 B。doc-gen 任务中候选只对 A 产文档，无法在 B 上重跑候选（除非交付件是「文档生成脚本」而非文档本身 — 但用户要的是文档，交付脚本不 faithful）。
3. **§4.2 真跑候选弱**：可在候选文档的 mermaid 块上跑 mermaid 解析器（subprocess），但断言多为「章节存在 / mermaid 可解析」式结构断言，§4.3「🚫 仅成员名/仅子串出现」风险高。
4. **金标巨大**：完整设计文档跨多轮生成（数千行 markdown），autosim 源码工程大，提取为 attachment 重，超本轮预算。
5. **mermaid 修复子任务**（U[302/303]）虽断言友好，但用户已给根因 → 规则② 排除作 A-档 prompt；用 U[0]/U[189] 作 prompt 则交付范围过大。

## 结论
trace 是真实的 CAD 工具文档生成场景，但不适配 design_flow「隐藏 B + 真跑候选 on B + ≥8 独立结构断言」契约。parked。pool 约束记录见 MEMORY_A r62。

## 资产（不合成，仅备查）
- A 输入理论位置：`/home/e0046686/autosim/`（SRAMAutoSim + autosim_script 两子工程）+ TASK_EXP_AUTOSIM.md
- gold 理论位置：trace assistant 多轮产出的设计文档（mermaid 修复后版本）
