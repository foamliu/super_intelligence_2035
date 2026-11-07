# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R1746 cline专项R1746(429额度ETA~14:26·cline93.1%≈opencode无差距·codex适配器不重试429)·7路predict alive(cline41/codex39/opencode75/hermes99=373total)·TB4 483completed/0passed
已完成:       H-B✅·Gate7/7·TB报告✅·full500✅·R1735-R1745 P0/P1/审计/cleanup/cline专项C1-C5+always-extract-patch修复+R1745报告·R1746 cline专项深化+报告R1746交付
当前动作:     R1746:①CPU/MEM PASS(load44/224·1.2Ti avail·7路predict 0%CPU) ②C1:7路predict=cline41/codex39/opencode75/claude-code47/pi30/hermes99/deepseek30=373total·real235/empty138 ③C2:cline14空patch=12×429(85.7%)+2×额度前真实失败(14.3%)=100%infra/能力边界 ④C3:空patch未归零根因=网关429额度耗尽(ETA~14:26,非run_single.py:45 bug已修)·额度前27/29=93.1%real=opencode(92.0%)无差距 ⑤新发现:codex空patch间隔≈2min=适配器不重试429(cline≈6min=有重试)·codex1real/39=infra非能力 ⑥cline24.2min/题vs opencode10.0min=更谨慎但质量同 ⑦TB4 483completed/0passed(reward=0=能力) ⑧C5:报告R1746交付(8.8KB) ⑨网关/v1/models=200·/v1/chat/completions=429(额度耗尽,ETA~14:26)
下一步:       ①等网关额度恢复(ETA~14:26)→resume自动重跑空patch ②监控7路predict进度(目标500/路) ③§22:4x两基准7路全交付 ④额度恢复后验证cline real%→90%+·空patch归零 ⑤codex适配器429重试策略改进(可选)
阻塞:         网关额度耗尽(HTTP 429 on /v1/chat/completions,ETA~14:26)——predict进程alive但产出空patch,需等额度恢复
ERROR_COUNT:  0
  📦 体积：TASK=28KB / MEMORY=11KB(本轮无归档)
  🔍 cline专项小结: SWE-bench real 27/41(65.9%) · 额度前27/29=93.1%≈opencode(92%) · empty 14(全infra:429额度) · 24.2min/task · TB4 483completed/0passed · 失败top1=网关429额度耗尽(ETA~14:26)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [12:35] R1746 cline专项R1746+429额度ETA确认:①CPU/MEM PASS(load44/224·1.2Ti avail·7路predict 0%CPU·无失控) ②C1:7路predict=cline41/codex39/opencode75/claude-code47/pi30/hermes99/deepseek30=373total·real235/empty138 ③**C2关键更新**:cline14空patch=12×429额度(85.7%)+2×额度前真实失败(09:56/10:26=14.3%)=100%infra/能力边界 ④**C3确认**:空patch未归零根因=网关429额度耗(real key probe=HTTP429"请等待1h58m",ETA~14:26)·非run_single.py:45 bug(R1744已修)·额度前27/29=93.1%=opencode(92.0%)无差距 ⑤**新发现**:codex空patch间隔≈2min=适配器不重试429立即放弃(cline≈6min=有重试轮询)·codex1real/39=infra非能力差·claude-code同模式(2min速败) ⑥cline24.2min/题vs opencode10.0min/题=cline更谨慎(更多工具轮次)但产出质量同 ⑦TB4 483completed/0passed(reward=0=能力,verifier已运行pytest) ⑧C5:报告R1746交付report_harness_cline_special_r1746_zh.html(8.8KB,含429更新+适配器重试策略差异表+时间分布) ⑨网关/v1/models=200·/v1/chat/completions=429(额度耗尽) ⑩predict7路alive(0%CPU,额度恢复后自动续跑) ⑪未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [12:15] R1745 cline专项深化(额度前93.1%=opencode无能力差距):①CPU/MEM PASS(load60/224·1.2Ti avail·7路predict 0%CPU·无失控) ②C1:7路predict=cline40/codex29/opencode74/claude-code37/pi28/hermes96/deepseek28=332total·real235/empty97 ③**C2关键**:cline 64空patch(progress file全量)分类=QUOTA40(62.5%)+ADAPTER_SDK15(23.4%)+ADAPTER_CONN8(12.5%)+OTHER1=100%infra/adapter·0%能力 ④**C3关键发现**:空patch未归零但根因=**网关403额度耗尽**(非run_single.py:45 bug,R1744已修)·**额度耗尽前cline 27/29=93.1%real=opencode(93.2%)无能力差距**·最后real patch@10:34(astropy-14096,3207B)·之后13题全empty(403每6min快速失败) ⑤TB4 509completed/0passed(reward=0=能力,verifier已运行pytest) ⑥网关/v1/models=200·/v1/chat/completions=403(额度耗尽) ⑦gw_proxy 9092/9093运行中 ⑧C5:报告R1745交付report_harness_cline_special_r1745_zh.html(7KB,含额度前后对比表) ⑨predict进程7路alive(0%CPU,额度恢复后自动续跑) ⑩未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [11:50] R1744 always-extract-patch修复+cline专项更新:①CPU/MEM PASS(load47/224·1.2Ti avail·7路predict 0%CPU·无失控) ②C1:7路predict progress=cline36/codex22/opencode74/claude-code31/pi26/hermes94/deepseek27=310total·real235/empty75(75.8%real)·cline real=27/36=75.0% ③C2:cline 9空patch全=no_progress_data(rc=None,wall=0,progress文件仅11/36条)·codex 21空patch=同因·网关=GATEWAY_QUOTA_EXHAUSTED ④**C3关键修复**:run_single.py:45+run_harness.py 6driver(210/249/277/360/498/550)——将`git_patch(workdir) if r.returncode==0 else ""`改为`git_patch(workdir)`(7处,DeepseekDriver:454已修)·run_single返回码`return 0 if rc==0 else 1`→`return 0`·py_compile验证通过 ⑤TB4 460completed/0passed(reward=0非None=能力,verifier已运行pytest) ⑥连接正常cline real=27/27=100% ⑦gw_proxy 9090/9091运行中 ⑧C5:报告R1744交付report_harness_cline_special_r1744_zh.html(7.3KB) ⑨未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [11:37] R1743 TB4重大纠正+cline专项C2重分类:①CPU/MEM PASS(load51/224·1.2Ti avail·7路predict alive) ②C1:7路predict progress=cline34/codex14/opencode73/claude23/pi24/hermes91/deepseek26 ③C2重分类(从progress file的stdout_tail):64空patch=额度耗尽33(51.6%)+AI_SDK15(23.4%)+ConnRef15(23.4%)+silent1(1.6%)=100%·infra=98.4%·R1742将11个timeout误分(实际=额度耗尽重试撞1800s超时)·AI_SDK从4升至15(R1742遗漏) ④C3:空patch未归零根因=run_single.py:45(`git_patch if rc==0 else ""`)·48/64空patch是rc!=0→即使修改了文件也丢弃diff·resume fix生效(is_predicted检查model_patch非空→下次重启重跑) ⑤**TB4重大纠正**:R1742"reward=None=verifier未运行=infra"是**错误的**!深挖verifier/目录:reward.json={"reward":0}(非None!)·reward.txt=0·ctrf.json=pytest 16tests 2pass/14fail·verifier**已运行**·trial result.json顶层reward=None是harbor schema(reward在verifier_result.rewards.reward=0)·正确归因=能力问题(glm-5.3-flash无法解TB4)·R1742归因红线违规 ⑥TB4 7路27completed/0passed·全7路completed trials的verifier/reward.json都是0 ⑦连接正常cline real=27/27=100% ⑧deepseek gw_proxy_dsh 9093=HTTP200(已恢复)·deepseek 26/500 real=24 empty=2 ⑨C5:报告R1743交付report_harness_cline_special_r1743_zh.html(12.4KB,纠正版) ⑩未完成指令:有(§22:4x+§10:10)⇒WAITING:0
