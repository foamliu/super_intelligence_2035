# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R1833 监控轮(§22:4x predict 821/3500·real冻结459(+0)·网关429持续ETA~05:25·TB-2.1 cline/hermes DONE·opencode harbor alive 48min 0reward(429)·codex 0done(docker down时跳过·需重跑)·cc/dsh/pi queued·dockerd已恢复·报告R1820仍current)
已完成:       H-B✅·Gate7/7·TB报告✅·full500✅·cline专项C1-C5+报告R1785+R1794+R1820·TB4 0passed(能力)·TB-2.1 oracle5/5✅+cline88reward(7pass=7.9%)DONE+hermes54reward(3pass=3.4%·35errored=429)DONE·§15:2x判据MET✅·R1789 eval 7/7DONE✅·R1804双报告交付✅·R1814-R1833 predict推进·R1833 predict821/3500(real冻结459·429确认infra)
当前动作:     R1833:①CPU/MEM PASS(load68/224=30%·无失控>80核·无proc>8000%·top=pretrain cline非本线·mem785G/2015G·avail1101G) ②体积:TASK=30KB(30306B)/MEMORY=14KB(14552B)·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429持续**curl chat/completions→「本次Token额度已用完，请等待1小时24分钟49秒后重试」ETA~05:25 ⑤**SWE-bench eval 7/7 DONE✅**不变:cline35/46(76.1%)·codex6/8·opencode80/102(78.4%)·cc27/36·pi26/34·hermes124/131(94.7%)·dsh33/40(82.5%) ⑥**predict 7路alive但429受阻**total821/3500(+13sinceR1832·**real冻结459(+0)**=infra铁证):cline96(62r·34e)·codex128(14r·114e)·opencode144(127r·17e)·cc147(38r·109e)·pi67(37r·30e)·hermes178(138r·40e)·dsh61(43r·18e) ⑦**TB-2.1**:cline88reward(7pass=7.9%)DONE·hermes54reward(3pass=3.4%·35errored=429)DONE·opencode harbor alive 48min 0reward(429·docker内npm install阶段)·codex0done(需重跑)·3路queued(cc/dsh/pi)·launcher PID2141831 alive·dockerd PID1480217已恢复·oracle5/5✅ ⑧报告R1820仍current(real未变) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑪research日报11-07已读(harness建议=2611.08478 Scientist World·TB4 verifier基线对照+trace记录法·TB4已弃故仅备查) ⑫未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 5/7路未完+§10:10)⇒WAITING:0
下一步:       ①等网关429恢复(~05:25)后predict 7路加速推进至500(real patch将恢复) ②TB-2.1 launcher serial:opencode(429·harbor alive)→cc→dsh→pi(均需429恢复) ③codex TB-2.1需手动重跑(serial launcher已跳过·docker down时0done·429恢复后重跑) ④SWE-bench predict满500后重跑eval出最终矩阵 ⑤报告最终版增量更新
阻塞:         网关429 QUOTA_EXHAUSTED(curl确认·ETA~05:25)·predict real冻结459·TB-2.1 opencode/codex 429受阻(但进程存活)
ERROR_COUNT:  0
  📦 体积：TASK=30KB(30306B) / MEMORY=14KB(14552B)（均≤32KB✅·无需归档）
  🔍 cline专项小结: SWE-bench predict:cline96/500(62real·34empty·64.6%real rate·34empty=全429 infra)·eval resolved:cline35/46(76.1%)·TB-2.1 88reward:7pass(7.9%)·失败top1=网关429(infra)·C3=resume fix生效(real冻结459·429期间+13全empty=0新增real=infra铁证)·opencode144done127real(88.2%real rate)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [04:03] R1833 监控轮(网关429持续ETA~05:25·predict821/3500(+13全empty)·real冻结459·TB-2.1 cline/hermes DONE·opencode harbor alive 48min 0reward(429·docker内npm install)·codex 0done(docker down时跳过需重跑)·launcher+dockerd均alive):①CPU/MEM PASS(load68/224=30%·无失控>80核·无proc>8000%·mem785G/2015G·avail1101G) ②体积:TASK=30KB(30306B)/MEMORY=14KB(14552B)·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429持续**curl chat/completions→「请等待1小时24分钟49秒后重试」ETA~05:25 ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive但429受阻**total821/3500(+13sinceR1832·**real冻结459(+0)**):cline96·codex128·opencode144·cc147·pi67·hermes178·dsh61 ⑦**TB-2.1**:cline88(7pass=7.9%)DONE·hermes54(3pass=3.4%)DONE·opencode harbor alive 48min 0reward(429)·codex0done(docker down·需重跑)·cc/dsh/pi queued·launcher PID2141831 alive·dockerd PID1480217已恢复·oracle5/5✅ ⑧报告R1820仍current ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证) ⑪research日报11-07已读(harness建议=2611.08478·TB4已弃仅备查) ⑫未完成指令:有(§22:4x+§15:2x+§10:10)⇒WAITING:0

