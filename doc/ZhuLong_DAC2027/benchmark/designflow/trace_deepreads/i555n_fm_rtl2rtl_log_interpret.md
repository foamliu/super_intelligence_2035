# Deepread: i555n — Formality RTL-to-RTL log 解读 (analysis-Q&A)

- session: `1794227785944_i555n` (子目录 `1794227785944_i555n/`)
- user: e0046913 · host: hfeg0pkn003 (10.129.2.12) · mc=12 · domain: **verification**
- scan: ssh_eda_search_20261116_072610 (keywords fm:formality:…)
- trace: 23 msgs / 121KB · model deepseek-v4-flash · ts 1794227786..878 (≈2026-11-09 20:36–20:37 CST)
- 形态: **analysis-Q&A / log-interpretation** → 结构化中文解读报告（不产脚本、不改文件）
- 复活来源: parked_reaudit_A.tsv (旧 weak 筛子判 "1 user-turn diagnostic not produce-task" → 11-15 令复活)
- ledger: A 状态 parked(r503-era) → claimed(r634) → 待合成后 mark case

## 用户原话（verbatim, msg[0]）
`<user_input mode="act">/proj/lacaa/TV1_digital/simdir/yutingq/FM_1109/flow_sync_level2level/logs 解读fm log情况</user_input>`

用户意图：给定一个 FM (Formality) 日志目录，**解读这份日志的运行情况**（是什么、跑了什么、结果如何、为什么）。这是纯分析/咨询任务，不要求修改文件或重跑。

## agent 工具链（23 msgs, 11 assistant turns）
1. `get_agent_policy_status` → enforcing, profileIds=[python-runner, shell-runner]
2. `list_allowed_files(/proj/.../flow_sync_level2level/logs, depth=2)` → 仅 1 个文件 `fm_rtl2rtl.log`
3. `run_commands`(`wc -l ...`) → **被 policy 禁用** ("Raw shell tool run_commands is disabled; use run_approved_command")
4. `read_files(fm_rtl2rtl.log, 1-120)` → 头部：Formality V-2023.12-SP5 banner
5. `read_files(fm_rtl2rtl.log, 120-2200)` → 全量（实际 527 行）
6. `read_files(fm_rtl2rtl.log, 166-462)` + `(209-388)` → 中段 set_top / 错误
7. `list_allowed_files(data/)` → rtl_ref/ rtl_fail/ + 3 个 .f filelist
8. `list_allowed_files(FM_1109/)` → Makefile / scripts/fm.tcl / setup/ / flow_*/
9. `read_files(syn_filelist.f, impl_pass.f, impl_fail.f, rtl_ref/.v:1-20, rtl_fail/.v:1-20)` → filelist 内容 + RTL 模块声明
10. `read_files(Makefile, 1-120)` + `(120-160)` → DESIGN 变量 + fm_r2r 目标
11. **最终回答 (msg[22])**：结构化中文报告（六节：是什么/执行步骤/根因/结论/命名细节/修复建议）

## 关键事实（全部 verbatim 可溯到 fm_rtl2rtl.log 行号）

### 1. 工具/版本/模式
- log L4: `Version V-2023.12-SP5 for linux64 - Jul 03, 2024`
- log L189: `set FM_MODE $FM_MODE ;# rtl2gate | gate2gate | rtl2rtl`
- log L317: `RM-Info: Skipping SVF for rtl2rtl mode`  ⇒ **FM_MODE = rtl2rtl**
- Makefile L8: `DESIGN = sync_level2level`；L20: `fm_r2r` 目标 → `FM_MODE := rtl2rtl`
- log L358–359: `Loading verilog file '.../rtl_ref/sync_level2level.v'` / `Current container set to 'r'`

### 2. 错误序列（根因链）
- log L383: `set_top r:/WORK/${DESIGN_NAME}`
- log L384: **`Error: Unknown name: 'r:/WORK/sync_level2level' (FM-036)`**  ← set_top ref 失败
- log L417: `Error: Top design has not been successfully linked in container 'r' (FM-236)`
- log L433: `set_top i:/WORK/${DESIGN_NAME}`
- log L434: **`Error: Unknown name: 'i:/WORK/sync_level2level' (FM-036)`**  ← set_top impl 失败
- log L487/490/511: **`Error: Reference design not set (FM-045)`** (preverify / match / verify 全失败)
- log L513: `Error: Top design has not been successfully linked in container 'r' (FM-236)`
- log: `save_session` → `Error: No session file generated. Reason : No such file or directory. (FM-427)`

### 3. 根因（agent 结论，已核实）
**Design 名与 RTL 模块名不一致。** Makefile `DESIGN=sync_level2level` ⇒ fm.tcl 用 `set_top r:/WORK/sync_level2level`，但两份 RTL 文件里的模块声明都是：
```verilog
module sync_level2level_impl( clk, rst_b, sync_in, sync_out );   // rtl_ref + rtl_fail 均如此
```
⇒ `set_top` 找不到 `sync_level2level` (FM-036) → reference design 未设定 (FM-045) → match/verify 全未执行。

### 4. 结论（关键判断）
**这不是一次"形式验证 FAIL"，而是一次从头没走通的配置错误。** match/verify 都没真正执行：
- log L523: `CPU usage for this session: 2.33 seconds`
- log L525: `Elapsed time: 17 seconds`
- log L521: `Current time: Mon Nov  9 20:33:51 2026`（开始 20:33:43，17s）
- 没有生成 `.done` / session / failing-point 报告。日志只有一串早期 setup 报错。

