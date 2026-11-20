# r664 deepread — jiaqis ge424 — Calibre DRC svrf.drc structure analysis

**session**: 1793790199273_ge424 · **user**: jiaqis · **host**: hfeg0plg76 (10.129.8.124, 也可经 172.16.8.175/hfeg0plg09 访问) · **match_count**: 42 · **domain**: physical_verify
**trace**: 59 msgs / 2.66MB / 30 user turns (多数为 tool_result)

## 用户真实意图

jiaqis（物理验证工程师）维护 Calibre DRC 天线规则检查流程。本 session 两个用户意图：

1. **MSG#0**「你直接读取一下这个log文件，分析一下」→ 分析 calibre DRC run log（pv_calibre.ant.log.gz / log）
2. **MSG#39**「分析一下这个文件」+ 附件 **svrf.drc**（2.35MB / 35400 行）→ 分析 DRC rule deck 结构

用户两次表达「为什么每次都需要写一个脚本来查找东西」（MSG#11/13）——对 assistant 反复写 _zl_*.py 脚本不满，但本质是要求**结构化分析**而非逐文件 grep。

## assistant 工具链

- `list_allowed_files` → `/home/jiaqis/work/zl/ant/` 目录 489 个 .rep + Antenna_RES.db(4.8GB) + pv_calibre.ant.log.gz + svrf.drc(2.35MB) + log(6.7MB)
- `editor` 写 7 个 _zl_*.py 脚本：_zl_find_logs.py / _zl_analyze_log.py / _zl_analyze2.py / _zl_rep_stats.py / _zl_svrf_parse.py / _zl_svrf2.py / _zl_svrf3.py
- `run_approved_command` (python-runner) 跑这些脚本
- 每次结束 _zl_cleanup*.py 删除临时脚本（用户要求干净）

## 关键产物（assistant 实际分析的数字）

**svrf.drc 结构统计**（MSG#45/49/53）：
- 35400 行
- 1626 个 rule check block（`NAME {` 模式）
- 119 个 rule family（去金属层后缀分组）
- top families: A_R_8_7 x231, A_R_8_3 x231, A_R_8_4 x158, A_R_8_3_1 x126, A_R_8_6 x116 ...
- base families: A_R x1566, TDV_R x3, BV0_R x3, V1_R_13 x1 ...

**#DEFINE 开关**：MIM_2P=NO, MIM_3P=YES, TPA_THICKNESS=2.8, //#DEFINE WITH_4MZ (注释), #DEFINE DRCQA

**.rep 结果统计**（MSG#33）：489 rep files, 488 parsed, sum of line-1 counts=9760000, top rule A.R.16.1:M21_M3 (20000 count, 1MB)

**calibre log**（MSG#21/25）：104272 行, Calibre v2022.3_33.19, cmd `calibre -drc -hier -turbo 64 -hyper svrf.drc`

## 资产可达性

- svrf.drc：在 trace uploads/ 目录逐字保存 ✓（已 scp 到 workdir，35400 行 / 2.35MB 验证）
- .rep files / log：在 /home/jiaqis/work/zl/ant/（jiaqis 私有，e0031982 ssh 可读但沙盒判分不需 live 文件）
- assistant 分析输出数字在 trace tool_result 内逐字保存 ✓

## 拟造设计（B档 mock-behavioral reframe）

**新子型** `calibre-drc-deck-structure-stats`（distinct vs jiaqis 已交付 DrcEnclosureTripleExtract-001=enclosure rule 提取 / DrcVsDrmRuleAudit-001=DRC vs DRM 审计）。

真实 svrf.drc 2.35MB + 依赖 Calibre 环境 → reframe 为通用纯 stdlib `calibre_drc_deck_analyzer.py`，解析任意 SVRF deck → 结构化 JSON 统计（total_lines / total_rule_blocks / defines / commented_defines / rule_families / top_families / metal_layers / max_metal_layer / drc_results_db / layout_system / precision）。

- **asset A** = svrf_A.drc（真实 deck 代表性切片 344 行 / 45 blocks / 33 families，含 #DEFINE + 多家族 + /* */ 块注释陷阱 + #IFDEF 条件块）
- **hidden B** = svrf_B.drc（合成 deck 209 行 / 26 blocks / 12 families / metals M0-M4 / 2 fake blocks 在 /* */ 内须排除）
- **check()** 16 条件 a-p：zip/compile/B-run/keys/blocks=26/families=12/defines/commented/metals/top4/setup/anti-hardcode-A/determinism/total_lines/AST-anti-hardcode/B2-degraded
- **家族分组规则**：strip 末尾 `(_M<数字>)+` 后缀

**判分牙**：subprocess 真跑 B + cross-input anti-hardcode（B 值全异于 A sentinel）+ 块注释陷阱（naive grep 过计 FAIL）+ 确定性 3x + AST 反硬编 + B2 退化。

**与 jiaqis 已有 case 的 distinct**：DrcEnclosureTripleExtract=triple-criteria enclosure rule 提取；DrcVsDrmRuleAudit=DRC deck vs DRM 文档审计；本案=deck 整体结构统计（block/family/metal/define 计数），无重叠。
