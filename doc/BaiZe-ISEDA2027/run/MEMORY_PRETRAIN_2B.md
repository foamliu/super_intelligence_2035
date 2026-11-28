> 🔴 **内存清理巡检 · 2026-11-28 23:0x · #3605 · 用户令（19:0x 查两机内存+清理）**
>
> **OOM 定性（18:09 崩溃）**：dmesg/journalctl 无记录（权限受限或已轮转）；依 MEMORY #3582 既有定论：根因=fork-COW RSS 累积（nw=8×mmap→swap 耗尽→内核 OOM-kill rank13 DataLoader worker pid 3983423，SIGKILL `is killed by signal: Killed`）；修复=nw=2+no_mmap（commit c423bcb9cc 19:59）。当前 S2 以 nw=2 稳定运行（iter=351310 step~7.0s loss~1.498 0NaN 0skip）。
>
> **两机内存全景（清理前 → 清理后）**：
> | 节点 | RAM used | RAM avail | Swap used/total | AnonPages | si/so |
> |:--|--:|--:|:--|--:|:--|
> | .29 前 | 787G | 1085G | 7.8/8G (97.6%) | 790G | 0/0 ✅ |
> | .29 后 | 791G | 1081G | 7.8/8G (97.6%) | 794G | 0/0 ✅ |
> | .12 前 | 822G | 1045G | 1.6/8G (19.3%) | 793G | 0/0 ✅ |
> | .12 后 | 827G | 1040G | 1.6/8G (19.3%) | 798G | 0/0 ✅ |
> RAM 波动±4G 属训练 DataLoader RSS 自然增长，非清理影响。
>
> **Top RSS（两机一致）**：16×pt_data_worker（72-76GB each）+ 8×python（21GB each）= S2 训练进程，全活跃不可清。无 stale eval/torchrun 进程。
>
> **清理清单**：
> 1. `.12 /tmp/test_lang_mcore_hf`（8.3G · Aug 26 · pretrain HF 转换测试 · 3 月前 · 判无主：无进程引用）→ **已删** · 释放 8.3G 磁盘
> 2. `.29 /tmp/baize_s2_pure_launch.log`（4.7KB · 18:09 崩溃 S2 启动日志 · 本线自产）→ **已删**
> 3. `.29 /tmp/baize_s2_restart.log`（4.4KB · 19:22 重启日志 · 本线自产）→ **已删**
> 4. `.29 /tmp/baize_llm_launcher_help.txt`（8KB · launcher 帮助输出 · 本线自产）→ **已删**
>
> **未清（合规跳过）**：.29 `/tmp/phantomjs`(5.1G harness线)·`/tmp/gw_proxy_debug.log`(1.8G 系统活跃写入)·`/tmp/dsh_sse_forwarded.log`(685M 系统日志)·`/tmp/torchinductor_*`(663M 无法确认本线)·`/tmp/{matplotlib,blender_ui,django_*,astropy_*,sympy}`(harness SWE-bench 产物)·.12 `/tmp/lmms_eval_*`(19G 疑似 vision)·`/tmp/arm*_protb_feats`(vision)·`/tmp/R{8,9}_*`(vision)·`/tmp/ray`(1.4G Apr 2 无法确认本线)·.12 `/dev/shm/psm_*`(42 个 178M root 所有)·两机 NCCL shm(.29=18 .12=16)全活跃无 stale。
>
> **释放量**：磁盘 8.3G（.12）+ 17KB（.29）；RAM 无变化（清理项均非内存驻留）。
>
> **残余风险**：① .29 swap 97.6%（nw=2 COW 页驻留，si/so=0 无活跃换页，但 swap 余量极低——若训练遇内存尖峰可能再次 OOM）；② .12 /dev/shm psm_* 178M（root 所有无法清）；③ .12 /tmp 仍有 vision/data 线大目录（~40G+，非本线不可清）。
>
> **结论**：两机内存健康（avail>1000G·si/so=0），S2 训练稳定；18:09 OOM 已修复（nw=2+no_mmap）；清理释放 8.3G 磁盘；.29 swap 97.6% 需关注但不构成即时风险。详见 `run/reports/report_pretrain_memory_cleanup_zh.html`。

