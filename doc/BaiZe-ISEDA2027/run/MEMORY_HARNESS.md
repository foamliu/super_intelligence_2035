# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2208 incr_eval DONE(+5resolved)+自检PASS+gateway 200 OK+双报告REGEN+hermes predict RESTARTED+心跳
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2208·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2208 incr_eval+监控+报告·R2208 incr_eval DONE(7inst+5resolved+1failed+1infra)+hermes predict RESTARTED+自检PASS
当前动作:     R2208: 自检PASS(CPU load44/224~20%·无harness>8000%·最高cline-patched 48%=0.5核·MEM 784G/2Ti avail1.1Ti·harness全<6.5GB)+gateway 200 OK(/v1/models=200·0.02s·stable)+incr_eval R2208 DONE(7inst·cline+3RESOLVED+1FAILED(11578/12585/13124 RESOLVED·12973 FAILED)·cc+2RESOLVED(14631/14672)·pi+1RESOLVED(14238)·+5resolved+1failed+1infra)+5/7 predict ALIVE(cline283f/243r·codex193f/108r·opencode500f/495r DONE·cc321f/224r·pi249f/212r·hermes450f/413r RESTARTED PID2677820·dsh176f/175r DEAD·5 predict procs alive)+predict advancing(2172files·1870real/3500=53.4%real·+4files+4real since R2207)+eval pass(cline185/248=74.6%·codex72/108=66.7%·opencode408/495=82.4%·cc180/226=79.6%·pi157/214=73.4%·hermes370/413=89.6%·dsh141/175=80.6%)+总resolved=1513(↑10)+cline C4(283f/243r/185res/62fail/40empty·pass74.6%·失败top1=能力差)+TB-2.1(cline10/89·codex1/89·opencode35/117·cc0/89·pi36/178·hermes7/89·dsh11/89)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2208(7way 10294B/cline special 7661B·0外链)+hermes predict RESTARTED(R2208·PID2677820·resume[59/500]·gw_proxy9092=200)+dsh silent-exit确定性bug(不重启)+research日报11-11已查(advice=trace回填列·ETA 2-3天·非新指令)·W:0
下一步:       ①本轮commit MEMORY+双报告+push ②下一轮incr_eval R2209(gateway 200→hermes predict产新real patch→eval backlog) ③predict向500推进(5路alive·opencode已满500·hermes RESTARTED向500推进·cc321·pi249·cline283·codex193远) ④各路满500后§22:4x两基准7路全交付 ⑤dsh不重启(silent-exit确定性·fix需dsh binary/SDK) ⑥hermes predict RESTARTED已确认alive(下轮验证产新file) ⑦research日报11-11 advice(报告加trace回填列·ETA 2-3天)纳入下轮参考 ⑧TB-2.1推进 ⑨后续incr_eval脚本须用修复后parser(inst_rep=rd.get(iid,rd))
阻塞:         <hermes predict RESTARTED(450f·PID2677820 alive·需下轮验证产新file)·各路尚未满500(2172files/1870real·/3500=53.4%real·opencode已满500)·§22:4x未全交付·dsh silent-exit=dsh binary确定性bug(非crash·非gateway)·incr_eval R2208已完成无后台进程>
ERROR_COUNT:  0
 体积: TASK=20.6KB / MEMORY=~27.7KB(均<32KB)
 cline专项小结: predict_glm53=283files/243real/185resolved/62failed/40empty(全429quota历史·infra=1·非resume bug·C3 resume fix R1733仍有效)·C1:243real/283total(可复算:ls predictions_glm53/cline-patched__*.json|wc -l→283)·C2:62failed=100%能力差(infra=1·13124初始NO report后RESOLVED)·C3:empty=40(429quota历史·非归零·归因红线区分)·C5:报告R2208 current(cline special 7661B·185/248=74.6%)·失败top1=能力差(real patch但tests fail)·opencode408/495=82.4%·gap7.8%=能力差

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> [23:43] R2207: 自检PASS(CPU load37.6/224~17%·无harness>8000%·MEM 785G/2Ti avail1.1Ti·harness全<6.5GB)+gateway 200 OK(/v1/models=200·0.02s·stable·recovered from R2204-R2206 429)+incr_eval R2207 DONE(6inst·cline scikit-learn-11310 RESOLVED·codex django-14034 FAILED·cc django-14608 RESOLVED·hermes sympy-24539/24562/24661 ALL 3 RESOLVED·+5resolved+1failed·总resolved 1498→1503)+4/7 predict ALIVE(cline281f/241r·codex193f/108r·opencode500f/495r DONE·cc319f/222r·pi249f/212r·hermes450f/413r DIED·dsh176f/175r DEAD·4 predict procs alive)+predict advancing(2168files·1866real/3500=53.3%real·+16files+7real since R2206)+eval pass(cline180/240=75.0%·codex72/108=66.7%·opencode408/495=82.4%·cc177/222=79.7%·pi155/212=73.1%·hermes370/413=89.6%·dsh141/175=80.6%)+cline C4(281f/241r/180res/60fail/40empty·pass75.0%·失败top1=能力差)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2207(7way 10294B/cline special 7661B·0外链)+hermes predict DIED(450f·需下轮诊断)+dsh silent-exit确定性bug(不重启)+research日报11-11已查(advice=trace回填列·ETA 2-3天·非新指令)·未完成指令:有(§10:10+§22:4x)·W:0

