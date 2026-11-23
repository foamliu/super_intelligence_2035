# t0dhm — felixw Calibre DRC runset patch (deepread r1034)

**trace_source**: user=felixw, host=hfeg0pkn004 (10.129.2.13), session_file=1795395353963_t0dhm, match_count=399, real_task_summary="stream-out GDS via Aether asOut + 生成/修补 drcRunset + calibre -gui -drc -runset -batch 跑 DRC + LSF 提交 + 写 skill.md"
**domain**: physical_verify (drc:8630 calibre:1187 pdk:500 aether:167 .gds:165 pyaether:109 lvs:62)
**ledger**: claimed r1034 (physical_verify), case pending
**session**: 204 msgs / 2.45MB, cwd=/proj/drgqx/V0/agentdir/felixw/DRC_test/, agent=lead
**source reachability**: `/proj/drgqx/V0/agentdir/felixw/DRC_test/` Permission-denied to e0031982 → **runset 内容从 trace 内提取**（MSG 44 read_files 全文 + MSG 148 最终 corrected 全文均捕获）

## 真实任务（6 user_input）
1. 跑 calibre DRC，产物放 `/proj/drgqx/V0/agentdir/felixw/DRC_test`；cell=`test1` lib=`A_felixw_test`；asOut stream-out GDS（命令含 -lib/-cell/-view/-gds/-layerMap/-objMap，layerMap=leGlobalVariables.layerMap，objMap=layerMap 路径去末级换 object.map）。先抽 gds。
2-3. 提供 runset 文件 + calibre DRC rule。runset 经 `drcRunset.sh` 生成到 `DRC_test/drcRunset`；runset 内 `drcRulesFile` 给默认 rule；替换 `cmnTemplate_LP`→gds 路径、`cmnTemplate_RN`→run drc 路径；16 core 则 `cmnNumTurbo`=16 + `cmnNumTurbo minCpus`=16。用 `calibre -gui -drc -runset $drcRunset -batch` 跑。
4. **(核心可离线子任务)** 修 runset：`drcLayoutPath` 错→应 `drcLayoutPaths`；新增 `drcRunDir`=<rundir>、`drcLayoutLibrary`=<libname>、`cmnTranscriptFile`=rundrc.log(固定)、`drcResultFile`=<topCell>.drc.results、`drcSummaryFile`=<topCell>.drc.summary。重跑。
5. DRC job 丢 LSF 排查（直接 terminal `calibre -gui -drc -runset -batch` 可上 LSF）。
6. 总结成 skill.md 放 DRC_test 下。

## 可离线合成的子任务（next-round case 候选）
**drcRunset patcher**：给 template drcRunset + config{libName, topCell, rundir, numCores}，产出 patched drcRunset。check() 解析输出断言每个 option。

### template drcRunset（MSG 44 全文，env A 基础）
```
*drcRulesFile: /apps/imctf/cad/runset/drgqx/v0/current/calibreDRC.rule
*drcLayoutView: layout
*drcLayoutGetFromViewer: 1
*drcWriteSummary: 1
*drcIncrDRCSlaveHosts: {use {}} {hostName {}} {cpuCount {}} {a32a64 {}} {rsh {}} {maxMem {}} {workingDir {}} {layerDir {}} {mgcLibPath {}} {launchName {}}
*drcIncrDRCLSFSlaveTbl: {use 1} {totalCpus 1} {minCpus 1} {architecture {{}}} {minMemory {{}}} {resourceOptions {{}}} {submitOptions {{}}}
*drcIncrDRCGridSlaveTbl: {use 1} {totalCpus 1} {minCpus 1} {architecture {{}}} {minMemory {{}}} {resourceOptions {{}}} {submitOptions {{}}}
*cmnPromptSaveRunset: 0
*cmnShowOptions: 1
*cmnReadIOFromRules: 0
*cmnSaveRunsetChanges: 0
*cmnBatchModeCompatibleControlFile: 0
*cmnVConnectReport: 1
*cmnVConnectReportUnSatisfied: 1
*cmnVConnectNamesState: ALL
*cmnTranscriptFile: rundrc.log
*cmnTranscriptEchoToFile: 1
*cmnTranscriptIncludedFiles: 1
*cmnReleaseLicense: 1
*cmnRunHostType: remotelsf
*cmnNumTurbo: 2
*cmnRunMT: 1
*cmnRunHyper: 1
*cmnSaveTVFRulesToSVRF: 1
*cmnTemplate_LP: /proj/drgqx/V0/ver/drc/%L/%l/%l.gds
*cmnTemplate_RN: /proj/drgqx/V0/ver/drc/%L/%l
*cmnTemplate_TF: rundrc.log
*cmnSlaveHosts: {use {}} {hostName {}} {cpuCount {}} {a32a64 {}} {rsh {}} {maxMem {}} {workingDir {}} {layerDir {}} {mgcLibPath {}} {launchName {}}
*cmnLSFStTbl: {minCpus 2} {architecture {{}}} {minMemory {{}}} {resourceOptions {{}}} {submitOptions {{-q pv}}}
*cmnLSFMtTbl: {minCpus 2} {architecture {{}}} {minMemory {{}}} {resourceOptions {{}}} {submitOptions {{-q pv}}}
*cmnLSFSlaveTbl: {use 1} {totalCpus 1} {minCpus 1} ...
```