> [03:52] R1832 监控轮(网关429确认ETA~05:25·predict808/3500·real冻结459·TB-2.1 cline/hermes DONE·opencode stuck 4tasks exception=429·codex需重跑·进程alive):①CPU/MEM PASS(load72.6/224=32%·无失控>80核·top=pretrain llama-server非本线·mem804G/2015G·avail1082G) ②体积:TASK=30KB(30306B)/MEMORY=13KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429确认**curl real key→「请等待1小时33分钟23秒后重试」ETA~05:25 ⑤**SWE-bench eval 7/7 DONE✅**不变:cline35/46(76.1%)·codex6/8·opencode80/102(78.4%)·cc27/36·pi26/34·hermes124/131(94.7%)·dsh33/40(82.5%) ⑥**predict 7路alive但429受阻**total808/3500(+21sinceR1831·**real冻结459(+0)**=infra铁证):cline95(62r·33e·65.3%)·codex124(14r·110e·11.3%)·opencode143(127r·16e·88.8%)·cc143(38r·105e·26.6%)·pi66(37r·29e·56.1%)·hermes177(138r·39e·78.0%)·dsh60(43r·17e·71.7%) ⑦**TB-2.1**:cline88reward(7pass=7.9%)DONE·hermes54reward(3pass=3.4%·35errored=429)DONE·opencode stuck(4tasks started·all exception code1=429·0reward)·codex0done(需重跑)·3路queued(cc/dsh/pi)·oracle5/5✅ ⑧报告R1820仍current(real未变) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑪未完成指令:有(§22:4x+§15:2x+§10:10)⇒WAITING:0

> [03:40] R1831 监控轮(网关429确认ETA~05:24·predict787/3500·real冻结459·TB-2.1 cline/hermes DONE·codex需重跑·进程alive):①CPU/MEM PASS(load66.7/224=30%·无失控>80核·top=pretrain llama-server非本线·mem799G/2015G) ②体积:TASK=30KB(30306B)/MEMORY=12KB(12172B)·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429确认**curl chat/completions→「本次Token额度已用完，请等待1小时43分钟51秒后重试」ETA~05:24 ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive但429受阻**total787/3500(+11sinceR1830·**real冻结459(+0)**=infra铁证):cline92(62r·30e)·codex118(14r·104e)·opencode142(127r·15e)·cc137(38r·99e)·pi65(37r·28e)·hermes174(138r·36e)·dsh59(43r·16e) ⑦**TB-2.1**:cline88reward(7pass=7.9%)DONE·hermes54reward(3pass=3.4%·35errored=429)DONE·codex0done(429blocked·73jobfiles/0reward·**需手动重跑**)·opencode running 0done(429)·3路queued(cc/dsh/pi)·oracle5/5✅ ⑧报告R1820仍current(real未变) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证) ⑪research日报11-07已读(harness建议=TB4 verifier+trace记录法·TB4已弃故仅备查) ⑫未完成指令:有(§22:4x+§15:2x+§10:10)⇒WAITING:0

