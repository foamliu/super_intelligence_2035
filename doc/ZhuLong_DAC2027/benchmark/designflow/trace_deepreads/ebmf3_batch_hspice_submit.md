# deepread: ebmf3 (chapinc @ hfeg0pkn002, mc=97) — batch HSPICE queue submission script

**session**: 1793270732926_ebmf3 / chapinc / hfeg0pkn002 / 10.129.2.11 / mc=97 / 82 msgs / spice_sim
**scan src**: summary_1105.tsv (shard B kw filter, mc>=10, fresh #2 by spice-ratio 0.91)
**claimed**: 2026-11-11 17:2x round

## USER#0 (verbatim, A-faithful source)
```
<user_input mode="act">你能帮我写一个python脚本自动往队列提交仿真吗，需要什么信息跟我提</user_input>
```
单 prompt 闭环（其后全 tool_use/result）。用户主动邀请 agent 提问（"需要什么信息跟我提"）。

## agent 提问 → 用户选择（ask_question 5 轮，按钮选项 = spec 来源）
1. 队列系统 → **LSF (bsub)**
2. 仿真工具 → **HSPICE (hspice)**
3. 输入形式 → **一个目录下多个 .sp netlist 文件，每个提交一个任务**
4. 参数细节 → **默认队列，无需特殊资源要求，日志按网表名.log**（但 agent 实现时用了 fqueue2h/8核/119min，见下）
5. 目录结构 → **激励和网表在同一个目录，.include 引用网表，hspice -i stim.sp -o stim_log**

## 产出（agent editor 14 次，最终 /home/chapinc/batch_submit_hspice.py）
`batch_submit_hspice.py` — 批量提交 HSPICE 仿真到 LSF 队列（bsub），stdlib only。

**CLI（argparse）**：
- `directory`（positional, default="."）— 存放 .sp 文件的目录
- `--pattern`（default=`*.sp`）— 文件匹配通配符
- `--exclude`（append, 多次）— 排除匹配文件
- `--queue`（default=`fqueue2h`）— LSF 队列名
- `--num-cores`（default=8）— CPU 核心数
- `--run-time`（default=119）— 最大运行时长（分钟，<2h）
- `--hspice-bin`（default=`hspice`）— hspice 可执行文件
- `--job-name-prefix`（default=""）— 任务名前缀
- `--extra-bsub-opts`（default=""）— 附加 bsub 参数（空格 split）
- `--list`（flag）— 仅列出匹配文件不提交
- `--dry-run`（flag）— 仅打印 bsub 命令不实际提交
- `--auto-confirm`（flag）— 跳过用户确认

**核心函数**：
- `collect_sp_files(directory, pattern, exclude_patterns) -> List[Path]`：`Path.resolve(strict=True)` + `sorted(glob(pattern))` + fnmatch 排除 + `.suffix.lower()==".sp"` 过滤（**非递归** glob）
- `generate_bsub_command(stim_file, queue, num_cores, run_time, hspice_bin, job_name_prefix, extra_bsub_opts) -> List[str]`：`["bsub","-q",queue,"-n",str(num_cores),"-W",str(run_time),"-J",job_name,"-o",log,"-e",err]` + extra_bsub_opts.split() + `[hspice_bin,"-i",stim_path,"-o",stim_dir/stem]`；log=`{stem}.log` err=`{stem}.err` job_name=`{prefix}{stem}`
- `collect_submission_info(stim_file, cmd) -> dict`：filename/job_name/log_file/err_file/command
- `print_summary_table(jobs)`：表格打印序号/文件名/任务名/日志文件
- `check_lsf_available()`：`which bsub` returncode==0
- `submit_jobs(jobs, dry_run, auto_confirm) -> int`：dry_run 打印命令；否则 input 确认后逐个 subprocess.run(cmd, timeout=30)，统计 success_count

**--dry-run 输出**：summary table + `[DRY RUN] 以下为将要执行的 bsub 命令：` + 每行 `  bsub -q fqueue2h -n 8 -W 119 -J <stem> -o <dir>/<stem>.log -e <dir>/<stem>.err hspice -i <dir>/<stem>.sp -o <dir>/<stem>`

**自验**（agent run_approved_command 9 次）：py_compile 通过、--help / --dry-run --list / --dry-run 正常、chmod +x。

## case 设计（A-faithful, spice_sim, L1, k=15）
- **deliverable**：`batch_submit_hspice.py`（CLI，stdlib only）
- **A-faithful 可行**：USER#0 是真实 produce-task 邀请（"写脚本自动往队列提交仿真"），spec 来自 ask_question 选项（LSF bsub + hspice + 单目录多 .sp + 默认队列/网表名.log）。prompt = 用户原话 + spec 澄清段。
- **判分**：subprocess 在隐藏 B 上跑候选脚本 `--dry-run`/`--list`，解析 stdout 验 bsub 命令结构（队列/核数/时长/jobname/log-err/hspice -i/-o）+ 过滤逻辑（--pattern/--exclude）+ 错误处理（不存在目录 exit≠0）+ 非递归（子目录 .sp 不提交）+ 后缀过滤（.scs 不提交）。不实际调 bsub/hspice（L1 离线）。
- **与既有 case 区分**：PostSimDeckBatch-001=后仿 deck 批量生成（PVT 替换+段重写）；本 case=LSF 队列批量提交脚本（bsub 命令生成+文件扫描过滤），distinct。MosToxeClassify=HSPICE model deck toxe 分类。无重叠。

## 资产可达性
- /home/chapinc/batch_submit_hspice.py（e0031982 guest 待验，但本 case A-faithful 用用户原话作 prompt，不依赖读 agent 产物；ref 自写）
- 判分只跑候选脚本 --dry-run/--list（不调 bsub/hspice），离线可判，无需 .75 仿真器
