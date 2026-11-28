> **轮(r1510) 治理轮 · §4.6 test_rationale 格式合规审计 · 5 case 修复 (stray-reference marker) · 2026-11-28.** task card 求 1 case; non-Lite-502 live-eval 全收口不变(review=502/502 REQ1 done/NA491/OPT0); r1503 DEBT(a) 全清; C-domain fresh 选料连续 21 轮(r1487-r1509)确认 mc≥5 band 耗尽 ⇒ 按 §止损 转不依赖新候选产出. .75 reach OK(eda_flow open_session 秒级 + run_commands hostname=hfhds201 RC=0 97ms, hspice+finesim in PATH). 最新扫描 ssh_eda_search_20261128_175430 不变(r1509 已确认). **本轮主任务 = §4.6 test_rationale 硬闸门格式合规审计(全 shard C 595 case)**: 全量扫描 `metadata.test_rationale` 是否符合 `k 条断言：①…②…` 格式 + k≥8 + k==markers. 审计结果: 586 OK / 9 non-compliant. 9 条分两类: (A) **stray-reference marker**(5 条, 本轮修) — 断言正文里用裸圆圈序号字符作交叉引用(如「被②④⑥捕获」「⑤–⑮全 FAIL」「条件⑥total」), 导致 markers 计数虚高, k_decl 正确; (B) **off-by-one 无 stray**(4 条, 下轮修) — k_decl 与 markers 差 1 但无 stray ref, 需读 check.py 数真实独立条件数才能定 k. **本轮修 5 条(纯 metadata 格式修复, 不动 check.py/test 字段/sha/judge_layers/check_live)**: ① SpfCapIncrementBackAnnotate-001 (k=12): ⑫ 末「条件⑥total」→「条件6的 total」; ② RscalcLabel-001 (k=16): ⑯ 末「被②④⑥捕获」→「被条件2/4/6捕获」; ③ MaxAreaRatioSidewallSolver-001 (k=16): ⑯ 末「在⑤–⑮全 FAIL」→「在条件5至15全 FAIL」; ④ RscalcFlowDocGen-001 (k=15): ⑤ 内「(UI#⑩用户要求…)」→「(UI#条件10用户要求…)」; ⑤ DummyQA-001 (k=18, **L2.live**): 前缀「18 条断言（11 静态 + 7 实跑 L2.live）：」全角括号夹在「断言」与「：」间致 regex `^(\d+)\s*条断言[：:]` 不匹配(k_decl 解析为 -1) → 改「18 条断言：」(静态/实跑拆分冗余, ⑫-⑱ 已带 inline 【L2.live】 tag). **自验**: ① 5 条修后全 COMPLIANT(k_decl==markers, k≥8, prefix 匹配); ② 全 shard C 复扫 591/595 OK(was 586); ③ DummyQA SKIP_RUN=1 框架接受(infra_fail=0 hook_blocks=0 workdir-leak OK, 8 A 附件部署, FAIL 仅因 SKIP_RUN 无 submit.zip); ④ §5⑤ sha 3-way sync 不受影响(test 字段未触, 21 L2.live 仍 0 drift); ⑤ L2.live 21 条复验 0 drift. **DummyQA(L2.live) 往 live_eval_changes.tsv 追加 1 行**(纯 test_rationale 格式修复, 非 check_live/judge_layers 变更, 但 L2.live case 透明登记). **残余 4 条 DEBT(下轮)**: ConvexEnclosePcellGen(k=26/m=25) / ERCBootPlan(k=26/m=25) / SkillPatternDecoordinate(k=26/m=25) / RTextChkPlan(k=16/m=17) — 均无 stray ref, 需逐条读 check.py 数独立条件数定 k 再 reconcile. cases/C=595 不变 / L2.live=21 不变 / non-Lite-502 review 不变. 📦 体积: MEMORY ~32KB / TASK ~32KB. WAITING: 0.

> **轮(r1509) 治理轮 · r1503 DEBT (a) 最后 1 条 candidate-exec 续审 · 1 case 修复 (ParaIlArrayComposer-001 unpassable) · r1503 DEBT (a) 全清 · 2026-11-28.** task card 求 1 case; non-Lite-502 live-eval 全收口不变(review=502/502 REQ1 done/NA491/OPT0) → C-domain fresh 选料连续 20 轮(r1487-r1508)确认 mc≥5 band 耗尽 ⇒ 按 §止损 转不依赖新候选产出. 本轮主任务 = **r1503 DEBT (a) 最后 1 残余 candidate-exec**: r1508 修 PinNetWiringAether, 残余 1 (ParaIlArrayComposer) r1508 标「同 real-bug 待修, 最后 1 条」. 本轮选 **ParaIlArrayComposer-001** 修复. **根因(双重复合)**: (1) check.py `A=workdir/assets/CASE/sample_a/PARA_unit_A.il` + `B=workdir/assets/CASE/hidden/PARA_unit_B.il` 建非存在子目录, run_one.sh judge-deploy 从不建 g2/assets/CASE/ 子目录(flat 拷 A 到 g2 root by basename + symlink g2/hidden→$JUDGE/hidden for B) → A/B 路径全不存在 → cond a `parse_il(A) failed: FileNotFoundError` → 16 conds a-p 全级联; (2) **更深**: A 附件在 `assets/CASE/sample_a/` 子目录, 但 harness 把 attachments strip 到 basename 后只查 `ASSETS_SRC/PARA_unit_A.il`(直接子文件) → 文件**从未部署**到 g2 root 或 cline workdir(basename-strip + assets_src/name 不存在 → skip); 且 assets 目录用**短名** ParaIlArrayComposer-001 而 run_one.sh(以 full-prefix task_id 调)+reference 目录用**full-prefix** EDA-Eval-DesignFlow-ParaIlArrayComposer-001 → assets 目录找不到; 且 case JSON `task_id` 字段也是短名(与所有兄弟 case 的 full-prefix 约定不一致) → workdir-build phase `d.get('task_id')==tid` 查不到 case. 该 case 从未跑通过 run_one.sh, 仅靠 broken negative_selftest(WORKDIR=BENCH_ROOT 匹配旧 assets/CASE/sample_a/ 布局=假通过)「验证」. v2 faithful harness 复现 rc=1 (parse_il(A) FileNotFoundError). **修复(非侵入 wiring + asset 布局 flatten, 16 conds a-p 断言逻辑一字不动)**: (a) git mv asset `sample_a/PARA_unit_A.il` → `PARA_unit_A.il` (删 sample_a/ 子目录); (b) git mv assets 目录短名→full-prefix; (c) JSON `task_id` 短名→full-prefix; (d) JSON attachment path + prompt `sample_a/` 引用 + leakage_isolation 文本 sync 到 flat full-prefix 布局; (e) check.py `A=workdir/PARA_unit_A.il` + `B=workdir/hidden/PARA_unit_B.il`. 同 r1505 IRReportPdf/r1507 IrDropHtmlReport/r1508 PinNetWiringAether 路径 wiring 模式 **PLUS** asset-layout flatten(本 case 独有, 因 sample_a/ 子目录). negative_selftest **重写** `_build_workdir` 对齐 real harness(A flat in tmp root, B in tmp/hidden/) + REF sanity PASS gate; 原版传 WORKDIR=BENCH_ROOT 匹配旧 broken assets/CASE/sample_a/ 布局=假通过. judge_layers 不变 [L0,L1] LIVE-NA(pure-Python pcell .il parse+array-compose+verify oracle, 无真 EDA). JSON test 字段 stale→sync disk check.py 3-way sha 51d5f22f39. **自验**: ① v2 faithful harness ref check.py 现 PASS 16/16(was rc=1 parse_il(A) FileNotFoundError); ② negative_selftest REF PASS + 5 negs ALL FAIL distinct first-fail {parse-gate,b,e,h,b}(§4.9 trio empty→parse-gate/print→b/core→h 3-distinct, pre-existing: empty+print 均无 valid parse → parse-gate/cond b 合理同捕, 非路径修复引入; hardcode_b→e, naive_stub→b extra); ③ SKIP_RUN=1 框架接受(attachments copied=['PARA_unit_A.il'], infra_fail=0 hook_blocks=0 workdir-leak OK, FAIL 仅因 SKIP_RUN 无 submit.zip). live_eval_changes.tsv 追加 1 行. **r1503 DEBT (a) 4 candidate-execution case 全部闭合**: GateNetlistBuildVerify(r1506) / IrDropHtmlReport(r1507) / PinNetWiringAether(r1508) / ParaIlArrayComposer(r1509). cases/C=661 不变 / L2.live=21 不变 / non-Lite-502 review 不变. 📦 体积: MEMORY ~14KB / TASK ~32KB. WAITING: 0.

> **轮(r1508) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1510，2026-11-28）。**[摘要: 治理轮 · r1503 DEBT(a) candidate-exec 续审 · 1 case 修复 (PinNetWiringAether-001 unpassable) · 2026-11-28 · PinNetWiringAether-001, 原文见 archive]

> **轮(r1507) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1509，2026-11-28）。**[摘要: 治理轮 · r1503 DEBT 续审 · 1 case 修复 · 2026-11-28 · IrDropHtmlReport-001 unpassable, 原文见 archive]

> **轮(r1506) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1509，2026-11-28）。**[摘要: 治理轮 · r1503 DEBT 续审 · 1 case 修复 · 2026-11-28 · GateNetlistBuildVerify-001 unpassable, 原文见 archive]

> **轮(r1505) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1509，2026-11-28）。**[摘要: 治理轮 · r1503 DEBT 续审 · 1 case 修复 · 2026-11-28 · r1505, 原文见 archive]

> **轮(r1504) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1507，2026-11-28）。**[摘要: 治理轮 · r1503 DEBT(b) PortTextPinPlan-001 __main__ contract bug 修复 · 1 case 修复 · 2026-11-28 · PortTextPinPlan-001, 原文见 archive]

> **轮(r1503) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1505，2026-11-28）。**[摘要: 治理轮 · r1502 DEBT 全量 ref-fails-check 审计 · 1 case 修复 (ErcRulecheckStatsScan-001 unpassable)  · ErcRulecheckStatsScan-001, 原文见 archive]

> **轮(r1502) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1505，2026-11-28）。**[摘要: 治理轮 · r1501 DEBT k-vs-check 审计续 · 1 case 修复 (DrcRunStatusAnalyze-001 unpassable) · 2026-11 · DrcRunStatusAnalyze-001, 原文见 archive]

> **轮(r1501) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1505，2026-11-28）。**[摘要: 治理轮 · r1500 DEBT k-vs-check.py 系统审计 · 1 case 修复 (DrcKgBuilder-001) · 2026-11-28.** task ca · DrcKgBuilder-001, 原文见 archive]

> **轮(r1500) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1505，2026-11-28）。**[摘要: 治理轮 · test_rationale 格式合规审计(§4.6 硬闸门) · 3 case 修复 · 2026-11-28.** task card 求 1 case; non- · CalibreOverlapArea-001, 原文见 archive]
> **轮(r1499) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1505，2026-11-28）。**[摘要: 治理轮 · non-Lite LIVE-REQ-done OaLayoutM1RectEdit-001 L2.live 漂移复验 · 0 改动 cases · 2026-11-28 · OaLayoutM1RectEdit-001, 原文见 archive]

> **轮(r1498) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1505，2026-11-28）。**[摘要: 治理轮 · L2.live §5⑤ sha 3-way sync 审计 · 1 drift 修复 (PyLibApiDocGen-001) · 2026-11-28.** task · PyLibApiDocGen-001, 原文见 archive]

> **轮(r1497) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1505，2026-11-28）。**[摘要: 治理轮 · non-Lite-502 LIVE-NA 复审(§2.1) · 0 假阴性 · 0 改动 cases · 2026-11-28.** task card 求 1 cas, 原文见 archive]

> **轮(r1496) 治理轮 · MEMORY 归档 r1488-r1494 → ARCHIVE · 0 改动 cases · 2026-11-28.** task card 求 1 case; non-Lite-502 live-eval 全收口不变(review=502/502, REQ1 done/NA491/OPT0). 选料: r1487-r1495 连续 9 轮确认 mc≥5-300 band C-domain physical_verify/layout fresh 耗尽(最新 r1495 扫 ssh_eda_search_20261128_143143 仅 8 fresh slugs, 7 偏 B/D, 唯一 C-domain x3t64 env-debugging dominant 已 park) ⇒ 本轮不强行造 weak case, 转治理. **本轮主任务 = MEMORY 体积治理**: MEMORY 超 32KB 红线达 ~44KB(r1495 已标记预存问题) ⇒ 按 §8 收尾 step0, 将 r1488-r1494 共 7 条已闭合交付轮原文(各 3.5-4.7KB)批量搬迁至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md(归档批次 r1496, +27854 bytes), 各留 1 行指针(含 case-id 摘要). MEMORY 45977→14244 bytes(~14KB), 远低于 32KB 红线. **0 改动 cases/C, 0 改动 check.py, 0 改动 live_eval**(non-Lite-502 review 全收口不变). cases/C=661 不变 / L2.live=21 不变 / non-Lite-502 review 不变 / live_eval_changes.tsv 不变. ledger 不变(本轮无 claim/mark). 📦 体积: MEMORY 14KB(归档后) / TASK ~32KB. WAITING: 0.

> **轮(r1495) 选料/监控轮 · x3t64 peek+park · 0 改动 cases · 2026-11-28.** task card 求 1 case; non-Lite-502 live-eval 全收口不变(review=502/502, REQ1 done/NA491/OPT0) → 按 task card 选料造题. .75 reach OK(eda_flow open_session 秒级 + run_commands hostname=hfhds201 RC=0 13ms). 选料: cross-check 全 4-shard ledger(4502 norm taken slugs) vs 最新 scan ssh_eda_search_20261128_143143/summary.tsv, C-domain keyword 过滤 mc≥5 dedup by session top-120 → 仅 8 fresh slugs(1qva5/6l1c8/6z0ga/e9m7f/hyep6/mymt8/x3t64/ybu94), 其中 7 偏 B/D(waveview/netlist/hspice-dominant wellesc plg17 / e0029308 plg57 hspice-dominant / xxchen plg56 drcpv PyQt-GUI bug-fix r1487 已判非 physical_verify) — 与 r1487「mc≥5-300 band physical_verify/layout fresh 耗尽」结论一致, 本轮再次确认. 唯一 C-domain fresh = **x3t64(wenhanz@hfeg0plg91 mc663 aether:3541+pyaether:2332+drc:561 layout_aether)**; r1488 曾因 plg91 host-key-verify 失败跳过, 本轮用 StrictHostKeyChecking=no+UserKnownHostsFile=/dev/null 重试 ssh OK, scp 1.37MB/381msgs 成功. 深读: session 是 wenhanz 用 pyAether 读 invLx2 stdcell 版图做 DRC prediction, **但 200+ msgs 被困在 pyAether env 搭建**(libstdc++.so.6 版本冲突 eda_agent 旧版 / libboost_regex.so.1.70.0 缺失 / libQt5ae / libpyaeutil.so / OpenAccess libs 一连串 LD_LIBRARY_PATH 调试 + SandBox run_code 内部 'emyString' object has no attribute 'load' 反复崩), 真正 produce-task(invLx2 版图读取+M1/PG DRC prediction+stdcell-drc-predictor skill 重写)埋在后 1/3 且多轮交互非 clean 单轮可交付. **结论: env-debugging dominant, produce-task thin & buried ⇒ 不 ship**. claim+park x3t64(layout_aether, note=env-debugging dominant produce-task thin buried). 🚫 不为凑数造 weak case. ledger: covered 588 / parked 815→816 / touched 1404. **0 改动 cases/C, 0 改动 check.py, 0 改动 live_eval**(non-Lite-502 review 全收口不变). cases/C=661 不变 / L2.live=21 不变 / non-Lite-502 review 不变 / live_eval_changes.tsv 不变. 📦 体积: MEMORY ~44KB(超 32KB 红线, 预存问题, 下轮应归档 r1489-r1492 至 ARCHIVE). WAITING: 0.

> **轮(r1494) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1496，2026-11-28）。**[摘要: 交付轮 · PathWidthFromRuler-001 [L0,L1] 落盘 + 自验全绿, 原文见 archive]

> **轮(r1493) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1496，2026-11-28）。**[摘要: 交付轮 · NicapBlockCreate-001 [L0,L1] 落盘 + 自验全绿, 原文见 archive]

> **轮(r1492) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1496，2026-11-28）。**[摘要: 交付轮 · DrcKgBuilder-001 [L0,L1] 落盘 + 自验全绿, 原文见 archive]

> **轮(r1491) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1496，2026-11-28）。**[摘要: 交付轮 · MarkSNShieldReport-001 [L0,L1] 落盘 + 自验全绿, 原文见 archive]

> **轮(r1490) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1496，2026-11-28）。**[摘要: 交付轮 · RegDecisionMatrix-001 [L0,L1] 落盘 + 自验全绿, 原文见 archive]

> **轮(r1489) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1496，2026-11-28）。**[摘要: 交付轮 · LvlBatchRunner-001 [L0,L1] 落盘 + 自验全绿, 原文见 archive]

> **轮(r1488) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1496，2026-11-28）。**[摘要: 交付轮 · LvsShortCheckRunsetPatch-001 [L0,L1] 落盘 + 自验全绿, 原文见 archive]

> **轮(r1487) 选料/监控轮 · mm1rj peek+park · 0 改动 cases · 2026-11-28.** task card 求 1 case; non-Lite-502 live-eval 已全收口(review=502/502, REQ1 done/NA491/OPT0, 本令让位)→ 按 task card 选料造题. 选料: cross-check 全 4 shard ledger(规范化 slug 去后缀, 8956 norm slugs) 找 fresh C-domain. .75 reach OK(eda_flow open_session 秒级 + run_commands hostname=hfhds201 RC=0 32ms, close_session cleaned). summary.tsv(ssh_eda_search_20261128_093245) C-domain keyword 过滤: **mc≥75 band top-40 dedup by session → cross-check 4-shard ledger 规范化 → 仅 1 "fresh"(6z0ga) 但 r1486 已判 xxchen plg56 drcpv PyQt-GUI bug-fix 族非 physical_verify design_flow**(7kizj 同族已 parked); 其余 top-40 全 case/parked(508od/sjzm0/1hkwu/56vki/ukkn7/sstk3/x4b0p/xxz7c/ijh76/m6imc/aneeo/qikhb/4iv57/fbz0w/20fct/vjlni/sroz5/m2vah/7kizj/aftvk/wf513/tef8l/58vqx/j7cyb/7rzyf/xza9c/hht3e/y20x8/as67p/6z0ga/cgqd1/6l1c8/yr9k2/4kf4h/mt7ua/n91pk/1mvxt/itvhk/9fg5t). **mc30-300 band dedup by session_file → 21 unique, cross-check → 3 fresh**(jr9iw/wellesc drc:1772+verilog:1136 netlist- dominant 偏 B/D; mm1rj/e0020134 pyaether:647+aether:445 layout_aether; 1wuoc/jasonxu hspice:1035 偏 B/D). 选 **mm1rj(e0020134@hfeg0plg86 mc299 pyaether:647+aether:445+dbget:213+dbshape:41, FRESH, vjlni 同用户新 session)** peek: plg86 fetchable(PATH-FIX 子目录 slug/slug.messages.json, 375KB/154msgs). peek 结论: session 是 `QA_pattern/aether_bridge` pyAether API 探索(列 16419 public attrs + bridge status RUNNING), **Q&A/exploration 非 design_flow produce-task**(无 deliverable), 不适合造 produce-task case; 154msgs. **claim+park mm1rj**(layout_aether, note=Q&A exploration 非 produce-task). ledger: covered 581 / parked 811 / touched 1392. **0 改动 cases/C, 0 改动 check.py**(🚫 不为凑数造 weak case). cases/C=654 不变 / L2.live=21 不变 / non-Lite-502 review 全收口不变 / live_eval_changes.tsv 不变. 📦 体积: MEMORY ~33KB. WAITING: 0.

> **轮(r1486) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]

