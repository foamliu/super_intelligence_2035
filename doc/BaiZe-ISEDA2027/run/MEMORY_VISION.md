# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🎉 **【ArmE-R2 全链路 ✅ DONE · ①训练✅(63400步,~37h) · ②ProtB✅ lp68.236±0.0182/5-NN58.904(🏆全实验最高!) · ③MLLM三阶段✅(Stage-2 09:50) · ④12集✅ 12/12 avg26.10% · ⑤报告✅】** 裁定 = **不可分辨(边界值)**（avg 26.10% vs ArmD-R2 26.12% = **−0.02pp** / vs ArmC 25.78% = +0.32pp / vs ArmB 26.10% = −0.00pp）。**编码器🏆历史最高已 secured**：ProtB lp 68.236% vs ArmD-R2 **Δlp+3.899pp**/Δ5-NN+2.948pp。**但MLLM下游完全持平** → ViT-L/14(304M)比B/16(86M)大3.5×，MLLM 12集平均却−0.02pp → **容量不是MLLM下游瓶颈**。**ProtB→MLLM传递性证伪（最强烈一例）**：编码器4-6pp ProtB优势完全未转化为MLLM下游增益。🔧 eval bridge修复：lmms_eval_baize_llava.py 硬编码196(ViT-B/16)→ViT-L/14产出256→8GPU全崩；已修3处动态num_image_tokens。ArmE-R2 = ArmE降LR重跑(LR 1e-3→5e-4+warmup 2000→3000, ViT-L/14, 6源173M对, 63400步, lr5e-4, C1最高0.9664@s45240)。⚠️ vs ArmD-R2 = 塔(B→L)+LR+warmup**三变量**+容量混杂→报告须分开。报告(完整7节)=reports/report_vision_armE_r2_20261024_zh.html(25.9KB,含①训练+③MLLM三阶段)+EXPERIMENTS_VISION.md §15。旧版17KB(report_vision_armE_r2_20261022_mllm_stage4_zh.html)保留备查。生成器=vision/generate_armE_r2_full_report.py。📄**下一步方案报告(运维令16:1x)**=`reports/report_vision_next_steps_protb_mllm_zh.html`(21.1KB,8节,0 script/0外链,生成器`vision/generate_next_steps_protb_mllm_report.py`)。核心结论:12集已饱和(逐集最大跨度1.66pp,多数<1σ)→单一建议=先做B4(MMBench/MMVet/MathVista+336anyres在已有ArmB/ArmE-R2 ckpt重测,~0 GPU·h)。**WAITING: 0**。

> 📦 **ArmD-R2 全链路 DONE**（①训练✅24.7h · ②ProtB lp64.3373/5-NN55.956 · ③MLLM✅ · ④12集avg26.12% · ⑤报告✅）详细状态块已归档 → `daily-memories-vision/2026-10-24.md`「ArmD-R2 状态块归档」节；**结论**：ArmD-R2 vs ArmC(LR轴一致,仅data3→6源+epoch4→3) ProtB Δlp+2.005pp 双正向但 MLLM 持平→传递性首次证伪；Stage-2 用原版780k(非opt47)故④含数据混杂,编码器ProtB结论不受影响。详见 `EXPERIMENTS_VISION.md §14` + `reports/report_vision_armD_r2_20261020_mllm_stage4_zh.html`。需要时再读。

> 📦 wake #242 (2026-10-24 05:04, ArmE-R2 ①训练第7次监控 step60160/94.9% 健康·ckpt@60000) 已归档 → daily-memories-vision/2026-10-24.md；**结论**：末段C1~0.93逼近历史最高0.9664，0nan/0oom，watcher活跃，ETA~07:00。需要时再读。

