# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R1821 监控轮(§22:4x predict 619/3500·real冻结459(429期间+28全empty)·网关429恢复~3.5h~05:23·TB-2.1 hermes62/89 stalled(3pass)·报告R1820仍current)
已完成:       H-B✅·Gate7/7·TB报告✅·full500✅·cline专项C1-C5+报告R1785+R1794+R1820·TB4 0passed(能力)·TB-2.1 oracle5/5✅+cline 89/89DONE(7pass=7.9%)·§15:2x判据MET✅·R1789 eval 7/7DONE✅(hermes124/131=94.7%)·R1804双报告交付✅·R1814-R1820 predict推进+报告·R1821 predict619/3500(real冻结459·429确认infra)
当前动作:     R1821:①CPU/MEM PASS(load65/224=29%·无失控>80核·top=pretrain llama-server 602%非本线) ②体积:TASK=30KB/MEMORY=19KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429 QUOTA_EXHAUSTED**「请等待3小时31分钟29秒」恢复~3.5h(~05:23) ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive但429受阻**total619/3500(+28sinceR1820·**real冻结459(+0)**=429期间全empty):cline74(62real·12empty·83.8%)·codex66(14real·52empty·21.2%)·opencode134(127real·7empty·94.8%)·cc85(38real·47empty·44.7%)·pi52(37real·15empty·71.2%)·hermes157(138real·19empty·87.9%)·dsh51(43real·8empty·84.3%) ⑦**TB-2.1**:cline89/7pass DONE✅·codex18/89(Killed·429stalled)·**hermes62/89 stalled**(last result 01:01·3pass·429blocked)·4路queued·launcher PID2141834 ALIVE ⑧报告R1820仍current(real未变·无需regen) ⑨research日报11-07已读(harness建议:Scientist World 2611.08478·TB4 verifier基线对照思路·参考非指令) ⑩cline专项C1-C5✅(C1复算命令见下) ⑪归因红线:429=infra(real+0=铁证)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑫未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0
下一步:       ①等网关429恢复(~3.5h~05:23)后predict 7路加速推进至500(real patch将恢复) ②TB-2.1 hermes继续至89/89→launcher自动启动opencode/cc/dsh/pi ③codex TB-2.1需重跑(429恢复后) ④SWE-bench predict满500后重跑eval出最终矩阵 ⑤报告最终版增量更新
阻塞:         网关429 QUOTA_EXHAUSTED(恢复~3.5h~05:23)·predict real冻结·TB-2.1 hermes stalled(429)
ERROR_COUNT:  0
  📦 体积：TASK=30KB(30306B) / MEMORY=19KB（均≤32KB✅·无需归档）
  🔍 cline专项小结: SWE-bench predict:cline74/500(62real·12empty·83.8%real rate·12empty=全429 infra)·eval resolved:cline35/46(76.1%)·TB-2.1 89tasks:7pass(7.9%)·失败top1=网关429(infra)·C3=resume fix生效(real冻结459·429期间+28全empty=0新增real=infra铁证)·opencode134done127real(94.8%=最高real rate)·复算:cd predictions_glm53&&python3 -c"import json,glob;[print(h,len(glob.glob(f'{h}__*.json')),sum(1 for f in glob.glob(f'{h}__*.json') if(json.load(open(f))[0].get('model_patch','')or'').strip())for h in['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']]"
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [01:53] R1821 监控轮(网关429持续恢复~3.5h·predict619/3500·real冻结459(+28全empty)·TB-2.1 hermes62/89 stalled·报告R1820仍current):①CPU/MEM PASS(load65/224=29%·无失控>80核·top=pretrain llama-server 602%·7路predict均<3%cpu) ②体积:TASK=30KB(30306B)/MEMORY=19KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429 QUOTA_EXHAUSTED**「请等待3小时31分钟29秒」恢复~3.5h(~05:23)·直连curl HTTP429确认 ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive但429受阻**total619/3500(+28sinceR1820·**real冻结459(+0)**=429期间新增28全empty=infra铁证):cline74(62real·12empty·83.8%)·codex66(14real·52empty·21.2%)·opencode134(127real·7empty·94.8%)·cc85(38real·47empty·44.7%)·pi52(37real·15empty·71.2%)·hermes157(138real·19empty·87.9%)·dsh51(43real·8empty·84.3%) ⑦**TB-2.1**:cline89/7pass DONE✅·codex18/89(Killed·429)·**hermes62/89 stalled**(last result 01:01·3pass·429blocked)·4路queued·launcher PID2141834 ALIVE ⑧报告R1820仍current(real未变·无需regen) ⑨research日报11-07已读(harness建议:Scientist World 2611.08478·参考非指令) ⑩cline专项C1-C5✅(C1复算命令已写入快照) ⑪归因红线:429=infra(real+0=铁证)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑫未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> [01:38] R1820 监控+三报告更新轮(网关429持续恢复~3.8h·predict591/3500·TB-2.1 hermes62/89·三报告R1820):①CPU/MEM PASS(load60/224=27%·无失控>80核·top=pretrain非本线·7路predict均<6%cpu) ②体积:TASK=30KB/MEMORY=19KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429 QUOTA_EXHAUSTED**「额度已用完请等待3小时47分钟40秒」恢复~3.8h(~05:26) ⑤**SWE-bench eval 7/7 DONE✅**不变:cline35/46(76.1%)·hermes124/131(94.7%)等 ⑥**predict 7路alive但429受阻**(cline71(62real·87.3%)·codex58(14real·24.1%)·opencode132(127real·96.2%)·cc77(38real·49.4%)·pi50(37real·74.0%)·hermes154(138real·89.6%)·dsh49(43real·87.8%)·total591/3500·+16sinceR1819) ⑦**TB-2.1**:cline89/7pass DONE✅(passed:bn-fit-modify,break-filter-js-from-html,build-pov-ray,prove-plus-comm,pypi-server,query-optimize,regex-chess)·codex18/89启动(0verifier=429stalled)·**hermes62/89 RUNNING**(36verified·3pass:modernize-scientific-stack,multi-source-data-merger,openssl-selfsigned-cert·harbor alive·docker portfolio-optimization)·4路queued·launcher PID2141834 ALIVE ⑧**三报告更新R1820**:gen_r1820→swebench(8004B)+tb21(6211B)+cline_special_r1820(4256B) ⑨research日报11-07已读  ⑩cline专项C1-C5✅(R1820报告新增) ⑪归因红线:429=infra(持续)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑫未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> [01:30] R1819 监控+报告更新轮(网关429再次耗尽·predict575/3500·TB-2.1 hermes64/89·双报告更新R1819):①CPU/MEM PASS ②体积:TASK=30KB/MEMORY=17KB✅ ③硬盘OK ④网关429恢复~4.5h ⑤eval 7/7 DONE ⑥predict575/3500 ⑦TB-2.1 cline89/7pass DONE·hermes64/89 RUNNING ⑧报告R1819 ⑨cline专项C1-C5✅ ⑩归因红线:429=infra·TB4全0=能力 ⑪未完成指令:有⇒WAITING:0

