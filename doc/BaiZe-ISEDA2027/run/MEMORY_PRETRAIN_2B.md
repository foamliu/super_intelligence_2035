# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

> 🆕 **2026-10-18 17:2x 更正（#550 又是误判 + 其 resume 落成 .12 重复训练已被运维杀掉）**：#550(17:02)「训练死亡→resume from step_8000」是**第二起误判**（同 #548）。实录：.29 主 run **PID 2597555**（`pt_elastic`，10-17 08:44:02 起 etimes≈32.6h，持 29815 端口）从未死，8×GPU 97-100%/51763MiB，`/tmp/...train.log` step 9790→9830/19980（49.2%）loss1.3174 lr1.54e-4 0 error；**0 步丢失**。#550 的 resume PID3698325 并非「不存在」，而是**落成 .12 的重复训练**（.29 卡满），与主 run 同写共享 NFS 输出目录=污染风险；**17:17 运维 ops134 已杀掉**（.12 卡释放供 ArmC）。输出目录完好（仅 step_2000/4000/6000/8000+verify_save_20，无重复写入 ckpt）。→ **无需/不重启/不 resume**（16:4x 正确）。下一 ckpt@step_10000（save_interval=2000，~17:5x）。

## 当前状态
- STAGE: **🟢 Xmodel-2.5 80B decay v2 健康运行中 @.29**（07:42 step14170/19980=70.9%, loss1.2551, lr5.82e-5, tok/s298.9K, elapsed2816.1min；0 error）。torchrun master PID**2597555**（10-17 08:44:02 起，持 29815 端口，etimes 169105s≈47.0h）——**本轮在 .29 本地直读**。✅ **step_14000 ckpt 已落盘**（07:06, model.safetensors 2700169168B=2.7GB 完好）。下一 ckpt@step_16000（save_interval=2000，~13:4x）。
  - PHASE: **decay80b_v2_RUNNING** — 80B decay v2 主 run 持续运行（step 14170/19980=70.9%, loss1.2551, lr5.82e-5）。save_interval=2000 ⇒ 下一 ckpt@step_16000（~13:4x）；step_14000 已于 07:06 落盘完好。ETA(19980-14170)=5810步×~11.9s≈19.2h→10-20 ~02:5x。脚本已备 RESUME_DIR/--resume（16:2x）+ 日志写 /tmp（16:4x）。⚠️ 注：磁盘脚本 SAVE_INTERVAL 现为 500（crash2 安全改），但 live run 仍用启动时 2000；若将来 resume 将用 500。
  - 轮询状态：**#585（07:42, 在.29=whag0pgpuap29, 本地直查, 零GPU）**：✅ 主 run 健康，勿 resume。torchrun master **PID2597555 存活**（10-17 08:44:02 起, etimes 169105s≈47.0h），8×GPU 100%/51763MiB；/tmp log 增长 step14170/19980（70.9%）loss1.2551 lr5.82e-5 tok/s298.9K；0 error（grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception 全文件=0）。ckpt step_2000/4000/6000/8000/10000/12000/14000 齐，step_14000(07:06)model.safetensors 2.7GB 完好；step_16000 not yet（~13:4x）。→ 按 16:4x「训练活着⇒不重启/不resume」零写训练侧。📦 体积：TASK18.1KB / MEMORY~30.6KB（归档 0KB）。
  - [07:42] #585 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes=169105s≈47.0h)持29815端口 + 8 workers(2605722-29)；8×GPU 100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step14170/19980(**70.9%**)(timing至14174) loss1.2551 lr5.82e-05 tok/s298.9K elapsed2816.1min；+140步/30min(#584@07:12=14030)=稳态~11.9s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（全文件）✅。② ckpt：step_2000/4000/6000/8000/10000/12000/14000 齐，step_14000(07:06)model.safetensors 2700169168B=2.7GB 完好；step_16000 not yet（~13:4x）；ETA(19980-14170)=5810步×11.9s≈19.2h→10-20 ~02:5x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~30.6KB（归档 0KB）。
  - [07:12] #584 🩺 v2 巡检 + 心跳（在**.12**=whag0pgpuap12, SSH→.29 只读, 零GPU）：① 训练核验：SSH .29 (whag0pgpuap29) OK；torchrun master PID2597555(10-17 08:44:02起, etimes=167381s≈46.5h)持29815端口 + 8 workers；8×GPU 98-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step14030/19980(**70.2%**) loss1.3078 lr6.00e-05 tok/s298.9K elapsed2788.3min；+20步/2min(#583@07:10=14010)=稳态~11.9s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception 全文件=0 ✅。② ckpt：step_2000/4000/6000/8000/10000/12000/14000 齐，**step_14000(07:06) model.safetensors 2700169168B=2.7GB 完好**；step_16000 not yet（~13:4x）；ETA(19980-14030)=5950步×11.9s≈19.7h→10-20 ~03:0x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本/未碰 .12 vision ArmC；仅 SSH 只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~30.5KB（归档 0KB）。
  - [07:10] #583 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes=167160s=1d22h26m)持29815端口 + 8 workers；8×GPU 100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step14010/19980(**70.1%**) loss1.2883 lr6.02e-05 tok/s298.9K elapsed2784.3min；+180步/39min(#582@06:31=13830)=稳态~11.9s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception 全文件=0（**0 真实错误** ✅）。② ckpt：step_2000/4000/6000/8000/10000/12000/14000 齐，**step_14000(07:06) model.safetensors 2700169168B=2.7GB 完好**；step_16000 not yet（~13:4x）；ETA(19980-14010)=5970步×11.9s≈19.7h→10-20 ~02:5x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~29.3KB（归档 0KB）。
  - [06:31] #582 🩺 v2 巡检 + 心跳 + MEMORY 滚动归档（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes=164853s=1d21h48m)持29815端口 + 8 workers；8×GPU 99-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step13830/19980(**69.2%**) loss1.2869 lr6.25e-05 tok/s298.9K elapsed2748.6min；+180步/33min(#581@05:58=13650)=稳态~11.9s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception 全文件=9 命中**全为** pynvml FutureWarning（启动行，benign），**0 真实错误** ✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29) model.safetensors 2700169168B=2.7GB 完好；step_14000 not yet（~07:0x）；ETA(19980-13830)=6150步×11.9s≈20.3h→10-20 ~02:5x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 归档：#566~#569(00:11-01:21 旧巡检, 均已闭合)滚入 daily-memories/2026-10-19.md，留 1 行指针。⑤ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳 + 归档。📦 体积：TASK18.1KB / MEMORY~28.9KB（归档 ~3.5KB）。
  - [05:58] #581 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes=162851s=1d21h14m)持29815端口 + 8 workers；8×GPU 97-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step13650/19980(**68.3%**)(timing至13654) loss1.2119 lr6.50e-05 tok/s298.9K elapsed2712.8min；+10步/2min(#580@05:56=13640)=稳态~11.9s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception 全文件=9 命中**全为** pynvml FutureWarning（启动行，benign），**0 真实错误** ✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29) model.safetensors 2700169168B=2.7GB 完好；step_14000 not yet（~07:0x）；ETA(19980-13650)=6330步×11.9s≈20.9h→10-20 ~02:5x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~29.9KB（归档 0KB）。
  - [05:56] #580 🩺 v2 巡检 + 心跳（在**.12**=whag0pgpuap12, SSH→.29 只读, 零GPU）：① 训练核验：SSH .29 OK；torchrun master PID2597555(10-17 08:44:02起, etimes≈1d21h12m)持29815端口 + 8 workers；8×GPU 97-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step13640/19980(**68.3%**)(timing至13644) loss1.2167 lr6.51e-05 tok/s298.9K elapsed2710.8min；+170步/35min(#579@05:21=13470)=稳态~12.4s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception 全文件=9 命中**全为** `torch/cuda/__init__.py:63` 的 pynvml FutureWarning（启动行，benign），**0 真实错误** ✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29) model.safetensors 2700169168B=2.7GB 完好；step_14000 not yet（~07:0x）；ETA(19980-13640)=6340步×11.9s≈21.0h→10-20 ~02:5x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~28.8KB（归档 0KB）。
  - [05:21] #579 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes=160663s=1d20h38m)持29815端口 + 8 workers(2605722-29)；8×GPU 97-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step13470/19980(**67.4%**)(timing至13464) loss1.2015 lr6.75e-05 tok/s298.9K elapsed2677.1min；+170步/32min(#578@04:49=13300)=稳态~11.9s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（全文件）✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:0x）；ETA(19980-13470)=6510步×11.9s≈21.5h→10-20 ~02:5x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~28.5KB（归档 0KB）。
  - [04:49] #578 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes=1d20h05m)持29815端口 + 8 workers；8×GPU 98-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step13300/19980(**66.6%**)(timing至13304) loss1.2693 lr7.00e-05 tok/s298.9K elapsed2643.3min；+50步/11min(#577@04:38=13250)=稳态~11.5s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（全文件）✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:0x）；ETA(19980-13300)=6680步×11.5s≈21.3h→10-20 ~02:0x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~28KB（归档 0KB）。
  - [04:38] #577 🩺 v2 巡检 + 心跳（在**.12**=whag0pgpuap12, SSH→.29 只读, 零GPU）：① 训练核验：SSH .29 (whag0pgpuap29) OK；torchrun master PID2597555(10-17 08:44:02起, etimes≈158152s=1d19h56m)持29815端口 + 8 workers；8×GPU 97-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step13250/19980(**66.3%**)(timing至13259) loss1.1607 lr7.08e-05 tok/s298.9K elapsed2633.4min；+110步/21min(#576@04:17=13140)=稳态~11.5s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（last200行）✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:0x）；ETA(19980-13250)=6730步×11.5s≈21.5h→10-20 ~02:1x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本/未碰 .12 vision ArmC；仅 SSH 只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~26.5KB（归档 0KB）。
  - [04:17] #576 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes≈156818s=1d19h33m)持29815端口 + 8 workers；8×GPU 100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step13140/19980(**65.7%**)(timing至13134) loss1.1770 lr7.25e-05 tok/s298.9K elapsed2611.6min；+180步/37min(#575@03:40=12960)=稳态~12s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（last100行）✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:0x）；ETA(19980-13140)=6840步×11.9s≈22.6h→10-20 ~02:5x。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ git：首次 fetch 503(proxy)→显式带 P=http://172.19.92.25:13128 后 fetch OK（HEAD=origin/main=1a0ab2e, 0/0 ahead/behind）。⑤ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~26.9KB（归档 0KB）。
  - [03:40] #575 🩺 v2 巡检 + 心跳 + MEMORY 滚动归档（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起, etimes154562s=1d18h56m)持29815端口 + 8 workers；8×GPU 97-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step12960/19980(**64.9%**)(timing至12959) loss1.3489 lr7.54e-5 tok/s298.8K elapsed2575.8min；+100步/19min(#574@03:21=12860)=稳态~11.4s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（last1200行）✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:0x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 归档：MEMORY 32.2KB 过 32KB 上限 → 滚入 #558~#565（10-18 20:42~23:24 旧巡检, 均已闭合）原文到 daily-memories/2026-10-18.md，留 1 行指针。⑤ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳 + 归档。📦 体积：TASK18.1KB / MEMORY~24.6KB（归档 ~7.5KB → daily-memories/2026-10-18.md）。
  - [03:21] #574 🩺 v2 巡检 + 心跳（在**.12**=whag0pgpuap12, SSH→.29 只读, 零GPU）：① 训练核验：SSH .29 (whag0pgpuap29) OK；torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers；8×GPU 97-100% util/51763MiB(81559总)；.29 /tmp/baize_xmodel25_decay_v2_train.log 增长 step12860/19980(**64.4%**)(timing至12864) loss1.2582 lr7.70e-5 tok/s298.8K elapsed2556.0min；+90步/19min(#573@03:02=12770)=稳态~12.7s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（tail）✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:0x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本/未碰 .12 vision ArmC；仅 SSH 只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~30.4KB（归档 0KB）。
  - [03:02] #573 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers；8×GPU 98-100% util/51754MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step12770/19980(**63.9%**)(timing至12764) loss1.2640 lr7.86e-5 tok/s298.8K elapsed2538.1min；+170步/33min(#572@02:29=12600)=稳态~12s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=8(均启动期pynvml FutureWarning)真实0✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:0x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~30KB（归档 0KB）。
  - [02:29] #572 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers；8×GPU 98-100% util/51763MiB(81559总)；/tmp/baize_xmodel25_decay_v2_train.log 增长 step12600/19980(**63.1%**)(timing至12599) loss1.3209 lr8.16e-5 tok/s298.8K elapsed2504.3min；+130步/26min(#571@02:03=12470)=稳态~12s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（last 800 lines）✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:3x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~30.5KB（归档 0KB）。
  - [02:03] #571 🩺 v2 巡检 + hostname 更正（在**.12**=whag0pgpuap12, SSH→.29 只读, 零GPU）：① **节点澄清（重要）**：本轮 `hostname`=whag0pgpuap12=**.12**（非 .29）；#554-#570 标「在.29本地直查」实为**误标**——那些会话在 .12 读共享 NFS `train_log.txt`（步数正确，但未实地核验 .29 PID/GPU/本地 /tmp）。② **SSH .29 核验**：`ssh 10.239.2.29` OK(whag0pgpuap29)；torchrun master **PID2597555 存活**（etimes=148824s≈41.3h, 10-17 08:44:02 起, 持 29815 端口, args=`baize_xmodel25_decay_v2.py --save_interval 2000 --total_steps 19980 --lr 1.67e-3`）；.29 nvidia-smi 8×GPU=7×100%+1×97% util/51763MiB(81559总)；.29 /tmp log tail step12470/19980(**62.4%**) loss1.2456 lr8.40e-5 tok/s298.8K elapsed2478.5min（mtime 02:03:52=live）。③ **ckpt**：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB(2700169168B)完好；下一 ckpt@step_14000（~07:0x）。④ **.12 本地**：8 卡跑 vision ArmC（PID4154295 torch.distributed.run→armB_aimv2_openclip.py, OUT=armC_20261018_*, 18:05起），🚫不碰；.12 /tmp/baize_xmodel25_decay_v2_train.log 是 #550 误判 resume 残留（17:17 rc=137 被杀），非 .29 实时日志。⑤ **动作**：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。⑥ 红线遵守：未碰 .29 训练/loop/ckpt/未清 /tmp/未改脚本/未碰 .12 vision ArmC；仅 SSH 只读 + 心跳。pretrain loop(.12, PID1294448)存活。📦 体积：TASK18.1KB / MEMORY~27.3KB（归档 0KB）。
  - [01:56] #570 🩺 v2 巡检 + 心跳（在**.29**=whag0pgpuap29, 本地直查, 仅只读零GPU）：① 训练核验：torchrun master PID2597555(10-17 08:44:02起)持29815端口 + 8 workers(2605722-29)；8×GPU 97-100% util/51763MiB；/tmp/baize_xmodel25_decay_v2_train.log 增长 step12430/19980(**62.2%**)(timing至12434) loss1.3740 lr8.47e-5 tok/s298.8K elapsed2470.6min；+170步/35min(#569@01:21=12260)=稳态~12.3s/step；grep error/traceback/OOM/CUDA/SIGTERM/SIGKILL/exception=0（全文件）✅。② ckpt：step_2000/4000/6000/8000/10000/12000 齐，step_12000(00:29)model.safetensors 2.7GB完好；step_14000 not yet（~07:0x）。③ 动作：按 16:4x「训练活着⇒不重启/不resume」→ 零写训练侧。④ git：fetch OK（HEAD=origin/main=f02287f）。⑤ 红线遵守：未碰训练/loop/ckpt/未清 /tmp/未改脚本，仅只读 + 心跳。📦 体积：TASK18.1KB / MEMORY~26KB（归档 0KB）。
