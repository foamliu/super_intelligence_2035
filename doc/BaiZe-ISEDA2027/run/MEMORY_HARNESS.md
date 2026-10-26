# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        H-A SWE-bench Verified 就绪核查完成(R518)+R519/R520活性复检确认状态未退化; 等运维拍板20条试点; 运维指令区无未完成指令.
已完成:       H-B ctx压缩报告✅·Gate7/7✅(R466)·7x89并发✅(R479)·R496全7路FIN87/87✅+McNemar✅·R499/R510 codex err✅·R509/R516报告✅·R517归档✅·R518 H-A Verified就绪核查报告✅(11323B,8节,13项全溯源)·R519活性复检✅·R520防判死心跳✅(归档R507-R517)
当前动作:     R520 防判死心跳(R519后~68min>60min阈值). liveness 5项实测全通过:①swebench500/500(不变)②pretrain loop在.29 PID1401353 etimes~53.7h需避让③load10.33/224(~4.6%)④/data6.0T free⑤ops/inbox RUN_ID219-221均pretrain线无harness新指令. 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效.
下一步:       ①等运维拍板20条Verified试点(先cline+hermes smoke 1条→20条→报初步结果→放大决策); ②codex全量补跑待运维拍板; ③H-B续作(机制维度扩展)
阻塞:         无未完成运维指令. H-A Verified试点待运维拍板(就绪报告R518已交付+R519/R520复检确认状态未退化,§3先报预算再跑).
ERROR_COUNT:  0
📦 体积：TASK=26994B(26KB) / MEMORY=见收尾(≤32KB✓,本轮归档R507-R517→daily 10-26)
```

### Gen7 pilot 最终结果(7×5=35 trials)
| Harness | Pass Rate | Errors | Notes |
|:--|:--|:--|:--|
| cline-patched | 5/5 (100%) | 0 | ✅ Perfect |
| pi | 5/5 (100%) | 0 | ✅ Perfect |
| codex (rerun) | 3/5 (60%) | 0 | ✅ config.toml fix worked |
| opencode | 3/5 (60%) | 1/5 | ⚠️ 1 AgentTimeoutError |
| hermes | 0/5 (0%) | 0 | Genuine 0% (no errors) |
| deepseek-harness | 0/5 (0%) | 0 | Genuine 0% (no errors) |
| claude-code (rerun3) | 0/5 (0%) | 3/5 | 🔴 1 RuntimeError(exit1)+2 AgentTimeoutError |

### Oracle check (15 tasks, R473)
- 15/15 completed, mean reward 0.733 (11/15 solvable by oracle)
- Failed by oracle: build-pmars, caffe-cifar-10(AgentTimeoutError), configure-git-webserver, git-multibranch

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[01:0x] R520 **防判死心跳(R519后~68min>60min阈值)**. ops/inbox RUN_ID219-221均pretrain线,无harness新指令. liveness 5项实测全通过(swebench500/500不变·pretrain PID1401353 etimes~53.7h需避让·load10.33/224·/data6.0T free·last commit R519@23:58). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1. 体积:TASK=26994B/MEMORY见收尾(归档R507-R517→daily 10-26,均≤32KB).
[23:5x] R519 **就绪状态活性复检(R518交付后~70min)**. 运维指令区顶部3条全[已归档],ops/inbox RUN_ID219-221均pretrain线,无harness新指令. 8项实测全通过(swebench500/500·gateway HTTP200 0.018s·pull 500/500·image_list 500·/data 6.0T free·load 9.35/224·pretrain loop在.29 PID1401353需避让·last commit R518@22:47). 结论:R518就绪状态未退化,运维待批20条Verified试点决策仍有效. **判据自检**:无未完成运维指令→WAITING=1(等运维拍板,§3先报预算再跑). 体积:TASK=26994B/MEMORY见收尾(均≤32KB).
[22:4x] R518 **H-A SWE-bench Verified 横评就绪核查(§1.2先20-50条/§3先报预算再跑)**. 实测13项:①docker镜像500/500在盘(sg docker -c 'docker images|grep swebench|sort -u|wc -l'=500,样本swebench/sweb.eval.x86_64.sympy_1776_sympy-24213:latest) ②下载DONE(progress.txt:514 DONE 2026-10-26 18:23:06 total=500 pulled=500 failed=0) ③sg docker可访问(610张镜像,本用户经sg docker切组) ④swebench v5.0.2 ⑤gateway /models HTTP200 0.02s ⑥Verified数据集带proxy可加载500题(首题astropy__astropy-12907与image_list.txt一致) ⑦image_list.txt 500行 ⑧/data 6.0T free ⑨load 7.52/224CPU ⑩pretrain loop在.29(避让) ⑪unshare rootfs仅13个(不适用500题) ⑫run_evaluation v5.0.2改名(需适配,r1_eval.py的make_test_spec/get_eval_report可用) ⑬直连gateway dummy key返回空(预期,真实key在gw_proxy). 评测路径选定**docker官方harness**. 产 gen_report_swebench_verified_readiness.py + report_swebench_verified_readiness_zh.html(11323B,8节,0script/0外链/0cline-patched,数字全溯源). 结论:就绪可启动20条试点(先cline+hermes smoke),需运维拍板+并发限制. **判据自检**:运维指令区顶部全为[已归档]指针,无未完成指令→WAITING=1(等运维拍板试点). 体积:TASK=26994B/MEMORY见收尾实测.

> 📦 R507-R517+R485-R506 长流水原文已归档 → daily-memories-harness/2026-10-26.md（结论：R517归档bookkeeping+报告复核;R509近期工作报告交付;R508/R507复跑进度刷新+3件deliverable;R502-R506复跑进度;R497-R500审计核验+复跑监控;R492-R496全7路FIN87/87+McNemar+适配器修复smoke;R485-R488双线并列监控TB+SWE-bench下载）。需要时再读。
> 📦 R460-R469 (2026-10-23~24, H-B报告完成+Gen7 pilot+codex/claude-code infra fix+rerun) 已归档 → daily-memories-harness/2026-10-23.md + 2026-10-24.md。结论：H-B报告58KB已push, Gen7 pilot 5/7(cline+pi=100%,opencode=60%), codex 0.164.0 API兼容性修复(config.toml), claude-code NFS perms修复(chmod755). 需要时再读。

> 📦 R431-R447 (2026-10-18~19, TB pilot Gen2-Gen3 + Docker blockers + relay checks, ~20 rounds) 已归档 → daily-memories-harness/2026-10-18.md + 2026-10-19.md。结论：Docker 只在 .29 可用, pilot Gen3 1/7→gw_proxy 修复→逐路定根因→Gen5 7/7 完。需要时再读。

> 📦 R352-R430 (2026-10-13~18, glm53 7×300 监控/修复/报告 + TB T2 前置 + Docker networking, ~60 rounds) 已归档 → daily-memories-harness/2026-10-13.md ~ 2026-10-18.md。结论：glm53 7×300 2100/2100 完成, SWEBENCH_COMPARE 报告交付, TB T2 Docker networking 突破。需要时再读。

> 📦 R113-R351 (2026-10-04~13, SWE-bench 7×300 pipeline 建立 + 早期 harness 横评, ~100 rounds) 已归档 → daily-memories-harness/2026-10-04.md ~ 2026-10-13.md。结论：SWE-bench pipeline 打通, R1 unshare 沙箱可行, 早期 5-way/7-way 横评完成。需要时再读。

> 📦 §P1/FIX2 (2026-10-13) 已归档 → run/ARCHIVE_OPERATOR_HARNESS.md。结论：P1-2 rerun DONE, fix2 32 条重评 9 FLIPPED, kimi 574→621 resolved。需要时再读。

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

> 📦 R35-R459 流水条目（2026-10-02~20, H-B 源码分析 + H-A SWE-bench 7×300 + TB pilot Gen2-Gen5, ~400 rounds）已归档 → daily-memories-harness/2026-10-02.md ~ 2026-10-20.md。需要时再读。最新流水见上方「本唤醒流水」。
