# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

> 🆕 **2026-10-18 17:2x 更正（#550 又是误判 + 其 resume 落成 .12 重复训练已被运维杀掉）**：#550(17:02)「训练死亡→resume from step_8000」是**第二起误判**（同 #548）。实录：.29 主 run **PID 2597555**（`pt_elastic`，10-17 08:44:02 起 etimes≈32.6h，持 29815 端口）从未死，8×GPU 97-100%/51763MiB，`/tmp/...train.log` step 9790→9830/19980（49.2%）loss1.3174 lr1.54e-4 0 error；**0 步丢失**。#550 的 resume PID3698325 并非「不存在」，而是**落成 .12 的重复训练**（.29 卡满），与主 run 同写共享 NFS 输出目录=污染风险；**17:17 运维 ops134 已杀掉**（.12 卡释放供 ArmC）。输出目录完好（仅 step_2000/4000/6000/8000+verify_save_20，无重复写入 ckpt）。→ **无需/不重启/不 resume**（16:4x 正确）。下一 ckpt@step_10000（save_interval=2000，~17:5x）。

## 当前状态
- STAGE: **🟢 Xmodel-2.5 80B decay v2 健康运行中 @.29**（22:06 step11280/19980=56.4%, loss1.2671, lr1.10e-4, tok/s298.8K, elapsed2242.2min；0 error）。torchrun master PID**2597555**（10-17 08:44:02 起，持 29815 端口）+ 8 workers（@.29）。✅ **step_10000 ckpt 已落盘**（17:52, 2.7GB 完好）。本轮 #562 在 **.12**（NFS 日志只读验证）。下一 ckpt@step_12000（save_interval=2000，~10-19 00:3x）。
  - PHASE: **decay80b_v2_RUNNING** — 80B decay v2 主 run 持续运行（step 11280/19980=56.4%, loss1.2671, lr1.10e-4）。save_interval=2000 ⇒ 下一 ckpt@step_12000（~10-19 00:3x）；step_10000 已于 17:52 落盘完好。ETA(19980-11280)=8700步×11.9s≈28.8h→10-20 02:5x。脚本已备 RESUME_DIR/--resume（16:2x）+ 日志写 /tmp（16:4x）。
  - 轮询状态：**#562（22:07, 在.12=whag0pgpuap12, NFS 日志只读, 零GPU）**：**✅ 主 run 健康，勿 resume**。本轮在 .12 无法直查 .29 进程（pgrep torchrun 无果=.12 本地；nvidia-smi 7×100%+1×0%/50559MiB=vision armC aimv2_openclip, 非本线）→ 改用共享 NFS `$OUTPUT_DIR/train_log.txt`（.29 实时写入）验证：mtime 22:06=live，tail step11280/19980(**56.4%**) loss1.2671 lr1.10e-4 tok/s298.8K elapsed2242.2min，+10步/2min=稳态11.9s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=**0 命中**✅。stale `baize_xmodel25_decay_v2_train.log`(mtime10-17 10:45)=.12旧killed run, 按16:4x不作判据。ckpt step_2000/4000/6000/8000/10000齐, step_10000(17:52)model.safetensors 2.7GB完好；下一 ckpt@step_12000（~10-19 00:3x）。→ 按 16:4x 零写训练侧。📦 体积：TASK18.5KB / MEMORY~30.2KB（归档 0KB）。
  - [22:07] #562 🩺 v2 巡检 + 心跳（在**.12**=whag0pgpuap12, NFS 日志只读, 零GPU）：① 训练核验：在 .12 无法直查 .29 进程（pgrep torchrun 无果、nvidia-smi 见 vision armC 7×100%+1×0%/50559MiB）→ 改用共享 NFS `$OUTPUT_DIR/train_log.txt`（.29 实时写）验证：mtime 22:06=live，tail step11280/19980(**56.4%**) loss1.2671 lr1.10e-4 tok/s298.8K elapsed2242.2min，+10步/2min=稳态11.9s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=**0**✅。stale `..._v2_train.log`(mtime10-17 10:45)=.12旧killed run，按16:4x不作判据。② ckpt：step_2000/4000/6000/8000/10000齐，step_10000(17:52)model.safetensors 2.7GB完好；下一 ckpt@step_12000（~10-19 00:3x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ git：fetch OK（默认503→带 proxy=http://172.19.92.25:13128 OK），本地=origin/main=e547956ac 无 ahead/behind。⑤ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.5KB / MEMORY~30.2KB（归档 0KB）。
  - [21:54] #561 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes 1-13:10)持29815端口 + 8 workers(2605722-29)；8×GPU 100% util/51763MiB；/tmp/baize_xmodel25_decay_v2_train.log 增长 step11210/19980(**56.1%**) loss1.2342 lr1.12e-4 tok/s298.8K elapsed2228.3min；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL=9（启动期 pynvml FutureWarning）✅。② ckpt：step_2000/4000/6000/8000/10000+verify_save_20 齐，step_10000(17:52)完好；下一 ckpt@step_12000（~10-19 00:3x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ git：默认 fetch 报 503(剥代理)，显式带 proxy=http://172.19.92.25:13128 后 fetch OK，本地与 origin/main 均=329846ac 无 ahead/behind。⑤ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.5KB / MEMORY~29KB（归档 0KB）。
  - [21:15] #560 🩺 v2 巡检 + MEMORY 滚动归档（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers；8×GPU 89-100% util/51763MiB；/tmp/baize_xmodel25_decay_v2_train.log 增长 step11020/19980(**55.1%**) loss1.4148 lr1.16e-4 tok/s298.8K elapsed2190.5min；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL=0 真实命中✅（仅启动期 pynvml FutureWarning）。② ckpt：step_2000/4000/6000/8000/10000+verify_save_20 齐，step_10000(17:52)完好；下一 ckpt@step_12000（~10-19 00:3x）。③ 归档：MEMORY 31.6KB 逼近 32KB → 滚入 #543~#546（14:09-15:20 旧巡检, 均已闭合）原文到 daily-memories/2026-10-18.md，留 1 行指针。④ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。⑤ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 归档。📦 体积：TASK18.1KB / MEMORY~29KB（归档 ~3KB → daily-memories/2026-10-18.md）。
  - [20:51] #559 🩺 v2 巡检 + 心跳（在**.12**=whag0pgpuap12, NFS 日志只读, 零GPU）：① **关键发现**：本轮唤醒在 **.12**（hostname=whag0pgpuap12, IP=10.239.2.12）而非 .29 → `pgrep -af torchrun`/`ps -p 2597555`/`nvidia-smi` 均只能查 .12 本地，不能直查 .29 训练进程。.12 GPU 8×97-100%/50559MiB 被 **vision** armB_aimv2_openclip.py（PID4154295=torch.distributed.run --nproc_per_node=8, 18:05:17 起, out=baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224）占用=正常。② **NFS 日志验证训练活着**：`$OUTPUT_DIR/train_log.txt` 实时增长 step10890@20:49:16→step10900@20:51:15（+10步/2min=稳态 11.9s/step）loss1.2501 lr1.20e-4 tok/s298.8K elapsed2166.7min；`timing_log.txt` 同步 step10899@20:51:03 t_fwd_bwd=391.4ms t_total=11909ms；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL=0 命中✅。/tmp/baize_xmodel25_decay_v2_train.log 在 .12 上 stale（17:17 SIGTERM=被杀的 #550 resume 残留，非判据）。③ ckpt：step_2000/4000/6000/8000/10000+verify_save_20 齐；step_10000(17:52,2.7GB)完好；step_12000 not yet（~10-19 00:3x）。④ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。📦 体积：TASK18.5KB / MEMORY~30KB（归档 0KB）。
  - [20:42] #558 🩺 v2 巡检 + 心跳（在.29=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers；8×GPU 97-100% util/51763MiB；/tmp/baize_xmodel25_decay_v2_train.log 增长 step10850/19980(**54.3%**) loss1.2930 lr1.21e-4 tok/s298.8K elapsed2156.8min；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL=0 真实命中✅（仅启动期 pynvml FutureWarning）。② ckpt：step_2000/4000/6000/8000/10000+verify_save_20 齐，step_10000(17:52)完好；NFS train_log.txt mtime 20:41=live；下一 ckpt@step_12000（~10-19 00:3x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。📦 体积：TASK18.5KB / MEMORY~30KB（归档 0KB）。
  - [20:07] #557 🩺 v2 巡检 + 心跳（在.29=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers；8×GPU 97-100% util/51763MiB；/tmp/baize_xmodel25_decay_v2_train.log 增长 step10680/19980(**53.4%**) loss1.3888 lr1.26e-4 tok/s298.8K elapsed2123.0min；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL=0 真实命中✅（仅 9 条启动期 pynvml FutureWarning）。② ckpt：step_2000/4000/6000/8000/10000+verify_save_20 齐，step_10000(17:52)完好；下一 ckpt@step_12000（~10-19 00:3x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 归档：#539~#542 闭合流水滚入 daily-memories/2026-10-18.md，留 1 行指针。📦 体积：TASK18.1KB / MEMORY28.9KB（归档 ~1.5KB）。
  - [19:33] #556 🩺 v2 巡检 + 心跳（在.29=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers；8×GPU 98-100% util/51763MiB；/tmp/baize_xmodel25_decay_v2_train.log 增长 step10500/19980(**52.5%**) loss1.1760 lr1.31e-4 tok/s298.8K elapsed2087.3min；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL=0 命中✅（last 200 lines）。② ckpt：step_2000/4000/6000/8000/10000+verify_save_20 齐，step_10000(17:52)完好；下一 ckpt@step_12000。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~29.6KB（归档 0KB）。
  - [19:00] #555 🩺 v2 巡检 + 心跳（在.29=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers；8×GPU 97-100% util/51763MiB；/tmp/baize_xmodel25_decay_v2_train.log 增长 step10340/19980(**51.7%**) loss1.2905 lr1.36e-4 tok/s298.8K elapsed2055.5min；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL=0 命中✅。② ckpt：step_2000/4000/6000/8000/10000+verify_save_20 齐，step_10000(17:52)完好；下一 ckpt@step_12000。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY28.9KB（归档 0KB）。
  - [18:25] #554 🩺 v2 巡检 + MEMORY 滚动归档（在.29=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes 1-09:41)持29815端口 + 8 workers；8×GPU 7×100%+1×98% util/51763MiB；/tmp/baize_xmodel25_decay_v2_train.log 增长 step10170/19980(**50.9%**) loss1.2008 lr1.42e-4 tok/s298.8K elapsed2021.8min；grep error/traceback/OOM/CUDA/SIGTERM=0 命中✅。② ckpt：step_2000/4000/6000/8000/10000+verify_save_20 齐，step_10000(17:52)完好；下一 ckpt@step_12000。③ 归档：MEMORY 31.7KB 逼近 32KB 上限 → 滚入 #535~#538（v5 中文HTML/R3降级/数字一致性/溯源补丁, 均已闭合）原文到 daily-memories/2026-10-18.md，留 1 行指针。④ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。⑤ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 归档。📦 体积：TASK18.1KB / MEMORY~30KB（归档 ~2.5KB → daily-memories/2026-10-18.md）。
  - [18:14] #553 🩺 **v2 巡检（在.12经SSH只读查.29）：step 10120/19980=50.6% 健康，step_10000已落盘，勿 resume**（在.12=whag0pgpuap12, SSH→.29 只读, 零GPU）：① **节点澄清**：本轮 hostname=whag0pgpuap12(10.239.2.12)=**.12**，非 .29；前轮 #548-#552 在 .29 本地直查。② **SSH .29 核验**：`ssh 10.239.2.29` OK(whag0pgpuap29)；torchrun master PID2597555(baize_xmodel25_decay_v2.py, --save_interval 2000, 10-17 08:44:02起)存活；.29 nvidia-smi 8×GPU=7×100%+1×98% util/51763MiB(81559总)；/tmp log tail step10120/19980(**50.6%**) loss1.4229 lr1.44e-4 tok/s298.8K elapsed2011.9min（step 10110→10120 +10步/2min 稳态增长）；NFS train_log.txt mtime 18:16:24=live。③ **ckpt**：step_10000/model.safetensors 2.7GB(17:52:22落盘)完好；下一 ckpt@step_12000。④ **.12 本地勿误判**：.12 8 卡现跑 **vision ArmC**(PID4154295 torch.distributed.run→armB_aimv2_openclip.py, 18:05:17起, OUT=armC_20261018_*, step60/57250)——vision 线的，🚫不碰；.12 /tmp/baize_xmodel25_decay_v2_train.log 是 #550 误判 resume(17:01起,step8000→8074,17:17 rc=137被ops134杀)残留，**非 .29 实时日志**。⑤ **动作**：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。⑥ 红线遵守：未碰 .29 训练/loop/ckpt/未清 /tmp/未改脚本/未碰 .12 vision ArmC；仅 SSH 只读 + 心跳。pretrain loop(.12, PID1294448)存活。📦 体积：TASK18.1KB/MEMORY~30.1KB（归档0KB）。
  - [17:52] #552 🩺 **v2 巡检：step 过 50% 关口，训练健康勿 resume**（在.29=whag0pgpuap29, 本地直查, 仅只读零GPU）：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers(2605722-29, ppid=2597555)；8×GPU 97-100%util/51763MiB(81559MiB 总)；/tmp log 增长 step9990/19980(**50.0%**) loss1.2861 lr1.48e-4 tok/s298.8K elapsed1986min；grep error/traceback/OOM/CUDA/SIGTERM/RESUME=0 命中✅。输出目录 train_log.txt mtime 17:50=live（区别于 10-17 10:45 的旧 NFS baize_...train.log）；ckpt dirs=step_2000/4000/6000/8000+verify_save_20，**step_10000 17:52 尚未落盘**（save_interval=2000，即将）。→ 按 16:4x「训练活着⇒不重启/不resume」零写训练侧。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。📦 体积：TASK18.1KB/MEMORY~29.9KB（归档0KB）。
  - [17:19] #551 ✅ **纠偏：#550 第二起误判 + 其 resume 落成 .12 重复训练已被运维 ops134 杀掉**（在.29=whag0pgpuap29, 本地直查, 零GPU）：① **核验 .29**：torchrun master PID2597555(pt_elastic, 10-17 08:44:02起, etimes117324s≈32.6h)持29815端口(fd=10)；8×GPU 97-100%util/51763MiB；`/tmp/baize_xmodel25_decay_v2_train.log` 增长 step9790→9830/19980(49.2%) loss1.3174 lr1.54e-4 tok/s298.8K elapsed1954min **0 error**。② **纠偏 #550 误判**：主 run 从未死、0 步丢失（9630→9830 无缝）；#550 所称「step_8000→9630 丢1630步/save_interval改500/下ckpt@step8500」均不符——运行进程仍 `--save_interval 2000`（下 ckpt@step10000）。③ **真凶**：#550 的 resume PID3698325 **确实启动过，但落成 .12 重复训练**（.29 卡满，复用共享 NFS 脚本/ckpt → 与 .29 主 run 同写 `xmodel25_baize_80b_decay/` 输出目录=重复训练+ckpt污染风险）。**17:17 运维 ops134「kill duplicate pretrain on .12 to free GPUs for ArmC」已杀掉 3698325 + 3737xxx workers**（outbox DONE 134，.12 卡 0%/4MiB）。④ **无污染核验**：输出目录仅 step_2000/4000/6000/8000 + verify_save_20，无 .12 重复训练写入 ckpt（被杀前不足 save_interval=500 门槛）；step_8000/model.safetensors 2.7GB(10-18 11:15) 完好；NFS train.log mtime 10-17 10:45=.12 旧 run 残留（再次佐证不能作判据）。⑤ **动作**：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧（不kill/resume/改脚本），仅核验+纠偏+心跳。⑥ 红线遵守：未 kill 健康训练/loop/ckpt/未清/tmp/未改脚本；pretrain loop PID1294147 存活；ops 中继 .last_run_id=134。📦 体积：TASK18.5KB/MEMORY~29KB（归档0KB）。
  - [17:02] #550 ✅ **训练死亡→已 resume from step_8000**（在.29=whag0pgpuap29, 本地直查, 零GPU）：① **死亡确认**（16:55:48 查）：8×GPU 0%/4MiB、无 torchrun、`/tmp/baize_xmodel25_decay_v2_train.log` 文件不存在 → 16:4x 判活规则三条件全满足（torchrun 消失+GPU 空+/tmp log 停止）。死因不明（无 dmesg 权限、/tmp 日志已丢失无法查 traceback）。死亡时间窗口：16:28(RUN_ID125 alive,step~9630)→16:55(dead)。② **自行 resume**（按 16:2x 长期授权"训练挂了唤醒时看到了立刻修，不需要运维许可"）：改 `baize_xmodel25_decay_v2.sh`——加 `RESUME_DIR="${RESUME_DIR:-}"/RESUME_ARG/--resume $RESUME_ARG` 支持行 + 日志 redirect 从 NFS `$OUTPUT_DIR/...log` 改回 `/tmp/...log`（16:4x 判活规则兼容；NFS 日志不可靠=`.12` 旧 run SIGTERM 覆盖）；启动 `RESUME_DIR=/nas_train/.../step_8000 setsid bash baize_xmodel25_decay_v2.sh > /tmp/..._resume.log 2>&1 < /dev/null &`。③ **验证**（17:02:47）：torchrun PID3698325 + 8 workers(3698840+) 存活；8×GPU 100% util/51761MiB；train_log `/tmp/baize_xmodel25_decay_v2_train.log` 出现 `RESUME: loading from .../step_8000, start_step=8000` + `[step 8000/19980] loss=1.2808 lr=2.38e-04`；0 real error（仅 pynvml FutureWarning）。④ 损失评估：step_8000→死亡点(~9630)≈1630 步丢失（save_interval 已从 2000 改 500，下次 ckpt@step_8500）；optimizer 状态未恢复=已知小 transient。ETA(19980-8000)=11980步×11.9s≈39.6h→10-20 08:4x。⑤ 红线遵守：🚫 未 kill 健康训练（训练已死才 resume）/未 kill loop/未碰 ckpt/未清 /tmp/未改 ops_relay.sh；✅ 仅改 `baize_xmodel25_decay_v2.sh`（加 resume 支持+日志路径）。pretrain loop PID1294448 存活。ops 中继 PID2663131 存活, .last_run_id=130。
  - [16:30] #549 ✅ **纠偏：#548「训练死亡」系误报，v2 健康运行**（在.29=whag0pgpuap29, 本地直查, 零GPU）：① **纠偏**：torchrun PID2597555 自 Oct17 08:44:02 起 **31.7h 连续存活**（ps lstart 佐证，从未重启）；train_log 15:53:22 step9400→16:29:07 step9580 **全程无缝 2min/10步**，grep resume/restart/error/traceback/OOM/CUDA/SIGTERM=0 命中；nvidia-smi 8×GPU 100% util、compute-apps=8×PIDs2605722-29(ppid=2597555) 各51754MiB。**结论：#548(15:55) 的"15:53:47 GPU全空闲/无torchrun"与事实矛盾→误报/观测抖动，训练从未死**。② **不 resume**：16:2x 令前置（8卡空/无torchrun）不成立；强行 resume=杀健康31.7h训练+回退step_8000丢1580步→违反"不杀健康训练"红线，**只记录不重启**。③ P0 ops 中继：PID1972249 存活、.last_run_id=**125**（123→125 前进），健康。④ 下一ckpt@step10000(~17:4x)；ETA(19980-9580)=10400步×11.9s≈34.4h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。
  - [15:55] #548 🚨 **80B decay v2 训练死亡 + P0 中继修复闭环**（在.29=whag0pgpuap29, 本地直查, 零GPU）：① **P0 中继修复**：执行 `/tmp/fix_relay_29_1018.sh`（写文件再执行避免 pkill 自匹配），kill 旧 relay PID1146484 → 启新 PID**2663131**(ppid=1 守护, 15:49:17起, repo=/nas_train/.../super_intelligence_2035), .last_run_id=**123**, outbox RUN_ID123(12:15:07 host=.29 exit=0)回执✅ → **P0 已闭环**。⚠️ 脚本用 `/nasdata/...` 路径 cd 失败(实际仓库在 `/nas_train/...`), 但 `ops_relay.sh` 内部硬编码正确路径, 中继正常启动。② **🚨 训练死亡**：15:53:22 train_log 最后一条 step9400/19980(47.0%) loss1.3298 lr1.70e-4 tok/s298.8K elapsed1868.8min(**完全正常**)；15:53:47 确认：GPU 8卡全空闲(0%util/4MiB)、无 torchrun 进程、train_log 5s 不增长(diff=0)、timing_log 最后 step9399@15:53:10。日志 grep 无 error/traceback/OOM/CUDA/signal。无 root 权限查 journalctl/syslog/kern.log。死因=**不明, 疑似外部 SIGTERM/SIGKILL**。最新 ckpt=**step_8000**(11:15, 含 model.safetensors), save_interval=2000 → step8001-9400(**1400 步损失**)。③ 10-18② 交付物核验：HTML 存在于 `run/reports/`(22KB) + `reports/`(29.3KB), `PLAN_V5_STABLE_1.5T.md`(15.3KB) + `PLAN_V5_DATA_PREREQ.md`(10.1KB) 均 committed(5 个 `pretrain plan-v5:` 提交)。④ 红线遵守：🚫 未重启训练/未 kill loop/未改 ops_relay.sh 本体/未清 /tmp/未碰 ckpt；仅只读+中继重启。pretrain loop PID1294448 存活。📦 体积：TASK30.3KB / MEMORY~24KB（归档 0KB → ARCHIVE_OPERATOR_PRETRAIN.md）。
  > 📦 **[已归档] #515~#518 流水（2026-10-17 23:48 ~ 2026-10-18 01:04, 🩺 v2 巡检 step4540→4910 + P0中继只读核验）→ daily-memories/2026-10-18.md；结论：step4540/4570/4740/4910 健康 loss1.29~1.52 tok/s298.4K 0 error, 中继2706247健康, ckpt step_2000+4000 已保存, ETA~50h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #519~#521 流水（2026-10-18 01:04~02:12, P0中继误报与纠偏）→ daily-memories/2026-10-18.md；结论：#519误报"2706247已死"重启1048010→#520纠偏2706247存活(22:07起)为唯一健康→#521(.12视角)1048010亦健康(两机各一中继互不冲突)；v2 step5100/5260 健康 0 error。需要时再读。**
  > 📦 **[已归档] #522~#534 流水（2026-10-18 02:19~08:12, 🩺 v2 常规巡检 step5290→7079 + P0 中继只读核验）→ daily-memories/2026-10-18.md；**结论**：v2 全程健康 0error、ckpt step_2000/4000/6000 已存、P0 中继两机闭环、ETA~10-20 02:5x。需要时再读。**
