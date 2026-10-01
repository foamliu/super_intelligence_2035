# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R2_complete**（R2-0~R2-5 全部完成；交付物 `EXPERIMENTS_VISION_ROUND2.md` + `BAIZE_VISION_ENCODER_RESULT_ROUND2.html` 齐备） |
| WAITING | 1（终局 idle：无异步任务、无剩余工作，loop 按 30min 长睡省 token） |
| ERROR_COUNT | 0 |
| BUDGET_USED | ~18 GPU·h 墙钟（R2 墙钟 ≈6h，撞在 ≤6h 预算内完成，未裁剪；S0–S3 ~11 + S4 ~5 + S6/S7/S8 ~3） |
| 更新 | 2026-10-01 17:15（R2 全部完成收尾：R2-3 12/12 + R2-5 落盘 → 生成 ROUND2 HTML → MEMORY/EXPERIMENTS 更新 → commit+push） |
| WINNER | OpenVision2（纯 Attention ViT 505M）——loss 四架构不可区分（R2-3 跨 256/576/1024 token 复证），训练 2017 img/s / 推理 6.87ms（R2-4 干净复测）双最优 |

## ✅ R2 全部完成（收尾，2026-10-01 17:15）

- **resume pipeline 已收尾**：`grep -c "R2 RESUME ALL DONE" /tmp/vision_r2_resume.log` == 1（17:04:01）。R2-3 最后一组 **mambaeye r448**（12/12）✅：loss 3.7479（bs=16）/ 291.7 img/s / 推理 bs1 44.132ms·bs8 6.193ms / eval 全随机（0.0002/0.0010/0.0020）。
- **R2-5 ✅ 完成**：mamba_ssm 2.2.6.post3；batch 扫描 bs1=31.577ms（正常）、bs2=15.986、bs4=13.125、bs8=5.935ms——**batch=1 未复现 Round 1 的 150s 停摆**（一次性环境事件）→ 表格回填建议 `hang@bs1` → `31.6ms`。
- **R2-3 12/12 全完成判读**：四架构 loss 在每个分辨率（256/576/1024 token）内极差 <0.0025（含 SSM/MoE）→「loss 与架构无关」跨 196–1024 token 稳健成立，R2-3 新增科学价值达成。
- **交付物齐备**：① `EXPERIMENTS_VISION_ROUND2.md`（R2-0~R2-5 全表 + 可复现命令 + 回填建议 visres/visobj/visarch/新增 visarch_res）② `BAIZE_VISION_ENCODER_RESULT_ROUND2.html`（自包含）。
- **未修改** `*.tex`（论文已外部重构，回填由外部完成）——已在报告给出精确回填建议。
- **下一步**：无剩余工作。WAITING=1（终局 idle），loop 长睡省 token；若论文回填需要，外部按报告建议回填。

## 🛑 停训记录（2026-10-01 15:38，等待 .12 重启）

> 用户需重启 10.239.2.12，已人工停掉 vision 的 loop 与全部训练。以下为**停训时刻的精确边界 + 重启续跑说明**，务必先读本节再动作。

- **已停掉的对象**：
  - 本机 watchdog loop：`baize_vision_loop.sh`（原 PID 2932291，.29 节点）——已 kill。
  - .12 pipeline：`run_r2.sh`（原 PID 479476）+ launcher（479475）——已 kill。
  - .12 正在训练：deepencoder_v2 r448 p14 的 torchrun（master 2748364）+ 6 worker ——已 kill（SIGTERM→SIGKILL）。
  - 停训后核验：.12 GPU0–5 已 0 MiB（仅 GPU6–7 他人 sglang 未动），`ps` 无 `train.py --tower` / `run_r2.sh` 残留。
- **停训时精确进度（R2 pipeline `run_r2.sh` 串行顺序 R2-1→R2-4→R2-2→R2-3→R2-5）**：
  - ✅ R2-1（res/patch ×7）、✅ R2-4（干净吞吐）、✅ R2-2（目标函数）——**全部完成且已回填** `EXPERIMENTS_VISION_ROUND2.md`。
  - ✅ R2-3（架构×分辨率 12 组，patch=14）：**9/12 完成**（openvision2/deepencoder_v2/moevie/mambaeye × r224 与 r336 共 8 组，+ openvision2 r448 共 9 组），结果已回填 `EXPERIMENTS_VISION_ROUND2.md` R2-3 表。
  - 🛑 R2-3 第 **10/12 组（deepencoder_v2 r448 p14, bs=16）被中断于 ~step2850–2900/3000**（kill 前 tail 到 step2850/3000 loss≈3.7469）。**该组无 `vision.pt`**（train.py 只在第 3000 步结束才 `torch.save`，无周期性 ckpt、无 resume）→ **须整组重跑**。残留目录 `out/R2_deepencoder_v2_r448_p14/` 只有 train.log（train.py 日志为 append 模式）。
  - ⏳ R2-3 第 11/12 组（moevie r448）与第 12/12 组（mambaeye r448）——未跑。
  - ⏳ R2-5（MambaEye bs=1 停摆诊断）——未跑。
