# Deepread — i4kkz (e0044979 @ hfeg0plg76, mc=20, spice_sim)

**trace**: `/home/e0044979/.cline/data/sessions/1793941518837_i4kkz/1793941518837_i4kkz.messages.json`
(698375 B, 47 msgs: 29 user-role [3 substantive user turns + 26 tool_results], 18 assistant)
agent = lead (e0044979 自己驱动 cline), 2026-11-05, CXMT Redwood lacaa TV1_FS SRAM characterization flow.

## 用户原话链 (3 substantive user turns)

### U0 (M00, ts=1793941520271) — 第一意图
> Check the run script: /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0044979/SRAM_tailor/CXN4HC2PS1024X72_8Tbitcell_NOpower_202610/run_two_stage_test.sh
> Will the python script in /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0044979/Python/schematic_gen_full_20261105/dspf-tool to be called?
> I have different version of the scripts. Just make sure if I set path in .sh file, the corresponding version to be called.

意图 = 验证 .sh 里设 TOOL_DIR 后到底哪个版本的 dspf-tool Python 包会被调用 (version-pinning Q&A)。
agent 答 (M16): Yes, 由 TOOL_DIR 经 `export PYTHONPATH="$TOOL_DIR/backend"` (line 151) 钉死；`python -m dspf.cli` 从 PYTHONPATH 解析；`backend/dspf/` 实存；POWER_TOOL=$TOOL_DIR/../tools/gen_tailor_power_reps.py 也跟随。caveat: line 31 是 plain 赋值非 env-overridable，要切换版本得编辑 line 31 或改成 `${TOOL_DIR:-default}`。

### U1 (M17, ts=1793942153434) — 第二意图 (主意图, 本 case 取此)
> For SRAM case at: /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0044979/artificial_SRAM/SRAM2048x256_8T/
> The tailor run time of each stage:
> === summary ===
>   stage1  wall=38:47.65  peakRSS=51515164 KB
>   stage2  wall=2:08:39  peakRSS=117126508 KB
>   detect_prep_sram_tb_post_job0 wall=0:00.67  peakRSS=29472 KB
>   xa_sram_tb_post_job0 wall=18:23.78  peakRSS=10739800 KB
>   detect_sram_tb_post_job0 wall=2:10.43  peakRSS=57688 KB
>   tailor_map_sram_tb_post_job0 wall=8:02.21  peakRSS=59887476 KB
>   tailor_plan_sram_tb_post_job0 wall=2:42.25  peakRSS=8190180 KB
>   tailor_fold_sram_tb_post_job0 wall=59:02.76  peakRSS=43226824 KB
>   powerrep_sram_tb_post_job0 wall=52:07.41  peakRSS=69437172 KB
> there are log files in this directory. I've optimized taior_fold, powerrep_sram stages, but each of them still spent about 1 hour. Can I set multi-processing for the two stages. And also check why "Stage 2" took so long.

意图 = (a) 给 tailor_fold + powerrep 开多进程 (b) 诊断 stage2 为何 2:08:39 这么久。
agent 读 .time + stage2.log + powerrep.log + tailor_fold.log + 源码 (power_pool.py, gen_tailor_power_reps.py, dspf_fold.py, service.py), 答 (M46) 见下。

(无第三意图 — M19..M46 全是 U1 的 tool_results + agent 的最终回答)

## agent 最终回答 (M46) — verbatim 关键证据

### TL;DR 表 (agent 从 .time 文件复算)
| stage | wall | user | CPU% | peak RSS |
|---|---|---|---|---|
| stage2 (process full) | 2:08:39 | 12000s | 170% (~1.7 cores) | ~117 GB |
| tailor_fold | 59:02 | 3482s | 104% (~1 core) | ~43 GB |
| powerrep | 52:07 | 3707s | 128% (~1.3 cores) | ~69 GB |

→ `--workers 4` 已开但几乎没用，因长相位是单线程的。

