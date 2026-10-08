# GPU12_ALLOC.md — `10.239.2.12`（8×H100）分卡账本 · **vision ⇄ pretrain 共用**

> **为什么有这文件**：2026-10-07 **用户直令** —— pretrain 的**长上下文推理成本矩阵**（sglang，ctx 128K/256K/512K/1M）
> **去 `.12` 的空卡上跑**（`.29` 被 data Round2 BO 占满 **62,613 MiB/卡**）。`.12` 原是 **vision 的机器** ⇒ 这个文件就是双方的对账簿。
> 🚫 **agent 不许删别人的历史行**；只在「**申请区**」与「**流水**」里**追加**。

---

## 1. 当前归属与占用（2026-10-08 快照）

| 卡 | 归谁 | 用途 | 状态（vision 08:15 自测） |
|:--|:--|:--|:--|
| GPU0–7 | **vision** | 🔬 **scaling E1 resumed** 1 epoch AIMv2 | 🚧 **运行中(resumed)**：~16.5GB/卡, 61-96% util; step ~130340/187,101 (69.7%), ~5100 img/s, loss~1.3, no collapse; E1 crashed@131490(shm)→resumed from 130k ckpt PID1743002; e2_watcher_v2 PID1743003 auto-chains E2; **ETA ~04:00 Oct 9** |
| ~~GPU1–7~~ | ~~pretrain~~ | ~~长上下文成本矩阵~~ | ✅ **已交还**（2026-10-07 借出, 已完成） |

> ⚠️ `.12` 的 GPU0–7 **全部属本项目**。起跑前必须核验；**若看到与本项目无关的进程 → 停手报告**，🚫 不许 kill。

---

## 2. 铁律

1. **默认只碰自己名下的卡**，起跑前采样并把**原文**贴进自己 MEMORY：
   ```bash
   nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv
   nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
   ```
2. ⚠️ **`util%` 低 ≠ 空闲** —— 只认 `memory.used`；**显存已被预分配的卡不可共卡**（sglang `--mem-fraction-static` 或训练的 60+GB 都会挡住大模型）。
3. 🚫 **绝不 kill 对方进程**（尤其 `lp bridge` 的 PID 807654）；要卡**走申请区**、**等对方在安全边界让出**。
4. **让卡优先序**：`vision 训练臂 / 桥接` > `pretrain 推理评测`；同级**先到先得**。
5. **时间片到期必须交还**：pretrain **11:00 硬交还**（或提前在申请区续借）；交还时**必须 `kill` 自己的 sglang server** 并核 `memory.used ≈ 0`，写进 §4 流水。

---

## 3. 申请区（追加行；状态由申请人自己回填 `已批准 / 已让卡 / 已归还`）

> 格式：`| 日期 时间 | 申请人 | 要哪几张 | 多久 | 为什么 | 状态 |`

| 日期 时间 | 申请人 | 要哪几张 | 多久 | 为什么 | 状态 |
|:--|:--|:--|:--|:--|:--|
| 2026-10-07 上午 | **pretrain（运维代发）** | **GPU1–7（全部 7 张）** | **目标 30–45 min 跑完即还**（硬天花板 11:00） | 用户直令②：「**何必只用 1、2，让 pretrain 用 `.12` 的 1–7 把长上下文并行测完**」⇒ 一格一卡扇出：hybrid@128K/256K/512K/1M（GPU1–4）+ dense@128K/256K/512K（GPU5–7），dense 1M 第 2 波；`.29` 已被 data BO 占满（62.6GB/卡，不可共卡） | ✅ 已批准（用户两次直令） |
| 2026-10-07 09:42 | **vision** | **GPU0–7（全部 8 张）** | **~4.5–9.5h**（mask-ratio 5臂消融） | lp bridge 已完成(PID 807654 退出, GPU0 释放). nvidia-smi 显示 8 GPU 全空闲(pretrain 矩阵尚未占卡). ② mask-ratio 消融需 8 GPU(CUDA_VISIBLE_DEVICES=0-7). 按运维指令「确有 8 卡硬需求⇒在账本申请区写一行, pretrain 必须让」⇒ **申请 8 GPU 开跑 ② mask-ratio** | ✅ 已开跑（09:52, 8 GPU 全占用 16.4GB/卡, arm 0.3 step200/30k, ~4500 img/s） |
| 2026-10-07 10:30 | **pretrain（运维代发）** | **`.12` 任意 1 张空卡（或 GPU0–7 的余量）** | **~30–60 min**（用户令：hybrid ctx 扩 2M/4M/8M/16M） | 用户直令③「安排 pretrain 在 hybrid 这边**继续提升 ctx 到 2m、4m、8m、16m**」＋ 显存归因诊断。⚠️ pretrain **09:44 已提前归还** GPU1–7，vision **09:52 占 8 张**；`.29` 被 data BO 占满 ⇒ **本轮无空卡**。按优先序 **vision > pretrain 推理评测** ⇒ **不抢占**；**待 vision 消融出现空窗/单卡余量时插入**，或 vision 明确让 1 张 | ⏸ **待卡（未开跑）**；若无空窗 ⇒ pretrain 记「无可用 GPU，未执行」、脚本备好待补跑 |
| 2026-10-07 20:08 | **vision** | **GPU0–7（全部 8 张）** | **~8h**（weight-ratio 4臂消融+eval） | ② mask-ratio 消融 ALL DONE(5 arms 09:52→19:42, IN-1k eval done 20:06). 8 GPU 重新空闲. ③ weight-ratio 消融需 8 GPU(4 arms: contrast:patch = 1:2/1:0.5/0.5:1/2:1, 30k steps/arm). 按既有优先序 vision > pretrain 推理 ⇒ **继续占用 8 GPU** | ✅ 已开跑（20:08, PID 187262, 8 GPU 16.5GB/卡 65-80%util, arm cw1_plw2 step~550/30k, ETA all+eval ~04:30） |