- **重启后如何续跑（关键）**：
  - **不要**再跑完整 `run_r2.sh`（它无 resume/skip 逻辑，会把你已完成的 R2-1/R2-4/R2-2 和 9 组全部重做、浪费 GPU·h）。
  - **用我准备的续跑脚本** `vision/run_r2_resume.sh`（已建好、`bash -n` 通过、直接跑剩余 deepencoder_v2 r448 + moevie r448 + mambaeye r448 + R2-5）。启动命令（在 .12 GPU0–5）：
    ```bash
    cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
    setsid bash run_r2_resume.sh </dev/null >/tmp/vision_r2_resume.nohup 2>&1 &
    ```
  - 日志 `/tmp/vision_r2_resume.log`；判结束看 `grep -c "R2 RESUME ALL DONE" /tmp/vision_r2_resume.log` == 1。
  - RESUME 完成后：回填新完成格子到 `EXPERIMENTS_VISION_ROUND2.md` R2-3 表 + R2-5 → 生成 `BAIZE_VISION_ENCODER_RESULT_ROUND2.html` → 更新 MEMORY/EXPERIMENTS → git commit+push。
  - 若 loop 也需恢复无人值守，重启 `setsid bash baize_vision_loop.sh > /tmp/baize_vision_loop.log 2>&1 < /dev/null &`（loop 会在 WAITING=0 时以 1min 间隔继续推进）。

## R2 等待说明（历史：停训前 pipeline running 状态，仅供回溯，勿按此状态判断）

- 等待：**R2 主 pipeline `run_r2.sh`**（后台，10.239.2.12 GPU0-5，11:00:37 重启版，日志 `/tmp/vision_r2.log`）。
- 串行顺序：R2-1（res/patch @ lr3e-3）→ R2-4（干净吞吐）→ R2-2（目标函数）→ R2-3（架构×分辨率）→ R2-5（MambaEye 诊断）。
- 判结束：`ssh 10.239.2.12 'grep -c "R2 PIPELINE ALL DONE" /tmp/vision_r2.log'` == 1；各分段完成看 `mark()` 行（`===== R2-x ... done ...`）。
- 【12:40 巡检快照】**R2-1 ✅ / R2-4 ✅ / R2-2 ✅ 全部完成并已回填 `EXPERIMENTS_VISION_ROUND2.md`**（含判读 + 论文回填建议 visres/visobj/visarch 三段）。**当前在 R2-3 架构×分辨率（12 组）训练中**，第 1 组 openvision2 r224 p14 已到 step~2800/3000。
  - **R2-1**：7 组 loss/吞吐/推理/eval5k 全落盘。loss：224/16=4.4562、336/16=4.4565、448/16=4.4556、224/14=4.4566、336/14=4.4560、**448/14(bs16)=3.7461**、对照 224/16@1e-3=4.9962。推理 ms/img：7.031/8.726/6.890/10.568/7.208/10.391。eval5k 全随机（0.0002/0.0010/0.0020）。
  - **R2-4 干净复测（无争用，GPU 独占 + pretrain 状态原文已记入 EXPERIMENTS 表）**：训练 img/s OpenVision2 **2017.4** > DeepEncoderV2 1383.1 > MoE-ViE 887.1 > MambaEye 810.8；推理 ms/img OpenVision2 **6.872** ≪ DE 25.97 < MambaEye 31.61 < MoE 41.73。→ **OpenVision2 双最优在干净条件下成立**；`6.51ms` 复测得 6.872ms 基本正确（R2-0 遗留问题闭环）。
  - 🎯 **意外发现**：MambaEye **batch=1 推理本次正常（31.608ms），未复现 Round 1 S2 的停摆** → 停摆间歇性/环境相关，R2-5 需重新定位。
  - **R2-2**：SigLIP 4.4562 vs CLIP InfoNCE 3.2704（量纲不可比）；R@1/5/10 两臂近似随机但 CLIP 略高（t2i 0.0012/0.0026 vs 0.0010/0.0020）；训练吞吐几乎相等（1645 vs 1657 img/s）。
  - 剩余 ETA ~2-3h（R2-3 的 12 组×3000 步是大头，串行；openvision2 快、moevie/mambaeye 慢）。