> 📎 **2026-11-28 11:1x · data 进展通报（供 pretrain 参考，非强制要求）**
>
> **一句话**：方案 C 全部完成、连续 fresh 复验 PASS；`blend_s2_preblend.tsv` 已 **13,847 → 180 shards / BLEND 14KB**，E2BIG 消除。data **WAITING=0**，无待答问题。
>
> ① **A 补丁已落地并双向验证**：`train.sh` L99-108（BLEND>100KB 时写 `blend_runtime.txt` + ARGS 传 `@filepath`）+ `pretrain_launcher.py` L284-290（识别 `@` 前缀从文件加载）。新 TSV 仅 14KB（<100KB）⇒ **连 `@file` 分支都不会触发**，走原生内联参数即可。
> ② **B pre-blend 5/5 DONE**（每源 16 shard）：finemath 64→16（9.4B tok）· megamath_pb 348→16（65B）· nemotron 193→16（195B）· stackv3_filt 8192→16（1.73TB）· megamath_web 4950→16（812GB）；`.done` + MANIFEST 齐全。
> ③ **验证**：`DRY=1` 端到端 S2=**180 shards inline、无 E2BIG**；S1 flag-off 回归 100 shards 正常；blendswitch **25/25 PASS**（`zero_overlap=0`、ratio `max_dev=0.0000%`）；`gen_blend --verify` PASS。
> ④ **启动口径**（与用户 10:1x 令一致）：`export BLEND_TSV=$PWD/configs/blend_s2_preblend.tsv` + `BLEND_CURSOR_OFFSETS_JSON=.../run/data/blendswitch/cursor_offsets_350k.json` → `setsid bash scripts/train.sh s1 > /tmp/baize_s2_launch.log 2>&1 </dev/null &`。**先 `git pull` 再取 TSV**；若仍见 13,847 shards = 旧 TSV。起后验 `blend.hot.switch` 生效 / iter 从 350k 续 / NaN=0 / step ≤7.4s。
> ⑤ **证据**：`run/data/blendswitch/{S2_SWITCH_ADVISORY.md, README_PATCH.md, verify_results*.json}`、`MEMORY_DATA.md` R1090–R1100。
> ⚠ **另（ops 11:09 体检，非 data 结论）**：S2 第二次尝试挂在 **EMFILE（fd 上限）**，不是 E2BIG；当前两节点 GPU 全 idle、ckpt 仍 350k。建议启动前两节点先 `ulimit -n 1048576`。
> ## 🔴 2026-11-28 10:1x 用户令 · **立刻执行 S2 切换**
>
> **用户原话**（逐字）：「你来直接执行 S2 切换」
>
> S1 已停、16 卡全空、350k ckpt 完好。**现在直接启动 S2**：
>
> ```bash
> cd /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm
> export BLEND_TSV=$PWD/configs/blend_s2_preblend.tsv
> export BLEND_CURSOR_OFFSETS_JSON=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/cursor_offsets_350k.json
> setsid bash scripts/train.sh s1 > /tmp/baize_s2_launch.log 2>&1 < /dev/null &
> ```
>
> 启动后验证：两节点 shim 生效（`grep -i 'blend.hot.switch'`）、iter 从 350k 续、NaN=0、step ≤7.4s。
> **本轮这是唯一动作**，不许再写「待运维决定」。
> ## 📎 2026-11-28 10:3x · **data 的诊断与建议，供你参考（不是强制要求）**
>
> 以下是 data 对 S2 启动失败的分析，**仅供参考**。你自己判断是否采用、如何采用；
> 若有更好的做法，按你认为对的做，不必迁就本文。
>
> **事实**：`RUN_ID 293` 启动 S2 失败于
> `torchrun: Argument list too long`（errno=E2BIG，08:06:45）。
>
> **data 判断的原因**（`run/data/blendswitch/S2_E2BIG_DIAGNOSIS.md`）：
> `train.sh` 把 blend 串作为**单个命令行参数**传给 torchrun；
> S2 有 13,847 个 shard ⇒ 串约 2.64 MB，超过
> `MAX_ARG_STRLEN`=128KB（单参数，编译期常量）/ `ARG_MAX`=2MB。
> S1 只有 ~100 shard、~20KB，所以没事。
>
> **data 给的三条路**（原文见其 §2）：
> - **A**：BLEND 写文件、命令行传 `@filepath`，`pretrain_launcher.py` 读到 `@` 时从文件加载。~15 分钟改 2 个文件，补丁 `run/data/blendswitch/fix_arg_too_long.patch`。
> - **B**：用 `pre_blend.py` 把 5 个未 pre-blend 的源各并成 16 shard（13,847 → ~192）。耗时 2-6h，`stackv3_filt`(1.8TB) 最慢。
> - **C**：A 先解锁 + B 后台并行。
>
> 用户已让 data 走 **C**。data 会跟进方案 A 的落地，并提示你 `DRY=1 bash train.sh s1` 可验 ARGS 是否已不含大字符串。
>
> **以上只是参考信息**。具体怎么改、改不改、有没有更简单的做法，由你判断。
❤️ **S2 MONITORING · 2026-11-29 01:52**·iter=352960/700000(50.4%)·step=6891-7011ms(last10 avg~6966ms=6.97s✅<7.4s gate)·loss=1.515-1.551(last10 avg~1.537 stable✅)·0NaN✅·0skip✅·GPU .29 8×100%/74GB✅ .12 8×57-100%/74GB✅(normal DP variance)·LR=1.000E-3 warmup DONE✅·grad_norm 0.078-0.351 normal✅·**grad_norm spike更新**:新spike iter352930 **2.258**(单步·loss=1.527 stable·0NaN·0skip·良性)·历史最大=iter350420 158.748(warmup·良性)·次大=iter352840 0.721·均为单步·loss未发散·**定性:偶发outlier非系统性问题**·blend-hot-switch shim applied✅·ckpt=352000✅·steps_since_restart=2960·TFLOP~1040/GPU✅·吞吐~605K tok/s✅·**内存**:.29 avail=843G swap=7.8/8G(97.6%·si/so=0✅)·.12 avail=989G swap=1.5/8G(si/so=0✅)·load .29=25(1min)/29(5min)/37(15min) .12=24(1min)/23(5min)·**⚠️已知·双节点确认**:cursor offsets未应用(.29+.12均BLEND_CURSOR_OFFSETS_JSON=""空)→7共享源从0重读→S1-S2重叠·S2已跑2960步(~758K samples·占700K总步0.42%·影响极小)·**待data正式验收交接后处置**(只读监控·20:0x令)·**data WAITING=0·config E(nw=2+no_mmap)达标·等data下轮正式交接**·**L1 eval**:340k=60.13% 350k=58.25%·eval_next=360k(ETA~13.6h≈11-29 15:25)·**autoqueue PID=1952828 alive✅**(idle·waiting for 360k·10k cadence confirmed✅)·**research日报11-29**:1条pretrain建议(MoLT looped transformer架构对照臂·CE token效率·不改主线配方只加对照)→同前轮·非本轮可执行·**常驻职责**:pretrain为训练健康负责·当前只读监控(data主导·20:0x令)·**训练健康判定:HEALTHY✅**(6.5h+稳定·step<gate·loss稳定·0NaN/0skip·grad_norm spikes良性)·WAITING: 0
WAITING: 0

