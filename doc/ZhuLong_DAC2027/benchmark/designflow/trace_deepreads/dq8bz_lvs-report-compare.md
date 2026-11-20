# Deepread: dq8bz (adaml @ 10.129.2.11, mc621, physical_verify LVS)

**session**: `1793600748187_dq8bz` (1.7MB messages.json, 402 msgs, 209 user / 193 assistant)
**trace_source**: user=adaml, host=10.129.2.11, session_file=1793600748187_dq8bz.messages.json, match_count=621
**keywords**: lvs:3570;netlist:2120;virtuoso:1004;calibre:921;.cdl:389;schematic:320;.gds:256

## Session overview (multi-phase LVS flow-driving)
- 续接笔记式 session（msg[0] = 3632-char context summary）。大目标：对 blcnand3GFx1（Virtuoso OA cell）跑 Calibre LVS 出 report；CDL 经 virtuoso-cli 桥接导出。
- 整 session 是 LVS flow-driving（CDL 导出卡点 → si.env → ADE L → nogoi Virtuoso 方案），多个子任务。
- **本 case 选取的子任务 = msg[159] LVS report 对比分析**（analysis-Q&A，11-15 令§二 revival）。

## 选取子任务：msg[159]「对照两份 LVS report 找差异」
**用户原话（msg[159]）**：
> /proj/m2701/V0_DDR4/ver/lvs/m2701_stdcells/blcnand3GFx1
> 这是calibre nmLVS 的工作目录，report显示 blcnand3GFx1的lvs是pass的，有virtual Connect的warning。你对照看看，上面的lvs跟这个lvs哪里不同。

**前置（msg[158]）**：助手刚汇报自己跑的 LVS = INCORRECT（Y 输出 OPEN，10 端口，net7/8 泄漏）。
**用户意图**：把"我跑的 INCORRECT LVS" vs "官方 PASS（带 virtual connect warning）LVS"做对照，找出差异根因。

## Assistant 工具链（msg[160]-[204]）
1. `list_allowed_files` 官方 run 目录 `/proj/m2701/V0_DDR4/ver/lvs/m2701_stdcells/blcnand3GFx1`
2. `read_files` 官方 `blcnand3GFx1.lvs.report` + `blcnand3GFx1.sp` + `netlist`
3. 对比两侧提取网表 → 顶层端口 8 vs 10；三条 NMOS 下拉串链顶端 Y vs net7/net8
4. `editor` + `run_approved_command` md5 对比两个 GDS（同 22528B，md5 不同：26ba9f 官方 vs 7008dc 我的）
5. 用官方 GDS + 我的 CCI runset 重跑 → 仍 10 端口 → **同 GDS 在不同 runset 下提取不同**
6. 对比两 runset：官方 `_calibreLVS.rule_`（1386B，`source /apps/imctf/cad/runset/m2701/v0_ddr4/current/calibreLVS.rule`，CONNECT t4m3）vs 我的 `lvs_runset.cal`（CCI `cci_lvs_for_Inno`，CONNECT t8m3，PRECISION 10000，删了 PRECISION 20000）
7. 坐标尺度 20×：官方 $X=2400 vs 我 $X=120
8. 附加发现：`run_lvs.py` 命令行带 `-spice <sv_extract.sp>` 锁死 layout 为旧 spice 网表

## Gold deliverable（msg[204] 结论表，用户接受 → msg[205] 转去更新 skill）
结构化对照报告，维度：
- **verdict**: INCORRECT(我) vs CORRECT(官方)
- **顶层端口**: 10 vs 8（多 net7/8）
- **三条 NMOS 下拉串链顶端**: chain1→Y / chain2→net7 / chain3→net8（我，Y open）vs 全→Y（官方）
- **GDS identity**: 同 22528B，md5 不同
- **runset source**: cci_lvs_for_Inno vs /apps/imctf/cad/runset/m2701/v0_ddr4/current/calibreLVS.rule
- **CONNECT 顶层金属**: t8m3 vs t4m3
- **PRECISION**: 10000(删了20000) vs 20000
- **坐标尺度**: $X=120 vs $X=2400（20×）
- **virtual connect warning**: 官方有，我无
- **-spice flag**: 我带（锁死旧 spice 网表），官方无
- **root_cause**: **runset**（同 GDS 在不同 runset 下提取裂/不裂 Y）— 非 GDS 非 CDL

## 旧台账判定（2026-11-06 parked）vs 11-15 令重判
- 旧 note: "no accepted gold product; CDL-export debugging session ended unresolved"
- **11-15 令§二 revival**：旧规则判 analysis-only = weak；新标准 analysis-Q&A 合法。本子任务（msg[159]-[204]）有**明确的用户接受 gold**（msg[204] 结论表 → msg[205] 用户转下一步「更新 skill」=接受对照结论）。
- reframe = mock-behavioral `lvs-run-comparison-analysis`（physical_verify，r645-r729 family 新子型 lvs-report-compare）：真实 calibre LVS report/extract.sp/runset.rule/gds.meta/cmd.log（path-dependent on /proj & /rundata）→ 纯 stdlib：解析两 run 目录清单 → 结构化 JSON 对照报告（verdict/ports/chain_connectivity/gds_identity/runset/coord_scale/virtual_connect/command_flags + root_cause 规则推导）。
- distinct vs r723 DrcCwdRaceEvidence=drc.summary 头 CWD 竞争 / r725 PdkQaSyncWorkflow=workflow / r726 FractureTableSchema=schema / r727 DeriveLayerFracture=set-consistency / r728 RepoOverview=repo-overview / r729 DummyDeckStructDiff=struct-diff。**本例 = LVS run diff（多维度对照 + 根因推导）**，C 域首例 LVS-report-compare。

## Viable ✓ → 合成 LvsRunCompare-001
