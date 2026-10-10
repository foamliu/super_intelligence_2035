# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

## 当前状态
- STAGE: **P-8 已暂停 · A/B Arm B 运行中 step200/300 ⚗️ · 决策已定** — Arm A ✅(249,276 tok/s, loss@300=3.980, VRAM 52.3GB)；Arm B step200/300, 257,631 tok/s(preliminary steps100-200), B/A=**1.0335**(❌<1.12), VRAM peak 70,591MiB=68.9GB(✅<76GB), loss@200=4.467(与A step200=4.473一致), 0 NaN。三判据: 吞吐FAIL / VRAM PASS / loss PASS → **恢复MBS=2/GBS=1024**。ETA Arm B完≈00:12。
- PHASE: **p8_ab_testing_armB_step200** — Arm B(MBS=3/GBS=1032) running step200/300, GPU ~69GB/card 100%util, VRAM peak 70591MiB。Arm A baseline: 249,276 tok/s / loss@300=3.980 / peak 52.3GB。Arm B preliminary B/A=1.0335(**未达1.12**), step_time~16,400ms已稳定100+步。三判据: 吞吐FAIL / VRAM PASS / loss PASS。ETA Arm B完≈27min→~00:12 最终确认。
- ERROR_COUNT: 0
- 轮询状态：30min 长轮询。**全 8 GPU 占用**（.29, ~69GB/card 100%util, Arm B MBS=3）。A/B 脚本 PID 1669415(ppid=1, setsid 持久)。P-8 ckpt@1049 已存(未受A/B影响, A/B用独立实验目录 p8_ab_A/p8_ab_B)。📦 体积：TASK=31.6KB / MEMORY=24.0KB ✅。🚫绝不 kill watchdog loop(PID 1391466)
- 🩺 **本唤醒推进 = #280（2026-10-10 23:45, A/B Arm B 监控·step200/300 · 决策已定）**：① git fetch+status 0/0 ✅（无新运维指令）。② **Arm B 进度**：step200/300, started 22:47:40, step_time avg 16,400ms(steps100-200) → **257,631 tok/s**, B/A=**1.0335**（需≥1.12 → **确认 FAIL**）, loss@200=4.467(与 Arm A step200=4.473 一致, 0 NaN, 0 skip, grad_norm 0.24-0.78), peak VRAM=70,591MiB(68.9GB, ✅<76GB), GPU 100%util 619 TFLOP/s。③ **三判据最终预判**：吞吐 **FAIL**(B/A=1.0335<1.12, step_time~16,400ms 已稳定100+步不可能翻盘) / VRAM **PASS**(68.9<76) / loss **PASS**(同轨迹无发散)。→ **决策已定：MBS=3 不达标 → 恢复 MBS=2/GBS=1024 原定稿(10,490/524/1049/1049)**。④ **ETA**：Arm B 100步×16.4s≈27min→~00:12 完整结束, A/B脚本自动写summary。⑤ P-8 ckpt@1049 未受 A/B 影响(A/B 用独立实验目录 p8_ab_A/p8_ab_B), 可直接从 step1049 续跑。⑥ **体积**：TASK=32372B(31.6KB) / MEMORY=24544B(23.5KB) ✅。→ **下次唤醒**：① 查 A/B 脚本是否结束(PID 1669415 是否还在) → 读 summary 确认 Arm B final last-100 → ② 正式记录决策 → ③ **重启 P-8 从 ckpt@1049 续跑 MBS=2/GBS=1024 原定稿(10,490/524/1049/1049)** → ④ 报 PID + 恢复监控。WAITING=1。
> 📦 **[已归档] #279 流水（2026-10-10 23:10, A/B Arm A 完成+Arm B 监控·step70）→ daily-memories/2026-10-10.md；结论：Arm A ✅ 249K tok/s/loss@300=3.980/52.3GB; Arm B step70 B/A=1.037 初步FAIL。需要时再读。**
> 📦 **[已归档] #278 流水（2026-10-10 22:37, A/B Arm A 进度监控·step260）→ daily-memories/2026-10-10.md；结论：Arm A step260/300 loss4.09, 248K tok/s, VRAM 52.3GB, 0 NaN, ETA Arm A完≈22:46。需要时再读。**
> 📦 **[已归档] #276 流水（2026-10-10 21:22, A/B bug 修复+重启）→ daily-memories/2026-10-10.md；结论：P-8 step1050 loss2.925/ckpt@1049, A/B 两 bug 修复后 21:21 重启, Arm A 训练中。需要时再读。**
> 📦 **[已归档] #275 流水（2026-10-10 20:40, P-8 监控·step970）→ daily-memories/2026-10-10.md；结论：P-8 step970 loss2.959, ETA step1050≈21:02。需要时再读。**
> 📦 **[已归档] #274 流水（2026-10-10 20:05, P-8 监控+暂停/A/B全链路复核）→ daily-memories/2026-10-10.md；结论：P-8 step840 loss3.037, 暂停/A/B全链路复核通过, ETA step1050≈21:02。需要时再读。**
> 📦 **[已归档] #273 流水（2026-10-10 19:31, P-8 监控+暂停/A/B脚本复核）→ daily-memories/2026-10-10.md；结论：P-8 step720 loss3.13, 暂停/A/B脚本复核通过, ETA step1050≈21:02。需要时再读。**
> 📦 **[已归档] #272 流水（2026-10-10 18:56, P-8 监控+脚本/数据核查）→ daily-memories/2026-10-10.md；结论：P-8 step590 loss3.278, 脚本/数据全核查通过, ETA step1050≈21:05。需要时再读。**
> 📦 **[已归档] #271 流水（2026-10-10 18:17, P-8 监控 + 暂停监控器 step 解析 bug 修复）→ daily-memories/2026-10-10.md；结论：P-8 step460 loss3.49, 暂停监控器step解析bug修复, PID799219重启, ETA step1050≈21:00。需要时再读。**
> 📦 **[已归档] #270 流水（2026-10-10 17:39, P-8 监控+A/B脚本修复+暂停监控器部署）→ daily-memories/2026-10-10.md；结论：P-8 step320 loss3.86, A/B脚本结构缺陷修复, 暂停监控器创建(后step解析bug→#271修复)。需要时再读。**
> 📦 **[已归档] #269 流水（2026-10-10 17:00, P-8 监控 + MBS A/B 脚本准备）→ daily-memories/2026-10-10.md；结论：P-8 step190 loss4.90, baize_p8_ab_test.sh 创建（后有现发现结构缺陷并修复）。需要时再读。**
> 📦 **[已归档] #268 流水（2026-10-10 16:18, P-8 启动+首 40 步）→ daily-memories/2026-10-10.md；结论：P-8 16:03 启动, step40 loss=8.38, 248K tok/s, 0 NaN, GPU 52-53GB, baize_p8_decay.sh 已创建。需要时再读。**
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

> 📦 **[已归档] #191–#203 流水（2026-10-08 06:22–14:05, R3 BO 监控+R2收官报告+状态核查）→ daily-memories/2026-10-08.md；结论：R3 BO 100-trial 搜索完成, R2 收官报告 46KB 已交付, P-8 仍不可启动。需要时再读。**
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
