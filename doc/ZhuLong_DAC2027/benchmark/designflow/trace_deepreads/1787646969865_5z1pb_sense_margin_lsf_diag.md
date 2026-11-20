# trace_deepread: 5z1pb — SenseMarginLsfQueueDiag howto-reframe candidate (D-netlist/waveform-adjacent, revival-from-parked)

## 元数据
- session_id: `1787646969865_5z1pb.messages.json`
- user/host: e0025730@hfeg0plg49 (10.129.8.86)
- mc: 24 (netlist:51;drc:22;verilog:2;schematic:2 — netlist dominant from pipeline scripts; drc from DRCOA product context)
- size: 36 msgs / 134KB / mtime 2026-08-25 17:13
- shard: D (netlist-adjacent flow-driving; D-pure filter: netlist positive, no hspice/finesim/spectre in scan kw — but primesim/bsub LSF runtime)
- ledger status: parked 2026-11-14 09:15 "skill-command /sense-margin-test" → r931 revival peek, buildable per 2026-11-15 reaudit (flow-driving/env-config restored)

## 任务真实意图 (U#0 verbatim)
- U#0 = msg0: `<user_input mode="act">/sense-margin-test</user_input>` — bare slash-command invoking the `sense-margin-test` skill
- skill desc (msg2 tool_result): "DRAM Sense Margin (SM) full automation pipeline for DRCOA products. Covers Finesim simulation automation (netlist switching)..."
- A-faithful 合规性: U#0 是「表达目标」轮（触发 sense-margin-test 流程）✓；未给根因/修复 ✗ → A 档合规（bare skill invocation = goal expression）
- 后续 U 轮全是 tool_result 或 "continue" 类催促，无新意图

## agent 探索路径 (assistant lead)
1. msg1: 调 skills{sense-margin-test} → 加载 skill
3. msg3-7: 探索 /home/e0025730/devops/sense-margin-test（不存在）→ 找到实际 /home/e0025730/devops/sense_margin（下划线）
5. msg7-10: 列 netlist/ job_logs/ setup/ stimulus/ bla2/ 目录 + 读 00_spf_gen.sh / 01_modify_netlist.sh / 02_test_bench_gen.sh / 03_run_jobs_bg.sh
7. msg13-16: 检查 job_logs/bla2_*.log → 发现 LSF `fqueueAry` "User cannot use the queue. Job not submitted."；读 bla2/run_jobs.sh / grab_the_result_data.pl / sed_param.sh / 04_check_and_submit_missing_files.sh
9. msg18-22: 读 bla2/toc_2.0ns/run → `bsub -q fqueueAry primesim -i D0_senw.sp -o ./cell0/D0_senw` → 确认 queue 权限是阻塞根因
11. msg22-28: 探测用户可用队列：`for q in fqueue3 fqueue3_drcoa fqueue3_temp_re fqueue2h ...; do bsub -q $q /bin/true; done` → 用户可用 fqueue3 / fqueue2h / interactive；不可用 fqueueAry / fqueueIdd / fqueue3_drcoa / fqueue3_BL / fqueue3_drgqa
13. msg28-32: bkill 清理探测 job；msg32 给最终诊断总结

## 关键产物 / GOLD
- 无文件交付（agent 全程 read/run_commands，未 write/editor 任何脚本）
- GOLD = msg32 口头诊断总结：pipeline 5 步（00 cleanup → 04 check）+ 阻塞根因（fqueueAry 未授权）+ 可用队列清单（fqueue3/fqueue2h/interactive）+ 修复建议（改 run 脚本的 -q 参数）
- 真实 pipeline 脚本签名：00_spf_gen.sh / 01_modify_netlist.sh / 02_test_bench_gen.sh / 03_run_jobs_bg.sh / 04_check_and_submit_missing_files.sh + bla2/toc_*/run（bsub -q fqueueAry primesim -i D*_senw.sp）