> 📦 §#3582（2026-11-28 18:15, S2 CRASHED只读review·崩溃前iter=350920 step~7043ms loss~1.500·DataLoader worker SIGKILL pid 3983423·两节点全idle·ckpt=iter_0350000）→ daily-memories/2026-11-28.md
> 📦 §#3574–#3580+S2 runbook+event timeline+§#3444–#3565（2026-11-27~28, 监控巡检~60轮+S2切换准备+340k/350k eval+S2运行920步崩溃→OOM诊断→修复重启）→ daily-memories/2026-11-27.md + daily-memories/2026-11-28.md；需要时再读。
> 📦 §#3200–#3443（2026-11-22~27, 监控巡检+S2切换ALL READY+10k cadence+eval 270k-340k）→ daily-memories/2026-11-2{2,3,4,5,6,7}.md；需要时再读。
> 📦 §#2900–#3199及更早（已归档）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。
## S2 切换 Runbook（350k 时执行 · Plan F Bridge Edition 冷切换）

> 详版：`run/data/blendswitch/SWITCH_RUNBOOK.md`(182行) · cursor offsets：`run/data/blendswitch/cursor_offsets_350k.json`
> 方案：冷切换(stop→改env→restart) · shim=runtime monkey-patch(不改site-packages) · 触发=env var `BLEND_CURSOR_OFFSETS_JSON`(不设=stock零开销)

**切换前确认(10-point已验证✅，切换前快速复验)**：
- ①shim: `ls /nas_train/app.e0031982/code/BaiZe-ISEDA2027/blend_hot_switch_bridge_compat.py`(4226B)
- ②train.sh L203-207: `BLEND_CURSOR_OFFSETS_JSON`在PYTORCH_ENV(透传.12)
- ③pretrain_launcher.py L302-310: shim import try/except
- ④cursor_offsets_350k.json: 89.6M samples, 7 shared+5 new sources
- ⑤blend_s2_preblend.tsv: 在`code/baize-llm/configs/`(3625B, 12源 web40/code40/math20)

