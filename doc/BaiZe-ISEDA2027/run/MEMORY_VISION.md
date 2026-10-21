# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🚀 **【ArmE ①训练 进行中 · T0=2026-10-21 22:02:33 · step14700/63400(23.2%) · 0.48 it/s · ETA≈28.4h(→~10-23 ~11:00) · 健康(loss 8.75→0.77@3020→spike1.68@4020-5020硬分片→recover0.86@6020→0.65@8200→spike0.94@11700→peak0.31@12120C1=0.746→oscillate0.49-1.07@13600-14400硬分片→recover0.49@14700/C1 0.0005→0.48@3020→dip0.19@5020→recover0.53@8200→peak0.746@12120→dip0.35@13600→recover0.63@14700/lr 8.99e-4 cosine降/0nan·oom·peak77.5GB)】** 唯一变量=视觉塔 ViT-B/16(86.2M)→**ViT-L/14(304.0M visual/427.6M total)**。⚠️ **模型名修正**：运维写 `ViT-L-14-224` 但 open_clip 3.2.0 无此 built-in→ 实用 `ViT-L-14`=224px默认(patch14/256tokens/width1024)，架构与运维意图完全一致。⚠️ **显存**：MBS=512 OOM→改 MBS=256/**accum=4 保持 GBS=8192**(峰值77.5GB,8卡H100-80GB)。⚠️ **不可避免混杂(须报告披露)**：per-micro-batch对比batch 4096→2048(MBS 512→256,OOM所致)；**GBS=8192+steps=63400保持不变**(仅1混杂)。数据/LR1e-3/min_lr1e-5/warmup2000/wd0.01/loss1:1/mask0.6/seed1234 **全同 ArmD-R2**。✅ config.json复核：n_visual=303966208(304.0M)/n_total=427616513(427.6M)/n_patches=256/patch_size=14/image_size=224 全对。✅ **ckpt@10000已保存**(checkpoint_10000.pt 5.1GB + latest.pt + open_clip_state_dict.pt 1.7GB + predictor.pt 6.6MB)。✅ **full_chain watcher已启动**(PID 339919,ppid=339915→1,等待训练完→自动②③④)。产物 OUT=`armE_20261021_aimv2_openclip_vitl14_224/`(不覆盖 armB/C/D_r2)。脚本 `run_armE_openclip.sh`+`armE_aimv2_openclip_vitl14.py`+`run_armE_full_chain.sh`+`run_armE_protb_eval.sh`+`stage{1,15,2}_train_armE.py`+`launch_12benchmarks_armE_offline.sh`+`open_clip_vitl14_1024.py` 全部就绪(Stage-2用原版LLaVA-NeXT-780k `pretrain-*.tar`×78)。**下一步**:训练完(~10-23 11:00)→②ProtB(主对照 ArmD-R2 lp64.3373/5-NN55.956)→③MLLM(Stage-2用原版780k)→④12集(对照 ArmD-R2 avg26.12%)→⑤报告 `report_vision_armE_20261021_mllm_stage4_zh.html`+`EXPERIMENTS_VISION.md §15`。**WAITING: 1**(训练中,loop唤醒监控发散红线)。

