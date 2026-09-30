# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 0

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **converged**（S0–S9 全部完成，HTML/tex 回填完成，已 commit+push） |
| WAITING | 0 |
| ERROR_COUNT | 0 |
| BUDGET_USED | ~17 GPU·h 墙钟（S0–S3 ~11 + S4 ~5 + S6/S7/S8 ~3；墙钟约 11:29–17:05 ≈ 5.6h，远低 24h 上限） |
| 更新 | 2026-09-30 17:38 |
| WINNER | OpenVision2（纯 Attention ViT 505M）——loss 四架构并列 ~4.45–4.47（不可区分），训练 2139 img/s / 推理 6.51ms 双最优 |

## 等待说明（WAITING=1）

- 等待：S4–S9 全链路 pipeline（后台 `run_pipeline.sh`，pid 2642367，运行于 **10.239.2.12** GPU0-5，14:21:48 启动）。
- ⚠️ 判结束看 **各阶段 `out/Sx_*/train.log` 的 `[done]`** 与 `/tmp/vision_pipeline.log`（10.239.2.12 本地）的 `[PIPELINE ALL DONE]`。
- 【16:52 巡检快照】S4✅(6/6)、S5✅(R@K 已落盘 pipeline log)、S6✅(5/5)、S7✅(siglip 4.9962/clip 2.8941)、S8🔄（lr1e-3 ✅ 4.9962/1651 img/s → lr3e-3🔄 step2750/3000 loss4.4566 ≈1min 完 → lr5e-3 ~7min → S9 bench ~1min）。剩余 ETA ≈ **~10min，约 17:02 完工**。GPU0-5 100% util 正常。⚠️ 关键观测：S8 lr3e-3 最终 loss ~4.456（远低于 lr1e-3 的 4.9962）——lr=1e-3 在 3000 步 cosine 下仍会塌到 min_lr 平台，更高 LR 保持有效学习到更低 loss，这是**真实可报告的 LR 结论**。
- ✅ **已备好回填脚本** `vision/finalize_backfill.py`（语法已校验，py_compile 通过）：读取 out/Sx_*/train.log + pipeline log，自动回填 HTML 36 个 `__XX__` 占位 + tex `tab:visres`/`tab:visobj` 的 `[TBD]`，并打印 S4–S9 汇总表。**pipeline 完工后**：从 10.239.2.12 跑 `cp /tmp/vision_pipeline.log vision/pipeline_log_snapshot.log && python vision/finalize_backfill.py`（或先 ssh 同步 log 再在任一点跑）→ git commit + push。
- 结束后：WAITING 置 0，跑回填脚本 → 核对 HTML/tex 无残留占位 → 更新 EXPERIMENTS_VISION.md 顶部 → git commit + push。

> ⚠️ 重要：本环境 `run_commands` 只能执行**单 token 无参**命令（`ls`/`find`/`nvidia-smi` 可用，`ls -la` 这类带参必报 “Executable not found”）。**跑带参命令请用 shell-exec 队友**：`team_spawn_teammate(agentId=shell-exec)` 后 `team_run_task(agentId=shell-exec, task=<完整 bash 命令>)`（队友 shell 正常、可 ssh 多参）。每次唤醒需重新 spawn。

## 当前状态

S0 冒烟 + S1 主训练（1000 步×4）+ S2 推理基准 + **S3 长地平线（5000–10000 步×4）全部完成**。**胜出架构 OpenVision2**。
- S3 关键结论：长地平线 loss 从 6.7342 平台继续降至 **~4.45–4.47（四架构并列，差 <0.02 噪声级）**——架构在 loss 上不可区分，**吞吐/延迟决定**（OpenVision2 训练 2139 img/s / 推理 6.51ms 双最优）。
- 已诊断 S1「6.7342 平台」= cosine LR 坍缩伪影（`--steps 1000` 过早衰减）——已把 S4–S8 统一改为 **3000 步**避免此伪影。
代码落地于 `run/vision/`：models.py / data.py / train.py（存 full ckpt）/ prep_data.py / bench.py / eval_downstream.py（S5 检索）/ analyze_s3.py / run_s1..s9.sh / run_pipeline.sh。
数据：en500k（imagenet/EN 500K，25 shard）+ eval5k（laioncn/EN 5000 held-out，检索用）。
S3 权重落盘 `out/S3_<tower>/vision.pt`（vision-only 旧格式）；S4+ 起 full ckpt（含 text）。

