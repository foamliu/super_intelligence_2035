# deepread: 1791946488468_0ewj2 (jiangbaol@hfeg0pkn003) — slicer sizing optimization

## trace meta
- source: `.75` scp 10.129.2.12 `/home/jiangbaol/.cline/data/sessions/1791946488468_0ewj2/1791946488468_0ewj2.messages.json` (301KB, 82 msgs, agent=lead)
- spice 计数: hspice=26 (summary.tsv tools 列); mc=29
- mtime 2026-11-05 (在 11-05 19:28 fresh summary.tsv 内；mc<30 故前轮 mc>=30 过滤遗漏 → 本轮 mc15-29 补掘发现)
- 11-06 13:2x 本轮 claim（mc=29, domain=spice_sim）
- jiangbaol = SlicerDmMeasAdd-001 同用户（不同 session、不同任务：本条=尺寸优化，前条=加差模 measure）

## USER#0 原话（A-档逐字，唯一需求轮；纯需求，无根因/无方案）
`/proj/dscqa/V0_LP6/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/004_onlySlicer_delay_dejoa.sp
根据该.sp调节pmoswidth/pmosfinger/nmoswidth/nmosfinger/itailwidth/itailwidthfinger/inwidth/inwidthfinger使Cur_slicer_latch_avg在TT_1V_45 corner下最大不超过380uA，使slicer2nd_dly_r0/slicer2nd_dly_r1最小，工作过程文件可放在/proj/dscqa/V0_LP6/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/SA_opt`

（USER#1-3 = 同文重复；USER#4 = job id "11_49023_..."；USER#5 = "strongarm比较器offset如何仿真" 偏题咨询，非主任务）

需求拆解（A-档，纯目标）：
1. 输入 = 004_onlySlicer_delay_dejoa.sp（strongarm slicer delay testbench，DEJOA 平台）
2. 调节 8 个参数：pmoswidth/pmosfinger, nmoswidth/nmosfinger, itailwidth/itailwidthfinger, inwidth/inwidthfinger
3. 约束：Cur_slicer_latch_avg @ TT_1V_45 corner ≤ 380µA（电流上限）
4. 目标：slicer2nd_dly_r0 / slicer2nd_dly_r1 最小化（延迟最小）
5. 工作目录：.../strongarm/SA_opt

## assistant 工具链（14 run_approved + 13 editor + 5 list_allowed_files + 5 read_files + 3 get_agent_policy_status + 1 search_codebase）
1. read_files 读源 .sp（004_onlySlicer_delay_dejoa.sp）+ list_allowed_files 探 /proj 目录
2. editor 写 sa_check.sh / fs_probe.sh / sa_sweep.sh（宽度优化 sweep driver，bsub finesim）/ sa_status.sh / sa_finalize.sh
3. run_approved 提交 finesim sweep（run 001/002）→ **FineSim license 阻塞**：lic_probe.sh / lic2.sh / lic3.sh 反复 lmstat 查 59001@hl01 FSPRO/CKTSIMM feature
4. sa_tail.sh grep run_001/002.log 的 ERROR/FATAL/license 行 → 仿真未成功完成
5. trace 末尾(msg#75) sa_finalize.sh 把 sa_sweep.sh 拷到 SA_opt/scripts/ + 写 README campaign/blocker 记录 → **未达用户明确接受态，无优化后 .sp 金标准产物**

## 金标准状况
- trace 末尾 assistant 仍卡在 FineSim license，**无用户接受的优化结果**（无最终 sizes + 无验证通过 .sp）
- ⇒ case 合成需 **合成金标准**（参考 SramIreadGen-001 模式）：便携 strongarm slicer testbench + sizing sweep 脚本，用 **hspice**（非 finesim，.75 上可用）跑宽度/指扫参，解析 .lis 的 Cur_slicer_latch_avg + slicer2nd_dly_r0/r1，选满足 ≤电流上限 且 delay 最小的 sizes
- 源 .sp（004_onlySlicer_delay_dejoa.sp）内容：需从 trace read_files tool_result 提取（strongarm slicer top + .measure tran Cur_slicer_latch_avg / slicer2nd_dly_r0 / slicer2nd_dly_r1 + TT_1V_45 .inc corner）

## case 设计（下轮合成，track=A-faithful, spice_sim L2/L3）
- case_id: `EDA-Eval-DesignFlow-SlicerSizeOpt-001`
- 交付: 通用 `slicer_size_opt.py <src_sp> <params.json> <out_dir>` — 读源 slicer testbench + 可调参数范围(pmos/nmos/itail/in width+finger sweep grids)→生成 sweep deck（.param 化 8 尺寸）→跑 hspice→解析每点 Cur_slicer_latch_avg + slicer2nd_dly_r0/r1→筛 ≤电流上限 的点中 delay 最小→写 opt_result.json{best_sizes, cur_avg, dly_r0, dly_r1, all_sweep_results}
- prompt = USER#0 原话逐字（A-档）
- task_brief.md ≤3 行（只写交付接口 outputs/submit.zip）
- assets A: 004_onlySlicer_delay_dejoa.sp 源（从 trace 提取，strongarm slicer stub + .measure + TT_1V_45 corner .inc）
- hidden B: 不同 slicer 拓扑参数/不同电流上限（如 ≤450µA）/不同 corner（如 SS_0.9V_125）/不同 sweep grid（防硬编码 A 的 380µA/TT_1V_45/具体 sizes）
- reference: slicer_size_opt_ref.py + check.py **k≥10 断言**:
  a zip 内文件齐全  b 候选 py_compile  c opt_result.json 结构(keys: best_sizes/cur_avg/dly_r0/dly_r1/all_sweep_results)
  d best_sizes 8 参数都在  e cur_avg ≤ 电流上限(B 的)  f dly_r0/dly_r1 为数值且 >0
  g all_sweep_results 至少 N 点(扫参覆盖)  h 至少 1 点 cur_avg 超限(证明非全过/真扫)
  i L2 hspice 真跑 B sweep deck job concluded 无 syntax error  j best 是 ≤上限 中 delay 最小(argmin 验证)
  k 跨输入护栏：B 跑脚本 → best_sizes 随 B params 变（证明无硬编码 A sizes）  l 电流上限用 B 的(非硬编 380µA)
  + 4-5 negative stubs + negative_selftest 全 FAIL + §4.9 三假提交全 FAIL
- 金标准 = 合成参考（trace 无产物）：hspice 跑 sweep 选最优
- 判分只跑 hidden B；判分器不进 SUT workdir
- 难度：L2/L3（真跑 hspice sweep + 多点解析 + 选优），目标 A-档通过率 ≤10%

## 备注
- trace 末尾未达用户接受态（FineSim license 阻塞），但任务需求 clean（纯目标，非诊断）⇒ A-档合格
- finesim 在 .75 不可用 → check.py 用 hspice（.75 上 /apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin）
- DEBT: 本轮(13:2x)因执行 11-05 运维令重扫(42 spice-hosts post-12:30=0 NEW / post-06:00=0 NEW)+794 fresh spice 候选 scout(29 spice-dominant 全前轮已知 reject + 12 lower-ratio 全诊断/咨询 + 13 mc15-29 补掘→1 clean=本条 0ewj2) 用尽 40min 预算，case 合成未完成；**下一轮第一件事即合成此 case 并交付**（🚫 不许连续两轮只深读）
- 本条 trace 小(82msgs/301KB)，下轮合成不需再深读