> [03:35] R1830 监控轮(网关429确认ETA~05:27·predict776/3500·real冻结459·TB-2.1 opencode running 0done·进程alive):①CPU/MEM PASS(load73.4/224=33%·无失控>80核·top=opencode44.6%非失控·mem806G/2015G) ②体积:TASK=30KB(30306B)/MEMORY=11KB(11311B)·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429确认**curl agi-gateway chat/completions→「请等待1小时52分钟14秒后重试」ETA~05:27 ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive但429受阻**total776/3500(+24sinceR1829·**real冻结459(+0)**=infra铁证):cline91(62r·29e)·codex114(14r·100e)·opencode142(127r·15e)·cc133(38r·95e)·pi64(37r·27e)·hermes173(138r·35e)·dsh59(43r·16e) ⑦**TB-2.1**:oracle5/5✅·cline88reward(7pass=7.9%)·hermes54reward(3pass=3.4%·35errored=429)·codex0done(429)·opencode running 0done(429·9jobs in /tmp)·3路queued(cc/dsh/pi) ⑧报告R1820仍current(real未变) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证) ⑪未完成指令:有(§22:4x+§15:2x+§10:10)⇒WAITING:0
> [03:19] R1829 监控轮(网关429确认ETA~05:26·predict752/3500·real冻结459·TB-2.1 hermes89/89DONE(3pass)·opencode刚started·进程alive):①CPU/MEM PASS(load67.6/224=30%·无失控>80核·top=pretrain llama-server非本线) ②体积:TASK=30KB(30306B)/MEMORY=31KB→归档R1811-R1828后~22KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429确认**gateway_probe.sh:/v1/models→HTTP200·/v1/chat/completions→「请等待2小时6分钟46秒后重试」ETA~05:26 ⑤**SWE-bench eval 7/7 DONE✅**不变:cline35/46(76.1%)·codex6/8·opencode80/102(78.4%)·cc27/36·pi26/34·hermes124/131(94.7%)·dsh33/40(82.5%) ⑥**predict 7路alive但429受阻**total752/3500(+13sinceR1828·**real冻结459(+0)**=infra铁证):cline89(62r·27e·69.7%)·codex107(14r·93e·13.1%)·opencode140(127r·13e·90.7%)·cc126(38r·88e·30.2%)·pi62(37r·25e·59.7%)·hermes171(138r·33e·80.7%)·dsh57(43r·14e·75.4%) ⑦**TB-2.1**:**hermes89/89DONE**(result.json:n_completed=89·n_errored=36·mean=0.0337·3pass·35 NonZeroAgentExitCode+1Timeout=mostly429)·cline89/89DONE(7pass·mean=0.0787)·codex19started/0done(429blocked)·**opencode刚started 03:14**(429blocked·launcher serial)·3路queued(cc/dsh/pi) ⑧报告R1820仍current(real未变) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑪未完成指令:有(§22:4x predict未满500+§15:2x TB-2.1 4/7路未完+§10:10)⇒WAITING:0
> 📦 R1817-R1828 流水(01:07~03:09,~12轮监控+网关429反复+predict 549→752/3500+TB-2.1 hermes 62→89/89DONE(3pass)+双报告R1817-R1822更新+research日报11-07已读)已归档 → daily-memories-harness/2026-11-08.md。**关键里程碑**:hermes TB-2.1 89/89DONE(3pass=3.4%·mean=0.0337·36errored)·predict real冻结459(429全程)·三报告R1820交付(cline_special+glm53_7way+tb21_7way)。需要时再读。

> 📦 R1811-R1816 流水(23:58~00:55,监控轮+deepseek eval完成+TB-2.1 cline89/89+hermes推进+网关429滚动+双报告多次更新)已归档 → daily-memories-harness/2026-11-08.md。**关键里程碑**:deepseek eval 33/40=82.5%(SWE-bench eval 7/7全done)·TB-2.1 cline89/89DONE(7pass=7.9%)·hermes 22→49/89(2pass→0pass)·网关429→200→429滚动·predict 530→542/3500。需要时再读。

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
