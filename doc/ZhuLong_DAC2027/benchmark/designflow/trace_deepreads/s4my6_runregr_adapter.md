# 深读笔记 · s4my6 · run_regr caselist 适配 (e0039102)

- **session**: 1793608238791_s4my6 · user e0039102 · host hfeg0plg74 · mc114
  (keywords: verilog:2081;netlist:90;synopsys:22;skipper:6;cadence:6;aether:6;analog:5;hspice:4)
- **187 msgs / 1.0 MB**，scp 到 .75 workdir 解析。
- **用户意图 (A-faithful 判定)**:
  - U#0 = skill_instructions `run-regr-skill`（run_regr 框架搭建与适配，含 case Dict schema）。
  - U#1 = 「你有参考什么目录下的文件吗？」
  - U#2 = **真实任务**：「适配 /proj/drgsa/V0/simdir/verilog/jason17w/regression/verilog.ddr5.drgsa.clean 到 VPS run_regr；run_drgsa 文件里 8 条 `./bin/vsim_uvs ...` 命令；参考文件夹 /rundata/ddgoa/.../verilog.lpddr5.ddgoa.0812/run_regr/；根据两项目区别 + skill 写 drgsa 的 run_regr 配置」。**未给根因** → A-faithful 合格。
  - U#3 = 「继续」。
- **agent 工具链** (98 tool_uses): skills×1, list_allowed_files×12, read_files×18, search_codebase×2, editor×43, run_approved_command×20, ask_question×1, get_agent_policy_status×1。
- **agent 产出**:
  - `/home/e0039102/run_regr_drgsa/custom_utils.py` (read_caselist：解析 vsim_uvs 行 → VPC case dict；`_opt` regex 提 -b/-f/-o/-sr；`_case_name` = sr_反序plusargs.bus_freq；`_task_name` 非 alnum→_；`get_job_submit_options` 丢 bsub/-o/-e/-J/-n)
  - `pattern` / `regr.env` / `task_pre_cmd.sh` / `task_post_cmd.sh`
  - `gen_caselist.py` / `validate.py` / `check.sh` / `README.md`
  - 后期又写 `/home/e0039102/run_regr/custom_utils.py`（同逻辑 refined 版）
- **判分可离线性**: 全部为纯 stdlib Python 解析 + 字符串/路径构造，无 EDA 工具依赖，无 NFS 私有路径依赖（环境变量 DRGSA_REPO_ROOT/date 控制路径确定性）→ L1 B 档合成。
- **合成 case**: EDA-Eval-DesignFlow-RunRegrCaselistAdapter-001 (digital L1 k=16 B档)
  - deliverable = custom_utils.py (read_caselist + get_job_submit_options)
  - A = run_drgsa_A.sh (8 命令) + framework_spec.md
  - B = run_hidden_B.sh (6 valid，跨 bus/freq/plusargs/sleep/noprobe，跳过注释/空行/echo/other_tool/缺-sr)
  - 自验 ref PASS 16/16；4 negative + §4.9 三假提交全 FAIL；k=16✓
- **与 r420 (us0hd RegrCaseFilter) 区别**: 同 user e0039102、同 vsim_uvs 域，但 deliverable 不同——r420 = 按 spec group 筛选 case + 去注释 + 逐字节参数；r421 = 把命令行解析成 run_regr case Dict（name/run_cmd/case_name/env/...）+ 反序 plusargs + 路径构造。archetype = spec-driven caselist→Dict 生成器（第 6 类，r420 是 case-filter）。
