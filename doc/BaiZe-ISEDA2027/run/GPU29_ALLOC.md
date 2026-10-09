# GPU29_ALLOC.md — `10.239.2.29`（8×H100）分卡账本 · **pretrain ⇄ data 共用**

> **为什么有这文件**：用户 2026-10-05 拍板 —— pretrain 的 **P-9.10 推理对比评测只需要 2 张卡**，
> **剩下的卡让给 data 跑数据配比实验**（「让它和 data 协调一下」）。
> `.29` / `.12` 跑的是**同一块 NFS 上的同一份工作副本** ⇒ **这个文件就是双方的对账簿**。
>
> 🚫 **agent 不许删别人的历史行**；只在「**申请区**」与「**流水**」里**追加**。

---

## 1. 当前分配（静态分区，默认长期有效）

| 卡 | 归谁 | 用途 | 生效 |
|:--|:--|:--|:--|
| **GPU 0–1** | **pretrain** | **P-9.10 hybrid vs dense 推理对比评测**（纯推理，≤2 卡）；P-9.5 / P-6② 亦在这 2 卡上穿插（各 1 卡） | 2026-10-05（等 P-9.8 armB 收尾） |
| **GPU 2–7（6 卡）** | **data** | **数据配比实验**（TP1/DP6，GBS 与既有基线对齐，5000 步短地平线） | 同上 |

> ⚠️ `.29` 的 GPU0–7 **全部属本项目**。起跑前必须核验；**若看到与本项目无关的进程 → 停手报告**，🚫 不许 kill。

---

## 2. 铁律

1. **默认只碰自己名下的卡**，起跑前核验并把**原文**贴进自己 MEMORY 的流水：
   ```bash
   nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
   ```
   （pretrain 看 GPU0–1；data 看 GPU2–7）
2. **要超出配额 → 先在「申请区」写一行**（格式见下），**等对方让卡**；对方会在**臂边界 / step 边界 / 任务边界**让出。
   🚫 **不抢跑、不 kill 对方进程。**
3. **让卡优先序**：`P-9.8/P-8 长跑` > `短跑配比臂` > `推理评测`；同级**先到先得**。
4. **P-8（8 卡正式训练）要卡时 data 必须让** —— 但 P-8 现在是**暂缓**状态（等 base 下满 + 配比定稿）。
5. 🚫 **绝不 kill**：`baize_pretrain_loop.sh`（watchdog，PID 1391466 系）及**任何对方的训练 PID**。

---

## 3. 申请区（追加行；状态由申请人自己回填 `已批准 / 已让卡 / 已归还`）

> 格式：`| 日期 时间 | 申请人 | 要哪几张 | 多久 | 为什么 | 状态 |`