> 🎉 **【ArmD-R2 全链路 ✅ DONE · ①训练✅ · ②ProtB✅ lp64.3373/5-NN55.956 · ③MLLM三阶段✅(Stage-2 原版数据 RE-RUN 18:01) · ④12集✅ 12/12 avg26.12% · ⑤报告✅】** 裁定 = **不可分辨(边界值)**（avg 26.12% vs ArmC 25.78% +0.34pp / vs ArmB 26.10% +0.02pp，落在 22–26.5% 带）。**编码器纯对照结论已 secured**：ArmD-R2 vs ArmC(LR轴一致,仅data3→6源+epoch4→3) ProtB Δlp+2.005pp/Δ5-NN+1.238pp 双双正向；但 MLLM 下游几乎持平→**ProtB→MLLM 传递性再次证伪**。⚠️ **数据版本披露**：Stage-2 instruct 用原版 LLaVA-NeXT-780k-webdataset(`pretrain-*.tar`,738588样本,非opt47)→ ④12集Δ含「视觉塔+Stage-2数据」两重混杂,非纯编码器对照;编码器ProtB结论不受影响。
> **口径声明**：**LR 轴已回退至 ArmC 档（1e-3 / 1e-5）**；ArmD-R2 vs ArmC 的差异**仅剩 data(3→6源) + epoch(4→3)** 两项。LR 与 min_lr 同步变动，报告中不得归因单一 LR 变量。
> **训练结果**：T0=09:20:34(10-20)→完成 10:02:49(10-21)，**总耗时 ~24.7h**，稳态 0.71–0.75 it/s。**最终 step 63400**：loss 0.6750 / contr 0.6611 / patch 0.0139 / C1~0.5163 / lr 1.00e-05（=min_lr）。⭐ **全局 JOINT best = s43700 loss0.1360 / C1 0.8902**（全 log awk 确认）。**全程 0 nan/inf/oom**（grep loss=nan/inf 命中 0）。末段硬分片抖动（s58000–63400 loss 0.14–1.07 振荡、C1 0.29–0.89），同 ArmC/ArmB 模式非发散。里程碑：s2k loss2.63/C1 0.079 → s11160 loss0.4305/C1 0.6684 → s22400 loss0.2621/C1 0.7918 → s37580 loss0.2512/C1 0.7935 → ⭐s43700 loss0.1360/C1 0.8902(best) → s58800 loss0.1427/C1 0.8807(逼近) → s63400 loss0.675/C1 0.52(末段抖动)。
> **产物**：OUT=`armD_r2_20261020_aimv2_openclip_vitb16_224/`：checkpoint_60000.pt + checkpoint_63400.pt + latest.pt(=s63400) + open_clip_state_dict.pt(599MB) + predictor.pt(4.7MB) + config.json。keep_ckpts2 保留 50000+60000(已滚动删 40000)。✅ config 复核：lr=0.001/min_lr=1e-05/wd=0.01/seed=1234/mask_ratio=0.6/contrast=1.0/patch=1.0/n_visual=86192640(86.2M) 全对。⚠️ ProtB 用 open_clip_state_dict.pt(=latest=s63400 末段抖动态，同 ArmB/ArmC 口径)；末段抖动或使 final lp 略低于 best 段——属协议已知特征。
> **②ProtB✅DONE lp64.3373±0.0034/5-NN55.956 vs ArmC 62.332/54.718 = Δlp+2.005/Δ5-NN+1.238（双双升，ArmD-R2 vs ArmC 干净对照仅 data3→6源+epoch4→3 两变量；LR 轴已回退 ArmC 档）→ 编码器质量核心结论已 secured**。✅ **③Stage-2 DONE 18:01:45**（运维令2026-10-21：改用原版`LLaVA-NeXT-780k-webdataset`/`pretrain-*.tar`，738588样本，3500步，loss4.7107→1.5580，3.39 steps/s，~20min）。✅ **④12集 DONE 18:42:35**（auto-chain watcher 检测 step3500 ckpt→8 GPU 并行，12/12 exit 0，~41min，avg 26.12%）。✅ **⑤报告 DONE**：`reports/report_vision_armD_r2_20261020_mllm_stage4_zh.html` + `EXPERIMENTS_VISION.md §14`，生成器 `vision/generate_armD_r2_mllm_report.py`。
> ✅ **善后**：上一轮 7 个发散产物全在 `armD_20261019_DIVERGED_archive/`；r2 全链路脚本就绪；full_chain watcher PID 4063278(ppid=1) 自动串行②③④。⑤报告需手动生成 `report_vision_armD_r2_20261020_mllm_stage4_zh.html` + `EXPERIMENTS_VISION.md §14`。
> 📌 **四阶段链**（串行）：训练→②ProtB→③MLLM(Stage-1 2500/1.5 LoRA 20000/2 3500)→④12集(离线缓存)→⑤报告 `report_vision_armD_r2_20261020_mllm_stage4_zh.html`+`EXPERIMENTS_VISION.md §14`。**✅ 全链路完成**。

> 📦 **wake #206 (2026-10-21 20:31, ArmD-R2 全链路状态复核)** 已归档 → daily-memories-vision/2026-10-21.md；**结论**：2026-10-21 运维令(Stage-2改原版780k)全完成并已提交(commit 9dce3f3d0)；④12集 avg26.12%✓；git 同步。需要时再读。

