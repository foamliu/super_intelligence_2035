# 深读笔记 — sid 1793180092850_scaqk (xinqiaoz @ hfeg0pkn002, mc=495)

- **session**: `1793180092850_scaqk.messages.json` (1.37MB, 329 msgs, agent=lead, zhulong/zhulong-style cline)
- **live 文件已删**，从 `.snapshot/hourly-new.2026-11-06_1300/.cline/data/sessions/1793180092850_scaqk/` 取回。
- **keywords**: pdk:1363; drc:370; calibre:243; .gds:17; skipper:3; lvs:3 → physical_verify (calibre dummy deck QA)。
- **tools**: 237 calibre (editor×118, run_approved_command×35, read_files×16)。
- **跨 shard 查重**: 选题前 `grep scaqk trace_ledger_*.tsv` → 仅 shard D 一条 parked（note: "Dummy QA setup (shard C calibre)"，D 自己识别为 C 域而退避）；shard A/B/C ledger 无。无 case 碰撞（D 未出 case）。shard C claim + mark case。

## 真实任务（Dummy QA — G7 T1 calibreDummy.rule）
Windows AI 写 Prompt，Linux 侧 AI（本会话）执行 21 项 Dummy QA 检查项，逐项推进、保留可复用脚本、向 Windows AI 报告。
- **U#0** 建工作环境（DUMMY/qa_workspace/T1/{chip,parsed,scripts,results}，软链 deck，gitignore qa_workspace）。
- **U#34** 验证 parsed/ 3 JSON 就位 + gitignore。
- **U#63** 检查项 1+2+7+8（头部开关 + 版本号）：GDS_TYPE==chip、suffix 记录参考、script_DEBUG=="False"、OUTGDS_HIER=="False"。**真实产物 qa_01_header_checks.py**：tclsh 探针（stub `source`/`exit`/`unknown` → source 整个 deck → `puts PROBE <var>=<val>`）取 GDS_TYPE/suffix/script_DEBUG/OUTGDS_HIER **终值**；regex 收集 line evidence；judge PASS/FAIL/NOT_SET；--guideline 比对 meta.rule_suffix/version。
- **U#88** 检查项 3+10（fill TYPE 推断 + CMP BLK_OR 矩阵）。
- **U#149** 用户给思路：用 tclsh 探针读 Tcl 部分（成本低、不出错），参考 qa_01_header_checks.py。→ 属「给方案」轮，不可作 A 档任务说明（可作 hint）。
- **U#229** 检查项 5（chip 侧数值逐字段对照，最核心）：rule `set <mask>_cmp [list ...]` vs guideline `masks.<mask>.locations.chip.params`，按 TYPE KEY 字段顺序，config 可严不可松（=/>=/范围/space-min/width-fixed）。
- **U#323** editor 工具损坏 → 转 JOURNAL 交接（会话终止）。

## 抽取的子任务（本 case）
抽「头部开关 QA」子任务（检查项 1/2/7/8），重构为**便携式 TVF 配置终值解析器** `dummy_header_qa.py`：纯 Python 状态机求 `set`/`if {$GDS_TYPE=="X"} {...}`/尾部 override 后的 final 值（不依赖 tclsh），再判 item1/2/7/8，输出确定性 JSON 报告。A=PASS fixture(chip 分支)，隐藏 B=FAIL fixture(GDS_TYPE=frame→frame 分支+尾部 script_DEBUG=True override)，强制通用非硬编码。

## 判分
13 条断言 (a–m)，k_check=13≥8；ref PASS 13/13；4 negative（fake_empty/fake_print_expected/fake_core_deleted/naive_hardcode_b）全 FAIL；§4.9 三假全 FAIL；test==disk roundtrip ✓；check.py 自包含（A/B 内嵌字符串字面量，无路径依赖）。

## 资产
- assets/.../A/{calibreDummy_A.rule, guideline_parsed_A.json} + prompt.md + task_brief.md
- reference/.../check.py + solution/dummy_header_qa.py + hidden/{calibreDummy_B.rule, guideline_parsed_B.json, hidden_manifest.json} + negative/{4 fake + negative_selftest.py}
