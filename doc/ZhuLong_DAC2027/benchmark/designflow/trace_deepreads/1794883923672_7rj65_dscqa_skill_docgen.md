# Deepread: 7rj65 — DSCQA skill-documentation generator

- **session**: 1794883923672_7rj65
- **user / host**: tongfanl @ hfhds201 (10.129.32.75 = .75 local)
- **mc**: 40 (b_pool_1118_230537, kw: netlist:371;verilog:203;analog:28;hspice:20;pdk:11;aether:5;waveview:4;rtl:2)
- **agent / model**: cline lead / deepseek-v4-flash
- **size**: 493397 B, 73 msgs (37 user / 36 assistant), mtime 2026-11-17 11:22
- **domain**: spice_sim (DDR6 DSCQA finesim 仿真工作流)
- **fresh**: cross-shard 4-ledger 去重后 .75-local fresh 5 之一 (r854 verified readable), 7rj65 是 mc≥10 的唯一剩余 (9rdno/cfnzq 均 mc4 < 10)

## 真实任务（用户原话链）

1. msg0 「你只到抽激励在哪里抽吗？」—— 模糊问抽激励环境位置
2. msg3 「为啥我把 AGENTS.md 放在路径下了，但你还是没有找到抽激励的环境在哪」—— 抱怨 AGENTS.md 未自动加载
3. msg11 「如何让你每次重启对话的时候，都是知道该背景知识？」—— 要启动即注入
4. msg23-31 agent 诊断：zhulong/Cline 不自动注入 ~/.cline/AGENTS.md（证据：~/.claude 不存在、.pi 不存在、globalState.json 是 Cline 状态文件）
5. msg32 「可以，但帮我修改下，有时候激励的结果也不需要传到上海，在合肥服务器也有对应的路径和脚本可以提交matrixrun脚本」—— 加合肥本地分支
6. msg42 路径：`/proj/dscqa/V0/simdir/finesim/dscqaF/Runfile/SpfBA/` + `run_fullchip_SpfBA` + `monitor_and_run_SpfBA_fullchip.sh`；物理盘 `/rundata/...`
7. msg50-58 agent 建 `dscqa-workflow/SKILL.md`（4 步工作流 + 上海/合肥双分支 + pushy description 列触发词）+ 改 AGENTS.md
8. msg59 「我希望你后面把 bmatrix、抽激励环境、matrixrun 脚本都分别学一下，并且生成文档，帮助你后期在帮助我工作时可以更加准确」—— **核心交付诉求**
9. msg60-72 agent 给指令模板，用户逐条发；agent 写 `references/bmatrix.md`（脚本路径/参数表/状态含义/红线/TODO）+ `references/stimulus_env.md`（环境目录/module load/命令/成功标志/产物/红线/TODO）

## 交付物（trace 中 agent 落盘的文件，.75 端 verbatim 读出）

- `~/.cline/skills/dscqa-workflow/SKILL.md`：frontmatter name=dscqa-workflow + description（pushy，列 抽激励/gen_stimulus_ltf/vecgen/WTM_fsm/shds2/matrixrun/run_fullchip_SpfBA/MatrixRun/bmatrix/bmatrix_tf/DSCQA 等触发词）+ 4 步速览 + 第1步(抽激励:vecgen二选一/gen_stimulus_ltf -l WTM_fsm_<MMDD>/module load ds/xcelium/2023.09/PASS:xx,Error:0) + 第2步(跑finesim matrixrun 二选一线路: 线路A上海 shds2 + MatrixRun输出目录; 线路B合肥本地 /proj/dscqa/.../SpfBA/ + run_fullchip_SpfBA + monitor_and_run_SpfBA_fullchip.sh + 出口 /proj/dscqa/.../dscqaF2/MatrixRun) + 第3步(查状态 bmatrix/bmatrix_tf 流程终点) + 通用红线
- `references/bmatrix.md`：/home/tongfanl/bmatrix_tf (perl chkMatrixRunResult.pl) + 参数表 -A/-P/-F/-E/-R/-D/-C/-grep/-u/-save/-rerun + 状态 Running/Pending/Exited/Fail/Comparing/Unknown + 汇总行 + 红线 + 3 TODO
- `references/stimulus_env.md`：环境目录二选一 + module load ds/xcelium/2023.09 + ./runsti/gen_stimulus_ltf -l log/stimulus_tongfanl/WTM_fsm_<MMDD> + 前置 ll patterns/analogsim/WTM/* + 成功 PASS:xxx,Error:0 + 产物 + 红线 + 2 TODO
- `AGENTS.md` 改：补全省略路径 + 加一行指向 dscqa-workflow skill

## case 合成（produce-可复用脚本模式）

- **testable core** = `gen_skill_docs.py`（参数化文档生成器）：读 workflow spec JSON → 生成 SKILL.md + references/<tool_id>.md
- **A 档** = `dscqa_workflow_spec.json`（trace-verbatim：所有路径/命令/参数/状态/红线/TODO 来自 trace agent 落盘的文件）
- **hidden B** = `aging_rel_workflow_spec_B.json`（结构同构、名字全换：dscqa→aging-rel, gen_stimulus_ltf→gen_aging_stim, vecgen→vecgen_rel, bmatrix_tf→rmatrix_tf, SpfBA→RelBA, shds2→bjds3, tongfanl→junhanl, WTM_fsm→REL_fsm, 3 步, xcelium 2024.06）
- **check** 真跑生成器在 B 上，15 断言 (a-o)：zip/脚本/py_compile/运行/SKILL name/触发词/3步结构/合肥提交目录/提交脚本/rmatrix.md路径+参数/aging_stim_env.md命令/反硬编码A(10个A-only token)/反stub(≥4 B名字)/确定性3重跑
- **asset_fidelity**：A spec 字段逐字自 trace agent 落盘文件；ref 生成器完全参数化（零 DSCQA 硬编码）；hidden B = 结构性差异非仅文件名（10 维度 rename + 步数 + 参数 -C→-G）
- **§4.9**：5 neg(empty/print_expected/hardcoded_a/core_deleted/nosim_stub) 全 FAIL NEG_RC=5/5；ref 15/15 PASS
- layer=L1（离线 Python 文档生成/解析，无 EDA 二进制 subprocess），track=faithful，domain=spice_sim，tier=B
- k_check=k_rationale=15 (a-o)