> 📦 **wake #207 (2026-10-21 22:0x, ArmE 启动: 脚本创建/显存probe/MBS256决策/烟雾通过/正式起训 T0=22:02:33)** 已归档 → daily-memories-vision/2026-10-21.md；**结论**：ArmE 唯一变量=视觉塔 ViT-B/16→ViT-L/14(304.0M visual/427.6M total)，MBS=256/accum=4 保 GBS=8192+steps63400(仅1混杂=per-micro-batch对比batch 4096→2048)，烟雾 STEPS=100 通过，正式起训。需要时再读。
> 📦 **wake #208 (2026-10-21 23:09, ArmE 首次监控 step1880/3.0%, 健康, 0.47it/s)** 已归档 → daily-memories-vision/2026-10-21.md；**结论**：ArmE 首次监控确认训练健康(loss单调降/C1单调升/0nan/peak77.5GB)，配置单变量守住。需要时再读。
> **本唤醒流水 [wake #212, 2026-10-22 04:1x]**：✅ **ArmE ②下游评估链脚本全部就绪**。训练仍在进行(~step10300/63400, 16.3%, ETA~31h, 健康)。**本轮工作 = 创建 ArmE 下游全链脚本(训练完后可直接执行)**：①**新建文件**(4个Python已cp+sed自armD_r2版,全py_compile✓)：`open_clip_vitl14_1024.py`(bridge,1024-d/256tokens)、`stage1_train_armE.py`/`stage15_train_armE.py`/`stage2_train_armE.py`(768→1024dim/196→256tokens/armD_r2→armE路径,无残留ArmD引用)。②**新建Shell脚本**(3个,bash -n✓)：`run_armE_protb_eval.sh`(传`--model ViT-L-14`)、`mllm_bridge/launch_12benchmarks_armE_offline.sh`(`--vision_backend armE`)、`run_armE_full_chain.sh`(编排:等训练→ProtB→Stage1/1.5/2→12集→报告)。③**共享基础设施改造(向后兼容,3文件)**：`armB_protb_eval.py`→`load_armB_visual`加`model_name`参数+call site传`args.model`(默认ViT-B-16不变)；`lmms_eval_baize_llava.py`→加`armE`分支(import `create_baize_vitl14_1024`/`BAIZE_VITL14_WIDTH`);`run_lmms_eval_r2.py`→加`CKPT_ARME`/`STAGE2_BASE_ARME`/`RESULTS_DIR_ARME`常量+`armE`到choices+elif分支。④**验证**：7个Python全py_compile✓,3个Shell全bash -n✓,无armD_r2/armD 残留(12bench仅2个rerun脚本名提示=不影响)。⑤**基线对照**：ArmD-R2 ProtB lp64.3373/5-NN55.956 / MLLM 12集avg26.12%。下一步：训练完(~10-23 10:30)→ops启动`run_armE_full_chain.sh`→自动串行②③④→⑤报告。**WAITING: 1**。📦 体积：归档wake#209→daily-10-22,MEMORY≈30.8KB≤32KB✓。
> **本唤醒流水 [wake #213, 2026-10-22 06:37]**：✅ **ArmE ①训练 第6次监控唤醒 · 健康(无发散) · ckpt@10k 已存 · full_chain watcher 活跃**。①**进度** step**14700/63400**(23.2%)，t≈515min(T0=22:02:33 10-21)，稳态 **0.48 it/s**，ETA≈28.4h→**~10-23 11:00**。②**loss 轨迹**(每~2000步采样)：s20 loss8.75/C1 0.0005 → s3020 loss0.77/C1 0.479(低点) → s4020-5020 硬分片抖动(loss spike 1.59-1.72, C1 dip 0.19-0.21) → s8200 loss0.65/C1 0.53(恢复) → s12120 loss0.31/C1 0.746(**新高!**) → **s13600-14400 三次硬分片抖动**(loss 0.49→1.07→0.85→1.04→0.77, C1 0.63→0.35→0.44→0.35→0.48) → **s14700 loss0.49/C1 0.63(恢复中)**。s13600-14400段振荡同ArmB/C/D模式(非发散,每次spike后均恢复)。patch loss稳定0.019-0.039。lr=8.99e-04(cosine降)。③**0 nan/inf/oom**：grep 'loss=nan'=0/'loss=inf'=0；广义 grep 1命中=日志头"confound"标注行(已知混杂,非异常)。peak=**77.5GB**稳定。④**GPU**：8×H100 ~76GB/81.5GB全活健康(hostname=whag0pgpuap12=.12✓)。⑤**DDP**：launcher PID 1535858(ppid=1,etimes~30907s≈8.6h)+8 worker全活。⑥✅**ckpt@10000已保存**(checkpoint_10000.pt 5.1GB+latest.pt+open_clip_state_dict.pt 1.7GB+predictor.pt 6.6MB+config.json)。⑦✅**config.json复核**：n_visual=303966208(304.0M)/n_total=427616513(427.6M)/n_patches=256/patch_size=14/model_name=ViT-L-14 全对→**单变量(仅视觉塔ViT-B/16→ViT-L/14)守住**。⑧✅**full_chain watcher存活**(PID 339919,ppid=339915→1,/tmp/armE_full_chain.log PHASE0轮询5min,最近[06:37:02]"Training still running")。⑨ArmD-R2/ArmB/ArmC产物未动(对照基线)。无新运维令(顶部仍10-21 20:4x ArmE块)。下一步：loop继续监控；ckpt@20k后核查；训练完(~10-23 11:00)→②ProtB→③MLLM→④12集→⑤报告。**WAITING: 1**。📦 体积：TASK=28.8KB / MEMORY=29.1KB（归档wake#210+#211→daily-10-22, 均≤32KB✓）。
> 📦 **wake #210 (2026-10-22 01:3x, ArmE 第3次监控 step6020/9.5% 健康)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：step6020 健康,0.48it/s,s4020-5020硬分片抖动后完全恢复,0nan。需要时再读。

> 📦 **wake #211 (2026-10-22 02:4x, ArmE 第4次监控 step8200/12.9% 健康 ckpt@10k临近)** 已归档 → daily-memories-vision/2026-10-22.md；**结论**：step8200 健康,C1新高0.531超越spike前,0nan,ckpt@10k临近。需要时再读。
>

>
> 📦 **wake #205 (2026-10-21 19:0x, ArmD-R2 全链路收尾→⑤报告生成完成)** 已归档 → daily-memories-vision/2026-10-21.md；**结论**：⑤报告 `report_vision_armD_r2_20261020_mllm_stage4_zh.html`+§14 DONE；裁定 avg26.12% 不可分辨(边界值)；编码器 ProtB Δlp+2.005pp/Δ5-NN+1.238pp 已 secured。需要时再读。
>
> 📦 **ArmD 原始轮（LR 2e-3, 2026-10-19~20）已归档** → daily-memories-vision/2026-10-20.md + ARCHIVE_OPERATOR_VISION.md；**结论**：ArmD(四变量: data3→6源+epoch4→3+lr→2e-3+min_lr→2e-5) 训练至 step21820 发散(loss0.45→9.3, C1 0.589→0.0002), wake#180 停止保全 ckpt_10000, 7 产物移入 DIVERGED_archive/。**已被 ArmD-R2 承接**(LR 轴回退 1e-3/1e-5)。
>
> 📦 **wake #180 (07:5x, ArmD 发散发现+停止保全 ckpt_10000)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #181 (09:2x, ArmD-R2 起训 T0=09:20:34 + 善后+建脚本+watcher)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #182 (12:0x, ArmD-R2 监控 step7980, 0.84 it/s 早期较快段)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #183 (13:1x, ArmD-R2 监控 step11020, ETA 修正稳态 0.78 it/s, 训练完成~10-21 08:10)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #184 (14:32, ArmD-R2 监控 step14480, s14240 新 best loss0.444/C1 0.659 超上轮)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #185 (15:56, ArmD-R2 监控 step18080, 过发散点 s16000 零发散确认)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #186 (17:12, ArmD-R2 监控 step21240, 全局best s11160 loss0.4305/C1 0.6684)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #188 (19:46, ArmD-R2 监控 step28780, 全局joint best s22400 loss0.2621/C1 0.7918 确认, s28k spike 已恢复非发散, 红线全过, 脚本复核 r2 路径/LR 全对, ETA 训练~10-21 08:25/全链路~13:15)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #189 (21:06, ArmD-R2 监控 step32000/50.5%, 稳态0.76 it/s, 红线全过, 半程零发散确认)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #190 (22:26, ArmD-R2 监控 step35500/56%, 0.75it/s, 红线全过, 全局joint best s22400 不变)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #192 (00:55, ArmD-R2 监控 step41820/66.0%, 红线全过, 全局best s37580 不变)** 已归档 → daily-memories-vision/2026-10-21.md。
> 📦 **wake #193 (02:10, ArmD-R2 监控 step44960/70.9%, 新全局best s43700 loss0.1360/C1 0.8902 确认, 红线全过)** 已归档 → daily-memories-vision/2026-10-21.md。

> 📦 **wake #194 (03:30, ArmD-R2 监控 step49280/77.7%, 红线全过, 全局best s43700 不变)** 已归档 → daily-memories-vision/2026-10-21.md。
> 📦 **wake #195 (04:45, ArmD-R2 监控 step52440/82.7%, s50000 ckpt 落盘, 红线全过)** 已归档 → daily-memories-vision/2026-10-21.md。
> 📦 **wake #197 (07:34, ArmD-R2 监控 step58780/92.7%, s55620 spike完全恢复确认, 红线全过)** 已归档 → daily-memories-vision/2026-10-21.md。
> 📦 **wake #198 (09:00, ArmD-R2 监控 step61640/97.2%即将收尾, s60000 ckpt已落盘, 末段抖动非发散)** 已归档 → daily-memories-vision/2026-10-21.md。
> **本唤醒流水 [wake #204, 2026-10-21 17:4x]**：🔄 **Stage-2 RE-LAUNCH（运维令2026-10-21「让vision使用原版」）**。opt47 instruct集被NFS删除→上轮Stage-2 0样本FAILED；本轮改用原版`LLaVA-NeXT-780k-webdataset/pretrain-*.tar`。✅ 脚本改2处(stage2_train_armD_r2.py L53 DATA_DIR、L118 glob pretrain-*.tar)已落地+grep复核。✅ 起跑前自检：8卡全空闲(4MiB)、Stage-1.5 step20000 ckpt在位(projector.pt17MB+adapter528MB)、失败output dir空。✅ 数据格式实测兼容：pretrain-0.tar json=`{texts:[{role:user,<image>+多选QA},{role:assistant,"C"}],media,name}`真实instruct(非caption)，与`LLaVANeXTInstructDataset`分组逻辑(image_N前缀)匹配。✅ 索引：`[Rank0] Dataset: 738588 samples from 78 tars`；独立78 tar全索引779111 json/738590 img/0 bad(285s)。✅ 训练健康：T0=17:41:32，step50/3500 loss4.7107 / 2.35 steps/s / GPU15.9GB / **ETA~18:06**。✅ 新建`run_armD_r2_stage2_only.sh`(Stage-2 only,不重跑前序)+auto-chain watcher(待step3500 ckpt→④12集)。⚠️ wake#203曾误判原版=pretrain/caption→本轮实测纠正(原版pretrain-*.tar实为instruct)。📦 体积：TASK=29.4KB / MEMORY=30.0KB(均≤32KB✓,无需归档)。下一步：等Stage-2完成(~18:06)→auto-chain跑④12集→手动⑤报告(须标注instruct数据版本差异)。

> 📦 **wake #199 (10:31, ArmD-R2 训练完成@10:02:49 → ②ProtB eval运行中, 全程0nan/inf/oom)** 已归档 → daily-memories-vision/2026-10-21.md。


> 📦 **wake #196 (06:06, ArmD-R2 监控 step55620/87.9%, spike峰段非发散, 红线全过)** 已归档 → daily-memories-vision/2026-10-21.md。




> 📦 **wake #191 (23:40, ArmD-R2 监控 step38820/61.2%, 新全局joint best s37580 loss0.2512/C1 0.7935, 红线全过)** 已归档 → daily-memories-vision/2026-10-21.md。

> 📦 wake #187 (18:28, ArmD-R2 监控 step24560, 全局best C1 0.7918@s22400 超原best) 已归档 → daily-memories-vision/2026-10-20.md。


> 📦 wake #179 (06:2x, ArmD 监控 keep-alive) 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 wake #177 (03:5x, ArmD 监控 keep-alive) 已归档 → daily-memories-vision/2026-10-20.md。

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
| PHASE | 🔄 **ArmD-R2 ③Stage-2 RUNNING(wake#204 17:41,运维令2026-10-21「让vision使用原版」)**。ArmD-R2=两变量(data3→6源+epoch4→3,LR轴已回退ArmC档1e-3/1e-5)。①训练✅DONE(10:02:49,63400步,24.7h零发散) ②ProtB✅DONE lp64.3373/5-NN55.96(vs ArmC 62.332/54.718 Δ+2.005/+1.238) ③Stage-1✅/Stage-1.5✅(step20000)/**Stage-2🔄RE-LAUNCHED@17:41:32**(原版LLaVA-NeXT-780k/pretrain-*.tar,738588样本,2.35steps/s,ETA~18:06) ④12集⏸auto-chain watcher待Stage-2 ckpt ⑤报告⏸。BLOCKER已解除(opt47被删→改用原版)。⚠️汇报口径:Stage-2 instruct数据 opt47→原版quick-start子集,④12集vs ArmB/ArmC须标注此差异(编码器结论不受影响)。 **WAITING=1**（③Stage-2运行中）。 || ERROR_COUNT | 20（同前） |
| BUDGET_USED | ~999 GPU·h (V3 ~106, ② ~1, ④-2ep ~80, ④-4ep ~134 incl. eval) |
| 更新 | **2026-10-19 13:58 (wake #167)**: 🔄ArmC 巡检健康(临近训完)。step **55640/57250(97.2%)**(+3580自#166, ~1.4h), loss=0.13(contr=0.11 patch=0.016, 末段硬分片抖动0.077-0.203非坍缩,同ArmB模式), C1~0.83-0.92(正常), lr=1.21e-05(cosine→min_lr=1e-5), 0.78it/s(稳态), 7/8×H100 100%@50559MiB(card1批间偶0%) peak50.4GB 无OOM, t=1192.5min(19.9h)。✅grep error/nan/oom/traceback=0；✅盘上核(OUT=/nas_train/app.e0031982/datasets/baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224/) ckpt@40000(08:17)+50000(11:51)+latest+open_clip_state_dict(598MB)+predictor(4.7MB)+config.json 均在(10000/20000/30000已滚动删, keep-ckpts2), final@57250~14:32；✅**config.json复核**: lr=0.001/min_lr=1e-05/wd=0.01/seed=1234/mask_ratio=0.6/contrast_weight=1.0/patch_loss_weight=1.0/n_visual=86192640(86.2M,与ArmB一致) → **只有 min_lr+wd 两变量** ✓；✅ArmB OUT dir未被触碰(ckpt_50000/57250 10-18完好)。✅**chain watcher PID 4131476存活**(ppid=1, /tmp/armC_full_chain.log PHASE0轮询5min, 最近[13:55:08]\"Training still running\"), 训练DDP worker PID 4154295等存活。⚠️日志行前缀`[ArmB]`=py脚本logger名硬编码, 实为ArmC run, 报告须注明。ETA (57250−55640)/0.78≈0.57h→~14:32训完；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒~10-19 19:00全链路完成。下一步: chain自动跑②→③→④；下一唤醒查②ProtB结果(lp/5-NN对比ArmB 62.093/58.102、④-4ep 67.05)+③④进度→生成报告 report_vision_armC_20261018_mllm_stage4_zh.html + EXPERIMENTS_VISION.md §13。📦 体积：TASK=29.7KB / MEMORY=30.4KB（均≤32KB✓，无需归档）。 |

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

- [05:27] **wake#212**：ArmE ①训练 监控 step12640/63400(19.9%)，0.48 it/s，ETA≈29.6h(→~10-23 07:40)。loss轨迹：s3020 0.77/C1 0.48→s4020-5020 spike1.68/C1dip0.19→s8200 0.65/C1 0.53→s11700 spike0.94/C1dip0.41→s12120 peak C1 0.746→s12640 0.51/C1 0.62(恢复中)。0nan/inf/oom。peak77.5GB。✅ckpt@10000已保存(checkpoint_10000.pt 5.1GB+open_clip_state_dict.pt 1.7GB)。✅config.json复核n_visual=303966208(304.0M)/n_patches=256全对。✅**full_chain watcher已启动**(PID 339915,ppid=1,等训练完→自动②ProtB→③MLLM→④12集)。修正full_chain脚本变量描述(ArmD"FOUR vars"→ArmE"SINGLE VAR=vit tower only")。Stage-2用原版LLaVA-NeXT-780k `pretrain-*.tar`×78确认。脚本全部就绪。ArmD-R2/ArmB/ArmC产物未动。📦 体积：TASK=29.5KB / MEMORY≈31.5KB(归档wake#201-203→daily-10-21, 均≤32KB✓)。
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
