# trace_deepread: xkg53 (FinesimAutoRun, analog_context)

- **session**: 1789019984423_xkg53.messages.json (sophiaw @ hfeg0plg09, mc26, 56 msgs)
- **domain**: analog_context (FineSim 仿真自动化)
- **档位**: A-faithful (trace-faithful)

## 用户原话（U#6，提需求轮，未指出根因 ✓）
> Python 脚本,自动运行finesim 仿真,/home/

U#0-U#5 为寒暄/选项导航（boilerplate，非提需求）。U#6 是唯一提需求轮：要一个 Python 脚本自动跑 finesim 仿真。

## agent 工具链
list_allowed_files(/rundata/ieda_agent_test/weihan) → read_files(runsim.sh / sim_execution.py / tck_clk_10corner.sp / tck_clk_10corner_alter) → 推断 finesim 命令格式 `finesim -spice -i <sp> -o <out> -np <cores>` + LSF `bsub -q <queue> -J <name> finesim ...` + `module load ds/finesim/<ver>` → editor 分段写 run_finesim.py（FineSimRunner 类：find_spice_files / count_alters / build_local/lsf / run_local / run_lsf / monitor_lsf_jobs / _check_results / print_summary / main CLI）→ py_compile 验证（沙箱不可用，转读文件校验完整性）→ U#55 给出 689 行总结。

## 关键物理
- FineSim 本地命令：`finesim -spice -i <sp> -o <out>/<base> -np <cores>`
- LSF 提交：`bsub -q <queue> -J <base> finesim -spice -i <sp> -o <out>/<base> -np <cores>`
- 模块管理：`module unload ds/finesim` + `module load ds/finesim/<version>`
- .sp 文件自动发现（glob *.sp）；`.alter` 块计数（PVT corner 扫描，每块一个 corner，首个 corner 为 base 不带 .alter）
- 输出目录 `<out>/<base>` 按净表名分目录
- 结构化摘要 JSON（dry-run 模式不执行仿真器，用于 CI/校验）

## 金标（A-faithful）
trace 末尾 agent 产出 run_finesim.py（689 行 FineSimRunner），用户未拒绝 → 接受。降级为通用 CLI 金标 `run_finesim_ref.py`：find_spice_files / count_alters / build_local/lsf / run_dry（JSON 摘要）/ main(argparse --sim-dir --output-dir --pattern --cores --queue --module-version --mode --dry-run)。

## 合成
- 资产 A（可见）：sim_dir_v1_vddsoc/（tck_clk_10corner.sp 10 corner=9 .alter + runsim.sh 命令模板）+ prompt.txt（U#6 逐字）+ task_brief.md（3 行交付接口）
- 隐藏 B：sim_dir_v2_vddio/（v2_vddio_8corner.sp 8 corner=7 .alter + runsim_b.sh，queue icfpga / cores 8 / module 2023.03-SP1，deck/节点/corner 数/queue/cores/版本均不同）+ hidden_manifest.json
- check 在 B 上 `--dry-run` 跑候选脚本，校验摘要 JSON 结构 / sp_files / total_alters / 命令格式 / LSF bsub / cores / queue / module load / 跨输入护栏 / 确定性 / pattern 过滤