> 📦 **[已归档] #535~#538 流水（2026-10-18 08:46~11:17, v5 中文HTML/R3降级/数字一致性补丁/溯源补丁）→ daily-memories/2026-10-18.md；**结论**：v5 三交付物（中文HTML+PLAN_V5_STABLE_1.5T.md+PLAN_V5_DATA_PREREQ.md）全部落盘并提交（5 个 pretrain plan-v5:），10-18② 令闭合。需要时再读。**
  > 📦 **[已归档] #539~#542 流水（2026-10-18 11:40~13:37, v5 三交付物终验/复验 + P0 ops中继核验闭合）→ daily-memories/2026-10-18.md；**结论**：v5 三交付物（HTML+PLAN_V5_STABLE_1.5T.md+PLAN_V5_DATA_PREREQ.md）全部落盘并 committed（5 个 pretrain plan-v5:），P0 中继 .last_run_id=123 回执闭环。需要时再读。**
> 📦 **[已归档] #543~#546 流水（2026-10-18 14:09~15:20, 🩺 v2 巡检 + P0 中继/v5 三交付物核验）→ daily-memories/2026-10-18.md；**结论**：v2 全程健康 0error、P0 中继闭环+无新命令、v5 三交付物 committed、ckpt step_2000/4000/6000/8000 已存。需要时再读。**

> 📦 **[已归档] #472~#514 流水（2026-10-17 02:16 ~ 23:20, 🩺 v2 监控 step280→4400 + 🔧_orig_mod修复重启续跑 + 🚨P0 中继恢复 relay-fix）→ daily-memories/2026-10-17.md；结论：v2 全程健康 0error、step_2000/4000 ckpt 已存、_orig_mod 修复 verify_save@step20 通过、ops 中继 PID2706247(22:07)已恢复(RUN_ID118-121 exit=0/.last_run_id=121 无新命令)、两项 P0 运维令均已闭环。需要时再读。**

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
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
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
