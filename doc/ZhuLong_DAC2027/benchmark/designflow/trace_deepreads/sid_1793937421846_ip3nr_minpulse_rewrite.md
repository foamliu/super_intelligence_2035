# Deepread: sid 1793937421846_ip3nr — MinpulseRewriteRun (berylwu @ hfeg0pkn002)

## Trace source
- session: `1793937421846_ip3nr.messages.json` (berylwu @ hfeg0pkn002, 67 msgs, 372KB, mtime 2026-11-06 NEW)
- 发现路径：本轮 11-06 12:0x 经 `.75 run_commands` 对 42 个 spice-active hosts 定向重扫(threshold 2026-11-06 06:00:00)→ 111 NEW sessions → dedup/scout → ip3nr 为最新且最干净 spice_sim 需求。
- shard B (spice_sim) ✓；trace-faithful A 档 ✓。

## USER 原话（A 档任务说明，逐字）
> /proj/commonIP/analog/v1_hl/lp5/v0/simdir/anasim/berylwu/ddgoa/rc_delay这个路径下，Dlyrc开头的几个文件夹下的minpulse_spf目录下的sp文件，替换里面的Old string (raw input)    : /proj/ddgoa/V0/model/current/
>   New string (raw input)    : /proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/
> 并直接run所有替换后的激励

- 纯需求轮 ✓（未指出根因、未给修复）。

## Assistant 工具链（36 tool calls）
1. `list_allowed_files` / `run_commands find` — 遍历 `rc_delay/Dlyrc*/minpulse_spf` 目录结构。
2. `editor explore_minpulse.py` + run — 探查 minpulse_spf 下 .sp 文件。
3. `read_files` — 读 sample .sp（含 `.inc /proj/ddgoa/V0/model/current/...`）。
4. `editor probe_logs/probe_env/probe_inode.py` + run — 探查运行环境/LSF。
5. `editor replace_model.py` + run — **核心**：批量替换 4 个 Dlyrc 目录下 minpulse_spf/*.sp 的模型路径 old→new。
6. `read_files` 验证替换后无 old 残留、new 存在。
7. `editor gen_submit.py` + run — 生成 `submit_minpulse.sh`（每目录 cd + `bsub -q fqueue3 -n 4 ... finesim -i <name>.sp -o <name>_TS/ -np 4`）。
8. `run_approved shell-runner submit_minpulse.sh` — 提交 32 jobs（LSF 1844147–1844182, PEND）。
9. `editor check_submit.sh` + run — 验证 LSF 提交 landed。
10. 最终 Summary → USER 接受。

## 金标准（trace 末尾用户接受结果）
- **32 .sp 文件改写**，4 个目录各 8 文件：
  - `Dlyrc_Pre/minpulse_spf` (8)
  - `Dlyrc_r1c/minpulse_spf` (8)
  - `Dlyrc_vdly/minpulse_spf` (8)
  - `Dlyrc_vint_Pre/minpulse_spf` (8)
- **每文件 5 处 old 路径 → new 路径 = 160 总替换**。
- 替换后：无 old 残留、new 存在；新模型目录 `/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/` 含 `model.sp` + `incFile_lp`。
- **32 jobs LSF 提交成功**（fqueue3, finesim -i ... -np 4, PEND）。

## 合成规划
- case_id: `EDA-Eval-DesignFlow-MinpulseRewriteRun-001` (spice_sim, A-faithful, L2)
- 交付：通用 `replace_and_run.py <root> <old> <new> <out_dir> [--sim] [--queue] [--run]`
  - 递归扫描 `Dlyrc*/minpulse_spf/*.sp`，替换 old→new，按原结构写 out_dir
  - 生成 `submit.sh`（bsub -q <queue> 包裹 `<sim> -i <name>.sp -o <name>_TS/ -np 4`）+ `replace_report.json`
- A/B 切分（跨输入护栏）：
  - A = 4 目录 × 8 文件 = 32（5 处/文件，ddgoa 路径）
  - hidden B = 3 目录 × 6 文件 = 18（4 处/文件，mtj 路径，不同目录名/计数/路径）
- check.py k=14 断言 a–n；L2 条件⑫ judge 侧把绝对路径 .inc 改写为本地空模型后 hspice 真跑重写后 B deck → job concluded。

## 自验结果
- 本地 check.py（MINPULSE_NOHSPICE=1）：**PASS 14/14**
- .75 HSPICE 真跑（l2_verify.py）：ref on B → 18 files / 72 repl / 3 folders ✓；hspice 重写后 B deck → rc=0 "job concluded" 无语法错 ✓
- 5 negative（empty/print_expected/hardcode_a/no_replace/wrong_counts）全 FAIL ✓
- §4.9 三假（empty/print_expected/no_replace）全 FAIL ✓
- 断言闸门 k_rationale=k_check=14≥8 ✓