> [01:19] R1818 监控+报告更新轮(网关200持续·predict565/3500·TB-2.1 hermes62/89(36verified·3pass)·双报告更新R1818):①CPU/MEM PASS(load62/224=28%·1.1TB avail·无失控>80核·top=pretrain非本线·harness predict均<2%cpu) ②体积:TASK=30KB/MEMORY=16KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关HTTP200✅** ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive**(cline71(62real·87.3%)·codex48(14real·29.2%)·opencode130(125real·96.2%)·cc69(38real·55.1%)·pi49(37real·75.5%)·hermes150(137real·91.3%)·dsh48(43real·89.6%)·total565/3500·+16sinceR1817) ⑦**TB-2.1**:cline89/7pass DONE✅·codex0 KILL(429)·**hermes62/89 RUNNING**(62dirs·36verified·3pass·docker portfolio-optimization)·4路queued·launcher PID2141834 ALIVE ⑧**报告更新R1818**:gen_r1818→swebench(8733B)+tb21(7244B) ⑨research日报11-07已读(harness建议=Scientist World 2611.08478·TB4已defer) ⑩cline专项C1-C5✅ ⑪归因红线:429=infra(已恢复)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑫未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> [01:07] R1817 监控+报告更新轮(网关200持续·predict549/3500·TB-2.1 hermes62/89(3pass)·双报告更新R1817):①CPU/MEM PASS(load65/224=29%·1129GB avail·无失控>80核·top=pretrain非本线·harness predict均<2%cpu) ②体积:TASK=30KB/MEMORY=15KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关HTTP200✅** ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive**(cline69(60real·86.4%)·codex42(11real·26.2%)·opencode126(121real·95.9%)·cc69(38real·55.9%)·pi45(35real·77.8%)·hermes150(137real·91.3%)·dsh48(43real·89.6%)·total549/3500·+7sinceR1816) ⑦**TB-2.1**:cline89/7pass DONE✅·codex18/0pass KILL(429)·**hermes62/89 RUNNING**(3pass=+openssl-selfsigned-cert新增·PID1610512 alive·etimes~94min·26/62 tasks vr=None=python3缺失)·launcher PID2141834 ALIVE ⑧**报告更新R1817**:gen_r1817→report_harness_tb21_7way_zh.html(9843B)+report_harness_glm53_7way_swebench_tb_zh.html(9566B) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(已恢复)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑪未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> [00:55] R1816 监控+报告更新轮(网关200持续·predict542/3500·TB-2.1 hermes33/89(2pass)·双报告更新R1816):①CPU/MEM PASS(load60/224=27%·1130GB avail·无失控>80核·top=pretrain llama-server非本线·harness predict均<2%cpu) ②体积:TASK=30KB/MEMORY=14KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关HTTP200✅**(curl /v1/models=200) ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive**(cline66(57real·86.4%)·codex42(11real·26.2%)·opencode123(118real·95.9%)·cc68(38real·55.9%)·pi45(35real·77.8%)·hermes150(137real·91.3%)·dsh48(43real·89.6%)·total542/3500·+5sinceR1815) ⑦**TB-2.1**:cline88/7pass DONE✅·codex18/0pass KILL(429)·**hermes33/89 RUNNING**(2pass=modernize-scientific-stack+multi-source-data-merger·PID1610512 alive·etimes~87min)·launcher PID2141834 ALIVE(sequential for-loop→hermes完后自动opencode/cc/dsh/pi) ⑧**报告更新R1816**:gen_r1816→report_harness_glm53_7way_swebench_tb_zh.html(8343B)+report_harness_tb21_7way_zh.html(8307B) ⑨cline专项C1-C5✅ ⑩research日报11-07已读(harness建议=Scientist World 2611.08478 baseline对照·TB4已defer不影响排期) ⑪归因红线:429=infra(已恢复)·TB4全0=能力·TB-2.1 cline7pass=能力·hermes2pass=能力(待全量) ⑫未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> [00:40] R1815 监控+报告更新轮(网关200持续·predict 537/3500加速·TB-2.1 hermes49/89 RUNNING·双报告更新R1815):①CPU/MEM PASS(load70/224=31%·1133GB avail·无失控>80核·top harness=cline24%=0.24核·pretrain/llama-server非本线) ②体积:TASK=30KB/MEMORY=13KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关HTTP200✅**(gateway_probe=GATEWAY_OK) ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive+加速**(cline65(56real·86.2%)·codex42(11real·26.2%)·opencode123(118real·95.9%)·cc68(38real·55.9%)·pi45(35real·77.8%)·hermes146(134real·91.8%)·dsh48(43real·89.6%)·total537/3500·+7sinceR1814) ⑦**TB-2.1**:cline90/7pass DONE✅(passed=bn-fit-modify·break-filter-js·build-pov-ray·prove-plus-comm·pypi-server·query-optimize·regex-chess)·codex18/0pass KILL(429)·**hermes49/89 RUNNING**(30reward.txt·0pass·PID1610512·etimes~74min)·4路queued ⑧**报告更新R1815**:gen_r1815→report_harness_glm53_7way_swebench_tb_zh.html(8330B)+report_harness_tb21_7way_zh.html(8305B) ⑨cline专项C1-C5✅(报告R1794) ⑩归因红线:429=infra(已恢复)·TB4全0=能力·hermes94.7%=能力·deepseek82.5%=能力·TB-2.1 cline7pass=能力·hermes0pass=待定 ⑪未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> [00:35] R1814 监控+报告更新轮(网关恢复200·predict加速·TB-2.1 hermes49/89·双报告更新R1814):①CPU/MEM PASS ②体积:TASK=30KB/MEMORY=12KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关已恢复HTTP200✅** ⑤**SWE-bench eval 7/7 DONE✅** ⑥**predict 7路alive+加速**(total530/3500) ⑦**TB-2.1**:cline90/7pass DONE✅·codex18 KILL·hermes49/89 RUNNING·4路queued ⑧**报告更新R1814** ⑨cline专项C1-C5✅ ⑩归因红线 ⑪未完成指令:有⇒WAITING:0

