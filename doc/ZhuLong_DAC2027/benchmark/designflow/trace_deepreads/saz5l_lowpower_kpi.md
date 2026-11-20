# Trace deepread — saz5l (shard A, r224)

- **session**: `1792562152582_saz5l` · user `e0046913` · host `hfeg0pkn003` · mc=40 (24 synthesis + 16 netlist)
- **file**: `/home/e0046913/.cline/data/sessions/1792562152582_saz5l/1792562152582_saz5l.messages.json` (50746 B, 11 msgs)
- **scan source**: daily log 20261108 (11/05 scan pool strict-digital evaporated; daily-log fallback finder_A.py)
- **agent**: lead (cline)

## 对话流
- msg#0-2 (user, 三连重复): 新入职 ALS/DTP&DS/CAD 团队社招员工(前司数字 BES 中端), 主管希望试用期 KPI 三个目标里两个擅长中端+一个挑战性(前端/后端), 请推荐几个"前端或后端环节"并简介+理由
- msg#3 (assistant): 对齐中端背景资产(SDC/netlist/等价性验证/脚本化), 推荐 CTS 质量自动化比对 / power-aware 等价性验证 / IR-drop 等候选
- msg#4 (user): 详细谈"CTS 质量自动化比对"(工具/目标/衡量标准)
- msg#5 (assistant): CTS 全展开(位置/采集/工具/目标/衡量标准/KPI 写法)
- msg#6 (user): 详细谈低功耗设计在数字 CAD 中的具体内容
- msg#7 (assistant): 低功耗全展开(功耗原理/全流程各阶段/工具/CAD 落地/中端切入点/衡量标准), 末尾提议细化"UPF一致性自动核对"或起草 KPI
- msg#8 (user, 不完整): 模仿 Top STA Flow 示例生成 low power flow KPI(只给目标描述①-④, 衡量标准空)
- **msg#9 (user, 完整) = A 档任务说明逐字原文**: 模仿 Top STA Flow 示例(目标描述①-④ + 衡量标准①-⑤), 生成试用期针对 low power flow 的 KPI 目标描述与衡量标准
- **msg#10 (assistant) = gold**: 目标名称 `Low Power Flow搭建（UPF一致性校验与功耗回归分析）`; 目标描述①-④(UPF/Power Intent 三阶段一致性校验/功耗回归分析体系/power-aware 等价性验证 isolation/retention/level-shifter + mismatch 根因/IR-drop 初筛 + Low Power sign-off checklist); 衡量标准①-⑤(覆盖率≥95% 可稳定执行/功耗报告分域回归比对/X block mismatch 分类/活动率 saif-vcd 回灌/tape-out 回归迭代无阻塞)

## A 档取轮判断
- msg#9 是"提出需求/表达目标"轮(要一个 low power KPI), 用户未指出根因也未给修复方案 → 符合 A 档选轮规则
- 任务性质: 纯文本生成咨询(无真 EDA 工具执行); 24 synthesis + 16 netlist 的命中来自 assistant 文本里概念性提及, 非工具调用
- 契约适配: reframed 为可复用 KPI 生成脚本 gen_kpi.py(读 config: flow_name/subtitle/concept_map/example_template → 解析示例段 + concept_map 最长键优先替换 + flow_name 重写 + ①-⑮ 重编号输出 markdown); 忠于用户原意(产出 low power KPI)同时满足隐藏 B 泛化(不同域 DFT + 不同示例结构)

## gold 关键事实(供断言)
- A 示例结构: 目标描述 4 条 + 衡量标准 5 条 (Top STA Flow)
- B (隐藏) = DFT Flow, 示例 = CDC Flow (目标描述 3 条 + 衡量标准 4 条, 结构与 A 不同)
- A 低功耗域词: UPF / Power Intent / isolation / retention / level-shifter / IR-drop / 功耗回归
- B DFT 域词: DFT / scan chain / ATPG / 故障覆盖 / 测试覆盖率 / sign-off checklist
- 反硬编: B 输出不得含 A 低功耗词 + 不得含 A 示例词(Top STA Flow / SDC约束 / timing closure)
