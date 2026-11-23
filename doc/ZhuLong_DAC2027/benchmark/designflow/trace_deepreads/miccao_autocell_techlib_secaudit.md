# 深读笔记 — miccao@hfeg0plg92 · 1789631689135_9pcjd

- **trace_source**: user=miccao, host=hfeg0plg92, session_file=1789631689135_9pcjd.messages.json, match_count=57
- **keywords**: techfile:137;schematic:92;.cdl:50;transistor:29;aether:21;netlist:19;lib.defs:18;virtuoso:8
- **domain**: analog_context (techfile/techlib 工艺数据安全审计)
- **size**: 691KB / 56 msgs / 2 real user turns
- **peek 轮次**: r1216 (2026-11-23)

## 真实用户意图（原话）

- U0: 「/apps/proplus/autocell.1.2026.8/autocell/examples/dram 下所有文件里的参数和 /proj/train/ddcpc/libs/TECHLIB_release 里面的参数有类似的吗？进行安全性检查，我怕这个工具写死了我们的工艺数据」
- U1: 「出一份 rep 附件，放到 /home/miccao/autocell/secuirty 下」

## 意图归纳

用户 miccao 担心 AutoCell 工具的 DRAM 示例目录里**硬编码了自家（CXMT G5 CIP）工艺数据**，要求：
1. 扫描两个目录树（AutoCell dram example vs TECHLIB_release）的所有文件，提取参数；
2. 比对两边参数的相似度/重叠（layer 名、GDS 编号、via 定义、model 名、DRC 规则、制造网格等）；
3. 输出一份结构化安全审计报告（.rep），给出"是否写死工艺数据"的结论。

TECHLIB_release 实际解析到 `/apps/imctf/cad/techlib/cxmt10G5_CIP/decqa/G5_CIP_techlib_decqa_v0d5_Rev08/TECHLIB_release`（CXMT 10nm G5 CIP 工艺库）。

## agent 工具链

list_allowed_files（双目录树 depth=3）→ read_files（dram/globals.tcl + dram 各 TCL + TECHLIB/techfile.tf 3353 行分段读）→ search_codebase（techLayers/GDS_NUMBER/layerNumber/dataType/layerDefinitions）→ read_files（CDF source、models、standardViaDefs、layerFunctions）→ run_commands(mkdir) → editor 分段写 `AutoCell_DRAM_Example_Security_Check.rep`（多轮 editor 追加+修正）→ read_files 回读校验。

## 可离线判分内核（草案）

纯 Python（无 EDA 沙盒依赖）：`techlib_sec_audit.py`
- 输入：两个目录树根路径（A=autocell examples, B=TECHLIB）+ 一份参数类别清单
- 解析：TCL 文件（set 变量、layer 定义）、techfile.tf（techLayers/GDS stream number/dataType/layerFunctions/standardViaDefs/DRC rules）、.cdl（model 名/subckt）、models 目录
- 比对：按类别计算 A∩B 参数重叠（layer 名集合交集、GDS number 多重集交集、via 名交集、model 名交集、DRC rule key 交集），每类给 overlap_count / A_only / B_only
- 输出：结构化 JSON + 文本 .rep，含 per-category overlap 表 + 总体结论（是否疑似写死工艺数据：overlap_ratio 阈值）

## hidden B 设计（草案）

- A 档：自包含，构造一个"autocell example 树"（globals.tcl + viadefs.tcl + layer 配置 + 一份 CDL）+ 一个"TECHLIB 树"（techfile.tf + models + tcl），两者有**部分重叠**（如 3 个 layer 名相同、2 个 GDS number 相同、1 个 via 名相同、0 个 model 重叠）→ oracle overlap 表
- B1：不同参数集，重叠模式不同（如 5 个 layer 重叠、0 via 重叠、2 model 重叠）→ 强制脚本真解析非硬编码
- B2：TECHLIB 用不同 techfile 结构（layerFunctions 顺序变、DRC rule key 命名变）→ 测鲁棒性

## k_check 草案（≥8）

①zip 含 .py + 可编译 ②B1 exit0 + 合法 JSON + 顶层键 ③B1 per-category overlap 表齐全 ④B1 layer 名交集集合匹配 oracle ⑤B1 GDS number 多重集交集匹配 oracle（反 A）⑥B1 via 名交集匹配 oracle ⑦B1 model 名交集匹配 oracle ⑧B1 总体 overlap_ratio 落在 oracle 区间 ⑨确定性 3 次 md5 一致 ⑩anti-hardcode-A B1 参数集与 A 不相交 ⑪B2 exit0 + oracle 匹配 + B2≠A ⑫B1 per-category A_only/B_only 集合匹配

## 与已有 case 不相交

- NetlistChk/NlchkNetlistAudit（netlist 命令审计，非双树参数重叠安全审计）
- PatternParamAudit（pattern 参数审计，单树非双树比对）
- 本 case 内核 = 双目录树参数提取 + 跨树 overlap 计算 + 安全结论，前述均为单文件/单树解析

## 状态

- **⚠️ 已在台账（不可造题）**：claim 时 REFUSED — 9pcjd 已在台账 status=case, case_id=EDA-Eval-DesignFlow-AutoCellParamSecurityAudit-001 (2026-11-15 23:42)。但 `cases/D/` 下**无该 JSON 文件**（phantom case_id，ledger 数据质量问题，待清理）。
- 本笔记保留作 r1216 freshness-methodology bug 排查的副产物（详见 MEMORY_D r1216 流水）。**不要据此 9pcjd 造题**（会重复）。
- r1216 真正发现：freshness 判据必须用 **全 4 shard 台账并集 + 剥 .messages.json 后缀**（单 shard D 台账 + 带 suffix 的 sid 会漏判，导致误 peek 已 claim 的 trace）。
