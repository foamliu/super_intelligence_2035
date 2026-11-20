# TRACE_TRIAGE_RUNBOOK — 696 例全量批次的失败归因执行手册

> 工具：`doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/05_batch_triage.py`
> （stdlib-only，py3.8+，已在 Windows 本机 `--selftest` 79 项全过）
>
> 本文只讲**在集群上怎么按顺序敲命令**、产物放哪、出事怎么排查。
> 本地自测：`python3 05_batch_triage.py --selftest` → `ALL SELFTEST PASSED`

---

## 0. 关键事实（不要写错的口径）

- 最新批次: `run_batch_20261109_171201`，696 cases / 8 workers / 2400s 超时
- 结果: PASS 62 / FAIL 558 / ERROR 70 / ABSENT 6
- `Pass% = PASS/(PASS+FAIL) = 62/620 = 10.0%`（论文正文用这个）
- `62/626 = 9.9%`（ERROR 记 non-pass，绝大多数表格里的数字）
- `62/696 = 8.9%`（ABSENT 也进分母）
- 本工具输出三种口径全部写进 `triage_summary.json` 的 `meta.pass_rate` /
  `overall.pass_rate`，tex 表头注释里也写了 `62/626 = 9.9%`。**引用时别混用口径。**

---

## 1. 上集群前：先把路径变量钉死（逐条执行）

```bash
cd ~/code/EDA-Flow-Bench            # 仓库根，按实际改
export REPO="$PWD"
export TRIAGE="$REPO/doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage"
export RUN="/nasdata/app.e0031982/code/EDA-Flow-Bench/eval/run_batch_20261109_171201"
export CASES="/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl"
export OUT="$TRIAGE/results/run_batch_20261109_171201"

ls -ld "$RUN" "$CASES" "$TRIAGE"          # 三个都必须存在
python3 --version                          # 需要 >= 3.8
```

---

## 2. 探结构（**必须先做**，不要直接全量跑）

### 2.1 看批次目录真实长相

```bash
find "$RUN" -maxdepth 2 | head -50
find "$RUN" -maxdepth 3 -name 'submit.zip'  | head -5
find "$RUN" -maxdepth 3 -name 'check*.log'  | head -5
find "$RUN" -maxdepth 3 -name 'judge*.json' | head -5
du -sh "$RUN"
```

把看到的形状对上工具的布局假设：

| 你看到的形状 | 对应 `--layout` |
|---|---|
| `$RUN/<task_id>/...` | `flat` |
| `$RUN/cases/<task_id>/...` | `nested` |
| `$RUN/worker_3/<task_id>/...` 或 `shard_7/...` | `shard` |
| 完全不一样（如 `$RUN/out/20261109/<task_id>`） | 仍用 `auto`，并加 `--case-glob "$RUN/out/20261109/{task_id}"` |

### 2.2 小样本 dry-run（不写任何文件）

```bash
cd "$TRIAGE"
python3 05_batch_triage.py \
    --batch "$RUN" --cases "$CASES" --out "$OUT" \
    --dry-run --limit 8
```

**看三件事**：

1. `布局命中 : <root> xN` —— 命中的根目录对不对（不是 `. x0`）
2. 每个 case 的 `evidence=` 有东西（`judge_result.json` / `check.log` / `submit.zip`）
3. 末尾 `coverage : N/M 找到判分证据 (xx%)`

### 2.3 全量 dry-run（只打印，不落盘）

```bash
python3 05_batch_triage.py \
    --batch "$RUN" --cases "$CASES" --out "$OUT" \
    --dry-run | tee /tmp/triage_dryrun.log | tail -30
```

判定通过的标准：**`status : {'PASS': 62, 'FAIL': 558, 'ERROR': 70, 'ABSENT': 6}`**
（与 ground truth 完全一致）→ 再做第 3 步。差得多就先看第 6 节排查表。

---

## 3. 正式跑（一条命令出全部产物）

```bash
cd "$TRIAGE"
mkdir -p results
time python3 05_batch_triage.py \
    --batch "$RUN" \
    --cases "$CASES" \
    --out   "$OUT" \
    --emit-tex 2>&1 | tee /tmp/triage_full.log | tail -20
```

