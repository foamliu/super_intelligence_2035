# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

## 当前状态
- STAGE: **P-8 正式预训练运行中 🚀**（2026-10-10 16:03 启动）— Mamba2-hybrid 2.22B from scratch, 44B tokens, dist_muon, WSD 5%/85%/10%。
- PHASE: **p8_training** — stable phase (web 88:code 8:math 4) running, step ~40/10490, loss 8.38↓, 0 NaN ✅
- ERROR_COUNT: 0
- 轮询状态：30min 长轮询。**全 8 GPU 占用**（.29, 52-53GB/card, 87-100% util）。PID 3620770-3620777 (8 processes)。📦 体积：TASK ≤32KB / MEMORY ≤32KB 需维护。🚫绝不 kill 训练进程或 watchdog loop
- 🩺 **本唤醒推进 = #268（2026-10-10 16:18, P-8 启动+首 40 步）**：① P-8 训练已启动（16:03:26, setsid 真后台）。② 8 GPU 进程 alive ✅（PID 3620770-3620777, etimes~326s）。③ 首 40 步数据：step10 loss=11.73/grad_norm=12.85/28.2s, step20 loss=9.72/16.9s, step30 loss=8.85/16.8s, step40 loss=8.38/grad_norm=6.23/16.9s。④ 稳态吞吐=248K tok/s（符合预期 249K），ETA≈2.05 天。⑤ 0 NaN / 0 skipped ✅。⑥ GPU 52-53GB/card（80GB 安全），595 TFLOP/s/GPU。⑦ 模型 3.00B params（2.47B transformer + 0.53B embedding）。⑧ **baize_p8_decay.sh 已创建**（SFT 64%+L3 24%+code 8%+math 4%，从 step-9441 ckpt 恢复，WSD decay 1049 步）。⑨ 日志：/tmp/baize_p8_train.log。→ 下一步：每 500 步监控 loss/grad_norm/tok/s；step 9441 时停 stable→起 decay。WAITING=1。
> 📦 **[已归档] #267 流水（2026-10-10 15:14, 状态核查）→ daily-memories/2026-10-10.md；结论：dist_muon已完成, GPU全空闲, P-8暂缓令未撤但数据前置已满足, 无新指令。需要时再读。**
> 📦 **[已归档] #266 流水（2026-10-10 14:40, 状态核查）→ daily-memories/2026-10-10.md；结论：dist_muon已完成, GPU全空闲, P-8数据前置已满足但暂缓令未撤, 无新指令。需要时再读。**
> 📦 **[已归档] #265 流水（2026-10-10 14:07, 状态核查）→ daily-memories/2026-10-10.md；结论：dist_muon已完成, GPU全空闲, P-8暂缓令未撤, 无新指令。需要时再读。**
> 📦 **[已归档] #264 流水（2026-10-10 13:33, 状态核查）→ daily-memories/2026-10-10.md；结论：dist_muon已完成, GPU全空闲, P-8暂缓令未撤, data前置接近完成。需要时再读。**
> 📦 **[已归档] #263 流水（2026-10-10 13:01, 状态核查）→ daily-memories/2026-10-10.md；结论：dist_muon已完成, GPU全空闲, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #262 流水（2026-10-10 12:14, dist_muon 重测+报告刷新）→ daily-memories/2026-10-10.md；结论：dist_muon loss 3.110/122K tok/s/37.3GB, 消除 plain Muon −26%/+38% 两项代价, 报告36.3KB已刷新。需要时再读。**
> 📦 **[已归档] #261 流水（2026-10-10 10:57, 状态核查）→ daily-memories/2026-10-10.md；结论：GPU全空闲, R3分词110/110 DONE, P-8暂缓令未撤, 体积OK。需要时再读。**
> 📦 **[已归档] #260 流水（2026-10-10 10:19, 状态核查+TASK归档）→ daily-memories/2026-10-10.md；结论：两项运维指令均已完成(commit 9fb2c7f8), TASK归档2块→27.9KB。需要时再读。**
> 📦 **[已归档] #259 流水（2026-10-10 09:44, 补推确认+心跳修正）→ daily-memories/2026-10-10.md；结论：9fb2c7f8 已成功推送, 上轮「push失败」更正为「已推送」。需要时再读。**
> 📦 **[已归档] #258 流水（2026-10-10, Muon报告刷新+昨夜汇报+TASK归档）→ daily-memories/2026-10-10.md；结论：两份报告(Muon 28.6KB+昨夜 11.6KB)已生成+commit 9fb2c7f8+push ✅, TASK归档2块。需要时再读。**
> 📦 **[已归档] #257 流水（2026-10-10 08:26, 状态核查）→ daily-memories/2026-10-10.md；结论：GPU全空闲, git 0/0, 两步运维指令均完成, 无需归档。需要时再读。**
> 📦 **[已归档] #254 流水（2026-10-10 06:50, Muon vs AdamW A/B 结果回收+报告+TASK归档）→ daily-memories/2026-10-10.md；结论：Muon loss 3.11 vs AdamW 4.00(−22.3%), 吞吐 87K vs 118K(−26%), VRAM 53.8 vs 39.0GB(+38%), 报告 22.5KB 已 commit f53ec86d+push。需要时再读。**
> 📦 **[已归档] #252 流水（2026-10-10 01:22, P-9.11-F 报告生成）→ daily-memories/2026-10-10.md；结论：DM 1M 数据落地, 报告 v2 生成(23.6KB/5表/SVG), warmup 修正 281×→24.5×, DM 2M 待测。需要时再读。**
> 📦 **[已归档] #251 流水（2026-10-09 19:45, 3个实验idea交付）→ daily-memories/2026-10-09.md；结论：3 idea按价值排序交付(Idea1=P-8彩排续跑), 建议「立即起P-8」。需要时再读。**
> 📦 **[已归档] #249 流水（2026-10-09 18:27, R3报告再确认）→ daily-memories/2026-10-09.md；结论：报告已存在+commit 00682e58+push, 8节/8内联SVG/10表/零外链。需要时再读。**
> 📦 **[已归档] #248 流水（2026-10-09 17:53, R3报告再确认）→ daily-memories/2026-10-09.md；结论：报告已存在+commit 00682e58+push, 8节/8内联SVG/10表/零外链。需要时再读。**
> 📦 **[已归档] #247 流水（2026-10-09 17:18, R3报告确认）→ daily-memories/2026-10-09.md；结论：报告已存在+commit 00682e58+push, 8节/8内联SVG/10表/零外链。需要时再读。**
> 📦 **[已归档] #246 流水（2026-10-09 16:10, R3收官报告生成）→ daily-memories/2026-10-09.md；结论：R3 HTML 报告 52.6KB 已生成+commit 00682e58+push, 8节/8内联SVG/10表/零外链/DB真实数据。需要时再读。**
> 📦 **[已归档] #245 流水（2026-10-09 15:22, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, git ahead 1(已合并), R3分词109进程/.bin=1.76TB/ETA~12-18h, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #244 流水（2026-10-09 14:45, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, git up-to-date, R3分词109进程/.bin=1.49TB/ETA~12-18h, P-8暂缓令未撤, 一并提交TASK.md T3 recipe。需要时再读。**
> 📦 **[已归档] #243 流水（2026-10-09 14:10, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, git up-to-date, R3分词110进程/.bin=1.3TB/ETA~2-4h, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #242 流水（2026-10-09 13:37, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, git up-to-date, R3分词110进程/.bin=989GB/ETA~3-4h, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #241 流水（2026-10-09 13:01, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, git up-to-date, R3分词110进程/.bin=989GB/ETA~3-4h, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #240 流水（2026-10-09 12:28, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, git up-to-date, R3分词110进程/.bin=736GB/ETA~6-8h, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #239 流水（2026-10-09 11:53, 状态核查+T3归档）→ daily-memories/2026-10-09.md；结论：T3运维块已归档(TASK→23.7KB), R3分词24.5%/110进程/.bin=538GB, GPU全空, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #238 流水（2026-10-09 11:11, T3提速验证完成）→ daily-memories/2026-10-09.md；结论：Test1 OOM/recompute无效, Test4 FP8 s=0.915, P-8最优=TP1·MBS2·bf16=249K。需要时再读。**
> 📦 **[已归档] #237 流水（2026-10-09 10:08, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, git up-to-date, GPIC 6872/8001, 分词36进程进行中, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #236 流水（2026-10-09 09:34, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, GPIC 6839/8001, Code/Math分词范围扩大中(11→36进程), P-8暂缓令未撤。需要时再读。**