> 📦 wake #247 (2026-10-24 12:57, ArmE-R2 ⑤报告复核) 已归档 → daily-memories-vision/2026-10-24.md；**结论**：报告(26.5KB,7节,0script/0外链)+§15链接+任务书归档(33.9→24.0KB)+commit e8dc74489 全闭合。需要时再读。
> **本唤醒流水 [wake #248, 2026-10-24 14:12]**：✅ **ArmE-R2 运维令 10-24 二次复核 · 全链路已闭合，数据纪律交叉验证通过**。①**报告** `report_vision_armE_r2_20261024_zh.html`(26.5KB,7节) 已于 wake#246 生成(commit e8dc74489)，wake#247 验收。本轮逐数溯源：ProtB lp68.236/per_seed[68.212,68.256,68.240]/5-NN58.904 ↔ `armE_r2_...results.json`✅；ArmD-R2 lp64.3373 ↔ `armD_r2_...results.json`✅(Δlp+3.899pp)；12集 11 benchmark 全 ↔ `consolidated_12benchmarks.json`✅(avg除MME=26.10%)；训练 log `/tmp/armE_r2_openclip_train.log` 确认 T0=10-22 17:52:54/done 10-24 06:57:43/spike峰s28520 loss1.4299✅；eval bridge `lmms_eval_baize_llava.py:53` 256/196 动态✅。②**无 N/A、无编造**。③git 同步(无 ahead/behind)。无新令。**WAITING: 1**。📦 体积：TASK=24.2KB / MEMORY=30.7KB（归档 wake#242→daily-10-24，均≤32KB✓）。
> **本唤醒流水 [wake #249, 2026-10-24 15:1x]**：✅ **ArmE-R2 运维令 10-24 三次复核 · 闭合运维令④残留项（旧版标注）**。前两轮(wake#247/#248)已完成报告(26.5KB,7节)+§15链接+任务书归档+commit/push。本轮发现运维令④「旧 17KB 版保留，标注"旧版"」残留：旧报告 `report_vision_armE_r2_20261022_mllm_stage4_zh.html` 自身无"旧版"标注(仅新报告footer与MEMORY引用)。已补：<body>后插入红底 kbox 横幅「⚠️ 旧版（已被完整版取代）· 6节简版·缺①训练与③MLLM三阶段·完整版见 report_vision_armE_r2_20261024_zh.html」。grep 验证新报告 0 `<script>`/0外链✅；HTMLParser 标签配平✅。体积自检 TASK=24.2KB/MEMORY=31.1KB 均≤32KB✓。commit `vision report:` 前缀。无新令。**WAITING: 1**。📦 体积：TASK=24.2KB / MEMORY=31.1KB（无归档，均≤32KB✓）。
> **本唤醒流水 [wake #251, 2026-10-24 17:41]**：🔄 **空唤醒复核 · 顶部运维令(16:1x)已 DONE(wake#250)，无新令到达**。①复核交付物：`reports/report_vision_next_steps_protb_mllm_zh.html`(实测 29419B ≈28.7KB；注：MEMORY/任务书旧记作21.1KB，实为28.7KB，本轮据实更正) grep 0 `<script>`/0 外链 ✅，生成器 `vision/generate_next_steps_protb_mllm_report.py` 在位 ✅。②git：vision 线工作树无未提交改动(仅见他线 baize_p8/harness/zhulong 在途文件，未触碰)；上次 vision commit f5f4825a5@17:02(wake#250)。③状态修正：wake#250 将 WAITING 置 0 → 会使 loop 每 1min 空转烧 token；现无训练运行，纠正为 **WAITING: 1**（待运维下一令，30min 轮询）。④体积自检 TASK=29283B/MEMORY≈30.8KB 均 ≤32KB✓，无需归档。本轮未启动训练/未动产物。无新令。**WAITING: 1**。📦 体积：TASK=28.6KB / MEMORY=30.8KB（无归档，均≤32KB✓）。
> **本唤醒流水 [wake #252, 2026-10-24 18:54]**：🔄 **空唤醒复核 · 顶部运维令(16:1x)仍 DONE(wake#250)，`git fetch` 0 behind ⇒ 无新令到达**。①vision 工作树无未提交改动（`git diff --stat` vision 文件空）；报告 `report_vision_next_steps_protb_mllm_zh.html`(29419B) 在位✅。②**清理 `[ahead 2]`**：本地领先 origin 的 2 个 commit 均为 `ops-relay` 结果提交（paul.liu/Yang Liu @18:13，非 vision 产物），按收尾铁律 `git push origin main` 推平 → 闭环自检 `git status -sb` 无 ahead/behind。③体积自检 TASK=29283B(28.6KB)/MEMORY≈30.4KB 均 ≤32KB✓，无需归档。本轮未启动训练/未动产物/未触碰他线文件。无新令。**WAITING: 1**。📦 体积：TASK=28.6KB / MEMORY=30.4KB（无归档，均≤32KB✓）。
> **本唤醒流水 [wake #253, 2026-10-24 20:03]**：🔄 **空唤醒复核 · 顶部运维令(16:1x)仍 DONE(wake#250)，`git fetch` 0 behind ⇒ 无新令到达**。①vision 工作树无未提交改动；报告 `report_vision_next_steps_protb_mllm_zh.html`(29419B) 在位✅；git 同步(无 ahead/behind)。②**归档 wake#223**(Oct-23 训练监控长条→daily-10-23 已有原文)释放 ~1KB 体积空间。③体积自检 TASK=28.6KB/MEMORY≈30.4KB 均≤32KB✓。本轮未启动训练/未动产物/未触碰他线文件。无新令。**WAITING: 1**。📦 体积：TASK=28.6KB / MEMORY=30.4KB（归档 wake#223→daily-10-23，均≤32KB✓）。
> **本唤醒流水 [wake #254, 2026-10-24 21:14]**：🔄 **空唤醒复核 · 顶部运维令(16:1x)仍 DONE(wake#250)，`git fetch` 0 behind ⇒ 无新令到达**。①vision 工作树无未提交改动（`git diff --stat` vision 文件空）；报告 `report_vision_next_steps_protb_mllm_zh.html`(29419B) 在位✅；git 同步(无 ahead/behind)。②体积自检 TASK=29283B(28.6KB)/MEMORY=31391B(30.7KB) 均≤32KB✓，无需归档。本轮未启动训练/未动产物/未触碰他线文件。无新令。**WAITING: 1**。📦 体积：TASK=28.6KB / MEMORY=30.7KB（无归档，均≤32KB✓）。
> **本唤醒流水 [wake #255, 2026-10-24 22:26]**：🔄 空唤醒复核·顶部运维令(16:1x)仍DONE(wake#250)，`git fetch`1behind(zhulong-ops-relay@22:26非vision)⇒无新令。①vision工作树净;报告`report_vision_next_steps_protb_mllm_zh.html`(29419B)在位✅。②`git pull --rebase --autostash`同步(仅zhulong inbox.md,不动vision文件)→0behind/0ahead。③体积自检TASK=29283B(28.6KB)/MEMORY初始32026B→加心跳+PHASE更新触32758B(32.0KB,贴顶)⇒归档wake#247(→daily-10-24)释放~0.7KB→MEMORY≈31.3KB,均≤32KB✓。本轮未启动训练/未动ArmB/C/D/E产物/未触碰他线文件。无新令。**WAITING: 1**。📦体积：TASK=28.6KB/MEMORY=31.3KB（归档wake#247→daily-10-24,均≤32KB✓）。




> 📦 **wake #206 (2026-10-21 20:31, ArmD-R2 全链路状态复核)** 已归档 → daily-memories-vision/2026-10-21.md；**结论**：2026-10-21 运维令(Stage-2改原版780k)全完成并已提交(commit 9dce3f3d0)；④12集 avg26.12%✓；git 同步。需要时再读。

> 📦 **wake #207 (2026-10-21 22:0x, ArmE 启动: 脚本创建/显存probe/MBS256决策/烟雾通过/正式起训 T0=22:02:33)** 已归档 → daily-memories-vision/2026-10-21.md；**结论**：ArmE 唯一变量=视觉塔 ViT-B/16→ViT-L/14(304.0M visual/427.6M total)，MBS=256/accum=4 保 GBS=8192+steps63400(仅1混杂=per-micro-batch对比batch 4096→2048)，烟雾 STEPS=100 通过，正式起训。需要时再读。
> 📦 **wake #208 (2026-10-21 23:09, ArmE 首次监控 step1880/3.0%, 健康, 0.47it/s)** 已归档 → daily-memories-vision/2026-10-21.md；**结论**：ArmE 首次监控确认训练健康(loss单调降/C1单调升/0nan/peak77.5GB)，配置单变量守住。需要时再读。
> 📦 **wake #212 (2026-10-22 04:1x, ArmE ②下游评估链脚本全部就绪)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：ArmE 下游全链脚本(4py+3sh+3共享改造)就绪，全py_compile/bash -n✓，单变量守住。需要时再读。
> 📦 **wake #213 (2026-10-22 06:37, ArmE 第6次监控 step14700/23.2% 健康 ckpt@10k)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：step14700 健康,bestC1=0.7845,s13600-14400硬分片抖动后恢复,0nan,watcher活跃。需要时再读。
> 📦 **wake #215 (2026-10-22 11:2x, ArmE 第9次监控 step22720/35.8% 健康 ckpt@20k 已存 watcher活跃)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：step22720 健康(第8次硬分片抖动后恢复中),bestC1=0.7845未破,0nan,config单变量守住,ckpt@10k+20k已存。需要时再读。
> 📦 wake #223 (2026-10-23 01:46, ArmE-R2 ①训练第3次监控 step13460/21.2% 健康·spike5发展中·ckpt@10k) 已归档 → daily-memories-vision/2026-10-23.md；**结论**：spike5底0.28(>0.05红线5.6×余量)，0nan/0oom，ETA~10-24 07:00。需要时再读。
> 📦 **wake #210 (2026-10-22 01:3x, ArmE 第3次监控 step6020/9.5% 健康)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：step6020 健康,0.48it/s,s4020-5020硬分片抖动后完全恢复,0nan。需要时再读。

> 📦 **wake #211 (2026-10-22 02:4x, ArmE 第4次监控 step8200/12.9% 健康 ckpt@10k临近)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：step8200 健康,C1新高0.531超越spike前,0nan,ckpt@10k临近。需要时再读。
>

>
> 📦 **wake #205 (2026-10-21 19:0x, ArmD-R2 全链路收尾→⑤报告生成完成)** 已归档 → daily-memories-vision/2026-10-21.md；**结论**：⑤报告 `report_vision_armD_r2_20261020_mllm_stage4_zh.html`+§14 DONE；裁定 avg26.12% 不可分辨(边界值)；编码器 ProtB Δlp+2.005pp/Δ5-NN+1.238pp 已 secured。需要时再读。
>
> 📦 **ArmD 原始轮（LR 2e-3, 2026-10-19~20）已归档** → daily-memories-vision/2026-10-20.md + ARCHIVE_OPERATOR_VISION.md；**结论**：ArmD(四变量: data3→6源+epoch4→3+lr→2e-3+min_lr→2e-5) 训练至 step21820 发散(loss0.45→9.3, C1 0.589→0.0002), wake#180 停止保全 ckpt_10000, 7 产物移入 DIVERGED_archive/。**已被 ArmD-R2 承接**(LR 轴回退 1e-3/1e-5)。
>
> 📦 **wakes #180–#198（ArmD-R2 ①训练全程监控：起训→完成@10:02:49, best joint s43700 loss0.1360/C1 0.8902）** 已归档 → daily-memories-vision/2026-10-2{0,1}.md。需要时再读。

> 📦 **wake #217 (2026-10-22 12:39, ArmE 第10次监控 step24800/39.1% 第9次spike恢复中)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：第9次spike峰值8.33(迄今最大),loss从8.33→3.76再升5.38(振荡恢复),0nan。需要时再读。

> 📦 **wake #220 (2026-10-22 19:1x, ArmE-R2 首次监控 step2160 健康·全链下游脚本就绪)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：warmup期零spike(vs ArmE同期多次spike)，本轮创建 ArmE-R2 全链下游脚本(6新+2改,全py_compile/bash✓)。需要时再读。

> 📦 **wake #218 (2026-10-22 14:0x, ArmE 第11次监控 step27180/42.8% 第9次spike恢复极慢)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：第9次spike峰值8.33(迄今最大), 3500步仅恢复到C1=0.030, 已备份ckpt_10000防删。→触发运维令(停ArmE→降LR重跑ArmE-R2)。需要时再读。

> 📦 **wakes #177,#179,#187,#191,#196,#199（ArmD/ArmD-R2 监控 keep-alive）** 已归档 → daily-memories-vision/2026-10-2{0,1}.md。

> ✅ **ArmC 全链路 DONE（wake #172, 2026-10-19 19:46）** — 详见 `run/reports/report_vision_armC_20261018_mllm_stage4_zh.html` + `EXPERIMENTS_VISION.md §13` + `ARCHIVE_OPERATOR_VISION.md`。要点：**两变量**（min_lr 1e-4→1e-5 + wd 0.1→0.01）；①训练 57,250 步 ✓ ②ProtB lp 62.332±0.014 / 5-NN 54.718（vs ArmB 62.093/58.102）③MLLM 三阶段 ✓ ④**12/12 DONE，avg(除 MME) 25.78% vs ArmB 26.10% = Δ−0.32pp，裁定不可分辨**；逐集 Δ 全在 ±2pp 内（5 升 6 降）。⏭ **已被 ArmD 承接**（见上）。
 > 📦 ArmB 全程（2026-10-17 09:1x ~ 10-18 07:55，wake #128~#145）+ 10-14~16 全天流水已归档 → `daily-memories-vision/2026-10-1{7,8}.md` + `ARCHIVE_OPERATOR_VISION.md`；**结论**：ArmB 训练 57,250 步健康（0.85–0.87 it/s）、ProtB lp 62.093 / 5-NN 58.102、MLLM 12 集 26.10%、报告 `report_vision_armB_mllm_stage4_zh.html` + `§12`。需要时再读。
 > 📦 2026-10-18 15:12（wake #151 Stage-2 DONE+切ArmB768塔+12集首跑启动）已归档 → daily-memories-vision/2026-10-18.md；**结论**：Stage-2 DONE(15.3min,loss1.4779)；lmms-eval加vision_backend开关；ai2d冒烟PASS；12集首跑@15:12启动(后证实FAILED,见#152)。
 > 📦 2026-10-17 23:37（wake #140: ArmB step31480(55%)健康,ETA~07:50 10-18）已归档 → daily-memories-vision/2026-10-17.md。
> 📦 2026-10-17 21:1x~19:5x（🔄 ArmB 监控 · wake #136~#139）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step15960→27540 健康, 0.85-0.87 it/s, ckpt@20000+10000已存, P1 ArmA 报告交付, ETA~08:00 10-18。
> 📦 2026-10-17 14:5x~17:27（🔄 ArmB 监控 · wake #133~#135）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step4540→12120 健康, P1 ArmA 中文报告交付(commit 2f15f88e), 0.86 it/s 稳态, checkpoint_10000 已存。
>
> 📦 2026-10-17 13:3x（🔄 ArmB 改 4 epoch 重启 · wake #132）已归档；**结论**：4-epoch run(steps=57250)由 wake #132 启动(PID 1203148)，wake #133 确认健康运行中(step 4540)。
>
> 📦 2026-10-17 09:1x~12:4x（wake #128~#131: ArmA 训练完成154500步 + ProtB lp=58.03±0.02%/5-NN=53.98% + Stage(iv)报告闭环(da8e9cd1) + ArmB 3-epoch 启动后被 #132 改 4-epoch）已归档 → daily-memories-vision/2026-10-17.md。
>
> 📦 **改动清单 + 10-14~16 全天流水**（wake #106~#128, ArmA 起训/12集 eval/Stage-1/1.5/2/open_clip wrapper）已归档 → daily-memories-vision/2026-10-{14,15,16}.md + ARCHIVE_OPERATOR_VISION.md；**结论**：✅ ArmA 全链路完成, 改动清单(LPT/workers/cudnn/fused)已落地, 配方不变。
> ✅ **④-4ep 基线（COMPLETE）**: ProtB 67.05±0.02% / ProtA 56.70% / zs 40.64%/72.64% / k-NN 42.35%. final_loss=0.0805, C1=0.5932, 748,404 steps, 60,545s. VERDICT: MODERATE, DIMINISHING. 详见 EXPERIMENTS_VISION.md §9.5/§9.7.
> 📦 ④-2ep / V2 Muon / V3 / ② probe / ④-4ep评测（2026-10-11~13）已归档 → daily-memories-vision/2026-10-14.md + ARCHIVE_OPERATOR_VISION.md；**结论**：V2 Muon 坍缩❌；V3 不可分辨；② probe=ceiling；④-2ep MODERATE；④-4ep 67.05% 递减确认。
> ✅ **③ 参照系说明** in `EXPERIMENTS_VISION.md §8.3`: BaiZe internal protocol labeling rules, 不可比原因逐条.

| 字段 | 值 |
|:---|:---|
| PHASE | ✅ **ArmE-R2 全链路 DONE**（①训练63400步✅ · ②ProtB lp68.236✅ · ③MLLM三阶段✅ · ④12集avg26.10%✅ · ⑤报告✅ · ⑥下一步方案报告✅）。ArmE-R2=ArmE降LR重跑(LR1e-3→5e-4+warmup2000→3000, ViT-L/14, 6源173M对)。历史最高C1=0.9664@s45240。现仅存ckpt@60000+63400(40000/50000已滚动删,训练代码无save-best机制)。ArmE(发散)/ArmD-R2/ArmB/ArmC产物未动。**WAITING=1**（16:1x方案报告已交付,无训练运行,待运维下一令）。 |
| BUDGET_USED | ~999 GPU·h (V3 ~106, ② ~1, ④-2ep ~80, ④-4ep ~134 incl. eval) |
| 更新 | **2026-10-24 22:26 (wake #255, 空唤醒)**: 顶部运维令16:1x「下一步如何提升ProtB与MLLM成绩」方案报告已于 wake#250 交付并提交(commit f5f4825a5)=`reports/report_vision_next_steps_protb_mllm_zh.html`(29419B/8节,0 script/0外链,生成器`vision/generate_next_steps_protb_mllm_report.py`)。核心结论:①12集已饱和(4臂ProtB跨度6.15pp但MLLM跨度0.34pp,逐集最大1.66pp,多数<1σ)→②单一建议=先做B4(MMBench/MMVet/MathVista+336anyres在已有ArmB/ArmE-R2 ckpt重测,~0 GPU·h)判定「评测盲区vs真失效」;顺带A3(ckpt_60000跑ProtB,~0.3 GPU·h)。③ProtB仍有~14-19pp理论空间(vs CLIP@336 82.66%)但主因是预训练。wake#251~#255 连续空唤醒复核:`git fetch` 1behind(zhulong-ops-relay非vision)→`git pull --rebase`同步0/0,无新令,工作树净,报告在位✅。📦体积:TASK=28.6KB✓/MEMORY=31.3KB✓。**WAITING=1**（待运维下一令,30min轮询）。 |

### 评测耗时归因（2026-10-15）

| 环节 | 耗时(估) | 说明 |
|:--|:--|:--|
| 训练链 (Stage-1/1.5/2) | ~4h | Stage-1 2500步(~1.5h) + Stage-1.5 20000步(~2h) + Stage-2 3500步(0.26h) + gate check/smoke(~0.3h) |
| adapter 适配 (lmms-eval wrapper) | ~3h | `lmms_eval_baize_llava.py` 编写+调试(generate_until/loglikelihood/multi-GPU LOCAL_RANK/batch_size) |
| 数据通道 (HF 下载) | ~1.5h | proxy 直连 hf.co；ai2d smoke 77MB OK；17 集首次下载是大头(预建缓存中) |
| 磁盘满崩溃 + 修复 | ~0.5h | limit50 8卡同时写 `/home`(47G)→崩；修复=迁 HF_HOME→/nas_env + 单进程预建缓存 |
| git 推送阻塞 | ~6h | `.12` 直连 github 不通(无 proxy)→ 6h 推不上来(运维已配 git config http.proxy=92.23 修复) |
| generate 输出 bug | ~0.5h | 早期 ai2d 输出解析调试(`HF_TOKEN=hf_dummy` + adapter 输出格式) |
> 📦 「运维问答·下一步工作建议 · 2026-10-08③」（1-A~1-D / 2-A~2-E / 3 GPU空窗 / 4-A~4-E 论文）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：旧版下一步建议（w384/336 AIMv2、C1-lp 消融、Stage-iv 前置、论文补 Limitations），多数已被后续 ArmA/ArmB/ArmC 工作覆盖（④-4ep 67.05%、V2全量=ArmB 62.09%、MLLM=ArmB 12集 26.10%）。需要时再读。
> 📦 「运维问答·下一步工作建议 · 2026-10-10」（④epoch缩放 / V2全量 / MLLM前置 / 论文 / w384 / 336 / C1-lp 排序）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：④epoch→④-4ep(67.05% MODERATE/DIMINISHING)；V2全量→ArmB(62.09%)；MLLM前置→ArmB Stage-iv 完成(12集 26.10% 不可分辨)。需要时再读。

## R9 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND9.md）

> 📦 R9 converged 结论（w512 选定 / scaling 幂律 acc=0.251−0.864·N^−0.090 渐近 25.1% / 瓶颈=数据量与目标函数非架构）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节。需要时再读。

## R10 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND10.md）

> 📦 R10 converged 结论（2D 拟合 M 边际全区间为负 / w384@15.36M=7.99% 全宽最高 / 加宽塔数据受限区间负收益）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节。需要时再读。

## R14 官方仓库调研（✅ 全部完成，2026-10-03）

> 📦 R14 官方仓库调研（OpenVision/AIMv2/OpenVision2/FastVLM/MambaEye/MoE-ViE 普查 + LICENSE + patch14/d24 vs 我们 patch16/d30）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节；产物 `VISION_OFFICIAL_REPOS_SURVEY.md`。需要时再读。

## E1 GPIC 规模实测（✅ 完成，2026-10-03）

> 📦 E1 GPIC 规模实测（12,537 对/tar → 全量≈100.3M / short 45% / C1 口径 18.5M·32M·118M 三类分母）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节。需要时再读。

## R11-L / R11-L2 / caption-weight / R11-F / R11-G / R11-H / R12 / 3-epoch 全部完成

> 📦 以上全部已闭合实验（R11-L 四臂→R11-L2→caption-weight→R11-F→R11-G→R11-H→R12→3-epoch 续跑）的详细流水已滚动归档 → `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（**原文未改**）。**结论以 `EXPERIMENTS_VISION_ROUND11.md` + `EXPERIMENTS_VISION_ROUND12.md` 为权威。**

**一句话结论**：R11-L 四臂（SigLIP/LocalLoss/CoCa/基线）**无一翻盘**；R11-L2 文本塔解冻（LoRA）**未翻盘**（−0.80 pp）；caption-weight 三点消融 → **caption 监督与 IN-1k 正交**；R11-F 数据源横比 → GPIC short/medium/short+medium **无显著差异**；⭐ **R11-G AIMv2 长跑翻盘**（lp@55.3M=19.76% vs 基线 7.40%，R²=0.91，渐近 >>25.1%）；R11-H 纯 AR **无翻盘**（翻盘依赖对比项）；R12 全量 58.8M 1.05 epoch lp@61.4M=17.57%（< R11-G 同 N）；3-epoch 续跑 344k/176M lp=20.27%，35 点 scaling R²=0.94，非单调 7/34，a 撞上界不可定。

> 📦 [04:20 Oct12] 全量 1-epoch 耗时估算 + AIMv2 提速归因实测（bs/nw 扫描）已归档 → daily-memories-vision/2026-10-12.md「Archived from MEMORY_VISION.md」节。**结论**：bs=64 下数据/IO 受限（GPU util~70%），~5000 img/s 是 NFS 架构上限；1 epoch ≈ 5.2–9.1h。需要时再读。

## 本唤醒流水

> 📦 [Oct 23] wake#224-228（ArmE-R2 ①训练监控 step11120→21920, spike4-8, 5条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#229（ArmE-R2 ①训练监控 step24040, C1历史最高0.9055@s23640, 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#230（ArmE-R2 ①训练监控 step26140, spike11底0.5239, 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#231（ArmE-R2 ①训练监控 step28380, spike12进行时底0.3348(迄今最深训练期底), 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#232（ArmE-R2 ①训练监控 step32580, spike13闭合+spike14进行中, 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#233（ArmE-R2 ①训练监控 step34700, spike15闭合+spike16进行中, 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#234（ArmE-R2 ①训练监控 step36920, spike16-17闭合但底反弹趋深, 1条）已归档 → daily-memories-vision/2026-10-23.md。**结论**：spike16底0.3702/spike17底0.4289(16-17反弹趋深),但vs ArmE仍379×强优。需要时再读。
> 📦 [Oct 23] wake#235（ArmE-R2 ①训练监控 step39080, spike17-18闭合, 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#236（ArmE-R2 ①训练监控 step41180, spike19进行中底0.5349, 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#237（ArmE-R2 ①训练监控 step43240, 历史最高C1=0.9186@s43180, spike19-20闭合, 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 23] wake#238（ArmE-R2 ①训练监控 step45340, 历史最高C1=0.9664@s45240, spike21进行中底0.7818, 1条）已归档 → daily-memories-vision/2026-10-23.md。需要时再读。
> 📦 [Oct 24] wake#239（ArmE-R2 ①训练监控 step51620, spike22+23闭合, C1=0.8981, 1条）已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 [Oct 24] wake#242（ArmE-R2 ①训练监控 step57980, spike25闭合, full_chain watcher启动, 1条）已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 [Oct 24] wake#243（ArmE-R2 ①训练末段监控step62240→收尾+②ProtB DONE, 2条）已归档 → daily-memories-vision/2026-10-24.md。**结论**：训练DONE 06:57:43(exit0,63400步) + ProtB lp68.236±0.0182/5-NN58.904(🏆全实验最高,vs ArmD-R2 Δlp+3.899pp)。需要时再读。
- [08:40] **wake#244**：ArmE-R2 ③MLLM 链路监控。✅Stage-1 projector DONE(07:23~07:32,exit0)→🔄Stage-1.5 LoRA step**13450/20000**(67.2%),3.36 steps/s,loss 4.1→3.6 健康下降(LoRA指令调优正常轨迹,同ArmD-R2模式),ETA~33min→~09:12。8×H100 ~16.5GB/卡全活(util 36~98%波动正常)。✅full_chain watcher活(PID 2894885,PHASE3 自动串行:Stage-1✅→Stage-1.5🔄→Stage-2→④12集)。✅发散红线全绿(Stage-1.5非训练塔,loss下降无nan)。产物未动。**下一步**:①Stage-1.5收尾(~09:12)→②Stage-2 instruct(3500步~15min,~09:27)→③④12集(8GPU并行~41min,~10:08)→④手动生成⑤报告`report_vision_armE_r2_20261022_mllm_stage4_zh.html`+`EXPERIMENTS_VISION.md §15`。主对照=ArmD-R2 avg26.12%。📦体积:TASK≈30.5KB/MEMORY≈30.5KB(均≤32KB✓,已将wake#243转指针控体积)。**WAITING: 1**。
- [10:06] **wake#245**：ArmE-R2 全链路 ✅ DONE。③Stage-1.5 DONE(~09:12)→Stage-2 DONE(~09:50,原版780k)→🔧eval bridge修复(`lmms_eval_baize_llava.py`硬编码196→ViT-L/14产出256→8GPU全崩；修3处动态`num_image_tokens`,冒烟`img_mask sum=256`✅)→④12集 DONE 10:05:44(12/12 exit0,8GPU并行~10min)→⑤报告✅`reports/report_vision_armE_r2_20261022_mllm_stage4_zh.html`+`EXPERIMENTS_VISION.md §15`。**裁定=不可分辨(边界值)**：avg26.10% vs ArmD-R2 26.12%=**−0.02pp**。🏆ProtB lp68.236%历史最高(vs ArmD-R2 Δlp+3.899pp)但MLLM下游完全持平→**容量不是MLLM下游瓶颈** + **ProtB→MLLM传递性证伪(最强烈一例)**。生成器`vision/generate_armE_r2_mllm_report.py`。⚠️vs ArmD-R2=塔+LR+warmup三变量+容量混杂。**WAITING: 1**。
- [11:45] **wake#246**：ArmE-R2 ⑤报告补齐+归档。✅生成完整7节中文HTML报告 `reports/report_vision_armE_r2_20261024_zh.html`(25.9KB,单文件自包含,无外链CDN/无script,标签配平,9表)——补齐旧版17KB缺的①训练段(里程碑/spike统计/ckpt/0nan0oom grep)与③MLLM三阶段(Stage-1/1.5/2 loss+eval bridge 196→256修复)。生成器`vision/generate_armE_r2_full_report.py`。✅EXPERIMENTS_VISION.md §15.7链到新报告(旧版标"旧版")。✅任务书归档:4个已闭合ArmE/ArmD块→ARCHIVE_OPERATOR_VISION.md(留1行指针),TASK 33.9KB→24.0KB(≤32KB✓)。所有数字来自落盘产物。📦体积:TASK=24.0KB/MEMORY≈31.2KB(均≤32KB✓)。**WAITING: 1**。


> 📦 [Oct 22] wake#221-223（ArmE-R2 ①训练监控 step4880→9060, 3条）已归档 → daily-memories-vision/2026-10-22.md。**结论**：post-warmup振荡型spike(C1底~0.16-0.35), spike4进行中, 远不如ArmE破坏性(0.0014)。需要时再读。
> 󾓶 [Oct 22] wake#220（ArmE-R2 ①训练启动+冒烟通过, 1条）已归档 → daily-memories-vision/2026-10-22.md。**结论**：停ArmE→降LR(5e-4)+warmup(3000)重跑ArmE-R2, 冒烟loss8.78→7.76单调×, 304M visual/427.6M total, 正式起训 PID 301905。需要时再读。
> 📦 [Oct 22] wake#212-219（ArmE ①训练监控→功能发散→停训, 3条）已归档 → daily-memories-vision/2026-10-22.md。**结论**：ArmE(ViT-L/14 lr=1e-3) s16000后反复spike→s29200 C1=0.0014≈随机→功能发散, 已停训归档。需要时再读。
> 📦 [Oct 21] wake#201-203（ArmD-R2 ③Stage-2 FAIL+BLOCKER recon, 3条）已归档 → daily-memories-vision/2026-10-21.md。**结论**：Stage-2 opt47数据被删→BLOCKED→运维令改用原版780k→ArmD-R2全链路DONE。需要时再读。
> 📦 [Oct 13~14] 本唤醒流水旧条目（Wake #45~#84, 含 ArmC 监控/MLLM bridge/报告刷新/④-4ep eval/外部编码器, ~15条）已归档 → daily-memories-vision/2026-10-{13,14}.md。**关键结论**：ArmC 154500步完成(ProtB 68.25%), ④-4ep ProtB 67.05%, MLLM bridge 5/5 PASSED, 外部编码器 SigLIP2 87.46% 最高。需要时再读。
> 📦 10-06~10-12 早期流水（R12b/scaling/fair-rerun/V3/②probe/④-2ep/④-4ep, ~40条）已归档 → daily-memories-vision/2026-10-{06..12}.md。**关键结论**：E1fair vs E2fair Δlp=+0.17pp indistinguishable; ④-4ep ProtB 67.05% MODERATE/DIMINISHING; ④-2ep ProtB 65.37%。需要时再读。
> 📦 [Oct 16] 本唤醒流水旧条目（Wake #108~#115, 含 precache 监控/Part B 验收/limit50 abort/12集 eval 完成/keepalive, 5条）已归档 → daily-memories-vision/2026-10-16.md。**关键结论**：✅ Part B 三项验收全通过(ai2d=0.60)；✅ 12/12 benchmarks 全量 eval 完成(ai2d 60.04%/mmmu 42.89%/realworldqa 43.01%)；consolidated_12benchmarks.json 交付。需要时再读。
> 📦 [Oct16 20:50~23:1x] Wake #118~#120（ArmA 监控+效率专项落地）已归档 → daily-memories-vision/2026-10-16.md；**结论**：ArmA step21940 健康；效率优化一揽子落地(修前2.40→修后3.35 it/s +40%, util 95-100%全卡, 三项验收全达标)。
> 📦 [00:30~17:27 Oct17] Wake #121~#135 内联流水（ArmA 监控 step59480→103400 + ArmA 训完154500步/ProtB 58.03% + ArmB 起训 step4540→12120 + P1 ArmA 中文报告交付, 6条）已归档 → daily-memories-vision/2026-10-17.md。**关键结论**：ArmA 3.35-3.37 it/s 稳定训完, ProtB lp 58.03±0.02%/5-NN 53.98%, ArmB 4-epoch 起(PID 1203148→1203161), 0.86-0.89 it/s, 无 OOM/无错误。需要时再读。
- 📦 **Wake #136~#152（2026-10-17~18, ArmB 训练监控/ProtB/12集）已滚动归档** → daily-memories-vision/2026-10-{17,18}.md。**结论**：ArmB 4-epoch 训完 57250 步；ProtB lp 62.093/5-NN 58.102；12集 avg 26.10%（首跑 4/12 失败因 nas_env 缓存缺集→改指 /tmp 修复），裁定不可分辨。需要时再读。
- 📦 **Wake #153~#158（2026-10-18~19, ArmC 训练启动+监控+③④脚本+chain watcher）已滚动归档** → daily-memories-vision/2026-10-{18,19}.md。**结论**：ArmC=两变量(min_lr 1e-4→1e-5 + wd 0.1→0.01)，57250 步训完；③④全链路脚本(stage1/1.5/2+12bench+full_chain)就绪，chain watcher 启动自动跑②③④。需要时再读。
- 📦 **Wake #162~#173（2026-10-19, ArmC 监控→训完→ProtB→MLLM→12集→全链路 DONE→idle keep-alive）已滚动归档** → daily-memories-vision/2026-10-19.md。**结论**：ArmC ①训练 DONE(57250步) + ②ProtB lp 62.332/5-NN 54.718 + ③MLLM 三阶段 DONE + ④12集 avg(除MME) **25.78%** vs ArmB 26.10% = Δ−0.32pp **裁定不可分辨**；根因=缓存路径配错(非代理)→改指 /tmp 修复全 12 集。两变量(min_lr+wd)未带来下游增益。ArmC 完整闭环，已被 ArmD 承接。需要时再读。

## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- Wakes #47/#49/#50/#51（2026-10-13）已归档至 `daily-memories-vision/2026-10-13.md`（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
