# trace_deepread — 1795068468777_09u61 (siyuji @ hfeg0plg72, mc11) · XTalk deepDFS 数据来源追踪

**日期**: 2026-11-21 r966 (peek + 深读 + 结构测绘; 合成留 DEBT 下一轮)
**trace_source**: user=siyuji, host=hfeg0plg72, session_file=1795068468777_09u61.messages.json, match_count=11, real_task_summary="阅读 xtalk.tcl 串扰分析自动化脚本，追踪 deepDFS 计算过程中每个信息项的来源文件/函数/变量"
**形态判定**: analysis-Q&A (code-comprehension) · **11-15 重审后合法任务形态** (旧规则下会被判 weak/explain 误杀)
**资产可物化**: ✅ 单文件 1219 行 TCL (40KB)，无 prod FSDB/netlist/GUI 依赖

## trace 对话流 (10 msgs, 2 user turn)

- **U[0]** (act): `~/Desktop/scripttest/zlong/xtalk.tcl 请你先认真阅读一下这个脚本`
  - A: read_files → 完整解读：基于 Synopsys CCK + HSPICE 的全芯片串扰噪声评估自动化脚本，分四阶段。
- **U[4]** (act): `在deepDFS的计算过程中，计算用到的信息都是从哪个文件、哪个函数获取的，以及对应的变量是什么`
  - A: read_files (重读关键段) → 输出「deepDFS 计算的数据来源完整追踪」表：每个信息项 → 来源 proc / 起点行 / 遍历方法 / 目标变量。
    - P-driver: `CalcPdrv` (L260), 入口 `cckExplore -method deepDFS -from $pwrHdl -proc CalcPdrv` (L744), 计算上拉等效电阻
    - N-driver: `CalcNdrv` (L437), 入口 `cckExplore -method deepDFS -from $gndHdl -proc CalcNdrv` (L751)

**主线交付意图**: 对 deepDFS 计算，结构化地给出「信息项 → 来源 proc(名+行) / 入口 cckExplore 调用(行+-proc 目标+-from 变量) / 关键变量」的 provenance 报告。**不是改脚本，是解析脚本产出溯源表。**

## xtalk.tcl 结构测绘 (deepDFS 相关, 用于下一轮合成 ground truth)

```
proc 总数: 10
  L15   proc mkindex {argv}            # 入口参数解析
  L102  proc getModelList {netlist}
  L117  proc genunit {device proj}
  L176  proc gen_top {netlist proj}
  L184  proc explore_inst {inst tid}    # (not used)
  L227  proc ::getResOrient::getResOrient {pwrHdl}        # BFS driver orient
  L232  proc ::getResOrient::getResOrientProc {instHdl tid}
  L260  proc CalcPdrv {inst tid}        # ← deepDFS P-driver (上拉等效电阻)
  L437  proc CalcNdrv {inst tid}        # ← deepDFS N-driver (下拉等效电阻)
  L620  proc get_driver {Pdrv Ndrv type vh vl}

deepDFS cckExplore 调用 (2 处):
  L744  cckExplore -method deepDFS -from $pwrHdl -proc CalcPdrv
  L751  cckExplore -method deepDFS -from $gndHdl -proc CalcNdrv

rail 句柄收集:
  L720  set pwrHdls ""
  L727  if {[lsearch $pwrHdls $railHdl] == -1}
  L728    lappend pwrHdls $railHdl
  L739  foreach pwrHdl $pwrHdls        # 驱动 CalcPdrv 入口

deepDFS 注释标记 (5 处, "for deepDFS"):
  L328, L373, L421, L557, L603  (return $::CCK_NULL ;# ... for deepDFS)
```

## 下一轮合成方案 (DEBT: 1, 已测绘可直接开工)

**case_id (拟)**: `EDA-Eval-DesignFlow-XtalkDeepDfsProvenanceAnalyze-001` (spice_sim, A 档 trace-faithful, L1)