> 📦 **[已归档] #232 流水（2026-10-09 07:19, 状态核查）→ daily-memories/2026-10-09.md；结论：GPU全空, GPIC 6759/8001, Code/Math分词无进展, P-8暂缓令未撤。需要时再读。**
> 📦 **[已归档] #231 流水（2026-10-09 06:41, P-8 前置预研完成）→ daily-memories/2026-10-09.md；结论：P-8 PREP 五节写入 EXPERIMENTS, Web 524B✅ / Code 270M🔴 / Math 609M🟠, 训练脚本可改, 100B≈12.5d。需要时再读。**
> 📦 **[已归档] #230 流水（2026-10-09 06:00, R3 BO 收尾）→ daily-memories/2026-10-09.md；结论：DB=100行(98 complete+2 failed), best=#8 score=0.4032, 全交付物写入, R3 全部完成。需要时再读。**
> 📦 **[已归档] #229 流水（2026-10-09 05:28, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=97行, t97-99训练中@78-88%, ETA~05:49。需要时再读。**
> 📦 **[已归档] #227 流水（2026-10-09 04:16, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=89行→97行, batch12(t89-96)全入库, 最后批(t97-99)起步, ETA~05:45。需要时再读。**
> 📦 **[已归档] #226 流水（2026-10-09 03:42, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=89行, batch12(t89-96)训练中@46-61%, ETA~06:00。需要时再读。**
> 📦 **[已归档] #225 流水（2026-10-09 03:05, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=89行, batch12(t90-95)起步@0.2-4.5%, ETA~06:00。需要时再读。**
> 📦 **[已归档] #224 流水（2026-10-09 02:32, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=81行, batch11@62-79%, ETA~06:00。需要时再读。**
> 📦 **[已归档] #223 流水（2026-10-09 01:56, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=81行, batch11起步@15-29%, ETA~06:10。需要时再读。**
> 📦 **[已归档] #221 流水（2026-10-09 00:45, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=73行, batch10起步@31-45%, ETA~06:13。需要时再读。**
> 📦 **[已归档] #220 流水（2026-10-09 00:09, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=65行→73行, batch9收尾, ETA~06:18。需要时再读。**
> 📦 **[已归档] #222 流水（2026-10-09 01:21, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=73行, batch10@80-94%, ETA~06:08。需要时再读。**
> 📦 **[已归档] #218 流水（2026-10-08 22:57, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=65行, batch9起步@2-15%, ahead 1补推。需要时再读。**
> 📦 **[已归档] #217 流水（2026-10-08 22:22, R3 BO 监控）→ daily-memories/2026-10-09.md；结论：DB=57行, batch8@63-77%, ETA~06:27。需要时再读。**
> 📦 **[已归档] #213 流水（2026-10-08 19:55, R3 BO 监控）→ daily-memories/2026-10-08.md；结论：DB=40行, batch6收尾@90-93%。需要时再读。**
> 📦 **[已归档] #214–#216 流水（2026-10-08 20:28–21:43, R3 BO 进度监控 DB=49→57行）→ `daily-memories/2026-10-08.md`；结论：BO健康运行, batch7(t48-56)训练中, t0055 EADDRINUSE失败已由t0056替补。需要时再读。**
> 📦 **[已归档] #209–#212 流水（2026-10-08 17:35–19:20, R3 BO 进度监控 DB=32→40行）→ `daily-memories/2026-10-08.md`；结论：BO健康, batch5→6训练中, ETA~05:45–05:50。需要时再读。**
> 📦 **[已归档] #204, #205, #207, #208 流水（2026-10-08 14:39–17:01, R3 BO 监控 batch3-4）→ `daily-memories/2026-10-08.md`；结论：DB从16→24rows, Best=#8(0.4032)持续领先, 0 NaN, ETA~06:05 Oct9。需要时再读。**
- 🩺 **本唤醒推进 = R3 BO 进度监控 #203（2026-10-08 14:05, .29 全8GPU BO运行中）**：① git fetch + status → **ahead 1**（data agent commit 5cc504d 未 push，本次一起 push）。② **BO 健康核查**：PID 2637043 alive (etimes=8572s≈143min, ppid=1 ✅)；8 GPU 全 62GB/41-87%util ✅。③ **DB 查询**：8 rows 全 status=complete（lowercase），score 0.3703~0.4032，Best=trial#8(0.4032)。④ **第2批(trials 8-15)训练中**：iter ~22000-22600/30517(~73%), lm loss 3.88-4.60, grad norm 0.59-0.97, **0 NaN** ✅ (grep 全 0)。⑤ **ETA 精算**：~8000 steps 剩余 @ ~167ms/step ≈ 22min → 第2批训练~14:25结束 +HF2min+eval3.6min→~14:31完成 → 84 trials剩余/8=10.5轮×90min=945min≈15.75h → 总ETA~06:15 Oct 9（≤24h ✅）。⑥ watchdog PID 1391466 ✅(etimes≈92h)。⑦ 体积：TASK=32527B(31.8KB) / MEMORY=18786B(18.4KB) 均 ≤32KB ✅。→ 下一步：30min后再查BO进度+DB trial数。WAITING=1。git：本次 push（含 data agent ahead commit）。
- 🩺 **本唤醒推进 = R3 BO 进度监控 #202（2026-10-08 13:30, .29 全8GPU BO运行中）**：① git fetch + status 0/0 ✅（无新运维指令，TASK 无变更）。② **BO 健康核查**：PID 2637043 alive (etimes=6435s≈107min, ppid=1 ✅)；8 GPU 全 62GB/43-89%util ✅。③ **⭐ 第1批8trial全COMPLETE✅**！DB(nemo_experiments/mix_search/mix_search_eval_r3.db, 20480B) 有8行, 0失败, 0 NaN。④ **首批 top scores**：trial#8=0.4032(best, boolq=0.589) > #3=0.3855 > #4=0.3853 > #1=0.3839 > #7=0.3839 > #2=0.3832 > #5=0.3759 > #6=0.3703。Best trial#8 配比: en=0.168/zh=0.198/l1_hq=0.324/ultrax=0.080/code=0.064/math=0.045。⑤ **第2批(trials 8-15)训练中**：iter ~8810-9490/30517(~30%), lm loss 4.0-5.2, grad norm 0.4-0.6, **0 NaN** ✅。⑥ **ETA精算**：~80min/batch(11:40→13:00实测) → 第2批~14:10完成 → 11轮剩余×80min=880min≈14.7h → 总ETA~05:00 Oct 9（≤24h ✅）。⑦ DB路径更正：run/下的0B db是空壳(不提交)，真实DB在 `nemo_experiments/mix_search/mix_search_eval_r3.db`。⑧ watchdog PID 1391466 ✅(etimes≈91.5h)。⑨ 体积：TASK=32527B(31.8KB) / MEMORY=~17KB 均 ≤32KB ✅。→ 下一步：30min后再查BO进度+DB trial数。WAITING=1。git：本次 push。
- 🩺 **本唤醒推进 = R3 BO 进度监控 #201（2026-10-08 12:55, .29 全8GPU BO运行中）**：① git fetch + status 0/0 ✅（无新运维指令，TASK 无变更）。② **BO 健康核查**：PID 2637043 alive (etimes=4459s≈74min, ppid=1 ✅)；8 GPU 全 62GB/61-83%util ✅；8 trial 日志活跃(12:55更新)。③ **训练进度**：8 trial 均 iter~28750/30517(94%), lm loss t0000~3.86/t0001~4.68, grad norm~0.7-1.2, **0 NaN** ✅ (grep 全 0)。④ **ETA 精算**：~1767 steps 剩余 @ ~155ms/step ≈ 4.5min → 训练~12:59结束 +HF2min+eval3.6min → 首批8trial完成~13:05 → 12 full rounds + 1 partial(4) = 100 trials → 总~19.5h → ETA~07:10 Oct 9（≤24h ✅）。⑤ DB=mix_search_eval_r3.db 0B（首批trial完成时写入）。⑥ watchdog PID 1391466 ✅(etimes≈91h)。⑦ 体积：TASK=32527B(31.8KB) / MEMORY=16651B(16.3KB) 均 ≤32KB ✅。→ 下一步：30min 后再查 BO 进度；首批 trial 完成时查 DB top scores。WAITING=1。git：本次 push。
- 🩺 **本唤醒推进 = R3 BO 进度监控 #200（2026-10-08 12:17, .29 全8GPU BO运行中）**：① git fetch + status 0/0 ✅（无新运维指令，TASK 无变更）。② **BO 健康核查**：PID 2637043 alive (etimes=2158s≈36min, ppid=1 ✅)；8 GPU 全 62GB/45-87%util ✅；8 trial 日志活跃(12:16更新)。③ **训练进度**：t0000 iter~14030/30517(46%), lm loss~4.0, grad norm~0.5, **0 NaN** ✅；t0001 iter~13810, loss~4.9（不同数据配比→不同loss，正常）。④ **ETA 精算**：379 steps/min(~158ms/step) → 训练余~43min→~13:00首批train结束 +HF2min+eval3.6min→~13:06首批8trial完成 → 12.5轮×86min=18.0h → ETA~05:40 Oct 9（≤24h ✅）。⑤ DB=mix_search_eval_r3.db 0B（无表，首批trial完成时写入）→ ⚠️ `sqlite3` CLI 不在 PATH，改用 python3 查。⑥ **P-8 prep**：/nas_train 33T 可用（够 ckpt）；训练脚本不在预期路径（待 P-8 启动令后再核验）；DATA_MIX_RECIPE.md 在位。⑦ watchdog PID 1391466 ✅。⑧ 体积：TASK=32527B(31.8KB) / MEMORY=15738B(15.4KB) 均 ≤32KB ✅。→ 下一步：30min 后再查 BO 进度；首批 trial 完成时查 DB top scores。WAITING=1。git：本次 push。
- 🩺 **本唤醒推进 = R3 BO 搜索启动 #199（2026-10-08 ~11:40, .29 全8GPU空闲→已占满）**：① git fetch + status 0/0 ✅。② **6 源小样本分词 6/6 DONE ✅**。③ **R3 BO 100-trial 搜索启动**：PID 2637043 (ppid=1)。④ **8 trial 并行训练中**：iter ~440/30517, 148ms/step, loss↓7.15, 0 NaN ✅。⑤ DB=mix_search_eval_r3.db 已创建。⑥ watchdog PID 1391466 ✅。⑦ 体积均 ≤32KB ✅。→ 下次唤醒查 BO 进度。WAITING=1。git：push ✅。