> [10:53] R1740 cline专项+exit-code修复:①CPU/MEM PASS(load59/224) ②C1:SWE-bench cline 27/29 real=93.1%(median patch 2398B)·opencode 67/67·hermes 67/74 ③C2:TB4首轮66/66全errored=RuntimeError(exit1)·根因=ECONNRESET(socket closed)=infra·重跑5题:2完成reward0=能力(verifier ran)+2errored="Model ended without recognized finish reason"=网关协议兼容(infra)+1CancelledError(我kill) ④C3:空patch 51.5%→6.9%(resume fix is_predicted检查model_patch非空·2个剩余空patch为新鲜产出将自动重跑) ⑤**exit-code修复**:cline_patched.py:201原"非零退出→raise RuntimeError→verifier跳过"改为"仅无run_result事件才raise,否则记warning让verifier评分"·语法验证OK ⑥cline TB4 rerun2启动(PID2737781,修复后代码) ⑦deepseek predict重启(PID2737772,gw_proxy_dsh 9093 HTTP200,astropy-13398 no-patch 138s,astropy-13453 SKIP=真实14059B patch progress记录stale 0B) ⑧7/7路predict alive(cline29/codex6/opencode68/claude21/pi22/hermes75/deepseek24) ⑨C5:report_harness_cline_special_r1740_zh.html交付(11.6KB) ⑩gateway HTTP200健康 ⑪未完成指令:有(§22:4x)⇒WAITING:0
> [09:33] R1739 predict重启:①CPU/MEM PASS(load70/224·1.2Ti avail) ②killed 7旧predict(429空转+旧resume代码:is_predicted用size>50B而非model_patch)→gateway立即恢复GATEWAY_OK(13并发→9并发→恢复) ③cleanup --delete×2=423空patch删除(392+31) ④restart predict batch1(opencode/hermes/cline)+batch2(codex/claude-code/pi)+batch3(deepseek)=7路 ⑤固定resume代码确认生效:SKIP real patch(500B/3058B/...),PREDICT deleted-empty任务 ⑥6/7工作正常(opencode task3/hermes task6/cline task3/codex task2/claude task2/pi task1) ⑦deepseek-harness 1.1s空patch=异常(gw_proxy_dsh 9093问题)→已kill待查 ⑧TB4 6路harbor alive·gateway 13并发OK ⑨§08:1x审计报告已交付+oracle=1.0×3✅→标✅已交付 ⑩未完成指令:有(§22:4x)⇒WAITING:0
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