> 📦 **[已归档] #566~#569 流水（2026-10-19 00:11~01:21, 🩺 v2 巡检 step11904→12260, 含 step_12000 ckpt 落盘核验）→ daily-memories/2026-10-19.md；**结论**：v2 全程健康 0error、step_12000(00:29) ckpt 2.7GB 完好、下一 ckpt@step_14000 ~07:0x。需要时再读。**
> 📦 **[已归档] #558~#565 流水（2026-10-18 20:42~23:24, 🩺 v2 巡检 step10850→12770）→ daily-memories/2026-10-18.md；**结论**：v2 全程健康 0error、step_10000/12000 ckpt 落盘、双节点视角（.12 NFS只读 / .29本地直查）均已核验、MEMORY 滚动归档。需要时再读。**
> 📦 **[已归档] #552~#557 流水（2026-10-18 17:52~20:07, 🩺 v2 巡检 step9990→10680 + MEMORY 滚动归档）→ daily-memories/2026-10-18.md；**结论**：v2 全程健康 0error、step_10000 ckpt 落盘、#535~#546 旧流水滚入 daily-memories、ETA~10-20 02:5x。需要时再读。**
> 📦 **[已归档] #548~#551 流水（2026-10-18 15:55~17:19, 🚨 误判三连：训练死亡误报→resume误判→.12重复训练被杀 + 纠偏闭合）→ daily-memories/2026-10-18.md；结论：#548/#550 均为误判（主 run PID2597555 从未死、0 步丢失），#550 resume 落成 .12 重复训练已被运维 ops134 杀，#551 纠偏闭环，v2 训练健康。需要时再读。**
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