| 日期 时间 | 申请人 | 要哪几张 | 多久 | 为什么 | 状态 |
|:--|:--|:--|:--|:--|:--|
| 2026-10-05 09:2x | 运维（外部） | — | — | 建立本账本：静态分区 GPU0–1=pretrain / GPU2–7=data | ✅ 生效 |
| 2026-10-05 10:26 | data | — | — | 可行性核查：GPU2-7 ❌ 不空——P-9.9（tensorwise FP8,PID 4044534）占满 8 卡，ETA ~15:00。P-9.8 armB 已完(~09:49)，pretrain 随即启 P-9.9。不 kill，等 P-9.9 完。base 分词已启动（4 进程 CPU，不占 GPU）。 | ⏳ 等待 P-9.9 完成 |
| 2026-10-05 12:24 | data | — | — | 第 127 次唤醒：P-9.9 仍占满 8 卡（PID 4044610-17, etime~2h30m, ETA ~15:15）。CPU-only 备料全速推进：base 分词 4 进程（~49GB .bin, 无 .idx）+ ✅ SFT-2605 转换完成（12/12 parquet, 30GB）+ ✅ SFT-2605 分词已启动（PID 2013590, 4 进程, 12:31 起）。GPU2-7 仍需等 P-9.9 ~15:15 完成。 | ⏳ 等待 P-9.9 完成 |
| 2026-10-05 13:07 | data | — | — | 第 128 次唤醒：P-9.9 仍占满 8 卡（PID 4044610-17, 100% util, ETA ~15:15, 剩约 2h）。CPU-only 备料进展：base 分词 4 进程（~61GB .bin, 无 .idx, 仍在跑 ~2.7h）；SFT 分词诊断：s3✅完成(521M tok), s0/s2 进行中, **s1❌失败**(no_think_Code.parquet 损坏→🔄重转换中 76%, PID 503949 on .12)；下载 l1_en_hq 2554/6006。GPU2-7 仍需等 P-9.9 ~15:15 完成。 | ⏳ 等待 P-9.9 完成 |
| 2026-10-05 13:52 | data | — | — | 第 129 次唤醒：P-9.9 tensorwise FP8 **iter 740/1000（74%）**（18.57s/iter, ETA **~15:15**, PID 4044534/4044610-17, 8×100% util ~72GB/卡）。CPU-only 备料进展：① base 分词 4 进程（~84GB .bin, ~91% done, 无 .idx, ETA ~30-60min）；② SFT 分词：s3✅完成(521M tok) / s0 进行中(10.77G) / s2 进行中(10.30G) / **s1 ✅ 已重启**(PID 4046447, no_think_Code 重转换完成 3.59G pyarrow 验证 3M rows → 清理旧 .bin → 重启, .bin 3.9M 刚起步)；③ 下载 l1_en_hq 2619/6006(184G)。**GPU2-7 仍需等 P-9.9 ~15:15 完成。** | ⏳ 等待 P-9.9 完成 |
| 2026-10-05 14:40 | data | — | — | 第 130 次唤醒：P-9.9 iter~880/1000（ETA~15:15）。⭐ **base 分词 ✅ 完成**（22.05B tok, 4 shard, 14:09）。SFT 分词：s2✅完成(3.58B tok,14:29)/s3✅(521M)/s0 进行中(.bin 16G, no_think_Math 最大集)/s1🔧冲突修复(发现双进程写同一.bin→kill 1287021/1287033+4046447→rm corrupted→干净重启 PID 2868155)。下载 l1_en_hq 2675/6006。**GPU2-7 仍需等 P-9.9 ~15:15 完成。** | ⏳ 等待 P-9.9 完成 |
| 2026-10-05 15:25 | data | GPU2-7 | ~2-4h | **⭐ Stable S0a 臂已启动！** P-9.9 ✅ 完成(15:15)→8 卡全释放→data 即刻起 S0a。口径：6卡 TP1/DP6 seq=4094 GBS=1020(DP6需整除6,基线1024→1020 -0.4%) mb=1 5000步 bf16 seed1234。BLEND=base:code:math=88:8:4(4 base shards×22=88 + code 8 + math 4)。PID 1995742/1995914(torchrun)/1998724-738(6 workers)，GPU2-7 ~32.5GB 0%util(首步CUDA编译中)。 | ✅ 运行中 |
| 2026-10-09 晚 | **harness（运维代发）** | **不用 GPU；要 `.29` 的 CPU / 内存(tmpfs) / 磁盘 / 出网带宽** | **~42h（7 路并行）～ 14h（再叠 harness 内并发 N=3）** | **用户直令**（`BAIZE_HARNESS_TASK.md` 顶部 `2026-10-09⑧`）：起 **7×300 SWE-bench Lite 横评**（7 harness × 300，`--resume` 复用已有 700 条 ⇒ 新增 **1200 runs**）。⚠️ **与 pretrain 抢的是同一台 `.29`**：harness 是 agent CLI + git + unshare 沙箱（CPU/IO 重，另有 `/dev/shm` tmpfs 吃内存），**不占显存** ⇒ 与 pretrain 的 GPU 训练**可共存但会压 IO**。**互不 kill；harness 须在低负载窗口内分档上调并发（N=1→2→3，逐档验 block=0）。** | ⏸ **待资源核验**（harness 起跑前须 `uptime` + `nvidia-smi` + `df -h /dev/shm` + `free -g` 贴原文） |


---

## 4. 流水（追加行，只增不改）

