# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2368 incr_eval4new(+3resolved+1infra)+双报告REGEN(gateway 200·eval 1794/2221·0empty·predict 4/7 alive·cline317·cc316·pi280·codex134·TB-2.1=已交付/SWE-bench Verified=~15天瓶颈codex)
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2368·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2367 incr_eval+监控+报告+ETA+cline根因修复·R2368 incr_eval4new(+3resolved+1infra)+双报告REGEN
当前动作:     R2368: 自检(CPU/mem OK·load39/224·无runaway)·gateway 200·incr_eval 4new(cc+4:django-13810RESOLVED+django-13820RESOLVED+django-13821RESOLVED+django-13837infra)→+3resolved+1infra·eval 1794/2221·0empty·predict:cline317r·codex134r·cc316r·pi280r·4/7 alive·**0empty all harnesses**·双报告REGEN(R2368 13:22)·未完成指令:有(§10:10+§22:4x)·W:0
下一步:       ①本轮commit+push ②cline predict继续向500推进(317→500) ③continue incr_eval ④codex=瓶颈134/500@25/天≈15天 ⑤各路满500后§22:4x两基准7路全交付 ⑥TB-2.1已交付
阻塞:         <各路尚未满500:cline317/codex134/cc316/pi280·§22:4x未全交付·opencode+dsh+hermes DONE·codex=瓶颈~15天>
ERROR_COUNT:  0
 体积: TASK=22KB / MEMORY=14KB
  cline专项小结: predict_glm53=317real/241resolved/0empty(全real·C3 fix确认有效·silent exit根因已修R2360·正确PRED_SUBDIR R2361+)·C1:317real·C2:failed=78(能力·real patch但tests fail)·C3:empty=0(已修·非resume bug·是build bug)·C4:241res/320eval=75.3%·C5:报告R2368(cline special·8699B)·失败top1=能力差(real patch但tests fail)·cc267/325=82.2%·opencode414/498=83.1%·gap=能力差

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> [13:22] R2368: incr_eval4new(+3resolved+1infra)轮·自检(CPU/mem OK·load39/224·无runaway)·gateway 200·incr_eval 4new(cc+4:django-13810RESOLVED+django-13820RESOLVED+django-13821RESOLVED+django-13837infra)→+3resolved+1infra·eval 1794/2221·0empty·predict:cline317r·codex134r·cc316r·pi280r·4/7 alive·**0empty all harnesses**·双报告REGEN(R2368 13:22)·未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2367 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2367 incr_eval7new(+6resolved)+cleanup2empty+双报告REGEN。需要时再读。
> 📦 R2365 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2365 monitor+cleanup1empty(eval不变1777/2199)。需要时再读。
> 📦 R2364 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2364 incr_eval5new+5resolved+cleanup4empty+双报告REGEN。需要时再读。
> 📦 R2363 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2363 incr_eval3new+3resolved+cleanup1empty+双报告REGEN。需要时再读。
> 📦 R2362 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2362 incr_eval3new+3resolved+cleanup3empty+双报告REGEN。需要时再读。
> 📦 R2361 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2361 incr_eval5new+2resolved+cline-patched RESTART(predictions_glm53)+cleanup1empty+kill2stuck容器+双报告REGEN。需要时再读。
> 📦 R2360 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2360 cline silent exit根因修复(skills@1.7.2+build:sdk)+cleanup132empty+pi+2resolved+双报告REGEN。需要时再读。
> 📦 R2359 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2359 监控(0new eval+68empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2358 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2358 监控(0new eval+19empty cleanup+cline+cc predict RESTARTED)+双报告REGEN。需要时再读。
> 📦 R2357 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2357 监控(0new eval+7empty cleanup+cline+cc predict DIED)+双报告REGEN。需要时再读。
> 📦 R2356 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2356 监控(0new eval+10empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2355 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2355 监控(0new eval+89empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2354 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2354 监控(0new eval+77empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2353 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2353 监控(0new eval+13empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2352 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2352 监控(0new eval+9empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2351 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2351 监控(0new eval+17empty cleanup+codex predict RESTARTED)+双报告REGEN+research日报11-13已读。需要时再读。
> 📦 R2350 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2350 监控(0new eval+10empty cleanup+1 runaway pytest 488GB KILL)+双报告REGEN。需要时再读。
> 📦 R2349 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2349 监控(0new eval+5empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2348 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2348 监控(0new eval+7empty cleanup)+双报告REGEN。需要时再读。
> 📦 R2347 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2347 监控(0new eval+0cleanup)+双报告REGEN。需要时再读。
> 📦 R2346 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2346 监控(0new eval)+cleanup(23empty:3codex+20cc)+双报告REGEN。需要时再读。
> 📦 R2345 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2345 incr_eval(4new:4resolved)+cleanup(1empty)+双报告REGEN。需要时再读。
> 📦 R2344 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2344 incr_eval(1new:codex sympy-20801 RESOLVED)+cleanup(1empty)+双报告REGEN。需要时再读。
> 📦 R2343 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2343 incr_eval(1new:pi sphinx-7757 RESOLVED)+双报告REGEN。需要时再读。
> 📦 R2342 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2342 incr_eval(4new:3resolved+1infra)+cleanup(3empty)+双报告REGEN。需要时再读。
> 📦 R2341 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2341 监控(0new+0cleanup·eval不变1753/2167)+双报告REGEN。需要时再读。
> 📦 R2340 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2340 incr_eval(1new+1resolved:cc sphinx-7985)+双报告REGEN。需要时再读。
> 📦 R2339 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2339 监控(0new+0cleanup·eval不变1752/2166)。需要时再读。
> 📦 R2338 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2338 incr_eval(1new+1resolved)+cleanup(2empty)+双报告REGEN。需要时再读。
> 📦 R2337 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2337 incr_eval(2new+2resolved:cc sphinx-7889+7910)+双报告REGEN。需要时再读。
> 📦 R2336 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2336 incr_eval(5new+4resolved)+cleanup(2empty)+双报告REGEN。需要时再读。
> 📦 R2334 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2334 incr_eval 1new(cline django-14034 FAILED)+cleanup 0empty+双报告REGEN。需要时再读。
> 📦 R2333 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2333 监控(0new real·cleanup13empty·cc resolved_count stale FIX)+双报告REGEN。需要时再读。
> 📦 R2332 流水已归档 → daily-memories-harness/2026-11-13.md。结论：R2332 监控(0new real·cleanup12empty·gateway 200)+双报告REGEN。需要时再读。
> 📦 R2305-R2331 流水(2026-11-13,~27轮监控+cleanup+incr_eval+双报告REGEN+CPU runaway处理)已归档 → daily-memories-harness/2026-11-13.md。需要时再读。
> 📦 R2252-R2304 流水(2026-11-12~13,gateway 429↔200反复+incr_eval多路catch up+cleanup空patch+双报告REGEN)已归档 → daily-memories-harness/2026-11-12.md / 2026-11-13.md。需要时再读。
> 📦 R2163-R2251 流水(2026-11-11~12,gateway 429↔200反复+incr_eval+cleanup+predict推进+双报告REGEN+opencode满500)已归档 → daily-memories-harness/2026-11-11.md / 2026-11-12.md。需要时再读。

> 📦 [08:49] R2162 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 11NEW(+7resolved→1347)+cleanup 2empty+双报告REGENERATED(R2162)。需要时再读。

> 📦 [08:33] R2161 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway RECOVERED(200)+TB-2.1 opencode rerun COMPLETED(33pass)+cleanup 12empty+incr_eval 0NEW(1340resolved不变)+双报告REGEN(R2161)。需要时再读。

> 📦 R2148-R2160 流水(2026-11-11,~13轮监控+gateway 429→200恢复+codex predict RESTARTED+cleanup多次+TB-2.1 opencode rerun)已归档 → daily-memories-harness/2026-11-11.md。需要时再读。

> 📦 R1958-R2152 流水(2026-11-09~11,gateway 429反复+incr_eval+TB-2.1+双报告+多次CPU KILL)已 bulk 归档 → daily-memories-harness/2026-11-09.md / 2026-11-10.md / 2026-11-11.md。需要时再读。

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
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（同一 NFS · git pull 后各线共享）
- **SWE-bench Verified 预测**：`run/harness/swebench_verified_full/predictions_glm53/`
- **SWE-bench Verified 评测**：`run/harness/swebench_verified_full/reports/eval_glm53_*.json`
- **双报告**：`reports/report_harness_glm53_7way_swebench_tb_zh.html` + `reports/report_harness_cline_special_zh.html`
- **报告生成器**：`run/harness/gen_report_glm53_7way.py` + `run/harness/gen_cline_special.py`