- 696 例预计 **1~4 分钟**（瓶颈在逐 case 扫文件；单 case 最多 40 个 json + 40 个文本，
  单文件上限 4MB / 4 万行，zip 只读中央目录不解压）
- 想要 json+tex、不要 report.md：加 `--json-only --emit-tex`
- 只想快速验证管道：加 `--limit 50`

---

## 4. 产物清单与预期体量

```
$OUT/
├── triage_summary.json          ~1.5–4 MB   每 case 的 status/class/decision/证据路径
├── report.md                    ~30–60 KB   人读：总体+逐域+类别 top+unknown+10 抽样
└── tables/
    ├── status_by_domain.tex     ~2–4 KB     Domain/PASS/FAIL/ERROR/ABSENT/Total/Pass%
    └── failure_by_domain.tex    ~2–4 KB     逐域失败类别（TO/INFRA/NOSUB/FMT/RT/SEM/ANTI/UNK）
```

`triage_summary.json` 顶层结构（便于脚本再加工）：

```json
{
  "tool":   {"name": "05_batch_triage.py", "version": "1.0.0"},
  "meta":   {"batch_dir", "cases_jsonl", "index_stats", "pass_rate", "repro_command", ...},
  "overall":{"total", "counts", "pass_rate", "unknown_ratio", "unknown_kinds", "wall_max_sec"},
  "class_order": ["PASS","ERROR_TIMEOUT","ERROR_INFRA","NO_SUBMIT","FORMAT_CONTRACT",
                  "ASSERT_RUNTIME","ASSERT_SEMANTIC","ASSERT_ANTIHARDCODE","UNKNOWN"],
  "failure_classes": {...},
  "domains":  {"<domain>": {"status": {...}, "class": {...}, "total": n}},
  "coverage": {"judged_cases", "judged_ratio_pct", "warnings": [...]},
  "cases":    [{"task_id","domain","status","class","unknown_kind","decision",
                "wall_sec","coverage","evidence":{"case_dir","verdicts","logs",
                "submit","hit_files","skipped_json"}}]
}
```

tex 表可直接 `\input`：

```latex
\begin{table}[t]\centering
\caption{全量 696 例评测状态矩阵（Pass\% = PASS/(PASS+FAIL)，62/626 = 9.9\%）。}
\input{tables/status_by_domain.tex}
\end{table}
```

`failure_by_domain.tex` 有 10 列，若超版心，整表套
`\resizebox{\columnwidth}{!}{ ... }`（表头注释里已写）。

---

## 5. 回仓库（**不要**把原始 trace 入库）

```bash
cd "$REPO"

# 1) 结果文件：只入 results/ 下的三件套
mkdir -p doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/results/run_batch_20261109_171201
cp -r "$OUT"/. \
      doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/results/run_batch_20261109_171201/

# 2) 自检没有夹带大文件（<5MB 才正常）
du -sh doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/results/run_batch_20261109_171201
find doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/results -size +5M

# 3) 只 add 结果目录 + 工具本身
git add doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/05_batch_triage.py
git add doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/TRACE_TRIAGE_RUNBOOK.md
git add doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/results/
git status --porcelain | head -20
git commit -m "eval_triage: 696-case failure triage (batch run_batch_20261109_171201)"
```

**入库路径（唯一）**：
`doc/ZhuLong_DAC2027/benchmark/designflow/eval_triage/results/run_batch_20261109_171201/`

**禁止入库**：
- `$RUN` 本身（原始 trace / submit.zip / 安装日志，GB 级，且含机器信息）
- `/tmp/triage_*.log`
- 任何 `*.trace` / `pi.log` / `session*.json` 原始会话

建议在该目录放一条 `.gitignore` 兜底：

```gitignore
# eval_triage/results/.gitignore
*.log
*.trace
*.jsonl
submit.zip
```


## 6. 出问题怎么排查（按症状查表）