## 合成计划 (r932 synth, howto-reframe 范式 承 r928/r929/r930)
- **形态**: manual-grounded howto produce reframe（D 域 flow-driving/env-config 子维度首例）
- **A 资产** (synthesized-reframe): `sense_margin_lsf_queue_diag_A.md`
  - §1 Overview[DRAM Sense Margin pipeline 5 步 + LSF bsub 提交模型]
  - §2 Method 1 Manual Diagnosis[2.1 读 pipeline 脚本 00-04 + bla2/toc_*/run / 2.2 检查 job_logs/*.log 找 "User cannot use the queue" / 2.3 bqueues 列可用队列 / 2.4 bsub -q <queue> /bin/true 探测权限]
  - §3 Method 2 Script-based Diagnosis[lsf_queue_probe.sh: 遍历候选队列 bsub /bin/true + 解析 "Job is submitted" vs "cannot use"]
  - §4 LSF Queue Parameters Reference 表[queue name / 用户权限 / bsub 返回 / 推荐用途]
  - §5 Pipeline Steps Reference[00_spf_gen / 01_modify_netlist / 02_test_bench_gen / 03_run_jobs_bg / 04_check_and_submit_missing_files]
  - §6 AskEDA KB[LSF bsub/bqueues/bjobs/bkill + primesim -i sp -o out]
- **question_A.txt** (verbatim U#0): `/sense-margin-test`
- **B hidden** (平行场景，反硬编码): `ddr4_iddq_leakage_lsf_queue_diag_B.md`
  - DDR4 Iddq Leakage 测试 pipeline 平行场景，B-only pipeline 步骤[leakage_spf_gen / leakage_netlist_mod / leakage_tb_gen / leakage_run_jobs / leakage_check_submit] + B-only LSF 队列[queueAry/queueIdd/queue3_drcoa → B 用户可用 queue4/queue2h/interactive] + B-only bsub 模型[bsub -q queueAry hspice -i D*_iddq.sp]
  - 反硬编码 A-only token{sense_margin, sense-margin-test, fqueueAry, fqueueIdd, fqueue3, fqueue2h, primesim, D0_senw.sp, DRCOA, bla2, toc_, 00_spf_gen, 01_modify_netlist, 02_test_bench_gen, 03_run_jobs_bg, 04_check_and_submit_missing_files}
- **candidate_ref.py** = `lsf_queue_diag_guide.py`: markdown 手册通用解析器（同 r930 odt_method_guide.py 范式）→ JSON{question,methods[{name,kind,tools,steps,description}],prerequisites,parameters,cited_sections,primary_method,overall}
- **check.py** 12 断言 a-l（同 r930 范式：a zip+py+out_A / b py_compile / c A JSON 7 键 / d B stdout JSON 7 键 / e B methods 覆盖 manual+script / f B primary_method 非 unknown / g B cited_sections 全在 B heading 且≥4 / h B parameters 非空三键 / i B prerequisites 非空+LSF/queue/bsub 关键词 / j report.txt 含 method/step/parameter / k 反硬编码 B stdout 0 A-only token（identifier-boundary 正则）/ l 3-seed md5 一致）

## A/B 区分要点
- A: DRAM Sense Margin / primesim / fqueueAry 阻塞 / D0_senw.sp / DRCOA
- B: DDR4 Iddq Leakage / hspice / queueAry 阻塞 / D*_iddq.sp / 不同 pipeline 步骤名
- 规模/取值/结构均不同（不同协议、不同仿真器、不同队列名、不同 pipeline 步骤）✓

## 判分可行性 (§4 牙)
- 12 独立断言 ≥8 ✓
- 隐藏 B 不进 SUT ✓
- 反硬编码 identifier-boundary 正则（避免 fqueue3 误匹配 queue3、D0_senw 误匹配 D0_iddq）✓
- 3 假提交（empty/print_only/core_deleted）全 FAIL ✓
- 退化提交回归 ✓

## 选料判定
- D-pure: netlist:51 主导（pipeline 净表切换），drc:22 来自 DRCOA 产品上下文非 DRC 工具操作；无 hspice/finesim/spectre scan kw → D 池合规
- 真实 trace ✓ (e0025730/hfeg0plg49/1787646969865_5z1pb)
- 可写 check() 有牙 ✓ (markdown 解析 + 反硬编码 + 3-seed)
- 复活理由: 2026-11-15 reaudit §II 将 flow-driving/env-config 恢复为可造；r931 peek 确认 A-faithful + howto-reframe 范式匹配
- 非 off_intent/over_constrained/downgraded: 用户真实意图是跑 sense-margin-test 流程，agent 诊断 LSF 队列权限是流程阻塞的真实一步，照实造 ✓

## r931 状态
- peek 完成（36 msgs 全读）
- deepread 落盘（本文件）
- 合成 defer to r932（budget 用尽：r931 候选 triage 耗时，ocldu/5z1pb 双 peek + 8 候选 ledger cross-check）
- ledger: 5z1pb parked → revival-claimed，r932 第一件事 synth
