# r611 deepread — xinqiaoz / hx63x — ssh_test_pdkqa profile

- **session**: 1791787171667_hx63x.messages.json
- **user/host**: xinqiaoz @ hfeg0pkn002 (10.129.2.11)
- **match_count**: 576 (pdk:2403 / drc:1979 / calibre:900 / .gds:10)
- **msgs**: 351 (178 user / 173 assistant), 8 user_input
- **domain**: physical_verify (C)

## 用户意图（UI#1, msg12 — 核心 produce-task）
> 后面的任务：
> 1. 实现自动化 ssh 执行 test
> 2. 沉淀经验到项目的相关指令文档中，ssh 到本地这个经验在很多地方都可以用得上，原因是 Zhulong是通过LSF bsub到Redhat8 的操作系统机器上运行的，和本地不是一个环境。也因此，以后执行指令遇到环境问题，都可以使用 ssh 的方式尝试

背景（trace 内 agent 推理 + 注释）：LSF 节点跑 RHEL8（Calibre VCO=aok），但 Calibre 2020.1_36 是 aoi VCO；calibre_env 自动切换在非交互 shell 失败 → 已验证 workaround = SSH 到 CentOS 7.8（aoi 可用）的远程主机跑测试。

## agent 交付（msg19-29 核心 + msg31-172 文档）
- **Task 1** — `scripts/profiles/ssh_test_pdkqa.sh`（bash profile）：
  - 读约定文件 `.tmp/SSH_CMD_AGENT.txt`（一行：脚本路径+参数，无 python 前缀；空/缺则默认 `DRC/tests/run_all_tests.py`）
  - 远程 env：`export LD_LIBRARY_PATH=...; export PYTHONPATH=...; source calibre_env`
  - `timeout 300 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 xinqiaoz@hfeg0pfn108 "cd /home/xinqiaoz/PDK_QA/pdkQaSystem && env && python cmd"`
  - `trap 'rm -f "$CMD_FILE"' EXIT`（退出清理约定文件）
  - 写 `profile_usage.log`（ISO timestamp + profile_id）
- **Task 2** — 文档更新（index.md / pitfall_registry P14 / known_issues K10 / testing-sop §4.5 SSH bypass / agent-command-profiles / generate_policy.py / project-conventions）

## 用户接受情况
UI#2「已执行，请验证」→ UI#5「给我提交列表和理由，我审核后一次性提交」→ UI#6「没有问题，请提交」→ UI#7「DRC/test/ 三个修改请提交」。**用户审核后批准提交 = accepted gold**。

## B档 mock-behavioral reframe（承 r602-r610 模式）
源码在 xinqiaoz 私有 workdir（沙盒不可达）→ asset_fidelity=synth。把「ssh-remote-test-runner profile」参数化为纯 Python3 `ssh_test_profile_builder.py <config.json> <out_report.json>`（stdlib only）：
- 解析命令（空→default；去 python 前缀）
- 构造 env_exports（LD_LIBRARY_PATH+PYTHONPATH+source calibre）
- 组装 ssh_command（timeout+ssh opts+user@host+cd+env+python cmd）
- VCO 判定 needs_ssh_workaround = (calibre_vco != local_vco)
- 配置完整性 + trap_cleanup + log_entry_format
- 确定性 JSON（sort_keys，26 顶层键）

输入 A（xinqiaoz/hfeg0pfn108/aoi vs aok/空 cmd_spec→default）；隐藏 B（testeng/hfeg0plg22/aoi==aoi VCO 一致/非空 cmd_spec 无前缀）；隐藏 B2（qateam/hfeg0pkn007/aok vs aoi 不一致/cmd_spec 带 python 前缀）反硬编。

## 16 条 a-p
结构 2(a:zip+py_compile / b:B exit0+26键) + B 命令解析 3(c:resolved==spec / d:used_default False / e:stripped False) + B VCO 1(f:needs_ssh_workaround False) + B env 1(g:LD+PY+source) + B ssh 1(h:timeout600+host+user+cd) + B 配置 1(i:config_complete) + B2 命令 2(j:python 前缀去掉 / k:stripped True) + B2 VCO 1(l:needs_ssh_workaround True) + 反硬编 2(m:B≠A / n:B2≠B) + 确定性 1(o:两跑字节一致) + 固定字段 1(p:trap rm-f + log 含 profile_id)。

自验 ref 16/16 PASS✓；3 neg(empty/print_only/deleted_core)全 FAIL✓ NEGATIVE_SELFTEST ALL-FAIL-OK✓；k=16≥8✓。

## 新子型
**ssh-profile-builder / remote-test-runner-profile** — C 域首次 yield「环境绕开 automation-tool」形态（setup/run-existing 现合法，2026-11-15 令）。区别于 r602 doc-grounded extraction / r603 deck-diagnostic / r604 sync-batch-planner / r605 geometry-compute / r606 config-parser-extend / r607 hierarchical-net-resolve / r608 constraint-pattern-gen / r609 requirements-doc-gen / r610 corner-space-pattern-gen。