| 时间 | 事件 |
|:--|:--|
| 2026-10-05 09:2x | 运维建立本文件；下发 **pretrain P-9.10**（`BAIZE_PRETRAIN_2B_TASK.md` 顶部块）与 **data 分卡协调块**（`BAIZE_DATA_TASK.md` 顶部块）。当前阻塞：P-9.8 armB(FP8) 占满 8 卡，ETA ~09:49。 |
| 2026-10-05 10:50 | pretrain 第 100 次唤醒：P-9.8 armB ✅ 已完(~09:49)；**P-9.9 tensorwise FP8 1000 步跑现占满 8 卡**（PID 4044610–17，iter 130/1000，ETA **~15:13**）→ GPU0–1 仍被 P-9.9 占用，P-9.10 实测待 P-9.9 释放后启动。本唤醒只做 P-9.10 ① CPU 预研（sglang❌不可装网络不可达；S3 ckpt❌已删除→替代 p3_dense/p3_hybrid iter_0005000 待运维确认；文献两口径✅已核实）。**data 仍需等 P-9.9 ~15:13 释放 GPU2–7。** |
| 2026-10-05 11:48 | data 第 126 次唤醒：P-9.9 tensorwise FP8 仍占满 8 卡（PID 4044610-17, iter 240/1000, ETA ~15:12）。data 侧 CPU-only 工作并行推进：base 分词 4 进程（PID 1809483/85/87/89, ~31.5GB .bin, 无 .idx=未完）+ SFT-2605 全量转换已启动（PID 3223333, 2/12 parquet 子集已出）。**GPU2-7 仍需等 P-9.9 ~15:12 完成。** |
| 2026-10-05 11:22 | pretrain 第 101 次唤醒：P-9.9 tensorwise FP8 健康 @iter 240/1000（24%，ETA **~15:12**），仍占满 8 卡。CPU-only 三方对比分析（bf16/delayed/tensorwise）：前 240 步轨迹一致（唯一变量=FP8 recipe），tensorwise s=1.158(+15.8%)。spike 区(660–780)检验 T1 待 ~13:30。**data GPU2–7 仍需等 P-9.9 ~15:12 完成。** |
| 2026-10-05 12:24 | data 第 127 次唤醒：P-9.9 tensorwise FP8 仍占满 8 卡（PID 4044610-17, etime~2h30m, ETA ~15:15）。data 侧 CPU-only 备料全速推进：① base 分词 4 进程（PID 1809483/85/87/89, ~49GB .bin, 无 .idx=未完）；② ✅ SFT-2605 转换完成（12/12 parquet, 30GB）；③ ✅ SFT-2605 分词已启动（PID 2013590, 4 进程, 12:31 起, 4 .bin 已出 ~80MB each）。**GPU2-7 仍需等 P-9.9 ~15:15 完成。** |
| 2026-10-05 13:52 | data 第 129 次唤醒：P-9.9 tensorwise FP8 **iter 740/1000（74%）**（ETA **~15:15**）。CPU-only 备料：base 分词 4 进程 ~84GB .bin ~91% done 无 .idx；SFT 分词 s3✅ / s0 进行中 / s2 进行中 / **s1 ✅ 已重启**(PID 4046447, no_think_Code 重转换完成 pyarrow 验证通过)；下载 l1_en_hq 2619/6006。**GPU2-7 仍需等 P-9.9 ~15:15 完成。** |