| 症状 | 大概率原因 | 怎么办 |
|---|---|---|
| `ERROR: 批次目录不存在或不是目录` | 路径拼错 / 在开发机上跑集群路径 | 用 `ls -ld "$RUN"` 确认；Windows 上跑 Linux 路径必然失败，这是**预期**行为 |
| dry-run 末尾 `布局命中 : . x0`，`coverage 0/696` | case 目录不是 `$RUN/<id>`，也可能 id 与目录名不一致 | `find "$RUN" -maxdepth 2 \| head -50` 看形状；再 `--layout flat/nested/shard` 或 `--case-glob "$RUN/<真实前缀>/{task_id}"` |
| 命中率 30%~60%，`ABSENT` 异常多 | 有 worker 分片目录没被枚举到（不是 `worker_N`/`shard_N`/`wN`） | `find "$RUN" -maxdepth 1 -type d` 看分片命名，然后 `--layout auto --max-depth 6`（退化全树扫描会兜住） |
| `status` 里 `ABSENT` = 0 但 ground truth 是 6 | 找错了目录（例如命中了 oracle 目录） | 看 `triage_summary.json` 里某条 `evidence.case_dir`，人工 `ls` 一下对不对 |
| `coverage` 很低（<50%）+ `UNKNOWN` 很高 | 判分产物名字不在白名单（`check/judge/grade/verdict/result/summary/eval/report/status`） | 看一个 case 目录：`ls -la <case_dir>`；把真实文件名报回来，扩 `TEXT_SUMMARY_NAME_RE` / `VERDICT_JSON_NAME_RE` 或加 `--case-glob`；短期可在 `report.md` §5 的 `coverage_warnings` 里逐条人工看 |
| `ERROR` 远多于 70，且大多是 `UNKNOWN` 类 | 日志里没有 infra/timeout 签名 | 抽 3 条看 `evidence.logs[*].err_lines`；若 harness 用的是别的话术（如 `gateway timeout`/`RPC failed`），补进 `INFRA_SIG` 或 `TIMEOUT_SIG` |
| `ERROR` 远少于 70（很多 ERROR 被算成 FAIL） | 判分 json 里写了 `"pass": false` 而真实状态是 ERROR | 结构化判定优先级最高；确认 harness 是否另写 status 字段（`status: "ERROR"` 已被识别） |
| 全是 `UNKNOWN`、`NO_SUBMIT` | 交付物不叫 `submit.zip`（如 `submission.tar.gz`、`answer/`、`out.zip`） | 目前识别 `submit/submission/answer/deliverable/solution/final` + `.zip/.tar/.tar.gz/.tgz`；名字不同就改 `SUBMIT_FILE_RE` / `SUBMIT_DIR_NAMES` |
| 跑得特别慢（>15 min） | 某个 case 目录里塞了巨型 oracle 树 | 单 case 上限 4000 文件 / 40 json / 40 文本，已封顶；可 `--limit 100` 先跑通再看 profile |
| `Pass%` 和论文 9.9% 对不上 | 口径混用 | 本工具表内是 `PASS/(PASS+FAIL)`；9.9% 是 `62/626`（ERROR 记 non-pass）；8.9% 是 `62/696` |

**永远不要**为了让数字对上 ground truth 而手改结果；先 `--dry-run --limit 8` 把
`case_dir` + `evidence` 打出来，用证据说话。

---

## 7. 方法说明（写论文附录时可直接引）

**证据分级**（越靠前越硬）

| tier | 来源 | 举例 |
|---|---|---|
| 1 | 结构化判定 json（`pass/passed/verdict/result/status/grade/success/ok/score`，支持一层嵌套） | `judge_result.json: {"pass": false}` |
| 2a | 判定行的强标记（行首 `PASS`、`PASS:`、`verdict: ... PASS`、`case X: PASS`） | `check.log: "FAIL: condition 3 not met"` |
| 2b | 正文里的弱标记（裸词出现）→ 判但仍打 coverage 警告 | 被迫兜底时才用到 |
| 3 | 交付物 `submit.zip` 能否打开 / 是否空 zip（真实机器检查） | `BadZipFile` → `FORMAT_CONTRACT` |

**失败分类的触发证据**（每条都写进 `triage_summary.json`）