- 🩺 **本唤醒推进 = R2 收官报告 #196（2026-10-08 ~09:10, .29 全8GPU空闲）**：① git fetch + status 0/0 ✅（无新运维指令）。② **R2 收官总报告**：`doc/BaiZe-ISEDA2027/report_pretrain_r2_final.html` 已完成——10 节（TL;DR / 实验设计总览 / 架构选型 / 超参搜索 / FP8 裁定 / 长上下文 / 提速实验 / 复杂推理 / P-8 建议 / 局限与诚实交代）+ 报告索引，**46KB / 6 张内联 SVG**（P-1 LR U 形 / P-5b loss scaling / P-6② Avg scaling law / P-9.8 FP8 loss 对比 / P-3 dense-vs-hybrid / BBH scaling），全部数字源自 EXPERIMENTS_PRETRAIN_2B_ROUND2.md。③ commit `pretrain R2收官: report_pretrain_r2_final.html` 已 push ✅。④ GPU 核验：.29 全8GPU 0MiB/0% ✅。⑤ watchdog PID 1391466 ✅。⑥ 体积：MEMORY=13.8KB ≤32KB ✅。→ 下一步：等待运维 P-8 启动令 / 分词完成。WAITING=1。git：本次 push。
- 🩺 **本唤醒推进 = 状态核查 #195（2026-10-08 08:36, .29 全8GPU空闲）**：① git fetch + status 0/0 ✅（无新运维指令，TASK 无变更；工作区干净无 modified）。② **GPU 核验**：本机=.29, GPU0-7 全 0MiB/0%，无 compute apps ✅。③ **P-8 前置核查**（读 data agent MEMORY_DATA 唤醒215@08:04）：base ✅全满 + 配比方案✅(88:8:4)；**暂缓令(10-02)未撤** + **分词未完成**——zh s9~81%done(45.9GB.bin,ETA~09:42), l1_en_hq 12进程(各~7.3GB.bin,ETA~15:30), GPIC 5741/8001 ETA~2.0d → **P-8 仍不可启动**。④ watchdog PID 1391466 ✅(etimes=311954s≈86.7h)。⑤ **体积自检**：TASK=23193B(22.7KB) / MEMORY=12942B(12.6KB) 均 ≤32KB ✅ 无需归档。→ 下一步：等待运维 P-8 启动令 / 分词完成。WAITING=1。git：本次 push。
- 🩺 **本唤醒推进 = 状态核查 #194（2026-10-08 08:02, .29 全8GPU空闲）**：① git fetch + status 0/0 ✅（无新运维指令，TASK 无变更；工作区仅 vision 线文件 modified，非本线不碰）。② **GPU 核验**：本机=.29, GPU0-7 全 0MiB/0%，无 compute apps ✅。③ **P-8 前置核查**（读 data agent MEMORY_DATA 唤醒214@07:32）：base ✅全满 + 配比方案✅(88:8:4)；**暂缓令(10-02)未撤** + **分词未完成**——zh s9~74%done(ETA~09:45), l1_en_hq 12进程运行中(各3.85GB.bin), GPIC 5714/8001 ETA~2d → **P-8 仍不可启动**。④ watchdog PID 1391466 ✅(etimes=309898s≈86.1h)。⑤ **体积自检**：TASK=23193B(22.7KB) / MEMORY=12149B(11.9KB) 均 ≤32KB ✅ 无需归档。→ 下一步：等待运维 P-8 启动令 / 分词完成。WAITING=1。git：本次 push。
- 🩺 **本唤醒推进 = 状态核查 #193（2026-10-08 07:29, .29 全8GPU空闲）**：① git fetch + status 0/0 ✅（无新运维指令，TASK 无变更）。② **GPU 核验**：本机=.29, GPU0-7 全 0MiB/0%，无 compute apps ✅。③ **P-8 前置核查**（读 data agent MEMORY_DATA 唤醒213@06:52）：base ✅全满 + 配比方案✅(88:8:4)；**暂缓令(10-02)未撤** + **分词未完成**——zh分词7shard✅DONE(98.80B tok), s9运行中(37.8GB ETA~11:00), l1_en_hq分词12进程已启动(s12-s23 ETA~16:00), GPIC 5686/8001 ETA~2.2d → **P-8 仍不可启动**。④ watchdog PID 1391466 ✅(etimes=307947s≈85.5h)。⑤ **体积自检**：TASK=23193B(22.7KB) / MEMORY=12393B(12.1KB) 均 ≤32KB ✅ 无需归档。→ 下一步：等待运维 P-8 启动令 / 分词完成。WAITING=1。git：本次 push。
- 🩺 **本唤醒推进 = 状态核查 #191（2026-10-08 06:22, .29 全8GPU空闲）**：① git fetch + status 0/0 ✅（无新运维指令，TASK 无变更，无 ahead/behind；工作区仅 harness 线文件 modified `kimi_pilot_results.json`，非本线不碰）。② **GPU 核验**：本机=.29, GPU0-7 全 0MiB/0%，无 compute apps ✅。③ **P-8 前置核查**（读 data agent MEMORY_DATA 唤醒212@06:04）：base ✅全满 + 配比方案✅(88:8:4)；**暂缓令(10-02)未撤** + **分词未完成**——zh分词7shard@50GB final-write-phase(无.idx, logs stalled~100min=final write/index phase), s9@32GB仍处理中(6.05M docs/5.22B tok), GPIC 5650/8001 ETA~2.1d, l1_en_hq分词未启动(脚本已就绪)→ **P-8 仍不可启动**。④ watchdog PID 1391466 ✅(baize_pretrain_loop.sh 运行中)。⑤ **体积自检**：TASK=23193B(22.7KB) / MEMORY=13737B(13.4KB) 均 ≤32KB ✅ 无需归档。→ 下一步：等待运维 P-8 启动令 / 分词完成。WAITING=1。git：本次 push。
> 📦 **[已归档] #184–#188 流水（2026-10-08 02:22–04:39, 状态核查, GPU空闲等P-8前置）→ daily-memories/2026-10-08.md；结论：均无新运维指令, P-8暂缓令未撤+分词未完成, 不可启动。需要时再读。**
> 📦 **[已归档] #181–#183 流水（2026-10-08 00:38–01:49, 状态核查）→ `daily-memories/2026-10-08.md`；结论：均无新运维指令, P-8 仍不可启动。需要时再读。**
> 📦 **[已归档] #149–#179 流水（2026-10-06 23:10 ~ 2026-10-07 23:33, 含 P-9.11-E/F + Report 4/5 + A 36/36 收官 + 状态核查）→ `daily-memories/2026-10-07.md`；结论均已写入 EXPERIMENTS_PRETRAIN_2B_ROUND2.md。需要时再读。**
n> 📦 **[已归档] #142–#148 + Report 1-3 流水（2026-10-06 ~17:53 – 2026-10-07 ~14:30, B1 长ctx/P-9.11-D/A v2/研究 Report 1-3）→ `daily-memories/2026-10-07.md`；结论均已写入 EXPERIMENTS_PRETRAIN_2B_ROUND2.md。需要时再读。**