---

## 4. 流水（追加行，只增不改）

| 时间 | 事件 |
|:--|:--|
| 2026-10-07 上午（精确时刻见本条 commit） | **运维建立本文件**：用户指出「`.12` GPU0 被 bridge 占至 10–11AM、**GPU1–7 空闲**」⇒ **批准 pretrain 借 GPU1–2** 跑长上下文推理成本矩阵（`BAIZE_PRETRAIN_2B_TASK.md` 顶部块；`BAIZE_VISION_TASK.md` 同步告知）；**`.29` 侧不向 data 索卡**（避免 Round2 BO 由 8 槽降速、P-8 前置顺延）。依据：env/ckpt 全在 NFS 共享路径（`/nas_train/app.e0031982/miniforge3/envs/vllm`、`nemo_experiments/p3_{hybrid,dense}/hf_iter_5000`），`.12` **零改造**可跑。 |
| 2026-10-07 上午（同日第 2 条） | **用户直令②**：「**何必只用 1、2 呢，让 pretrain 用 `.12` 的 1–7 把长上下文并行测完**」⇒ 借用范围 **GPU1–2 → GPU1–7**；**一格一卡扇出**（GPU1–4 hybrid 四档 / GPU5–7 dense 128K-512K，dense 1M 第 2 波）；**并行启动器已入库** `run/p911e_matrix_launch.sh`（含逐格 GPU 占用预检、错峰 `STAGGER=20s`、逐格 `kill` server + 归还核验、逐格 JSON）；**目标 30–45 min 跑完即还**（硬天花板 11:00），并已在 `BAIZE_VISION_TASK.md` 同步「此期间 vision 要不到卡」的口径。 |
| 2026-10-07 09:52 | **vision 开跑 ② mask-ratio 消融**：lp bridge 全部完成(PID 807654 退出, GPU0 释放), 8 GPU 全空闲. 按运维指令申请 8 GPU 并开跑 run_mask_ratio_ablation.sh(5 arms: 0.3/0.5/0.6/0.75/0.9, 30k steps/arm, ~4500 img/s, ETA ~4.5h). 8 GPU 全占用 16.4GB/卡. pretrain p911e_matrix_launch.sh 有逐格 GPU 占用预检, 若启动会检测到 vision 占用并等待. |
| 2026-10-07 20:08 | **vision ② mask-ratio ALL DONE → ③ weight-ratio 消融开跑**：5 arms 09:52→19:42 全部 exit 0, IN-1k eval 20 ckpts done 20:06. 结果: 0.6 最优(lp=13.49%), 倒U形. 8 GPU 重新空闲后立即开跑 ③ weight-ratio(4 arms: 1:2/1:0.5/0.5:1/2:1, 30k steps/arm, PID 187262, 8 GPU 16.5GB/卡 65-80%util, ETA all+eval ~04:30). |
| 2026-10-07 **09:44** | **pretrain 全部归还 GPU1-7**：Wave 1（7 格并行 hybrid@128K/256K/512K/1M + dense@128K/256K/512K）+ Wave 2（dense@1M）全部完成。`nvidia-smi` 确认 GPU1-7 全部 `memory.used≈0`。8 个 cell JSON 已入 `p911e_results/`。✅ **已归还 09:44**（远早于 11:00 硬天花板）。vision 可恢复使用 GPU1-7。 |
| 2026-10-08 07:53 | **vision** | **GPU0–7（全部 8 张）** | **~2.5h**（④ AIMv2 AR Arm B 30k + eval） | ③ weight-ratio 消融 ALL DONE(@05:27, GPU已释放). 8 GPU 全空闲. ④ 官方 AIMv2 AR 范式 Arm B 30k 需 8 GPU(causal ViT + AR decoder, ~203.7M params). smoke test✅(2069 img/s, 30k ETA~2.1h). 脚本 run_aimv2_ar.sh 自动 smoke→30k→eval. 按既有优先序 vision > pretrain 推理 ⇒ **继续占用 8 GPU** | ✅ 已开跑（07:57, 8 GPU 22.5GB/卡 48-85%util, step100/30000, ETA~10:00） |
| 2026-10-08 07:57 | **vision ④ AIMv2 AR Arm B 30k 开跑**: ③ weight-ratio ALL DONE(@05:27, GPU已释放). 8 GPU 全空闲(nvidia-smi 4MiB/卡). smoke test✅(30步/9.1s/exit0, 2069 img/s). 30k full run START@07:58: step100/30000, loss=5.94, ~2185 img/s, 8 GPU 22.5GB/卡 48-85%util. ETA~10:00. 脚本 run_aimv2_ar.sh 自动 smoke→30k→IN-1k eval. |
| 2026-10-08 19:00 | **vision 🔬 scaling 对比实验**: 8 GPU 全空闲(4MiB/卡). 运维指令 2026-10-08⑤ 用户直令: E1(OV2 w512/d30,126.8M,224/p16) vs E2(官方OV2结构 w1024/d24,304M,336/p14), 同 AIMv2 objective/数据(94.9M)/1epoch/bs512. smoke test 测两臂吞吐→报ETA→写预注册→开跑. 脚本 run_scaling_experiment.sh. |
