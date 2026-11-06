# 深读笔记 — sid 1786587864281_hvynl (r188 候选)

- **trace**: `1786587864281_hvynl` · user `e0014566` @ `hfeg0pkn005` · mc=162 · 102 msgs / 508KB messages.json
- **session 窗口**: 2026-08-13 02:24 → 02:58 (exit_code=1)
- **关键词分布**: 399 virtuoso · 85 cellview · 9 dbGet · 5 calibre · 4 "lang":"skill" · 3 spectre
- **domain**: pg_layout（Virtuoso RsCalc 电阻计算流，power-network 电阻准备）
- **真实工作目录**: `/home/e0014566/test_layout_rscalc_flow_12/`（在 .75 = hfeg0pkn005 上可达）

## 用户意图轮（A-档 seed 候选）

- **msg#0（逐字原文，纯需求 seed）**:
  > 读文档 prompt_flow.md , 只执行里面 rscalc 电阻计算这一步，算出每隔RNODE处的电阻。
  - 纯需求：读 flow 文档 → 只执行 rscalc 这一步 → 算出每个 RNODE 处的电阻。
  - 未指出根因、未给修复方向 → 合格 A-档 seed。
- msg#27/136: `/continue`、`continue` — 推进轮，非 seed。
- 后续用户轮（msg#82 cdl/v2lvs 等）属不同子任务，不纳入本 case。

## assistant 工具链（关键产物）

1. read `prompt_flow.md` + `common.config` + `rscalc.config` + `SKILL.md` + `run_rscalc_nogui.il` (assets/run_rscalc_nogui.il, 710 行)
2. 用 `gen_rscalc_agent.py` 把 18 个 config 参数内联进 `run_rscalc_nogui.il` → 生成 `run_rscalc_agent.il` (36189B) + `.cmd`
3. 用 `SandBox_MCP_Server__run_code` (lang=skill) + `run_commands` (setsid detached) 启动 `virtuoso -nograph -replay run_rscalc_agent.il`
4. 多轮 poll/wait（poll_wait.sh）监测 `DONE!` sentinel
5. **崩溃**：process 跑到 label-extraction 阶段后 exit（无 `DONE!`，`addNets.txt` 0 bytes）

## 真实 bug + 根因（msg#97 / msg#99 逐字）

```
*Error* dbILGetDbObject: invalid dbObject - (db:0x2f65389a 0 0)
*Error* load: error while loading file at line 739
```
agent 诊断（msg#99 逐字）:
> The error is `dbILGetDbObject: invalid dbObject` in `CXMTTransformedLabelToTopPri`
> (line 287: `dbGetTrueOverlaps` + `item~>theLabel` access) — the cellview's
> dbObjects became **stale after `leoXstreamOut`** (the GDS streaming invalidated
> handles in the opened cellview). The fix is to **reopen the cellview after GDS
> streaming**, before label extraction.

## 源码定位（run_rscalc_nogui.il, 710 行 / 35404B）

- L281 `procedure( CXMTTransformedLabelToTopPri(runDir myLayer type cfgNet1)`
- L286 `cvId=geGetWindowCellView()` ← 取当前 window 的 cellview
- L287 `myshpList=dbGetTrueOverlaps(cvId cvId~>bBox myLayer 0:999 t)` ← **崩溃点**（cvId 已 stale）
- L290-291 `item~>theLabel` ← 同样 stale
- L398 `foreach(myLayer NetLayers CXMTTransformedLabelToTopPri(...))` ← NetLayers (RTEXT) 调用点
- L402 `foreach(myLayer PointLayers CXMTTransformedLabelToTopPri(...))` ← PointLayers (RNODE) 调用点
- L583 `procedure( RunRsCalcNoGui()` ← 主入口
- L620 `geOpen(?lib libName ?cell cellName ?view viewName ?mode "r")` ← **唯一一次** 开 cellview
- L680 `leoXstreamOut(... ?layermap G4B_layermap ?info t)` ← iejoad 分支
- L682 `leoXstreamOut(... ?layermap leGlobalVariables->layerMap ?info t)` ← 默认分支（本 case 命中）
- L692 `CXMTutRscalc_run(gdsDir pwrNets cellName ...)` ← 调用 core（内含 L398/L402 → 崩溃）

**因果链**: geOpen(L620) → leoXstreamOut(L682) 使 cvId 的 dbObject handle 失效 → CXMTutRscalc_run(L692) → CXMTTransformedLabelToTopPri(L281) → dbGetTrueOverlaps(stale cvId) → `dbILGetDbObject: invalid dbObject` 崩溃。

**金标准修复**: 在 leoXstreamOut 块之后、CXMTutRscalc_run 调用之前，**重新 geOpen** 刷新 cellview，使 geGetWindowCellView() 返回 fresh cvId。

## A-档 case 设计（L1-boundary）

- **task_id**: `EDA-Eval-DesignFlow-RscalcStaleDbobjFix-001`
- **domain**: pg_layout
- **候选交付**: `patch_stale_dbobj.py`（Python 修补器）在 `outputs/submit.zip`
  - CLI: `python3 patch_stale_dbobj.py <input.il> <output.il>`
  - 读入 buggy `.il` → 定位 `leoXstreamOut(...)` 调用 + 后续 `CXMTutRscalc_run(...)` **调用点**（非 procedure 定义）
  - 在两者之间插入 `geOpen(?lib libName ?cell cellName ?view viewName ?mode "r")` 重开 cellview（带 `[patch_stale_dbobj]` 标记注释）
  - 必须通用：用 `libName`/`cellName`/`viewName` 变量，不硬编码 A 的字面量
- **check.py**: 静态审计 + subprocess 真跑候选 on A(可见) + B(隐藏, 不同 cell/lib/layer/行号)
  - 15 条独立断言 a–o（见 check.py）
- **A 资产（SUT 可见）**: `run_rscalc_nogui.il`(原 buggy, 710 行 verbatim) + `prompt_flow.md`(flow 文档) + `rscalc.config` + `crash_snippet.log`(崩溃错误逐字) + `task_brief.md`(≤3 行接口)
- **隐藏 B（不进 SUT 沙盒）**: `run_rscalc_nogui_B.il`(合成 buggy, cell=TopCell/lib=synth_lib/layers=M1-M4/leoXstreamOut 与 CXMTutRscalc_run 行号不同) + `hidden_manifest.json`
- **真跑**: subprocess `python3 <candidate.py> <A.il> <out_A.il>` + `<B.il> <out_B.il>`，断言 out 文件存在 + 行序（reopen 在 leoXstreamOut 之后、CXMTutRscalc_run 之前）+ 反硬编码（out_B 不含 A 的 Array16G_B/auto_austin_case1）

## 跨 shard 去重

- r163 `RscalcChkptGen-001`（trace 9rnwg, e0014566）= check-point 生成 + RTEXT 标注脚本 `gen_rscalc_chkpts.py`，bug = 3 元组→4 元组。**不同**：本 case = stale dbObject 修补器 `patch_stale_dbobj.py`，bug = leoXstreamOut 后 cvId 失效需重开。不同 trace、不同 bug、不同交付物。
- r168 `PwrFillAgentGen-001`（vfz3r, e0014566）= powerfill agent 生成。不同。
- r185 `AutoViaPwrFillCellRemove-001`（a9ta2, e0014566）= autovia/powerfill cell 识别删除。不同。

## leakage 隔离

- SUT 沙盒只放 A 资产（buggy .il + flow doc + config + crash snippet + task_brief）；🚫 不放 check.py、reference/、hidden/、jsonl。
- check.py 在独立 temp 目录解 submit.zip 跑判分。