**资产 A** = `xtalk.tcl` 真实 1219 行 (本轮已 scp 到 workdir，下一轮从 .75 workdir 或重新 scp)
**hidden B** = 合成 ~200 行 TCL 变体：**同名 proc 重命名** (CalcPdrv→PullRDrvCalc / CalcNdrv→SinkRDrvCalc / mkindex→buildArgIndex / gen_top→emitTopDeck …) + **行号平移** + **rail 变量改名** (pwrHdls→powerRailList / gndHdl→gndRailHdl / railHdl→curRail) + **保留同结构** (10 proc / 2 deepDFS cckExplore / 5 "for deepDFS" 注释标记)。anti-hardcode-A：B 的 proc 名/行号/var 名全异于 A。
**reference** `deepdfs_provenance.py`: 正则解析 TCL → JSON：
  - `procs`: [{name, start_line, args}] (10 条)
  - `deepDFS_calls`: [{line, method, from_var, proc_target}] (2 条)
  - `rail_vars`: {collect_var, collect_set_line, collect_iter_line}
  - `deepdfs_markers`: [行号…] (含 "for deepDFS" 的注释行)
**check.py** (拟 ≥12 断言 a-l):
  - a) zip 含 3 文件 (deepdfs_provenance.py / run.sh / spec.json)
  - b) py_compile analyzer OK
  - c) run.sh bash -n OK
  - d) analyzer 在 B 上 exit 0 产 JSON
  - e) JSON 顶层键齐全 (procs/deepDFS_calls/rail_vars/deepdfs_markers)
  - f) procs 数量 == B 实际 proc 数 (check 内独立 grep `^\s*proc ` 复算)
  - g) procs 名集合 == B 实际 proc 名集合 (anti-hardcode)
  - h) procs start_line == B 实际 proc 起始行 (独立 grep -n 复算)
  - i) deepDFS_calls 数量 == 2
  - j) deepDFS_calls 的 proc_target == B 实际 cckExplore -proc 目标 (独立 grep 复算)
  - k) deepDFS_calls line == B 实际 cckExplore 行 (独立复算)
  - l) deepdfs_markers 行集 == B 实际 "for deepDFS" 行集 (独立复算)
  - m) anti-hardcode-A: B 的 procs 名 ≠ A 的 procs 名 (硬编码 A 答案者 FAIL)
  - n) 确定性: 2 次运行 JSON 逐字节一致
**negative** (≥3 §4.9 三假): neg_empty / neg_print_expected (打印 A 的固定 JSON) / neg_core_removed (解析逻辑删，返回空 dict) → 全 FAIL；可选 neg_hardcode_a (返回 A 的 proc 名) → FAIL on (g/m)。
**k_rationale == k_check == 14 ✓ (≥8 硬闸门)**

**判分有牙依据**: check 内对 B 独立 grep 复算 ground truth (proc 名/行/cckExplore 目标/注释行)，与 analyzer 输出 JSON 逐一比对 → 硬编码 A / print-stub / 空壳 / 删核心 全暴露。B 的重命名+行平移保证 anti-hardcode-A。

## 本轮未合成的原因 (诚实)
本轮 r966 前 ~29 min 用于: mc-matrix 取证 → r965 已 park 的 high-mc fresh 重审 → 低 mc 段 (mc10-120) fresh spice 候选过滤 (59 条) → peek 2 候选 (09u61/9kx5a，均 analysis-Q&A 合法形态) → claim 09u61 → scp xtalk.tcl + 结构测绘。剩余预算 (~11 min) 不足以完成 hidden B 合成+ref analyzer+check(≥8)+三假+neg+自验+jsonl+台账+提交 的完整闭环；强赶产出 incomplete case (不能进 jsonl) 反而浪费。故本轮停在「claim+深读+测绘」，DEBT:1 留下一轮第一件事合成。

## 证据链
- mc-matrix: `python3 designflow/trace_ledger.py --shard B mc-matrix --src designflow/summary_1120_reconstructed.tsv` → mc≥10 pool=2072 touched=1789 fresh=283
- claim: `python3 designflow/trace_ledger.py --shard B claim --session 1795068468777_09u61 --user siyuji --host hfeg0plg72 --match 11 --domain spice_sim` → claimed
- xtalk.tcl: 1219 行 / 40283 B, 经 .75 SSH scp 到 eda_flow workdir; grep 结构测绘见上
- 09u61.messages.json: 10 msgs, 2 user turn (U[0] 阅读脚本, U[4] deepDFS 数据来源追踪)