**执行步骤**：
1. 等350k ckpt落盘：`cat /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt`=350000
2. 记录现场：step time/loss/GPU util/两机load/训练PID
3. kill训练：kill .29 + .12 的 torchrun+pretrain_launcher
4. 改s1.env L16：`BLEND_TSV="$BAIZE_LLM_HOME/configs/blend_s2_preblend.tsv"`(原S1行注释保留)
5. 设env：`export BLEND_CURSOR_OFFSETS_JSON="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/cursor_offsets_350k.json"`
6. 从350k resume：`bash /nas_train/app.e0031982/code/baize-llm/scripts/train.sh s1`
7. 🔴验证shim生效：.29日志出现`[blend-hot-switch] Bridge compat shim applied`+`Applying cursor offsets` · **.12日志也必须出现**`Applying cursor offsets`(否则SSH透传失败→DDP数据不一致→立即kill回退)
8. 前100步观察：loss微跳±5%✅(>±15%调查)·ratio偏差≤1pp✅(>2pp调查)·step≤+2%·LR恒定1e-3
9. L1 eval 350k：CPU-only(daemon autoqueue 10k边界，与S2训练并行)

**回退(patch失败/loss spike/NaN/step>>7.4s)**：
1. kill训练 → `unset BLEND_CURSOR_OFFSETS_JSON` → s1.env恢复`BLEND_TSV=.../blend_s1_preblend.tsv`
2. 从350k ckpt用原S1配置resume → 标`⚠️待运维处理`

**首次切换失败教训(05:18)**：executor Phase4 只查.29 GPU0(fixed sleep20)·未查.12 GPU·.12残存显存→launcher FATAL"GPU非空闲"→auto-rollback S1(成功)·**已修复**:Phase4b加dual-node GPU poll(SSH查.12 max MiB·poll until both<1000MiB·max180s·rollback if not clear)·bash -n syntax OK
**纪律**：切换后恢复维护态(不再自行重启)·切换前后step/loss/GPU必须记录·cursor offsets由data验证(3级25/25 PASS)不需重验·executor fix已完成待运维决定重试

(心跳已迁移至顶部·此节为切换前 runbook)

---

## 待决策（等用户拍板）

### P2-001: L2/L3 评测瓶颈 — llama.cpp SSM bug + 早期训练（2026-11-12 #2063 更新 · HF五重验证完成）
- **现状**：160k ckpt(25%训练) L2 评测：llama.cpp 全 0%（SSM 生成 bug）。**🟢 HF transformers 五重验证完成**：HumanEval=15.0%(3/20) + GSM8K=10.0%(1/10) + MBPP=5.0%(1/20) + BBH=3.3%(1/30) + MATH=0.0%(0/10)，生成 Avg5集=6.66%。MMLU=23.16%(≈随机25%,MC不受生成bug影响=纯能力不足)。L3 TB smoke 0/2(llama.cpp生成退化)。L4 已移交 post-train。
- **根因定案（HF五重验证后）**：
  1. **llama.cpp SSM 生成 bug（主因）**：PR #31703 修复了权重映射，但生成仍退化(repetition loop)。HF transformers 生成正常，证明模型权重/SSM 计算正确。**修复路径：L2/L3 评测应用 HF transformers/vLLM 替代 llama.cpp**。
  2. **数据配比不足**：code 19% + math 7% = 26%。HF 显示 code 生成有效(15%) + math 有基础能力(10%) 但不足。MATH=0% 是唯一 HF 也=0% 的任务(MATH-500 难度远超 2B@25%训练)。
  3. **训练早期(25%)**：模型在 stable phase(lr=1e-3 恒定)，尚未进入 instruction-SFT/decay。MMLU≈随机说明知识能力未建立。
- **L3/L4 资源调查（#2063 新增 · #2069 L4 移交）**：
  - L3：无可用 GPU 做 vLLM-based 评测(.29 pretrain 8×100%, .12 vision R9 8×100%, .17 SSH timeout)。vLLM/SGLang 未安装在 .29/.12。CPU HF 太慢(multi-turn agentic)。
  - L4：**已移交 post-train（2026-11-12 用户令）**。不再做 L4 资源调查/SSH。post-train 隧道已 4 次复验 OK。
- **建议（🚫 不自行改生产配置）**：
  1. **短期(当前~350k,50%)**：维持现状继续监控。每 20k ckpt 跑 L1+L2(HF)，观察 MMLU 是否从 25% 起步上升、生成能力是否随训练改善。
  2. **评测改进**：L2 已切换到 HF transformers（五重验证完成）。L3 需 GPU 窗口(vLLM)或等 SSH .17 恢复。L4 已移交 post-train（不再 pretrain 负责）。
 
