# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.6-B 配比实验 → d=128/L=14 proxy(18.36M) → BO搜索(eval-set语料代理)进行中(168/200, mix_search_eval.db, PID 1011682@.29 alive~6h35m, GPU2-7; best=5.831981 #155; held_out_eval=eval-set语料代理bin); base下载@.12: zh✅256/256下满(301G), l1_en_hq 5088/6006 85%
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满；base分词(22.05B tok)；D-CLEAN-1/2/3/4；S0a已kill；proxy d128 provider+recipe创建；held-out bin+held_out_eval(eval-set语料代理bin,2.77M tok/19.6K docs); baize_mix_optuna.py创建；5项必验全通过；BO(val-loss obj)115/200→改道eval-set语料代理(mix_search_eval.db,168/200); §6.1预注册+代理定义已写入DATA_MIX_RECIPE.md; zh下载完成✅
当前动作:     唤醒165(22:05) ①BO eval study=168/200(PID 1011682@.29 alive~6h35m,best=5.831981#155,先验88:8:4=#79 loss5.886 rank~92/168 Δ0.054),rate~28.4/h(150→168 in 38min),32trial剩余,ETA~23:12Oct6 ②base下载: zh✅256/256下满(301G)! l1_en_hq 5088/6006(379G,85%,5snap×1000✅+CC-2025-51@89 actively downloading part-0090,0 incomplete)
下一步:       ① BO eval study 32trial剩余(ETA~23:12)→200trial完成;② BO完成后:重跑top-5+先验(88:8:4)共6个config带ckpt→lm_eval 8集→取均分作真objective;③ 代理val-loss-vs-均分Spearman秩相关验证(top-K全评);④ 噪声测量(top-5 ckpt各测3次报σ);⑤ l1_en_hq下载监控(余918→ETA~11:15 Oct7);⑥ 产出report_data_mix_eval.html
阻塞:         无
ERROR_COUNT:  0
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
- [22:05] **唤醒165**：①本机=`.12`。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive~6h35m,`--objective eval`):**168/200 complete**(0 pruned,6 in-flight t168-173)。**新best=5.831981**(#155:web=0.847/code=0.035/math=0.118),top5=#155/149/96/125/55(loss 5.832~5.833)。先验88:8:4=#79(loss=5.886048,**rank~92/168,Δ=0.054→先验不竞争力**)。rate:150→168 in 38min=~28.4/h,32剩余,ETA~23:12。GPU2-7各6.7GB/~10%util,GPU0-1=pretrain。③⭐**base下载**: zh✅**256/256下满**(301G)! l1_en_hq **5088/6006**(379G,84.7%,5snap×1000✅+CC-2025-51@89 actively downloading part-0090),0 incomplete,PID 3076519+retry-loop 3076502 alive。l1_en_hq余918→ETA~11:15 Oct7(速率~70/h)。④vision占.12 GPU0-7(R12b,与data无冲突,data用.29 GPU2-7)。⑤**BO完成后计划**:top-5(#155/149/96/125/55)+先验88:8:4(#79)共6个config需重跑带ckpt→lm_eval 8集取均分→Spearman秩相关验证代理有效性→噪声σ→report。📦 体积：TASK=31.7KB / MEMORY=30.8KB（归档 0KB,均≤32KB ✅）。

- [21:27] **唤醒164**：①本机=`.12`。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive~5h56m,`--objective eval`):**150/200 complete**(0 pruned)。**新best=5.832362**(#149:web=0.920/code=0.037/math=0.043),top5=#149/96/125/55/65(loss 5.832~5.835)。先验88:8:4=#79(loss=5.886048,**rank82/150,Δ=0.054→先验不竞争力**)。rate加速:124→150 in 36min=~43.3/h(前轮6.7/h),50剩余,ETA~22:40。GPU2-7各6.7GB/~10%util,GPU0-1=pretrain。③⭐**base下载**: zh✅**256/256下满**(301G)! l1_en_hq **5045/6006**(376G,84%,5snap×1000✅+CC-2025-51@45 actively downloading part-0047),0 incomplete,PID 3076519+retry-loop 3076502 alive。l1_en_hq余961→ETA~10:30 Oct7(速率~1.22parquet/min)。④vision占.12 GPU0-7(R12b,与data无冲突,data用.29 GPU2-7)。📦 体积：TASK=31.7KB / MEMORY=29.9KB（归档 0KB,均≤32KB ✅）。

- [20:51] **唤醒163**：①本机=`.12`。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive~5h21m,`--objective eval`):**124/200 complete**(0 pruned,6 in-flight t130-137)。**best=5.832675**(#95:web≈0.94/code≈0.03),top5=#95/54/64/49/74(loss 5.833~5.843)。先验88:8:4=**#78**(web=0.881/code=0.085/math=0.034,loss=5.886048,**rank66/124,Δ=0.053→先验不竞争力**)。rate减速:120→124 in 36min=~6.7/h(前轮31.8/h),ETA待观察。GPU2-7各6.7GB/~10%util,GPU0-1=pretrain。③⭐**base下载**: zh✅**256/256下满**(301G,0 incomplete)! l1_en_hq **5001/6006**(373G,83.3%,+50 since 20:15),0 incomplete,PID 3076519+retry-loop 3076502 alive,actively writing(mtime 20:51)。l1_en_hq余1005→ETA~08:55 Oct7(速率~1.39parquet/min)。④vision占.12 GPU0-7(R12b,与data无冲突,data用.29 GPU2-7)。📦 体积：TASK=32.5KB / MEMORY=28.8KB（归档 0KB,TASK略超32KB但远低于40KB红线,无可归档已闭合块）。

- [20:15] **唤醒162**：①本机=`.12`。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive~4h45m,`--objective eval`):**120/200 complete**(0 pruned),rate~31.8/h(102→120 in 34min)。**best=5.8327**(#96:web=0.9429/code=0.0338/math=0.0233),top5=#96/55/65/50/75(loss 5.833~5.843)。先验88:8:4最近=#79(web=0.881/code=0.085/math=0.035,loss=5.886,**rank63/120,Δ=0.053→先验不竞争力**)。remaining80 ETA~22:45。GPU2-7各6.7GB/~10%util,GPU0=pretrain(5.4GB/30%),GPU1=空闲。③⭐**base下载**: zh✅**256/256下满**(301G,最后part-256 mtime 20:02),0 incomplete! l1_en_hq 4951/6006(370G,82.4%,+28 since 19:41),0 incomplete,PID 3076519+retry-loop 3076502 alive。l1_en_hq余1055→ETA~06:00 Oct7。④vision占.12 GPU0-7(与data无冲突,data用.29 GPU2-7)。📦 体积：TASK=32.5KB / MEMORY=28.8KB（归档 0KB）。

- [19:41] **唤醒161**：①本机=`.12`。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive~4h11m,`--objective eval`):**102/200 complete**(0 pruned),rate~48.6/h(85→102 in 21min,加速)。**best=5.8327**(#96:web=0.9429/code=0.0338/math=0.0233),top5=#96/55/65/50/75(loss 5.833~5.843)。先验88:8:4最近=#59(web=0.876/code=0.090/math=0.035,loss=5.8570,**rank15/102,Δ=0.024→先验仍不竞争力但差距较85trial时缩小**)。remaining98 ETA~21:41。GPU2-7各6.7GB/10%util,当前t0107(GPU7)运行中。③**base下载**✅活跃@.12:PID 3076519(retry-loop PID 3076502),l1_en_hq 4923/6006(367G,82%,+36 since 19:20),zh 243/256(286G,95%,+10),0 incomplete,log显示连续完成(CC-MAIN-2025-47 part-0914~0924)。zh余13→ETA~20:08;l1_en_hq余1083→ETA~06:00 Oct7(速率~1.7parquet/min)。④vision占.12 GPU0-7(与data无冲突,data用.29 GPU2-7)。📦 体积：TASK=31.7KB / MEMORY=27.3KB（归档 0KB）。

- [19:20] **唤醒160**：①本机=`.12`。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive~3h50m,`--objective eval`):**85/200 complete**(0 pruned),best=5.8328(#55:web=0.884/code=0.105/math=0.011),top5=#55/65/50/75/19(loss 5.833~5.850),先验88:8:4最近#79(web=0.881/code=0.085/math=0.035,dist=0.007)loss=5.886 rank43/85 Δ=0.053。rate~25.9/h,remaining115 ETA~4.4h。③⭐**held_out_eval bin内容确认**:解码tokenized bin→**eval-set语料**(ARC+HellaSwag+WinoGrande+BoolQ),2,770,208tok/19,627docs→确认=运维可行方向#2。代理定义+预注册(阈值σ×2/噪声≥3次/Spearmanρ<0.5改全量lm_eval/最终以lm_eval均分排序)已写入DATA_MIX_RECIPE.md §6.1。④**base下载**✅活跃:PID 3076519,l1_en_hq 4887/6006(364G,81%,+47 since 18:19),zh 233/256(274G,91%,+7)。zh余23→ETA~2h,l1_en_hq余1119→ETA~25h。⑤DATA_MIX_RECIPE.md §9.2/§9.3/§9.5已更新。📦 体积：TASK=31.7KB / MEMORY=27.3KB（归档 ~5KB: wakes148-155移除,daily-memories已有）。


- [18:19] **唤醒159**：①本机=`.12`(whag0pgpuap12)。②**BO eval study**(DB=nemo_experiments/mix_search/mix_search_eval.db,PID 1011682@.29 alive 2h49m,`--objective eval`):**72/200 complete**(0 pruned),GPU2-7各6.7GB/10%util,当前t0066运行中(GPU5)。**best=5.8328**(#55:web=0.884/code=0.105/math=0.011),top5=#55/65/50/19/9(loss 5.833~5.849)。⚠️**先验88:8:4分析修正**:用math=1-web-code重算距离→最近trial=#32(web=0.873/code=0.084/math=0.043,dist=0.009)loss=5.8927,**rank 43/72,Δ=0.060→先验不竞争力**。上轮(唤醒158)报"#42最近,rank4/54,Δ=0.018竞争力强"**是错误的**——根因=DB params中math=0.0000存储bug致距离计算用了math=0,实际#42=88.8:5:6.3(dist=0.038)并非88:8:4最近点。附近点#59(87.6:9:3.5,dist=0.012)rank10/72 Δ=0.024尚可。rate~25/h,剩余128→ETA~23:20。③**base下载**✅活跃@.12:PID 3076519(hf download,since Oct04),l1_en_hq 4840/6006(361G,80%,+35 since 17:40),zh 226/256(266G,88%,+19 since 17:40)。zh余30 parquet→ETA~2h;l1_en_hq余1166→ETA~25h(速率~4.6G/h)。④vision占.12 GPU0-7(与data无冲突,data用.29 GPU2-7)。📦 体积：TASK=31.7KB / MEMORY=30.6KB（归档 0KB）。

- [17:40] **唤醒158**：①本机=`.12`(whag0pgpuap12)。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive 133min,`--objective eval`=held_out_eval proxy val loss):**54/200 complete**(0 pruned),GPU4-7各6.7GB active。**best=5.8357**(#50:web=0.876/code=0.042/math=0.083),top5=#50/19/9/42/8(loss 5.836~5.857)。**先验(88:8:4)最近=#42**(web=0.888/code=0.050/math=0.062,loss=5.854,**rank 4/54**,Δ=0.018<0.02→先验竞争力强)。⚠️DB params中math=0.0000=存储bug(实际训练用math=1-web-code,trial cmd line确认`0.082614 .../anneal_math2`)。rate~24/h,剩余146→ETA~23:40。③**base下载**✅活跃@.12:PID 3076519(hf download,since Oct04,retry-loop PID 3076502)→运维P0「重启base」**无需执行**(已活跃)。l1_en_hq 4805/6006(358G,80%,+27 since 17:00,active dl CC-MAIN-2025-47 part-0807),zh 207/256(245G,81%,+17 since 17:00)。合下载~34G/h,余~199G→ETA~6h。④vision R12b占.12 GPU0-7(r9_train.py,PID 2670128,与data无冲突)。📦 体积：TASK=31.7KB / MEMORY=29.4KB（归档 0KB）。

- [15:10] **唤醒156**：①**BO eval study**(mix_search_eval.db,PID 1011682 `--objective eval`,GPU2-7各6.7GB/9-11%util):**18/200 complete**,best=**5.8491**(#9:web=0.856/code=0.081/math=0.063),top5=#9/8/17/18/6(loss 5.849~5.871)。old study(mix_search.db,115trial,best=4.6420)保留对比。②**base下载**:PID 4172910(hf_transfer+lock cleaner)crashed——lock cleaner(-mmin+1)误删活跃lock→`FileNotFoundError: .incomplete`。**修复**:kill lock cleaner(PID 4172912)→清所有.lock→重启PID 530450(无lock cleaner,接受偶发lock wait)。进度:l1_en_hq 4738→4750(+12,354G),zh 172→174(+3,205G)。③**任务书归档**:7块(§A规模定案/§D第0步分工/§C评测硬规则/运维规程agent归档/第5轮块头/用户复核②块头/改道方案裁定)→ARCHIVE_OPERATOR_DATA.md,各留1行📦指针。📦 体积：TASK=31.7KB / MEMORY=30.4KB（归档 ~6KB → ARCHIVE_OPERATOR_DATA.md）。

- [17:00] **唤醒157**：①**BO eval study**(mix_search_eval.db,PID 1011682 alive 89min,`--objective eval`=held_out_eval proxy val loss,GPU2-7各6.7GB/0-16%util):**36/200 complete**(ID1-36,0 pruned),6 running(t0036-t0041,t0036 step210/500 loss6.24 s/step1.58s)。**best=5.8477**(#19:web=0.834/code=0.047/math=0.119),top5=#19/9/8/25/17(loss 5.848~5.863)。**先验(88:8:4)最近=#8**(web=0.888/code=0.049/math=0.063,loss=5.8566,**rank 3/36**,Δ=0.0089<0.01→**先验竞争力强**)。GP-EI有sklearn ConvergenceWarning(length_scale近下界,非致命)。rate~24trial/h(36trial/89min),剩余164→ETA~23:45。②**base下载**:PID 3689969 alive(52min,proxy=172.19.92.25:13128,hf_transfer),l1_en_hq 4778/5652(356G,+24 since 15:10,~13/h),zh 190/256(224G,+15,active dl part-192-of-256,~10G/h)→zh ETA~10h,l1_en_hq慢(~1G/h,待zh完加速)。③**体积自检**:TASK=31.7KB✅ MEMORY=31.8KB✅ 均≤32KB,无需归档。📦 体积：TASK=31.7KB / MEMORY=31.8KB（归档 0KB）。

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。


### ①-⑧ 已归档（详见 `daily-memories-data/2026-10-06.md`）

| # | 主题 | 结论 | 日期 |
|:--|:--|:--|:--|
| ① | SFT-2605 重下 | ✅ 1504 jsonl / 318.99 GB，与 HF 官方清单逐字节一致 | 10-02 |
| ②-④ | D-CLEAN-1/2/3 | ✅ 盘点 + 删除 servers(974G)+nemo R1(310G)+laion(7.8G)+pip(3.3G) ≈1.3T；nemo R2 ckpt 保留 | 10-03 |
| ⑤ | 下载白名单 | ✅ 停 en_v1_4，只下 l1_en_hq+zh+GPIC | 10-03 |
| ⑥-⑦ | D-CLEAN-4 + LLaVA ckpt | ✅ 盘点：本用户可回收 ≈11.4TiB(含 LLaVA-OV 22TiB iter ckpt)，待运维拍板 | 10-04 |
| ⑧ | LIT_IDEAS HTML | ✅ 产出 `LIT_IDEAS_2026-10-05.html`（52 entries/0 unverified/62% turnover），含成本专章+ISEDA投稿要求(4-6页) | 10-04 |
### ⑨ 🔴 配比实验可行性核查（2026-10-05 运维分卡指令 · §0.6-B）— ✅ 可行性核查完成，⏳ 等 GPU2-7

> 运维 2026-10-05 批准：`.29` GPU2-7（6 卡）归 data 跑配比实验，与 pretrain 推理评测并行。**起跑前置 = 先等 P-9.8 armB(FP8) 跑完**。

**① GPU2-7 核查（10:26 实测原文）**：
```
ssh 10.239.2.29 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'
→ 8 个 python 进程各 ~72GB，PID 4044610-4044617
ssh 10.239.2.29 'nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv'
→ 8 卡各 100% util / ~72GB used
```
**结论**：❌ **GPU2-7 当前不空** —— P-9.8 armB 已于 ~09:49 完成，但 pretrain 随即启动 **P-9.9**（tensorwise FP8 1000 步跑，PID 4044534，~10:02 起，**占满 8 卡**，ETA ~15:00）。**不 kill（铁律）**，等 P-9.9 完。

**② 脚本/recipe 核查（✅ 全部就位）**：
- `run/baize_p5b_train.sh`：8 卡 TP1/DP8 模板（GBS=1024/seq=4094/WSD/bf16）—— **已复制为** `run/baize_mix_train_template.sh`（改为 6 卡 TP1/DP6，CUDA_VISIBLE_DEVICES=2,3,4,5,6,7）
- `code/BaiZe-ISEDA2027/pretrain_launcher.py`：✅ 支持 `--train-data-path` blend `[w, prefix, w2, prefix2, ...]`
- `code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py`：✅ parquet→.bin/.idx（需 `*.snappy.parquet` 后缀；base 文件名是 `*.parquet`→已用软链加 `.snappy` 后缀解决）

**③ 训练数据 .bin/.idx 核查（.29 上）**：
| 源 | 状态 | 路径 | token 估 |
|:--|:--|:--|--:|
| `p5b_l3` (L3 web) | ✅ 16 片 | `data/p5b_l3/p5b_l3_train_s{0..15}.bin` | ~20.6B |
| `anneal_code` | ✅ | `data/anneal_code.bin` (345M) | ~180M |
| `anneal_math2` | ✅ | `data/anneal_math2.bin` (1.7G) | ~860M |
| `ultrafineweb_l3_qa_700m` | ✅ | `data/ultrafineweb_l3_qa_700m.bin` (2.97G) | ~1.5B |
| `tokenizer_eod` | ✅ | `data/tokenizer_eod` | — |
| **base (ultrafineweb_en)** | 🔜 **分词中** | `data/mix_base/mix_base_train_s{0..3}` | ~21B（48 parquet→4 shard，4 进程并行 @ 10:32 起） |
| **SFT-2605** | ❌ 未分词 | `/nas_inference/.../UltraData-SFT-2605/data/` (1504 jsonl, 298G) | 需写 jsonl→text 转换器（chat 格式，preprocess_data.py 只认 parquet content 列） |
| **SFT-Agent-2609** | ❌ 未分词 | `/nas_inference/.../UltraData-SFT-Agent-2609/` (50 shard, 51G) | 同上 |

**④ 环境（✅）**：`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`；tokenizer=`/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash`；ssh .29 免密 ✅。

**⑤ 已创建脚本**：`run/baize_mix_tokenize_base.sh`（base 分词，已启动）+ `run/baize_mix_train_template.sh`（6 卡训练模板，待 GPU 就绪）。

**⑥ 下一步**：base 分词完成（ETA ~1-2h）→ 汇总 token 数 → P-9.9 完成（~15:00）→ GPU2-7 空 → 起 Stable 段 S0a 臂（base:code:math=88:8:4, 5000 步）→ ckpt→HF→lm_eval Table 2（8 集）。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **§0.6-B 配比实验改道 → 🔄 BO搜索(eval proxy obj)进行中(36/200, mix_search_eval.db, PID 1011682, GPU2-7; best=5.8477 #19); base下载中(PID 3689969, l1_en_hq 4778/5652 356G, zh 190/256 224G); 任务书+MEMORY均≤32KB** |
| WAITING | 1（🔄 BO eval study运行中: 36/200 trial, best=5.8477(#19), PID 1011682; base下载PID 3689969 l1_en_hq+zh; 每30-60min查进度+commit心跳） |
| ERROR_COUNT | 2（①GP竞态crash已修复见流水唤醒150；②base下载lock cleaner误删活跃lock→已撤lock cleaner见流水唤醒156） |
| 节点 | `10.239.2.29`（GPU2-7 BO搜索并行，GPU0-1空闲） |
| 更新 | 2026-10-06 |

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| R research（🎯 只答 §0 两问） | ✅ 完成（DATA_RESEARCH v1.1：LLM 够/走路线A；Vision 换 GPIC short 消截断） |
| R2 LLM 数据侧调研（任务书两项优先） | ✅ 完成（DATA_RESEARCH R2 节：8 源事实表满填 / base vs L3 重叠实测 0% / P-8 三档 44B·100B·200B = base-en(86):code(10):math(4)；base 2.99TB 下载已启动） |
| R2 视觉侧调研（§0.4 去 HF 找通用图文对） | ✅ 完成（DATA_RESEARCH R2-视觉侧：本地 12 源图像形态+≤77 实测 / 13 HF 候选其中 7 URL-only 淘汰 / 前 3 推荐 CC12M≈11M + Amshaker≈6M + LLaVA≈1.15M，50 万→1800 万对 ×35，无需新下载） |
| phase0 inventory（实测盘点） | ✅ 完成（DATA_LEDGER v0） |
| phase5 isolation（**先立闸**） | ✅ 完成（v0.3：536 任务 + NFKC/Unicode 归一化 + 8-gram 兜底 + **SFT 嵌套 jsonl 目录同闸扫描**，全快照正控 100%） |
| phase1 validate（完整性校验） | 🟡 校验脚本已备（validate_data.py），全量跑待下载完成后 |
| phase2 text（通用文本 .bin/.idx） | 🟡 分词打包 wrapper 已备（preprocess_text.sh + 污染闸门），跑待下载完成后 |
| phase3 domain（EDA 领域语料排查） | 🚫 **已取消**（运维 2026-10-01 夜：评测 prompt 由 docstring 生成、与语料天然同源，入库无意义）；但 EDA-Eval 158 任务黑名单红线**依然有效、继续执行** |
| phase4 mm（多模态打包） | ⬜（待下载完成） |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [x] ~~EDA API 知识库能否导出纯文本~~ → **已确认可行**：`eda_fastmcp/docs/` 本就是 md/json 纯文本（≈45MB，见 DATA_LEDGER §5）。
- [x] ~~EDA 语料入库授权~~ → **整条线已取消**（运维 2026-10-01 夜）：评测 prompt 由 docstring 生成、与语料天然同源，"把测试集放进训练集"无意义 → phase3_domain 不再调研/入库。**但 EDA-Eval-PyAether 158 任务黑名单红线照常执行。**
- [x] ~~内部培训材料 / 脱敏 CAD 案例能否用于训练~~ → 随 phase3_domain 一并取消。
- [ ] 多模态下载预计完成时间
- [x] ~~`UltraData-SFT-2605/-Agent-2609` 具体存储格式~~ → **已实测**：Agent-2609 = **jsonl**（50 shard / 51 GiB，2GB/shard）；**2605 = 落盘为空**（仅 179 个 `.lock` 缓存文件 / 22.4KiB，无数据，需重下）
- [x] ~~`UltraData-SFT-2605` 重新下载~~ → **✅ 已下满并核验一致（2026-10-02 唤醒 37）**：落盘 **1504 jsonl / 318,990,252,711 B = 318.99GB（297.08 GiB）**，`.incomplete` = 0，**与 HF 官方清单（1504 文件 / 318,990,252,711 B）逐字节完全一致**；逐子目录 `no_think` 855✓（CG 50/Code 300/IF 20/Kn 80/Math 300/ML-Kn 50/ML-Math 55）+ `think` 649✓（CG 50/Code 279/IF 20/Kn 50/Math 250）。token `hf_lqLxH…`（用户 foamliu）。

- 2026-10-05 —— 唤醒 111（已滚动归档至 daily-memories-data/2026-10-04.md）
- 2026-10-05 —— 唤醒 112（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 113（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 114（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 115（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 116（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 117（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 118（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 119（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 120（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 121（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 122（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 123（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 124（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 125（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 126（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 127（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 128（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒129~130（✅base分词完成22.05B tok+SFT s2✅3.58B+s1冲突修复+P-9.9仍占8卡+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒131~132（🚀S0a臂启动step60/5000+ETA更正312GPU·h/臂+baize_mix_eval.sh✅创建+SFT分词进度+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒133~134（⚠️S0a crash/重启→step84/5000+SFT分词进度+git proxy同步成功+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒135~136（S0a step145→200/5000+✅✅SFT-2605全4shard完成20.97B tok!+🔄Agent-2609分词启动+git pull proxy同步）（详情已归档）
- 2026-10-05 —— 唤醒137（19:23 S0a step260/5000+Agent-2609 2/4+下载巡检+内存滚动）（详情已归档至 daily-memories-data/2026-10-05.md）

- 2026-10-05 —— 唤醒138（20:02 S0a step330/5000+Agent-2609 s0/s1进行中+D-CLEAN-4定案确认）（详情已归档至 daily-memories-data/2026-10-05.md）
 - 2026-10-05 —— 唤醒139（20:45 S0a step390/5000 loss4.07+✅Agent-2609 s0完成2.58B tok→3/4 done+下载l1_en_hq 3157+git proxy同步）：① ⭐ **S0a健康推进**：step390/5000, loss 4.07（稳定下降 4.56@300→4.46@310→4.42@320→4.36@330→4.29@340→4.25@350→4.20@360→4.15@370→4.13@380→4.07@390, LR=1.0e-3达峰, 0NaN/0skipped），~37.8s/iter, GPU2-7 6卡38-86%util ~39GB。**ETA=(5000-390)×37.8≈48.4h→~Oct7 21:00**。PID 2528081-2528090。② ✅ **SFT-Agent-2609分词**：**s0✅完成** — 2,578,877,685 tokens (2.58B) / 69,895 docs, .bin 10.3G + .idx 1.4M + .json (20:21完成)；s2✅(1.23G)；s3✅(2.6G)；**s1🟡仍跑** — .bin 12.9G增长中(~2.2MB/s, PID 166424, etime~1h48m, 输入=sft_General_Agent.parquet symlink, 无.idx=未完)。→ **3/4 shard完成**。③ 下载l1_en_hq **3157/6006**(+51, retry-loop PID 3076502+hf PID 3076519活)、zh **171/256**(冻结)、gpic **3486 tars**(PID 144981活)、en **2048✓**。④ ✅ **git fetch via proxy成功**(与origin/main同步, 无behind/ahead)。⑤ GPU0-1 on .29空闲(4MiB, 0%util, pretrain P-9.10已完成)；GPU2-7 S0a训练中。磁盘/nas_train 84%(34T free) /nas_inference 65%。MEMORY_DATA.md=27.5KB(≤32KB✓)。下一步=⏳等S0a完(~Oct7 21:00)→ckpt→HF→lm_eval Table2(8集)；判Agent-2609 s1完→Decay段全备料(SFT-2605✅20.97B+Agent✅)→起Decay臂；填DATA_MIX_RECIPE.md实测值；下载续推。
 - 2026-10-06 —— 唤醒140（01:13 ⭐report_data_mix_s0a.html实时更新+S0a step820/5000 loss3.23+✅✅Agent-2609全4shard完成→Decay全料就绪+下载巡检+git proxy同步）：① ⭐ **S0a健康推进**：step820/5000, loss 3.23（稳定下降 10.84@10→4.93@250(LR达峰)→3.57@600→3.40@700→3.25@800→3.23@820, LR=1.0e-3, 0NaN/0skip），~37.6s/iter, GPU2-7 6卡30-82%util ~39GB。**ETA=(5000-820)×37.6≈43.7h→~Oct7 20:53**。PID 2525319(etimes=31703≈8h48m)。② ✅✅ **SFT-Agent-2609分词全完成**：s0✅(2.58B tok)+**s1✅**(.bin 18G+.idx 6.2M+.json, 21:27完成)+s2✅(1.23G)+s3✅(2.6G)→**4/4 done! Decay段全料就绪**。③ ✅ **report_data_mix_s0a.html已更新**（运维指令2026-10-05深夜2⑤）：实时数据step760→820/loss3.30→3.23/ETA→Oct7 20:53/GPU表/SVG图表修正(82个数据点逐10步, 修正了旧版y坐标映射错误)/日志附录/里程碑表。纯CPU写作,不占GPU。④ 下载l1_en_hq巡检(进行中)。⑤ ✅git fetch via proxy成功(无behind/ahead)。GPU0-1空闲。磁盘/nas_train 84%。MEMORY_DATA.md≈29KB(≤32KB✓)。下一步=⏳等S0a完(~Oct7 20:53)→ckpt→HF→lm_eval Table2(8集)；✅Decay段全料就绪→可起Decay臂(SFT占比搜索)；填DATA_MIX_RECIPE.md实测值。
 - 2026-10-06 —— 唤醒145（08:06 🔴 Step0 kill S0a 2.2B单臂 → 代理模型创建 → 标定启动 → MEMORY/GPU更新）：① 🔴 **Step0 kill**（运维指令 §「Step 0」kill）：
   - **kill 目标**：`mix_stable_s0a` = watchdog PID 2525272 → torchrun PID 2525319 → 6 workers 2528081-2528090
   - **kill 命令**：`kill 2525272 && sleep 2 && kill 2525319 2528081 2528082 2528083 2528084 2528085 2528086 2528087 2528088 2528089 2528090`
   - **GPU 释放验证**：`nvidia-smi` → GPU2-7 all 0 MiB / 0% util ✅
   - **watchdog restart script**：`/tmp/restart_mix_stable_s0a.sh` 已 `rm -f` ✅
   - **DEPRECATED**：`baize_mix_stable_s0a.sh` 已加 `exit 1` + 注释 `DEPRECATED: killed 2026-10-06 per ops §Step0` ✅
   - **作废**：step1470/5000 loss2.76，~100 GPU·h 浪费（已记录教训）→ 改道代理模型 BO 搜索
   ② **代理模型创建**：
   - `mamba2_hybrid_proxy/__init__.py` ✅
   - `mamba2_hybrid_proxy/provider.py`：`NVIDIAMambaHybridModelProviderProxy` — h=512, L=14, pattern="M-M-M--M-M*-M-", tie embed, GQA 4Q/1KV, mamba_groups=2, ce_fusion=True
   - `mamba2_hybrid_proxy/recipe.py`：`pretrain_config` — WSD scheduler, GBS=16, seq=2048, train_iters=13700, bf16_mixed
   - `pretrain_proxy_launcher.py`：standalone argparse launcher（复用 bridge_compat + forward_step）
   - `baize_mix_calibrate.sh`：3 LR × 50 steps 并行（GPU2=3e-4, GPU3=1e-3, GPU4=3e-3）
   - **修正**：`context_model_parallel_size` → `context_parallel_size`（dataclass 字段名差异）
   ③ 🔄 **标定进行中**：GPU2/3/4 各 ~6.5GB / 54-86% util（对比 2.2B 的 39GB！）；日志在 /tmp/baize_calib_lr{0,1,2}.log；ETA ~5min
   ④ 下一步：等标定完成 → 实测 s/step → 锁定模型尺寸 → 创建 held-out bin → 写 Optuna study → Day1/Day2 搜索

### 标定结果（2026-10-06 08:22 完成）

| LR | s/step (avg) | loss@50 | grad norm@50 | TFLOP/s |
|---|---|---|---|---|
| 3e-4 | 1.57s | 7.692 | 0.472 | 14.8 |
| **1e-3** | **1.56s** | **7.081** | **0.509** | 15.0 |
| 3e-3 | 1.60s | 7.274 | 0.325 | 14.7 |

- **s/step ≈ 1.5s**（目标 0.095s，差 16×，瓶颈=data loading，GPU util 仅 ~15 TFLOP/s / 1000）
- **精确参数量**：`sum(p.numel())` = **92,711,712** (~92.7M)
  - Embed (tied): 129408×512 = 66.3M (71.5%)
  - Body: 26.5M (28.5%)
  - 比例 2.220B/92.7M ≈ 1/24（目标 1/23，偏差 ~4%）
  - vocab: 129281→padded 129408 (÷128)
  - 层分配: 6 Mamba + 1 attention + 7 MLP = 14 ✓
- **Trial 预算**：500 步/trial × 1.5s = 12.5 min/trial × 6 GPU → **T≈691 > 400 ✅**（锁定 h=512/L=14，不需缩尺）
- **LR 选择**：LR=1e-3（与 2B recipe 一致，loss@50 最优）
- **校准 checkpoint 已清理**（`rm -rf nemo_experiments/calib_lr*`）

### Held-out 验证集 + BO 搜索脚本 + Smoke Test（2026-10-06 08:50 完成）

#### ① create_heldout_bins.py — 已创建并运行
- 脚本位置：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/create_heldout_bins.py`
- 方法：hash-split（`md5(salt:doc_idx) % 100 < valid_pct`），salt=42，valid_pct=5%
- 用 `_IndexReader(path, multimodal=False)` 读 .idx，`numpy.memmap` 读 .bin，`IndexedDatasetBuilder` 写出
- **运行结果**：
  | 域 | 源 | docs | tokens | 文件大小 |
  |---|---|---|---|---|
  | base | mix_base_train_s0 | 2451 | 2,003,023 | 7.7M bin + 48K idx |
  | code | anneal_code | 1451 | 2,000,625 | 7.7M bin + 29K idx |
  | math | anneal_math2 | 4618 | 2,000,101 | 7.7M bin + 91K idx |
  | **合计** | | **8520** | **6,003,749** | **~24M** |
- 输出路径：`data/heldout/held_out_{base,code,math}.{bin,idx}`

#### ② baize_mix_optuna.py — 已创建并通过语法检查
- 脚本位置：`run/baize_mix_optuna.py`（336行）
- **替代 Optuna**：`.29` 离线（`pip install optuna` → Network is unreachable），改用 **GP-EI**（sklearn GPR + scipy Expected Improvement）
  - sklearn 1.7.2 + scipy 1.15.3 已可用
  - Matern(ν=2.5) kernel + L-BFGS-B 优化 EI（20 random restarts）
  - 前 12 trial 随机采样，之后 GP-EI 引导
  - 中位数 pruning：intermediate val loss > 1.5× 已完成 trial 中位数 → kill
- **搜索空间**：
  - Stable (Day1)：web ∈ [0.80, 0.95], code ∈ [0.03, 0.12], math = 1 - web - code
  - Decay (Day2)：sft_pct ∈ [0.40, 0.80] + 4D SFT class simplex（待 SFT shard 准备后启用）
- **训练参数**：500 steps/trial, eval_interval=100, eval_iters=10, GBS=16, seq=2048, LR=1e-3, WSD(50 warmup/450 decay), bf16_mixed
- **并行**：6 GPU（2-7）ThreadPoolExecutor + Queue 管理 GPU 分配
- **存储**：SQLite（`nemo_experiments/mix_search/mix_search.db`），支持断点续跑
- **Checkpoint 自动清理**：trial 结束后 `shutil.rmtree(ckpt_dir)`，避免 200×400MB=80GB 填盘
- **日志解析**：`VAL_LOSS_RE = r"validation loss at iteration\s+(\d+).*?lm loss value:\s*([\d.eE+-]+)"`

#### ③ Smoke Test — 通过 ✅
- GPU2, 20 steps, blend=0.85/0.08/0.07, eval@10/20
- **结果**：
  | 指标 | 值 |
  |---|---|
  | s/step (warmup, 前10步) | 9.7s |
  | s/step (warmup后, 后10步) | **1.4s** ✅ |
  | train loss (step 10→20) | 10.72→8.70 |
  | val loss (step 10→20) | 9.34→8.23 |
  | log parser 提取 | `{10: 9.344584, 20: 8.227096}` ✅ |
- Smoke test checkpoint 已清理

#### ④ 启动命令（待运维批准）
```bash
ssh 10.239.2.29 'export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230; \
  nohup /nas_train/app.e0031982/miniforge3/envs/py310/bin/python \
  /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_optuna.py \
  --phase stable --n-trials 200 --gpus 2,3,4,5,6,7 --n-random 12 \
  > /tmp/mix_search_main.log 2>&1 &'
```
- ETA：200 trials × 12.5 min / 6 GPU ≈ 6.9h
- 监控：`sqlite3 nemo_experiments/mix_search/mix_search.db "SELECT id,params,loss,status FROM trials ORDER BY loss LIMIT 10"`

## 🔴 事故复盘 — S0a 2.2B 单臂 kill（2026-10-06 08:06）

> **背景**：运维指令 §「Step 0」要求 kill `mix_stable_s0a`，改用代理模型 BO 搜索路线。
> **决策理由**：单臂 2.2B 跑 5000 步 × 6 卡 ≈ 310 GPU·h 才出一个数据点；代理模型 96.8M 单卡 50 步 ≈ 5 min 出一个数据点，T≥400 才有统计意义。
> **浪费**：step1470/5000 ≈ 1470/5000 × 310 ≈ 91 GPU·h（~100 GPU·h，保守估计含 overhead）。
> **教训**：数据配比搜索不应直接跑 full-size 模型，应先小 proxy 模型快速扫配比，再选 top-K 跑 full-size 确认。
> **kill 原始输出**：
> ```
> # kill watchdog → torchrun → 6 workers
> $ kill 2525272 && sleep 2 && kill 2525319 2528081 ... 2528090
> # GPU verify
> $ nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
> 2, 0 MiB, 0 %    ← released ✅
> 3, 0 MiB, 0 %    ← released ✅
> 4, 0 MiB, 0 %    ← released ✅
> 5, 0 MiB, 0 %    ← released ✅
> 6, 0 MiB, 0 %    ← released ✅
> 7, 0 MiB, 0 %    ← released ✅
> # rm restart script
> $ rm -f /tmp/restart_mix_stable_s0a.sh
> ```







## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