### 5. 命名细节（filelist 语义）
- `syn_filelist.f` = `/proj/.../rtl_ref/sync_level2level.v`（参考/golden）
- `sync_level2level_impl_pass.f` = `/proj/.../rtl_ref/sync_level2level.v`（注释：与 golden 逻辑一致，期望 PASS）
- `sync_level2level_impl_fail.f` = `/proj/.../rtl_fail/sync_level2level.v`（注释：注入输出取反 bug，期望 FAIL）
- RTL 头注释: rtl_ref = "EXPECTED FORMAL PASS / Identical logic"；rtl_fail = "EXPECTED FORMAL FAIL / final output stage INVERTED (~sync_ff[...])"
- Makefile L27: `FM_IMP_RTL_FILELIST ?= ""`（默认空串；log 实际读了 `..._impl_pass.f`）

### 6. 修复建议（agent 给出三选一）
对齐 top 名与 RTL 模块名：① 改 Makefile `DESIGN = sync_level2level_impl`；② 改 RTL `module sync_level2level`；③ fm.tcl `set_top` 用 `sync_level2level_impl`。改完 `make fm_r2r`（传 `FM_IMPL_RTL_FILELIST`）：pass.f→PASS，fail.f→FAIL。

## 资产保真（asset_fidelity = trace-embedded，同 r631 Lpddr5 模式）
**原始文件无法 scp**（`/rundata/lacaa/...` 属 e0046913，e0031982 Permission denied）。资产从 cline trace 的 `read_files` tool_result 重建（去行号前缀），已 stage 到 `trace_deepreads/i555n_staged_assets/`：
| 文件 | 来源 msg | 行数/大小 | 完整性 |
|---|---|---|---|
| `fm_rtl2rtl.log` | msg6(1-120)+msg8(120-2200) | 527 行 / 31KB | **完整** |
| `Makefile` | msg19(1-120)+msg21(120-160) | 160 行 / 4.5KB | **完整** |
| `syn_filelist.f` | msg17 | 1 行 | 完整 |
| `sync_level2level_impl_pass.f` | msg17 | 1 行 | 完整 |
| `sync_level2level_impl_fail.f` | msg17 | 1 行 | 完整 |
| `rtl_ref_sync_level2level.v` | msg17(1-20) | 19 行 | **部分**（仅 agent 读到的头部，含 `module sync_level2level_impl` 声明 — 足证根因） |
| `rtl_fail_sync_level2level.v` | msg17(1-20) | 19 行 | **部分**（头部，含 INVERTED 注释 + 模块声明） |

> `.v` 文件 agent 只读了 1–20 行（足以确认模块名）；完整 RTL 不在 trace 中。合成时以头部为 asset，并在 task 说明里如实标注"RTL 头部（trace 已读范围）"。

## 合成计划（next round, C-A analysis-Q&A 模板，承 r588–r631）

- **case_id**: `EDA-Eval-DesignFlow-FmRtl2rtlLogInterpret-001`（fresh 复活，非 v2）
- **domain**: verification · **A 档 trace-faithful**（用户原话逐字作 task 说明）
- **deliverable**: `fm_log_interpret_report.json` only（结构化 JSON 解读报告，非 .md/脚本）
- **A 资产**（SUT 可见）: `fm_rtl2rtl.log` + `Makefile` + 3 filelist + 2 RTL 头 → zip 进 assets
- **隐藏 B**: 构造一份**不同失败模式**的 FM log（e.g. set_top 成功但 verify 真 FAIL 有 failing point；或 DESIGN 名一致但 read_verilog 路径错 NOFILE），配套不同 filelist/Makefile。B 与 A 在**失败模式 / 错误码 / design 名 / 是否生成 session** 维度不同 → anti-hardcode
- **check() 结构 (k≥8, k_rationale=k_check)**:
  - content-correctness (a–n, ~14): tool=Formality / 版本=V-2023.12-SP5 / 模式=rtl2rtl / design=sync_level2level / RTL 模块=sync_level2level_impl / set_top 失败 FM-036 / ref 未设定 FM-045 / match+verify 未执行 / 非"验证FAIL"而是配置错误 / CPU 2.33s / 17s elapsed / 无 session 生成 / filelist 语义(pass→ref, fail→rtl_fail) / 修复方向(对齐 top 名)
  - evidence-verification (o): 报告内 ≥8 distinct evidence token，每个是 fm_rtl2rtl.log 真实子串（行号可溯），覆盖 版本+FM-036+FM-045+set_top+CPU+module名
  - B judge-self-check (p): 内嵌 `_parse_b_log` 独立解析 B，A 报告与 B truth ≥6 维度全异（失败模式/design/错误码/是否set_top成功/是否verify执行/有无failing point）
  - 3-seed (q): 打乱 B 解析顺序，sha256 稳定
- **A_FILES 内联进 check.py**（自包含，参考 r631 模式），避免 SUT 沙箱泄漏 reference
- **自验**: ref PASS + 2+ negative FAIL (empty/print-expected/wrong-rootcause) + §4.9 三假 FAIL + e2e jsonl test field 独立跑 PASS

## 备注
- run_commands 被 policy 禁用是 trace 真实细节（agent 改用 read_files），不影响任务形态。
- 这条 trace 是 e0046913 当天 FM_1109 调试会话之一；C 台账标 "wrong-shard A"（verification 属 A），A 台账标 parked，现复活。