> [23:59] R2208: 自检PASS(CPU load44/224~20%·无harness>8000%·最高cline-patched 48%=0.5核·MEM 784G/2Ti avail1.1Ti·harness全<6.5GB)+gateway 200 OK(/v1/models=200·0.02s·stable)+incr_eval R2208 DONE(7inst·cline scikit-learn-11578/12585/13124 RESOLVED·12973 FAILED·cc django-14631/14672 RESOLVED·pi django-14238 RESOLVED·+5resolved+1failed+1infra·总resolved 1503→1513)+5/7 predict ALIVE(cline283f/243r·codex193f/108r·opencode500f/495r DONE·cc321f/224r·pi249f/212r·hermes450f/413r RESTARTED PID2677820·dsh176f/175r DEAD·5 predict procs alive)+predict advancing(2172files·1870real/3500=53.4%real·+4files+4real since R2207)+eval pass(cline185/248=74.6%·codex72/108=66.7%·opencode408/495=82.4%·cc180/226=79.6%·pi157/214=73.4%·hermes370/413=89.6%·dsh141/175=80.6%)+cline C4(283f/243r/185res/62fail/40empty·pass74.6%·失败top1=能力差)+TB-2.1(cline10/89·codex1/89·opencode35/117·cc0/89·pi36/178·hermes7/89·dsh11/89)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2208(7way 10294B/cline special 7661B·0外链)+hermes predict RESTARTED(R2208·PID2677820·resume[59/500]·gw_proxy9092=200·原log predict_hermes_glm53.log仅6行=Nov7原始启动·死因=未知·进程消失无core)+dsh silent-exit确定性bug(不重启)+research日报11-11已查(advice=trace回填列·ETA 2-3天·非新指令)·未完成指令:有(§10:10+§22:4x)·W:0

> 📦 R2203-R2206 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429↔200反复(quota周期性耗尽)·incr_eval 0new(eval caught up·1498resolved)·predict 2112→2152files/1859real·opencode满500·cline C4 pass74.9%稳定。需要时再读。

> 📦 R2190-R2191 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval +5resolved(1444→1446)·predict 1820→1823real·opencode满500·双报告REGEN·dsh DEAD。需要时再读。