### 1. powerrep — 有真并行杠杆，当前关着
dominant phase `supply_graph` = 1352s (22.5 min) of 3080s total. log 证据 (verbatim):
```
power: supply graph pool skipped: per-net state ~6951 MB exceeds the 1024 MB budget
       (DSPF_POWER_POOL_MAX_MB overrides); serial scan
```
guard 在 `tools/gen_tailor_power_reps.py:67`:
```python
_NET_POOL_MAX_STATE_BYTES = int(os.environ.get('DSPF_POWER_POOL_MAX_MB', '1024')) << 20
```
每 supply net pooled state ~6951 MB > 默认 1024 MB → pool 跳过退化串行。
**开法**: `export DSPF_POWER_POOL_MAX_MB=9216` (>7000) + `DSPF_WORKERS=8`. 坑: 每 worker 拷 ~7GB, peakRSS 会涨过 69GB。
connectivity audit 用固定 2 workers (硬编码 `audit_scans_parallel`, 非 --workers): `connectivity audit: before/after scans by 2 worker(s) in 947.5s`.

### 2. tailor_fold — 不是 runtime 开关，热循环是串行
并行部分: rc fragment assembly (`rc fragments: 4 file(s) by 4 worker(s) in 50.8s`) + coupling-emit shard N/4.
串行部分 (单核):
```
fold: coupling.db verify: ... 51061806 edges ... full verification passed in 529.1s   <- ~9 min, single core
fold: coupling_peri_peri.spf: 50570289 coupling line(s) in 46.4s
fold: deck checks done in 63.5s    (full re-read of the emitted deck)
fold: checking MOS DC connectivity against the input deck
```
+ load `12879346 collapsed terminal mapping(s)`. CPU% 104% ⇒ wall≈user, 全串行。
**无 env 开关**, 要真并行得 shard coupling.db verify + deck_check + DC-connectivity (代码改).
cache 复用: `fold: coupling.db verify cache written (.../dspfproc/tailor/coupling_verify)` — 重跑复用省 529s, 别删 cache dir.

### 3. stage2 为何 2:08:39
giant flat DSPF: 46862 MB (46.8 GB), 6.8M device cards, 1.93M nets, 51M coupling edges; peakRSS ~117GB, 887M minor page faults ≈ 3.5TB pages touched → memory/bandwidth-bound.
wall split (verbatim from stage2.log):
```
split      3761.6s   (~63 min, ~49% of total!)   <- largest single component
index       592.4s
stats        36.6s
conly         0.0s   (reused from stage 1)
+ pass A structure (A prescan 136.8s), pass C reduce, rc_reduced merge
  (43.96M coupling edges), coupling.db emit (51M edges, 160M nodes), classify (272.7s)
= total    7676.1s
```
CPU ~1.7 cores, 长 phase (split/merge/index) 单线程, 已 memory-bandwidth limited. 加 workers 过 4 主要涨 RSS 而非降 wall.

### Bottom-line recommendations (agent)
1. powerrep — 立即可做: `DSPF_POWER_POOL_MAX_MB=9216` + `DSPF_WORKERS=8`, 重启 22.5min supply_graph 并行; 监控 RSS (每 worker ~7GB).
2. tailor_fold — 无 env 开关: 已 --workers 4 但 529s coupling-verify + 63s deck-check + DC-connectivity 单线程; 重跑复用 tailor/coupling_verify cache; 真并行需 shard verify/connectivity (代码改).
3. stage2 — 非核数问题: 46.8GB flat DSPF, split≈63min, 117GB memory-bound, 仅 1.7 cores; 加 workers 不帮, 应攻 split/index 串行成本.

## 本 case 合成方向 (r698)

意图 = U1: SRAM dspf-tool two-stage characterization 流程的性能诊断 + 多进程开启 how-to (explain-Q&A + how-to produce).
形态 = produce-task: 写 `perf_diagnoser.py(workdir, out_dir)` 解析 `perf_summary.json` + `*.log` + `run_script.sh` → 结构化 JSON 诊断报告 (stages/bottleneck_phases/parallel_levers/no_lever_phases/recommendations/summary/tool_family).
A档 trace-faithful: A asset 用 verbatim perf summary (M17 原话) + verbatim log 串行跳过消息 (M46 引用) + verbatim run_script 关键行 (M16 引用).
hidden B cross-input guard: 不同 tool family (HSPICE measurement aggregation, 非 FineSim/dspf), 不同 stage 名, 不同 env var (MEAS_POOL_MAX_MB 非 DSPF_POWER_POOL_MAX_MB), 不同数值, 不同 no-lever phase (report_gen format-merge 非 fold coupling.db verify). 分析器必须现场解析 B, 硬编码 A 数值必 FAIL.
