# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

> 🆕 **【OCR 合成数据 10M ✅ DONE · wake#275 · 2026-10-26 04:0x】** 用户令(22:4x)。全量 DONE：ok=9,999,999 fail=0 · 2000 tars · 470GB(0.5046TB) · 893.6 img/s · 3h6m30s · 8类 cat_counts==plan。交付物：数据本体+index.jsonl(9.999M)+STATS/VALIDATION/DATASET_CARD/MANIFEST+preview_200.html+preview_10k.tar+报告 `reports/report_vision_ocr_synth10m_zh.html`(15754B)+5脚本`vision/ocr_synth/*.py`。加载器兼容已验 build_gpic_loader→(16,3,224,224)。**两处质量偏差(如实披露,未掩盖)**：①文本sha1去重 **2.4486%>1%目标**(244,858多余,合成文本组合空间有限)；②泄漏 **113命中**(leak_rate1.16e-5,短串巧合如0.29→029非真实泄漏)。**✅ 已裁定：接受现状**（2026-10-28 用户直令·accept as-is·不重生成/不过滤）。本轮只造数据不启encoder训练(等用户批预算)。详见 daily-memories-vision/2026-10-26.md。

## 状态头

> **本唤醒流水 [wake #392, 2026-10-30 05:06]**：空唤醒·补心跳防判死。上次心跳 wake#391@10-30 04:35 距今 ~31min。运维令区全部✅DONE/已归档/已闭合，无新指令。ops/inbox.md RUN_ID 224=pretrain令(非vision)。git pull --rebase 成功(Already up to date)。📦 体积：TASK=24093B(23.5KB)/MEMORY=29972B(29.3KB) 均≤32KB✓。**仍在等**：②OCR SFT 预算 ③MMVet/MathVista key ④336+anyres。**未完成指令：无** ⇒ **WAITING: 1**。
> 📦 wake#380/#378/#372/#371/#370/#369/#368 (2026-10-29 15:08~22:12, 7轮空唤醒·补心跳防判死·均无新令·交付物在位·体积均≤32KB) 已归档 → daily-memories-vision/2026-10-29.md。需要时再读。
> 📦 wake#367/#366/#365/#364/#363 (2026-10-29 12:24~14:35, 5轮空唤醒·补心跳防判死·均无新令·交付物在位·体积均≤32KB) 已归档 → daily-memories-vision/2026-10-29.md。需要时再读。
> 📦 wake#362/#360/#358/#357/#355/#354/#352/#351/#348 (2026-10-29 04:02~11:20, 9轮空唤醒·均无新令·补心跳防判死·交付物在位·体积均≤32KB) 已滚动归档 → daily-memories-vision/2026-10-29.md。需要时再读。
> 📦 wake#340~#346 (2026-10-28 23:37~10-29 02:53, 7轮空唤醒·均无新令·补心跳防判死·交付物在位·体积均≤32KB) 已滚动归档 → daily-memories-vision/2026-10-{28,29}.md。需要时再读。
> 📦 wake#331~#339 (2026-10-28 18:40~23:05, 8轮空唤醒·均无新令·补心跳防判死·交付物在位·体积均≤32KB) 已滚动归档 → daily-memories-vision/2026-10-28.md。需要时再读。
> 📦 wake#314~#330 (2026-10-28 00:59~18:08, 17轮·wake#330=执行OCR 10M质量裁定令/其余空唤醒·均无新令·体积均≤32KB) 已滚动归档 → daily-memories-vision/2026-10-28.md。需要时再读。
> 📦 wake #311/#310/#309/#308/#307/#306/#305/#304/#302/#301/#300/#299/#298/#297/#296/#295/#294 (2026-10-27 02:42~23:50, 18 轮空唤醒·均无新令·补心跳防判死·交付物在位·体积均≤32KB) 已滚动归档 → daily-memories-vision/2026-10-27.md。需要时再读。
> 📦 wake #290 (2026-10-26 23:02, 空唤醒·无新令·补心跳防判死·滚动wake#258-270旧指针控体积·inbox RUN_ID221=只读probe非vision令·体积均≤32KB) 已归档 → daily-memories-vision/2026-10-26.md。需要时再读。
> 📦 wake #289 (2026-10-26 21:50, 空唤醒·无新令·补心跳防判死·inbox RUN_ID216只读probe·体积均≤32KB) 已归档 → daily-memories-vision/2026-10-26.md。需要时再读。
> 📦 wake #288 (2026-10-26 20:35, 空唤醒·无新令·补心跳防判死·交付物位置澄清4报告在项目级reports) 已归档 → daily-memories-vision/2026-10-26.md。需要时再读。
> 📦 wake #287 (2026-10-26 19:24, 空唤醒·无新令·补心跳防判死·inbox RUN_ID210只读probe·体积均≤32KB) 已归档 → daily-memories-vision/2026-10-26.md。需要时再读。
> 📦 wake #286/#285/#284/#283/#280/#279 (2026-10-26 09:2x~18:12, 均空唤醒补心跳/归档收尾) 已滚动归档 → daily-memories-vision/2026-10-26.md。需要时再读。

> 📄 **【路线①细化 · OCR 专项 SFT 执行方案报告 ✅ DONE · wake#272 · 2026-10-25 21:0x】**（9节方案报告 `reports/report_vision_ocr_sft_plan_zh.html`(22706B/0 script/0外链/标签配平)+生成器+EXPERIMENTS §17；回答四问：中英配比A英6:中3:混1/B中英1:1·公式三通道(纯公式5%/正文夹公式3%/混排2%)·类别P0-P2·SFT=ArmE-R2 step3500+LoRA r64+LR1e-5+70:30混780k；判据 OCRBench≥+2pp + 决策树）全文已归档 → daily-memories-vision/2026-10-25.md。需要时再读。
> 📦 **wake #278 (2026-10-26 07:49, 空唤醒复核·无未完成指令·补心跳防判死·10M数据集+脚本+报告在位·git同步)** 已归档 → daily-memories-vision/2026-10-26.md。需要时再读。

> 📦 wake #277 (2026-10-26 06:32, 体积维护归档·22:4x块归档+MEMORY滚动·无未完成指令) 已归档 → daily-memories-vision/2026-10-26.md。需要时再读。


> 📦 wake#275 (2026-10-26 04:0x)：10M 全量 DONE 收尾(9,999,999/fail=0/470GB+报告15754B+§18+commit `vision ocr-synth:`；两处偏差如实记录)。流水原文 → daily-memories-vision/2026-10-26.md（亦见顶部 🆕 块）。**未完成指令:无**。
> 📦 wake#276 (2026-10-26 05:22)：空唤醒复核·22:4x 交付完整性确认+任务书标✅DONE。流水原文 → daily-memories-vision/2026-10-26.md。**未完成指令：无**。

> 📦 wake#273 (2026-10-25 22:03)：空唤醒复核·git 同步 0/0·19:5x+17:5x 两运维令仍✅DONE·四交付物在位(ocr_sft_plan 22706B/ocr_synthdata 29177B+两.py)。流水原文 → daily-memories-vision/2026-10-25.md。**未完成指令：无**。



> 🎉 **【ArmE-R2 全链路 ✅ DONE · ①训练✅(63400步,~37h) · ②ProtB✅ lp68.236±0.0182/5-NN58.904(🏆全实验最高!) · ③MLLM三阶段✅(Stage-2 09:50) · ④12集✅ 12/12 avg26.10% · ⑤报告✅】** 裁定 = **不可分辨(边界值)**（avg 26.10% vs ArmD-R2 26.12% = **−0.02pp** / vs ArmC 25.78% = +0.32pp / vs ArmB 26.10% = −0.00pp）。**编码器🏆历史最高已 secured**：ProtB lp 68.236% vs ArmD-R2 **Δlp+3.899pp**/Δ5-NN+2.948pp。**但MLLM下游完全持平** → ViT-L/14(304M)比B/16(86M)大3.5×，MLLM 12集平均却−0.02pp → **容量不是MLLM下游瓶颈**。**ProtB→MLLM传递性证伪（最强烈一例）**：编码器4-6pp ProtB优势完全未转化为MLLM下游增益。🔧 eval bridge修复：lmms_eval_baize_llava.py 硬编码196(ViT-B/16)→ViT-L/14产出256→8GPU全崩；已修3处动态num_image_tokens。ArmE-R2 = ArmE降LR重跑(LR 1e-3→5e-4+warmup 2000→3000, ViT-L/14, 6源173M对, 63400步, lr5e-4, C1最高0.9664@s45240)。⚠️ vs ArmD-R2 = 塔(B→L)+LR+warmup**三变量**+容量混杂→报告须分开。报告(完整7节)=reports/report_vision_armE_r2_20261024_zh.html(25.9KB,含①训练+③MLLM三阶段)+EXPERIMENTS_VISION.md §15。旧版17KB(report_vision_armE_r2_20261022_mllm_stage4_zh.html)保留备查。生成器=vision/generate_armE_r2_full_report.py。📄**下一步方案报告(运维令16:1x)**=`reports/report_vision_next_steps_protb_mllm_zh.html`(21.1KB,8节,0 script/0外链,生成器`vision/generate_next_steps_protb_mllm_report.py`)。核心结论:12集已饱和(逐集最大跨度1.66pp,多数<1σ)→单一建议=先做B4(MMBench/MMVet/MathVista+336anyres在已有ArmB/ArmE-R2 ckpt重测,~0 GPU·h)。🔬**A3 ckpt_60000 ProtB(wake#266,2026-10-25 12:38)**✅DONE:lp68.3067±0.0155/5-NN59.002 vs final(63400)68.236±0.0182/58.904 → Δlp+0.071pp/Δ5-NN+0.098pp(均<0.3pp不可分辨,逐seed一致+0.07pp)⇒「末段抖动/best段省1-2pp」假设**证伪**(末段稳定;~14pp到CLIP@336缺口非ckpt选择可回收→强化报告主结论:须预训练侧改动)。🔬**B4(wake#264自发执行报告推荐项)**:MMBench en_dev_static双臂✅(ArmB24.14%/ArmE-R2 23.88%,Δ−0.26pp→确认MCQ评测盲点);MMVet/MathVista**阻塞(需OPENAI_API_KEY,无法伪造)**;336+anyres**阻塞(需工程改造+scope批准)**→3/4组件待运维裁决。**未完成指令:无**(16:1x报告DONE/10:3x报告DONE;B4系自发非运维令)。**WAITING: 1**。
> 🔬 **【OCR 合成数据调研报告 ✅ DONE · wake#271 · 2026-10-25 18:57】** 用户令(17:5x)全链路交付：①实测四臂 OCR 四集（OCRBench 1.60-1.80% / DocVQA 7.35-7.58% / ChartQA 12.16-12.92% / InfoVQA 16.18-17.09%；四臂跨度 ≤1pp，与 ArmE-R2 编码器 ProtB 68.2% 最高形成对比 → 缺位在专项数据/任务对齐，非编码器容量）；②经代理检索 arXiv 摘要(2026-10-25)覆盖 7 类 18 法（SynthTIGER/SynthText/trdg/Donut-SynthDoG/UDOP/Pix2Struct/Nougat/mPLUG-DocOwl/dots.ocr/ChartQA/Chart-to-Text/olmOCR/PaddleOCR/Visual-RFT/自训练伪标注/im2latex；GOT-OCR2.0 检索未命中，标「未查到」）；③报告 `reports/report_vision_ocr_synthdata_zh.html`（29177B/8节/0 `<script>`/0 外链/标签配平/≥15KB）；④生成器 `vision/generate_ocr_synthdata_report.py`；⑤EXPERIMENTS §16 指针。单一建议=路线①（低成本合成 OCR 识别对 50-200 万 + 专项 SFT，判据 OCRBench ≥+2pp）。本轮只调研+写报告，未启训练/未动产物/未伪造 API key。**未完成指令：无**。**WAITING: 1**。

> **本唤醒流水 [wake #271, 2026-10-25 18:57]**：🔬 执行运维令 17:5x。读四臂 consolidated_12benchmarks.json 量化四集 → 经代理 172.19.92.25:13128 检索 arXiv 摘要（修正多个初版错误 ID）→ 写 generate_ocr_synthdata_report.py → 修 3 处写入缺陷（`\u9700` 被写成截断 U+FFFD、Nougat `effect=` 行丢失、f-string `{B,C}` 未转义）→ 生成 HTML 29177B 自检全过 → 写 §16/本块/日流水 → commit `vision ocr-report:`。数字全自溯源；外部数字标「未查到」不伪造。**未完成指令：无** ⇒ **WAITING: 1**。



> 📦 **ArmD-R2 全链路 DONE**（①训练✅24.7h · ②ProtB lp64.3373/5-NN55.956 · ③MLLM✅ · ④12集avg26.12% · ⑤报告✅）详细状态块已归档 → `daily-memories-vision/2026-10-24.md`「ArmD-R2 状态块归档」节；**结论**：ArmD-R2 vs ArmC(LR轴一致,仅data3→6源+epoch4→3) ProtB Δlp+2.005pp 双正向但 MLLM 持平→传递性首次证伪；Stage-2 用原版780k(非opt47)故④含数据混杂,编码器ProtB结论不受影响。详见 `EXPERIMENTS_VISION.md §14` + `reports/report_vision_armD_r2_20261020_mllm_stage4_zh.html`。需要时再读。

> 📦 wake #242 (2026-10-24 05:04, ArmE-R2 ①训练第7次监控 step60160/94.9% 健康·ckpt@60000) 已归档 → daily-memories-vision/2026-10-24.md；**结论**：末段C1~0.93逼近历史最高0.9664，0nan/0oom，watcher活跃，ETA~07:00。需要时再读。

> 📦 wake #247 (2026-10-24 12:57, ArmE-R2 ⑤报告复核) 已归档 → daily-memories-vision/2026-10-24.md；**结论**：报告(26.5KB,7节,0script/0外链)+§15链接+任务书归档(33.9→24.0KB)+commit e8dc74489 全闭合。需要时再读。
> 📦 wake #248 (2026-10-24 14:12, ArmE-R2 二次复核·数据纪律交叉验证通过) 已归档 → daily-memories-vision/2026-10-24.md；**结论**：报告26.5KB/7节数字逐项溯源通过(ProtB/12集/训练log/eval bridge)，0 N/A/0编造，git同步。需要时再读。
> 📦 wake #249 (2026-10-24 15:1x, ArmE-R2 运维令10-24三次复核·闭合旧版标注残留) 已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 wake #251 (2026-10-24 17:41, 空唤醒复核·纠正WAITING 0→1省token) 已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 wake #252 (2026-10-24 18:54, 空唤醒复核·清ahead-2 ops-relay提交) 已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 wake #253 (2026-10-24 20:03, 空唤醒复核·归档wake#223) 已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 wake #254 (2026-10-24 21:14, 空唤醒复核·16:1x报告仍DONE无新令) 已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 wake #255 (2026-10-24 22:26, 空唤醒复核·归档wake#247释放体积) 已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 wake #256 (2026-10-24 23:42, 空唤醒复核·归档wake#248释放体积) 已归档 → daily-memories-vision/2026-10-24.md。需要时再读。
> 📦 wake #257 (2026-10-25 00:57, 空唤醒复核·16:1x报告仍DONE无新令) 已归档 → daily-memories-vision/2026-10-25.md。需要时再读。
> 📦 wakes #258–#270 (2026-10-25 02:07~17:46, 13 轮空唤醒复核·16:1x+10:3x 报告均 DONE·无新令·B4 3/4 阻塞待运维·A3 ckpt_60000 假设证伪·心跳重置判死时钟) 已归档 → daily-memories-vision/2026-10-25.md。需要时再读。





> 📦 wake#272 归档：wakes #205-#218 + ArmB/ArmC/ArmD 原始轮 + 2026-10-17/18 流水指针块（均已在对应 daily-memories-vision/<日期>.md / ARCHIVE_OPERATOR_VISION.md，本块仅为指针）已从 MEMORY 滚出 → daily-memories-vision/2026-10-25.md「wake#272 归档」节。结论未变。需要时再读。
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
| PHASE | ✅ **ArmE-R2 全链路 DONE**（①训练63400步✅ · ②ProtB lp68.236✅ · ③MLLM三阶段✅ · ④12集avg26.10%✅ · ⑤报告✅ · ⑥下一步方案报告✅）。ArmE-R2=ArmE降LR重跑(LR1e-3→5e-4+warmup2000→3000, ViT-L/14, 6源173M对)。历史最高C1=0.9664@s45240。现仅存ckpt@60000+63400(40000/50000已滚动删,训练代码无save-best机制)。ArmE(发散)/ArmD-R2/ArmB/ArmC产物未动。**WAITING=1**（OCR 10M质量偏差✅已裁定:接受现状; 16:1x方案报告已交付,无训练运行,待运维下一令/OCR SFT预算）。 |
| BUDGET_USED | ~999 GPU·h (V3 ~106, ② ~1, ④-2ep ~80, ④-4ep ~134 incl. eval) |
| 更新 | **2026-10-30 05:06 (wake #392, 空唤醒·补心跳防判死)**：运维令区全部✅DONE/已归档/已闭合，无新指令。ops/inbox.md RUN_ID 224=pretrain令(非vision)。git pull --rebase 成功(Already up to date)。体积 TASK=24093B/MEMORY=29972B 均≤32KB✓。**未完成指令：无**。**WAITING=1**（待运维下一令/批准 OCR SFT 预算/API key/336 scope 裁决，30min轮询）。 |

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