| class | 触发条件（机器可核验） |
|---|---|
| `ERROR_TIMEOUT` | `wall >= 2400s`，或日志命中 `timed out/timeout/deadline exceeded/killed after`（纯 `timeout=2400` 配置行被过滤） |
| `ERROR_INFRA` | 日志行命中 `MCP/connection refused|reset/ECONNRESET/gateway/rate limit/429/API-key/...` 且不含 agent 逻辑排除词 |
| `NO_SUBMIT` | 判定为 FAIL 但 case 目录内无任何 submit 交付物 |
| `FORMAT_CONTRACT` | submit zip 打不开 / 空 zip / 空 submit 目录，或日志命中 `BadZip/missing entry/naming/...` |
| `ASSERT_RUNTIME` | 日志命中 `Traceback`/`returncode [1-9]`/`No such file or directory`/`syntax error` |
| `ASSERT_ANTIHARDCODE` | 同时出现「可见 A 通过」与「hidden/held-out/B 失败」 |
| `ASSERT_SEMANTIC` | 日志命中失败条件编号：`condition|check|test #N ... FAIL`（编号写进 `evidence.fail_conditions`） |
| `UNKNOWN` | 以上都不命中 → **单列，绝不并入别类**，并计入 unknown 比例与 coverage 警告 |

分类优先级（docs 同 `classify_fail` docstring）：
`NO_SUBMIT > FORMAT_CONTRACT > ASSERT_RUNTIME > ASSERT_ANTIHARDCODE > ASSERT_SEMANTIC > UNKNOWN`。
理由：脚本没跑完就没有语义比较；anti-hardcode 是语义不符里更具体的子情形。

**unknown 比例** = `UNKNOWN / (FAIL + ERROR)`，同时给 `UNKNOWN / Total`；
报告 §5 会显式列出 `UNKNOWN` 的构成（`NO_EVIDENCE_AT_ALL` / `NO_VERDICT_BUT_SUBMIT`）。

---

## 8. 已知限制（写进 limitations，不要藏）

1. 文本层是**启发式**：强/弱标记只基于行内词法，不理解语义；因此 weak 命中的
   case 一律带 coverage 警告，`report.md` §7 给了 10 例随机抽样供人工复核。
2. `FORMAT_CONTRACT` 只能核验「zip 打不开 / 空」这类通用契约；「缺哪个 entry」
   依赖日志自述或 oracle 清单（本工具不读 oracle，避免误用 ground truth）。
3. `ASSERT_SEMANTIC` 只能给出**失败条件编号**，无法给出「应该是多少」——那是
   oracle 的工作，工具不越界。
4. 若 harness 未落任何判分产物，任何工具都只能报 `UNKNOWN`；本工具的价值是
   **把这种情况显式计数并列出清单**，而不是假装知道。



---

## 9. 本机自测证据（随工具一起入库）

| 文件 | 内容 | 复现命令 |
|---|---|---|
| `05_selftest.out.txt` | 81 项断言的完整输出，末行 `ALL SELFTEST PASSED` | `python3 05_batch_triage.py --selftest` |
| `05_dryrun_missing_path.out.txt` | 对着**不存在**的集群批次目录跑 `--dry-run` 的报错（应看到 `ERROR:` + `提示:` + `探针:` 三行，退出码 2） | `python3 05_batch_triage.py --batch /nasdata/.../run_batch_20261109_171201 --cases .../EDA-Eval-DesignFlow.jsonl --out results/run_batch_20261109_171201 --dry-run` |

自测覆盖（12 个合成 case / 4 域 / 目录混搭 `flat` + `cases/` + `w3/`）：
PASS 2、FAIL 7、ERROR 2、ABSENT 1；Pass% = 2/9 = 22.2%；coverage 9/12 = 75.0%；
UNKNOWN 2（22.2% of FAIL+ERROR）；每个 FAIL 子类各 1 例
（`ASSERT_SEMANTIC` / `ASSERT_ANTIHARDCODE` / `NO_SUBMIT` / `FORMAT_CONTRACT` /
`ASSERT_RUNTIME`）、`ERROR_TIMEOUT`、`ERROR_INFRA` 各 1 例，另有 1 例「无判分证据」。
断言还覆盖：tex 逐行内容、report.md 抽样 10 例、`--json-only` 不写 tex/md、
二次运行确定性、`--dry-run` 不落盘、id 键别名探测、缺失键/缺失目录退出码 = 2。
