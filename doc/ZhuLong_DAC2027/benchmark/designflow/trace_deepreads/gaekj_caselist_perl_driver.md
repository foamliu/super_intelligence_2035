# Deepread: gaekj — caselist → perl regression driver (run_ddgoa template)

- **session**: 1794385786325_gaekj.messages.json
- **user**: e0039102 @ hfeg0pbn16 (10.129.32.204), mc154, verilog:986 dominant (A-domain digital)
- **scan**: ssh_eda_search_20261113_131349 (11/13 池)
- **msgs**: 351 (193 user / 158 assistant), 16 real user turns
- **lineage**: same user as mm45d (r450 RegrCaseDedup-001) — e0039102 verilog_lib_trans / ddgoa regression lineage, but deliverable zero-overlap (different task archetype: run-script templating vs case-list dedup)

## Conversation arc

- **U#0**: resume interrupted session pxf8v — "总结一下对话，建立对话框架" (agent builds session_framework_run_regr.md)
- U#1-3: continue / verify-all-passed / where-is-caselist-template
- **U#4**: "按标准模板生成的 run_项目名文件在哪？路径下没找到" (agent had previously generated a bash-style driver, now deleted)
- **U#5 (CORE produce-task)**: "1. 按标准模板生成的 run_项目名文件 应放在 /rundata/.../run_lpddr5_ddgoa_WOWTOP/run_lpddr5_ddgoa_WOWTOP；2. 标准模板参考 /rundata/.../jason17w/regression/.../run_ddgoa，按模板重写 run_lpddr5_ddgoa_WOWTOP，路径放新地方"
- U#6: "标准驱动文件需要放在这个目录" (path refinement)
- **U#7-9 (skill authoring)**: "把整个对的流程顺下来写成 vps 配置 skill，方便另一个 Agent 另一个项目也能自动配置" + "不能写太死，换项目要灵活" + "模板也需要提炼总结，不能只给具体模板路径，skill 里不能有写死的路径"
- U#10-15: continue / editor-workaround / "你的 skill 是哪些，我搬到另一个 Agent 上试下"

## Agent tool chain (U#5, idx 109-161)

1. `list_allowed_files` + `read_files` → read standard template **run_ddgoa** (perl driver: `system("./bin/vsim_uvs -sr <case> [-b \"<byte>\"] -d \"<defines>\" --noprobe -q <queue> --ncconfig \"<nc>\" -l \"<date>\" &"); system("sleep 5");`, sections by byte value)
2. `read_files` → read existing `run_regr/run_lpddr5_ddgoa_WOWTOP` (shell version, lines 80-130) — found it deleted
3. `editor` → write **gen_run_perl.py** (parse caselist `-sr/-b/-d` → group by byte (empty→x16, first-appearance section order) → emit perl driver in run_ddgoa format, SR_W=22 column align, header comment block, `system("sleep 5")` initial, section markers `###---for <sec>---#` / `########--- <sec> ---###`)
4. `run_approved_command` (python-runner) → run gen_run_perl.py → 330 cases / 6 sections (x16/x8/x8 hibyte/x8 mrconfig/x8 hibyte mrconfig/x16 hibyte mrconfig, 55 each), written 82060 B / 347 lines
5. `editor` → write **verify_run_perl.py** (count system() lines, section headers; parse perl cases vs caselist cases — case order + byte+defines identical; `perl -c` syntax check; sample x8 section)
6. `run_approved_command` → verify PASS
7. `editor` → write **move_run_perl.py** (move file to final user-specified path, remove empty subdir) + update session_framework_run_regr.md

## Key format (run_ddgoa template, from gen script)

```
#!/usr/bin/perl
# run_lpddr5_ddgoa_WOWTOP -- standard regression driver (run_ddgoa template)
# project / case source / tool / log dir / usage  (header comment block)
system("sleep 5");
###-----------------for x16-------------#
system("./bin/vsim_uvs -sr <case-padded-22> -d \"<defines>\" --noprobe -q vbatch_lp --ncconfig \"+nc...\" -l \"11-10\" &"); system("sleep 5");
########---------- x8 ---------------------------###
system("./bin/vsim_uvs -sr <case-padded-22> -b \"<byte>\" -d \"<defines>\" --noprobe -q vbatch_lp --ncconfig \"+nc...\" -l \"11-10\" &"); system("sleep 5");
```

## A-faithfulness & feasibility

- **A-faithful**: ✅ 用户给路径+模板+目标，未给解析算法/分组规则/列宽/section 标记格式 (合格)
- **deliverable**: 修改私有 `/rundata/ddgoa/.../run_lpddr5_ddgoa_WOWTOP` + `/home/e0039102/*.py` → **INFEASIBLE** on .75 (Permission denied / private path)
- → **B档合成**: 自包含 caselist + template，deliverable = 通用生成器脚本 `gen_perl_driver.py`，check() 在隐藏 caselist_B 上运行验证

## Synthesized case plan

- **ID**: EDA-Eval-DesignFlow-CaselistPerlDriverGen-001
- **domain**: digital, **level**: L1-B, **archetype**: caselist-to-perl-regression-driver-generator
- **A (visible)**: template_run_ddgoa + caselist_A (12 cases / 4 sections) + run_lpddr5_ddgoa_WOWTOP_A (expected A output)
- **B (hidden)**: caselist_B (15 cases / 5 sections, different cases/byte values/defines)
- **deliverable**: gen_perl_driver.py (--caselist --out, config defaults from template)
- **check**: 16 conditions — zip/script/stdlib/run + shebang + header + initial sleep + section markers + case count + -sr order + -b iff + -d match + section grouping + flags + sr-align + cross-input guard + 3-seed grouping invariance
- **negatives**: naive_empty / print_only / hardcoded_A / core_removed / wrong_byte_rule
