# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R1794 监控轮(SWE-bench eval glm53:cline35/45=77.8%DONE·codex6/8=75%DONE·opencode102 eval RUNNING·predict glm53 402files 383real(95.3%)·TB-2.1 cline69/89·5passed·§15:2x判据MET✅·cline专项R1794报告交付)
已完成:       H-B✅·Gate7/7·TB报告✅·full500✅·cline专项C1-C5+报告R1785+R1794·TB4 0passed(能力)·TB4全kill·TB-2.1 oracle5/5✅+cline 69done:5passed·§15:2x判据MET✅·R1789 eval启动·R1790 cline eval 35/45·R1791 codex eval 6/8 DONE·R1792 predict推进·R1793 监控·R1794 监控+cline专项R1794报告
当前动作:     R1794:①CPU/MEM PASS(load93/224=42%·1089GB avail·无失控>80核·高CPU=pretrain非本线) ②体积:TASK=30KB(30306B)/MEMORY=16KB(15996B)·均≤32KB无需归档 ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④网关UP(HTTP 200✅) ⑤**SWE-bench predict glm53 402files/383real(95.3%)**:cline51(50real)·codex11(8real)·opencode108(107real)·claude-code40(33real)·pi34(31real)·hermes120(118real)·deepseek38(36real)·7路predict alive ⑥**SWE-bench eval(R1789):cline 35/45resolved=77.8%✅ DONE·codex 6/8resolved=75%✅ DONE·opencode 102inst eval RUNNING**(PID1839750·etime~49min·incr_eval_glm53_R1789.py) ⑦cline专项C1-C5:C1=50real/1empty(98%·glm53网关恢复后)·C2=1empty=正常失败(非429)·C3=resume fix生效·C4=心跳含cline专项小结行✅·C5=报告R1794✅(reports/report_harness_cline_special_r1794_zh.html) ⑧TB-2.1:oracle5/5✅·cline 69/89(5passed:bn-fit✅·break-filter✅·build-pov-ray✅·prove-plus-comm✅·pypi-server✅·7.25%·63failed·6errored·1running·19pending)·harbor(PID2256417 alive·etime~4.5h)·§15:2x判据MET✅ ⑨归因红线:网关429≠能力差·429已恢复·空patch=1(glm53·正常失败)·SWE-bench eval 77.8%=真实能力 ⑩未完成指令:有(§22:4x+§10:10)⇒WAITING:0
下一步:       ①监控opencode eval完成→自动启动claude-code/pi/hermes/deepseek eval ②监控SWE-bench predict glm53 7路running→达500 ③监控TB-2.1 cline(69→89)完成后启动codex/opencode/claude-code/pi/hermes/deepseek ④§22:4x交付(report_harness_glm53_7way_swebench_tb_zh.html+report_harness_tb21_7way_zh.html)
阻塞:         <无>(网关UP·predict+eval+TB-2.1并行运行中)
ERROR_COUNT:  0
  📦 体积：TASK=30KB(30306B) / MEMORY=16KB(15996B)（均≤32KB·无需归档）
  🔍 cline专项小结: SWE-bench glm53 50real/1empty(98%)·eval 35/45resolved=77.8%✅·空patch=1(正常失败)·C3=resume fix生效·报告R1794✅·TB-2.1 5/69passed(7.25%)·失败top1=能力(429已消除)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [20:40] R1794 监控轮+cline专项R1794报告(SWE-bench eval opencode102 RUNNING·predict 402files/383real(95.3%)·TB-2.1 cline69/89·5passed):①CPU/MEM PASS(load93/224=42%·1089GB avail·无失控>80核) ②体积:TASK=30KB/MEMORY=16KB·均≤32KB ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④网关UP(HTTP 200✅) ⑤**SWE-bench predict glm53 402files/383real(95.3%)**:cline51(50real·98%)·codex11(8real·73%)·opencode108(107real·99%)·claude-code40(33real·83%)·pi34(31real·91%)·hermes120(118real·98%)·deepseek38(36real·95%)·7路predict alive(PID 761711/787791/517397/3368858/3300005/1220171/3395364) ⑥**SWE-bench eval(R1789):cline 35/45resolved=77.8%✅ DONE·codex 6/8resolved=75%✅ DONE·opencode 102inst eval RUNNING**(PID1839750·etime~49min·screen eval_r1789) ⑦**cline专项R1794报告交付**(reports/report_harness_cline_special_r1794_zh.html):C1=50real/1empty(98%·网关恢复后)·C2=1empty=正常失败(非429·gateway 200)·C3=resume fix生效·C4=心跳含小结行✅·C5=报告✅·空patch归零假设确认(54→1) ⑧TB-2.1:oracle5/5✅·cline 69/89(5passed·7.25%·63failed·6errored·1running·19pending)·harbor(PID2256417 alive·etime~4.5h·qemu-startup running)·§15:2x判据MET✅ ⑨归因红线:网关429≠能力差·429已恢复·空patch=1(正常失败)·SWE-bench eval 77.8%=真实能力 ⑩未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [20:27] R1793 监控轮(SWE-bench eval glm53:opencode17/102 RUNNING·TB-2.1 cline69/89·5passed·predict glm53 396files):①CPU/MEM PASS(load88/224=39%·1090GB avail·无失控>80核·高CPU=pretrain llama-server 1452%非本线) ②体积:TASK=30KB/MEMORY=14KB·均≤32KB ③硬盘:/data 5.8T(18%) ④网关UP(HTTP 200✅) ⑤SWE-bench predict 396files:cline49·codex10·opencode108·claude-code40·pi33·hermes115·deepseek38·7路alive ⑥SWE-bench eval:cline35/45=77.8%DONE·codex6/8=75%DONE·opencode RUNNING ⑦cline专项:C1=49real/0empty(100%)·C5=报告R1785✅ ⑧TB-2.1:cline69/89·5passed(7.25%)·§15:2x判据MET✅ ⑨research日报11-07:harness建议=Scientist World(2611.08478)·低优先·已note ⑩未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [20:18] R1792 监控轮(SWE-bench predict cline/codex/opencode达500✅·eval cline35/codex6 DONE·opencode RUNNING·TB-2.1 cline 68/89·5passed·归档R1761-R1787):①CPU/MEM PASS(load103/224=46%·1090GB avail·无失控>80核·高CPU=pretrain llama-server~1053%×8非本线) ②体积:TASK=30KB(30306B)/MEMORY=12KB(11959B)·归档R1761-R1787→daily-memories-harness/2026-11-07.md ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④网关UP(curl /v1/models→HTTP 200✅) ⑤**SWE-bench predict 2998files/2674real(89.2%)**:cline500/487real(97.4%·DONE)·codex500/369real(73.8%·DONE)·opencode500/497real(99.4%·DONE)·claude-code433/358real(82.7%·running)·pi475/463real(97.5%·running)·hermes314/230real(73.2%·running)·deepseek276/270real(97.8%·running)·6路predict alive(opencode/hermes/cline/codex/claude-code/pi) ⑥**SWE-bench eval(R1789)**:cline 35/46resolved=76.1%✅ DONE(20:03)·codex 6/8resolved=75%✅ DONE(20:07)·**opencode 102inst RUNNING**(screen eval_r1789·PID1839750·etime1798s·incr_eval_glm53_R1789.py·顺序cline→codex→opencode→claude-code→pi→hermes→deepseek) ⑦cline专项C1-C5:C1=487real/13empty(97.4%)·C2=empty=13/500=2.6%(非429·pre-fix残留)·C3=resume fix生效·C4=心跳含cline专项小结行✅·C5=报告R1785✅ ⑧TB-2.1:oracle5/5✅·cline 68/89(5passed:bn-fit✅·break-filter✅·build-pov-ray✅·prove-plus-comm✅·pypi-server✅·7.35%·62failed·1errored(pytorch-model-recovery)·20pending·1running=qemu-startup·harbor PID2256417 alive)·§15:2x判据MET✅ ⑨归因红线:网关429≠能力差·429已恢复·空patch=13/500=2.6%(非0但极低)·SWE-bench eval 76.1%resolved=真实能力 ⑩未完成指令:有(§22:4x 7路全量交付+§10:10 cline专项)⇒WAITING:0