> [23:58] R1811 监控+报告更新轮(deepseek eval RUNNING·TB-2.1 cline89/89 DONE(7pass)·hermes22/89 RUNNING(0pass·9errored)·网关429 ETA~29min·双报告更新R1811):①CPU/MEM PASS(load55/224=25%·1133GB avail·无失控>80核·top=llama-server 652%=6.5核+pretrain python 144%·均非失控) ②体积:TASK=30KB(30306B)/MEMORY≈32KB·均≤32KB·无需归档 ③硬盘:/data 5.8T(18%)·/ 351G(4%) ④**网关429持续**:gateway_probe.sh→"Wait: 29分钟22秒"·/v1/models=200 ⑤**SWE-bench eval(R1789)**:6/7 done不变·**deepseek RUNNING**(40inst·PID1799584·eval容器运行中·etimes~27min) ⑥**predict**7路alive(429阻塞新任务) ⑦**TB-2.1**:**cline 89/89 DONE**(result.json:n_completed=89·n_errored=7·mean=0.0787·7passed=bn-fit-modify·break-filter-js·build-pov-ray·prove-plus-comm·pypi-server·query-optimize·regex-chess)·codex 17/89 KILL(429·17errored·0pass)·**hermes 22/89 RUNNING**(n_completed=22·n_errored=9·n_running=1·n_pending=66·0pass·9errored=AgentTimeout6+RuntimeError1+python3缺失2)·4路queued ⑧**报告更新R1811**:report_harness_tb21_7way_zh.html(cline89/89修正+hermes22/89+codex17/89)+report_harness_glm53_7way_swebench_tb_zh.html(同上) ⑨cline专项C1-C5✅(报告R1794) ⑩归因红线:429=infra·hermes python3缺失=infra·TB4全0=能力·hermes 94.7%=能力·TB-2.1 cline 7pass=能力 ⑪未完成指令:有(§22:4x deepseek eval running+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> [00:22] R1813 监控+报告更新轮(predict 7路alive推进中·TB-2.1 hermes44/89RUNNING·网关429滚动限流·双报告更新R1813):①CPU/MEM PASS(load49/224=22%·1130GB avail·无失控>80核·harness线进程均低CPU) ②体积:TASK=30KB/MEMORY=11KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 351G(4%) ④**网关429=滚动限流**(非硬阻断·~5min/周期·00:22直连测得HTTP429「请等待5分钟15秒后重试」) ⑤**SWE-bench eval(R1789) 7/7 DONE✅** ⑥**predict 7路alive+推进中**(glm53 progress:cline144/500·codex270/500·opencode160/500·cc276/500·pi107/500·hermes238/500·dsh115/500) ⑦**TB-2.1**:cline 88rewarded/7pass DONE✅·codex 19/89 KILL(429)·**hermes 44/89 RUNNING**(25rewarded·0pass·19errored)·4路queued ⑧**报告更新R1813** ⑨cline专项C1-C5✅ ⑩归因红线:429=infra·TB4全0=能力·hermes94.7%=能力 ⑪未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> [00:10] R1812 监控+报告更新轮(deepseek eval DONE✅33/40=82.5%·SWE-bench eval 7/7全完成·TB-2.1 hermes32/89 RUNNING·网关429 ETA~19min·双报告更新R1812):①CPU/MEM PASS(load50/224=22%·1135GB avail·无失控>80核) ②体积:TASK=30KB(30306B)/MEMORY=34KB→归档R1810-R1788流水后≤32KB ③硬盘:/data 5.8T(18%)·/ 351G(4%) ④**网关429持续**:gateway_probe.sh→"Wait: 19分钟32秒"·/v1/models=200 ⑤**SWE-bench eval(R1789) 7/7 DONE✅**:cline35/46(76.1%)·codex6/8(75%)·opencode80/102(78.4%)·cc27/36(75%)·pi26/34(76.5%)·hermes124/131(94.7%)·**deepseek33/40(82.5%)**←NEW(00:04完成·eval_glm53_deepseek-harness.json) ⑥**predict**7路alive:cline62/codex30/opencode119/cc58/pi39/hermes138/dsh43·429阻塞 ⑦**TB-2.1**:cline89/89DONE(7pass:7.9%)·codex17/89KILL(429)·**hermes32/89 RUNNING**(0pass·12errored·20zero_reward·PID1610512 harbor)·4路queued ⑧**报告更新R1812**:report_harness_glm53_7way_swebench_tb_zh.html(deepseek33/40+7/7完成)+report_harness_tb21_7way_zh.html(hermes32/89) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra·TB4全0=能力·hermes94.7%=能力·deepseek82.5%=能力·TB-2.1 cline 7pass=能力 ⑪未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0

> 📦 R1788-R1811 流水(19:33~23:58,监控轮+deepseek eval启动→完成+TB-2.1 cline89/89+hermes推进+网关429反复+双报告多次更新)已归档 → daily-memories-harness/2026-11-07.md。**关键里程碑**:deepseek eval 33/40=82.5%完成(SWE-bench eval 7/7全done)·TB-2.1 cline 89/89 DONE 7pass=7.9%·hermes 22→32/89·网关429反复(keyB额度耗尽)·§15:2x判据MET✅。需要时再读。
> 📦 R1761-R1787 流水(13:50~19:18,监控轮+cline专项报告R1761-R1763+网关429恢复+TB-2.1 cline 3→5passed+predict全量推进)已归档 → daily-memories-harness/2026-11-07.md。结论：网关429恢复后cline复产real patch·空patch归零·TB-2.1 5/68passed=7.35%·SWE-bench predict cline/codex/opencode达500。需要时再读。
> 📦 R1750-R1755 流水(13:07~13:35,cline专项统计+C3验证+报告R1747)已归档 → daily-memories-harness/2026-11-07.md。结论：cline空patch=100%infra(429额度)·C3 resume fix生效·适配器正常时27/27=100%real。需要时再读。
> 📦 R1743-R1749 流水(12:15~13:12,cline专项C2修正+SDK崩溃分类+429额度ETA+报告R1743-R1747)已归档 → daily-memories-harness/2026-11-07.md。结论：TB4全0=能力(verifier已运行·reward=0非None)·cline空patch=100%infra(429额度65%+SDK崩溃25%+连接6%)·适配器正常时cline 27/27=100%real·resume fix生效(R1744)·报告R1743-R1747交付。需要时再读。
> 📦 R1739-R1740 流水(09:33~10:53,predict重启+exit-code修复+cline专项)已归档 → daily-memories-harness/2026-11-07.md。结论：killed 7旧predict后gateway恢复·cleanup 423空patch·resume fix生效·exit-code修复(cline_patched.py:201)·TB4 rerun2启动。需要时再读。
> 📦 R1738 流水(09:08,监控轮)已归档 → daily-memories-harness/2026-11-07.md。结论：gateway耗尽ETA09:20·cleanup dry-run=372空·TB4 hermes60reward全0=能力·运维预判overlay根因=错误。需要时再读。
> 📦 R1612-R1734 流水(2026-11-05~07,约50轮 incr_eval/监控/TB4启动/quiet轮)已 bulk 归档 → daily-memories-harness/2026-11-05/06/07.md。**关键里程碑**:cline rerun 356/500=71.3% · deepseek→212 · kimi全7路100% · TB4全量66×7启动 · R1685 cline低分归因(86%能力差) · R1695 proxy修复 · R1714-15 TB4 pip修复。需要时再读。

## 🗣️ 运维问答

> **Q1 (09:0x令): Terminal-Bench 一共多少题？**
> **A**: 89 题（全量）。`ls ~/terminal-bench/` = 89 个任务目录。之前 7×15 = 105 trials 是因本地只有 15 个镜像，**非任务集只有 15 题**。

> **Q2 (09:0x令): 为什么只有 15 题参与？**
> **A**: 本地只有 15 个 `alexgshaw/*:20251031` 镜像（Docker Hub pull 来的）。其余 74 个之前没拉成功——但**根因不是"MITM proxy blocks"**，而是当时 daemon.json proxies 可能还没配或 daemon 没重启。**现在 daemon.json 已配 172.19.92.25:13128，实测 docker pull 成功**。

> **Q3 (09:0x令): 能不能把剩下 74 个镜像拉下来？**
> **A**: **能！** 实测 `docker pull alexgshaw/circuit-fibsqrt:20251031` 成功（392MB）。已启动 `_pull_all_tb_images.sh`（PID 2611629）批量拉取 73 个缺失镜像。共享 base layer 已缓存，预计 ~1-2h 完成。/data 剩余 6.4TB，空间充足。

> **Q4 (09:0x令): 改成 7 并发？**
> **A**: **已完成！** R479 (16:21) 启动 7x89 并发：7 harnesses × 87 tasks = 609 trials, 7-way concurrent。每 harness 独立 jobs-dir 在 /tmp（避免 NFS stale handle），共享 gw_proxy (9090/9091)。v2 串行已 kill（部分结果已保存）。ETA ~2.5-3h。口径声明：7-way concurrent（与之前串行结果不可直接比）。

> **Q5 (09:2x令): 同事通过 92.25 代理成功拉过 Docker 镜像？**
> **A**: **确认！** daemon.json `proxies` 字段已配 `http://172.19.92.25:13128`，Docker 27.5.1 支持。实测 pull 成功。**无需额外配 systemd drop-in**（daemon.json proxies 已足够）。

> 📦 R113-R202 (2026-10-04~09, 早期 SWE-bench 横评 + SWEBENCH_COMPARE 监控 + 7-way harness 横评) 已归档 → daily-memories-harness/2026-10-04.md ~ 2026-10-09.md。需要时再读。

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（**多 agent 共用**，见 `AGENTS.md`）
- **同级任务线**（🚫 不要碰）：`MEMORY_VISION.md` / `MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md`

## 流水

> 📦 R35-R112 (2026-10-02~04, H-B 源码分析启动 + SWE-bench 可行性核查) 已归档 → daily-memories-harness/2026-10-02.md ~ 2026-10-04.md。需要时再读。最新流水见上方「本唤醒流水」。
