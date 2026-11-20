# trace_deepread: 1794464932663_5li8u — LSF EXIT 故障诊断（ghyang @ hfeg0plg93）

- session: `1794464932663_5li8u.messages.json`（468KB，99 msgs）
- user: ghyang @ hfeg0plg93（10.129.8.225），mc=59，domain=schematic_netlist（netlist:64 / synopsys:167 / schematic:6）
- 选取用户轮：**U#20**（A-faithful 候选，提出需求、未给根因/修复）=「刚刚执行的这些脚本文件看起来都没在运行，看看对应的log文件，判断是出了什么问题」

## 用户意图（两个真实任务轮）

**U#1**（提出需求）：「在这个路径下/proj/ddgoa/V0/workdir/ghyang/DDGOA/有Yiotwist_case5spf*8个文件夹，每个文件夹中都有run-all这个可执行脚本，首先检查这个脚本文件的内容是不是一致，随后分别在各自的路径下执行这8个脚本，因为执行文件中有相对路径，我想如果不在文件路径下执行好像会有问题」
→ 检查 8 个 run-all 一致 + 各目录下执行（相对路径）

**U#20**（提出需求，本轮造题选用）：诊断为什么脚本没在运行。
→ 查 log 判断问题

## assistant 工具链与关键产物

1. `list_allowed_files` 列 8 个 `Yiotwist_case5spf*` 文件夹 → 各含 run-all
2. `read_files` 读 8 个 run-all → 对比：7 个一致，`Yiotwist_case5spf` 的 `mkdir` + `sim_p1_pl3.sp` 被注释
3. `run_approved_command`(shell-runner) 跑包装脚本 `run_all_case5spf.sh`（cd 各目录后 ./run-all）→ 提交 23 个 bsub job 到 fqueueAry
4. **U#20 后**：`list_allowed_files` 列各 `res_all/` → 发现 `Yiotwist_case5spfmerge1` 缺 `.fsdb/.mt0.csv`
5. `read_files` 读 `.elog/.log` → 时间戳是 11/5-10（旧任务），新 job 11/12 14:29 提交
6. `run_approved_command` `bjobs -a` → **23 个新 job（2529246-2529298）全 EXIT**，exit code 1，0 CPU
7. `bjobs -l` → 每个 job `finesim sim_pXaY_pl3.sp -o ./res_all/ -np 6`，Exited exit code 1，CPU 0.0s
8. `debug_finesim.sh`：`finesim --version` 报 `GLIBCXX_3.4.26 not found (required by .../eda_agent/.../libstdc++.so.6)` ×4
9. `check_env.sh`：`LD_PRELOAD=/apps/imctf/cad/ai/agent/eda_agent/eda-agent-20261022-164820/lib/libstdc++.so.6:/apps/.../libgcc_s.so.1`
10. 读 `lsf_test_2530414.err`：`/apps/lsf/.../etc/res: /lib64/libc.so.6: version GLIBC_2.18 not found (required by .../eda_agent/.../libstdc++.so.6)`
11. **根因**：eda_agent shell-runner 注入旧 `libstdc++.so.6` 经 `LD_PRELOAD` → bsub 传播到执行主机 → 执行主机 glibc 太旧（缺 GLIBCXX_3.4.26 / GLIBC_2.18）→ finesim 与 LSF res 二进制均崩溃 → 23 job 全 EXIT
12. **修复**：`LD_PRELOAD="" bsub ...` 清空变量 → 测试 job 2531404 成功提交 fqueueAry（`env -u LD_PRELOAD bsub` 因 PATH 问题失败，改用 `LD_PRELOAD=""`）

## GOLD（用户实际接受的结果）

- 根因：eda_agent LD_PRELOAD 旧 libstdc++.so.6 经 bsub 传播 + 执行主机 glibc 不兼容
- 证据：bjobs -l（23 EXIT/exit 1/CPU 0）、finesim --version（GLIBCXX_3.4.26）、check_env（LD_PRELOAD eda_agent 路径）、lsf_test .err（GLIBC_2.18）
- 修复：bsub 前清空 LD_PRELOAD（`LD_PRELOAD="" bsub ...`）

## 造题处置

- 真实资产（/proj/ddgoa/、/home/ghyang/）属 ghyang 私有、且 LSF/finesim 环境不可复用 → **B-grade synthesized-reframe**
- asset A = 真实日志（bjobs_l / finesim_version_err / check_env / lsf_test_2530414 .out/.err / test_clean_bsub / run_all_case5spf.sh），保留真实 host / jobid / 路径 / 错误串
- hidden B = 合成平行场景（**license server unreachable**，LD_PRELOAD 干净、无 GLIBCXX），交叉输入守卫反硬编码
- reference = `diagnose_lsf_exit_ref.py` 通用日志模式分析器（LD_PRELOAD+libstdc+++GLIBCXX → libstdcxx_mismatch / FlexLM license → license_unreachable / missing .sp）
- harness-for-teeth Q&A→produce reframe（要求候选交付通用 `diagnose_lsf_exit.py` + A 诊断 + report，判分对隐藏 B 复核）
- check.py 14 断言（a-n），ref PASS 14/14，5 neg 全 FAIL（fake_empty/fake_print_expected/fake_core_deleted/naive_hardcode_a/naive_license_only）
- case_id: EDA-Eval-DesignFlow-LsfExitDiagQA-001，domain=schematic_netlist，grade=B，track=synthesized，level=L1
