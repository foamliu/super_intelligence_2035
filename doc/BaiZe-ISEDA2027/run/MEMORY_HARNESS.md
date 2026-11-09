# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2005 监控轮+predict 1365/3500+incr_eval R1992 claude-code running+TB-2.1全7路rerun(7docker active)+不产出HTML(11-09报告纪律)
已完成:       H-B✅·Gate7/7·TB报告✅·full500✅·cline专项C1-C5+报告R1785-R2004·TB4 0passed(能力)·TB-2.1 oracle5/5✅·§15:2x判据MET✅·R1789 eval 7/7DONE✅·R1804双报告交付✅·R1969-R2004 incr_eval推进+双报告·R2004 监控轮+predict 1361+TB-2.1(164d/26p)+不产出HTML+gateway 200
当前动作:     R2005:①CPU PASS(harness 0.0-29.3%·load 265=pretrain非本线) ②MEM PASS(1130GB avail) ③gateway 200(健康) ④predict 7路alive=1365/3500=39.0%(cline167·codex86·opencode335·cc176·pi129·hermes342·dsh130) ⑤incr_eval R1992:codex DONE(33/34)+opencode DONE(243/244)+claude-code running(44new·22:24启动) ⑥TB-2.1全7路RERUN(7 docker active:torch-tensor-parallelism/circuit-fibsqrt/mteb-retrieve/git-multibranch/feal-diff-crypt/configure-git-webserver/compile-compcert) ⑦日常轮不产出HTML(11-09报告纪律) ⑧cline empty=17/167=10.2%(均sphinx-doc·能力) ⑨disk:/data 5.8T(18%)·/ 352G(4%) ⑩research日报11-09已读(R2004纳入参考) ⑪未完成指令:有(§22:4x+§10:10)⇒W:0
下一步:       ①incr_eval R1992 claude-code完成→merge→启动下一轮incr_eval(pi/hermes/dsh new preds) ②predict 7路继续推进至500(当前1365/3500=39.0%) ③TB-2.1全7路rerun推进至89(7docker active) ④全DONE后聚合最终7路报告 ⑤cline empty 17个均sphinx-doc(能力)→trace分析确认
阻塞:         无(gateway 200健康·predict正常推进·incr_eval正常推进·TB-2.1 7docker active)
ERROR_COUNT:  0
  📦 体积：TASK=31.0KB / MEMORY=~17KB（归档 ~15.5KB旧流水指针 → daily-memories-harness/2026-11-08.md等）
  🔍 cline专项小结: predict 167/500(150r/17e=89.8%real·空patch=17/167=10.2%·均sphinx-doc=能力)·eval incr_R1992 codex DONE(33/34)+opencode DONE(243/244)·C2=100%能力(infra=0)·C3 resume fix✅(51.5%→10.2%·未归零=17 sphinx-doc)·7路alive·gateway 200·失败top1=能力(eval fail)·TB-2.1(7docker active)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
