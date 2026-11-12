# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2335 监控+cleanup轮(gateway 200·incr_eval 0new real·cleanup 6empty deleted·eval 1744/2157·predict 4/7 alive·TB-2.1=已交付/SWE-bench Verified=~15天瓶颈codex)
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2335·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2334 incr_eval+监控+报告+ETA·R2335 incr_eval(0new real)+cleanup(6empty deleted)+双报告REGEN
当前动作:     R2335: 自检PASS(load41/224~18%·无harness>8000%·MEM avail1070G)·gateway 200(0.12s)·incr_eval 0new real(全caught up·pi sphinx-11445=empty patch已删)·cleanup 6empty deleted(cline1·codex2·cc2·pi1→待re-predict)·eval cumulative不变:cline231/306·codex87/136·opencode414/498·cc241/295·pi195/267·hermes435/480·dsh141/175·总1744/2157·predict files post-cleanup:cline303·codex129·cc292·pi267·predict 4/7 alive(cline→django-14053·codex→sympy-19783·cc→sphinx-7757·pi→sphinx-11510·opencode498DONE·hermes480DONE·dsh175DONE)·磁盘OK(/data 5.8T 18%·/ 351G 4%)·双报告REGEN(R2335·7way 12201B·cline special 9973B)·未完成指令:有(§10:10+§22:4x)·W:0
下一步:       ①本轮commit+push ②下轮continue incr_eval+cleanup(predict flowing·6empty待re-predict) ③predict 4/7向500推进(codex=瓶颈129/500@25/天≈15天·cc292·pi267·cline303) ④各路满500后§22:4x两基准7路全交付 ⑤TB-2.1已交付
阻塞:         <各路尚未满500:cline303/codex129/cc292/pi267·hermes480近满·§22:4x未全交付·opencode+dsh DONE·codex=瓶颈~15天>
ERROR_COUNT:  0
 体积: TASK=22KB / MEMORY=9KB(归档后·大幅瘦身)
  cline专项小结: predict_glm53=303real/231resolved/0empty(running django-14053·C3 resume fix R1733仍有效)·C1:303real·C2:failed=能力(real patch但tests fail)+infra0·C3:empty=0·C4:231res/303real=76.2%·C5:报告R2335(cline special·231/303·9973B)·失败top1=能力差(real patch但tests fail)·opencode414/498=83.1%·gap=能力差

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> [05:5x] R2335: 监控+cleanup轮·自检PASS(load41/224~18%·无harness>8000%·MEM avail1070G)·gateway 200(0.12s)·incr_eval 0new real(全caught up·pi sphinx-11445=empty patch已删)·cleanup 6empty deleted(cline1·codex2·cc2·pi1→待re-predict)·eval cumulative不变:cline231/306·codex87/136·opencode414/498·cc241/295·pi195/267·hermes435/480·dsh141/175·总1744/2157·predict files post-cleanup:cline303·codex129·cc292·pi267·predict 4/7 alive(cline→django-14053·codex→sympy-19783·cc→sphinx-7757·pi→sphinx-11510·opencode498DONE·hermes480DONE·dsh175DONE)·磁盘OK(/data 5.8T 18%·/ 351G 4%)·双报告REGEN(R2335·7way 12201B·cline special 9973B)·未完成指令:有(§10:10+§22:4x)·W:0
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