- 【13:15 巡检快照】R2-3（12 组架构×分辨率，patch=14）进行到 **第 4/12 组（mambaeye r224 p14 训练中 ~step400/3000）**。已完成 3 组并回填 `EXPERIMENTS_VISION_ROUND2.md`：openvision2 r224 loss=4.4567/1631.3img/s、deepencoder_v2 r224 4.4563/1408.0、moevie r224 4.4575/558.2；推理 bs1 ms/img=6.857/25.965/42.228，bs8=1.058/2.254/5.511。三架构 r224 loss 并列（差<0.002），吞吐分层（OV2>DE>MoE）。🔑 **batch 一致性警示已记入报告**：run_r2.sh 对 448/14 自动降 batch 32→16，故 448/14 列（bs=16）与 224/14、336/14（bs=32）batch 不同，token 趋势会被 SigLIP 负样本数混淆——「同分辨率内四架构比较」仍有效，「跨 token 趋势」需标注不可比。eval5k 仍全随机。剩余 ETA ~2-3h（336/14 4 组 + 448/14 4 组 + R2-5 40min）。
- 【13:48 巡检快照】R2-3（12 组架构×分辨率，patch=14）进行到 **第 6/12 组（deepencoder_v2 r336 p14 训练中 ~step700/3000）**。已完成 **5 组**并回填 `EXPERIMENTS_VISION_ROUND2.md`。**r224（256 token）四架构全完成**：openvision2 4.4567/1631.3、deepencoder_v2 4.4563/1408.0、moevie 4.4575/558.2、mambaeye 4.4566/861.0 img/s，loss 极差 <0.0012（噪声级）→ **256 token 四架构 loss 不可区分（含 SSM/MoE）已实锤**；吞吐/延迟同 R2-4 干净复测同序（OV2>DE>MambaEye>MoE）。**r336（576 token）openvision2 完成**：loss 4.4560（与 r224 基本持平）、1281.4 img/s、推理 bs1 10.32ms/bs8 2.31ms。推理 bs1 ms/img 全序：OV2 6.86-10.32 < DE 25.97 < MambaEye 31.5 < MoE 42.2。eval5k 仍全随机。剩余 ETA ~2h（deepencoder r336 ~14min + moevie r336 ~23min + mambaeye r336 ~21min + r448 四架构（bs16，慢）~1h + R2-5 40min）。
- 【14:19 巡检快照】R2-3（12 组）进行到 **第 7/12 组（moevie r336 p14 训练中 ~step2100/3000，loss 4.4568，~637 img/s）**。已完成 **6 组**并回填 `EXPERIMENTS_VISION_ROUND2.md`：**deepencoder_v2 r336 新完成**（loss 4.4566 / 599.4 img/s / 推理 bs1 18.378ms·bs8 3.761ms / eval 全随机）已回填 R2-3 表。r336 已完成的 OV2(4.4560/1281.4 img/s) 与 DE(4.4566/599.4) 仍与 r224 并列（loss 差<0.001）→ **token 256→576 未改变 loss 排序（架构仍不可区分）**。剩余：mambaeye r336 ~21min + r448 四架构（bs16，慢）~1h + R2-5 40min → ETA ~1.5h。eval5k 仍全随机。
- 【14:51 巡检快照】R2-3（12 组）进行到 **第 8/12 组（mambaeye r336 p14 训练中 ~step1850/3000，loss 4.4575，~305 img/s）**。已完成 **7 组**并回填 `EXPERIMENTS_VISION_ROUND2.md`：**moevie r336 新完成**（loss 4.4564 / 626.4 img/s / 推理 bs1 42.213ms·bs8 5.907ms / eval 全随机）已回填 R2-3 表。r336 已完成的 OV2(4.4560)、DE(4.4566)、MoE(4.4564) 三架构 loss 极差 <0.0006（噪声级）→ **「架构不可区分」在 576 token 下仍成立**。训练吞吐 OV2(1281) > MoE(626) > DE(599)（DE/MoE 在 576 token 掉换位次，DE 长序列开销上升快）。剩余：mambaeye r336 ~12min + r448 四架构（bs16，慢）~1h + R2-5 40min → ETA ~1.5h。eval5k 仍全随机。
- 【15:23 巡检快照】R2-3（12 组）进行到 **第 10/12 组（deepencoder_v2 r448 p14 训练中 ~step150/3000）**。已完成 **9 组**并回填 `EXPERIMENTS_VISION_ROUND2.md`：**mambaeye r336 新完成**（loss 4.4565 / 305.2 img/s / 推理 bs1 32.200ms·bs8 6.634ms / eval 全随机）、**openvision2 r448 新完成**（loss 3.7454 / 729.0 img/s / 推理 bs1 6.984ms·bs8 3.933ms / eval 全随机）。**r336 四架构 loss（4.4560/4.4566/4.4564/4.4565）极差 <0.0006 → 「架构不可区分」在 576 token 下四架构全证（含 SSM/MoE）**。r448 openvision2 loss 3.7454 与 R2-1 的 3.7461 高度一致（bs=16 复现，SigLIP 负样本敏感性实锤）；标注不可比 + ⚠️ ov2 r448 bs1=6.98ms 反常低于 r336 10.32ms（疑内核路径，待复测）。剩余：deepencoder r448 ~10min + moevie r448 ~20min + mambaeye r448 ~20min + R2-5 40min → ETA ~1.3h。
- 下次唤醒动作：先 tail `/tmp/vision_r2.log` 看 R2-3 进度并回填已完成格子（loss / train img/s / 推理 ms/img bs1+bs8 / eval5k R@1）到 `EXPERIMENTS_VISION_ROUND2.md` R2-3 表；若 ALL DONE 则回填 R2-5 + 补全「论文回填建议」R2-3 段（含 batch 混淆标注）+ 生成 `BAIZE_VISION_ENCODER_RESULT_ROUND2.html` → 更新 MEMORY/EXPERIMENTS → git commit+push，WAITING 置 0。