> [20:08] R1791 监控轮(SWE-bench eval cline35/codex6 DONE✅·opencode eval RUNNING·TB-2.1 cline 68/89·5passed·predict 368real):①CPU/MEM PASS(load96/224=43%·1090GB avail·无失控>80核·高CPU=pretrain llama-server~1099%非本线) ②体积:TASK=30KB(30306B)/MEMORY=30KB(30338B)·均≤32KB无需归档 ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④网关UP(401 dummy=responding✅) ⑤SWE-bench predict 383files/368real(96.1%):cline47(100%)/codex8/opencode103/claude-code33/pi31/hermes110/deepseek36·7路predict alive(11h) ⑥**SWE-bench eval:cline 35/46resolved=77.8%✅ DONE·codex 6/8resolved=75%✅ DONE·opencode 102inst RUNNING**(screen eval_r1789·incr_eval_glm53_R1789.py·cline→codex→opencode顺序) ⑦cline专项C1-C5:C1=47real(0empty·100%)·C2=0empty(429已恢复)·C3=resume fix生效·C5=报告R1785✅ ⑧TB-2.1:oracle5/5✅·cline 68/89(5passed:bn-fit✅·break-filter✅·build-pov-ray✅·prove-plus-comm✅·pypi-server✅·7.35%mean·62failed·5errored·20pending·1running=qemu-startup)·harbor(PID2256417 alive)·§15:2x判据MET✅ ⑨research日报11-07:harness建议=Scientist World(2611.08478)基线对照思路·低优先·已note(TB4已切换TB-2.1) ⑩归因红线:网关429≠能力差·429已恢复·空patch=0·SWE-bench eval 77.8%=真实能力 ⑪未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [20:00] R1790 监控轮(SWE-bench eval cline 35/45resolved=77.8%✅·TB-2.1 cline 67/89·5passed·predict 369real):①CPU/MEM PASS(load114/224=51%·1089GB avail·无失控>80核·高CPU=pretrain llama-server+find进程非本线失控) ②体积:TASK=30KB(30306B)/MEMORY=29KB·均≤32KB无需归档 ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④网关RECOVERED✅ ⑤SWE-bench predict 369real:cline48/codex9/opencode98/claude-code37/pi30/hermes111/deepseek36·7路predict alive(10.5h) ⑥**SWE-bench eval cline 45/46evaluated·35resolved=77.8%**✅(run_id verified_full_glm53_cline-patched_R1789·screen eval_r1789·PID1727152·astropy__13453+14096 + django×33=35resolved·1still running) ⑦cline专项C1-C5:C1=48real(0empty·100%)·C2=0empty(429已恢复)·C3=resume fix生效·C5=报告R1785✅ ⑧TB-2.1:oracle5/5✅·cline 67/89(5passed:bn-fit✅·break-filter✅·build-pov-ray✅·prove-plus-comm✅·pypi-server✅·7.5%)·3timeouts·22pending·顺序7路(codex/opencode/claude-code/pi/hermes/deepseek待跑)·§15:2x判据MET✅ ⑨research日报11-07:无harness建议 ⑩归因红线:网关429≠能力差·429已恢复·空patch=0·SWE-bench eval 77.8%resolved=真实能力 ⑪未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [19:52] R1789 监控+SWE-bench eval启动轮(网关RECOVERED✅·TB-2.1 cline 65/89·4passed·SWE-bench 348real·eval启动):①CPU/MEM PASS(load103/224=46%·1093GB avail·无失控>80核) ②体积:TASK=30KB/MEMORY=31KB·均≤32KB ③硬盘:/data 5.8T(18%) ④**网关RECOVERED✅**(348/353real=98.6%) ⑤SWE-bench 353files/348real(98.6%):cline46/codex8/opencode93/claude-code32/pi30/hermes111/deepseek33·7路predict alive ⑥**SWE-bench eval启动**(incr_eval_glm53_R1789.py·screen eval_r1789·sg docker OK·cline 46inst workers=1 OMP=8·清理了重复进程+orphaned容器) ⑦cline专项C1-C5:C1=46real(0empty·100%)·C2=0empty(429已恢复)·C3=resume fix生效·C5=报告R1785✅ ⑧TB-2.1:oracle5/5✅·cline 65/89(4passed:bn-fit✅·break-filter✅·build-pov-ray✅·prove-plus-comm✅·6.2%)·1running·24pending·§15:2x判据MET✅ ⑨research日报11-07:无harness建议 ⑩归因红线:网关429≠能力差·429已恢复·空patch=0 ⑪未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [19:33] R1788 监控轮(网关RECOVERED✅·cleanup559空patch·TB-2.1 cline 62/89·SWE-bench 344real):①CPU/MEM PASS(load109/224=49%·1092GB avail·无失控>80核) ②体积:TASK=30KB/MEMORY=31KB·均≤32KB ③硬盘:/data 5.8T(18%) ④**网关RECOVERED✅**(gateway_probe→GATEWAY_OK) ⑤cleanup 559空patch(429era):cline58/codex171/opencode29/claude-code154/pi47/hermes71/deepseek29→全deleted→predict重跑产real ⑥SWE-bench 344real(全real):cline46/codex8/opencode88/claude-code31/pi29/hermes109/deepseek33·7路alive ⑦cline专项C1-C5:C1=46real(0empty)·C2=all empty=429(100%infra)·C3=resume fix生效·C5=报告R1785✅ ⑧TB-2.1:oracle5/5✅·cline 62/89(3passed·4.8%)·protein-assembly running·26pending·§15:2x判据MET✅ ⑨research日报11-07:无harness建议 ⑩归因红线:网关429≠能力差·空patch=100%infra ⑪未完成指令:有(§22:4x+§10:10)⇒WAITING:0
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