> 📦 **[已归档] 第 139–141 次唤醒流水（A 复杂推理 v1/v2 + P-9.13 Step 2 提速收官）→ `daily-memories/2026-10-07.md`；结论均已写入 EXPERIMENTS_PRETRAIN_2B_ROUND2.md。需要时再读。**

> 📦 **[已归档] 第 132–138 次唤醒流水（P-9.12 NCCL topo ✅ + P-9.13 提速扫描 + 空窗提案 #135 + 状态核查 #132–#134）→ `daily-memories/2026-10-07.md`；结论均已写入 EXPERIMENTS_PRETRAIN_2B_ROUND2.md。需要时再读。**

> 📦 **[已归档] 第 110–135 次唤醒流水（P-9.5 profiler / P-9.10③ / P-9.11② / P-5b 8-set eval / P-6② scaling law / 状态核查 #128–#135）→ `daily-memories/2026-10-05.md` + `daily-memories/2026-10-06.md`；结论均已写入 EXPERIMENTS_PRETRAIN_2B_ROUND2.md。需要时再读。**


## [已归档] 第 102–107 次唤醒流水（P-9.9 巡检 + 收官 + P-9.10①sglang A/B）→ `daily-memories/2026-10-05.md`

## 🗣️ 运维问答 · 2026-10-09（补测对比报告 · 先报后跑门控）

