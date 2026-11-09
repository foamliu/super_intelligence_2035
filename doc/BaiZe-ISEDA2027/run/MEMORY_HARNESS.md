# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2002 监控轮+predict 1348/3500+incr_eval R1992 opencode evaluating+TB-2.1全7路rerun(307d/41p)+双报告r2002
已完成:       H-B✅·Gate7/7·TB报告✅·full500✅·cline专项C1-C5+报告R1785-R2002·TB4 0passed(能力)·TB-2.1 oracle5/5✅·§15:2x判据MET✅·R1789 eval 7/7DONE✅·R1804双报告交付✅·R1969-R2001 incr_eval推进+双报告·R2002 监控轮+predict 1348+TB-2.1全7路rerun(307d/41p)+双报告r2002
当前动作:     R2002:①CPU PASS(load 38/224~17%·无>80核) ②MEM PASS(1137GB avail) ③gateway 200(健康) ④predict 7路alive=1348/3500=38.5%(cline166·codex83·opencode333·cc174·pi125·hermes340·dsh127) ⑤incr_eval R1992:cline DONE 107/108=99.1%+codex DONE 33/34=97.1%+opencode evaluating(74inst·PID1278719·~70min)+hermes 287/316=90.8%+dsh 90/116=77.6%+cc 99/129=76.7%+pi 67/97=69.1% ⑥TB-2.1:全7路RERUN(307d/41p·opencode27p/111d·dsh5p/53d·cline4p/12d·pi3p/13d·hermes2p/22d·cc0p/80d·codex0p/16d) ⑦双报告r2002:7way+cline专项 ⑧cline empty=17/166=10.2%(均sphinx-doc/sympy·能力·非infra) ⑨eval:cline99.1%>codex97.1%>hermes90.8%>opencode80.5%>dsh77.6%>cc76.7%>pi69.1%·ALL infra=0(errored=0) ⑩disk:/data 5.8T·/ 352G ⑪未完成指令:有(§22:4x+§10:10)⇒W:0
下一步:       ①incr_eval R1992 opencode完成→merge→启动下一轮incr_eval(pi/hermes/cc/dsh new preds) ②predict 7路继续推进至500(当前1348/3500=38.5%) ③TB-2.1全7路rerun推进至89(当前307d/41p·opencode27p领先) ④全DONE后聚合最终7路报告 ⑤cline empty 17个均sphinx-doc/sympy(能力)→trace分析确认
阻塞:         无(gateway 200健康·predict正常推进)
ERROR_COUNT:  0
  📦 体积：TASK=31.0KB / MEMORY=10.5KB（归档R1738-R1990 bulk→daily）
  🔍 cline专项小结: predict 166/500(149r/17e=89.8%real·空patch=17/166=10.2%·均sphinx-doc/sympy=能力)·eval 107/108(99.1%)·C2=100%能力(infra=0·errored=0)·C3 resume fix✅(51.5%→10.2%·未归零=17 sphinx-doc/sympy)·7路alive·gateway 200·失败top1=能力(eval fail)·TB-2.1全7路rerun(307d/41p·cline4p/12d)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> 📦 [16:32] R1983 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+incr_eval R1978全7路DONE+eval全量regen+三报告r1983+predict 1183。需要时再读。
