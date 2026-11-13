# r535 deepread — zp3rn · Argus_DRC PCT/AGT 间距 deck 编写型 produce-task

**session**: 1792203098166_zp3rn · sherlock@10.129.35.107 · mc=169 · kw drc:1870;pdk:300;calibre:169;lvs:76;cellview:73;cadence:60
**domain**: physical_verify · **子型**: author-new DRC deck（与 r524 DrcDeckUpdateQa-001 同谱系，本次是 spacing-not-equal 双分支规则）
**trace 规模**: 125 total msgs / 76 user msgs（多数是 tool_result 回传）

## USER#0（原文）
> 我需要一条DRC规则来检查PCT和AGT两层版图层次是否有距离不等与0.15um的情况，使用的工具为Argus_DRC，请帮我生成一段符合需求的deck

## 关键对话流
- USER#0 提出需求。assistant 先调 `qualib-tcl-generator` skill（不对路）、`list_allowed_files`、`search_codebase`、`fetch_web_content`（被 policy 拒）、`run_commands`（被拒，仅 run_approved_command 且 filePath 须 .sh）、多轮 `RAG_MCP_Server__search_apis`（返回的几乎全是 SKILL/Virtuoso API：mgGetLayerSpacing / drdGetMinSpacing / techGetSpacingRules / pvsApplyDRC，与 Argus SVRF deck 语法关联弱）。
- **USER#27**（关键转折）：用户重申需求并附上参考文件 `calibreDRC.rule`（39208 行 G4C DRAM Calibre-DRC rule file）："请参考附件中的DRC文件，帮我生成一段符合需求的deck"。
- assistant 读 calibreDRC.rule（分批 read_files），识别 SVRF 语法（EXT / SIZE / NOT TOUCH / VARIABLE / LAYER MAP / ABUT<90 / REGION / INTERACT / ANGLE），用 `editor` 分块写 `/home/sherlock/Documents/PCT_AGT_DRC.rule`（中途 insert 操作致结构错乱 → 删掉重建）。
- **idx=105** assistant 总结产物 PCT_AGT_DRC.rule：4 个 check —— PCT_AGT_Check_001（EXT<0.15 + EXT>0.15，报告所有 ≠0.15）/ 002（±GRID 容差）/ 003（SIZE + NOT TOUCH 几何验证）/ PCT_AGT_S_004_00（仅 EXT<0.15）；含 LAYER MAP（PCT=10/AGT=11）、VARIABLE GRID、@ 注释、overlap guard。
- **USER#106**（转向）：用户粘出一条既有规则 `CELL_BL_S_013_00`（AGT/PCT 在 BL 方向 min-space + overlap check，用 ANGLE/INTERACT/EXT/ABUT<90/REGION/TOUCH/SINGULAR）请 assistant 解释——说明用户拿到生成 deck 后转去对照既有类似规则理解，未明确"接受"。

## GOLD / 资产
- 产物文件 PCT_AGT_DRC.rule 已不在磁盘（assistant 虚拟 fs 写入，未持久化到 host）→ 据 idx=105 总结 + idx=106 真实 SVRF 片段重建语法。
- asset A：`reference_svrf.rule`（从 calibreDRC.rule 抽取的真实 SVRF 片段：header + LAYER MAP + VARIABLE + CELL_BL_S_013_00 真规则 + 算子清单）+ `config_A.json`（PCT/AGT/0.15/grid 0.001）+ task_brief + prompt。
- 合成方向：交付 = 参数化 Python deck 生成器 `gen_spacing_drc_deck.py`（读 config json，输出 SVRF deck）；"不等于 X" 必含 `<X` 与 `>X` 两分支。

## 隐藏 B（防硬编码）
- B: M1/M2 maps 20/21 target 0.2 grid 0.005；B2: MT1/MT2 maps 30/31 target 0.3 grid 0.002。
- check.py 对 B 与 B2 各跑一遍脚本，校验 deck 含对应 LAYER MAP / EXT <target / EXT >target（精确值，非 target±grid）/ ABUT<90 / REGION / GRID / 层名 / DRC 块 / ≥2 EXT / 长度>200，且不含 A 字面量 PCT/AGT/0.15。
- 双配置防 print-stub（单配置可硬编 B 答案，双配置不可）。

## 自验
- ref GOLD：B+B2 均 PASS（14/14 条件 a-n）。
- 3 neg（empty / hardcode_A / only_min）ALL-FAIL。
- §4.9 三假（empty / print_expected / core_deleted[删 EXT > 分支]）ALL-FAIL。print_expected 靠 B2 拦（硬编 B 的 M1/M2/0.2 deck 在 B2 上无 MT1/MT2/0.3 且漏 M1/M2/0.2）。
- k_rationale == k_check == 14 ≥ 8 ✓。

## 选料过程（r527 kw-source 归因法）
本轮 peek 29 个 fresh C 域候选（mc 25-250，多用户），hit 1（zp3rn）/ reject 28：
- xinqiaoz@10.129.2.11 pdkQaSystem issue-handler skill 集群（4msuj/xnd0q/v25ss/pksze...）：USER#0 = 同一段 `<skill_instructions name="issue-handler">` 模板，drc/pdk/calibre kw 全来自被处理的 PDK QA 系统（codebase-context inflation 第六型：skill-orchestrated workflow）→ 全 reject。
- env/Q&A/run-existing 簇：slj4a「查下有没有接入我的aether」/ taaak「能启动Aether吗」/ poa8g「Aether」/ 55qgy「桥接连接失败」/ ge5tf「你好」/ 30cgz「linux怎么复制文件」/ wn9jo「有没有PDK文件」/ zdzqa「vdbias 如何影响delay cell时序」→ reject。
- 跨域 produce-task（C 域 kw 但任务非 C）：szlie（.sp 参数化生成 = B/D spice_sim）/ p64wo（DDR testbench 加 enops = A verification）/ enbl7（SV netlist model 名检索表 = D netlist）/ xm22u+le1s7（cline skill-creator = infra）/ l4tre（genReleaseNote 清理 = infra）/ qcrl8（PEX 流，依赖 GloryEX 商业工具 + autosim 框架，离线不可判）→ reject for C。
- qwreb（genPGDummy_for_Logic.py「这个flow理一下」= code-review explain，非 produce）→ reject。
- **zp3rn**：USER#0 动词「生成」+ 宾语「deck」+ Argus_DRC = clean physical_verify author-new produce-task ✓。

## 谱系
physical_verify produce-task 第五子型 **author-new spacing-not-equal**：r524 author-new（写新 deck）、r529 format-convert、r526 pipeline-build、r531 optimize-modify、**r535 author-new-spacing-NE**（双分支 <X+>X）。与前四子型 kw 同构（drc/calibre/.gds dominant），唯 USER#0 动词+宾语可分。anti-hardcode：双隐藏配置 B/B2（variable-name + value generalization，r531 cond(o) 升级版）。