> **运维令**：补测 + 中文对比报告：BaiZe-Hybrid 2.220B ⚔ 参数匹配 Dense Llama，SGLang，ctx 持续 ×2 直到 hybrid OOM。门控：先报「参数匹配方案 + 测试矩阵 + ETA + 占用卡」，再开跑。

### ① 参数匹配方案

**主对手臂 = Dense Llama 36L（随机初始化）**
- 构建：复用 `p3_dense`（MiniCPM5-2B, 42L）的架构配置，**仅减层数 42→36**，使总参数对齐 hybrid。
- 架构配置（`config.json` 将照此生成）：

| 参数 | 值 | 来源 |
|:--|:--|:--|
| `architectures` | `LlamaForCausalLM` | 标准 Llama |
| `vocab_size` | 129,408 | 与 hybrid/dense 同 tokenizer |
| `hidden_size` | 2,048 | 同 p3_dense |
| `intermediate_size` | 6,144 | 同 p3_dense（SwiGLU 3×H） |
| `num_hidden_layers` | **36**（从 42 减 6） | 调此值对齐参数 |
| `num_attention_heads` | 16 | 同 p3_dense |
| `num_key_value_heads` | 2 | 同 p3_dense（GQA） |
| `head_dim` | 128 | 同 p3_dense |
| `hidden_act` | silu | SwiGLU |
| `tie_word_embeddings` | false | 同 p3_dense |
| `max_position_embeddings` | 4096 | 同 p3_dense（推理时 SGLANG_ALLOW_OVERWRITE 扩展） |
| `rope_theta` | 5,000,000.0 | 同 p3_dense |