> 📦 R2192-R2202 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429↔200反复·incr_eval catch up(eval 1450→1498·+48)·predict 1828→2126files/1859real·opencode满500·R2193发现并修复incr_eval parser bug(inst_rep=rd.get(iid,rd))·双报告REGEN。需要时再读。
> 📦 R2184-R2191 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval 累计+19resolved(1420→1446)·predict 1799→1823real·opencode满500·双报告REGEN R2184-R2191·dsh DEAD。需要时再读。
> 📦 R2175-R2183 流水(2026-11-11,incr_eval+监控+双报告+restart stalled routes)已归档 → daily-memories-harness/2026-11-11.md。**关键**:incr_eval多路catch up·hermes +1resolved(sphinx-7985)·total1420·predict 1799real/1927=93.4%·6/7 alive·dsh DEAD(silent-exit)·gateway functional。需要时再读。

> 📦 [09:51] R2165 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+cleanup 4empty+双报告REGENERATED(R2165)。需要时再读。

> 📦 [09:31] R2164 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+0empty(无需cleanup)+双报告REGENERATED(R2164)。需要时再读。

> 📦 [09:14] R2163 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 9NEW(+6resolved→1353)+cleanup 4empty+stuck R2142 container清理+双报告REGENERATED(R2163)。需要时再读。

> 📦 [08:49] R2162 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 11NEW(+7resolved→1347)+cleanup 2empty+双报告REGENERATED(R2162)。需要时再读。

> 📦 [08:33] R2161 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway RECOVERED(200)+TB-2.1 opencode rerun COMPLETED(33pass)+cleanup 12empty+incr_eval 0NEW(1340resolved不变)+双报告REGEN(R2161)。需要时再读。

> 📦 R2148-R2160 流水(2026-11-11,~13轮监控+gateway 429→200恢复+codex predict RESTARTED+cleanup多次+TB-2.1 opencode rerun)已归档 → daily-memories-harness/2026-11-11.md。需要时再读。

> 📦 [06:55] R2152 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA持续+predict 1673real不变+cleanup 14empty(429infra)+incr_eval 0NEW(1340resolved不变)+TB-2.1 opencode 82/89done。需要时再读。

