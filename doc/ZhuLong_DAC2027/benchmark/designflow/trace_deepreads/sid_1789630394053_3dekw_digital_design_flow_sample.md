# Deepread — 1789630394053_3dekw (zhigangw @ hfeg0pkn002)

- mc=80, 81 msgs (49 user / 32 assistant), 388KB, agent=cline lead
- tools used: list_allowed_files, get_agent_policy_status, search_codebase, RAG_MCP_Server__search_apis (pyAether/skill), read_files, editor, run_approved_command(denied)
- domain: pg_layout (APR/floorplan/digital flow; candidate pg_score=5 via innovus+floorplan)

## Real user intent

USER#1 (ts=1789630394501, 唯一意图轮, 原文):
> `plese get simaple of digital design flow`

(= "please get sample of digital design flow"). 所有其余 user 轮为空 content（cline tool_result 回灌）。

## What the agent actually did

1. 探查 workspace: `/home/zhigangw/Desktop`, `/home/zhigangw/mywork` (src/python, src/pyAether/labs, apr/innovus, src/skill, zwu_working_note)。
2. 读真实脚本:
   - `src/python/mac_fp16_x16_finish.v` (RTL, module mac_fp16_x16)
   - `apr/innovus/flooplan_init.tcl` (68B, setEndCapMode+addEndCap)
   - `apr/innovus/run_finish.tcl` (Innovus Foundation Flow finish)
   - `apr/innovus/inn2vir.tcl` / `inn2vir_G4B.tcl` (GDSII streamOut → Virtuoso, reflibs stdcells_pim)
   - `src/pyAether/labs/aeCmd/makecell.py` (pyAether cell gen)
   - `zwu_working_note/readme.idjoa` (LIBs: IC28HKN_VHS / G4B; APR apr_tmp_flow)
3. 合成并写入 `/home/zhigangw/mywork/zwu_working_note/digital_design_flow_sample.md` (687 行, 13 章节 + 附录):
   - 流程总览 (RTL→GDSII) + 10 阶段 (RTL/DC Synthesis/Floorplan/Placement/CTS/Routing/StarRC/PT/GDSII→Virtuoso/LVS) + Quick Start + Appendix
   - 每阶段引用真实脚本路径 + 代码块 + summary
4. USER 无追问/无修正 → 接受结果（会话以 agent 摘要结束）。

## Gold (real accepted artifact)

`/home/zhigangw/mywork/zwu_working_note/digital_design_flow_sample.md` — agent 实写、用户接受。

## Failure modes (case 教学点)

1. 硬编码 A 专属内容（mac_fp16_x16 / idjoa / IC28HKN / G4B / flooplan_init.tcl）跨 bundle 穿透
2. 漏 Flow Overview 顺序 / stage 编号错
3. 代码围栏缺 lang 标签 / 内容与 scripts[key] 不符
4. 坏 bundle 仍写文件 / 退出码错
5. 非确定性（路径混入 stdout）

## Case 设计 (B-档 synthesized, L1-boundary)

- task_id: EDA-Eval-DesignFlow-DigitalDesignFlowSampleGen-001
- deliverable: 单文件 Python `digital_design_flow_sample_gen.py` (CLI `<bundle.json> [--outdir DIR]` / `--help` / 无参 exit1 / 坏 bundle exit1+stderr)
- bundle schema: {creation_date, project_env, design_name, tool_chain[], flow_stages[{key,title,script_path,lang,summary}], scripts{key:content}}
- 输出 doc: `# Digital Design Flow - Simple Sample` + header(project/design/toolchain→) + `## 1. Flow Overview`(编号列表) + 每 stage `## <n>. <title>`(>Script + ```lang + content + summary) + `## Quick Start` + `## Appendix`
- 资产 A=inputs/prompt.md+task_brief.md+bundle_A.json(真实 4 skill 脚本片段 + flow_17 风格 10 stage)
- hidden B(嵌入 check.py): B1 clean(ddr4_ctrl_top/TSMC28/8 stage)、B2 cross-input(rf_pll_frac/SkyWater130/Yosys+OpenLANE/6 stage, 验不含 A token)、B3 坏 bundle(缺 scripts, exit1+stderr)
- 12 断言 (a-l), k_check=12>=8 GATE PASS
- negatives: 5 fake (empty→a / print→b / core-deleted→f / hardcode-a→e / ignore-lang→h) NEG_RC=0 distinct labels
- §4.9 三假提交: 空壳→a / 只 print→b / 参考解删核心(overview)→f 全 FAIL
- 自验: ref PASS 12/12 (CHECK PASS)
- test 字段 md5==磁盘 check.py (94c78749d0c7545f341b7025e31b4eea, 13662B)