> **轮(r1485) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]

> **轮(r1484) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]

> **轮(r1483) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]

> **轮(r1482) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]

> **轮(r1481) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]

LIVE-NL: C review=502/502 · REQ=1(done 1) · OPT=0 · NA=491 · L2.live 21 · cases/C 661. r1509 治理轮 · r1503 DEBT(a) 最后 1 条 candidate-exec 续审 · 1 case 修复 ParaIlArrayComposer-001 (unpassable: 双重复合根因 — ① check.py A/B 硬编码 workdir/assets/CASE/sample_a+hidden 子目录 g2 从不建 → cond a parse_il(A) FileNotFoundError → 16 conds a-p 全级联; ② 更深: A 附件在 sample_a/ 子目录 harness basename-strip 后查 ASSETS_SRC/PARA_unit_A.il 直接子文件不存在 → 从未部署到 g2/cline workdir; 且 assets 目录用短名 + JSON task_id 短名 与 run_one.sh full-prefix 调用 + reference full-prefix 约定不一致 → 目录找不到 + case 查不到; 该 case 从未跑通 run_one.sh 仅靠 broken neg_selftest 假通过; 修复: git mv asset sample_a/→flat + assets 目录短名→full-prefix + JSON task_id→full-prefix + attachment/prompt/leakage_isolation sync + check.py A=workdir/PARA_unit_A.il + B=workdir/hidden/PARA_unit_B.il, 同 r1505/r1507/r1508 wiring 模式 PLUS asset flatten; neg_selftest 重写 _build_workdir 对齐 harness + REF sanity gate; [L0,L1] LIVE-NA judge_layers 不变, JSON test sha 3-way sync 51d5f22f39, v2 faithful harness ref PASS 16/16, neg_selftest 5-neg ALL FAIL distinct {parse-gate,b,e,h,b} §4.9 trio 3-distinct + REF PASS, SKIP_RUN=1 框架接受 · r1503 DEBT(a) 4 candidate-exec 全清: GateNetlistBuildVerify r1506 / IrDropHtmlReport r1507 / PinNetWiringAether r1508 / ParaIlArrayComposer r1509) · 2026-11-28. r1508 治理轮 · r1503 DEBT(a) candidate-exec 续审 · 1 case 修复 PinNetWiringAether-001 (unpassable: check.py assets=workdir/assets/CASE 建非存在子目录 → fixture_path/hidden_manifest/hidden_spec + _load_fixture sys.path 全解析到不存在路径 → cond a 立即 FAIL 'oa_fixture.py missing' → 14 conds a-n 全级联; 读 run_one.sh 源码确认 g2 从不建 g2/assets/CASE/ 子目录, 同 r1505 IRReportPdf/r1507 IrDropHtmlReport 模式; 改 assets=workdir + _load_fixture sys.path.insert(workdir); neg_selftest 重写 _build_workdir 对齐 harness A flat+B in hidden/ + REF sanity gate, 原版传 repo assets dir 匹配旧 broken 布局=假通过; [L0,L1] LIVE-NA judge_layers 不变, JSON test sha 3-way sync 6fce2b1674, v2 faithful harness ref PASS, neg_selftest 5-neg ALL FAIL {f,d,d,i,g} §4.9 trio 2-distinct + REF PASS, SKIP_RUN=1 框架接受 · 残余 DEBT: ParaIlArrayComposer 同 real-bug 待修, 最后 1 条) · 2026-11-28. r1507 治理轮 · r1503 DEBT(a) candidate-execution 续审 · 1 case 修复 IrDropHtmlReport-001 (unpassable: check.py 硬编码 workdir/AssetsA + workdir/B 两非标准目录 harness 从不创建 → A/B 路径全不存在 → cond i rc=1 + j/k/l 全 0; 读 run_one.sh 源码确认 3 残余 candidate-exec 均 real-bug 非 harness-FP: g2 从不建 g2/assets/CASE/ 子目录; 改 assets_a=workdir + b_dir=workdir/hidden 同 r1505 IRReportPdf 模式; neg_selftest _setup_workdir 对齐 harness; [L0,L1] LIVE-NA judge_layers 不变, JSON test sha 3-way sync 423cb2ae23, v2 faithful harness ref PASS 13/13, neg_selftest 3-neg ALL FAIL {b,f,b} 2-distinct + REF PASS, SKIP_RUN=1 框架接受 · 残余 DEBT: ParaIlArrayComposer+PinNetWiringAether 同 real-bug 待修) · 2026-11-28. r1506 治理轮 · r1503 DEBT(a) v3-harness 残余 24 rc!=0 续审 · 1 case 修复 GateNetlistBuildVerify-001 (unpassable: _run_candidate 传相对 spec_path 但 subprocess cwd=tmp → 候选 open() FileNotFoundError → cond c/m/o 必 FAIL; 改 abspath, 同 r1505 NicapPcell 模式; neg_selftest pre-existing ref-script-from-zip 修复; [L0,L1] LIVE-NA judge_layers 不变, JSON test sha 3-way sync ab4adbd05, faithful judge ref PASS, neg_selftest 4-distinct {a,e,j,n} §4.9 trio distinct · 24 rc!=0 分类: 4 stale已修 + 4 __main__ stale-path(cosmetic) + 12 harness-FP + 4 candidate-exec(1 修/3 待 v3)) · 2026-11-28. r1505 治理轮 · r1503 DEBT(c) IRReportPdf-001 + NicapPcellParamExtract-001 深查+修复 (2 unpassable check.py wiring bugs: IRReportPdf b_summary/B-image 误读 A 副本@workdir root 非 B@hidden/ → cond j/m 必 FAIL, 改 hidden/ 优先; NicapPcell _run_script 相对 layout_path + cwd=out_dir 不匹配 → cond c rc=1 级联, 改 abspath; 两 case [L0,L1] LIVE-NA judge_layers 不变, JSON test sha 3-way sync 4fd2f29657/bc7e54bab5, v2 harness ref PASS 13/13 + 18/18, neg_selftest §4.9 trio distinct · r1503 三项 DEBT 全清) · 2026-11-28. r1504 治理轮 · r1503 DEBT(b) PortTextPinPlan-001 __main__ contract bug 修复 (r1204-era reform e0643a514 改 check() PASS return 3-tuple→True 但 __main__ 仍 unpack 3-tuple → ref PASS 路径 TypeError 崩; __main__ 改 shape-agnostic, FAIL-path 3-tuple 保留给 negative_selftest label 解析; JSON test stale→sync disk 3-way sha 633c1524; judge_layers 不变 [L0,L1] LIVE-NA; ref __main__ 现 PASS[all], neg_selftest 7 negs 6 distinct 保留 · DEBT: r1503 (a)v3 harness 路径覆盖 + (c)IRReportPdf/NicapPcellParamExtract 深查) · 2026-11-28. r1503 治理轮 · r1502 DEBT 全量 ref-fails-check 审计 · 1 case 修复 ErcRulecheckStatsScan-001 (hidden B2 缺第6 edge-case 文件夹 CEDGE_SampleC 无 erc.rep, cond p unpassable→passable, check.py 不动 judge_layers 不变, neg4 牙齿恢复 · v1+v2 审计 tooling 342 cases, 24 仍 rc!=0 多为 harness 路径假阳性) · 2026-11-28. r1501 治理轮 · r1500 DEBT k-vs-check.py 系统审计 · 1 case 修复 DrcKgBuilder-001 (k 16→20 对齐 check.py c1-c16c 20 独立条件 · 全量 661 扫描仅此 1 real bug) · 2026-11-28. r1500 治理轮 · test_rationale 格式合规审计(§4.6) 3 case 修复(CalibreOverlapArea/DanglingDrcDeckGen/LvsShortCheckRunsetPatch) · 2026-11-28. r1499 治理轮 · non-Lite REQ-done OaLayoutM1RectEdit-001 L2.live 漂移复验全绿 · 2026-11-28. r1498 治理轮 · L2.live §5⑤ sha 3-way sync · 1 drift 修复 PyLibApiDocGen-001 · 2026-11-28. r1497 治理轮 · non-Lite-502 LIVE-NA 复审(§2.1) 0 假阴性 · 2026-11-28. r1496 治理轮 · MEMORY 归档 r1488-r1494→ARCHIVE · 2026-11-28.
> **轮(r1480) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]
> **轮(r1479) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]
> **轮(r1478) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1488，2026-11-28）。**[摘要见 archive]
> **轮(r1477) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1476) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1475) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1474) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1473) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1470) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1468) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1469) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1467) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1463) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1464) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1462) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1461) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1460) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1456) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1455) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1453) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1452) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1451) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1449) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1450) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1448) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1447) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1445) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1444) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1442) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1418) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1417) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1416) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1399) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1254) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1253) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1244) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1243) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1242) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1241) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1239) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1238) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1237) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1240) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1236) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1235) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1234) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1233) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1232) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1230) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1229) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1228) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1227) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1226) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1225) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1224) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1223) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1222) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1221) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1220) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1214) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1215) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1213) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
> **轮(r1212) 已归档至 ARCHIVE_OPERATOR_DESIGNFLOW_C.md（归档批次 r1484，2026-11-28）。**[摘要见 archive]
