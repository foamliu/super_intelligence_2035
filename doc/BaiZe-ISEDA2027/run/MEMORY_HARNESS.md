# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R1743 cline专项TB4重大纠正(reward=0非None=能力问题非infra)·7路predict alive(14-91/500)·TB4 27completed/0passed(reward=0=verifier已运行pytest 2pass/14fail)
已完成:       H-B✅·Gate7/7·TB报告✅·full500✅·R1735-R1742 P0/P1/审计/cleanup/cline专项C1-C5+exit-code修复·R1743 TB4纠正(reward=0非None=C2重分类+run_single.py:45根因)
当前动作:     R1743:①CPU/MEM PASS(load51/224·1.2Ti avail) ②C1:7路predict progress:cline34/codex14/opencode73/claude23/pi24/hermes91/deepseek26 ③C2重分类:64空patch=额度耗尽33(51.6%)+AI_SDK15(23.4%)+ConnRef15(23.4%)+silent1(1.6%)=100%·infra=98.4% ④C3:空patch未归零根因=run_single.py:45(rc!=0丢弃patch)·resume fix生效(is_predicted检查model_patch非空) ⑤**TB4重大纠正**:R1742"reward=None=verifier未运行"是错误的!深挖verifier/目录:reward.json={"reward":0}(非None!)·ctrf.json=pytest 16tests 2pass/14fail·verifier已运行·reward=0=能力问题(glm-5.3-flash无法解TB4)·R1742归因红线违规(能力失败误标infra) ⑥连接正常cline real=27/27=100% ⑦deepseek gw_proxy_dsh 9093=HTTP200(已恢复)·deepseek 26/500 real=24 ⑧C5:报告R1743交付(12.4KB,纠正版)
下一步:       ①监控7路predict进度(目标500/路) ②修复run_single.py:45(始终提取git_patch)→验证空patch率下降 ③§22:4x两基准7路全交付 ④额度充足时段重跑cline验证空patch归零假设
阻塞:         无
ERROR_COUNT:  0
  📦 体积：TASK=28KB / MEMORY=9.1KB(本轮无归档)
  🔍 cline专项小结: SWE-bench real 27/34(79.4%) · empty 7(20.6%=100%infra) · 连接正常real=27/27=100% · TB4 27completed/0passed(**reward=0非None**=能力问题,verifier已运行pytest 2pass/14fail) · 失败top1=网关额度耗尽(33/64=51.6%) · top2=AI_SDK(15)+ConnRef(15)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
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