- **精确参数量**（Python 实算）：
  - Embedding: 129,408 × 2,048 = 265,090,048
  - LM head: 265,090,048（不 tie）
  - 每层 attn: q 4,194,304 + k 524,288 + v 524,288 + o 4,194,304 = 9,437,184
  - 每层 MLP: 3 × 2,048 × 6,144 = 37,748,736
  - 每层 norms: 2 × 2,048 = 4,096
  - 每层合计: 47,190,016
  - 36 层: 1,698,840,576
  - Final norm: 2,048
  - **总计: 2,228,897,792 = 2.229B**
  - **vs hybrid 2,220,268,032 = +0.389%（±1% 内 ✅）**
- ⚠️ **权重随机初始化**（`torch.randn` × `initializer_range=0.02`）—— 本次比的是**速度/显存**，与权重值无关；报告中将显式标注。
- tokenizer 文件直接复制 `p3_dense`（同 vocab=129,408）。

**参考臂 = p3_dense（MiniCPM5-2B, 2.512B, 42L）**：附录/脚注用，佐证「未做参数匹配时偏袒 dense 约 +13% 参数」。

**备选方案（若运维要求更紧匹配）**：L=35, kv_heads=4（匹配 hybrid 的 4 KV heads）→ 2,218,407,936 = −0.084%。但 KV cache 翻倍（kv=4 vs kv=2）会使 dense 更早 OOM，可能不是「公平」的解读。

