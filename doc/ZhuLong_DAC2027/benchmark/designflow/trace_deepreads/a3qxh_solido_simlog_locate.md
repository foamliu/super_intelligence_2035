# 深读笔记 · a3qxh · Solido 仿真日志定位 how-to

- **session**: `1793347339807_a3qxh` (e0024852 @ hfeg0pkn002, mc23, spice_sim)
- **trace**: 子目录 `1793347339807_a3qxh/1793347339807_a3qxh.messages.json`，36 msgs / 220KB
- **scan**: ssh_eda_search_20261116_072610
- **造题**: EDA-Eval-DesignFlow-SolidoSimlogLocateGuide-001（how-to Q&A → 产出生成式 how-to 指南）

## 用户真实意图（原话）
1. `<user_input mode="act">how to find simulator log files?</user_input>`
2. 澄清选了 "Cadence Spectre/HSPICE logs"
3. `<user_input mode="act">/rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852 find this path simulator log file of solido</user_input>`
4. `<user_input mode="act">talk with me in chinese</user_input>`

用户想在一个 **Solido Variation Designer 工作目录**里找到仿真器日志文件的位置。这是典型的 how-to/咨询类真实意图（非 produce-task），按新标准属可造。

## agent 工具链与发现
- `ask_question` 澄清哪种仿真器 → Cadence Spectre/HSPICE
- `get_agent_policy_status` + `list_allowed_files` 探 `/rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852`（depth 2）→ 看到顶层 `logFile`(file)、`results/`、`Sram_high_sigma/`、`variation_designer*`、`per_device_setup.xml`、`project.setup` 结构 ⇒ 判定 Solido Variation Designer 工程
- `list_allowed_files` 探 `results/`（depth 2）→ 5 个 task 子目录 `FPVT-0/FPVT-1/MC-2/MC-5/MC-6`，每个含 `engine.log` + `summary.txt` + `summary.json` + `metrics/` + `results.db` 等
- `read_files` 读 `results/MC-6/summary.txt` → 含 `Simulator name: finesim (hspice-compatible)` + `Log file: .../results/MC-6/engine.log` + `Solido Variation Designer 2022.1.2`
- `list_allowed_files` 探 `Sram_high_sigma/<uuid>/00000000/` → 大量 `<NNNNNNNN>.tgz` 归档
- `editor` 写 `inspect_tgz.py` + `run_approved_command`(python-runner) 解包一个 `.tgz` → 内含 `simulator_stdout.log`(1.97MB)、`simulator_stderr.log`(0)、`run_simulator`、`netlist/tb_snm_solido.sp`
- 读 `run_simulator` + `simulator_stdout.log` 头部 → 实际启动器是 `Synopsys PrimeSim HSPICE V-2023.12`（`hspice tb_snm_solido.sp`）

## 关键事实（trace 真值，用于 A 档）
| 项 | 值 |
|---|---|
| 工具 | Solido Variation Designer 2022.1.2 |
| 仿真器后端 | finesim (hspice-compatible) |
| 实际启动器 | PrimeSim HSPICE V-2023.12 |
| workdir | /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852 |
| 顶层日志文件 | logFile (file) |
| results/ tasks | FPVT-0, FPVT-1, MC-2, MC-5, MC-6（5 个，各含 engine.log） |
| 每样本归档 | Sram_high_sigma/<uuid>/00000000/<NNNNNNNN>.tgz |
| 归档内日志 | simulator_stdout.log / simulator_stderr.log |
| 网表 | netlist/tb_snm_solido.sp |

## 合成决策
- **形态**：how-to Q&A → 产出生成式 how-to 指南（结构化 JSON 报告）。判分用脚本解析 doc/ 输入产报告，check 验关键知识点覆盖 + cross-input guard + A-leak + 真跑 + 确定性 + 4 假提交。
- **A（SUT 可见）**：重建 Solido workdir 树清单 `workdir_manifest.json` + `summary_sample.txt` + `simulator_stdout_head.txt` + `run_simulator_sample.sh` + `sample_archive_listing.txt` + `scenario.md`（全 trace 真值）。
- **hidden B（cross-input guard）**：合成 e0044471 的 spectre 后端 Solido 工程（不同 user/路径/版本/启动器/tasks/uuids/归档数/网表名/日志名），`_gen_B.py` 产 B 输入 + `_gt_B.json`。
- **判分**：check.py 19 条独立断言（a-s），10 条 cross-input 值守卫 + A-leak 守卫 + 确定性 + 真跑(subprocess)。
- **自验**：reference 19/19 PASS；4 negatives（空壳/print-only/hardcode-A/deleted-core）全 FAIL。
