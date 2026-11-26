# 深读笔记 · 1793874126039_qvr6i · e0039602 @ 10.129.8.235 (hfeg0plg103) · mc=148 · schematic_netlist

> trace 来源：`/home/e0039602/.cline/data/sessions/1793874126039_qvr6i/1793874126039_qvr6i.messages.json`（801KB，108 msgs，2 轮用户交互）
> 选料轮：shard D #541（2026-11-12）。fresh-sid（不在 4-shard ledger / all_shard_sids）。

## 用户真实任务（逐字 U#0）

> rules_prompt1.py这个脚本描述的是各个网表当中的model转换为sv文件需要依照的逻辑，比如
> final_merged_netlist_digitial.v到simlib_drcoa_digital.sv   final_merged_netlist_stdcell.v到
> simlib_drcoa_stdcells.sv     final_merged_netlist_stdcells_ac.v到simlib_stdcells_ac.sv   请你
> 仔细阅读这个脚本，整合一下里面prompt格式，让他变得更易于AI读取，如果你觉得里面目前给出的
> 几个示例不够典型，你也可以再修改一下，总之就是这个文件现在有一些没有逻辑，有一些乱，你把他
> 弄整洁了让AI更容易看懂，注意不要删除里面表达出的知识

**任务性质**：文本重构 / prompt 模板整理（L1 纯 stdlib parse/transform）。
`rules_prompt1.py` 内 `RULES = """..."""`（约 700 行）描述"原理图网表 module → simlib SV 库文件"
的转换规则，分节 `【0】~【8】`（【7】含 7.1~7.5 子节），含查找表 / 模式 A-E / module 骨架 /
时序默认 / few-shot 示例 / BUILDING_BLOCK_CATALOG。用户要：把凌乱、无序、重复的 RULES 文本
重排成清晰层级结构，便于 AI 读取，**且不得删除任何知识**。

## agent 实际做法

1. list_allowed_files → read rules_prompt1.py 全文（分块，因截断多次读）。
2. 把 RULES 重排为 `【0】~【8】` 顺序，【7】拆 7.1~7.5，顶部加工作流程摘要，去重，保全部知识。
3. 用 editor 分块写 new_rules_body.txt → apply_rewrite.py 把新 body 拼回 rules_prompt1.py。
4. 中途拼接触丢闭合 `"""` 导致文件损坏；重拼恢复 split 代码 + BUILDING_BLOCK_CATALOG。
5. verify_rules.py（py_compile + AST 提取 RULES + split 完整性 + section 头全在）+ exec_test2.py
   端到端执行（RULES_INSTRUCTIONS / FEW_SHOT_EXAMPLES / build_prompt 全过）。
6. 清理临时脚本。U#2 问"工作在哪个目录"，答 `/home/e0039602/Documents/netlist_change`。

## 关键事实（用于 A/B/C 合成）

- 网表类型 → 输出 SV：`final_merged_netlist_{digital|stdcell|stdcells_ac|io|analog}.v → simlib_drcoa_*.sv / simlib_stdcells_ac.sv`
- 一级转换查找表：标准门/单元 → simlib cell（INVX4→simlib_inv_x4 等）
- 模式 A-E：A=单 module 全量；B=静态前缀+动态 user；C=仅 catalog+tagged source；D=仅 instructions；E=全量+AVAILABLE
- module 骨架（【7】）：7.1 布局（module 声明→端口→内部线→实例→specify）；7.2 monitor；7.3 spec_gates(MGM)；7.4 specify；7.5 AVAILABLE physical cells
- 时序默认：tsetup / thold / tco（值因网表而异）
- few-shot 示例：module 名 + 网表片段 → SV 片段
- 凌乱特征：节序乱、有重复节、工作流程摘要行被埋在中间节、7.x 子序乱

## benchmark 抽象（A/B/C）

SUT = `netlist_sv_rules_reorg.py <input.txt> <output.txt>`：读凌乱 RULES 文本 → 按 `【N.` 锚点
解析节 → 按 N 升序重排 → 同 N 重复节丢弃(去重) → `工作流程摘要:` 行提取到顶部 → 【7】内 `7.x`
子行升序 → 输出干净版本，保留全部事实行。纯 stdlib（re/sys）。
A(可见)=analog/stdcells_ac 网表值集；B(hidden)=digital/stdcell；C(anti-hardcode)=io。
A/B/C 的 gate 名 / 时序值 / 网表映射 / 示例 module 名全不相交。check.py 16 条件 a-p 独立
（结构 + 事实保留 + B/C 反硬编码 + 3-seed + §4.9 三假）。

## 域判定

schematic_netlist（网表 model→SV 转换规则文本重组）。actual_tool_demand 100% 文本 parse/transform
（agent 仅 read/editor/run_approved_command 跑 py_compile+exec，无 EDA 运行时）。L1。
