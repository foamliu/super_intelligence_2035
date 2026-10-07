# GPU12_ALLOC.md — `10.239.2.12`（8×H100）分卡账本 · **vision ⇄ pretrain 共用**

> **为什么有这文件**：2026-10-07 **用户直令** —— pretrain 的**长上下文推理成本矩阵**（sglang，ctx 128K/256K/512K/1M）
> **去 `.12` 的空卡上跑**（`.29` 被 data Round2 BO 占满 **62,613 MiB/卡**）。`.12` 原是 **vision 的机器** ⇒ 这个文件就是双方的对账簿。
> 🚫 **agent 不许删别人的历史行**；只在「**申请区**」与「**流水**」里**追加**。

---

## 1. 当前归属与占用（2026-10-07 快照）

| 卡 | 归谁 | 用途 | 状态（vision 07:12 自测 + 用户旁证） |
|:--|:--|:--|:--|
| **GPU0** | **vision** | `lp 协议 A/B 桥接`（`vision/lp_protocol_bridge.py`, PID 807654） | 🚧 **占用中**：2.4GB / 39% util（NFS I/O bound）；ckpt1 ✅（Δlp=**+10.05pp**）、ckpt2 streaming ~51%、ckpt3 待跑；**ETA ~10:00–11:00** |
| **GPU1–2** | **pretrain（借出）** | 长上下文推理成本矩阵（GPU1=hybrid、GPU2=dense，各 4 档顺序） | 📌 2026-10-07 运维代申请 → **✅ 批准，借用至 11:00**（见 §3） |
| **GPU3–7** | **vision** | 排队项（mask-ratio/权重比消融、AIMv2 官方 AR 范式、text-AR…） | ⬜ 空闲；**11:00 前 vision 可自由用** |

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
| 2026-10-07 上午 | **pretrain（运维代发）** | **GPU1–2** | **至 11:00**（不够则续借 ≤2h） | 用户直令：sglang 长上下文推理成本矩阵（ctx 128K/256K/512K/1M，hybrid ⚔ dense，吞吐/prefill/decode/显存）；`.29` 已被 data BO 占满（62.6GB/卡，不可共卡） | ✅ 已批准（用户当场点头） |

---

## 4. 流水（追加行，只增不改）

| 时间 | 事件 |
|:--|:--|
| 2026-10-07 上午（精确时刻见本条 commit） | **运维建立本文件**：用户指出「`.12` GPU0 被 bridge 占至 10–11AM、**GPU1–7 空闲**」⇒ **批准 pretrain 借 GPU1–2** 跑长上下文推理成本矩阵（`BAIZE_PRETRAIN_2B_TASK.md` 顶部块；`BAIZE_VISION_TASK.md` 同步告知）；**`.29` 侧不向 data 索卡**（避免 Round2 BO 由 8 槽降速、P-8 前置顺延）。依据：env/ckpt 全在 NFS 共享路径（`/nas_train/app.e0031982/miniforge3/envs/vllm`、`nemo_experiments/p3_{hybrid,dense}/hf_iter_5000`），`.12` **零改造**可跑。 |