### ② 测试矩阵

| 维度 | 取值 | 说明 |
|:--|:--|:--|
| **模型** | {hybrid 2.220B, **dense-matched 2.229B**, p3_dense 2.512B(ref)} | 主对比 = hybrid vs dense-matched |
| **ctx** | 128K→256K→512K→1M→2M→4M→8M（×2） | 持续 ×2 直到 **hybrid 自己 OOM** 才停 |
| **mem-frac** | {0.6, 0.85} | ≥0.6（旧 0.3 太低致 dense 假 OOM）；同 ctx 两臂同值 |
| **bs** | {1, 8} | 至少两档 |
| **gen_len** | 64 | 同 P-9.11 |
| **WARMUP** | 1 | 丢弃首请求（消除 CUDA kernel 编译冷启动） |
| **REPEATS** | 3（取 median） | 公平口径 |
| **per-B 归一化** | tok/s ÷ B | 报告中每格同时报原始和 per-B |

**SGLang flags（两臂一致，仅 hybrid 额外加 SSM dtype）**：
```
--mem-fraction-static {0.6|0.85}
--attention-backend flashinfer
--dtype bfloat16
--context-length {ctx}
--disable-radix-cache
SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
# hybrid 额外: --mamba-ssm-dtype float32
```
- 环境：`vllm` conda env（sglang 0.5.9），与训练 env 隔离。
- prompt 构造：tokenizer 精确计数（`len(tok(prompt))` = ctx − 128 safety margin），复用 `p911d_sglang_vram_bench.py` 的 `make_prompt_precise()`。
- 每格记录：prefill tok/s / TTFT / decode tok/s / e2e / 峰值 VRAM / pool tokens / prompt 实 token 数 / status(SERVED/OOM/TIMED_OUT)。

**已有数据可复用**：P-9.11-E 的 mem-frac=0.3 结果（`p911e_results/*.json`）作为**低 mem-frac 对照**附录，不作为主表数据（口径不同）。

**终止条件**：hybrid 在某 ctx × mem-frac 下 OOM/不可服务 → 该 mem-frac 的扫描到此 ctx 为止；但**另一 mem-frac 继续扫**直到也 OOM。两 mem-frac 都 OOM → 全停。

### ③ ETA

| 阶段 | 墙钟 | 说明 |
|:--|:--|:--|
| 创建随机 Dense 模型 | ~10 min | Python 脚本生成 config.json + safetensors + 复制 tokenizer |
| 128K–512K（3 ctx × 2 mf × 3 model × 2 bs） | ~1–2h | 低 ctx 每格 <1min，4–6 GPU 并行 |
| 1M（2 mf × 3 model × 2 bs） | ~1–2h | hybrid 1M prefill ~7min/req，dense 可能 OOM |
| 2M（2 mf × 2 model × 2 bs） | ~2–3h | hybrid 2M ~30min/req（P-9.11-F TTFT=427s@mf0.6） |
| 4M–8M（若 hybrid 存活） | ~2–3h | 4M 已知 TIMED OUT@mf0.85；8M 可能不可服务 |
| **合计** | **~6–10h** | 可跨多个唤醒分阶段完成 |

### ④ 占用卡

- **.29 GPU 0–7**（8×H100 80GB），**纯推理**（无训练、无重 I/O）。
- 同时活跃 2–4 个 SGLang server（每个占 1 GPU），其余 GPU 空闲。
- 🚫 不碰 .12（vision 节点）。
- 🚫 不启动 P-8、不改 P-5b recipe、不 kill watchdog。

