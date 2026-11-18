# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0
> 🆕 **R2706 · 2026-11-18 23:4x — 监控轮·MM容器301/580(51.9%)·0新incr_eval·cumulative不变**·心跳第一行: SWE-bench Verified 7路 cumulative(不变): **hermes444/500=88.8%**·**opencode415/500=83.0%**·**claude-code292/500=58.4%**·**cline275/500=55.0%**·**pi227/500=45.4%**·**deepseek153/500=30.6%**·**codex98/500=19.6%**·📦 监控轮: 0 unevaluated real-patch(predict进程仍在处理当前instance·无新real-patch落盘)→无incr_eval·cumulative Pass%不变·📦 **SWE-bench Multimodal容器下载**(用户令11-18): **301/580 pulled=51.9%**(0 FAILED✅)·pull_all_images.sh alive(PID 3749136·NI=19)·正在pull #302(carbon-design-system__carbon-12384)·每image≈6min·剩余279≈28h·predict 5/7 alive(cline382/codex194/cc392/pi331/dsh206·opencode+hermes COMPLETE 500/500)·0 429✅·**自检**: load41.75/224≈18.6%busy·无proc>8000%✅·无RSS>50GB✅·pretrain 8GPU不受影响✅·**全部运维令✅已交付**·research日报11-18已读·WAITING=0·📦 TASK≈30.2KB MEMORY≈10.2KB(✅≤32KB)
> 📦 R2705 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器300/580·2 real-patch跨2路(deepseek django-12774+pi django-12858)全RESOLVED✅·FALSE INFRA路径bug复发已手动修正·7way报告REGEN(15506B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2704 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器298/580·1 real-patch(cline django-15957)FAILED(ability·patch applied but tests fail)·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2703 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器295/580·1 real-patch(codex django-13109)RESOLVED+5 empty-patch merge→failed·FALSE INFRA路径bug复发已手动修正·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2702 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器293/580·3 real-patch跨2路(pi1+dsh2)全RESOLVED·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2701 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮+FALSE INFRA路径bug修复·MM容器290/580·5 real-patch跨2路全RESOLVED+codex/dsh empty→failed·fix_r2701_eval_path.py修正5题误标infra·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2700 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器286/580·predict 5路alive·0新incr_eval·cumulative不变·自检clean）。需要时再读。
> 📦 R2699 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器283/580·predict 5路alive·0新incr_eval·cumulative不变·自检clean）。需要时再读。
> 📦 R2698 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮+FALSE INFRA修复·MM容器281/580·7 real-patch跨3路eval: cline5全RESOLVED+pi1 FAILED+dsh1 RESOLVED·fix_false_infra_R2698.py交叉校验修正7题误标infra·incr_eval模板已修·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2697 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器243/580·predict cline+1(django-15380)·无incr_eval(1新real-patch不足阈值)·cumulative不变·自检clean）。需要时再读。
> 📦 R2696 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载225/580·cline django-15375 RESOLVED·hermes infra修正 django-14631/14725 从infra→failed(能力·patch-apply-fail)·hermes infra 2→0·7way报告REGEN(18730B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2695 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载194/580·3 real-patch跨3路eval全FAILED(能力)·path bug致3题误标infra→fix_r2695修正为failed·75 empty-patch merge入failed·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2694 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载167/580·7 instances 4 routes·cline django-15268+15277 RESOLVED·cc django-14500 RESOLVED·pi django-11820 FAILED·hermes 14631/14725 infra第5次·deepseek django-12304 RESOLVED·7way报告REGEN(18741B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2693 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载133/580·3 instances 3 routes·cc django-14434 RESOLVED·deepseek django-12276 RESOLVED·hermes 14631/14725 infra第4次·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2692 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载117/580·4 instances 3 routes·+1 RESOLVED(pi django-11749)+2 FAILED+2 infra(hermes 14631/14725 第3次)·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2691 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载104/580·6 instances 4 routes·+4 RESOLVED+0 FAILED+2 infra·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2690 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载90/580·10 instances 6 routes·+7 RESOLVED+1 FAILED+2 infra·cline django-14725 race-fix·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2689 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·dedup修正+MM容器下载56/580·3 instances·dsh django-11603 RESOLVED·hermes 2 infra仍NO report.json·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2688 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载42/580·11 instances 6 routes·+6 RESOLVED+3 FAILED+2 infra·CPU_SPIRAL_SKIP added·pi infra dedup·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2687 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器下载31/580·predict 5路alive·无incr_eval·自检clean·research日报已读）。需要时再读。
> 📦 R2685 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·5 instances 4 routes·+2 RESOLVED+0 FAILED+3 infra·7way报告REGEN·SWE-bench Multimodal容器下载17/580·scikit-learn CPU kill）。需要时再读。
> 📦 R2684 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·8 instances 5 routes·+5 RESOLVED+0 FAILED+3 infra·7way报告REGEN·SWE-bench Multimodal容器下载启动6/580·scikit-learn CPU kill）。需要时再读。
> 📦 R2683及更早(R2683~R2481, Gen7 pilot, R474-R477) 流水已归档 → daily-memories-harness/2026-11-14~18.md + 2026-10-24~28.md。需要时再读。

## 📊 进度快照

PHASE:        R2706 监控轮·SWE-bench Multimodal容器下载301/580(51.9%)+Verified predict 5路alive·0新incr_eval
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·10:3x ability桶拆两层✅·SWE-bench predict 7路resume LAUNCHED(R2665)·opencode 500/500 COMPLETE+eval 415/500=83.0%✅·hermes 500/500 COMPLETE+eval 444/500=88.8%✅·incr_eval R2680~R2705 DONE·**SWE-bench Multimodal容器下载进行中**(580 images·sequential nice19/ionice3·301/580 pulled=51.9%·0 FAILED)·CPU_SPIRAL_SKIP added(sklearn-14710)·FALSE INFRA路径bug已修(R2701·fix_r2701_eval_path.py·R2705手动修正deepseek)
当前动作:     R2706: 监控轮·0 unevaluated real-patch→无incr_eval·cumulative Pass%不变·MM容器下载301/580(PID 3749136 alive·NI=19·0 FAILED·正在pull #302)·predict 5路alive(cline382/codex194/cc392/pi331/dsh206)·自检clean(load41.75/224≈18.6%busy·无本线proc>8000%CPU·无RSS>50GB·pretrain 8GPU不受影响)
下一步:       继续监控MM容器下载(301/580)+5路predict·新real-patch落盘后跑incr_eval→刷新7way报告·Multimodal下载完成后准备MM评测
阻塞:         无
ERROR_COUNT:  0
 体积: TASK≈30.2KB / MEMORY≈10.2KB（✅≤32KB）
 SWE-bench Verified Pass%(cumulative resolved/500, after R2706): hermes444=88.8%·opencode415=83.0%·cc292=58.4%·cline275=55.0%·pi227=45.4%·dsh153=30.6%·codex98=19.6%·(partial·predict still running for 5 routes)
 真实 Pass% (layer-A/B 拆分后, 分母=89): cline 42/89=47.2%[真38/超8/环1|47.2~57.3%] · codex 25/89=28.1%[真59/超3/环1|28.1~32.6%] · opencode 45/89=50.6%[真31/超1/环8|50.6~60.7%] · cc 30/89=33.7%[真51/超0/环8|33.7~42.7%] · pi 35/89=39.3%[真48/超1/环5|39.3~46.1%] · hermes 41/89=46.1%[真27/超2/环19|46.1~69.7%] · deepseek 11/89=12.4%[真41/超0/环36|12.4~52.8%] · layer-B=93题(66确认infra+9 ability_lean+18 ambiguous)
  SWE-bench Multimodal容器下载(用户令11-18): pull_all_images.sh·swebench_mm/pull_progress.log·swebench_mm/pull_state.txt·580 images total·301 pulled(0 FAILED)·nice19/ionice3·不抢.29 CPU✅
  research日报11-18 harness建议: ①artifact-based judging(exit code只做旁证·产物存在性+空跑记0·arxiv 2611.21407) ②provider binding检查(同名工具不同来源·arxiv 2611.21577) → 纳入未来计划
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