[22:23] R2005 监控轮+predict 1365/3500+incr_eval R1992 cc running+TB-2.1(7docker active)+不产出HTML(11-09报告纪律):①CPU PASS(harness 0.0-29.3%·load 265=pretrain非本线) ②MEM PASS(1130GB avail) ③gateway 200(健康) ④predict 7路alive=1365/3500=39.0%(cline167·codex86·opencode335·cc176·pi129·hermes342·dsh130·+4sinceR2004) ⑤incr_eval R1992:codex DONE(33/34 resolved)+opencode DONE(243/244 resolved)+claude-code running(44new·22:24启动) ⑥TB-2.1全7路RERUN(7 docker active:torch-tensor-parallelism/circuit-fibsqrt/mteb-retrieve/git-multibranch/feal/configure-git-webserver/compile-compcert) ⑦日常轮不产出HTML(2026-11-09报告纪律·只写心跳+daily一行) ⑧cline empty=17/167=10.2%(均sphinx-doc·能力·非infra) ⑨disk:/data 5.8T(18%)·/ 352G(4%) ⑩research日报11-09已读(R2004纳入参考) ⑪归档~15.5KB旧流水指针(11-08及更早→daily文件) ⑫未完成指令:有(§22:4x+§10:10)⇒W:0
> 📦 [22:09] R2004 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1361+TB-2.1(164d/26p)+不产出HTML+gateway 200。需要时再读。
> 📦 [22:02] R2003 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1358+TB-2.1全7路rerun(62d/23p)+不产出HTML+gateway 200。需要时再读。
> 📦 [21:39] R2001 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1341+TB-2.1全7路rerun(177d/39p)+双报告r2001+gateway 200。需要时再读。
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
> 📦 [21:27] R2000 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+predict 1337+TB-2.1全7路rerun(112d/16p)+双报告r2000+gateway 429滚动。需要时再读。
> 📦 [18:52] R1990 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval 28new running+双报告r1990+predict 1261+gateway 429。需要时再读。
> 📦 R1981-R1984 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+TB-2.1数据修复+双报告r1981-r1984+predict 1170-1190。需要时再读。
> 📦 [15:20] R1980 流水已归档 → daily-memories-harness/2026-11-09.md。结论：incr_eval opencode DONE(234/292)+claude-code 34/69进行中+cline empty 6(sphinx-doc)+双报告r1980。需要时再读。
> 📦 [14:10] R1976 流水已归档 → daily-memories-harness/2026-11-09.md。结论：监控轮+cline专项r1976(空patch误报0·已R1977更正)+incr_eval R1975 DONE。需要时再读。
> 📦 [13:55] R1975 流水已归档 → daily-memories-harness/2026-11-09.md。结论：eval全量regen(7路)+incr_eval R1975(3missing DONE)+cline专项r1975(空patch 2/137=1.5%)。需要时再读。
> 📦 [13:13] R1973 流水已归档 → daily-memories-harness/2026-11-09.md。结论：CPU kill(sklearn 178核)+incr_eval R1972推进(cline DONE→codex)+gateway QUOTA_EXHAUSTED。需要时再读。
> 📦 [12:55] R1972 流水已归档 → daily-memories-harness/2026-11-09.md。结论：CPU kill(sklearn 160核)+eval全run扫描重生成(2280/2966=76.9%)+incr_eval R1972启动(297missing)+cline专项r1972报告。需要时再读。
> 📦 [12:17] R1970 流水已归档 → daily-memories-harness/2026-11-09.md。结论：codex predict RESTARTED+incr_eval_hermes DONE(149/168)+eval merge 7/7DONE+cline专项r1970。需要时再读。
> 📦 [11:50] R1969 流水已归档 → daily-memories-harness/2026-11-09.md。结论：gateway RESTORED+cleanup 1656空patch+7路复产real+cline专项r1969+TB-2.1 152p。需要时再读。
> 📦 [11:32] R1968 流水已归档 → daily-memories-harness/2026-11-09.md。结论：gateway QUOTA EXHAUSTED发现(/models=200但/chat/completions=CURL_FAILED)·predict 2702/3500 real=1047 empty=1655·cline专项r1968报告·TB-2.1 124passed。需要时再读。
> 📦 [11:20] R1967 流水已归档 → daily-memories-harness/2026-11-09.md。结论：gateway HTTP200确认·predict 2694/3500·cline专项r1967报告·TB-2.1 152p/1165trials。需要时再读。
> 📦 [10:44] R1965 流水已归档 → daily-memories-harness/2026-11-09.md。结论：gateway RECOVERED·predict 2685/3500 real=1040·TB-2.1 123passed。需要时再读。
> 📦 [11:09] R1964 + [10:34] R1963 流水已归档 → daily-memories-harness/2026-11-09.md。结论：R1964 gateway 429持续+predict 2680/3500·R1963 TB4→TB-2.1切换确认+oracle5/5+123p。需要时再读。
> 📦 R1958-R1962 流水(09:25~10:15,监控+三报告更新+gateway 429发现)已归档 → daily-memories-harness/2026-11-09.md。**关键**:gateway 429 QUOTA_EXHAUSTED首次出现在R1962·predict 2680/3500·TB-2.1 123p。需要时再读。

> 📦 R1885-R1957 流水(2026-11-08,~30轮监控+incr_eval+TB-2.1+双报告更新)已 bulk 归档 → daily-memories-harness/2026-11-08.md。**关键**:gateway 429反复→200恢复·predict 1561→2061/3500·real 662→790·TB-2.1 62→69p·codex TB-2.1 84err=适配器(wire_api)·deepseek proxy修复。需要时再读。

> 📦 R1788-R1884 流水(2026-11-07~08,incr_eval全量+TB-2.1 7路全交付+双报告R1785-R1820)已 bulk 归档 → daily-memories-harness/2026-11-07.md。**关键里程碑**:SWE-bench eval 7/7全done·cline356/opencode401·TB-2.1 cline 89/89DONE 7pass·hermes 89/89DONE 5pass·§15:2x判据MET✅。需要时再读。

> 📦 R1612-R1787 流水(2026-11-05~07,~50轮 incr_eval/监控/TB4/quiet)已 bulk 归档 → daily-memories-harness/2026-11-05/06/07.md。**关键**:cline rerun 356/500=71.3%·deepseek→212·kimi全7路100%·TB4全量66×7·R1685 cline低分归因(86%能力差)·R1695 proxy修复。需要时再读。

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
