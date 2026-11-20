# trace_deepread — 1793270732926_ebmf3 (chapinc @ hfeg0pkn002)

- **shard**: B (spice_char) · **domain**: spice_sim · **mc**: 97 · **spice_ratio**: 0.902 (hspice:339 / netlist:36)
- **session**: `/home/chapinc/.cline/data/sessions/1793270732926_ebmf3/1793270732926_ebmf3.messages.json` (82 msgs, lead agent)
- **A 档用户原话（IDX 0, verbatim）**: 「你能帮我写一个python脚本自动往队列提交仿真吗，需要什么信息跟我提」
  - 纯「提出需求」轮，用户未指出根因/未给修复方案 → 合规 A 档任务说明。

## 对话流（assistant 工具链）
1. `ask_question` ×5 澄清：队列=fqueue2h / 每任务 -n 8 / -W 119（<2h）/ 命令模板 `hspice -i <stim.sp> -o <stim_log>` / 同目录所有 .sp 各一独立任务 / 日志按激励文件名命名。
2. `run_commands` + `list_allowed_files(/home/chapinc)` + `read_files(ro.sp)` —— 查工作目录与已有激励文件结构（ro.sp：`.inc './netlist'` + PDK `.lib` + `.tran sweep` + 多条 `.meas`）。
3. `editor` 多段写 `/home/chapinc/batch_submit_hspice.py`（分头部/核心函数/工具函数/主入口）。
4. `run_approved_command`：py_compile 语法检查 → **发现 py<3.9 不支持 `list[str]`** → `editor` 把 `list[str]/list[Path]/list[dict]` 改 `typing.List[...]`。
5. `run_approved_command`：`--dry-run` 验证生成的 bsub 命令格式；`--help` 验证选项。
6. IDX 79 收尾说明；IDX 80 用户追问「是否需把脚本 copy 到仿真文件夹」→ IDX 81 答「脚本放固定位置，目录作第一参数传入即可」→ 用户接受。

## 金标准（用户实际接受的结果）
`batch_submit_hspice.py`，CLI：`directory`（位置参，默认 cwd）/ `--pattern`(默认 *.sp) / `--exclude`(多次,通配) / `--queue`(默认 fqueue2h) / `--num-cores`(默认 8) / `--run-time`(默认 119 分钟) / `--hspice-bin`(默认 hspice) / `--job-name-prefix` / `--extra-bsub-opts` / `--list` / `--dry-run` / `--yes`。
扫描目录匹配 *.sp（排除 excludes），每文件生成：
```
bsub -q <queue> -n <cores> -W <minutes> -J <stem> -o <dir>/<stem>.log -e <dir>/<stem>.err <hspice_bin> -i <abs.sp> -o <dir>/<stem>
```
dry-run 实测输出（trace IDX 69）：
```
bsub -q fqueue2h -n 8 -W 119 -J ro -o /home/chapinc/ro.log -e /home/chapinc/ro.err hspice -i /home/chapinc/ro.sp -o /home/chapinc/ro
```
带 LSF 可用性检查、提交前确认（--yes 跳过）、摘要表（序号/文件名/任务名/日志文件）。py<3.9 兼容（typing.List）。

## case 合成（EDA-Eval-DesignFlow-BatchBsubHspice-001）
- **交付**：`outputs/submit.zip` 内含 `batch_submit_hspice.py`。
- **A 资产**（真实附件，原文不加注解）：`simdir/ro.sp`（chapinc 真实激励，verbatim）+ `ro2_delay.sp` + `ro3_ac.sp` + `netlist`。
- **隐藏 B**：`hidden/simdir_B/` 自包含 stub deck —— `inv_tb.sp`/`nand2_tb.sp`/`ringosc_tb.sp`（不同 DUT/参数/结构，inline `.model` level=1）+ `skip_me.sp`（测 --exclude）。B 与 A 在 DUT/参数/结构上不同。
- **reference**：`batch_submit_hspice_ref.py`（spec-faithful）+ `check.py` **k=11 断言 a-k**。
- **L2**：check.py 用 subprocess 真跑 SUT 脚本（--dry-run/--list/--help）解析真实输出，并用真实 hspice 跑 B `inv_tb.sp` 断言 `hspice job concluded` 干净收尾（.75 真 hspice 实测 3 个 B deck 全 concluded）。
- **自验**：本地 fake hspice → REF 11/11 PASS；5 negative（empty/print_expected/hardcode_a/no_hspice_seg/wrong_defaults）全 FAIL；§4.9 三假（empty/print/ref-core-deleted）全 FAIL。
- **断言闸门**：k_rationale = k_check = 11 ≥ 8 ✓。
