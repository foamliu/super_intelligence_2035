# 深读笔记 q3lrp — signal→.run cross-ref via task bridge

## Trace meta
- session_file: `1793965015681_q3lrp.messages.json`
- user: `graywang` @ `hfeg0pjn140` (10.129.40.149)
- match_count: 210（kw=verilog:3443;pex:654;analog:227，但 c_tot=0 → 纯 A-domain）
- agent: deepseek-v4-flash (cxmt-deepseek-flash)
- 6 msgs / 单轮 user prompt / 1.2MB
- 模式判定: **CLEAN produce-task**（graywang 已 proven，r411 同用户出 PatternTaskXref-001）

## 原始用户需求（user_input mode="act"）
> 我给你一个文件 `/proj/.../cmname`，里面有很多信号名，你帮我在路径 `.../patterns/cmds_testmode/` 下的文件和文件夹中的文件里去找包含这些信号名的语句，然后根据语句所在的 task，去路径 `.../Regressions/` 下以 `.run` 结尾的文件中去找到有调用过这些 task 的文件，找到的这些文件的文件名不包含 `.run` 后缀就是我需要的 pattern name，你把所有符合条件的 pattern name 整理并去重后整理到一个文件里给我

三跳链：**signal → .v(task) → .run(pattern)**。
- 一跳：signal 出现在某 .v 文件的某 `task` 体内 → 把 signal 归到该 task
- 二跳：.run 文件里 `taskname()` 调用 → 把该 task 的 signals 归到该 .run
- 输出：每个 signal 的 pattern 名集合（.run 去 `.run` 后缀，去重）

## cmname 文件格式
```
  1 | cm0_ts_CompWrClkDly<0>
  2 | cm0_ts_CompWrClkDly<1>
  3 | cm0_ts_CompDrvSel<0>
  ...
```
- 信号名带 `<N>` 索引（Verilog bus 位选 angle-bracket 形式）
- 行号前缀（`  N | ` 格式），parse 时需 strip

## 关键难点（agent 的解法）
1. **索引归一化**：同一信号在 .v 文件里可能以三种形式出现：
   - `cm0_ts_CompWrClkDly<0>`（angle，与 cmname 一致）
   - `cm0_ts_CompWrClkDly[0]`（bracket，Verilog 也合法）
   - `cm0_ts_CompWrClkDly`（base，整 bus 不带位选）
   agent 的 `find_in_run.py` 为每个 signal 构造 search_set = {orig, `<N>`↔`[N]` swap, base}。
2. **task 归属**：扫 `.v` 文件用正则 `\btask\s+(\w+)\s*[\(;]` 提 task 定义，然后 task 体内找 signal 的 search_set 任一形式出现 → signal 归该 task。
3. **task→run 间接匹配**：扫 `Regressions/*.run` 找 `taskname()` 调用，把 task 的 signals 传播到该 .run 文件。
4. **直接 + 间接**：agent 同时支持「signal 直接出现在 .run」和「signal 经 task 间接出现在 .run」（双通道）。

## trace 结局
- agent 的 `find_in_run.py` 写到 Phase 1 + Phase 2 版本（先扫 .v 建 task→signal map，再扫 .run 找 task 调用 + 直接 signal 引用，输出 JSON）。
- **脚本 SIGKILL'd**（沙盒 timeout）→ trace 内未跑成功，但 deliverable spec 清晰可判分。
- agent 最后一次 editor new_text 是完整脚本（~150 行），结构完整。

## B 档合成判断
- trace 是工程只读 + agent 写工具但未跑通 → 不是 A-faithful（无最终可用 patch）。
- 需求边界清晰、可离线判分 → **B 档 synthesized**：把三跳 cross-ref 核心 + 索引归一化抽成纯 stdlib 脚本。
- 提供工作 reference 实现（trace 内 agent 脚本未跑通，case 必须给可跑的 gold）。

## 与 r411 PatternTaskXref-001 的区分（零重叠）
| 维度 | r411 PatternTaskXref | 本 case SignalRunXref |
|---|---|---|
| 输入 | 无独立 signal 文件，直接扫 cmds_mrs .v | 独立 `signals.txt` 文件（signal 名带 `<N>` 索引）|
| 一跳匹配 | task 定义 → 词边界扫引用（task 名直接在 .run）| signal → .v task 体（**三形式归一化** `<N>`/`[N]`/base）|
| 二跳 | 无（task 直接被 .run 引用）| **task → .run**（task 调用间接传播 signal）|
| 输出结构 | task_to_file / task_refs / file_refs | signal_to_runs / run_to_signals / task_to_signals / unmatched_signals |
| 判分重点 | 词边界（cfg 不匹 cfg_full）| 索引归一化（`<N>`↔`[N]`↔base 三形式）|
| 输入方向 | A: task 定义 → .run 引用 | A: signal(`<N>`) → .v(`[N]`) → .run；**B 反向**：signal(`[N]`) → .v(`<N>`) |

零 check 条件重叠：r411 全是词边界条件，本 case 全是归一化 + task-bridge 条件。

## case 落地
- case_id: `EDA-Eval-DesignFlow-SignalRunXref-001`
- domain: digital / L1 log-parser+cross-check / B档 synthesized
- deliverable: `signal_run_xref.py`（纯 stdlib，`--signals/--vdir/--rdir/--out`）
- A: 4 .v + 4 .run + 9 signals（8 matched + 1 unmatched）
- B: 5 .v（含 1 no-task `.inc`）+ 5 .run + 8 signals（7 matched + 1 unmatched），**B signal 文件用 `[N]` 形式（A 用 `<N>`），B .v 体用 `<N>` 形式（A 用 `[N]`/`<N>` mix）→ 测双向归一化**
- k=15 conditions，4 negative（naive_empty/print_only/core_removed/hardcoded_A）全 FAIL，§4.9(a)(b)(c) FAIL
- check.py 独立 oracle：line-based task block 扫 + token set 成员判定（与 ref 的 regex search_set 不同实现，避免同 bug 互掩）
