# trace deepread: 1793261933061_z7stj — SimRunDepExtract-001

## 元数据
- session_id: `1793261933061_z7stj`
- user/host: ypzheng@hfeg0pkn003
- mc: mc273 (verilog-dominant: verilog:1556 / netlist:1028 / analog:1020 / cmos:209 / schematic:152 / floorplan:71)
- size: 260 msgs, 1.34 MB
- shard: A (digital)
- status: claimed r192 → case `EDA-Eval-DesignFlow-SimRunDepExtract-001`

## 任务真实意图
LPDDR5 FineSim coretiming 仿真 runcmd 依赖文件清点：
- 解析 coretiming_wisteria runcmd 的 active runsim 行（runner / control / netlist / filelist / simulator / options）
- 解析 coretiming.saved filelist 的 active pattern dirs / corners / counts
- 输出结构化 JSON

真实 trace 末尾用户接受 assistant 给出的完整依赖图。

## A 档合规性
- USER#186 逐字（A-rule②）：「这是仿真的runcmd文件，跑这个仿真的时候涉及到了哪些其他的文件，把它们的路径都找出来/proj/ddgoa/V0/simdir/finesim/workdir/coverage/savefile_for_DE/wisteria/coretiming_wisteria」
- 干净需求，无根因 / 无修复方向 → A-faithful 合规
- assistant 全程仅 read_files 清点依赖，run_commands 被策略禁用，未修改任何文件 → L1-static

## A 资产重建（从 trace tool_results 逐字）
- runcmd = 7 行，active line 6：
  - runner = `/rundata/ddgoa/V0/simdir/finesim/workdir/coverage/runsimFC_LP5_coverage`
  - control = `control.finesim_promd_vcap_common_0930_wisteria`
  - netlist_dir = `Netlist_Vcap_20261021PM_RasSpf_wisteria`
  - netlist_name = `netlist`
  - filelist = `./coretiming.saved`
  - simulator = `Primesim_2023`
  - options: `-i 8 -q fqueue3_ddgoa`
- coretiming.saved = 30 行，12 active + 18 disabled
  - **真实文件怪癖**：SS 角行用 `_1067_` 4 位目录 vs FF/TT `_10667_` 5 位 → 3 unique pattern_dirs（非 2）
  - 6 corners / 18 disabled (# 与 ## 皆禁用)

## 隐藏 B 合成（结构性对立于 A 每个被断言维度）
- runner = `runsimFC_LP5_basic` (vs coverage)
- control = `_1105_dvpo` (vs promd_0930_wisteria)
- netlist_dir = `Netlist_Vcap_20261101PM_DvpoSpf_dvpo` (vs RasSpf_wisteria)
- netlist_name = `spice` (vs netlist)
- filelist = `./dvpo_coretiming.saved`
- simulator = `Primesim_2024` (vs 2023)
- options: `-i 16 -q fqueue2_foobar`
- active_line = 4 (vs 6)
- 3 pattern_dirs (无怪癖) / 8 active / 4 corners / 3 disabled

## check.py 设计
- 17 conds (a-q)，k_rationale=k_check=17
- subprocess 真跑候选于隐藏 B（主判，§4.2 L2-static 真跑）
- cross-input guard 再跑可见 A（反硬编任一）
- 反伪造：候选自报 deps_report.json 须与独立重跑 A 一致
- A/B 以 base64 内嵌（A_RUNCMD_B64/A_SAVED_B64/B_RUNCMD_B64/B_SAVED_B64）→ check.py 自包含，无 `__file__`/外部路径依赖
- v1 path-based check.py e2e /tmp 失败（路径解析）→ 重写 base64 自包含版

## 自验
- ref PASS 17/17（本地 + /tmp e2e 双验）
- 5 negatives 全 FAIL（NEG_RC=0）：fake_empty / fake_print_expected / fake_core_deleted (§4.9 三假) + naive_skip_disabled / naive_hardcode_a_dirs (两朴素)
- jsonl test 字段端到端 roundtrip OK
