# Deepread: 1794453706054_ploz9 (steveny @ hfeg0plg189, mc=97)

**domain**: physical_verify (Virtuoso layout rscalc flow — AutoVia/PowerFill/RsCalc/RTEXT)
**user/host**: steveny / 10.129.32.189 (hfeg0plg189)
**session**: 1794453706054_ploz9, 76 msgs, 45 assistant tool calls
**case built**: EDA-Eval-DesignFlow-CadToolCliRefactorAudit-001 (physical_verify, L1, k=13)

## 真实用户意图（U#0 逐字）

> rules/skills/test_layout_rscalc_flow_19/里面，用到了eda agent skill里面提到到一些cad tool，你更新一下文档，把这两个关联起来。另外，我们要开一个项目，做cad tool的cli化改造，我们的flow里改造了几个工具，但是没有做验证，我们接下来要深入进去，看看和现有工具相比，我们做了哪些改造，是否做对了，是否做到位了。

U#2 (msg46): "在项目readme中完善背景信息...本地只有较弱的模型，无法联网...本地环境叫PDC环境...外面有一个开发测试环境..." (PDC vs 开发测试环境资源约束说明, 写进 README)
U#3 (msg56): "提交"

## trace agent 工具链

1. list_allowed_files 探 `test_layout_rscalc_flow_19/` + `eda_agent/` 目录结构
2. read_files 读 4 个 runner SKILL.md + eda_agent SKILL.md + steveny_PRACTICE_HANDBOOK.md + steveny_vs_austin_CMD_REVIEW.md
3. editor 改 4 个 runner SKILL.md（加"与 eda_agent 关联"段）+ 新建 LINK_eda_agent.md + 更新 INDEX.md + eda_agent/SKILL.md（反向引用）+ references/workspace_index.md
4. editor 新建 adhoc_jobs/cad_tool_cli_refactor/{README.md, 01_cli_refactor_audit.md, request_to_devt_env_TEMPLATE.md}
5. git 精确路径暂存 + 两个 commit（避免污染他人暂存）

## 真实交付（gold）

- **Commit 9819844** "关联 rscalc 闭环与 eda_agent 技能文档"（7 文件 +1260）：
  4 runner SKILL.md (autovia/powerfill/rscalc/rtext) + LINK_eda_agent.md + INDEX.md + eda_agent/SKILL.md
- **Commit 03a8b68** "新建 CAD tool CLI 化改造验证项目"（4 文件 +265）：
  adhoc_jobs/cad_tool_cli_refactor/{README, 01_cli_refactor_audit, request_to_devt_env_TEMPLATE}.md + references/workspace_index.md

## 4 个 runner 的真实 gap（审计依据）

| runner | original GUI 行为 | CLI 化 gap | priority |
|---|---|---|---|
| virtuoso-autovia-runner | GUI 驱动菜单，手动 config pick | 沙盒阻塞 load()/loadi()/evalstring()，需 shell() 启动 -nograph -replay 绕过；config 内联去 load() | P1 |
| virtuoso-powerfill-runner | genPowerFill.py 是 tkinter GUI 弹窗 | 同上 load() 阻塞 + 去除 tkinter 弹窗（参数全走 config） | P1 |
| virtuoso-rscalc-runner | IMCutRscalcFlow.il GUI+3D 可视化 | 同上 load() 阻塞 + 去除 3D 可视化（改文本输出 .rvn） | P1 |
| virtuoso-rtext-checkpoint-designer | 手动 GUI 点击放置 RTEXT | 全 inline 在沙盒跑（无 shell 绕过）；替代手动放置 | P2 |

## reframe（mock-behavioral）

真实 CAD 源码/Virtuoso 在 .75 上 path-dependent（需 OA 环境 + 真实 SKILL 沙盒），SUT 跑不了真 Virtuoso。
reframe 为纯 stdlib 结构化分析器：解析 runner SKILL.md（frontmatter name + Context&Problem 段 + 与 eda_agent 关联段）+ eda_agent SKILL.md，产出 LINK_eda_agent.md（每 runner 三类关联：执行沙盒/CAD 源码优先/SKILL API 参考）+ 01_cli_refactor_audit.md（6 列审计表）。
- 交付 = `cli_refactor_audit.py`（--input-dir / --output-dir 接口固定）
- check() 在隐藏 B（4 个不同 runner: drc/lvs/peg/antenna）上跑 SUT 脚本，校验产出对 B 内容的正确性（13 条独立断言）
- B 与 A 结构同、tool 名/gap 不同 → 硬编码 A 的 runner 名必 FAIL

## 选料过程

candidates_mc10.tsv mc≥10 fresh (4-shard ledger 排除, 后缀修正) → 176 true-C (c_strong≥50, C/数字比>0.3) → 排除 xinqiaoz PDK cluster + e0014566 flow-driving cluster → peek 6 候选 (ploz9/mwqz9/h1v18/ayqtu/ypwty/9dj4b)：
- mwqz9 (mwxi mc58 aether:157): project-sync 脚本改造(合肥/上海互传) → 非 EDA, skip
- h1v18 (lizwen mc67 aether:357): "smash快捷键是什么" Q&A → 太琐碎无交付, skip
- ayqtu (simplec mc54 aether:121): "加载我路径下的skill" → setup 无交付, skip
- ypwty (ziyuny mc55 aether:247): 粘贴 skill 写作指南 → 上下文不明, skip
- 9dj4b (shuoran mc50 drc:526): finesim measure 结果处理脚本 → B-domain spice_sim, skip
- **ploz9 (steveny mc97 virtuoso:513 cellview:75 .gds:23)**: VIABLE ✓ doc 关联 + CLI 改造审计, 真实 C-domain 交付

前 5 高 mc 候选 (p64wo/ij4uu/focjw/fyknj/l7aol) peek 后全判 D-domain (DDR5 verif / verilog translator / netlist 语法检查) —— "drc"/"lvs" 关键词来自路径名非物理 DRC。