### oracle patched drcRunset（MSG 148，A 档 lib=A_felixw_test/cell=test1/rundir=/proj/drgqx/V0/agentdir/felixw/DRC_test/cores=16）
关键改动（相对 template）：
- 新增 `*drcLayoutPrimary: test1`（=topCell）
- 新增 `*drcLayoutPaths: <rundir>/test1.gds`（注意复数 Paths，非 drcLayoutPath）
- 新增 `*drcLayoutLibrary: A_felixw_test`（=libName）
- `*drcLayoutGetFromViewer: 1` → `0`
- 新增 `*drcRunDir: <rundir>`
- 新增 `*drcResultFile: test1.drc.results`（=<topCell>.drc.results）
- 新增 `*drcSummaryFile: test1.drc.summary`（=<topCell>.drc.summary）
- `*cmnNumTurbo: 2` → `16`（=numCores）
- `*cmnLSFStTbl minCpus 2` → `16`；`*cmnLSFMtTbl minCpus 2` → `16`
- `*cmnTemplate_LP` → `<rundir>/test1.gds`
- `*cmnTemplate_RN` → `<rundir>`
- `*cmnTranscriptFile: rundrc.log`（固定，template 已是）

## next-round 合成计划
- **case**: EDA-Eval-DesignFlow-CalibreDrcRunsetPatch-001 (physical_verify/drc_runset_patch)
- 公开 env_A: template drcRunset + task_spec(config_A: lib=A_felixw_test cell=test1 rundir=/proj/drgqx/V0/agentdir/felixw/DRC_test cores=16) + drcRunset.sh 输出片段
- 隐藏 env_B: config_B 不同 lib/cell/rundir/cores（如 lib=TB_DRC cell=inv_chain rundir=/tmp/drc_b cores=8），check() 只跑 B
- 隐藏 env_C: cross-input anti-hardcode guard（config_C 又不同）
- **判分**: check() 解析候选产出的 drcRunset，断言 ≥8 条：①drcLayoutPaths(复数) 值=<rundir_B>/<cell_B>.gds ②drcLayoutPrimary=<cell_B> ③drcLayoutLibrary=<lib_B> ④drcLayoutGetFromViewer=0 ⑤drcRunDir=<rundir_B> ⑥drcResultFile=<cell_B>.drc.results ⑦drcSummaryFile=<cell_B>.drc.summary ⑧cmnNumTurbo=<cores_B> ⑨cmnLSFStTbl minCpus=<cores_B> ⑩cmnLSFMtTbl minCpus=<cores_B> ⑪cmnTemplate_LP=<rundir_B>/<cell_B>.gds ⑫cmnTemplate_RN=<rundir_B> ⑬cross-input C guard ⑭3-seed 随机 config 一致性
- **关键反 hardcode**: drcLayoutPath(单数) 必须不存在/必须为 drcLayoutPaths(复数)；hardcode_a 把 A 答案套 C 必 FAIL（cell/lib/rundir 不同）
- 与 r1027 SearchDrcLaunchSqliteFix 区别：r1027=启动脚本+SQLite 兼容补丁(WAL/UPSERT)；本 case=Calibre drcRunset 字段补丁(Paths/Primary/Library/RunDir/Result/Summary/LSF cores)，产物/断言/trace 全不同