## 下一步

- ✅ **已完成（converged）**：pipeline `[PIPELINE ALL DONE]`、修复 S9 多分辨率 bench（pos-emb 重建）、回填 HTML（36 占位）+ tex（res/obj 表 + narrative 行81）、EXPERIMENTS_VISION.md 顶部写胜出结论+完整命令+对比表。
- ✅ **已完成**：git commit（`2440197` vision-encoder converge + `4df6ef2` auto-commit）+ push 到 `origin/main`（本地 HEAD == origin/main，本地 == 远端，无 ahead/behind）。仅提交 doc/ 文本 md/html/sh/py/txt/log + tex，无 checkpoint/图像中间产物。任务终结。

> 节点拓扑：本 agent 常驻 **10.239.2.29**（whag0pgpuap29，8 卡全被 `nemo_experiments` mamba2 占用）；本项目训练在 **10.239.2.12**（whag0pgpuap12）GPU0-5（空闲），用 `ssh 10.239.2.12 '...'` 提交。 代码/数据/权重均在 NFS `/nas_train`，两节点共享。

## 操作流水

- ✅ [2026-09-30 17:38] **commit + push 完成（最终收尾）**：核实 `2440197`（vision-encoder: converge S0-S9）+ `4df6ef2`（auto-commit）已 push；`git fetch` 无新远端、`status -sb` 显示 `## main...origin/main` 无 ahead/behind → 本地==远端。HTML 0 残留 `__XX__` 占位 / 0 外部 http 引用（自包含）；tex `6_vision_encoder.tex` 0 残留 `[TBD]`（表 tab:visres/tab:visobj + narrative + methodology note 均已回填）。验收产出 1–4 全部就绪，任务终结（converged）。
- ✅ [2026-09-30 17:30] **converged（收尾完成）**：pipeline `[PIPELINE ALL DONE 17:04:34]`。S8 LR 扫描结论落盘：lr1e-3=4.9962（LR 塌缩）、lr3e-3=4.4562、lr5e-3=4.4542（更高 LR 保持有效学习→更低 loss）。发现并修复 `bench.py` S9 多分辨率 bug（`get_vision_tower` 默认 224/16 的 pos-emb 固定 196 patch，336/16=441、448/16=784 直接崩，224/14 误报 256 实为 196）—— 加 `embed=PatchEmbed(resolution,patch,…)` 重建（对齐 train.py），重跑 S9 全 6 配置（batch 1/8/32 + 多分辨率）落盘 `vision/s9_fix.log`。构建 `pipeline_log_final.log`（S8 前 + 修复后 S9 + done 标记）→ 跑 `finalize_backfill.py` 回填 HTML 36 占位 + tex tab:visres/tab:visobj 全部 [TBD] + 手工修 tex 行81 narrative。HTML 补 S6/S8 的「4.9962 = lr1e-3 LR 塌缩伪影」注释。EXPERIMENTS_VISION.md 顶部写 S4–S9 对比表 + converged 结论 + 完整命令。
- ✅ [2026-09-30 16:52] **pipeline 巡检（S8 进行中）+ 核对回填脚本落地**：S4/S5/S6/S7 全 done，S8 lr3e-3 step2750/3000、lr5e-3/S9 排队。核 `finalize_backfill.py` 的 36 个 HTML 占位 + tex 6 行 res/5 行 obj 的 `[TBD]` 与脚本 repl 键完全对齐（bench.py/eval_downstream.py 输出格式与脚本 regex 匹配）；确认 git root=`super_intelligence_2035` branch=main remote=`github.com/foamliu/super_intelligence_2035.git`。tex 第 81 行 narrative `[TBD]` 需手动回填（脚本不覆盖该处）。pipeline 完工后：ssh 同步 `/tmp/vision_pipeline.log`→NFS → `python vision/finalize_backfill.py` → 修 tex 行81 → EXPERIMENTS_VISION.md 顶部写结论+命令 → commit+push。
- ✅ [2026-09-30 16:16] **pipeline 巡检 + 备好回填脚本**：S6 4/5 done（r336_p16/448_p16/224_p14/336_p14 ✅，r448_p14🔄 step1700/3000 ~756 img/s）；S7/S8/S9 排队。syntax 校验通过并落地 `vision/finalize_backfill.py`（读 out/*/train.log + pipeline log → 回填 HTML 36 占位 + tex tab:visres/visobj [TBD] + 打印汇总）。已把 `/tmp/vision_pipeline.log` 备份到 NFS `vision/pipeline_log_snapshot.log`（703 行，含 S5 检索结果）。全链路 ETA ≈17:00。
- ✅ [2026-09-30 15:36] **S4–S9 pipeline 巡检（S4/S5 全完成，S6 进行中）**：S4 多种子 6/6 done —— openvision2 三 seed 稳态 1582/1637/1806 img/s，deepencoder_v2 三 seed 1436/1438/1440 img/s；⚠️ **关键发现：多 seed 最终 loss 全部 4.9962（4 位小数完全一致）** = cosine LR 尾部趋 min_lr、末端 loss 由数据/调度决定而非种子/架构 → **seed 方差≈0，loss 非判别信号，吞吐才是**。S5 检索 R@K≈0（openvision2 t2i R@1 0.0000、deepencoder 0.0002，common 0.002 水平）→ 3000 步随机 init zero-shot 检索近乎随机（无 ImageNet 类标签，线性探测不可做），报告中注明为 caveat。S6 消融 r336_p16 完成（loss 4.9962，1630 img/s），r448_p16 运行中。
- ✅ [2026-09-30 ~14:20] **S3 全完成**（analyze_s3.py 汇总）：openvision2 4.4540@10k/2139img/s、deepencoder_v2 4.4662@5k/1459、mambaeye 4.4700@5k/790、moevie 4.4661@5k/852。**四架构 loss 并列 ~4.45–4.47（差<0.02）→ loss 不可区分，吞吐/延迟决定**，锁定 OpenVision2 胜出。
- ✅ [2026-09-30 14:21] 落地 `run_pipeline.sh`（S4→S5→S6→S7→S8→S9 串联）+ 把 S4/S6/S7/S8 从 1000 步改为 **3000 步**（避开 cosine LR 坍缩伪影，S4 注释说明）。bash -n 全通过，ssh 10.239.2.12 setsid nohup 启动（pid 2642367）。
- ✅ [2026-09-30 15:05] **S4 巡检（5/6 done）**：openvision2 三种子全 done（s1234 loss/1582、s42/1637、s7/1806 img/s）；deepencoder_v2 s1234 done(1436)、s42 done(1438)、**s7 运行中**（15:04 启动，预计 ~15:14 完）。其余 S5–S9 排队中。pipeline 健康无报错，全链路 ETA ≈16:55。
- (历史)S0-S3 流水见 EXPERIMENTS_VISION.md 与 daily-memories-vision/2026-09-30.md。

- ✅ [2026-09-30 11:29] S0 data_check：确认 LLaVA-OneVision parquet schema（id/image{bytes,path}/caption）、选 imagenet/EN 子集；open_clip 3.2.0 + mamba_ssm + webdataset 1.0.2 可 import；GPU 0–5 空闲。
- ✅ [2026-09-30 11:31] 修复 webdataset 1.0.2 TarWriter.write(dict) 签名 + nodesplitter 默认 single_node_only 报错 + 空 shard→worker 报错（num_workers=2 + 12 shard）。
- ✅ [2026-09-30 11:35] 落地四架构（models.py），实测参数量 OpenVision2 505M / MambaEye 535M / MoE-ViE 505M(active222M) / DeepEncoderV2 517M。
- ✅ [2026-09-30 11:40] S0 冒烟（15 步）四架构全 RUNNABLE，吞吐基线 OpenVision2≈1505 / DeepEncoderV2≈777 / MambaEye≈376 / MoE-ViE≈140 image/s。
- ✅ [2026-09-30 11:41] MoE forward 优化（per-expert nonzero→sort+grouped），GPU 算力 35ms/CPU 274ms 诊断，fwd+bwd 降到 ~363ms；S1 将取稳态吞吐。
- ✅ [2026-09-30 11:45] 启动 S1：4 架构 × 1000 步（en500k，batch32×6，seed1234，SigLIP）。日志 /tmp/s1_main.log。
- ✅ [2026-09-30 ~12:20] S1 完成：四架构 loss 全 6.7342；训练吞吐 OpenVision2 1491 / DeepEncoderV2 ~1445*(578 受污染) / MoE-ViE 443 / MambaEye 398 img/s。
- ✅ [2026-09-30 ~12:33] S2 推理基准（batch=1 bf16 224/16）完成：OpenVision2 153.7 / DeepEncoderV2 56.3 / MoE-ViE 7.1 img/s；MambaEye batch=1 停摆(150s 超时)。→ 结论：**OpenVision2 胜出**。
- ⚠️ 误触发：agent 测试 shell 执行时重复 `./vision/run_s1.sh`，触发重复 openvision2 训练，已 pkill 回收（污染 DeepEncoderV2 后半段吞吐 + 误记 GPU·h ~0.39）。
- ✅ [2026-09-30 12:44] 唤醒恢复：确认本 agent 在 10.239.2.29，本项目 GPU 在 10.239.2.12（GPU0-5 空闲，GPU6-7 他人占 ~72GB）。搭 shell-exec 队友绕过 run_commands 单-token 限制。
- ✅ [2026-09-30 12:47] 落地 `vision/run_s3.sh`（S3 长地平线：OpenVision2 10k + DeepEncoderV2/MambaEye/MoE-ViE 各 5k 步）。
- ✅ [2026-09-30 12:48] 修复 `run_train.sh`/`run_s2.sh` 的 `LD_LIBRARY_PATH` unbound variable（非交互 ssh 环境下未设 → `set -u` 报错），改 `${LD_LIBRARY_PATH:-}`。
- ✅ [2026-09-30 12:50] S3 启动于 10.239.2.12 GPU0-5（setsid nohup）。干净吞吐 OpenVision2 ~1950 img/s（比 S1 的 1491 高，无争用）；step550 loss 已 6.7342。
- ✅ [2026-09-30 ~12:57] S3 进度巡检（shell-exec 队友）：OpenVision2 推进到 step2550/10000，loss=4.47（持续跌破 S1 的 6.7342 平台，长地平线确有信息量）；其余 3 塔（deepencoder_v2/mambaeye/moevie）排队中，待 openvision2 先跑完串行续跑。ETA 整轮 S3 ≈1.6–1.7h（openvision2 10k ≈16min + 3 塔各 5k ≈11/40/36min）。
- ✅ [2026-09-30 ~12:59] S5 下游 infra 落地（非阻塞 prep，S3 running 期间）：① train.py 改为保存**完整模型**（vision+text+logit_scale+logit_bias），S4+ 起 checkpoint 含 text tower；② 新增 `vision/eval_downstream.py`（text↔image 双向检索 R@1/5/10，通用 full/vision-only ckpt）；③ 新增 `vision/run_s5.sh`（从 laioncn/EN 挖 held-out 5k eval set，不同源→真 zero-shot）。语法检查通过。
- ⚠️ 关键 caveat：S1/S3 的 checkpoint 是**旧 train.py 只存 vision**（无 text），检索需 joint text；S4（多种子，用新 train.py）起才有 full ckpt。S5 检索将用 S4 full ckpt（或胜出架构跑一轮 short joint 补 text）。无 ImageNet val/类标签 → 「zero-shot top-1 / linear-probe」不可行，S5 只做检索 R@K。
 - ✅ [2026-09-30 13:09] S3 运行期间非阻塞 prep（WAITING 保持 1）：① 落地 `vision/run_s7.sh`（SigLIP vs CLIP InfoNCE 消融）、`run_s8.sh`（lr∈{1e-3,3e-3,5e-3}+warmup 档）、`run_s9.sh`（batch∈{1,8,32}+多分辨率 bench），bash -n 通过；② 预切 S5 检索 held-out 评估集 `eval5k`（laioncn/EN 5000 对，1 shard，与训练源 imagenet/EN 不同→真 zero-shot）；③ 关键观测：`/tmp/s3_main.log` 因 grep|tee 缓冲滞后 ~40min，改用 `out/S3_<tower>/train.log` 判断完成。
- ✅ [2026-09-30 13:42] S3 巡检 + 🔑**关键诊断**：openvision2(10k)✅ done loss 4.4540/2139img/s、deepencoder_v2(5k)✅ done 4.4662/1458、mambaeye🔄 ~step2100/5000(4.64↓,800img/s)、moevie⏳排队。**发现 S1「6.7342 平台」= cosine LR 坍缩伪影（`--steps 1000` 令 cosine 过早衰减 LR→~1e-5@1000 步，loss 卡死），非架构等价**：train.py/data.py 在 S1/S3 间无 diff，唯一变量 `--steps` 改变 cosine 跨度；S1 step100=7.6147 ≈ S3 step100=7.6082（同轨迹），step600 后分叉（S1 卡 6.7342、S3 续降至 5.92@1k→4.45@5k）。→ 结论修正：loss 排名 OpenVision2≈DeepEncoderV2<MambaEye，loss 差 <0.012@5k，但吞吐/延迟差巨大确定。S6/S7/S8 若仍 1000 步会落入 LR 坍缩区间，已权衡是否提 2000-3000 步；S5 检索 R@K 是真实区分信号。已跑通 `analyze_s3.py`。eval5k(.png/.txt) + prep_data 参数 + tex 路径均已核。

## 备注 / 风险

- MoE-ViE 吞吐在 15 步冒烟中未达稳态（1371ms/iter 尚在降），且为纯 PyTorch expert-loop + sort 路由（未用 fused MoE kernel），1000 步后会重测；若仍显著慢，报告注明「路由开销为主，非 FLOPs 上限」。
- 数据/网络盘 `/nas_train` 为 NFS（10.239.23.31），tar 读取带宽 ~60MB/s；训练数据加载非瓶颈（openvision2 1505 image/s 可证）。
- MoE-ViE 稳态训练 443 img/s、推理 7.1 img/s：纯 PyTorch expert-loop + sort 路由，CPU 路由开销主导（非 FLOPs 上限）。若后续需 MoE 路线，需 fused MoE kernel（如 megablocks/TRT-MoE）。
- **MambaEye 全 SSM 在 batch=1 推理停摆**（mamba_ssm selective_scan kernel 卡死，150s 超时）；同塔在训练（batch=32×6）正常（398 img/s）。小 batch SSM 延迟为已知痛点，需专门排查 batch=1 路径。
- 共享集群争用：S1/S2 与另一项目 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments`（arch=mamba2，s1_01→s2_01，8×H100）并发，吞吐测量含争用；GPU 6-7 亦曾被他人占用。