### ⑤ Warmup 24× 归因（证据）

- **现象**：P-9.11-E hybrid 128K bs=1 prefill=1,591 tok/s（TTFT=79.1s）vs bs=8 prefill=447,796 tok/s（TTFT=2.25s）→ **281× 差距**。
- **归因**：bs=1 是 server 启动后**第一个请求** → SGLang/flashinfer 首次执行时触发 CUDA kernel JIT 编译 + cuBLAS handle 初始化 + memory pool 首次分配 → **冷启动开销 ~77s**。bs=8 紧随其后，kernel 已编译 → 正常速度。
- **证据**：(a) 2M ctx 的结果（`p911e_hybrid_ctx2097152_gpu5.json`）TTFT=8.49s/prefill=237,575 tok/s → 比 128K bs=1 快 150× → **不是 ctx 越大越慢**，而是首请求冷启动；(b) dense 128K bs=1 TTFT=23.97s 也偏慢（但比 hybrid 好，因 dense 无 SSM kernel 需编译）。
- **修正**：本次 **WARMUP=1** 丢弃首请求 → REPEATS=3 均为 warm 状态 → 消除冷启动偏差。旧 P-9.11-E 的 bs=1 数据**不应作为公平对比基线**（无 warmup）。

### ⑥ 下一步（等运维确认后执行）

1. 创建随机初始化 Dense Llama 36L → `hf_checkpoints/dense_matched_2.22b/`
2. 落地 SGLang 基准脚本（复用 `p911d_sglang_vram_bench.py`，加 WARMUP/REPEATS）
3. 分阶段跑：先 128K–512K（快速验证）→ 1M–2M → 4M+（直到 hybrid OOM）
4. 生成 `report_pretrain_baize_vs_dense_fair_zh.html`（中文，≤5 表，内联 SVG）

---

> 📦 **[已归档] 🗣️ 运维问答「提 3 个实验 idea」（2026-10-09, #251 已交付）→ daily-memories/2026-10-09.md；结论：3 idea 按价值排序（①P-8彩排续跑 ②P-8 44B下限档 ③R3配比迁移A/B），建议「立即起P-8」。需要时再读。**

---

## 关键笔记（运维常驻参考）
- seq_length=**4094**（固定口径，非 4096）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- transformer_engine 2.12.0+5671fd36 / torch 2.8.0+cu128 / CUDA 12.8 / megatron-core 0.16.1 / mamba-ssm 2.2.6.post3（P-9.4 已核实，与任务书预期一致）。
- 结果主文件：R2=`EXPERIMENTS_PRETRAIN_2B_ROUND2.md`；Round1=`EXPERIMENTS_PRETRAIN_2B.md` + `BAIZE_PRETRAIN_RESULT.html` + `ISEDA2027/4_llm_pretrain.tex`。
- ckpt：p3_hybrid/iter_0005000 → **HF nemotron_h ✅**（`nemo_experiments/p3_hybrid/hf_iter_5000/`，323 keys, 2.220B）+ p3_dense/iter_0005000 → **HF Llama ✅**（`nemo_experiments/p3_dense/hf_iter_5000/`，381 keys, 2.512B）；原始 mcore distcp @ `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/`。

## GPU / 进程
- 主训练 10.239.2.29（8×H100 GPU0~7）：P-5b ✅ 已结束；P-9.1~P-9.7 全 ✅ 定稿；P-9.8 ✅ / P-9.9 ✅ / P-9.10 ①②③ ✅ / **P-5b 8-set eval ✅ COMPLETE**（GPU0-1 已释放）；**⭐ 全 8 GPU 空闲**（data agent @08:06 kill S0a → GPU2-7 释放；proxy 标定尚未起跑）；**P-9.11 ① HF 转换 ✅ BOTH DONE**（p3_hybrid→nemotron_h + p3_dense→Llama，待 sglang 起服）。
- watchdog `baize_pretrain_loop.sh` PID 1391466 必须 7×24 存续，🚫 绝不 kill。
- P-9（P-9.1 ✅ / P-9.2 ✅ / P-9.3 ✅ / P-9.4 ✅ / **P-9.5 ✅ COMPLETE** — 崩溃修复 + 5-way 归因 + HTML / P-9.6①② ✅ / P-9.7 ✅ / P-9.8 ✅ COMPLETE → delayed FP8 可用于 P-8 / **P-9.9 ✅ COMPLETE → tensorwise T1/T4 FAIL → P-8 沿用 delayed** / **P-9.10 ① ✅ sglang ✅ 可用(vllm env) [第109次更正] → eager 下界✅已测 + sglang 上界待 HF 转换补测，② ✅ COMPLETE eager 下界 H1✅H2❌H3❌H4✅**）；🚫 不对 live 长跑做 nsys/ncu attach。