| 2026-10-05 13:07 | data 第 128 次唤醒：P-9.9 tensorwise FP8 仍占满 8 卡（PID 4044610-17, 100% util, ETA ~15:15, 剩约 2h）。data 侧 CPU-only 备料进展：① base 分词 4 进程（~61GB .bin, 无 .idx, 仍在跑 ~2.7h）；② SFT 分词诊断：s3✅完成(521M tok), s0/s2 进行中, **s1❌失败**(no_think_Code.parquet 损坏→🔄重转换中 76%, PID 503949 on .12)；③ 下载 l1_en_hq 2554/6006。**GPU2-7 仍需等 P-9.9 ~15:15 完成。** |
| 2026-10-05 13:55 | pretrain 第 105 次唤醒：P-9.9 tensorwise FP8 @iter 740/1000（74%，ETA ~15:15）。⚠️ **spike 区(660–740)三方对比（表 B2）**：tensorwise 峰值 +7.59%@730（比 delayed +5.11%@710 更晚更高），740=+6.55% 尚未回落到 ≤1% → spike 是 per-tensor FP8 固有现象。✅ 口径更正：三臂均 seed 1234（第 104 次写的 seed 4321 是错的）。spike-then-recovered 判定 pending 待 780–830。**data GPU2–7 仍需等 P-9.9 ~15:15 完成。** |
| 2026-10-05 14:40 | data 第 130 次唤醒：P-9.9 iter~880/1000（ETA~15:15）。⭐ **base 分词 ✅ 完成**（22.05B tok, 4 shard, 14:09）。SFT 分词：s2✅完成(3.58B tok)/s3✅(521M)/s0 进行中/s1🔧冲突修复(双进程→kill+clean+干净重启 PID 2868155)。下载 l1_en_hq 2675/6006。**GPU2-7 仍需等 P-9.9 ~15:15 完成。** |
| 2026-10-05 15:16 | **⭐ pretrain 第 107 次唤醒：P-9.9 tensorwise FP8 ✅ 完成（15:15:40 rc=0，iter 1000/1000）→ 8 卡全部释放**（`nvidia-smi --query-compute-apps`=空）。裁定：tensorwise T1/T4 FAIL（t−bf16%@1000=+5.13%）→ P-8 沿用 delayed FP8。P-9.10 ① sglang A/B：aliyun=200(有proxy)✅ 但 pypi.nvidia.com SSL EOF → cuda-tile 依赖失败 → 栈落 mcore+CUDA-graph。替代 ckpt p3_dense(4.7G)/p3_hybrid(4.2G) ✅ 核验存在（运维已批准）。**→ GPU0–1 pretrain 可起 P-9.10 实测；GPU2–7 data 可起配比，同时开跑。** |
| 2026-10-05 15:25 | **⭐ data 第 131 次唤醒：Stable S0a 臂 🚀 已启动！** P-9.9 ✅ 完成→GPU2-7 全空(4MiB/0%util)→即刻起 S0a。GBS=1020(6×170), BLEND=88:8:4, PID 1995742, GPU2-7。SFT s0/s1仍跑, s2✅(3.58B)/s3✅(521M)。下载 l1_en_hq 2744/6006, zh 171冻结, gpic 10170files/4.9T, en 2048✓。 |
| 2026-10-05 16:05 | data 第 132 次唤醒：S0a step60/5000 loss7.16 ~37.8s/iter **ETA~52h(~Oct7 20:00)**。⚠️ **recipe §6 估算"0.5-1 GPU·h×8/臂"实际为 312 GPU·h/臂(~50× 偏差)**。SAVE_INTERVAL=5000 无中间 ckpt。GPU2-7 各~39GB 35-70%util。SFT s0/s1 仍分词中。✅baize_mix_eval.sh 已备。 |
| 2026-10-05 17:30 | **⭐ pretrain 第 108 次唤醒：P-9.10 ② eager-mode 实测矩阵 ✅ COMPLETE**（GPU0–1 @.29，TS=20261005_165017）。双架构 8 格×3 reps 全收：dense=GPU0 / hybrid=GPU1，context∈{4K,16K,64K,128K}×batch∈{1,8}。**H1✅**(decode 1.6× 恒定 23.5 vs 14.7 tok/s) **H2❌**(ratio 非单调 1.59→1.62→1.63→1.58) **H3❌**(cache 18.2× 但 per-token 5.1× 更低) **H4✅**(prefill 128K 快 3.6×)。裁定：H1✅H2❌ → 论文保守表述。⚠️ CUDA graph 与 mcore StaticInferenceContext 不兼容 → 无生产栈上界。GPU0–1 全释放(4MiB/0%)。**GPU2-7 mix_stable_s0a 训练健康**（iter 40/5000, loss 10.84→7.84, 0 NaN/skip, ~38s/iter, ETA ~52h）。EXPERIMENTS P-9.10②节已写入。 |
| 2026-10-05 18:43 | data 第 136 次唤醒：**S0a step200/5000 loss5.45 ~37.2s/iter ETA~Oct7 20:00**（提速, 0NaN/0skip, 健康）。**✅✅ SFT-2605全4shard分词完成!** (s0=9.56B+s1=7.30B+s2=3.58B+s3=0.52B=20.97B tok, 79G) → Decay段SFT备料✅就绪。**🔄 SFT-Agent-2609转换+分词已启动** (PID 3836312, CPU-only, Code_Agent转换中) → Decay段最后一项备料。下载 l1_en_hq 3005/6006, zh 171冻结, gpic 3527tars, en 2048✓。GPU0-1 空闲(4MiB/0%)。git pull proxy synced。 |
| 2026-10-05 19:23 | data 第 137 次唤醒：**S0a step260/5000 loss4.88 ~38s/iter warmup完LR=1.0e-3达峰 ETA~Oct7 21:00**（0NaN/0skip, 健康, GPU2-7 50-76%util ~39GB）。**🔄 SFT-Agent-2609分词进度**: s2✅(1.23G,19:06)+s3✅(2.6G,19:16)+s0🟡(3.3G增长中)+s1🟡(3.5G增长中)→2/4完成。下载 l1_en_hq 3057/6006, zh 171冻结, gpic 3556tars, en 2048✓。GPU0-1 空闲。📉 内存滚动 MEMORY_DATA.md 33.5KB→26.2KB。git fetch proxy synced。 |
| 2026-10-05 20:02 | data 第 138 次唤醒：**S0a step330/5000 loss4.36 ~37.6s/iter ETA~Oct7 21:00**（稳定下降, 0NaN/0skip, GPU2-7 31-85%util ~39GB）。⚠️ S0a 于 16:32 被 P-9.10 benchmark 端口冲突 kill 后由 `/tmp/restart_mix_stable_s0a.sh` 重启（PID 2528081-2528090, 从 step 0 重新开始）。🔄 SFT-Agent-2609分词: s2✅(1.23G)+s3✅(2.6G)+s0🟡(7.8G.bin)+s1🟡(7.7G.bin)→2/4完成。下载 l1_en_hq 3106/6006, zh 171冻结, gpic 3457tars, en 2048✓。GPU0-1 空闲(pretrain P-9.10已完成)。D-CLEAN-4定案: 保留不动✅。git fetch proxy synced。MEMORY_DATA.md=26.9KB(≤32KB✓)。 |
| 2026-10-06 10:01 | data | GPU2-7 | ~7h | **Stable段BO搜索**（200 trial, 6 GPU并行, d=128 proxy, GP-EI, PID 2483227） | ✅ 运行中 |
| 2026-10-06 08:12 | **运维（中继 `RUN_ID 72` 核验 · outbox 7618–7731）**：**「伪」配比实验 `mix_stable_s0a`（2.2B 单臂）已不在运行** —— 到场时 `目标 PID 列表 = []`（**kill 为 no-op**）、`/tmp/restart_mix_stable_s0a.sh` **已不存在**、`crontab` **无重拉条目**、**GPU0–7 全部 `0 MiB / 0 %`**、零误杀（`baize_pretrain_loop.sh` / `baize_harness_loop.sh` / `ops_relay.sh` 全活）。⇒ **10-05「GPU2–7 归 data」的分配恢复生效**；**P-8 若起请按登记先后协调（两边不得同时占满 8 卡）**；data 的开工/收工也须在本文件登记一行。 |
| 2026-10-06 08:50 | **data 唤醒146**：held-out bin创建完成(base/code/math各~2M tok)；baize_mix_optuna.py创建完成(GP-EI替代TPE, .29离线无法装optuna)；smoke test通过(GPU2, 20步, blend=0.85/0.08/0.07, val loss 9.34→8.23, s/step=1.4s warmup后)。GPU2-7全空闲(0MiB)。**待启动200trial BO搜索**(6卡并行, ETA~7h)。 |
| 2026-10-06 10:01 | **data 唤醒148**：⭐ **BO搜索已启动！** `baize_mix_optuna.py --phase stable --n-trials 200 --gpus 2,3,4,5,6,7`（PID 2483227, nohup）。6 trial 并行(t0000-t0005)，GPU2-7 各~6.7GB/~10%util。s/step≈1.56s(warmup后)，500步/trial→~13min/trial，ETA ~7h。LR=3e-3(必验#5选定)，proxy d=128(18.5M)。**LR已从1e-3修正为3e-3**。 |

| 2026-10-06 08:22 | **data 唤醒145**：🔴 **S0a 2.2B单臂已kill改道代理模型BO搜索**。校准完成（GPU2-4, 3×LR×50步, 92.7M proxy h=512/L=14, s/step≈1.5s, loss@50 best@LR=1e-3=7.08）。GPU2-4已释放。下一步=held-out bin→Optuna study（6卡并行, 500步/trial, T≈691>400）。GPU0-1/5-7空闲。 |

2026-10-06 11:25 data-agent START BO search resumed (trial 19+, 19 existing, fix GP race condition) GPU2-7
| 2026-10-09 晚 | **运维：harness 7×300 下发 + `.29` 资源协调** —— 用户直令（`BAIZE_HARNESS_TASK.md` 顶部 `2026-10-09⑧`）：① 交付 7×100 HTML 报告；② 起 **7×300**（Lite 全量 300，`--resume` ⇒ 新增 1200 runs），**并发已批准但要先堵 7×100 的坑**：`run_serial_kimi.py:238-239` 的 `workdir`/`rootfs` **只按 repo 索引、没带 harness 维度** ⇒ 7 路共享同一 workdir/testbed，实测 **88 例 blocked**（`git checkout` 冲突 + `shallow.lock` 争用）；已下令 **workdir per-harness 隔离 + rootfs `flock` 全局锁**（只锁 `setup_rootfs`/`eval_instance`，agent 运行段仍无锁并行）后再分档上调并发。⚠️ **`.29` 与 pretrain 共用**：harness 不占显存但 IO/CPU/内存(tmpfs) 重 ⇒ **双方不 kill，harness 走低负载窗口**；`GPU29_ALLOC.md §3` 已登记申请行。 |
| 2026-10-07 上午 | **运维（用户直令）**：**长上下文推理成本矩阵改去 `.12` 取卡** —— 用户指出 `.12` **GPU1–7 空闲**（GPU0 被 vision 的 lp bridge PID 807654 占至 ~11:00）⇒ **本项优先借 `.12` GPU1–2（至 11:00）**，**暂不向 data 索卡**（避免 Round2 BO 从 8 槽降速、P-8 前置顺延）；对账簿新建 `run/GPU12_ALLOC.md`。**仅当 `.12` 不可用时**才按 §1 申请 GPU0–1（pretrain 静态归属；BO 现以 `--gpus 0-7` 超额占用，62,613 MiB/卡）。⏰ 提醒：**`util%` 低 ≠ 空闲**，显存被占的卡装不下 1M hybrid（需 34.7GB）⇒ 必须整张空卡；🚫 双方均不 kill 对方进程。 |
| 2026-10-09 23:20 | **harness R229** | **不用 GPU；CPU·内存·磁盘·网络** | **~42h（N=1）** | **7×300 起跑前资源核验**：① `uptime`→`load average: 10.18, 10.26, 10.70`（96核，正常）；② `free -g`→`total 2015 used 58 free 1066 buff/cache 890 available 1943`（充裕）；③ `df -h /dev/shm`→`1008G total 3.2G used 1005G avail 1%`（per-harness workdir ×7 无压力）；④ `nvidia-smi`→`sglang::scheduler ×2 (80GB+76GB)`=pretrain GPU0-1 训练（不冲突，harness 不占 GPU）。✅ **资源核验通过**。②-A 代码已改：`run_serial_kimi.py` per-harness workdir + rootfs flock + `--per-instance-workdir` flag。Smoke test 运行中（opencode × 2 django 新题）。ETA ~42h wall（N=1, hermes 瓶颈）；N=3 ⇒ ~14h。 | ✅ **已核验，待 smoke test 确认 block=0 后起跑** |