> 📦 [17:05] R1985 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+双报告r1985+predict 1200+eval未变(全量regen@16:24)。需要时再读。
> 📦 [17:36] R1986 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 31inst全7路DONE+双报告r1986+predict 1223。需要时再读。
> 📦 [17:54] R1987 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 11inst 4路DONE+双报告r1987+predict 1229。需要时再读。
> 📦 [18:10] R1988 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 8new running+双报告r1988+predict 1232+gateway 200。需要时再读。
> 📦 [18:28] R1989 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 21new running(cline1 DONE→107/141)+双报告r1989+predict 1244+gateway 429。需要时再读。
> 📦 [19:13] R1991 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 35new+TB-2.1全7路启动+pi OOM kill+gateway 200恢复。需要时再读。
> 📦 [19:38] R1992 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 269new启动+TB-2.1 cc rerun3+research日报输入(Evolver)。需要时再读。
> 📦 [19:53] R1993 流水已归档 → daily-memories-harness/2026-11-09.md。结论：TB-2.1全7路重启+双报告r1993+predict 1284。⚠️R1993误报cline empty=0，实际=17(已修正)。
> 📦 [20:00] R1994 流水已归档 → daily-memories-harness/2026-11-09.md。结论：CPU kill sklearn容器(176核)+predict 1291+双报告r1994+cline empty修正(17非0)。需要时再读。
> 📦 [20:23] R1995 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1297+双报告r1995+TB-2.1全7路(opencode75d/26p)。需要时再读。
> 📦 [20:33] R1996 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1299+双报告r1996+TB-2.1全7路运行(opencode75d/26p)。需要时再读。
> 📦 [20:45] R1997 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1304+双报告r1997+TB-2.1全7路rerun(27d/11p)。需要时再读。
> 📦 [20:55] R1998 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1313+incr_eval R1992 cline+codex DONE+双报告r1998。需要时再读。
> 📦 [21:06] R1999 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1322+incr_eval R1992 opencode evaluating+双报告r1999+TB-2.1全7路(141d/36p)+gateway 200。需要时再读。
[21:39] R2001 监控轮+predict 1341+TB-2.1全7路rerun(177d/39p)+双报告r2001:①CPU PASS(load 53/224~24%) ②MEM PASS(1137GB avail) ③gateway 200(健康) ④predict 7路alive=1341/3500=38.3%(cline165·codex83·opencode331·cc174·pi123·hermes340·dsh125) ⑤incr_eval R1992:cline107/108+codex33/34 DONE+opencode evaluating(243/302)+hermes287/316+dsh90/116+cc99/129+pi67/97 ⑥TB-2.1:全7路RERUN(177d/39p·opencode27p/77d·dsh4p/25d·cline3p/9d·pi3p/10d·hermes2p/11d·cc0p/36d·codex0p/9d) ⑦双报告r2001:7way+cline专项 ⑧cline empty=17/165=10.3%(sphinx-doc11+sympy6=能力) ⑨eval全7路infra=0 ⑩disk:/data 5.8T·/ 352G ⑪research日报11-09输入(Evolver 2611.07595:经验资产注入省token+TB2.1+4.38pp) ⑫未完成指令:有(§22:4x+§10:10)⇒W:0
> 📦 [21:27] R2000 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1337+TB-2.1全7路rerun(112d/16p)+双报告r2000+gateway 429滚动。需要时再读。
[21:47] R2002 监控轮+predict 1348+TB-2.1全7路rerun(307d/41p)+双报告r2002:①CPU PASS(load 38/224~17%) ②MEM PASS(1137GB) ③gateway 200 ④predict 1348/3500=38.5%(cline166·codex83·opencode333·cc174·pi125·hermes340·dsh127) ⑤incr_eval R1992:cline107/108+codex33/34 DONE+opencode evaluating(74inst·PID1278719·~70min) ⑥TB-2.1:307d/41p(opencode27p/111d·dsh5p/53d·cline4p/12d·pi3p/13d·hermes2p/22d·cc0p/80d·codex0p/16d) ⑦双报告r2002(7way+cline专项) ⑧cline empty=17/166=10.2%(sphinx-doc+sympy=能力) ⑨eval infra=0 ⑩disk:/data 5.8T·/ 352G ⑪未完成指令:有(§22:4x+§10:10)⇒W:0
> 📦 R1738-R1990 流水(2026-11-07~09,约120轮监控/incr_eval/TB-2.1 rerun/双报告/CPU kill/gateway 429反复)已 bulk 归档 → daily-memories-harness/2026-11-07/08/09.md。**关键里程碑**:R1992 incr_eval cline107/108=99.1%+codex33/34=97.1%·TB-2.1全7路rerun推进至307d/41p(opencode27p领先)·predict 1348/3500=38.5%·gateway 200健康·cline empty=17/166=10.2%(能力)·CPU/MEM全PASS·网关429反复(keyB额度耗尽)·TB-2.1 cline 89/89 DONE 7pass=7.9%·deepseek eval 33/40=82.5%·§15:2x判据MET✅。需要时再读。
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