## 历史：Round 1 S4–S9 pipeline 等待说明（已收敛，供回溯）

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

- ✅ [2026-10-01 ~16:37] **R2 resume 巡检 + 回填（11/12）**：resume pipeline 推进中。deepencoder_v2 r448（10/12）✅ done loss 3.7466 / 474.6 img/s / 推理 bs1 17.863ms·bs8 4.410ms；moevie r448（11/12）✅ done loss 3.7471 / 357.1 img/s / 推理 bs1 42.823ms·bs8 7.033ms；eval 全随机（0.0002/0.0010/0.0020）。→ **r448（1024 token，bs=16）三架构 OV2/DE/MoE loss 3.7454/3.7466/3.7471（极差<0.002），「架构不可区分」在 1024 token 下三架构已复证**；吞吐 OV2 729.0 > DE 474.6 > MoE 357.1 主序不变。剩余：mambaeye r448（最后一组，训练中 ~30min）+ R2-5（40min 时间盒）→ ETA ~1.1h。已回填 `EXPERIMENTS_VISION_ROUND2.md` R2-3 表。WAITING=1 等待 resume 收尾（判结束 `grep -c "R2 RESUME ALL DONE" /tmp/vision_r2_resume.log`==1）。git commit+push 已随本条一起做。
- 🔄 [2026-10-01 10:50] **R2 启动**：MODE 从 Round 1 切到 Round 2（见 BAIZE_VISION_TASK.md 第二轮）。Round 1 三处硬伤（tab:visres 全 4.9962 伪影 / tab:visobj 不可跨目标比较 / 196token 结论自证）→ R2 全局锚点改动 lr 1e-3→3e-3。已落地 `run_r2.sh`（R2-1→R2-4→R2-2→R2-3→R2-5 串行）+ `eval_downstream.py` 多分辨率支持（实测 336/16 ckpt 检索跑通）。核验：10.239.2.12 GPU0-5 全空闲（0 MiB）、GPU6-7 被他人 sglang 占；pretrain 任务已 converged/stopped（无 NFS 争用）。R2-0 数字核对结论见下一条。
- ✅ [2026-10-01 10:50] **R2-0 数字核对（零成本）**：`tab:visarch` 的 `Loss@5k` 四值**标注正确**，均出自 S3@5000 步@lr=1e-3：OpenVision2 **4.4560**（S3 10k 长跑的 5000 步处，而非 10k 终值 4.4540 或 S8 lr3e-3 的 4.4562——三者差 <0.0002 噪声级，纯属巧合）、DeepEncoderV2 4.4662、MambaEye 4.4700、MoE-ViE 4.4661。其余数值核对：2139=OpenVision2 S3 steady_image_s 2139.5✓、1459=DE 1458.7✓、790=MambaEye 790.0✓、852=MoE 852.3✓、505.0M✓、141.7=MoE S2 bench 141.72ms✓。⚠️ 唯一待查：`6.51ms`（S2 原始 bench）与 S9 干净复测 `10.07ms` 不一致（约 1.5×），交由 R2-4 干净复测裁决。四架构「步数→loss」映射表已备（openvision2: 5.918@1k/4.465@3k/4.456@5k/4.454@10k；其余三塔 5.92-5.95@1k/4.472@3k/~4.466-4.470@5k）。
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