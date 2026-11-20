# 深读笔记 · nzxx2 (ziyuny@hfeg0pnd002, mc44, 107msgs, 340KB)

## trace_source
- user: ziyuny
- host: hfeg0pnd002
- session_file: 1789904654090_nzxx2.messages.json
- match_count: 44 (49 schematic 7 pyAether 4 virtuoso 3 netlist 1 synthesis)
- real_task_summary: 在 Aether 上对模拟电路 cell 执行 group generate（AnaWeave / auto-group-generator skill）

## 用户轮（A-faithful 候选）
- USER#0 ★ `<user_input mode="act">在train/ddgoa_test项目中的，GG_Demo/VblhSFRStbyAmpIP2上做group genertate</user_input>` —— 纯目标，无根因/修法（A-faithful 合格）
- USER#31: 同 flow 不同 cell (GG_Demo_simple/VwlpRefAmpIP) —— 纯目标
- USER#55: "使用v1.1 ... GG_Demo/VblhSFRStbyAmpIP2上做group genertate" —— 纯目标
- USER#43-74: 给 skill 改名 (AnaWeave)、迁移脚本 —— 非目标轮（命名/维护任务，不作 A 档任务说明）

## assistant 工具链（USER#0 → msg#30 完成段）
1. skills(auto-group-generator) 加载 skill
2. list_allowed_files / read_files 读 group_generator_cfg.json
3. editor 创建 validate_cfg 脚本 → run_approved_command(python-runner) 校验 cfg JSON 合法（19 top-level keys, 7 必须项齐全: PDK/IsFinfet/TermCdfCfg/PolyContactCfg/GuardRingCfg/CdfCfg/DRCCfg, PDK=TECHLIB, IsFinfet=False）
4. run_approved_command(shell-runner) 因 dynamicFileRoots 限制 → editor 创建 wrapper run_gg_vblhsfrstbyampip2.sh → 启动 run_group_generate.sh
5. 日志显示 flow: aeOpenDesign→True, aeLoadGroupGeneratorConfigFile→True, aeCstAnalysisFromDesign→True, aeCstRealizeAllFromDesign→True, aeSaveDesign→True
6. editor 创建 poll 脚本 → 轮询日志发现 `GROUP GENERATE DONE: GG_Demo/VblhSFRStbyAmpIP2/layout`，无 [FAIL]
7. msg#30 汇总验收报告（全部 acceptance criteria 满足）

## 金标准（msg#30 验收报告，事实层）
- cfg_valid: JSON 合法 + 7 required keys 齐全
- pdk=TECHLIB, is_finfet=False
- flow_steps: aeOpenDesign/aeLoadGroupGeneratorConfigFile/aeCstAnalysisFromDesign/aeCstRealizeAllFromDesign/aeSaveDesign 全 True
- success_marker: `GROUP GENERATE DONE: GG_Demo/VblhSFRStbyAmpIP2/layout`
- fail_markers: 无（无 [FAIL]）
- overall_pass: True

## 合成计划 · EDA-Eval-DesignFlow-GgFlowReport-001 (eda_other, A-faithful, L1-static+subprocess)
- 任务说明 = USER#0 逐字原文
- 交付 = gg_flow_report.py(argv: config_path, log_path, output_dir → 写 gg_flow_report.json)
  - 校验 cfg(JSON parse + 7 required keys + PDK/IsFinfet 取值)
  - 解析 log(5 个 flow step markers + success marker + cell path + [FAIL] markers)
  - overall_pass = cfg_valid AND 5 steps True AND success_marker AND no FAIL
- A 资产: config_a.json(真实 cfg, PDK=TECHLIB) + log_a.log(忠实重建 GG_Demo/VblhSFRStbyAmpIP2 成功 run) + prompt + task_brief
- 隐藏 B: config_b.json(PDK=FINFET_22, IsFinfet=true, 结构对立) + log_b.log(真实 zyTest/VwlpRefAmpIP 成功 run, 不同 cell) 反硬编码; 另附 log_fail.log(真实 [FAIL] run) 供失败守卫
- check.py 16 conds a-p: zip/py_compile/A-cfg_valid/A-required-keys/A-pdk/A-is_finfet/A-flow5/A-success-marker/A-cell-path/A-no-fail/A-overall_pass/B-pdk-different/B-cell-different/B-is_finfet-different/fail-log-overall_pass-False+fail-markers
- 真跑候选: subprocess 跑 candidate on (A cfg+log) 与 (B cfg+log) 与 (fail cfg+log)，解析输出 JSON 比对