> 📦 [05:48] R2147 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA+incr_eval 2new(+2resolved→1340)+TB-2.1 opencode rerun ALIVE+双报告REGEN R2147。需要时再读。
> 📦 [05:32] R2146 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA+incr_eval 5new ALL resolved(+5→1338)+TB-2.1 opencode rerun ALIVE+双报告REGEN R2146。需要时再读。
> 📦 [05:18] R2145: incr_eval轮·①CPU PASS(load40/224·无harness进程>8000%·最高pcpu=191%=claude-code run_single) ②MEM PASS(761G/2Ti·1.1Ti avail·/data 5.8T) ③gateway 200 RECOVERED(gateway_probe.sh HTTP 200·predict加速·+26files since R2144) ④predict 7路ALIVE:cline220·codex136·opencode449·cc239·pi185·hermes393·dsh175=1815files(+26) ⑤incr_eval R2145 RUNNING:opencode9new DONE(362/443↑9·0infra)·hermes9new launching·deepseek2new pending·eval 1326resolved(↑9·opencode362·hermes332·cline153·cc151·pi135·dsh129·codex64) ⑥TB-2.1 opencode rerun ALIVE(31p/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=异构判官>重复跑(已在7way中) ⑧cline C4:220files/206real/153resolved/14empty·C2失败top1=能力差(real patch but tests fail) ⑨双报告REGEN R2145(glm53_7way 9.0KB+cline_special 6.6KB)·清理3个orphan incr_eval进程(仅保留PID3163523)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [04:56] R2144 流水已归档 → 本文件上半。结论：监控轮·gateway 429·predict +8files·1317resolved UNCHANGED·TB-2.1 opencode rerun ALIVE·MEMORY归档。需要时再读。
> 📦 [04:46] R2143 流水已归档 → 本文件上半。结论：incr_eval R2142 DONE(1317resolved)+TB-2.1 opencode run31p+双报告REGEN+gen_report动态修复+CPU/MEM PASS。需要时再读。
> 📦 [04:17] R2141 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2141(7new·4new resolved)+双报告regen+gateway RECOVERED(429清除)+7路ALIVE(1768files)+TB-2.1 99p。需要时再读。
> 📦 [03:45] R2140 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2140(10new·6new resolved)+双报告regen+gateway 429 QUOTA_EXHAUSTED+7路ALIVE(1728files)+TB-2.1 79p。需要时再读。
> 📦 [02:55] R2138 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2138(pi 2new both failed=能力·0new resolved·全7路eval caught up)+双报告regen+7路ALIVE(1662files)+TB-2.1 79p。需要时再读。
> 📦 R2134-R2137 流水已归档 → daily-memories-harness/2026-11-11.md。结论：R2134 incr_eval(+1resolved)+双报告regen·R2135 CPU KILL(sklearn 180核)+重启3停滞orch→7路ALIVE·R2136 incr_eval(+4resolved→1297)+双报告regen·R2137 opencode eval merge(django-11734→fail)+双报告regen。需要时再读。
> 📦 [01:31] R2133 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1603real(↑5)+incr_eval R2133(1inst·+1resolved)+eval 1292resolved(↑5)+cleanup 1empty(429)+双报告REGENERATED(R2133)+TB-2.1 79p。需要时再读。
> 📦 [01:16] R2132 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1598real(↑9)+incr_eval R2132(6inst·+4resolved)+eval 1287resolved(↑4)+cleanup 3empty(429)+双报告REGENERATED(R2132)+TB-2.1 79p。需要时再读。
> 📦 [01:00] R2131 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1589real(↑3)+incr_eval R2131(3inst·+1resolved)+eval 1283resolved(↑1)+双报告REGENERATED(R2131)+TB-2.1 78p。需要时再读。
> 📦 [00:47] R2130 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1586real(↑7)+cleanup 0empty+incr_eval R2130(11inst·+9resolved)+eval 1282resolved(↑9)+双报告REGENERATED(R2130)+TB-2.1 77p。需要时再读。
> 📦 [00:33] R2129 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1579real(↑9)+cleanup 2empty+incr_eval R2129(4inst)+eval 1273resolved(↑3)+双报告REGENERATED(R2129)+merge_R2129_glm53.py修复deepseek model_dir。需要时再读。
> 📦 [00:15] R2128 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1570real(↑4)+cleanup 1empty+incr_eval R2128(5inst)+eval 1270resolved(↑6)+双报告REGENERATED(R2128)。需要时再读。
> 📦 [00:05] R2127 流水已归档 → daily-memories-harness/2026-11-10.md。结论：gateway 200 STABLE+predict 1566real(↑14)+cleanup 4empty+incr_eval R2127(22inst)+eval 1264resolved(↑22)+双报告REGENERATED(R2127)。需要时再读。
> 📦 [23:25] R2125 流水已归档 → daily-memories-harness/2026-11-10.md。结论：gateway 200 STABLE+predict 1526real(↑9)+cleanup 3empty+incr_eval R2125(28inst)+eval 1234resolved/1502evaluated+TB-2.1 82p/682t+双报告REGENERATED(R2125)。需要时再读。
> 📦 R2013-R2118 流水(2026-11-09~10,~100轮监控+gateway 429反复+incr_eval+TB-2.1+双报告+多次CPU KILL)已 bulk 归档 → daily-memories-harness/2026-11-09.md / 2026-11-10.md。**关键**:gateway 429/QUOTA反复→恢复·predict 1250→1455real·incr_eval多路catch up·TB-2.1 40→85p·cline empty=能力差非429·gen_report动态状态行修复。需要时再读。
> 📦 R1958-R2012 流水(2026-11-09,~25轮监控+gateway 429/QUOTA_EXHAUSTED+incr_eval+TB-2.1)已 bulk 归档 → daily-memories-harness/2026-11-09.md。**关键**:gateway 429反复·QUOTA_EXHAUSTED reset~02:24·predict 2680/3500·TB-2.1 123p·incr_eval 7/7DONE。需要时再读。

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
