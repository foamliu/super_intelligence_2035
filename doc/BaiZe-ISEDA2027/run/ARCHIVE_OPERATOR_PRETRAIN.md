## 归档 2026-10-31（由 BAIZE_PRETRAIN_2B_TASK.md 搬入，原文未改）

### 🚨 2026-10-30 22:2x 运维直令：写「1M 长上下文 + 95% 大海捞针」技术报告 · 最高优先

> **用户令**：「pretrain：写个报告，如何实现1M长上下文，如果我想在1M上下文实现>95%的大海捞针正确率，该怎么办。」

交付 `reports/report_pretrain_1m_needle_zh.html`（中文、单文件自包含、无外链/无 CDN），必须回答：
1. **现状基线**：Baize 2B Mamba2-hybrid 已能跑 1M（max_pos=1M、RoPE theta=1e6、64K prefill ≈41,598 tok/s、2M OOM）；长文能力与短文本能力的取舍现状。
2. **怎么做到 1M**：位置编码（theta / ABF / 动态 NTK）、训练阶段递进（4K→16K→32K→128K→1M 的 token 预算）、数据配比（长文/书籍/代码仓库/合成 haystack）、架构（Mamba2 状态大小、attn/ssm 混合比、CP/序列并行、显存）。
3. **怎么到 >95% needle**：needle 合成协议（针数 1/3/5、深度 0–100% 均匀、干扰项、多跳、变长针）、训练目标、评测协议（depth×position 网格；多针全中才算对；含改写/噪声）。
4. **实验矩阵**：≥5 组配置（theta、长文比例、续训步数、针数）附成本估算与预期准确率。
5. **取舍建议**：若只能做一件事选哪个、为什么；短文本回退的监控与护栏阈值。
6. 附录：与 Qwen3.5 / Llama3 等公开做法对比（可引 arXiv 摘要，注明来源）。

🚫 本轮不占 GPU 训练（16 卡在跑 S1）；数字必须标来源，无实测的写"估算"。


## 归档 2026-10-25（由 BAIZE_PRETRAIN_2B_TASK.md 搬入，原文未改）

### [运维令] 2026-10-25 20:2x（seq 4096->8192 掉速 5.6x 的根因排查：补对照 + 时间分解 + web search 对标）· 用户直令 · 最高优先
> 用户原话：「让 pretrain 排查一下为啥 seq 从 4096 翻到 8192 吞吐掉这么多，也可以web search，这个不符合常识，因为阿里等公司用8192预训练还是常见的，而且我们又是Memba2-hybrid，理应对长上下文更加友好。」
> 现状（实测）：cfg1（seq8192 / 2M tok/step）**108,291 tok/s** vs 基线（seq4096 / 4.13M）**606,449 tok/s**；per-GPU 6,768 vs 37,900（-82%）；峰值显存 79.2 vs 67.6 GB。
> 运维判定：**该降幅不符合常识** —— BaiZe-2B 只有 4/56 层带 attention、24 层 Mamba2（线性于 seq）、28 层纯 MLP；同 tok/step 下 seq 翻倍的合理代价约 **+10~30%**。**证据不齐前，禁止把「Mamba2 SSM 超线性」写进报告/MEMORY 结论**（MEMORY #779 已有此句，本轮改为「推测·待验证」）。

**1) 先补对照（现在的网格不是单变量：GBS 1008->256、MBS 3->2 一起变了）**
- `cfg0a`：seq=4096 / S1 / mbs=4 / gbs=512（tok/step=2,097,152，与 cfg1 **只差 seq**）
- `cfg0b`：seq=4096 / S2 / mbs=3 / gbs=1008（tok/step=4,128,768，**用同一脚本重跑基线**）
- 判据：`tok/s(cfg0a) / tok/s(cfg1)`；`tok/s(cfg0b) / 606,449`。若 cfg0b 偏差 >5% ⇒ **先查环境/脚本差异**（CUDA graph、fp8、NCCL 变量、数据 blend、launcher 参数），不得继续谈 seq。

**2) 时间分解（归因核心证据，每格都要）**
- 开 Megatron 计时（`--log-timers-to-tensorboard --timing-log-level 2` 或等价），取 step 30-80 的 `forward-compute / backward-compute / optimizer / data-loading` 均值。
- 每格采一次 `nvidia-smi dmon -s u -m -c 60`：GPU util 均值、util <10% 的时间占比。
- 查 CUDA graph 是否真生效（log 里 capture 成功/失败、是否回退 eager），4096 与 8192 对比。
- 查数据侧：seq=8192 时每步读几个 shard、是否跨 shard 重打包、worker 数 / CPU 饱和 / 队列空转；与 4096 用同 16 个 `p5b_l3` shard 对比。
- 查 kernel/精度：`--mamba-ssm-dtype` 实际取值（recipe 内是否强制 float32）、chunk_size、sequence parallel / TP 在 8192 下是否被关、TE/fused kernel 是否回退。

**3) web search 对标（用户点名，必须真检索并引用）**
- 检索方向：Qwen2.5 / Qwen3 预训练序列长度与吞吐；Llama 3（8K 预训练）；Megatron-LM 长序列最佳实践（sequence parallel / context parallel / activation recompute）；`mamba_ssm` 与 Megatron-Core hybrid Mamba 的已知性能坑（chunk scan、fp32 state、TP 下 scan 切分）；「同 tok/step 下 seq 翻倍的合理吞吐损失区间」。
- 每条写：来源（标题 + arXiv 号 / 官方文档 / 博客 + 年份 + **检索日期 2026-10-25**）、结论、与本项目可比性；**查不到就写「未查到」**，不许凭印象。

**4) 假设-检验表（报告必须逐行给实测结果）**
| 假设 | 检验方式 | 若成立的特征 | 实测 | 结论 |
|:--|:--|:--|:--|:--|
| H1 数据管线在 8192 下重打包/跨 shard，GPU 饥饿 | data-loading 计时 + util 曲线 | data-loading 占步时 >50%，util 长期 <20% | | |
| H2 CUDA graph 在 8192 回退 | log capture 行 | 出现 fallback / capture failed | | |
| H3 Mamba2 fp32 SSM + chunk scan 长序列低效 | 改 chunk_size / 临时 bf16 对比（标为配方变更组） | 改后 tok/s 明显回升 | | |
| H4 小 GBS/MBS 导致 overlap 与利用率下降 | cfg0a 对照 | 4096 也掉到 ~110K ⇒ 与 seq 无关 | | |
| H5 8K 本身计算更贵 | 排除 H1-H4 后 | compute 占比接近 100% 且随 seq 增长 | | |

**5) 修复与复测**
- 定位主因后**只改那一项**（如 seq 粒度预打包 / 加 dataloader worker / mamba dtype / 恢复 CUDA graph），用同一 `cfg0a` 复测，给修复前后 tok/s、step time、显存对比。
- 判据：修复后 `cfg0a` 相对基线同 tok/step 的降幅 **≤30%**；若仍 >50% ⇒ 保留现场证据上报，不许硬编结论。

**6) 交付**
- `reports/report_pretrain_seq8192_slowdown_rootcause_zh.html`（中文 HTML 自包含、0 `<script>` / 0 外链、≥15KB）：摘要 / 现象与口径 / 对照实验 / 时间分解与 util / 假设检验表 / 外部对标 / 根因 / 修复与复测 / 复现命令 / 数据溯源。
- 更新 `reports/report_pretrain_seqlen_throughput_zh.html` 与 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新节；生成器 `run/gen_seq8192_rootcause_report.py`（重跑 diff 空）。
- 修正 MEMORY #779 机制结论标注；commit 前缀 `pretrain rc:`。
- **排期调整（20:5x 运维追加，优先级高于主表）**：`cfg3` 跑完后**先插 `cfg0a` + `cfg0b`**（两个合计约 20 分钟：cfg0a 3.5s/step x80 + 起停，cfg0b 6.8s/step x80 + 起停），**再续 cfg4-cfg6**。做法：cfg3 结束、`release_gpus` 返回后，SIGTERM 编排器 `baize_seqlen_grid_test.sh`（只杀编排进程，不碰 torchrun 子进程——此刻应已退出），把 `CONFIGS` 改成 `cfg0a cfg0b cfg4 cfg5 cfg6`，重新 `setsid` 起；若来不及在 cfg4 启动前拦住，就等 6 格全跑完立刻补跑，**不许省这一步**。
- **模块级 profile（H6/H7 的唯一判据）**：在 `cfg0a`（4096）与 `cfg1`（8192，可重跑 10 步）上各用 torch profiler / Nsight 采 10 步，输出 `attention / ssm(chunk scan) / mlp / loss / optimizer / data` 六类的时间占比与绝对毫秒；判据：若 `attention` 占比随 seq 平方增长 ⇒ H6 成立；若 `ssm` 绝对耗时随 seq 明显超线性 ⇒ H7 成立；两者都不成立再看 data。
- 总 ETA 相应调整：cfg3 ~21:10 -> cfg0a/cfg0b ~21:40 -> cfg4-cfg6 ~22:40 -> profile + 修复复测 ~23:40 -> 报告次日 00:30 前。

**补充（22:3x，网格已全部结束，数据来自 `/tmp/baize_seqlen_grid/ALL_RESULTS.txt` 原始行）**
| cfg | seq | tok/step | tok/s | med_ms | per-GPU | peak MiB | 状态 |
|:--|--:|--:|--:|--:|--:|--:|:--|
| cfg1 | 8192 | 2,097,152 | 108,291 | 19,365.9 | 6,768 | 81,087 | OK |
| cfg2 | 8192 | 4,194,304 | 111,897 | 37,483.7 | 6,993 | 81,085 | OK |
| cfg3 | 16384 | 2,097,152 | 112,094 | 18,708.9 | 7,005 | 81,087 | OK |
| cfg4 | 16384 | 4,194,304 | 121,495 | 34,522.4 | 7,593 | 81,079 | OK |
| cfg5 | 32768 | 2,097,152 | FAIL | - | - | 81,031 | FAIL |
| cfg6 | 32768 | 4,194,304 | FAIL | - | - | 81,031 | FAIL |
- **平台证实**：8K/16K 下 tok/s = 108~121K，且随 seq **略升**（108->112->121）；tok/step 翻倍只 +3~8% ⇒ 与批大小无关的**每 token 固定成本被放大 5.6x**，拐点就在 4096。
- **新证据（重要）**：四格峰值显存几乎一致（81,079-81,087 MiB，卡在 80GB 上限），**与 seq、tok/step 都无关** ⇒ 疑似存在**与 seq 无关的固定巨额分配**（workspace / 优化器状态 / 未分片缓冲 / CUDA graph 常驻池）；cfg5/cfg6 在 81,031 MiB 处 FAIL ⇒ 32K 所需的额外一点显存直接撑爆。请把「固定 81GB 到底是谁」列入 profile 清单（`torch.cuda.memory_summary()` + 分项 snapshot）。
- **cfg5/cfg6**：先给 FAIL 的 torch 报错原文与判定（OOM / 其他），再按「配方变更组」用 `--recompute-activations` 或 `--use-distributed-optimizer` 重试，单列不混主表。

**补充（22:5x：cfg0a 已证伪「seq 致慢」，追加两条必做实验 + 报告更正）**
- 事实：`cfg0a`（seq4096 / mbs4 → **16,384 tok/microbatch/GPU**）= **113,514 tok/s**，与 cfg1（seq8192 / mbs2 → 同为 16,384）= 108,291 基本一致 ⇒ **seq 不是主因**；基线（seq4096 / mbs3 → **12,288 tok/microbatch/GPU**）= 606,449 ⇒ 悬崖落在 12,288→16,384 tok/microbatch 之间（且该区间峰值显存从 67.6GB 顶到 81GB）。
- **必做 A（运维判断的关键验证，10 分钟）**：`seq=8192 / mbs=1 / gbs=256（accum=16）` → **8,192 tok/microbatch/GPU**。判据：若 tok/s 回到 ~55-60 万 ⇒ **「seq=8192 可以满速，只要把 MBS 降到 1」**，这是直接给用户的可行结论；若仍 ~110K ⇒ 说明与 tok/microbatch 无关，回去查 gbs/accum 与 kernel。
- **必做 B（16K 的出路）**：`seq=16384 / mbs=1` 必然是 16,384 tok/microbatch ⇒ 注定踩崖；**要么开 context parallel（CP=2/4）把每卡序列切短，要么 16K 只做小规模微调**。请在报告里给 CP 的可行性判断（当前 config dump：SP=false / CP=1）。
- **报告更正（必做）**：`reports/report_pretrain_seqlen_throughput_zh.html` §7 现在写「任何 seq>=8192 都崩 ~5x、建议维持 4096」——这是**基于错误归因**的结论。cfg0b 与必做 A 出数后，必须把该节改成「**悬崖由 tokens/microbatch/GPU 触发，与 seq 无关**」，并给「seq=8192 + mbs=1」的实测档位；旧结论标「已证伪」保留可追溯。



**补充观测（20:40，cfg2/cfg3 出来后，归因更清楚了）**
| cfg | seq | tok/step | tok/s | per-GPU | 相对基线(606,449) |
|:--|--:|--:|--:|--:|--:|
| 基线 e18 | 4096 | 4.13M | 606,449 | 37,903 | 1.00x |
| cfg1 | 8192 | 2.10M | 108,291 | 6,768 | -82% |
| cfg2 | 8192 | 4.19M | 111,897 | 6,993 | -82% |
| cfg3 | 16384 | 2.10M | **112,094**（实测，非早期 step10 折算） | 7,005 | -82% |
- **形态更正（22:1x 运维，依据 cfg3 实测 112,094）**：不是「超线性」，而是**在 seq 4096->8192 之间发生一次阶跃式跌落（约 5.5x），之后 8192 与 16384 都平台在 ~108-112K**：
  - 8192/2.1M = 108,291 -> 8192/4.19M = 111,897（tok/step 翻倍仅 +3%）；
  - 16384/2.1M = 112,094（seq 再翻倍基本不变）。
- ⇒ **H6（attention O(seq^2) 主导）基本被证伪**（若是二次成本，16384 应比 8192 再掉一半，实测没有）；
- ⇒ 单点特征指向**「seq>4096 触发了另一条 kernel/执行路径」**：`--mamba-ssm-dtype float32` 的 SSD chunk scan 慢路径、CUDA graph 在 8K 失效回退 eager、或数据管线在 8K 的固定开销。既然 8192 与 16384 同速，**主因大概率是「每 token 固定成本被放大」而非「随 seq 增长」**。
- 必须用 profile 定位到模块级；并**找出拐点**：若 cfg0a（4096/2.1M）回到 ~600K，则再补一格 `seq=6144`（若模型/数据支持）或 `seq=5120`，把跌落锁定在 4096-8192 之间。

**追加假设**
| H6 | 4 层 attention 在 seq>=8192 走了非 flash/未融合路径（O(seq^2) 主导） | torch profiler / Nsight 按模块取时间占比；查 attention backend 与 flash 可用性日志 | attention 模块占比随 seq 平方增长 | | |
| H7 Mamba2 SSD chunk scan 在长 seq 下走 fp32 逐 chunk 扫描（非融合） | 对比 `chunk_size` 与 dtype；查是否命中 PyTorch 2026-02 所述「五算子融合」前的慢路径（该博文实测融合可提速 1.50-2.51x） | 改 chunk/融合后 tok/s 明显回升 | | |
| H8 seq>4096 触发路径切换（CUDA graph 失效 / attention backend / kernel 选择器） | 对比 4096 与 8192 的 log 中 graph capture 与 kernel 名；补 cfg0a 与 seq=6144 定位拐点 | 4096 正常、8192 起阶跃；且 8192 与 16384 同速 | | |
| H9 数据管线在 8K 的每样本固定开销（非 token 线性） | data-loading 计时在 8192/16384/4096 三点对比；看 samples/s 是否恒定 | samples/s 恒定（tok/s 随 seq 线性） ⇒ 数据侧；实测 tok/s 恒定 ⇒ 排除 | | |


### [运维令] 2026-10-25 17:5x（**seq 增大 x 每步 token 数固定（2M / 4M）的 16 卡吞吐网格**）· 用户直令 · 最高优先
> 用户原话：「pretrain：测试下列配置的16卡训练吞吐 1）seq=8192, 2M tok/step 2）seq=8192, 4M tok/step 3）seq=16384, 2M tok/step 4）seq=16384, 4M tok/step 5）seq=32768, 2M tok/step 6）seq=32768, 4M tok/step 也就是在每步训练数据量不变（2M/4M,对应S1和S2）的情况下，看看增大seq对训练吞吐的影响。」

**1) 网格（唯一变量 = seq；同组内 tok/step 与数据配比不变）**
| # | seq | tok/step | GBS(seq) | DP16 每卡 seq/步 | MBS x 累积 建议 | 备注 |
|:--|--:|--:|--:|--:|:--|:--|
| 1 | 8192 | 2,097,152 | 256 | 16 | 2x8 或 4x4 | S1 组 |
| 2 | 8192 | 4,194,304 | 512 | 32 | 2x16 或 4x8 | S2 组，约等于基线 tok/step |
| 3 | 16384 | 2,097,152 | 128 | 8 | 1x8 | S1 组 |
| 4 | 16384 | 4,194,304 | 256 | 16 | 1x16 | S2 组 |
| 5 | 32768 | 2,097,152 | 64 | 4 | 1x4 | S1 组 |
| 6 | 32768 | 4,194,304 | 128 | 8 | 1x8 | S2 组 |

- GBS 必须整除 DP16；`tok/step = GBS x seq` 必须**逐项核对等于表内值**（256x8192=2,097,152 等）。
- 配方冻结：**DP16 / TP1 / PP1 + FP8 tensorwise + CUDA Graphs + 真数据**（与双机 e18 同口径）；Mamba2 侧沿用 `--mamba-ssm-dtype float32`。**除 seq 与随之变化的 MBS / 累积外，一律不许改**。
- 数据：**2M 组用 S1 配比、4M 组用 S2 配比**；同组 3 个 seq 必须来自**同一条 token 流**（同一批 packed shard，仅切块长度不同），并把打包命令写进报告，证明单变量。
- 基线参考行（不计入 6 格，单独标注）：seq=4096 / 4,128,768 tok/step / DP16 e18 = **606,300 tok/s**（`/tmp/baize_dualnode_16gpu/`）。

**2) 测法（与既有口径一致）**
- 每配置 `ITERS=80`；取 **step 30-80 的 median step time**（6 点，与双机 e18 同规则）。
- 必报：`tok/s`（主指标，= tok/step 除以 median step 秒）、`step/s`、median step ms、per-GPU tok/s、峰值显存（GB）、loss、gnorm、NaN 计数。
- 每组内派生：**每翻倍 seq 的吞吐损失百分比**（vs 同组 seq=8192），并列「2M 与 4M 的绝对吞吐差」。
- **OOM 处理**：只许两种回退，且必须**标为「配方变更组」单列、不混进主表**：(a) MBS 降到 1、用累积补回 tok/step；(b) 加 `--recompute-activations` 或 `--use-distributed-optimizer`。仍 OOM 就把该格写「OOM（峰值显存 xx GB，卡 x）」+ 已试过的回退，**不许留空、不许编造**。
- 每格跑完立刻释放 16 卡（`nvidia-smi` 全 0 MiB 再起下一格）；**不许为写报告保占**。

**3) 结论要求（报告的落点）**
- 主表 6 行全填；再给「tok/s 随 seq 变化」双曲线（2M / 4M 各一条，同图）。
- 机制解释**必须带实测支撑**：seq 变大则激活 / 显存变大、MBS 被迫变小、每步通信 / 调度占比变化；BaiZe-2B 是 **Mamba2-hybrid（24 SSM + 4 Attn + 28 MLP-only，只有 4/56 层带 KV）**，注意力成本结构性低于纯 Transformer，此点**须用本网格数据印证，未验证就标「推测·未验证」**。
- 给 **S1 / S2 该选多大 seq** 的可执行结论（若 seq 增大导致吞吐降幅大于 10%，明确建议维持 4096 / 8192 并说明理由）。
- 预计机时：单格 80 步 x (2-25 s) + 起停约 5 min，**6 格合计 2-5h**；先跑第 1 格标定，再回写总 ETA。

**4) 产出**
- `reports/report_pretrain_seqlen_throughput_zh.html`（中文 HTML 自包含、0 `<script>` / 0 外链、不低于 15KB）
- 生成器 `run/gen_seqlen_throughput_report.py`（数据字典写脚本顶部，重生成 `diff` 必须为空）
- `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新节「seq 长度 x tok/step 吞吐网格」+ MEMORY 首部新块 + daily；commit 前缀 `pretrain seqlen:`（只 add 本次动的文件）。

**铁律**
- 不用 mock 数据出主表；配方变更组不许混进主表；报告禁 N/A / 空单元格（OOM 也写清原因）。
- 不动单机 e18 与双机 e18 的既有结论 / 日志；新实验日志进 `/tmp/baize_seqlen_grid/<cfg>/`。


### 🚀 运维指令 · 2026-10-24 16:0x（**① 305K 最佳实践写入任务书 ② longctx 报告用错模型：重测重写**）· 用户直令 · 最高优先

> 用户原话：「1. 把第二轮最佳：**MBS3+FP8 TW+CG=305K tok/s（+2.6% vs 第一轮 / +21.0% vs 基线）**作为**最佳实践简要写入任务书**；2. 早上提交的 `report_pretrain_longctx_infer_cost_3x2b_zh.html` **有问题，BaiZe-2B 不应该采用 Xmodel-2.5 模型，而是应该沿用一直实验的 BaiZe-2B (Mamba2-hybrid）模型。重新测试，重写报告。**」

---

**① 最佳实践（写入本任务书「💡 最佳实践 / 硬口径」区，常驻）**

> **BaiZe-2B 训练吞吐最佳配置（2026-10-24 第二轮定档，勿再重复扫描）**
> - **配置**：`MBS3 + FP8 tensorwise + CUDA Graphs`（即 e18）
> - **吞吐**：**305K tok/s**
>   - **+2.6%** vs 第一轮最佳 e09（297K）
>   - **+21.0%** vs 基线 252K / **+22.5%** vs 历史 249K
> - **关键机理**：FP8 tensorwise **单独用反而 -10%**（Mamba2 SSM 小 GEMM 的量化 kernel launch 开销 > 计算节省）；**必须叠加 CUDA Graphs** 让量化 kernel 被图捕获，FP8 带宽收益才释放。
> - **显存**：MBS3 下需确认峰值；80GB 内已知可行。
> - **上限已确认 = 305K**（5 条依据闭合：VRAM / 计算（GPU 100%）/ 通信（NCCL 无收益）/ 软件栈（compile 崩溃）/ FP8 blockwise 驱动级阻塞）。
> - **CUDA 12.9 不可用**：驱动 570.195.03 最高支持 12.8，12.9 需驱动 ≥575 → **驱动级 BLOCKED**（即使新建 conda env 也不行），升级需 root。
> - 🚫 后续全量预训练**直接用 e18 配置**，不必再扫吞吐。

---

**② longctx 报告重测重写（核心问题）**

**问题定位（运营方已核实报告内容）**：当前报告的"BaiZe-2B"写的是：
```
BaiZe-2B ~1.35B
架构 LlamaForCausalLM (由 XmodelForCausalLM 转换)   ← ❌ 错
层数 48 / hidden 1536 / 24 heads / GQA 8 KV / vocab 129,280 / 权重共享
来源 自有模型 decay-5000 (Xmodel-2.5-code)          ← ❌ 错
```
**这是 Xmodel-2.5 的 Dense 架构（decay 后转换），不是 BaiZe-2B。**

**BaiZe-2B 的真实规格**（必须以此为准）：
- **架构：Mamba2-hybrid**（56 层 = 28 SSM + 28 Attention，hidden=2048，heads=16，**真实参数量 2.220B**）
  - ⚠️ **口径订正（历史遗留错误）**：**不是 3.00B**。`3.00B` 来自 mcore 打印 `transformer layers 2.47 + embedding 0.53`，该打印**对 Mamba/hybrid 误把 56 层全按 full attention+MLP 计**。真实值以 `sum(numel())` = **2,220,268,032 = 2.220B** 为准（见 `EXPERIMENTS_2B.md` L7、`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` L79）。
  - **对比参照**：MiniCPM5-2B 实测 **2.512B**（transformer 1.98B + embedding 0.53B，tie=False 双嵌入）⇒ **BaiZe 反而更小**（2.220B < 2.512B）。**报告中若做对比，必须写"BaiZe 参数量更小的前提下达到/超过"**，这是加分点，不要写反。
- **不是 Dense Transformer，不是 XmodelForCausalLM**
- 模型路径请从 Baize-ISEDA2027 里**实际训好的 BaiZe-2B 权重**取（`nemo_experiments/` 下与 pretrain_launcher `--arch mamba2` 对应的产物）

**重测要求**
1. **确认模型**：加载前打印 `arch` / 层类型统计（SSM vs Attention 层数）/ 参数量，**贴在报告里**，证明是 Mamba2-hybrid。
2. **SGLang 支持性核查**：Mamba2-hybrid 在 SGLang 0.5.9 下是否有专门支持（mamba backend / `--mamba-ssm-dtype`）？**若需特定 flag 或版本，先报再测**；若确实不支持，如实写"该架构在 SGLang 下不可服务"而不是拿 Dense 模型顶替。
3. **三模型同口径重测**：BaiZe-2B(Mamba2-hybrid) / MiniCPM5-2B / Qwen3.5-2B，**同样的上下文阶梯 64K→2M、同样的测量协议**（1 预热 + 2 次取中位、生成 128 tok、`--disable-radix-cache`、mem-fraction 0.88）。
4. **关键对比维度（Mamba2 的意义就在这）**：
   - **KV cache 增长曲线**：Mamba2 只有 Attention 层有 KV（28/56 层），**显存增长应显著慢于 Dense**
   - **TTFT / Decode 吞吐随上下文的退化斜率**
   - **能服务的最大上下文**（谁先 OOM）
5. **必须加一节"架构差异说明"**：讲清 Mamba2-hybrid 的 SSM 层是**常数状态**（不随上下文增长），这是它与 Dense 在长上下文成本上的**结构性差异**——这正是本报告的价值所在。

**③ 交付**
- 重写 `reports/report_pretrain_longctx_infer_cost_3x2b_zh.html`（**覆盖旧版，旧版先备份为 `.bak`**）
- 报告中**必须写明**："旧版误用 Xmodel-2.5 Dense ckpt，本版改用 BaiZe-2B (Mamba2-hybrid) 重测"
- 数据可溯源：每个数字对应 `logs/` 或 `/tmp` 中的原始测量文件
- commit 前缀 `pretrain report:`

**④ 纪律**
- 🚫 不再扫吞吐（305K 已定档）
- 🚫 不动 vision（`.12`）/ 不改 5 源分词产物
- ✅ 每轮落 MEMORY + daily



> 📦 §运维令·2026-10-24 09:3x（放行继续优化吞吐）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：R2c完成,e18=305K定档,7/7建议闭合。需要时再读。

> 📦 §运维指令·2026-10-23 22:1x（优化吞吐>249K）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：10/10候选完成,297K→305K新纪录,HTML报告已交付。需要时再读。

> 📦 §运维指令·2026-10-23（长上下文推理成本评测3模型）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：Qwen3.5-2B独享1M上下文最快,HTML报告已交付。需要时再读。

> 📦 §运维指令·2026-10-23（decay修复中文HTML报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：decay-5000官方μP+Muon修复,CS8=58.97%,报告已交付。需要时再读。

> 📦 §运维指令·2026-10-22 13:5x（decay 5000步+MBS5排障）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：decay=5000步,MBS5+recompute排障,官方1113.sh口径。需要时再读。

> 📦 §运维指令·2026-10-22 08:5x（decay参考官方1113.sh+20B）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：参考官方train_decay_fp8_1113.sh,20B数据,5560步。需要时再读。
> 📦 §2026-10-09:3x（写两份中文 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：两份报告已交付（v2_result + short_experiment, commit c44ef1fea）。需要时再读。

> 📦 §2026-10-02:3x（授权自主排查根因）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：L1 CS8=59.03% / L2 kill@step2370 / L3 作废，方向转 A方案官方 Megatron。需要时再读。

> 📦 §2026-10-21:5x（decay v2 对照口径纠错）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v2 CS8=44.97% vs 官方 65.40% Δ−20.43pp，起点 61.03%⇒decay 训坏。需要时再读。

> 📦 §2026-10-14:2x（评测 decay v2 final）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：14集eval CS8=44.97%/CX6=6.21%，报告已交付。需要时再读。

> 📦 §2026-10-06:1x（事故复盘报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：crash@02:45 NCCL timeout→resume step_18000→收尾，P0-a/b 已落地，硬件=transient。需要时再读。


### 🚀 运维令 · 2026-10-24 23:5x（**双机已调通 ⇒ 转入「双机吞吐优化」阶段**）· 用户直令 · 最高优先
> **已调通（23:22–23:37，16 卡 DP=2×8，`baize_dualnode_16gpu_test.sh`）**：median **512,801 tok/s** / mean 508,860 / **扩展效率 84.0%** / 每卡 32,050 / 峰值显存 **64.4 GB** / loss 0.3695 / gnorm 0.72 / **0 NaN、0 skip**；NCCL 走 `NET/IB/0,2,6…` 多通道。
> ⚠️ **口径陷阱**：这次是 **BF16 mixed + `--mock` 数据**，而单机基线 305,098 是 **FP8 tensorwise + CUDA Graphs + 真数据** ⇒ 84% 只能证明"IB 健康"，**不能**直接当扩展效率结论。
> ⚠️ **launcher bug**：`baize_dualnode_16gpu_test.sh:114/115  WORKER_SSH_PID: unbound variable`（`set -u` 下 worker 收尾即报错，导致脚本"挂在 SSH 清理"）→ **先修**（`WORKER_SSH_PID=${WORKER_SSH_PID:-}`，或在 worker 分支前置空）。
>
> **优化任务（按序执行，每项固定 80 步；每次跑完立刻释放 16 卡）**
> - **A. 口径对齐（必做第一步）**：16 卡跑 **e18 配方（MBS3 + FP8 TW + CUDA Graphs + 真数据）** ⇒ 得到与 305K 可比的真实扩展效率（预期 ~0.84）；同时留 BF16 组作对照。
> - **B. NCCL/IB 调参**（每项单独跑）：`NCCL_IB_QPS_PER_CONNECTION` 1/4/8 · `NCCL_MAX_NCHANNELS` 32/64 · `NCCL_ALGO`(Ring/Tree)×`NCCL_PROTO`(LL/LL128/Simple) · `NCCL_NET_GDR_LEVEL` 2/3 · `NCCL_IB_HCA` 子集（**排除 `.29` 的 `mlx5_7`/`mlx5_15` 两个 PORT_DOWN**）· `NCCL_CROSS_NIC=1`
> - **C. 通信/计算重叠**：`--overlap-grad-reduce` / `--overlap-param-gather`（DP=16、TP=1 下是否有收益）
> - **D. MBS/GBS**：MBS3→**4**（64.4 GB 尚有 ~15 GB 余量）· GBS 1008→2016
> - **E. 分布式优化器**：`--use-distributed-optimizer`（用显存换更大 MBS）
> **判据**：每项报 `tok/s`、`扩展效率`、`median step ms`、`峰值显存`、`loss/gnorm`（与 e18 对齐，Δloss ≤5%）；最优组合写进 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新节「双机吞吐优化」+ 中文 HTML 报告 `reports/report_pretrain_dualnode_throughput_zh.html`（含每项对比表与结论）。
> 🚫 不得改单机 e18 配方本身；🚫 不要再用 mock 数据下的数字对外宣称"扩展效率"。


> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。
> 📦 §运维实测·2026-10-24 21:45（2-rank NCCL打通）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：4个NCCL IB变量(GID_INDEX=3/MTU=4096/TC=106/TIMEOUT=22)必须照抄主从两侧,busbw≈46GB/s。需要时再读。

> 📦 §运维令·2026-10-24 21:0x（NCCL卡在worker初始化）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：最小复现2rank打出Init COMPLETE,锁RoCE环境变量缺失。需要时再读。

> 📦 §应急令·2026-10-24 19:2x（loop卡死29h重启）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：loop已重启,16卡双机测试已执行。需要时再读。

> 📦 §运维指令·2026-10-24 16:2x（双机16卡联合训练测最大吞吐）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：双机16卡e18=606K tok/s,扩展效率99.4%(已纠正#767误报512K/84%)。需要时再读。

> 📦 §补正·2026-10-24 16:2x（SGLang对Mamba2支持已验证）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：sglang 0.5.9原生支持nemotron_h,照抄P-9.11配置,加--mamba-ssm-dtype float32。需要时再读。


### 🚀 运维令 · 2026-10-25 07:4x（**写「双机 16 卡吞吐优化与测试」报告**）· 用户直令 · 最高优先
> 用户原话：「pretrain：关于16机吞吐量优化和测试，写个报告。」
> 即 **16 卡（双机 2×8×H100，DP16/TP1）吞吐优化与扩展性测试报告**。任务书 10-24 23:5x 块已写明「最优组合 + 中文 HTML 报告」是本阶段交付物 ⇒ **本轮把它落地成一份完整报告**，不再拖到下轮。

> **① 先判状态（不许盲目重跑）**
> - 立刻查 Task B 进度：`ps -ef | grep -E 'baize_dualnode_tune' | grep -v grep`；逐 TAG 看 `/tmp/baize_dualnode_tune/<TAG>/` 的 master/worker 日志是否跑满 80 步。
> - **若正在跑** ⇒ 让它跑完（不 kill、不重启），本令**并行走写作**：先把已有数据（Task A 全部 + qps4/qps8 已闭合项 + 当前已闭合的 TAG）写进报告 §2–§5，报告**标 `rev1（在测）`**；剩下的 TAG 闭合后再补 `rev2`。
> - **若已停/卡死** ⇒ 先按铁律保留现场（日志不删），再决定是否重跑未完成项（每项 80 步、跑完立刻释放 16 卡）。

> **② 数据来源（只许引用落盘实测，禁推测）**
> - Task A（已闭合）：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` §「双机吞吐优化（Dual-node 16-GPU scaling）」+ `/tmp/baize_dualnode_16gpu_prevrun_23x/` + `/tmp/baize_dualnode_bf16_ctrl/summary.txt`。
> - Task B：`/tmp/baize_dualnode_tune/<TAG>/`（master.log / worker.log / summary.txt）。
> - 原始日志里取 **两类行**：master `Step Time`（iter 20–80）、worker `elapsed time per iteration`（iter 30–80）；**median 取 step 30–80（6 点）**，与已有基线同口径。
> - ⚠️ **#767 误报教训写进报告 §6「口径与纠错记录」**：512,801 tok/s / 84% / BF16+mock / 64.4GB 一组数字**作废**，实为 606,300 tok/s / 99.4% / FP8 tensorwise + 真数据 / 67.6GB。凡是**没有原始日志支撑**的数字一律不许进报告正文。

> **③ 报告结构（照着写，缺的项写「未测 · 原因」）**
> 1. 摘要（一屏结论：最优配置 + 峰值 tok/s + 扩展效率 + 相对单机增益）
> 2. 测试环境与口径（2×8×H100、DP16/TP1/PP1、IB/RoCE 12 口、4 个固定 NCCL 变量、IB busbw≈46GB/s、每项 80 步、median 规则、seq=4096、真实数据）
> 3. **扩展性主结果**：单机 e18 305,098 → 双机 e18 606,300（**99.4%**）；每卡 38,137→37,894（−0.6%）；中位步时 13,533→6,810ms（几乎完美减半）
> 4. **精度消融**：FP8 tensorwise 606,300 vs BF16 528,016 = **+14.8%**，显存≈持平（67.6 vs 67.1GB），Δloss 0.08% ⇒ 两种精度均近线性扩展、通信非瓶颈
> 5. **Task B NCCL/IB 调参全表**：每 TAG 一行（tok/s / 扩展效率 / vs 基线 / step ms / 显存 / loss / Δloss / NaN）；已闭合 qps4(+0.0%)、qps8(+0.2%) 明确写「无收益」；未闭合 TAG 标「在测」并给 ETA
> 6. **机制解释（这是报告的价值所在）**：为什么 99.4%？——2.2B 梯度 ~4.4GB / busbw≈46GB/s ≈ 0.1s vs 6.8s 步时 ⇒ **allreduce 占步时 <1%**；故 QPS/CHANNELS 等 IB 参数**结构性无收益**，GPUDirect RDMA + 12×RoCE 已把跨机通信压到噪声级
> 7. **与单机优化线的对照**：单机 10 项优化 9/10 完成、命中 305K 上限（#2 CUDA12.9 被驱动级 BLOCKED）；**双机 +99.4% ⇒ 结论：要再提吞吐只能靠加节点做数据并行，软件侧单机/双机已无空间**
> 8. **剩余优化项与建议排序**（C 重叠 / D MBS4→GBS2016 / E distributed-optimizer / 更大 DP32），每项给「预期收益 / 风险 / 是否值得做」
> 9. **复现命令**（脚本名 + 关键 env + ITERS=80 + 判据提取方法）
> 10. 附：数据溯源表（每个数字 → 哪个日志哪个文件哪一行）

> **④ 产出与归档**
> - 报告：`reports/report_pretrain_dualnode_throughput_zh.html`（**中文 HTML、单文件自包含、0 外链/0 CDN/0 `<script>`**，按常驻规程）。体积建议 ≥15KB，含表格 + 结论框。
> - 生成器：`run/gen_dualnode_throughput_report.py`（照 `run/gen_perf_report.py` / `run/gen_longctx_report.py` 的写法：数据写在脚本顶部字典里，脚本负责生成 HTML），**保证报告可重生成**。
> - 校验：生成后自检 `grep -c '<script' = 0`、0 个 `http` 外链、`HTMLParser` 标签配平。
> - `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` §「双机吞吐优化」补一行指针指向本报告。
> - `MEMORY_PRETRAIN_2B.md` 首部新块 + `run/daily-memories-2b/2026-10-25.md` 追加；commit 前缀 `pretrain report:`（只 add 本次动的文件，禁 `git add -A`）。

> **🚫 铁律**
> - **纯写作零 GPU**：写报告本身不占卡；TF 测完立刻释放 16 卡，**不许为写报告保占**。
> - 🚫 mock 数据的数字不许当扩展效率；🚫 不许改单机 e18 配方本身；🚫 未验证的机制解释标注「推测·未验证」。
> - 报告里 **不许出现 N/A 或空单元格**：没测就写「未测（原因）」。
> - 若 Task B 全部 TAG 在本轮内闭合，直接出 `rev2` 终版；若未闭合，`rev1` 也要能独立读懂（不依赖在测项）。

---

### 🆕 运维调整 · 2026-10-09（🔁 只用 `.29` + 改序：**① 对比基准 → ② Muon vs AdamW**；撤下 T1/T2/T3）· 用户直令 · **最高优先（覆盖下方 ⚗️Muon 与 🌙夜班 两块）**

> **用户令**：「pretrain 的实验都安排在 `.29`，`.12` 我会安排 vision 的实验。实验次序调一下：**1) 参数匹配对比基准；2) Muon vs AdamW（各自 1000 步，GBS=16，seq=4096，对比 loss）**。」

**① 机器改动**
- **所有 pretrain 实验一律在 `.29`**。🚫 **不要去 `.12`**（`.12` 归 vision）。
- ⇒ 撤销下方 ⚗️ 块里「占 `.12` + 登记 `GPU12_ALLOC.md`」的要求。

**② 次序**：**① 参数匹配对比基准**（`report_pretrain_baize_vs_dense_fair_zh.html`）**→ ② Muon vs AdamW**。

**③ Muon vs AdamW（用户给定口径，取代 ⚗️ 块的 Step 1）**
- **两臂各 1000 步 · GBS=16 · seq=4096 · bf16 · 同 seed**；**对比 loss 曲线**（附 grad-norm / 吞吐 / 显存）。
- 仍**先做接线三步核查**：本地 `megatron-core 0.16.1` 是否含 `muon.py`/`emerging_optimizers` → 缺则 `pip install emerging_optimizers`（环境隔离）→ `pretrain_launcher.py`/`recipe.py` 透传 `optimizer=muon`/`dist_muon`。**参数分组：2D 矩阵→Muon；1D/norm/embed/lm_head/SSM 标量→AdamW**。
- 先跑通 smoke（1 卡小步）再铺两臂；跑不通即如实报「卡在哪」，不熬夜 debug。

**④ 撤下「其它实验」**（用户：「其它实验有价值吗，我还没看出来」）
- 🚫 **T1 长上下文适配 / T2 等参 Dense 训练侧 / T3 R3 配比迁移 A/B 一律不做**，**留作 backlog**（理由：T3 landscape 平坦→大概率 null；T2 属论文润色；T1 服务 Stage (ii)、宜用 P-8 真基座）。
- ⇒ 撤销下方 🌙 块的全部内容。

**纪律**：🚫 不启动 P-8 · 🚫 不 kill watchdog · 分阶段 commit（`pretrain 对比:` / `pretrain Muon:`）。

---

### 🆕 运维更正 · 2026-10-09（✅ **NeMo/Megatron 支持 Muon** —— 更正上条「未接入」的旧判断）· 最高优先

> **更正**：上条「Muon 未接入 / 实现风险」引的是 `run/EXPERIMENTS.md` 里 **S3-03 的旧结论（已过时）**。**查官方原文后**（2026-10-09）：
> - **Megatron-Core** 有 `core/optimizer/muon.py`（shim → `emerging_optimizers`）+ `core/optimizer/emerging_optimizers` + `layer_wise_optimizer`（`dist_` 前缀 = layer-wise **distributed** Muon）。
> - **Megatron-Bridge（NeMo）** 有 Muon recipe：`bridge/recipes/utils/optimizer_utils.py`（含 `muon_extra_scale_factor` / `muon_scalar_optimizer`＝嵌入/偏置/norm 的标量优化器）。
> - **NVIDIA blog（2026-04-22）**：Muon 经 **Emerging-Optimizers** 库进入 Megatron-Core；**NeMo Megatron Bridge 26.02** 已实测 Muon 吞吐（GB300 上近 AdamW 持平）。
> ⇒ **探针改为「三步核查」，不再当"从零实现"**：① 本地 `megatron-core 0.16.1` 是否含 `muon.py`/`emerging_optimizers`；② `megatron.bridge` 版本是否有 Muon recipe（`optimizer_utils`）；③ **缺则 `pip install emerging_optimizers`**（注意环境隔离）；④ 在 `pretrain_launcher.py` + `mamba2_hybrid_2b/recipe.py` 透传 `optimizer=muon`/`dist_muon` + muon 参数。**跑通即进 A/B。**
> ℹ️ 官方对大规模 Muon 推荐 **layer-wise distributed optimizer**（整层分给各 DP rank，避免正交化时的额外通信）。

> 📦 2026-10-10 从 BAIZE_PRETRAIN_2B_TASK.md 搬入（两步运维指令均✅完成后归档，原文未改）。

---
# ARCHIVE — 历史运维指令（源自 BAIZE_PRETRAIN_2B_TASK.md）

> 运维 2026-10-05「任务书瘦身」时移出（**原文未改**，不改任何结论）。仅当需要查历史指令细节时再读。

### 🆕 运维答复 · 2026-10-05（**替代 ckpt ✅ 批准 / `sglang` ⚠️ 运维更正：先查 `https_proxy`，限时 30 分钟复测**）· **接下方 P-9.10 块**

> 收到第 100 次唤醒的「待运维确认」，逐条答复。**起跑时序不变**：P-9.9 约占到 **~15:15** → 之后 pretrain 拿 **GPU0–1** 起 P-9.10 实测、data 拿 **GPU2–7** 起配比，**同时开跑**。

**① 替代 ckpt：✅ 批准用 `p3_dense/iter_0005000` + `p3_hybrid/iter_0005000`**
- 你核实的「S3 原始 ckpt 已丢失」**属实，且是运维自己造成的**：`run/DISK_CLEANUP_INVENTORY.md` §6.3 记录，D-CLEAN-2（2026-10-03）删除 Round1/S 系列 27 个目录 ≈310G，**其中就含 `mamba2_2b_1000step` 与 `minicpm5_2b_1000step`**。**运维认账，不追责。**
- **不要求重训 S2/S3 1000 步**。理由：`p3_dense`（2.512B）/`p3_hybrid`（2.220B）是**同一对架构**、**P-3 控变量下同步训练 5000 步**、**两个 ckpt 都在**，比丢失的那对**更收敛、更可比**；重训只能换来与一个「已被判定为非生产栈」的旧数字的绝对可比性 ⇒ **不值当**。
- **但必须标注**（并按你写的办）：`⚠️ 权重口径切换：S3 = 1000 步 / 24.6M token（已删）→ P-3 = 5000 步 / 123M token`；**旧 10.3× 与本次数字不得直接相减**，两者并列、**各自标栈与权重**。
- ⚠️ **给运维的教训（已记）**：删 ckpt 前须查一遍「有哪些已发表的结论引用了它」。以后此类清理会先做引用检查。

**② `sglang`：⚠️ 运维更正 —— 不是「集群禁 pip」，是**那次 shell 没带 `https_proxy`**；**限时 30 分钟**按下面 A/B 复测一次，**不行再按原样放弃**
- 🔧 **撤回我上一条的根因判断**（「集群网络策略，换 `uv` / 指定版本 / `--no-deps` 都救不了」= **错的**）。`.29` 上**代理是有的**：`~/.bashrc:140` = `export https_proxy="http://172.19.92.25:13128"`（`:139` 是注释掉的旧 `.23`）。2026-10-04 RUN_ID 28 已实测（见 `run/ops/outbox.md`）：**外网「无 proxy = FAIL / 有 proxy = OK」**（`git ls-remote github`），**内网网关两种都 200**；`no_proxy`/`NO_PROXY` 均为空。
- 🧠 **`Errno 101 Network is unreachable` 的正确读法**：DNS 解析成功、但**公网 IP 直连被挡**（= 流量没走代理）。若是**代理本身**连不上，报的会是 **111 (ECONNREFUSED)** 或超时 ⇒ 你那次 `pip` 的 shell **env 里没有 `https_proxy`**。三个典型来源（自查是哪个）：① **非交互 shell 不读 `~/.bashrc`**；② 脚本沿用了给 cline 的 `env -u http_proxy -u https_proxy …` 剥 proxy 配方；③ 在 `chroot`/容器里跑、env 没带进去。
- ✅ **同机反向证据（关键）**：**harness 线在同一台 `.29` 上这两天 pip 装包一直是成功的** —— 做法就是**显式钉死**：`http_proxy=http://172.19.92.25:13128`、`https_proxy=同`、`PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/`（`run/harness/r1_eval.py:144-148`）；实测 **aliyun 镜像 200 ✅**，而官方 `pypi.org` / `files.pythonhosted.org` = `000`。⇒ **aliyun 镜像在这台机上通，只是必须走代理。**
- 🧪 **先做 30 分钟 A/B（原始输出贴进 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 的 P-9.10 ①）**：
  ```bash
  echo "proxy=[${https_proxy:-<empty>}]"; env | grep -i proxy || echo "(NO PROXY IN ENV)"
  curl -sS -m 10 -o /dev/null -w 'aliyun=%{http_code}\n' https://mirrors.aliyun.com/pypi/simple/            # 期望 200
  env -u https_proxy -u http_proxy -u HTTPS_PROXY -u HTTP_PROXY \
      curl -sS -m 10 -o /dev/null -w 'aliyun-noproxy=%{http_code}\n' https://mirrors.aliyun.com/pypi/simple/  # 期望 000/超时 ⇒ 证明「必须有 proxy」
  curl -sS -m 10 -o /dev/null -w 'nvidia=%{http_code}\n' https://pypi.nvidia.com/                            # cuda-tile 的源（200/403 都算可达）
  pip config list; pip download -v --no-deps -d /tmp/pipchk sglang 2>&1 | tail -15
  ```
- 🔧 **若「有 proxy = 200」成立**，用**显式钉死 + 隔离落点**装（不受父 shell env 影响；**不碰共享 env**）：
  ```bash
  export http_proxy=http://172.19.92.25:13128 https_proxy=http://172.19.92.25:13128
  python -m pip install -v --proxy http://172.19.92.25:13128 \
    --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    --extra-index-url https://pypi.nvidia.com/ \
    --target /nas_train/app.e0031982/sglang_libs sglang lm-eval
  ```
  - 🚫 **绝不要在共享 py310 env 里装**（**P-9.8 arm B 崩溃的元凶就是共享 env 被 `pip install -e` 污染**，sympy 导入链炸掉全部 8 个 rank）——**P-9.9 现在还在跑**，动 torch/transformers = 直接把在跑的训练搞崩。必须 `--target`（或 `python -m venv`）；起服时加 `PYTHONPATH=/nas_train/app.e0031982/sglang_libs`。
  - 🚫 **不要用 `--no-deps`**（把「装时的依赖问题」推成「跑时的缺包崩溃」）；版本冲突就按报错**逐个显式钉版本**。
- 🚦 **放弃判据（问完就停）**：A/B 里**「有 proxy」仍拿不到 200**，或 `pypi.nvidia.com` 也不可达 ⇒ **立即按原裁定放弃**，栈落 `mcore + CUDA-graph`（仍是「连它也失败才退回 `mcore 直驱（下界）`」）。
- ⏱ **不许阻塞主线**：A/B + 装栈是 **CPU/网络**活，与 GPU0–1 的 P-9.10 评测**并行**做；**P-9.10 到点照起**；装不成就在结论标题里如实写「SGLang 装不上 + 确切报错」。
- ⏳ 若拿到**离线 wheel** 或白名单开通，随时补测（记「待运维」即可）。

**③ 一处算术更正（请按这个口径出表）**
- 你在 §①-3 写的「dense `42KB → 42KB×32 = 1.34GB @128K`」**量纲错了**：`43,008 B` 是**每 token** 的 KV，必须**再乘 context 长度**。
- 正确口径（batch=1，bf16）：
  | 项 | 4K | 64K | 128K |
  |:--|--:|--:|--:|
  | dense KV（≈42 KB/token）×1 | **≈176 MB** | ≈2.8 GB | **≈5.6 GB** |
  | hybrid attn KV（≈4 KB/token）×1 | **≈16 MB** | ≈256 MB | ≈524 MB |
  | hybrid SSM 态（52 层） | **常数** | 常数 | 常数（**实测得出**） |
- ⇒ **比例仍是 32×（dense）vs 常数（SSM）**，你的 H3 方向不变；但**绝对数要以实测为准**。且这意味着 **batch=8 × 128K 时 dense KV ≈45 GB** —— **很可能正是 dense 的 OOM 边界**，请把它作为矩阵里的关键观测点（**OOM 就如实记 OOM**，🚫 不许偷偷降 context 不标注）。
- H3 阈值（hybrid ≤1.3× / dense ≥4× / 差距 ≥3×）**照原样不变**，以实测为准。

> ✅ 本块是对下方 P-9.10 块的**补充裁定**；其余条款（2 卡、预注册 H1–H4、诚实条款、不 kill 对方进程）**全部不变**。

### 🆕 运维指令 · 2026-10-05（**P-9.10：hybrid vs dense「生产级推理栈 + 长上下文」对比评测 —— 只占 2 卡，与 data 分卡并行**）⭐ 高优先 · **已批准**

> **用户拍板（2026-10-05）**：「**给 pretrain 补一个对比评测任务**（要 GPU 所以该 pretrain 做），但**不需要 8 张卡**；**让它和 data 协调一下 —— pretrain 做对比评测时，data 可以同时做数据配比试验**。」
>
> **为什么要补**：现在论文/报告里 hybrid vs dense 的 **decode 10.3×** 是 **mcore 直驱（无 CUDA graph / flashinfer）** 测出来的 —— profiler 已定位为 **CPU launch bound**（dense `Self CPU ≈620 ms` vs `Self CUDA 4.05 ms`）⇒ **10.3× 是「同一劣化栈下的相对值」，不能当生产解码优势用**。
> 而我们**真正的结构优势在长上下文**（dense 的 KV 随 context 线性增长，hybrid 只有 4/56 层有增长 KV）—— **这个到今天还没有一个实测数字**。**本项就是去补它。**

#### ① 卡的分配（**本项铁律**）
- **P-9.10 只用 2 张卡**：`CUDA_VISIBLE_DEVICES=0,1`（`.29`）。
- **`.29` GPU2–7（6 卡）归 data 跑配比实验** —— 账本 = **`run/GPU29_ALLOC.md`**（**双方都要用它**，申请也写在那里）。
- ⏳ **起跑前置**：**先等 P-9.8 arm B(FP8) 跑完**（它现在占满 8 卡，ETA ~09:49）→ 出裁定 → 再动卡。
- 📢 **你要 >2 卡时**（如 **P-9.9 的 armB 复现/拉长**（大概率仍是 TP4·8 卡）、**P-9.5** 需原 TP1·DP8 配置、**P-6②** 想并行多 ckpt、或 **P-8**）：**先在 `run/GPU29_ALLOC.md` 的「申请区」写一行**（哪几张/多久/为什么），**等 data 在臂边界让卡**；🚫 **不抢跑、不 kill 对方进程**。
  - 💡 **能降到 ≤2 卡就别申请**（例如 P-9.9 的 recipe 查证是纯 CPU；只有真跑 armB 才占卡）。

#### ② 做什么（两步；**先做①，便宜**）

**① 栈对齐 —— 把「测量栈」从下界抬到生产级**
1. **再试装 `sglang`** —— **照运维区最上方 2026-10-05 的更正后 ② 执行**（先查 `https_proxy` → 显式带 `--proxy` + `--target` 安装；🚫 共享 env、🚫 `--no-deps`）→ **记录确切报错（原始输出）**。
2. **同时准备 fallback**：**mcore 直驱 + CUDA graph（或 `torch.compile`）** —— 直接打掉逐层 launch 开销。
3. **栈优先级**（能到哪级用哪级，**并写进结论标题**）：
   `SGLang`（`nemotron_h` / Llama）> `mcore + CUDA-graph` > `mcore 直驱（下界）`。
   ⚠️ **只到「下界」时**：必须**额外给出 CPU/GPU 分解**（`Self CPU` vs `Self CUDA`）推出 **GPU-only 上界**（dense ≈250 tok/s），并写清「**这是下界，不是生产数**」。

**② 对比评测矩阵（核心）**
- **两个模型**：`MiniCPM5-2B`（dense）vs `Mamba2-hybrid 2B` —— **沿用架构轮那一对 ckpt**（`code/BaiZe-ISEDA2027/nemo_experiments/{minicpm5,mamba2}_2b_1000step/checkpoints/iter_0001000`；代码 `code/BaiZe-ISEDA2027/`：`infer_benchmark.py` / `mamba2_hybrid_2b/` / `minicpm5_2b/`），**同一份权重、只换栈与上下文长度** ⇒ 与旧 10.3× 直接可比。
  （⚠️ **先核验 ckpt 是否还在**；不在 → 如实报告并说明替代方案，🚫 不许换权重还不标注。）
- **context ∈ {4K, 16K, 64K, 128K}**（至少到 64K；128K 视显存）
- **batch ∈ {1, 8}**（batch=8 才反映服务吞吐；OOM 就降到可行值并写明降到了多少）
- **每格记录**：`prefill 延迟 & tok/s` · `decode tok/s & TPOT` · `峰值显存` · **缓存/状态字节数随 context 的增长曲线**
- **每格重复 ≥3 次取中位 + 记方差**；每次测量前核验本卡无其它进程。
- 🔎 **顺手用 `cimi_search`/`cimi_fetch` 核实两个口径**（一手优先）：① **Nemotron-H / hybrid-SSM 长上下文 decode 的公开数据**；② **MLA / GQA 的 KV 字节-per-token 公式**（给 H3 的口径背书）。**核不到就写「未核实」。**

#### ③ 预注册判据（先定后测，🚫 不许事后改）

| # | 假设 | 判据 |
|:--|:--|:--|
| **H1** | hybrid 的解码优势在**生产栈**下依然存在 | 各 context 下 `hybrid decode tok/s ≥ dense × 1.5` |
| **H2** | 优势**随 context 增大而变大**（=结构性的，不是 launch 伪影） | `ratio(128K) ≥ ratio(4K)`，且 4K→128K **单调不降** |
| **H3** | hybrid 的**缓存/状态内存不随 context 线性增长** | hybrid 4K→128K 内存增长 **≤1.3×**；同期 dense **≥4×**（差距 **≥3×**） |
| **H4** | prefill 没被牺牲 | `hybrid prefill 延迟 ≤ dense × 1.2` |

**裁定**
- **H1+H2 过** → 「**hybrid 的解码优势是结构性的 → 可进论文/成本叙事**」；
- **H1 过、H2 不过** → 「**优势只在短上下文**（属部分 launch 伪影）」→ 论文按此**保守表述**；
- **H1 不过** → **如实写负结果**，并**回收旧「10.3×」的表述**（改为「mcore 直驱下界口径」）。
- ⚠️ **诚实条款**：**栈名必须出现在结论标题里**；**下界不许当生产数**；SGLang 装不上就如实写「装不上 + 确切报错」。

#### ④ 边界与产出
- **铁律**：🚫 **不改 P-5b recipe、不回训、不产模型**（本项**纯推理**）；🚫 不 kill 任何进程（含 watchdog 与 data 的配比臂）。
- ⚠️ **口径声明**：训练 seq 是 **4094** ⇒ 在 16K/64K/128K 上测的是**位置外推下的速度/显存**，**不是质量** —— 报告里必须写明。
- **📌 产出**：`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新增 **P-9.10** 节（**逐格原始输出 + 命令 + 路径 + 栈名**）；`BAIZE_2B_ARCH_RESULT.html` 的 decode caveat 按新结论更新（**若与旧结论冲突：两个数都留，各自标栈**）；`MEMORY_PRETRAIN_2B.md` 记一行。
- **成本**：装栈 + 转 HF ≈1–3h（多为 CPU）· 评测 ≈1–3h ⇒ **≤半天**。
- 🚦 **与既有队列的关系**：P-9.8 裁定 → **P-9.10（本块，2 卡）** → P-9.5 / P-6② **在这 2 卡上穿插**（各 1 卡，与 data 的 6 卡不冲突）；**P-8 仍暂缓**（等 base 下满 + 配比定稿）。

> ✅ **本区块生效即视为已批准** —— 无需再等拍板；**卡的分区/申请见 `run/GPU29_ALLOC.md`，超出 2 卡必须先申请。**

### 🆕 运维指令 · 2026-10-05（**P-9.8 裁定修订：瞬时 spike 不构成否决 —— 给 FP8 更多机会**）⭐ 高优先 · **已批准**

> **用户立场（2026-10-05）**：**DeepSeek-V3 已在 FP8 上跑通并公开** —— 这是**无法翻盘的事实** ⇒ **不能让一次「瞬时不一致」就否决 FP8**，**必须给 FP8 更多机会证明自己**。
> **运维复核你的数据**：iter660–750 的差异是**瞬时 spike**（峰值 5.11%@iter710），**iter770+ 已恢复 ≤1%**（870=0.73%）⇒ 判据 #4 的 **4.36% 是单点极端值**，**用它一票否决证据不足**。

**① 裁定规则修订（先定后测，🚫 不许事后改）**
- **#4 改为「持续性」判据**：一次偏离**只要在 ≤100 步内回落到 ≤1%**，**不计为 FAIL**（记为 `spike-then-recovered`）；**只有「连续 ≥100 步维持在 >2%」或「持续恶化」才判 FAIL**。
- ⇒ **本次 P-9.8 armB 裁定修订为**：**#1/#2/#3 PASS + #4 = spike-then-recovered** ⇒ **「FP8 长程与 bf16 一致 → 可用于 P-8」**（P-8 若用 FP8，**前 500 步仍照原令密切监控 loss/nan/skip**）。
- ⚠️ **原样保留并如实写进 EXPERIMENTS**：spike 的位置/幅度/**恢复步数**、以及原始逐 100 步数据。**🚫 不许把 spike 抹掉。**

**② 给 FP8 更多机会（新增 P-9.9，按序执行）**
1. **换 seed 复现**：armB **同配置、`seed 4321`、1000 步** → 若 **spike 不复现** ⇒ 判「随机数值波动」；若**复现** ⇒ 记为 FP8 的已知现象（写进坦白条款）。
2. **拉长到 ≥2000 步**：看后段是否**持续**一致 —— 这是**直接对齐 DeepSeek-V3 结论**的最有力证据。
3. **📌 查并试「更细粒度的 FP8 recipe」**（重点）：**DeepSeek-V3 用的是 fine-grained（按块，128×128）缩放**，而我们现在用的是 **`bf16_with_fp8_delayed_scaling_mixed`（delayed / per-tensor 口径）** —— **数值上更弱**，很可能正是 spike 的来源。
   → **查 `transformer_engine` / `megatron-core 0.16.1` 实际暴露了哪些 FP8 recipe**（`fp8_*` 枚举、blockwise / `cs`、`fp8_mlp` / `fp8_attn` 子项）；**若有 fine-grained → 同配置重跑 armB**，看 **spike 是否消失** 且 **s 是否仍 >1.05**。
4. 全部跑完 → **合成「FP8 在本模型上的可用性」结论**（含 **recipe 对比表**）。

> 🔎 **请用你的新能力（`cimi_search`/`cimi_fetch`）直接读 DeepSeek-V3 论文的 FP8 章节**（fine-grained quantization 的做法、哪些算子保留 bf16/高精度），把「**我们该用哪个 recipe**」落成**一手引用**。

**③ 铁律不变**：🚫 不改 P-5b recipe、不回训；不存 ckpt（`--save-interval 0`）；🚫 绝不 kill watchdog loop。

### 🆕 运维指令 · 2026-10-05（✅ **你已具备联网检索能力（MCP `cimi_search`/`cimi_fetch`）—— 做手头任务时用起来**）

> **已开通（运维 2026-10-05 实测）**：`.29:8090` 的 `eda_fastmcp` SSE MCP 已接入 cline；`cline config mcp` 显示 **`pyAether_MCP_server [sse]`**，**本线已实测 `cimi_search` 成功（rc=0）**。
> **两个工具**：**`cimi_search`**（联网搜索 → 标题 + 摘要 + URL）· **`cimi_fetch`**（抓网页正文 → 用来核实数字）。
> ⇒ **做手头任务时顺手用，不为它专门开一轮**。对本线最有用的两处：
> ① **核实关键论文的原始数字**（Chinchilla 20:1 · μP/Tensor Programs V · **Data Mixing Laws** · WSD · Mamba-2 · FP8）→ 作为 **P-8 决策**与「**reduced-horizon proxy search**」支柱的**文献锚点**；
> ② 查 **Megatron-Core / transformer_engine / mamba-ssm** 的**已知问题与官方建议**（例：尾存 ckpt 的 `save_state_dict_async_plan` gather OOM、`CUDA_DEVICE_MAX_CONNECTIONS=1`）→ 印证你 P-9.6 的实测。
> **🔒 证据纪律**：一手优先（论文原文 / arXiv / 官方仓库 / 官方榜单）；**引用必须给 URL + 年份**；二手博客只能作线索并标「二手·未核」；**核不到就写「未核实」——🚫 不许凭记忆编数字**。
> **🚫 边界**：不改下载白名单 · 不占 GPU · 不下大文件（`cimi_fetch` 只取网页正文）· **不改论文 `.tex`（论文仍冻结中）**。若工具不可用 → 先 `cline config mcp` 看 `pyAether_MCP_server [sse]` 是否在，**如实报告**。

### 🆕 运维指令 · 2026-10-04（**P-9.8：bf16 vs FP8 长程一致性 A/B（≥1000 步）—— 填满凌晨空窗**）⭐ 高优先 · **已批准**

> **用户拍板（2026-10-04 深夜）**：「**队列照跑（P-9.5 → P-6②）+ 追加 P-9.8**」。
> **为什么要做**：`P-9.6②` 自己标注的风险尚未关闭 ——
> > ⚠️ **长跑 loss 质量待验**：**60 步短测 loss 持平 ≠ 长跑收敛一致**；若 P-8 采用 FP8，前 500 步须密切监控 loss/nan/skip，与 bf16 对照。
> 而 **P-8 的推荐候选A 正是 FP8**（`TP4·SP·MBS8·seq8192·FP8·MAX_CONN=1`，235K tok/s）→ **不关掉这个风险就上 P-8 会踩雷**。
> **窗口**：`P-9.7` 定稿（~22:40）后起；本线队列 + 本项合计用满凌晨空窗。

**执行顺序（本轮）**
**P-9.7 定稿**（取 last-100 均值，按已预注册判据）→ **P-9.5 复跑**（修 `on_trace_ready` 回调 / 或回落；~0.5h）→ **P-9.8（本块，长杆，先跑）** → **P-6②**（能力 vs token scaling + 外推）→ （**P-8 仍暂缓**，等 base 下满 + 配比定稿）。

> 📌 **为什么 P-9.8 排在 P-6② 之前**：P-9.8 是**长杆（≈11h）**、必须吃满夜间窗口；P-6② 是**纯推理**（lm_eval）、白天也能低成本补，且不依赖 P-9.8。

---

#### P-9.8 规格（控变量：**只变精度 bf16 vs FP8**）

| # | 项 | 值 |
|:--|:--|:--|
| 1 | 载体（= **P-9.6② 的 FP8 转正点**） | **`TP4 · SP-on · MBS8 · seq8192`**（M=65536）；**`GBS=512`**（维持 §P-9.0 不变量 ≈4.19M tok/步）|
| 2 | 臂 A（对照） | **bf16**（基线 22.16 s/iter ≈189K tok/s，P-9.6② 同点实测）|
| 3 | 臂 B（待测） | **FP8**：`--precision bf16_with_fp8_delayed_scaling_mixed`（P-9.6② 实测 17.86 s/iter，s=1.24）|
| 4 | 两臂共同 | **`CUDA_DEVICE_MAX_CONNECTIONS=1`**（沿用 P-9.6② A 点结论：比默认快 2.3%）· seed 1234 · WSD/1e-3 不变 · `--save-interval 0`（**不存 ckpt**）|
| 5 | **步数** | **各 1000 步** |
| 6 | 打点 | **每 100 步**记录：`loss` · `grad norm` · `nan` · `skipped`（+ 末段 s/iter、tok/s、峰值显存、TFLOP/s/GPU）|
| 7 | 成本 | bf16 1000×22.16s ≈ **6.2h** + FP8 1000×17.86s ≈ **5.0h** → **合计 ≈11h**（⚠️ 略超 ~10h 窗口 → 见「窗口纪律」）|

**🔒 预注册判据（先定后测，🚫 不许事后改）** —— 四条**全过**才算「FP8 长程与 bf16 一致」：

| # | 指标 | 阈值 |
|:--|:--|:--|
| 1 | **同 step loss 相对差**（末段 100 步均值） | **≤ 1%** |
| 2 | **nan / skipped** | **= 0**（两臂全程）|
| 3 | **grad-norm 漂移**（末段 vs 首段的中位/分位） | **≤ 10%** |
| 4 | **每 100 步 loss 曲线最大偏离** | **≤ 2%** |

**裁定**：**四条全过** → 「**FP8 长程可用于 P-8**」→ 写入 P-8 配置建议（候选A 保持 FP8）；**任一不过** → 「**FP8 长程不可用于 P-8**」→ **P-8 定 bf16**（除非运维另批）。

**窗口纪律**
- ⏱ **若 08:30 仍未跑完 → 截到已完成步数、如实报告**（`🚫 不硬撑、不挤占 P-6②`）；并注明「未达 1000 步，判据按已跑段给出**暂定**结论」。
- 🛑 **不与其它重 I/O 抢卡**（`.12` vision 侧 R11-G/R11-H 同时在跑 → 只用到 `.29` 本机 8 卡）。

**铁律**：🚫 **不改 P-5b recipe、不回训**；本项**不存 ckpt、不产出模型**，结论**只用于 P-8 配置决策**；`🚫 绝不 kill watchdog loop`。

**📌 报告要求**：公平表（两臂 `s/iter` / `tok/s` / 峰值显存 / `TFLOP/s/GPU`）+ **逐 100 步 loss/nan/skip/grad-norm 原始输出** + 结论贴**命令 + 原始输出 + 路径**；若为负结果**照实写**。

> ✅ **本区块生效即视为已批准** —— 承接方**无需再等拍板**，按上述顺序执行。



> **动机（运维 2026-10-04）**：P-9.6 得出 **A1（TP1·DP8·MBS2·seq4096·bf16）= 249K tok/s 速度最优**，**但这是 60 步短测**；而 **P-9.1 早测同配置只有 218K**（差 **14%**，当时标注「疑早测有争用」）。
> ⇒ **拿一个"争用较少时刻"的短测数字去定 P-8 的吞吐预期有风险** → **必须先确认 A1 的稳态吞吐**。

**做什么**
- **配置固定为 A1**：`seq=4096 / GBS=1024 / TP1·DP8 / MBS=2 / bf16`（= P-9.1 的胜出点）；
- 跑 **≥1000 步**（`--save-interval 0` **不存 ckpt**，避免尾部 save gather 干扰）；
- 取 **last 100 步稳态均值** 的 `s/iter` 与 `tok/s`；
- 同时报：**GPU 利用率（TFLOP/s/GPU）**、**峰值显存**、**有无其它进程争用**（`nvidia-smi` + `pgrep -af` 核查同机是否有别的训练/下载在抢）。

**🔒 预注册判据（先定后测）**

| 稳态 tok/s | 裁定 |
|:--|:--|
| **≥ 240K** | ✅ **确认 249K 可信** → P-8 按 A1 定（吞吐优先） |
| **218K – 240K** | ⚠️ 取**实测稳态值**作为 P-8 基线，并**注明短测不可用** |
| **< 218K** | ❌ 短测有系统性偏差 → **一律以长跑为准** |

**成本**：1000 步 × ~17–20 s ≈ **5–6 h**（GPU 独占，避免与 P-9.6 并行）。
**优先级**：**排在 P-9.6 之后、P-9.5 / P-6② 之前**（它是 P-8 决策的**直接输入**）。
**铁律**：不改 recipe、不回训、不存 ckpt —— **只测吞吐**。


### 🆕 运维指令 · 2026-10-04（**P-9.6：先在 bf16 下找到【训练速度最优】配置，再在该点测 FP8 是否有收益**）⭐ 最高优先

> **用户观察（2026-10-04）**：当前最好配置 **④ TP2·SP·MBS4 峰值显存仅 51.0 G / 80 G** → **余量 ~29 G** ⇒ **MBS 应该还能往上加**，「训练速度还有潜力可挖」。
> **用户指定方法（两步法，必须照做）**：**① 先在 bf16 配置下找训练速度最优的配置 → ② 再在这个配置下测 FP8 是否有收益。**

**⚠️ 为什么必须先抬 M（关键背景，来自你自己 P-9.4 的实测）**

| 事实 | 数据 |
|:--|:--|
| FP8 微基准交叉点 | **M ≈ 30–32K**（**不是 16K**）：`s=0.58/0.71/0.90/1.14/1.31` @ M=4096/8192/**16384**/32768/65536 |
| 当前 ④ 的 M | **16384** → 未加权 **s=0.90（仍倒挂）** |
| P-9.4 端到端（M=16384） | **A(SP-off) s≈1.01 持平；B(SP-on) 反慢 ~15%** |

⇒ **在 M=16384 上测 FP8 本来就是「不公平的考场」**。要真正回答「FP8 有没有收益」，**必须先找到一个 M ≥ 32768 的配置**。

**⭐ 抬 M 的两个杠杆（`M = MBS × seq`）**
1. **抬 MBS**：`4 → 8 → 16`（受显存限制；④ 的 51 G → MBS=8 预计 >75 G，可能 OOM，可配 **TP4** 换显存）
2. **抬 seq**（⭐ **推荐先试**）：**保持「每步 ≈4.19M token」不变量** → `seq 8192→GBS 512` · `seq 16384→GBS 256`
   → **`MBS=4 × seq 8192 = M=32768` 直接越过交叉点**，且**顺带拿到长上下文能力**（对 P-8 是双重收益）

#### ① 步骤一：bf16「训练速度最优」配置搜索（先做）

- **维度**：`{TP 1 / 2 / 4} × {SP on / off} × MBS {4, 8, 16} × seq {4096, 8192, 16384}`，**每点都保持 `GBS × seq ≈ 4.19M`**（不变量，见 §1）；
- **每点 60 步短测**，报：**`s/iter` · `tok/s` · 峰值显存(max/8) · TFLOP/s/GPU · OOM?**
- **判据（预注册）**：**吞吐最优** 且 **峰值显存 ≤ 72 G**（留 ≥8 G 安全余量，避免长跑 OOM）；
- **成本控制**：点数 **≤ 20**（单点 ≈20–30 min → 总 ≈8–10 h）；**按吞吐可能性排序先扫**（先 seq 8192/16384 的 TP2·SP on/off·MBS4，再 MBS 8/16，再 TP4）。
- 🚫 **不改 P-5b recipe、不回训**。

#### ② 步骤二：在【步骤一的最优点】上测 FP8

- 在该点做 **bf16 vs FP8 端到端**（`--precision bf16_with_fp8_delayed_scaling_mixed`，各 60 步，同 MBS/seq/GBS/TP/SP）；
- ⚠️ **必带对照**：P-9.4 发现 **B(SP-on) 下 FP8 反慢 ~15%**，疑为 **FP8 amax/delayed-scaling allreduce 与 SP allreduce 叠加** → **本轮务必设 `CUDA_DEVICE_MAX_CONNECTIONS=1` 做 A/B 对照**（此前建议未设）；
- **🔒 预注册判据（先定后测）**：

| 情形 | 裁定 |
|:--|:--|
| 最优点 **M ≥ 32768** 且 FP8 **s > 1.05** | ✅ **FP8 转正** → 把该点写入 P-8 配置建议 |
| 最优点 **M ≥ 32768** 但 FP8 **s ≤ 1.05** | ❌ **FP8 在本 model 上不转正** → **定稿 bf16**，把「不转正」作为**正式结论入库** |
| 最优点 **M < 32768** | ⚠️ 标注「**未给 FP8 公平机会**」→ **补一个 M≥32K 的点**再测一次 |

- **📌 报告要求**：参数量 + **token/步** + `s/iter` + **峰值显存** + TFLOP/s/GPU；结论贴**命令 + 原始输出 + 路径**。

#### ③ 优先级与排期
- **本指令 = 最高优先**，并**吸收 P-9.3（seq 多点）**（把"找最快点"与"seq 扫描"合并为一次扫描）；
- 顺序：**P-9.6① → P-9.6② → P-9.5（profiling）→ P-6② → 定 P-8**；
- **P-8 仍暂缓**（等 base 下满 + 配比定稿）。

#### ④ ✅ 运维确认（2026-10-04 12:30）—— **以「seq 轴」为主轴，不要单纯堆 MBS**

> 用户**赞同**下述判断并**批准按此安排 P-9 实验**：
> **「最优点大概率是『把 seq 抬到 8192/16384 + SP on + 合适 MBS』这个方向，而不是单纯堆 MBS」**——因为 MBS 1→2 的 +59% 主要来自**少了一半 grad-accum**，但 **TP2 的通信开销已在 ④ 上吃掉 ~4%**；而**抬 seq 一次给两样**：把 `M` 推过 FP8 交叉点（30–32K）**且**白拿长上下文能力。

**⭐ 建议的扫描顺序（每点 60 步，均守 `GBS×seq ≈ 4.19M` 不变量；本表可直接照跑）**

| 序 | seq | GBS | TP | SP | MBS | **M** | 作用 |
|:--|--:|--:|:--|:--|--:|--:|:--|
| **1** | **8192** | 512 | 2 | **on** | 4 | **32768** | 🎯 **运维预测的最优点**（越过 FP8 交叉点） |
| 2 | 8192 | 512 | 2 | off | 4 | 32768 | SP 对照（同 M） |
| 3 | 16384 | 256 | 2 | on | 4 | 65536 | 更远；看 M 是否还涨吞吐 |
| 4 | 16384 | 256 | 2 | off | 4 | 65536 | SP 对照 |
| 5 | 4096 | 1024 | 2 | on | **8** | 32768 | **MBS 轴对照**（同样到 M=32768，但靠堆 MBS） |
| 6 | 4096 | 1024 | 2 | off | 8 | 32768 | MBS/SP 交叉对照 |
| 7 | 4096 | 1024 | 2 | on | **16** | 65536 | 上探（**预期 OOM**，OOM 也如实记） |
| 8 | 8192 | 512 | **4** | on | 8 | 65536 | TP4 换显存（若 5/7 OOM 才做） |
| 9 | 8192 | 512 | **1** | off | 2 | 16384 | TP1 抬 seq 对照（vs P-9.1 的 TP1·MBS2·seq4096） |
| 10 | 4096 | 1024 | 2 | on | 4 | 16384 | **P-9.2 ④ 基线**（必跑，用于同机同口径归一） |

- **可提前剪枝**：若第 1/2 点的 **峰值显存 > 72 G** 或 **OOM** → 跳到 3/4（seq 更容易）与 5/6；若第 1 点**吞吐已优于 210K 基线** → **优先扩 seq**（3/4），**不必**再堆 MBS。
- **裁量**：**总点数 ≤10**；若 8 h 内跑不完 → **保序**（1→2→5→3→10→…），宁少勿乱。
- **步骤二**：在步骤一的**最优点**（预期 = 第 1 点）上做 bf16 vs FP8（判据见 ②，**必带 `CUDA_DEVICE_MAX_CONNECTIONS=1` A/B**）。



### ✅ 更正 · 2026-10-04（**上面那条「救 ops 中继」的 URGENT 已作废 · 无需执行**）

> **中继已自行恢复**（`.last_run_id` 已推进到 36，09:57 后正常产出）→ **上面那条 URGENT 请直接跳过**，**不要再 `pkill`/重启 relay**（避免误伤正在执行的任务）。
> ⏱ 若你**已经**执行过重启、且 `pgrep -af ops_relay.sh` **恰好 1 条** → 也没问题，如实记一行即可。
> **回到常规：继续 P-9.2 巡检。**

### 🚨 运维指令 · 2026-10-04（**最高优先 · 紧急但轻量 ≈30 秒：请帮忙恢复 ops 中继**）

> **为什么找你**：`run/ops/ops_relay.sh` 是**外部运维唯一的远程通道**（运维**无法 SSH 登录**，只能靠你）。它现在被一个**跑飞的进程卡住**了（`.last_run_id` 停住、不再产出）。
> **耗时**：≈ **30 秒** · **不占 GPU** · **不改任何训练 recipe** · **不删任何数据**。
> ⏱ **本条优先于 P-9**（但它只需半分钟，做完立刻回到 P-9.2）。

**请依次执行，并贴【原始输出】**：

```bash
# 1) 现状
pgrep -af 'ops_relay.sh' | cut -c1-120
echo '--- 跑飞的残留（ops 的 grep / fuser）---'
pgrep -af 'grep -rl|fuser -v /nas_train' | cut -c1-120

# 2) 杀掉跑飞的残留（杀不到就跳过，无副作用）
pkill -f 'grep -rl .*stage_1.5_mid_training' 2>/dev/null
pkill -f 'fuser -v /nas_train' 2>/dev/null
sleep 2

# 3) 重启中继（先 pull 再起；setsid 脱离进程组防工具超时误杀）
pkill -f ops_relay.sh 2>/dev/null
sleep 2
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
git pull --rebase
setsid bash ops_relay.sh > /tmp/baize_ops_relay.log 2>&1 < /dev/null &
sleep 6

# 4) 校验 —— 必须【恰好 1 个】relay
pgrep -af ops_relay.sh | cut -c1-120
echo '--- relay 日志尾 ---'; tail -6 /tmp/baize_ops_relay.log
```

**判据（验收）**：`pgrep -af ops_relay.sh` **恰好 1 条**，且 `/tmp/baize_ops_relay.log` 出现轮询行（如 `poll…`/`run …`）。

**🚫 三条红线（务必遵守）**：
1. **不要** `pkill` 你自己（`baize_pretrain_loop.sh`）、也不要动 harness 的 loop；
2. **不要**动 GPU 上正在跑的 **P-9.2**（`baize_p9_tpsp_scan.sh`）；
3. **不要删任何数据** —— 中继恢复后**它会自动接手**待执行的磁盘清理（RUN_ID 36），**你完全不需要做删除动作**。

**回报**：把上述 4 步的**原始输出**（可 `cut -c1-140`）写进 `MEMORY_PRETRAIN_2B.md` 的**底部流水一行**，然后**继续 P-9.2 巡检**。若中继仍起不来，同上格式报告失败点即可。


### 🆕 运维指令 · 2026-10-03（新增 **P-9**，**排在 P-5b 之后、P-6② 之前** —— ⏱ **尽早跑，🚫 不得后置到 P-6② 之后**）

> 🚫 **铁律不变**：**绝不打断正在跑的 P-5b**（改 MBS/精度会使该 long-run recipe 失效、loss 曲线断裂）。
> **P-9 只在 P-5b 跑完后的空窗执行**；**P-8 仍按原令暂缓**（等 base 下满 + 配比实验定稿）。

**背景（运维 2026-10-03 提出两点，必须捆绑验证）**：
1. **MBS 太小**：当前 `--micro-batch-size 1`（GBS=1024 / DP8 → **每步 128 次 grad-accum**）；实测 8 卡各 **~39GB / 80GB**，**显存余量过半**。运维问：**MBS 1→2（或更高）能否提速？**
2. **FP8 在 Xmodel-2.5 上凭「Megatron-LM + TransformerEngine」拿到 +30%** —— 与本线 P-4R「单算子 `s=0.65` 倒挂」**冲突**，运维要求**在正确口径下复评**。

**机制（运维分析，供你验证，不许直接抄结论）**：P-4R 的 `s=0.65` 是 **每 GEMM 的 M = seq** 下测的（访存受限）。**FP8 要 `s>1` 需 `M ≳ 16K`**。而 **M ≈ MBS × seq**：
- `seq=4096`：MBS=1 → M≈4096（倒挂）· MBS=2 → M≈8192（仍 <16K）· **MBS=4 → M≈16384 ≈ 交叉点** · MBS=8 → M≈32768（`s→1.34` 饱和区）
- `seq=8192`：MBS=1 → M≈8192 · **MBS=2 → M≈16384 ≈ 交叉点**（长上下文下**更少 MBS** 即进 FP8 收益区）
→ **MBS 与 FP8 是同一件事**：**先把 MBS 抬上去（提高 M），FP8 才可能转正。**

#### P-9.0 口径与不变量（**P-9 与 P-8 都必须遵守**）
- ✅ **seq 今后统一 `4096`**（P-9 / P-8）；`seq=4094` **只保留在正在跑的 P-5b（🚫 不动、不参与对比）**。
- ⭐ **不变量：每步 ≈ 4M token**（`GBS × seq ≈ 4.0M`；**SLM 公认口径**，决定总体训练速度）：`4096→GBS1024` · `8192→512` · `16384→256` · `2048→2048`（均 **4.19M**）。**改 seq 必须同步改 GBS。**
- 📌 **总步数 = 总训练 token ÷ 4M —— 与 seq 无关** → **LR 计划（按步数）语义不变**，loss-vs-token 跨 seq 可比；seq 只改 **每步样本数 / 总序列数**，代价只落在 **每步耗时 / 显存**。
- 其余固定：**WSD 5%-85%-10% / LR=1e-3 / seed=1234 / 8×H100（`10.239.2.29`）/ TP1·DP8**。
- **P-9 = 吞吐/显存基准**（短测、不存 ckpt）；**不改 P-5b recipe**，结论只用于 **P-8**。

#### P-9 分节索引（执行顺序；⏱ **尽早**，🚫 **不得后置到 P-6② 之后**）
| 节 | 内容 |
|:--|:--|
| **P-9.1** | MBS 扫描（问题①） |
| **P-9.2** | 其它可变参数扫描（**仅已暴露开关** A–D） |
| **P-9.3** | seq 多点扫描 + 预注册预测/判据 |
| **P-9.4** | FP8 复评（⚠️ **按 M 扫**，问题②） |
| **P-9.5** | profiling / 瓶颈诊断（问题③） |
| **P-9.6** | 结论：P-8 推荐配置 |
| **P-9.7** | A1 稳态吞吐确认（≥1000 步长跑，取 last-100 均值） |
| **P-9.8** | 🆕 **bf16 vs FP8 长程一致性 A/B**（各 1000 步；见最上方（七）） |

**优先级覆盖**：**P-5b（自然跑完）> P-9 > P-9.8 > P-6② > P-8（暂缓）**。

#### P-9.1 MBS 吞吐/显存扫描（问题①）
- `MBS ∈ {1,2,4,8}` × **短测 ~60 步**（bf16、不存 ckpt）@ `seq=4096 / GBS=1024`；记 **s/iter、tok/s、峰值显存、是否 OOM**。
- 产出：`MBS → 吞吐/显存` 表 + **最大可行 MBS**。

#### P-9.2 其它可变参数扫描 —— **只用「已暴露的开关」**（⏱ 运维 2026-10-03 定）

> 🚩 **前置事实（agent 的 P-9 非 GPU 预研已查明，2026-10-03 #37）**：
> **`launcher` 只暴露 `--micro-batch-size` / `--tensor-parallel` / `--sequence-parallel` / `--seq-length` / `--precision`**（+ 口径项 `--global-batch-size` / `--train-iters`）。
> 👉 **P-9 只用这些**；**🚫 不改 `recipe`**。每次**只动一个变量**（短测 ~50–100 步，bf16，记 **s/iter + 峰值显存 + tok/s**）；**全程维持 4M/步**。

| 类 | 变量（**已暴露**） | 试什么 | 预期作用 |
|:--|:--|:--|:--|
| **A** | `--micro-batch-size`（= **P-9.1**） | 1→2/4/8 | 减 128 段累积 + **抬高 M（FP8 的 M）** |
| **B** | `--tensor-parallel` × `--sequence-parallel` | TP1·DP8 vs TP2·DP4；SP on/off | 改每卡形状 / 通信 |
| **C** | `--seq-length`（→ **P-9.3** 多点扫描） | 2048 / 4096 / 8192 / 16384（**GBS 同步**） | 长上下文档价 |
| **D** | `--precision`（→ **P-9.4** FP8 复评） | bf16 vs fp8 | 精度轴 |

**🚫 本阶段不做（需改 `recipe` → 已冻结）**：
`--recompute-*` · `--overlap-grad-reduce` / `--overlap-param-gather` / `--use-distributed-optimizer` · `--num-workers` / `--dataloader-type` · `--attention-backend`。

> 📌 **记录在案（不在 P-9 内做）**：其中 **通信重叠类** 理论收益最大 —— P-4 profile 显示 **NCCL 占 GPU 自耗时 41.7%（最大单项）**。若 **P-9d 的 profiling 证实它仍是瓶颈** → **另开任务、经运维批准后再改 recipe**。

- 🚫 **不要一次改多个**（否则无法归因）；**不改 P-5b**；每条结论**贴 flag + 命令 + s/iter 原始输出**。
- **产出**：`变量 → Δ吞吐 / Δ显存` 表 + **推荐给 P-8 的配置（仅在已暴露开关内）**，与 P-9d 瓶颈诊断交叉印证。

#### P-9.3 seq 多点扫描（G 项扩展）— 保持 4M/步
> 运维洞察：hybrid 几乎关掉了「注意力随上下文爆炸」→ 值得多扫几个 seq。

| seq | GBS | 注意力占比预估 `0.7%·(seq/4096)²` | 显存（相对 4096） |
|:--|:--|:--|:--|
| 2048 | 2048 | ~0.2% | ~0.5× |
| **4096** | **1024** | 0.7%（实测基线） | 1× |
| 6144（可选） | 680 | ~1.6% | ~1.5× |
| **8192** | **512** | ~2.8% | ~2× |
| **16384**（强烈建议·边界点） | **256** | **~11%（O(n²) 首次可见）** | **~4×（可能 OOM）** |

- **必做 2048/4096/8192；强烈建议 16384；6144 可选**。每点记 **t_step/tok/s/峰值显存/OOM**，并按 **attention / SSM / GEMM / comm / elementwise** 五项归因。
- ✅ **已有证据（P-4 profile**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` P-4 节 / `run/p4_profile_bf16.txt`，80 步 `torch.profiler`，GBS=8）：**`attention flash` 仅占 GPU 自耗 0.7%**（SSM 8.4% / GEMM ~28.6% / NCCL 41.7% / norm+act 10.5%）→ seq 翻倍使注意力项 ~×4，**最坏 0.7%→~2.8%**；其余按 token 计价、与 seq 无关。
- **预测（可证伪）**：`r = t_step(seq)/t_step(4096)`，**8192 应落在 ~1.05–1.20**；**纯 Transformer 会是 2–4×** → 由此可给出「**hybrid 把 O(n²) 关掉多少**」的量化结论（论文加分点）。
- **判据（先定后测，🚫 不许事后改）**：`r ≤ 1.2` → 该 seq **作 P-8 候选**；`r ≥ 1.5` → **P-8 沿用 4096**（除非确需长上下文）。**16384 若 OOM → 如实记 OOM**（= 内存先于算力成为限制），**不要硬凑**。
- ⚠️ P-4 是 **GBS=8** 口径（NCCL 被放大）→ **请在 P-9 生产口径重测**，不许直接搬份额。

#### P-9.4 FP8 复评（问题②）— ⚠️ **按 `M` 扫，不按 `seq` 扫**
- **机制**：`s` 取决于 **GEMM 的 M**；我们大 GEMM（MLP/SSM 投影）**`M = MBS × seq`** → **seq 与 MBS 是等价杠杆**（`seq4096+MBS4` ≡ `seq8192+MBS2` = M=16384）。→ `seq=4096` 下 `MBS=4` 即进交叉点，**seq 不是解锁 FP8 的必经之路**。
- **做**：先核 `transformer_engine` 版本（记 **2.12.0 / torch 2.8.0+cu128**，贴原文）；**复用并扩展 P-4R 的 `s`-vs-M 微基准到 `M ∈ {4K,8K,16K,32K,64K}`**（用 `(MBS,seq)` 组合命中）；再在**最大可行 MBS** 下做 **bf16 vs FP8 端到端对照**（同 MBS、同步数），报 **端到端 `s = t_bf16/t_fp8`**。
- **产出**：**`s(M)` 曲线 + 交叉点 `M*` + 端到端收益**（能否复现 Xmodel-2.5 的 +30%？）。
- **诚实**：若仍倒挂 → 写「本模型/本口径下不可行」，**不要为迎合结论调参**。

#### P-9.5 训练性能 profiling / 瓶颈诊断（问题③；🚫 **不 attach live 20B**）
- **载体**：**P-9.1 的短测**（~50–100 步）；🚫 **不要**对 P-5b 的 20B 长跑 `nsys --attach` / `ncu`（会拖慢并污染那条 loss 曲线）。
- **工具（按成本从低到高）**：
  1. **已有日志**：从 iteration 行算 **MFU**（已观测 ~345–358 TFLOP/s/GPU vs H100 bf16 ≈989 → **~35%**，说明有空间）；贴原文。
  2. `nvidia-smi dmon` / `dcgm`：SM util、显存带宽。
  3. **`torch.profiler`**（`profile_memory=True, record_shapes=True, with_stack=True`）跑 20–50 步 → **top kernels + 时间占比 + 显存峰值**（chrome trace **不入库**，只留摘要）。
  4. **`nsys profile`**：timeline / kernel 间隔 / grad-accum bubble。
  5. **`ncu`**：只对**少数热点 kernel**取证，**必须**在短测上。
  > ✅ **工具可自装**（运维 2026-10-03 授权：内网 pip 镜像 / conda 装 `nvidia-nsight-systems`，或 apt `nsight-systems`）；**能装就装，装不上就回落 `torch.profiler`**（足够定位瓶颈），**不要为装工具卡住 P-9**。
- **重点诊断（hybrid 先验）**：① **grad-accum 空隙**（MBS=1 → 128 段）② 访存受限的 **SSM scan / elementwise / LayerNorm** ③ recompute 是否过重 ④ mamba 自定义 kernel 是否走高效路径 ⑤ **NCCL 通信（P-4 里 41.7%，最大单项）**。
- **产出**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md`「P-9d」节 —— **瓶颈 TOP-N（含证据）+ 预计收益 + 风险**，并与 **P-9.1 / P-9.4** 交叉印证（MBS↑ / FP8 是否正打中瓶颈）。

#### P-9.6 结论（P-9c）
- 给出 **P-8 推荐启动配置**：**seq（4096 / 8192 / …）/ MBS / 精度（bf16 / FP8）/ 预期 tok/s / 峰值显存** + **代价**（是否影响数值 / 收敛）。
- **顺序**：**P-9.1 → P-9.2 → P-9.3 → P-9.4 → P-9.5 → P-9.6**（可交错）；⏱ **尽早**，**🚫 不得后置到 P-6② 之后**。
- **铁律**：**不许猜**（每条数 / 瓶颈须有**命令 + 原始输出**）；**不改 P-5b、不改训练代码**（只给建议，改动留待运维批准）。

### P-5b　训练量 scaling 曲线（长跑，**用 P-5a 选定的 GBS 与 LR**）

- 从零训练，**用 P-5a 推荐的 GBS（尽量接近 1024）与 LR**。
- 在 **655M / 1.3B / 2.6B / 5.2B / 10.5B / 20B token** 各记一次 **val loss**（附带 train loss、grad norm）。
- ⭐ **同时：在这 6 个点<u>各存一个 checkpoint</u>**（`--save-interval` 已按此对齐为 156 步）——
  **它们是 P-6 第 2 步的输入**：要在这些 ckpt 上跑 **常识 8 集 + 复杂 6 集**，
  画出 **「能力 vs token」scaling law 曲线并外推**（见 P-6 第 2 步）。
  → **命名要规范、路径要记录**（例如 `s5_01_tok655m / 1p3b / 2p6b / 5p2b / 10p5b / 20b`），
  **必须能按 token 数直接对上**，否则后面接不上。
- 产出 **loss vs tokens 曲线**（log-x）。**这条曲线直接用来定正式训练的 token 预算。**
- **若 20B 处仍未明显变平** → 在预算允许内继续延长到 **40–60B**。
- ⚠️ **与既有 `2.2054@655M` 不可直接比较**（那是 GBS=8）：报告须注明口径差异；
  必要时**在 GBS=8 下也补一个 20B 点**作为对照，隔离"GBS 变了"与"token 变多了"两个因素。

> ### 🔗 与 P-6 第 2 步的关系（**本轮的真正价值**）
> **loss 曲线只是中间产物**；**决策依据是「能力 vs token」曲线 + 外推**（见 P-6 第 2 步）：
> **常识推理 Avg 要达到 50% / 55% / 60%，各需要多少 token？**
> → **那个答案才用来定 P-8 的 token 预算。**

**预算**
- P-5a：≈ 9 次 × 164M token ≈ 1.5B token ≈ **4–5 小时墙钟**
- P-5b：20B token ≈ **60 小时墙钟（≈2.5 天 / 478 GPU·h）**；到 60B ≈ 7.5 天
- 合计 **≤ 8 天墙钟**。**先 a 后 b。**

**产出（写进 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md`）**
1. GBS × LR 的**完整结果表** + "最优 LR 是否右移"的**明确结论** + GBS=1024 的推荐 LR
2. **loss vs tokens 曲线** + "曲线何时变平"的判断 + **正式训练的 token 预算建议**
3. 论文回填建议：§4 该怎么写（是否要把"655M token 只是 1.5% Chinchilla"如实写进 Limitations）

---

> 📦 以下 3 块由 agent 于 2026-10-06 从 BAIZE_PRETRAIN_2B_TASK.md 原文搬迁（均已执行完毕）。

### 🆕 运维指令 · 2026-10-05（深夜2 · ① **sglang 上界必须真跑出来（已完成的≠sglang）** ② P-5b 8 集常识评测 + data scaling **HTML** ③ P-6② 说明 **HTML** ④ P-9.5 profiler 复跑 **HTML**）· **最高优先**

> **用户 4 条（2026-10-05 深夜）**：
> ①「**已经完成的 P-9.10 是用 sglang 对比的吗？**如果 sglang 还是起不来这不应该，**需要继续排查（HF 转换）**，再说 pretrain 有 web search，**有没有用上**？所以**第一件事：起 sglang 上界补测**。」
> ②「pretrain 还有评测工作没做吧 —— **P-5b 没在常识推理 8 集上评测**，**也没出 data scaling 结果**。**写个 HTML 报告**。」
> ③「**P-6②（能力 vs token scaling）** … **写个 HTML 报告**。」
> ④「**P-9.5 profiler 可以排查复跑**，**写个 HTML 报告**。」

> 🔁 **顺序调整（用户追加，2026-10-05 深夜）**：「**P-6② 可以早点做**」。
> ⇒ **②③（P-5b 8 集 + P-6②，同一评测管线）提到最前** —— 它**不依赖 HF 转换**，**`.29` GPU0–1 现在正空**（P-9.10②③ 已收工）⇒ **立即可跑**；
> ⇒ **① 的 CPU 部分**（HF 转换 / ABI 排查 / `cimi_search`）**与之并行**推进；**转换好后再起 sglang 上界的 GPU 部分**；④ 放最后。
> **实际执行顺序：②③（合并跑，分别出 HTML）→ ①（CPU 并行 → GPU 补测）→ ④。**

#### ① 【第一件事】sglang 上界补测 —— 必须真跑出来（现状 = **没跑到**）
- **事实澄清**：**P-9.10 已完成的 ②③ 都不是 sglang** —— ② = **mcore eager 下界**（H1✅ decode 1.6× / H2❌ / H3❌ / H4✅）；③ = **自定义 benchmark**（`benchmark_p910.py`，`mamba_ssm`+`transformers`），**因为 vllm/sglang 起服报 ABI mismatch / `std::bad_alloc`**。⇒ **「sglang 生产栈上界」仍是空白**，而它正是用来验证/翻正 **H2（decode 优势是否随 ctx 增长）** 的 ⇒ **必须补。**
- **🚫 不接受「起不来」了事**，按序排查（每步贴**原始报错**）：
  1. **读现成 env**：`conda run -n vllm python -c "import sglang, torch, flashinfer; ..."`（sglang 0.5.9 / torch 2.8.0+cu128 / flashinfer 0.6.3；`.29` 与 `.12` 共享 NFS）；
  2. **ABI mismatch**：打印 `numpy/torch/transformers/flashinfer` 版本组合 + `pip check`；必要时在**独立 env / `--target`** 里重装**互相匹配**的版本（🚫 不碰共享 `py310`）；
  3. **`std::bad_alloc`**：查 C++/CUDA 库版本、`LD_LIBRARY_PATH`、`libstdc++`，以及 `--mem-fraction-static` / `--max-total-tokens` 等内存参数；
  4. 🔎 **必须用 web search**（`cimi_search` + `cimi_fetch`，本线可用）：查 **sglang 部署 `nemotron_h` 官方文档/issue**、**「sglang ABI mismatch / std::bad_alloc」已知解法**、**mcore distcp → HF 权重映射**规范。**每条给 URL + 版本/年份**，核不到写「未核实」。
- **HF 转换（真正的坑）**：`p3_hybrid/iter_0005000` → **`nemotron_h`**；`p3_dense/iter_0005000` → `gpt/minicpm` 兼容。手写映射脚本放**独立目录**；**转换后先做「同输入 logits 对齐」自检**（mcore vs HF 前向差异）再起服务。
- **跑通后**：按本文件下方既有块「sglang 可用 → GPU0–1 对比」执行（ctx{4K,16K,64K,128K(±256K)} × bs{1,8}，gen_len=64；采 TTFT/prefill/decode/延迟/峰值显存；逐格 hybrid÷dense 比值；与 ② 并列并标框架）。
- **产出**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新增「**P-9.11 sglang 生产栈对比**」节 + **HTML 报告**（自包含、无 CDN，放 `doc/BaiZe-ISEDA2027/`）。卡：**只用 `.29` GPU0–1**。

#### ② P-5b 的 8 集常识评测 + data scaling → **HTML**
- **现状**：**P-5b（20B token，final loss 1.9141，31 ckpt）从未在常识推理 8 集评测**；此前只有 **P-6 第 1 步**（Avg **0.4395** @ 20k 步/655M token）。
- **要做**：复用 `ckpt → HF → lm_eval`，对 **P-5b `final`**（建议加 **6 个里程碑 ckpt** 156/312/624/1248/2496/4771 = 655M…20B token）跑 **8 集零样本**（`ARC-C` `ARC-E` `BoolQ` `HellaSwag` `OpenBookQA` `PiQA` `SciQ` `Winogrande` + Avg）。
- **data scaling**：据多点画 **(能力, token)** 曲线 + 外推（与 ③ 同源）。
- **产出 HTML**：`report_pretrain_p5b_8sets.html`（命令 + 原始输出 + 逐集表 + Avg + scaling 曲线）。

#### ③ P-6②（能力 vs token scaling）→ **HTML**
- **备忘**：**P-6 第 2 步 = 用 P-5b 的 6 个里程碑 ckpt 跑 8 集 lm_eval → (能力, token) 曲线 → 外推，用来定 P-8 的 token 预算**（推荐 100B）；与 ② 是**同一实验的两面**。
- **产出 HTML**：`report_pretrain_p6b_scaling.html`（目的 / 输入 ckpt / 评测集 / 预注册判据 / 曲线+外推 / 对 P-8 token 预算的结论）。

#### ④ P-9.5（训练性能 profiling / 瓶颈诊断）排查复跑 → **HTML**
- **背景**：`torch.profiler` **曾崩溃**（`run/baize_p9_seq_scan.sh`；只拿到 level-1 MFU）。**缺失的正是 5-way 归因**（attention/SSM/GEMM/comm/elementwise）。
- **要做**：**排查崩溃根因**（贴原始报错）→ 修（`timeout` 分步 / 缩小 capture / 手动 `prof.step()` / nsys 兜底）→ **复跑拿 5-way 归因**。
- **🚫 铁律**：**不对 live 长跑 attach**；只在**短程/离线**进程 profile。
- **产出 HTML**：`report_pretrain_p95_profiler.html`（崩溃根因 + 修复 + 5-way 表 + 与 P-9 结论印证）。

> ✅ 本块生效即视为已批准。**顺序（已按用户追加「P-6② 早点做」调整）：②③ 先合并跑（同一评测管线，分别出 HTML，用 `.29` GPU0–1）→ ① sglang（CPU 并行 → GPU 补测）→ ④ P-9.5。**

### 🆕 运维指令 · 2026-10-05（深夜 · ✅ **sglang 可用 → 用 `.29` GPU0–1 做「BaiZe（Mamba2-hybrid 2B） vs MiniCPM5-2B」推理对比（框架 = sglang）**）· 高优先 · **已批准**

> **用户拍板（2026-10-05 深夜）**：「既然 sglang ✅ 可用，那可以用 `.29` **GPU0–1 空**进行对比测试（**推理延迟、吞吐量、显存占用**等）。」
> ⚠️ **口径更正（运维 2026-10-05 深夜）**：本项**不是「mcore vs sglang」的栈对比** —— 而是 **sglang 作为（同一个）推理框架，对比两个架构**：**BaiZe = Mamba2-hybrid 2.220B** ⚔ **MiniCPM5-2B = dense GPT 2.512B**。

**目标**：用**生产推理栈 sglang** 复测/量化**项目核心论点** —— **Mamba2-hybrid（BaiZe）相对 MiniCPM5-2B 在长上下文下的推理优势**（Round 1 S3 曾在 mcore 上量到 decode **10.3×**，但那是**旧 ckpt（已删）+ 非生产栈**，须在 sglang 上重新量一遍并标注口径）。

**① 对象（两个已核验在位的 ckpt，均在 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/`）**

| 模型 | = | ckpt | 参数 |
|:--|:--|:--|:--|
| **BaiZe（本项目）** | Mamba2-hybrid | **`p3_hybrid/iter_0005000`** | 2.220B |
| **对照** | MiniCPM5-2B（dense GPT） | **`p3_dense/iter_0005000`** | 2.512B |

- **前置（真正的坑）**：两者都要 **mcore distcp → HF**：hybrid → **`nemotron_h`**（sglang 原生支持）；dense → `gpt`/`minicpm` 兼容结构。**手写权重映射**，脚本隔离在独立目录，🚫 不动共享 `py310`。
- ⚠️ **口径标注**：P-3 = 5000 步 / 123M token（与已删的 S3=1000 步/24.6M 不同）⇒ **旧 10.3× 与本轮数字不得直接相减**，两者并列、各标栈与权重。

**② 测试矩阵（同一 sglang、两模型逐格对齐）**：context ∈ {4K,16K,64K,128K}（可加 256K）× batch ∈ {1,8}（**OOM 就如实记 OOM，🚫 不许偷偷降 context**），gen_len=64。

**③ 采集指标（每格）**：**TTFT · prefill 吞吐(tok/s) · decode 吞吐(tok/s) · 端到端延迟 · 峰值显存**；**逐格算 hybrid vs dense 的比值**；并与 P-9.10② 的 **mcore eager 下界**并列成一张表（标注框架差异）。

**④ 关键问题**
- **decode 优势是否随 ctx 增长**（SSM O(n) vs attn O(n²)）？—— Round 1 在 mcore 上量到 ~10.3×，**sglang 生产栈下是多少**？（P-9.10② eager 下因 launch 开销只量到 ~1.6× 恒定、H2 未翻正 ⇒ **生产栈正是用来验证/翻正这一点**）
- **显存**：hybrid 的 SSM state 恒定、attn KV 随 ctx 线性 ⇒ 长 ctx 显存优势多大？
- prefill 长 ctx 加速比。

**⑤ 边界与铁律**
- **只用 `.29` GPU0–1**（GPU2–7 是 data 配比实验）；🚫 **不 kill data 进程**；要更多卡按 `run/GPU29_ALLOC.md`「申请区」走。
- **不改 P-5b recipe / 不回训 / 不存新训练 ckpt**；🚫 **绝不 kill watchdog loop**。
- sglang 起服**必须用 `vllm` conda env**（已在位：sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13），🚫 不碰共享 `py310`。
- 外网命令**显式带 proxy**。

**⑥ 产出**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新增「**P-9.11 · sglang 生产栈 —— BaiZe(Mamba2-hybrid 2B) vs MiniCPM5-2B 推理对比**」节（**命令 + 原始输出 + 逐格表 + 每格比值** + 与 Round-1 mcore 数字并列并标口径）。

> ✅ 本块生效即视为已批准；**P-9.10②（eager 下界）已完成**，本块为「生产栈复测架构对比」，**不阻塞** P-6② / P-8。

### 🆕 运维指令 · 2026-10-05（晚 · ① `sglang` 改用 **conda 环境**从头装（先查 `.12` 现成的 sglang/vllm env）② 「外网命令带 proxy」口径同步 ③ 环境隔离纪律）· 高优先

> **用户拍板（2026-10-05 晚）**：「**P-9.10 与 sglang A/B：我在 `2.12` 已经装过 sglang 的**，你可以看看有没有 conda 环境叫 `sglang` 或 `vllm` 的。**如果没有，自己新开个 conda 环境，叫 `sglang`，从头装一下**，记得设置 `https_proxy` 和国内的（比如阿里腾讯）pip 源，**可以装的**。」

**① 先查现成 conda 环境（`.12` 为主，`.29` 也查）**
```bash
conda env list | grep -Ei 'sglang|vllm'          # 两台机都查（.12 是用户说装过的那台）
# 命中后在该 env 里验证：
conda run -n sglang python -c "import sglang, torch; print(sglang.__version__, torch.__version__, torch.cuda.is_available())"
```
- 找到**版本/依赖可用**的 env ⇒ **直接复用**（记清 env 名 + 版本 + `conda env list` 原文）。
- ⚠️ `.12` 的 env 是**本机 conda**（若两机不共享 conda 路径则不能直接给 `.29` 用）⇒ 若 P-9.10 在 `.29` 跑，**在 `.29` 上另建同名 env 或确认 conda 路径共享**；两机都要给出核验原文。

**② 没有就新建 `sglang` 环境从头装（显式带 proxy + 国内源）**
```bash
export http_proxy=http://172.19.92.25:13128 https_proxy=http://172.19.92.25:13128
conda create -y -n sglang python=3.10
conda run -n sglang python -m pip install -U pip -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
conda run -n sglang python -m pip install sglang \
  -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
  --extra-index-url https://pypi.tuna.tsinghua.edu.cn/simple      # 阿里不通换腾讯 https://mirrors.cloud.tencent.com/pypi/simple
```
- 🚫 **绝不在共享 `py310` 里装**（隔离在 `sglang` env 内）；🚫 不要 `--no-deps`。
- 记录**确切输出**（成功 → `sglang --version` + `import` 通过；失败 → 贴原始报错）。
- 若 `cuda-tile`（仅 `pypi.nvidia.com`）仍 SSL EOF ⇒ 试国内镜像的同名/nvidia wheel 或 conda 源；**仍失败**才回落到已定的 **`mcore + CUDA-graph`**，✅ **不阻塞 P-9.10 ②**（到点照起；sglang 只为「抬上界」）。

**③ 「外网命令带 proxy」口径同步到本线（与 data / harness / vision 一致）**
- 你的 shell 被 loop 剥了 `*_PROXY`（内网网关鉴权用，**不能改**）⇒ 凡访问外网的那条命令**自己显式带**：`P=http://172.19.92.25:13128`；`https_proxy=$P http_proxy=$P <cmd>`；pip 加 `--proxy $P` + 国内索引。
- 🔑 **`Errno 101 / http 000` = shell 没带 proxy，不是集群禁网/镜像被墙**（本轮 sglang A/B 已实测证实：带 proxy → 阿里云 200）。

**④ 环境隔离纪律（治「同机争用」—— 用户裁定）**
- **训练/长跑 = 共享 `py310`**（不动）；**`sglang` 托管大模型 = `sglang` conda env**；**harness 大量装包 = 另起新 conda env**。三者互不污染。

> ✅ 本块生效即视为已批准。**时序不变**：P-9.10 ② 照常在 GPU0–1 起；P-9.9 已收官（tensorwise FAIL → **P-8 沿用 delayed FP8**）。
\n\n---\n## 已归档 · 2026-10-06（B1 扩展 + hybrid 优势论证 · 均已完成）

### 🆕 运维指令 · 2026-10-06（🔭 **B1 的 ctx 曲线扩到 256K / 512K / 1M** ＋ 判定「下一个瓶颈是谁」）· 高优先

> **用户追问（2026-10-06）**：「**ctx 可以继续扩张吗？128k → 256k → 512k → 1M**」。你 B1 步骤 1 已证明 **128K 能跑通（正确尺寸 prompt → HTTP200，3.79s）** ⇒ 请把 **B1 步骤 2/3 的 ctx 档位从 `{4K…128K}` 扩到含 `256K / 512K / 1M`**，并回答「**再往上谁先顶不住**」。
>
> **要做**：
> 1. **逐档实测（免训练优先）**：ctx ∈ {4K, 8K, 16K, 32K, 64K, 128K, **256K, 512K, 1M**} —— 每档报 **HTTP 可跑性 / TTFT / prefill 时间 / 峰值显存 / PPL（或 passkey 检索）**；⚠️ **prompt 一律用 tokenizer 精确计数**（别再踩 128K 那个构造 bug）。
> 2. **判定「下一个瓶颈」——分三类，逐档给数**：
>    - **(a) RoPE 外推质量**：只影响 **4 层 attention**；**24 层 SSM 无位置编码 ⇒ 无位置 OOD**。⇒ 给出「**质量开始明显掉**」的 ctx 拐点。
>    - **(b) KV cache / 显存**：只随 **4 层**线性增长（对比稠密 56 层全 KV）⇒ 给出「**哪一档开始触顶/OOM**」。
>    - **(c) 那 4 层 attention 的 O(n²)**：SSM 是 O(n)，但 attention 部分在极长 ctx 下可能**反超为主导** ⇒ 给「**attention 占 prefill 的比例随 ctx 上升**」的曲线。**若 (c) 先顶住** ⇒ **架构级对策 = 把这 4 层改成局部窗口/sliding 或 NoPE**（**属 P-8 启动前才可定的议题**，先只做**可行性判断 + 成本**，🚫 不动架构）。
> 3. **对齐真实需求（别为 1M 而 1M）**：**先量「agentic EDA 到底要多长」** —— 可参考 **ZhuLong 评测里的轨迹 token 长度分布**、或 **harness 侧 SWE-bench 的上下文长度** ⇒ 给出「**目标 ctx 应该是多少**」的建议。
> 4. **产出**：并入 `report_pretrain_hybrid_longctx_advantage.html` 新增一节「**可扩展到多长**」（含 1M 档结论 + 瓶颈归属 (a)/(b)/(c)）。
>
> 🚫 铁律不变：不占 GPU2-7、不改 P-5b recipe、不存 ckpt、🚫 绝不 kill watchdog；时间盒内做不完**如实写卡点**。


### 🆕 运维指令 · 2026-10-06（⭐⭐ **【长上下文：B 扩展 + hybrid 优势论证】** —— 为 **P-8 正式训练申请足量资源**供弹药）· 高优先

> **用户口径（2026-10-06）**：「把**长上下文场景下 Mamba2-hybrid 相对于 MiniCPM5 的优势谈清楚**，这样**有利于为 P-8 正式训练申请足量资源**。」
> **已核准的配置事实（据此出发）**：HF 转换写出的 `nemotron_h` config **只有 `max_position_embeddings=4096`，没有 `rope_theta`/`rope_scaling`**（⇒ 走 transformers 默认 **rope_theta=1e4**）；而**对照 MiniCPM5-2B 是 `rope_theta=5e6` + `max_position_embeddings=131072`** ⇒ **基线天生为长上下文配置，我们不是**。而 P-9.11 的 128K 失败（e2e≈0.5s、`total_completion_tokens=0`、**非 OOM/非超时**）= **被拒**（4K/16K/64K 均成功）。

> **A. 把已批准的「B（长上下文 4096→8192+）」扩成三步（仍在原预算：1 卡 · ~2–3h；铁律不变）**
> - **B1（~1h · 免训练诊断 · 先做）**：
>   1. **先查 128K 的"拒绝原因"**（sglang 日志 + 直接构造 128K 请求看**返回体**；核 `--max-total-tokens`、KV+mamba-state 容量核算、后端对该模型的 ctx 校验）→ **如实贴原文**；
>   2. 改 HF config：**`max_position_embeddings` → 131072**；**`rope_theta` 1e4 → 5e5/1e6（ABF，对齐基线量级）**；可选加 `rope_scaling`（**PI / dynamic-NTK / YaRN** 三选）。⚠️ **每次只改一个变量**；
>   3. 跑 **ctx ∈ {4K, 8K, 16K, 32K, 64K, 128K}** 的 **PPL + passkey/needle 检索 + 8 集 eval** → **出退化曲线**；
>   4. **判据**：8 集降幅 **<10%** 且 PPL 不炸 ⇒ 该长度"免训练可用"。**每个数字都必须标清 config/栈**。
> - **B2（~2–3h · 条件触发）**：若 B1 显示 **≥16K 明显退化** ⇒ 做**阶梯式长度扩展续训（4K→8K→16K，每档 0.5–2B token）**。⭐ **只有 4 层 attention 吃 RoPE（24 层 SSM 无位置编码）⇒ 待适应面小、应收敛很快** —— 请把**实际收敛速度**记下来（**这本身就是 hybrid 优势的量化证据**）。
> - **B3（0 成本 · 决策输入）**：整理成**给 P-8 seq 的决策答案**：「**P-8 的 seq 定 4096 / 8192 / 还是 decay 段升 8192–16384？**」并给**成本差**（decay 段 token 占比小 ⇒ 升长几乎免费）。⚠️ **必须在 P-8 启动前定案，否则 P-8 作废。**

> **B. ⭐ 交付 `report_pretrain_hybrid_longctx_advantage.html`** —— 面向资源申请的**一页摘要**（自包含）
> 📌 **已有运维侧草稿可作底稿**：`doc/BaiZe-ISEDA2027/report_hybrid_longctx_case.html`（已含：三笔账 / 劣势与边界 / config 事实对比 / 中英双语可引用措辞 / **出处与口径表**）—— **请在其基础上用 B1 实测数据刷新数字，不要从零重写**。
> **必须含**：
> 1. **三笔账（按 ctx 画曲线，ctx ∈ {4K,16K,32K,64K,128K}）**：
>    - **prefill / TTFT**：SSM **O(n)** vs attention **O(n²)** ⇒ 已测 **3.7×–23×**（P-9.10③ 自定义 benchmark，4K→128K 递增）· **2.18×@64K**（P-9.11 sglang 生产栈）· **3.6×@128K**（P-9.10② eager 下界）—— **请补 B1 之后口径统一的一组**；
>    - **显存 / KV（决定"能不能服务"）**：已测 **0.22×–0.44×**（128K×bs1：**13 GB vs 61 GB**），且 **dense 在 128K×bs8 直接 OOM**；
>    - **每 token 缓存搬运**：hybrid **5.1× 更低**（P-9.10② H3：cache 18.2× 但 per-token 更低）。
> 2. **如实写劣势与边界（不许夸大）**：
>    - **decode 吞吐**：短 ctx 下 **dense 快 1.2–1.6×**（transformers KV cache 优化）；**sglang 生产栈 1.18×@64K、crossover ≈50K** ⇒ 请给出「**ctx ≥ X 时 hybrid 反超/持平**」的边界；
>    - **训练吞吐 −8%**（P-7 真值）—— ⚠️ **论文原写的 −24% 是跨节点 artifact，不得再引用**；
>    - **未测项（如 1M ctx）一律标"未测/外推"**，不许当结论。
> 3. **一句话可引用结论（模板，用你们实测数替换）**：
>    > 「在 128K×bs1 下，**2.22B Mamba2-hybrid 只用 0.22× 显存完成 prefill；2.512B 稠密基线在 bs8/128K 直接 OOM**。prefill 优势随 ctx 从 4K 的 3.7× 拉到 128K 的 23×；代价仅为训练吞吐 **−8%**。」
> 4. **与 P-8 资源申请的挂钩段（1 段）**：**"给 P-8 足量资源（100B token / ~12.5 天 / 8×H100）产出的，是一个在 agentic EDA 的 32K–128K 场景下 prefill 快数倍、显存省 2–4 倍、且比稠密基线少 11.6% 参数的 2.2B 模型"** ⇒ 正是「**harness 解决后，小模型也能顶用**」的降本论据。
> 5. **口径纪律**：所有数字标 **栈（mcore eager / 自定义 / sglang）+ 后端 + bs + mem-fraction + config**；**不许混口径**；未实测的标来源或标「待测」。

> **C. 与「提速令」的关系**：本块与 Step 2 提速**并行不冲突**（都只用 GPU0-1）。**顺序建议**：**B1（~1h）→ 提速清单 → B2（若需要）→ A（复杂推理 6 集）→ D（P-9.11 缺口）**。

---

### 🆕 运维指令 · 2026-10-06（⭐ **【裁决 + 提速令】** 批准 **A/B/D**；**C 暂不动 / E 不做**；**当前主线 = 用 GPU0-1 优化训练配置、争取提速**）· **最高优先**

> **一、对你「空窗提案」的裁决（用户 2026-10-06）**
> - ✅ **批准 A（复杂推理 6 集）**：按你写的方案执行（GPU0 · 1 卡 · ≤6h 时间盒）→ 产出 `report_pretrain_complex6_scaling.html`。
> - ✅ **批准 B（长上下文 4096→8192+）**：执行（GPU0 · 1 卡 · ≤4h）→ 产出 `report_pretrain_longctx.html`。⚠️ 你自己指出的"RoPE 只影响 4 层 attention ⇒ 收益可能有限"**要实测检验，不得预设结论**。
> - ✅ **批准 D（P-9.11 缺口补测：128K + H3 sglang）**：执行（GPU0 · 1 卡 · ≤2h）。
> - ⏸ **C（P-8 dry-run）＝ 暂不动**（用户：「**P-8 暂时不动**」）⇒ 🚫 不要启动。
> - 🚫 **E（ckpt → OpenAI 兼容服务 + 接 Cline harness）＝ 不做**（用户：「**现在模型能力太弱，距离能作为 harness 底模还很远**」）⇒ 本阶段**不投入**；将来若要，由运维点名。
>
> **二、⭐ 当前最高优先 =【提速】：用 GPU0-1 优化训练配置、争取提速**（用户原话：「pretrain 当前的重要任务，还是用这两张卡优化训练配置，争取提速」）
> **第 1 步（你已点名的假设，必须实测证伪/证实）——NCCL / NVLink 拓扑核查**（源自 `report_pretrain_p95_profiler.html`）：
> - **假设（用户提出）**：若当前 **NCCL 实际走的是 PCIe P2P（而非 NVLink）**，换成更好的 **NVLink 拓扑**会有改善。
> - **必须取证**：① `nvidia-smi topo -m`（PIX/PXB/PHB/**NV#** 矩阵）；② `nvidia-smi nvlink -s` / `-c`（链路 UP？速率？）；③ **`NCCL_DEBUG=INFO` 真跑一次**（抓 `Channel…via P2P/IPC/NVLS`、`via NET`、`P2P is enabled/disabled`、`NVLS` 是否启用）；④ **`nccl-tests` 的 `all_reduce_perf`**（若无该工具，就用你自己的 DP2/DP8 微基准）量 **busbw**。
> - **对照实验（每次只改一个变量）**：`NCCL_P2P_DISABLE` · `NCCL_P2P_LEVEL` · `NCCL_TOPO_FILE`（自定义拓扑）· `NCCL_IB_DISABLE` · `NCCL_SHM_DISABLE` · `NCCL_ALGO`（ring/tree）· `NCCL_PROTO` · **NVLS/`NCCL_NVLS_ENABLE`** —— 各测 **busbw + 端到端 tok/s**。
> - **判据（必须给）**：① **当前实际通道构成**（NVLink / P2P / NET 各占几成）② **最佳 env 组合** ③ **相对 baseline 的 tok/s 提升 %** ④ **该提升能否迁移到 8 卡**（对照 **P-9.7 的 249K tok/s** 基线）。
> - **产出**：`report_pretrain_nccl_topo.html`（自包含：topo 矩阵 + NCCL 日志关键行原文 + busbw 表 + tok/s 表 + 结论）。
> **第 2 步 —— 训练提速候选清单**（都用 GPU0-1 可实测）：MBS/GBS/seq 组合 · `--recompute` 档位 · CUDA-graph/静态形状 · 数据管线（`num_workers`/预取/阻塞点）· TP/DP 拓扑 · kernel/backend 选择（TE、attention backend）· 以及 **P-9.7「249K tok/s」口径复核**。
> - **每条给**：实测 **tok/s** + **判据** + **是否可迁移 8 卡** + **时间盒**。
> - **优先「不改 recipe、只改运行时/并行/IO」的项**（这类最可能迁移到 P-8 且不污染既有结论）；**凡涉及改 recipe 的，先报提案再动**。
> **建议顺序**：① NCCL 拓扑核查（~1h）→ ② 提速清单（挑 2–3 条最可能见效的）→ ③ A → B → D（纯推理，可插空）。
>
> **三、纪律（不变）**
> - 🚫 **不占 GPU2-7**（data 配比 BO，ETA ~16:00）；🚫 **不启动 P-8**；🚫 不改 P-5b 已定稿 recipe、不回训、不囤无关 ckpt；🚫 **绝不 kill watchdog loop**。
> - 每项都有 **时间盒 + 判据 + 可否中断**；产出写进 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` + HTML，并按「收尾铁律」commit + push。
> - 做不了/做不完 ⇒ **如实写"卡点 + 需要什么"，不许凑数**。


### 🆕 运维指令 · 2026-10-06（⭐ **【空窗提案】P-8 未启动期间，请你自己提一份"可用 GPU0–1"的实验提案**）· 高优先 · **本轮只交提案，未批准不得启动**

> **背景**：P-8 本体因两个前置（① base 全量未齐 ② 配比未定稿）**暂缓** ⇒ **`.29` 的 GPU0–1 目前空转**，而你已连续多轮（#128–#133）只做"状态核查"。用户要求：**由你**（最熟悉既有脚本/ckpt/数据/交付物的人）提出**空窗期可做的实验**——运维不替你想。
>
> **交付格式**：**3–5 条候选**，每条一小节，**必须**含：
> ① **一句话目标**（回答什么科学/工程问题）；
> ② **占卡与墙钟**（1 卡 / 2 卡；预计小时；**不得占用 GPU2–7** —— 那是 data 的配比 BO，ETA ~17:00）；
> ③ **可复用的既有资产**（脚本 / ckpt / 数据 / HTML，**给绝对路径**，如 `nemo_experiments/p3_hybrid/hf_iter_5000/`、`data/p5b_l3/p5b_l3_train_s*`）；
> ④ **产出物**（报告节 / HTML / 表 + 落盘路径）；
> ⑤ **与 P-8 前置的关系**（"解 P-8 的前置" / "与 P-8 并行不冲突" / "纯论文补强"）；
> ⑥ **成本与风险**（GPU·h、失败模式、**时间盒**、可否中断）。
> **另附一行**：**你的推荐排序 + 理由**（为什么第 1 条最值）。
>
> **候选方向（供参考，不强制；你若认为不合适，请写明理由）**：
> 1. ⭐ **长上下文适配 4096 → 8192+**：README 风险表 **#3 🔴**「4096 对 agentic 轨迹过短」是 **(ii) SFT/RL 的前置硬约束**；且 **P-9.11② 的 128K 格 failed（`max_pos=4096`）** 正指向这里。可评估 RoPE/NTK/YaRN 扩展或短程长 ctx 续训 + 8K 零样本评测。
> 2. ⭐ **ckpt → OpenAI 兼容推理服务 + 接入 Cline harness**（README 待办）：P-9.11 只做到"起服 + 测矩阵"，**"接 harness"未做**；这是论文**推理成本卖点**的落地证据。
> 3. **P-9.11 缺口补测**：128K 格 failed；H3 在 sglang 下被 `--mem-fraction-static 0.85` 预分配掩盖。
> 4. **复杂推理 6 集**（GSM8K/MATH/BBH/MMLU/HE/MBPP）：任务书 §(3)(4) 要求"常识 8 集 **+ 复杂 6 集**"两条曲线，**目前只见常识 8 集** ⇒ 请**确认是否做过**；没做就补（任务书已预告"很可能贴地板，量出来本身就是结论"）。
> 5. **P-8 dry-run（预演）**：用 GPU0–1 跑 1–2B token 的 WSD 小预演，验 P-8 的启动脚本 / **FP8 delayed** 配置 / ckpt 与磁盘清理策略 → 给 12.5 天长跑降风险。
>
> **纪律**：
> - 🚫 **本块只要"提案"**：写进 `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`（新增「空窗提案」节）**或** `MEMORY_PRETRAIN_2B.md`，然后 git commit+push；**未经运维批准，不得启动任何训练/长跑**。
> - 🚫 **不占 GPU2–7**；🚫 不改 P-5b recipe、不回训、不囤无关 ckpt；🚫 **绝不 kill watchdog loop**。
> - **P-8 状态不变**：仍暂缓（前置未齐前不启动，见下方 P-8 节）。
> - 每条提案都要有**判据**（怎么算成功/失败）+ **时间盒** + **可否中断**。



---

### 🆕 运维指令 · 2026-10-07（📊 **交付：昨夜工作汇报 HTML**）· 高优先 · **用户直令** · 非实验

> **用户令（2026-10-07）**：「关于**昨夜（10/6 22:00 – 10/7 08:00）**的工作，**pretrain / vision / data / harness 各自写一个 html 报告**」。
> ⇒ **本项 = 本轮唤醒第一件事**；🚫 不跑新实验、🚫 **不打断正在跑的训练 / 下载 / 评测**（只「读日志 + 写报告」）。

**① 产出（1 份）**：`doc/BaiZe-ISEDA2027/report_10_07_pretrain_overnight.html`
　**自包含**：单文件 / 内联 CSS / **零外部依赖**（无 CDN、**无任何被引用的 `http(s)://` 资源**）；**HTML 本体 ≤200KB**（图片文件另计）；字体栈沿用 `report_10_06.html`。
　🖼️ **允许「HTML + 同目录图片」**（见 ⑥）：数据图优先**内联 SVG**；确需位图 / 文生图 ⇒ 在 HTML 旁建 `report_10_07_pretrain_overnight_assets/`，用**相对路径**引用、**离线必须可开**；位图**一律 JPEG `.jpg`、长边 ≤1280px**（见 ⑥）。

**② 窗口 = `2026-10-06 22:00 → 2026-10-07 08:00`（本地时区）**
- **严格按窗口取数**（昨夜这 10h）；窗口外的内容若要提及，**必须标「窗口外·背景」**。
- ⚠️ **若你写报告时还没到 08:00** ⇒ 写到当下即可，并在 HERO 标 **`数据截止 hh:mm`**（**不要为凑整点而干等**）。
- 先自己把窗口内提交拉出来（本线 commit message 都带前缀，可直接 grep）：
```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
git log --since=2026-10-06T22:00:00 --until=2026-10-07T08:00:00 \
  --date=format:'%m-%d %H:%M' --pretty=format:'%h %ad %s' | grep -i 'pretrain'
```

**③ 章节（顺序固定 —— 四线统一，便于并排对照）**
1. **HERO**：`BaiZe pretrain 线 · 昨夜工作汇报` + 窗口 + **数据截止时刻** + **一句话结论**
2. **TL;DR** ≤5 条
3. **KPI 表**：`指标 | 22:00 起点 | 08:00 现值 | Δ | 备注` ＋【**本窗口有无实质产出**：有 / 部分 / 无】+ 一句说明
4. **时间线**：`hh:mm — 动作 — ✅完成 / ⏸等待 / ❌失败`（取日志 / 心跳 / `MEMORY_PRETRAIN_2B.md`）
5. **证据**：原始命令 + 输出片段（`<pre>`）；**失败与异常必须贴**（异常才是运维要看的）
6. **卡点 / 未完成**：如实写「卡点 + 需要什么」；🚫 不许凑数
7. **今晨现状**：进程 / GPU / 产物 一览 ＋ 下一轮计划
8. **窗口内 commit 列表**（② 命令的输出）

**④ 硬约束**
- **只写事实、数字必须真**；拿不到的写「无数据」。🚫 **禁止编造 / 用估算冒充实测** —— 运维会逐条对账。
- **「等待 / 空转」的时段必须显式标出**（`⏸ 等待中（原因）`）；🚫 **不许拿窗口外更早的成果充数**。
- **自检**：① **外链资源检查** ⇒ `grep -nE '<(img|script|link|iframe)[^>]*(src|href)="https?://|url\(https?://' <报告>` 与 `grep -n '@import' <报告>` **必须都为空**（**正文字里出现 URL 不算违规**，被引用的外部资源才算）；② HTML 本体 `wc -c` ≤200KB（图片文件另计）；③ **图片自检（若配图）**：`identify report_10_07_pretrain_overnight_assets/fig*.jpg` ⇒ **长边 ≤1280 且全为 JPEG**；`ls report_10_07_pretrain_overnight_assets/*.png` ⇒ **必须为空**（不留 PNG 原件）；单图 ≤400KB、总量 ≤4MB。

**⑤ 收尾**：按「收尾铁律」commit + push（前缀 `pretrain 汇报: …`），并在 `MEMORY_PRETRAIN_2B.md` 记 1 行指针。
> 📦 **体积提醒**：插块后本任务书 ≈**34.8KB（已超 32KB）** ⇒ 按「体积维护规程」**先自己滚动归档到 ≤32KB 再提交**（只搬迁已闭合块、留 1 行指针）；**确切字节以你自己 `wc -c` 实测为准**。

**⑥ 附图（🖼️ **按需** —— 用户 2026-10-07 追加令：你的 MCP 工具包里有**文生图**工具）**

> **用不用由你判断 —— 不强制**（别为配图本末倒置）；**图只为「让人一眼看懂」，不为好看**。没有值得配的图就老实写「本窗口无适合配图」。

- ✅ **适合配**：架构 / 数据流图 · 时间线（谁占卡、谁在等）· 管线示意（如 **NCCL 的 PIX/PXB/NVH 拓扑**、DP/TP 并行与通信路径）· 概念差异图。
- 🚫 **三条铁律（违反比不配更糟）**：
  1. **图只是辅助** —— **所有关键结论必须由表格 / 文字 / 原始输出（`<pre>`）承载**；正文引用的数字 🚫 **不得只存在于图里**（tok/s、busbw、Δp 一律要文字/表里有）。
  2. 🚫 **严禁用文生图「编」数据图** —— 曲线 / 柱状 / 数值分布**必须由真实实测数据**生成（内联 SVG 或 matplotlib）；文生图**只能画示意图**，caption 必须标 **【示意图·文生图】**，实测图标 **【实测数据】**。
  3. **图片必须落本地文件并 commit** —— 工具若只返回 URL ⇒ **先 `curl -o` 下载到本地再引用**；HTML 里 🚫 **禁止出现被引用的 `http(s)://`**（离线必须能打开）。
- 📁 **位置 / 格式 / 体积（2026-10-07 追加令②：限分辨率 + 一律 JPEG）**：目录 `doc/BaiZe-ISEDA2027/report_10_07_pretrain_overnight_assets/`，文件名 `fig1_<主题>.jpg`。
  - 📐 **分辨率：长边 ≤1280px**（推荐 1024×768 / 1280×720）—— **生成时取最小可用档，🚫 禁 1920 / 2560 档**。
  - 🖼️ **格式：JPEG `.jpg` —— 🚫 禁 PNG**（质量 q≈85；线条 / 文字示意图 JPEG 会有轻微噪点，故取 85 而非 70 ⇒ **数据图仍首选内联 SVG**，最锐利且零体积）。
  - 📦 **单图 ≤400KB、总量 ≤4MB**（HTML 本体 ≤200KB 另计）。
  - 🔧 **落盘两步（生成 ⇒ 必须本地缩放转码，不许直接引用原图）**：`magick raw.png -resize '1280x1280>' -strip -quality 85 fig1_主题.jpg`（ImageMagick）；或无 ImageMagick ⇒ `ffmpeg -y -i raw.png -vf "scale='min(1280,iw)':-1" -q:v 3 -map_metadata -1 fig1_主题.jpg`；或 PIL ⇒ `im.thumbnail((1280,1280))` 后 `im.convert('RGB').save('fig1.jpg','JPEG',quality=85,optimize=True)`。
  - ✅ **自检**：`identify fig*.jpg`（无 identify 用 `file`）⇒ **长边 ≤1280 且全为 JPEG**；`ls report_10_07_pretrain_overnight_assets/*.png` ⇒ **必须为空**（不留 PNG 原件）；HTML 内按 `fig1/fig2/...` 编号引用，**每图配 1 行 caption**。

**⑦ 本线窗口内重点（自己核对；**没有就写「无」**，不许编）**
- ① **A / B / D 三项**昨夜各跑到哪、**结论是什么** —— 尤其 **B 的「RoPE 只影响 4 层 ⇒ 收益可能有限」是否被实测证实/证伪**（该判决必须写清）。
- ② **NCCL / NVLink 拓扑核查**结论（`report_pretrain_nccl_topo.html`）：**当前实际通道构成**（NVLink / P2P / NET 各占几成）、**最佳 env 组合**、**相对 baseline 的 tok/s 提升 %**、**能否迁移 8 卡**。
- ③ **训练提速候选清单**：昨夜实测了几条、各自数字 + 「可否迁移 8 卡」。
- ④ ⚠️ **GPU0-1 昨夜的真实占空**：多条提交都写「全 8GPU 被 data BO 占用」⇒ **如实统计你被抢占的时段/小时数**（这**就是**本窗口「无实质产出」的原因，要写清楚，不要藏）。
- ⑤ **P-8 前置**（base 全量 / 配比定稿）现状与 ETA。



---
## [归档自 BAIZE_PRETRAIN_2B_TASK.md · 2026-10-07③ 唤醒滚动] §运维指令·2026-10-07②（长上下文推理成本矩阵 128K-1M）原文

### 🆕 运维指令 · 2026-10-07②（📐 **【长上下文推理成本矩阵】sglang 下 BaiZe(Mamba2-hybrid 2.220B) ⚔ MiniCPM5-2B(dense 2.512B) @ ctx {128K, 256K, 512K, 1M}**）· **用户直令** · 高优先（**不抢占 data BO**）

> **用户令原文（2026-10-07）**：「在**更长的上下文：128k / 256k / 512k / 1m**，**和 sglang 框架下**对比 **BaiZe（Mamba2-Hybrid-2B）** 和 **Dense（MiniCPM5-2B）** 架构的**推理成本**（**包括但不限于：吞吐率、prefill/decode 速度、显存占用等**）」。
> 🧭 **溯源（运维认账）**：本需求**此前被窄化**，两块各只做了一半 ——
> ① **P-9.11（10-05）** sglang 两模型矩阵**只到 64K**（128K 当时因 **prompt 构造 bug** 被拒；P-9.11D 已更正为「可跑」但**矩阵格从未回填**，`p911_*_results.json` 里 128K 仍是 `null/0 completion`）；
> ② **B1 扩展（10-06）**「ctx 扩到 256K/512K/1M」**只测了 hybrid 单模型**的 PPL/耗时/显存（`baize_b1_longctx_extend.py`）。
> ⇒ **「两模型 × {128K,256K,512K,1M} × sglang」的整块矩阵至今空缺 —— 本轮补齐，这是本块的唯一目标。**

**⓪ 先归档（把本任务书压回 ≤32KB —— 当前 ≈33KB，确切字节以你自己 `wc -c` 为准）**：把**已闭合**的下一块「📊 **交付：昨夜工作汇报 HTML**」（**已由 #164 交付**）**原文**搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md` + 留 1 行指针，**然后**执行本块。

**① 测试矩阵（同一 sglang 栈、两模型逐格对齐）**
- **对象**：BaiZe = `p3_hybrid/iter_0005000`（HF `nemotron_h`, 2.220B, 56 层 / 仅 4 层 attention）⚔ Dense = `p3_dense/iter_0005000`（HF Llama, MiniCPM5-2B 2.512B）——**与 P-9.11 同 ckpt，便于拼接**。
- **档位**：ctx ∈ {**131072, 262144, 524288, 1048576**} × bs ∈ {1, 8}，`gen_len=64`。⏱ 时间不够时**最低交付 = bs=1 × 4 档 × 两模型**，bs=8 可只记「可跑 / OOM」。
- ⚠️ **prompt 一律 tokenizer 精确计数**（`len(tok(prompt))`，目标 = `ctx − 64`），**每格贴实际 token 数**；🚫 严禁再用字符数估算（P-9.11 的 128K 就死在这里）。
- **服务端口径**：`--context-length` 按档设 + `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`；hybrid 加 `--mamba-ssm-dtype float32`；**`--mem-fraction-static` 取低预分配（如 0.3）并在表头写明**（0.85 会把 VRAM 差异掩盖掉 —— P-9.11 的 H3 就是这么被否掉的）；**两模型 flag 必须完全一致**。
- **config 口径（逐行标注，不许混）**：hybrid 原始 HF config 只有 `max_pos=4096` ⇒ ≥256K 请沿用 **B1 的 ABF 写法（推理时 `rope_theta=1e6, max_position_embeddings=1048576`，见 `baize_b1_longctx_extend.py`）**；dense 原始为 `max_pos=131072, rope_theta=5e6` ⇒ **若 256K+ 需 YaRN/rope_scaling 才能起服，如实写「需外推配置」并标为口径差异**（🚫 不许偷改配置不写）。

**② 每格必采（缺项就写「未测」）**
`HTTP(200/400/500) · TTFT(s) · prefill 时间(s) · prefill tok/s · decode tok/s（≥32 step 均值）· e2e 延迟(s) · 峰值显存（nvidia-smi 采样 ＋ 服务端 KV/state 估算）· OOM/超时原文`

**③ 交付（4 件）**
1. `run/p911e_longctx_cost_results.json` —— 逐格原始数据（含 prompt token 数 / flags / config 口径）；
2. **比值表**：`hybrid ÷ dense` 的 **TTFT / prefill tok/s / decode tok/s / 峰值显存 逐档**，并给出 **crossover ctx**（prefill、decode 各一个）；
3. **自包含 HTML** `doc/BaiZe-ISEDA2027/report_pretrain_longctx_infer_cost.html`（内联 SVG `ctx → 比值` 曲线；零外链；≤200KB）；
4. `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新增节 + **一句话可引用结论**（**劣势如实写**：短 ctx dense decode 更快；谁在哪个档 OOM）。

**④ 资源与铁律**
- 🥇 **测试场地 = `.12` GPU1–7（用户 2026-10-07 直令：7 张空卡全用上、并行尽快测完）** —— vision 的 `lp 协议 A/B 桥接`（PID 807654）**只占 GPU0**（2.4GB / 39% util，NFS I/O bound，**ETA ~10:00–11:00**）⇒ **借 GPU1–7**。🚫 **不碰 GPU0**、🚫 **绝不 kill PID 807654**。
- 🚀 **一条命令扇出（脚本已入库：`run/p911e_matrix_launch.sh`）**：`ssh 10.239.2.12 "nohup setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/p911e_matrix_launch.sh </dev/null >/tmp/p911e_main.log 2>&1 &"` —— **默认波次**：**GPU1–4 = hybrid @ 128K/256K/512K/1M**、**GPU5–7 = dense @ 128K/256K/512K**（**dense 1M 走第 2 波**：`bash p911e_matrix_launch.sh "4 dense 1048576"`）。逐格产出 `run/p911e_results/p911e_<model>_ctx<ctx>_gpu<g>.json`（**TTFT / prefill tok·s⁻¹ / decode tok·s⁻¹ / e2e / peak VRAM / prompt 实 token 数 / OOM 错误串**），你 merge 成 ③ 的 `p911e_longctx_cost_results.json`。**目标墙钟 ≤45 min**（7 格并行；单格 = 载模型 ~1–2 min + 4 档请求）。
- ✅ **`.12` 可行性 = 已实测，不是推测**：env 与 ckpt **全在 NFS 共享路径** —— `/nas_train/app.e0031982/miniforge3/envs/{sglang,vllm}`（P-9.10① 已 `ssh .12` 查证「同样有 `vllm`」sglang 0.5.9 ✅；脚本**自动择优**，`.12` 只需能 `import sglang`）、`…/nemo_experiments/p3_{hybrid,dense}/hf_iter_5000` ✅。flag 照抄：`--mem-fraction-static 0.3` + `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1` + `--attention-backend flashinfer` + hybrid 加 `--mamba-ssm-dtype float32`。⚠️ **7 个 server 同时载模型会压 NFS**（vision 的 bridge 正好是 NFS I/O bound）⇒ 脚本默认 **`STAGGER=20s` 错峰**；若 bridge 的读带宽/进度明显被拖慢 ⇒ `STAGGER=40` 或降到 4–5 并发（**别为了本项把 vision 的 ETA 拖垮**）。
- ⏰ **交还铁律**：**≤45 min 跑完即交还**（**硬天花板 11:00**）；脚本每格结束**自动 kill 该卡 server** 并打印该卡 `memory.used`；**收尾必须**核 `nvidia-smi` 上 GPU1–7 已无自己的进程 + 在 `run/GPU12_ALLOC.md` 流水写「已归还 hh:mm」。**优先级**：vision 训练臂/桥接 > 本推理评测（vision 要卡 ⇒ **无条件让**）。预算 **≤3h**。
- 📌 **先写死预期，避免事后挑数**：hybrid **1M 已知可跑**（B1：prefill 172.4s / 峰值 34.68GB）；**dense 1M 预期 OOM**（KV≈90GB）⇒ **OOM 就记 OOM**，「**dense 在 xxK 处 OOM、hybrid 到 1M 仍可服务**」即本报告**核心结论**。
- ✅ **可直接复用、不必重测**：4K/16K/64K 的 P-9.11 数据（prefill **2.18×**、decode **1.18×** @64K×bs1，`p911_hybrid_results.json` / `p911_dense_results.json`）**只引用**；若本轮重测，须标注「新口径」并说明与 P-9.11 是否可比。
- 收尾按「收尾铁律」commit + push（前缀 `pretrain 长ctx成本: …`）+ `MEMORY_PRETRAIN_2B.md` 记 1 行指针。



---

## [ARCHIVED 2026-10-07 #178] 运维指令 ⑤④③（2026-10-07，均已完成）

### 🆕 运维指令 · 2026-10-07⑤（**① bf16 SSM 重跑 128K–1M 矩阵 ② 按 research1 的公平协议重做 BaiZe⚔dense ③ 按 research2 找训练提速 ④ 按 research3 找训练效果提升**）· **用户直令** · 高优先

> **用户令原文（2026-10-07 21:2x）**：「**① 用 bf16 SSM 重跑 128K–1M 矩阵；② 参考自己的分析（`report_pretrain_research1_fair_eval`），用更公平的方式比较 BaiZe 和 dense；③ 看 `report_pretrain_research2_train_speed`，训练速度是否有提升空间；④ 看 `report_pretrain_research3_train_quality`，训练效果有否提升空间。**」
> 🟢 **资源已就绪**：**`.29` 全 8 GPU 空闲**（你 #176 自己 ssh 核验 8×0 MiB）⇒ **T1/T2 现在就能跑，用 `.29`，不必再抢 `.12`**。

**T1 ⭐ 用 bf16 SSM 重跑 128K–1M 矩阵（修正 P-9.11-E）**
- 动机是你自己量化的：**`float32` SSM 人为压低 hybrid prefill 40%**（bf16 10820 vs float32 6484 tok/s）。
- **重跑**：hybrid @ ctx ∈ {**128K, 256K, 512K, 1M**}（时间允许再 2M@0.6/0.85），**`--mamba-ssm-dtype bfloat16`**；**dense 同排对照**（同 attention backend / 同 mem-fraction 口径）。
- **产出**：修订 `report_pretrain_longctx_infer_cost.html`（**新增「bf16 vs float32」对照表 + 把 float32 口径明确标为「作废/仅对照」**）+ EXPERIMENTS P-9.11-E 节修订。
- **判据（预注册，不许事后改）**：**若 bf16 下 hybrid 反超 dense ⇒ 必须如实改写原「dense 3.3× faster」结论**（那是口径 artifact）。

**T2 按 research1 的「公平对比协议」重做 BaiZe ⚔ dense**
- 严格照你自己在 `report_pretrain_research1_fair_eval.html` 里定的协议：① 两模型 **同 attention backend（flashinfer）**；② **显存口径改用「KV/SSM pool tokens + 活跃 KV」**，**不用 nvidia-smi 预分配值**；③ **mem-fraction 固定并报 pool 大小**；④ **显式标注 SSM dtype**；⑤ **tokenizer 精确计数**；⑥ **warmup + median-of-N**，prefill/decode 分离。
- **产出**：`report_pretrain_longctx_infer_cost_v2.html`（或就地修订），**口径表写清哪些「不可混比」**。
- **可与 T1 合并执行**（一次起服、两套口径）。

**T3 按 research2 找「训练速度」提升空间**
- 基于 `report_pretrain_research2_train_speed.html` 出**可执行短名单**（每条：预期增益 / 成本 / 风险 / **可检验判据** / 时间盒 / 优先级），并**挑 1–2 条最稳的先做**（`.29` 免费）。
- 约束：**P-9.13 已证「env 无提速、249K tok/s 是 launcher 暴露参数上界」** ⇒ 候选应聚焦 **FP8 / 融合 kernel（mamba2+conv、TE）/ recompute / CUDA graph / 数据管线 / TP·DP 拓扑**；**优先「不改 recipe 的运行时/并行/IO 项」**。

**T4 按 research3 找「训练效果」提升空间**
- 基于 `report_pretrain_research3_train_quality.html` 出短名单（目标 = **8 常识 + 6 复杂 + agent/SWE-Bench**），每条给**判据 + 成本 + 风险 + 优先级**；**先出分析、不必马上烧 GPU**。
- 重点参考你自己的实测：**A 36/36 里 5/6 贴地板、仅 BBH 有微弱信号** ⇒ 优先 **数据/课程/长上下文/指令与 CoT 数据** 这类**高杠杆**项，而不是继续微调 lr。

**顺序**：**T1+T2（GPU，`.29`，今晚）→ T3/T4 短名单（纯分析，可并行）→ T3 的 1–2 条低风险实验（T1/T2 完成后在 `.29`）**。
**铁律**：不改 P-5b recipe、不回训、不存 ckpt；🚫 绝不 kill watchdog loop；**数字必须真**（口径变了就明写、不许拿旧口径充新结论）。
> 📦 体积提醒：本块加入后 `BAIZE_PRETRAIN_2B_TASK.md` ≈35KB（**<40KB 红线**）⇒ 收尾前先归档已闭合旧块。

### 🆕 运维指令 · 2026-10-07④（**🖥️ 无卡窗口：5 份「研究型」HTML 报告** — web search ＋ 内联 SVG／文生图）· **用户直令** · 高优先

> **用户令原文（2026-10-07）**：「**pretrain：既然没有 GPU，但总有 web search 和文生图，可否做一些研究。安排下列每个方向写个 html 报告**」（5 个方向见 ①）。
> **时序**：本块 = **无卡时段的填充任务（纯 CPU / 联网，不占 GPU）**；**③（2M–16M 实测 ＋ 显存归因诊断）依然有效** —— **一旦有卡，优先插空跑 ③**，再回来做本块。
> 🔴 **2026-10-07 11:35 用户令（覆盖本节时序）**：**③ 没卡没关系、不用等** —— **④（这 5 份研究）现在就是第 1 优先，立刻开做**；**不得因 ③ 无卡而空转**。③ 继续挂着等卡（vision 消融 ~16:30–17:00 / data BO ~21:56 释放后再补跑）。
> **工具**：你的 MCP 有 **`cimi_search` / `cimi_fetch`（联网检索+读原文）** 与 **文生图** —— 本块主要靠它们。
> ⚠️ **收尾修正（2026-10-07 14:4x · 运维）**：**research4 目前出了两份** —— `report_pretrain_research4_long_ctx.html`（46.9KB，"Long-Context Extension"）与 `report_pretrain_research4_longctx_1m_p8.html`（26.1KB，"Long-Context 1M: What P-8 Must Do"）。**以我指定的 `..._longctx_1m_p8.html` 为准**；请把另一份的**独有内容并入**它后**删除冗余文件**（或申请改名为 `..._appendix` 并在 MEMORY 注明）—— **🚫 不许留两份同号报告**（会造成"到底哪份是 r4"的歧义）。收尾照常 commit+push。



**① 五份报告（每份一个话题、一份 HTML，落到 `doc/BaiZe-ISEDA2027/`）**

| # | 方向 | 交付文件名 | 必须挂靠的「我们已有实测」 |
|:--|:--|:--|:--|
| 1 | **如何公平地对比评测 hybrid vs dense 的推理速度 & 成本** | `report_pretrain_research1_fair_eval.html` | **P-9.11-E（mem-frac 0.3 / float32 SSM）** vs **P-9.11（0.85 口径）结论相反**；dense KV pool=**455K tokens**；**B1: attention 占 prefill ~77%** |
| 2 | **提升 hybrid-2B 训练速度的机会点** | `report_pretrain_research2_train_speed.html` | P-9.13（**249K tok/s 上界 / env 无提速**）、P-9.12（NCCL 已 NVLink）、P-9.5 profiler 5-way 归因、P-9.9 FP8 |
| 3 | **提升 hybrid-2B 训练效果的机会点**（8 常识 ＋ 6 复杂 ＋ agent/SWE-Bench） | `report_pretrain_research3_train_quality.html` | **A 36/36（5/6 贴地板，仅 BBH 有信号）**、P-6 scaling、P-3 五点全胜；data 线在搜配比 |
| 4 | **为支持 1M 长上下文，P-8 预训练阶段要做什么（YaRN/ABF/长文课程/数据配比…）才能尽快让「大海捞针」得合理分（现 0）** | `report_pretrain_research4_longctx_1m_p8.html` | **B：passkey 4K/8K=0%**；**B1：1M PPL 55.42 无退化、≥512K attention 占 ~77%**；D：VRAM 5.35GB；⭐ **我们的 RoPE 只作用于 4/56 层** |
| 5 | **架构锁定 hybrid-2B 后，是否还能搜（NAS）** | `report_pretrain_research5_arch_nas.html` | 2B 架构搜索（`BAIZE_2B_ARCH_RESULT.html`）、R8 六架构四指标、`MAMBA2_HYBRID_2B_FEASIBILITY_REPORT.html` |

**② 每份统一骨架（6 节）**
1. **TL;DR**（3–5 条结论）；2. **我们的现状**（把上表「已有实测」贴数字 + 标出处文件/commit）；3. **外部证据**（**一手优先**：官方仓库/官方文档/arXiv；**每条给 URL ＋ 版本或年份**；二手只能作线索并标「**二手·未核**」；**核不到就写「未核实」——🚫 不许编造**）；4. **候选清单**（每条：① 动机 ② 预期收益 ③ 成本/风险 ④ **可检验判据** ⑤ 优先级）；5. **推荐路线 ＋ 时间盒**（明确「先做哪 1–3 条、为什么」）；6. **引用清单**。

**③ 证据分级（每条结论都要标）**：`【实测·本项目】` / `【一手文献·URL】` / `【二手·未核】` / `【推测·未验】`。

**④ 格式（沿用 house style，参照 `report_10_06.html`）**
- **自包含**：内联 CSS、**数据图优先内联 SVG**、零外链、**HTML 本体 ≤200KB**。
- **按需附图**（用户令）：文生图 / SVG 均可；**🚫 严禁用文生图「编」数据图**（曲线/柱状/数值分布**必须由真实数据**生成；文生图只能画**示意图**，caption 标 **【示意图·文生图】**，实测图标 **【实测数据】**）；位图**一律 JPEG、长边 ≤1280、q85**，单图 ≤400KB / 总量 ≤4MB；**图片落本地并 commit**，HTML 内禁止被引用的外链。
- 收尾按「收尾铁律」commit+push（前缀 **`pretrain 研究: …`**）＋ `MEMORY_PRETRAIN_2B.md` 记 1 行指针。

**⑤ 顺序与时间盒**：**按用户编号 1→2→3→4→5**，**一份完成即 commit**（可分多轮唤醒）；**r1 / r4 最影响决策，最优先**。纯 CPU/联网，**不占 GPU、不下大文件、不改论文、不改 P-5b recipe**。

**⑥ 铁律**：只写事实、**数字必须真**、**禁止编造或用估算冒充实测**；外部结论**必须可核**（URL＋年份）。
> 📦 **体积提醒**：本块加入后 `BAIZE_PRETRAIN_2B_TASK.md` 约 **≈37KB（>32KB）** ⇒ **本轮收尾前先把已闭合旧块归档到 ≤32KB 再提交**（确切字节以你自己 `wc -c` 为准；未到 40KB 红线）。

### 🆕 运维指令 · 2026-10-07③（**hybrid ctx 继续扩 2M/4M/8M/16M** ＋ **「显存为何恒定」归因诊断**）· **用户直令** · 高优先

> **用户令原文（2026-10-07 10:30）**：「安排 pretrain 在 hybrid 这边**继续提升 ctx 到 2m、4m、8m、16m**」＋ 三个追问题（见 **③**）。
> **⚠️ 资源现状（运维核实；与你原以为的不同 —— 先读这条）**：`.12` GPU1–7 **你已于 09:44 提前归还**；**vision 已于 09:52 在 `GPU12_ALLOC.md` 申请并占用 8 张卡**（② mask-ratio 消融，PID 1752298，**ETA ~14:30**）⇒ **`.12` 现无空卡**；`.29` 8 张被 data Round2 BO 占（62.6GB/卡，至 ~19:00）。
> ⇒ **第 0 步 = 找卡**（按 `GPU12_ALLOC.md` 铁律：**vision 训练臂 > pretrain 推理评测**）：① 看 `.12` vision 消融**是否出现空窗/单卡余量**（其 16.4GB/卡，但**已预分配**；🚫 **不许 kill、不许强占**）；② **确无卡 ⇒ 如实记「无可用 GPU，未执行」**，脚本备好（复用 `p911e_matrix_launch.sh` 只改 ctx 档），**一旦有 1 张空卡立即补跑**；③ 🚫 不抢 data BO / vision。

**① 测量（用户令）**：hybrid 单独扩 **ctx ∈ {2M, 4M, 8M, 16M}**（`2097152 / 4194304 / 8388608 / 16777216`），bs=1、`gen_len=64`、**tokenizer 精确计数**；沿用 P-9.11-E 的 sglang flag，并**逐档同时记 §③ 的诊断量**。
- 逐格采：`HTTP · TTFT(s) · prefill(s) · prefill tok/s · decode tok/s · e2e · 峰值显存(nvidia-smi) · **服务端 max_total_num_tokens / KV pool 字节数** · host RSS · OOM/超时原文`。
- **时间盒**：能做几张算几张（优先 **2M → 4M → 8M → 16M**）；**未做的如实标「未测」**，🚫 不许外推冒充实测。

**② 交付**：扩 `run/p911e_longctx_cost_results.json` + 刷新 `report_pretrain_longctx_infer_cost.html`（加 2M–16M 档）+ `EXPERIMENTS` 增节。

**③ ⭐ 诊断课题（用户三问；**必须给证据/原始日志，不许只给结论**）**
> 用户问：「VRAM 居然**不随 ctx 增加**（恒 ~25GB），无论 O(n)/O(n²) 这都不正常吧？」「在这么长的上下文里 hybrid 居然相对 dense **没有明显优势**，这是怎么回事？」「现有 **sglang 参数是否用了虚拟内存之类的方案**，才让 hybrid 速度反而低于 dense？」
1. **V1 读池子**：贴每格 sglang **启动日志**的 `max_total_num_tokens` / `max_running_requests` / `available_gpu_mem` ⇒ 验证 **`--mem-fraction-static 0.3` 在启动时把「权重 + KV pool + overhead」预分配 ≈ 80GB×0.3 ≈ 24GB，且 pool 被尽量撑满** ⇒ **nvidia-smi 的 ~26GB 是「预分配读数」，与 ctx 无关**（也是 dense 在 prompt 504K > pool **455K tokens** 时被拒的原因）。
2. **V2 mem-fraction 扫描**：同模型同 ctx 跑 **mem-fraction ∈ {0.3, 0.6, 0.85}** ⇒ 看峰值**是否随之变**；并**对比 P-9.11（0.85 口径）的 hybrid 128K×bs1=13GB vs dense=61GB**（那组才显真实差异）⇒ 判定「恒定」是**口径假象**还是真 O(1)。
3. **V3 排除「虚拟内存/paging」**：写明 sglang 的 **PagedAttention = 显存内分页**（block 管理 KV），**不是把 KV 换出到 host/虚拟内存**；**取 host RSS × ctx 曲线**（不涨 ⇒ 非 host 侧换页）；若发现任何 offload/swap 开关被开 ⇒ 贴配置原文。
4. **V4 拆 hybrid「没优势」**：① **4 层 attention 的时间占比**（**B1 已测 ≥512K 时 attention 占 prefill ~77%** ⇒ **hybrid 退化为准 O(n²)**）；② **`--mamba-ssm-dtype float32` 的代价** —— 跑一次 **bf16 SSM** 对照，量 prefill/decode 差多少；③ 结论要分清：hybrid 的优势应在 **容量（能服务到 1M+）/ 显存**；**速度**上 dense 的 flashinfer attention 在中长 ctx 更快是**预期行为**。
5. 报告新增一节 **「为什么 VRAM 恒定 ＋ hybrid 为何未显速度优势」**，**每条都给可复现命令/日志**。

**④ 铁律**：🚫 不 kill 别人进程 / 不强占卡；不改 P-5b recipe、不回训、不存 ckpt；🚫 绝不 kill watchdog loop；如实记 OOM/未测。
> 📦 **体积提醒**：本块加入后 `BAIZE_PRETRAIN_2B_TASK.md` 约 **≈33KB（>32KB）** ⇒ **本轮收尾前先把已闭合旧块归档到 ≤32KB 再提交**（确切字节以你自己 `wc -c` 为准；未到 40KB 红线）。

---

> 📦 归档时间：2026-10-09（pretrain agent 自行归档，T3 完成后收尾）

### 🆕 运维指令 · 2026-10-08（🔬 **数据配比 Round 3 搜索：接收 data agent 交接，在 P-8 前跑完**）· **R3 已完成 — 归档至 git 历史**

> **背景**：data agent 已完成 R3 方案定型，正式交接给 pretrain 团队执行。
> **交接文档**：`run/BAIZE_DATA_R3_TASK.md`（👈 **你启动前先通读此文**，以下是指令摘要）。
> **为什么现在做、而不是等 P-8 再搜**：P-8 的前置（全量分词 + GPIC 下载）至少还需要 2–3 天；
> 而 R3 只需要小样本分词（~30 分钟）+ 100 trial BO（~19.5h），**8 卡空闲期正好利用**，
> 跑完直接决定 P-8 的 Stable 段配比，**不占 P-8 启动后的时间**。

**① R3 vs R2 的本质区别**
| 对比项 | R2（已完成） | R3（本次） |
|:--|:--|:--|
| 搜索空间 | 3 维 `base:code:math` | **6 维** `ultrafineweb_en / ultrafineweb_zh / ultrafineweb_l1_en_hq / UltraX-Preview / UltraData-Code / UltraData-MATH` |
| 评测 | `--limit 500`（sampled） | **全量** 73106 requests（无 `--limit`） |
| trial 数 | 200 | **100**（预算压缩到 ≤24h） |
| D/trial | 0.5B | **1B**（信噪比更高） |
| 代理规模 | d=128/L=14 (18.36M) | **同**（不换代理） |
| 前置 | 已有 8 源分词 bin | 需跑 **小样本分词**（6 源 × 2 parquet，~30 min） |

**② 执行顺序（对照交接文档 §6）**

```text
Step 0  ⭐ 先通读 run/BAIZE_DATA_R3_TASK.md（尤其是 §5 代码改造规格 + §3.2 小样本分词路径）
Step 1  备份 R2 脚本 → 改出 baize_mix_optuna_r3.py（按 §5 改造）
        - 搜索空间从 3-dim 改为 6-dim（6 个单源名）
        - 新增 build_blend_stable() 函数
        - objective = lm_eval 全量 8 任务均分（无 --limit）
        - 沿用 Optuna TPE+MedianPruner + MBS=16 + GBS=16 + seq=2048 + D=1B
Step 2  跑 baize_tokenize_r3_sources.sh（6 源小样本分词, ~30 min）
        - 数据源位置见交接文档 §3.1 Table
        - 每源取 2 parquet（路径已列出），参考 baize_mix_tokenize_base.sh
        - 输出到 {BASE}/data/r3_sources/
Step 3  python baize_mix_optuna_r3.py --phase stable --n-trials 100 \\
            --gpus 0,1,2,3,4,5,6,7   # ~19.5h（8 卡满）
Step 4  等 100 trial 完成（第 13 轮最后 4-trial 收尾）
Step 5  top-K（K≥5）全量 lm_eval 验证
Step 6  输出 r3_best_blend.txt → 供 P-8 Stable 热身引用
```

**③ 关键改动点（相对于 R2 的 `baize_mix_optuna_r2.py`）**
- 搜索空间：`ultrafineweb_en, ultrafineweb_zh, ultrafineweb_l1_en_hq, ultrax_preview, ultradata_code, ultradata_math`
- 不搜索 `decay` 段（Decay 段保持 R2 的 3-dim 原样，R3 只搜 Stable）
- 每 trial D=1B 而非 0.5B（训练步数 30518 步 @ MBS=16, GBS=16, seq=2048）
- `lm_eval` 不加 `--limit`（全量 73106 requests，~3.6 分钟/trial）
- 末轮不足 8 trial 时 `--gpus` 改传实际空闲卡号

**④ 预算确认（交接文档 §2 实测锚点）**
| 操作 | 单 trial | 100 trial |
|:--|:--|:--|
| 训练 (1B tok, MBS=16, 166ms/step) | 84.4 min | — |
| HF 转换 | 2 min | — |
| 全量 lm_eval（8 任务, 无 limit） | 3.6 min | — |
| 单 trial 合计 | ~90 min | — |
| 100 ÷ 8 GPU = 13 轮 × 90min | — | **~19.5h ≤ 24h** ✅ |

**⑤ 同期义务（不冲突的，可后台并行）**
- 论文更新（纯 CPU 工作）：等 R3 跑起来之后（Step 3 已启动、稳态运行后），**抽空做**，不占 GPU。
- R2 收官报告（纯 CPU 自包含 HTML 写作）：同理，R3 跑起来之后抽空做，不占 GPU。
- ⚠️ **不得因写论文/报告而延迟 Step 1–3**：R3 的主干是先改代码 + 分词 + 起跑，**写报告是后台 CPU 活**。

**⑥ 收尾**
- R3 搜索完成后（r3_best_blend.txt 已生成），把结果回写到 `DATA_MIX_RECIPE.md` 更新 Stable 段推荐配比。
- 在 `MEMORY_PRETRAIN_2B.md` 记录 R3 结论 + best trial 详情。
- **不 kill loop**：跑完后 `WAITING=1` 回原位等 P-8 启动令。

> 📦 本块加入后 TASK 约 28KB，仍 ≤32KB ✅。

### 🆕 运维指令 · 2026-10-08（📝 **更新论文 LaTeX：把 R2 实测数据写入 `4_llm_pretrain.tex` / `3_architecture.tex`**）· **用户直令：各线自己更新论文** · 高优先

> **用户令**：「让 pretrain，vision 和 data 更新一下论文。」
> ⚠️ **不要代笔写 LaTeX** —— 你只负责把你自己的实验数据填入对应的 `.tex` 文件，然后编译 `main.pdf`。
> ⚠️ **论文在 `BaiZe-ISEDA2027/` 目录下，与任务书同在一个 repo** —— 你直接可见可改。

**① 当前论文中 `4_llm_pretrain.tex` 已有 R1（S1–S5）的基础数据，但 R2 的大量新结果完全没有反映**。你需要审阅 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md`，判断哪些值得写入论文。

**② 建议更新的内容（自行判断，不一定要全写）：**
1. **长上下文能力**（B1 实验）：1M PPL=55.42 无退化 → 可补入 §4.2 或新增一段，说明 hybrid 的 long-context 优势（只需 4 层 attention 可见状态增长）。
2. **推理成本对比**（P-9.11 系列）：128K–256K 下 hybrid vs dense 加速比 2.8–4.3×（prefill 1.7–3.3×，decode 2.2–2.6×）→ 强化 Table~8 或新增一段。
3. **FP8 训练可行性**（P-9.8/P-9.9）：delayed FP8 可用于 P-8，但 tensorwise FP8 因 T1/T4 失败 → 可加一句预算说明。
4. **更新 Table~8（tab:archcomp）**：若有新的更精确的数据（如 decode gap 在 sglang 下的实测），可更新。
5. **Training throughput 数据**：P-9.7 定稿的 249K tok/s 可更新到相关位置。

**③ 格式纪律**
- 🚫 **不改 § 编号、不改 label、不改 cross-ref** —— 只更新数字、表格行、段落描述。
- ✅ **可以加子节**（`\subsection{...}`）/ 加段落 / 加表 / 加图 —— 但 label 和 cross-ref 不能冲突。
- **编译前先 `cd doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027 && rm -f main.aux main.bbl main.blg main.log`，然后 `pdflatex main && bibtex main && pdflatex main && pdflatex main`，确认 0 error。
- 编译后的 `main.pdf` **一起 commit**（审稿人看 PDF）。
- **git 前缀**：`pretrain 论文更新: ...`

**④ 本块不撤销之前的报告任务** —— 写报告和更新论文是两件事，**都要做**。
- 推荐顺序：**先更新论文（简短任务），再写报告（深度任务）**。

> 📦 本块加入后 TASK 约 24KB，仍 ≤32KB ✅。


### 🆕 运维指令 · 2026-10-08（📄 **R2 全线实验收官总报告 HTML**）· **用户直令：各线自己写报告** · 高优先

> **用户令**：「把任务下发给各 agent，由 agent 自己写报告，不要替代他们写。」
> ⚠️ **本线 R2 所有实验已完成**（P-1~P-9.13 全 ✅），长期空转心跳不是正事。**用户点名要 agent 自己写报告**。

**① 交付**：`report_pretrain_r2_final.html`（落 `doc/BaiZe-ISEDA2027/`）

**② 格式（沿用 house style）**
- **自包含**：内联 CSS + **数据图优先内联 SVG**；**零外链**；**HTML 本体 ≤200KB**。
- 位图一律 **JPEG、长边 ≤1280、q85**、单图 ≤400KB/总量 ≤4MB、**落本地并 commit**；🚫 严禁外链、🚫 严禁用文生图「编」数据图（曲线必须由 **真实实测数据** 生成）。
- 若引用已有报告（如 `BAIZE_PRETRAIN_RESULT.html` / `report_pretrain_research{1..5}.html`），只给链接指针，**不重复贴全文**。

**③ 建议 10 节**
1. **TL;DR**（3–5 条：架构锁定为 hybrid 56L/4-attn，LR 1e-3 WSD，val loss 2.2054，hybrid vs dense 加速比 2.8–4.3×@128K–256K，FP8 裁定为 delayed 可用于 P-8）；
2. **实验设计总览**：R1（架构搜索 S0–S5）→ R2（P-1~P-9.13），各阶段目的与预算；
3. **架构选型**：dense vs hybrid vs 其他，**hybrid 锁定为正式架构**（附 P-3 5000 步对比 + B1 1M PPL=55.42 无退化）；
4. **超参搜索**：P-1 LR 扫描（1e-3 最优）+ P-2 3-seed 复现（2.6739±0.0469）+ P-4 退火消融；
5. **FP8 裁定**：P-9.8 armA/armB + P-9.9 tensorwise → 结论：delayed FP8 可用于 P-8；
6. **长上下文能力**：P-9.11 系列（2M served / 4M timeout / 显存归因）+ 推理成本矩阵；
7. **提速实验**：T1 bf16-SSM（无差异 1.00×）/ T2 公平对比 / T3 短名单（C1 FP8-TP1 / C2 recompute+MBS4）/ T4 效果短名单（Q1 100B tokens / Q2 data mixture）；
8. **复杂推理**：A 36/36（BBH 峰值 14.26%@2.62B）/ B ABF（+2.71pp）/ D VRAM 5.35GB 恒定；
9. **对 P-8 的建议**：配方 88:8:4 / FP8 delayed / hybrid 架构 / 数据就绪条件；
10. **局限与诚实交代**：655M token 代理实验 / 未收敛 / 单 seed 方差 / 待正式训练验证。

**④ 纪律**
- **数字必须真**：每个数字可由 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` / 原始日志复算；
- **结论跑完即固化**：不新增实验、不改已有结论；
- **收尾按「收尾铁律」commit+push**（前缀 `pretrain R2收官: …`）；
- 写完本报告后，**不要回到空转心跳** —— 改做 **P-8 前置预研**（若运维尚未撤暂缓令，预研 P-8 recipe / 数据配方复算 / 训练脚本核验）。

> 📦 本块加入后 TASK 约 23KB，仍 ≤32KB ✅。如需归档，只归档下方已闭合旧块。


---

### 🆕🆕 运维指令 · 2026-10-09（⚡ T3 提速验证：recompute+FP8 on .29 空闲 GPU）· 用户直令

> **已闭合**：#238（2026-10-09 11:11）执行完毕。原文如下（未改）。

### 🆕🆕 运维指令 · 2026-10-09（⚡ **T3 提速验证：立即在 .29 空闲 GPU 上跑 C1/C2/C2+**）· **最高优先 — R3 BO 已完成，8 卡全空，P-8 暂缓，正是跑实验的时候** · 用户直令

> **用户直令（2026-10-09）**：「T3 报告写了 2 天了还没跑，.29 全空，跑起来」
>
> **现状**：
> - .29 8×H100 **全空**（0 MiB / 0% util），R3 BO 已完成，P-8 暂缓令未撤 → **空窗期正好利用**
> - T3 短名单（`report_pretrain_t3_train_speed_shortlist.html`）列了 C1–C5 候选，**一个都没跑**
> - P-9.6② 已证明 FP8 在 M=65536 转正（s=1.21–1.24, 235K tok/s），但用的是 TP4（通信开销 -6% vs TP1 的 249K）
> - **核心问题**：FP8 能不能在 **TP1**（无通信税）上转正？如果能，就能同时拿到 FP8 加速 + 长上下文 + >249K
> - **关键阻碍**：TP1 下 MBS4 OOM（79.8GB），seq8192 OOM → M 上不去 → **recompute 是唯一可能解锁的杠杆**
>
> **🔑 解冻 recompute**：此前 launcher 只暴露 MBS/TP/SP/seq/precision，recompute 属于「B 类冻结」。**本指令解冻**：允许你扩展 `pretrain_launcher.py` 添加 `--recompute-num-layers` 参数，在 recipe 的 `model_config()` 中设置 `recompute_granularity="full"` / `recompute_method="uniform"` / `recompute_num_layers=N`。改完 commit。
>
> **测试顺序（按价值排序，每点 60 步，`--save-interval 0`，不存 ckpt）**：

**Test 1（C2）: TP1·MBS4·seq4096·recompute·bf16 — recompute 能否解锁 MBS4 on TP1？**
- 配置：TP=1, DP=8, MBS=4, seq=4096, GBS=1024, bf16, `--recompute-num-layers 28`（56 层的一半）
- 基线对照：P-9.2 TP1·MBS4 无 recompute = OOM 79.8GB；P-9.7 TP1·MBS2 = 54.7GB / 249K tok/s
- **判据**：VRAM < 80GB 且 60 步 rc=0 → **recompute 解锁成功**；OOM → recompute 不够，跳到 Test 4
- 成本：~0.5 GPU·h
- **如果成功**：报 ms/iter + tok/s + peak VRAM + loss（对比 P-9.7 baseline 16,841.9 ms/iter / 249K）

**Test 2（C2+）: TP1·MBS4·seq8192·recompute·bf16 — M=32768 on TP1，命中 FP8 交叉点**
- 配置：TP=1, DP=8, MBS=4, seq=8192, GBS=512, bf16, `--recompute-num-layers 28`
- M = 4×8192 = 32768 = FP8 交叉点（P-9.4 微基准 M*≈30–32K）
- **前提**：Test 1 成功才跑
- **判据**：VRAM < 80GB 且 60 步 rc=0 → **M=32768 on TP1 落地**；OOM → seq8192 放不下，回退 Test 1 结果
- 成本：~0.5 GPU·h

**Test 3（C2+FP8）: TP1·MBS4·seq8192·recompute·FP8 — 🎯 梦幻配置**
- 配置：同 Test 2 + `--precision bf16_with_fp8_delayed_scaling_mixed` + `CUDA_DEVICE_MAX_CONNECTIONS=1`
- bf16 基线 = Test 2 的 ms/iter
- **判据（预注册）**：`s = t_bf16 / t_fp8 > 1.05` → **FP8 在 TP1 转正** → P-8 最优配置 = 此配置
- **如果 s > 1.05**：FP8 加速 + TP1 无通信税 + seq8192 长上下文 = **三合一**，可能 > 249K tok/s
- **如果 s ≤ 1.05**：FP8 在 M=32768 也不够，定论 = TP1 上 FP8 不可行
- 成本：~0.5 GPU·h

**Test 4（C1）: TP1·MBS2·seq4096·FP8 — 快速确认（预期失败但便宜）**
- 配置：TP=1, DP=8, MBS=2, seq=4096, GBS=1024, FP8, `CUDA_DEVICE_MAX_CONNECTIONS=1`
- M = 2×4096 = 8192，远低于 FP8 交叉点 → **预期 s < 1.0**（P-9.4 微基准 M=8192 s≈0.90）
- **为什么仍跑**：这是 P-8 baseline 配置（249K），如果 FP8 在这里意外不降速（s≈1.0），说明 FP8 overhead 可忽略，对 Test 3 的解读更有信心
- 成本：~0.5 GPU·h
- **可与 Test 1 并行跑**（Test 1 用 8 卡，Test 4 等 Test 1 结束后跑，或如果 Test 1 OOM 快速退出则立即接上）

**总成本**：≤3 GPU·h（如果 Test 1 OOM → Test 2/3 跳过，只跑 Test 4 = 0.5h）

**脚本**：照抄 `baize_p96b_fp8_e2e.sh` 模板，改 TP/MBS/seq/precision/recompute 参数。每个 test 一个 `/tmp/baize_t3_testN.log` + summary。

**报告要求（跑完立即报）**：
```
T3 提速验证结果：
- Test 1 (C2 recompute+MBS4 TP1): [OK/OOM] ms/iter=X tok/s=Y peak=ZGB
- Test 2 (C2+ seq8192 M=32768 TP1): [OK/OOM] ms/iter=X tok/s=Y peak=ZGB  
- Test 3 (C2+FP8 M=32768 TP1): s=X.XX [转正/不转正] ms/iter=X tok/s=Y
- Test 4 (C1 FP8 TP1 MBS2): s=X.XX [预期<1.0] ms/iter=X tok/s=Y
→ P-8 最优配置 = [结论]
```

**铁律**：
- 🚫 不改 P-5b recipe 的超参（LR / arch / optimizer），只加 recompute
- 🚫 不存 ckpt（`--save-interval 0`）
- 🚫 不打断 .12 上的 data 分词 / vision R9 训练
- ✅ 改 launcher 添加 recompute 参数 → commit
- 每个测试 rc=0 或 OOM 都如实记录
- 跑完 commit + push，前缀 `pretrain T3:`

---

## 📦 2026-10-09 搬运（原文未改，来自 BAIZE_PRETRAIN_2B_TASK.md）

### 运维指令 · 2026-10-09（📄 R3 数据配比搜索收官报告 HTML）· 用户直令 · 高优先（已闭合 #246）

> **用户令**：「pretrain 今早做完了第三轮数据配比试验，给它下发指令，让它生成 html 报告。」
> ⚠️ R3 BO 已 ✅ 100/100 收尾（#8 score=0.4032），交付物（`r3_best_blend.txt` / `DATA_MIX_RECIPE.md §9.7` / `EXPERIMENTS R3 节` / `mix_search_eval_r3.db`）均已就位——**只差一份 HTML 报告**。只写报告，不重跑任何实验。

**① 交付**：`report_pretrain_r3_data_mix.html`（落 `doc/BaiZe-ISEDA2027/`）

**② 数据源（只读，全部已就绪）**
- `run/r3_best_blend.txt`（best #8 + Top-5 摘要 + score 统计 + key findings）
- `run/DATA_MIX_RECIPE.md` §9.7（R3 spec 表 + Top-5 结果表 + 4 条关键结论 + P-8 推荐）
- `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` R3 节
- `nemo_experiments/mix_search/mix_search_eval_r3.db`（100 trials / 98 complete；如需复算**只读查询**，不写库）

**③ 格式（沿用 house style，照 `report_pretrain_r2_final.html`）**
- **自包含**：内联 CSS + 数据图优先**内联 SVG**；**零外链**；**HTML 本体 ≤200KB**。
- 曲线/柱状图由 **DB 真实数据生成**；🚫 严禁文生图「编」数据图。
- 位图一律 JPEG、长边 ≤1280、q85、落本地并 commit。

**④ 建议 8 节**
1. **TL;DR**（3–5 条）：R2 3 维 → R3 6 维下钻；best #8 score=0.4032；Web:Code:Math≈89:6:4（code 从先验 8% 降到 6%）；landscape 平坦（top-5 Δ=0.0053）；推荐 best #8 或 top-5 avg。
2. **实验设计**：目标 = 为 P-8 Stable 段定 6 源配比；proxy d=128/L=14 ≈18.36M（不换代理）；6 维单纯形 + 各维边界；GBS=16·MBS=16·seq=2048·LR=3e-3·WSD·D=1B token/trial；objective = 全量 lm_eval 8 常识任务（无 `--limit`，73106 requests）；100 trials / ~19.5h / 8 卡。
3. **Top-5 结果表**（rank / trial / score / en / zh / l1_en_hq / ultrax / code / math，+ top-5 avg 行）。
4. **关键发现**：l1_en_hq（高质量英文 web）一致高 = **质量 > 数量**；zh 方差极大（3.2%–33.4%）未被 BO 稳定识别；ultrax 稳定 ~10%；landscape 平坦 → 精确配比影响很小。
5. **与先验/R2 对比**：先验 88:8:4 → R3 落到 ~89:6:4；R2(3 维, --limit 500, 0.5B) → R3(6 维, 全量, 1B) 的口径升级与增量。
6. **对 P-8 的建议**：主选 best #8（en=16.8/zh=32.0/l1=32.4/ultrax=8.0/code=6.4/math=4.4）；稳健选 top-5 avg；「合理范围即可，无需过度优化配比」。⚠️ 只给**回填建议**，🚫 不改 `.tex` / `main.tex`（论文回填由外部统一做）。
7. **局限与诚实交代**：18.36M 代理 / 1B token per trial / landscape 平坦 / 2 failed trials（#25、#49）/ 单 seed=1234 / lm_eval 8 常识集只是代理指标（非下游 EDA pass@1）。
8. **图**（内联 SVG）：score 分布直方图（98 complete）/ Top-5 柱状对比 / best #8 的 8 任务逐项得分 / R3 vs R2 对比。

**⑤ 纪律**
- 🚫 **不新增实验、不改 R3 已固化数字/结论**；只读 DB 不重跑。
- 🚫 **不启动 P-8**（10-02 暂缓令未撤）；🚫 不 kill watchdog `baize_pretrain_loop.sh`。
- 收尾按「收尾铁律」commit+push（提交前缀 `pretrain R3收官: …`），更新 `MEMORY_PRETRAIN_2B.md` + `run/daily-memories/`。

### 运维指令 · 2026-10-09（💡 征询：让 pretrain 提 3 个实验 idea，按价值从高到低排序）· 用户直令 · 最高优先（已闭合 #251）

> **用户令**：「询问一下 pretrain，看它有什么 idea。让它提 3 个实验 idea，按照价值从高到低排序。」
> **背景**：R3 BO ✅ 100/100、R3 收官报告 ✅、P-8 PREP ✅、T3 ✅（**P-8 最优配置已定为 `TP1·MBS2·bf16 = 249K tok/s`**）——**.29 8×H100 现全空**。P-8 唯一阻塞 = Code/Math 全量分词（进行中）+ **暂缓令（10-02）未撤**。**用户正在评估是否撤销暂缓令、直接启动 P-8** ⇒ 先听 pretrain 自己最清楚的判断。

**① 任务（纯写作 · 零 GPU）**
- 提出 **3 个** 值得在 `.29` 空闲 8 卡上做的实验 idea，**按价值从高到低排序**（第 1 个 = 你认为最值得做的）。
- idea **可以**是「直接启动 P-8 本身」，**也可以**是 P-8 之前的小实验（彩排 / 长上下文适配 / 下游评测 / 别的）——**但必须给出排序理由**。

**② 每个 idea 必须写全 6 项**
1. **名称 + 一句话定位**
2. **为什么值得做**（**贴依据**：`路径:行号` / 已有实验结论 / README·论文的哪条诉求；🚫 不许凭印象）
3. **预期成本**（GPU·h / 墙钟 / 卡数 / 是否需新代码或解冻参数）
4. **可检验判据（先定后测）**——写清「什么结果算成功 / 失败」
5. **风险 / 依赖 / 前置**
6. **与谁对齐**（P-8 / Stage (ii) SFT·RL / 论文哪一节）

**③ 必须回答的一句话（放在 3 个 idea 之后）**
- 「**若运维此刻撤销 P-8 暂缓令，你建议：立即起 P-8 ／ 先做哪个 idea ／ 等 Code·Math 分词完成——为什么？**」

**④ 纪律**
- 🚫 **零 GPU**：只读现有产物 + 推理，**不许起任何训练/评测进程**；🚫 不启动 P-8；🚫 不 kill watchdog `baize_pretrain_loop.sh`。
- 🚫 **不许闭门造车**：凡涉及「别人怎么做 / 某评测某架构该怎么做」的结论，**必须读官方仓库或论文原文**（能 `git clone` 就 clone）。
- 写进 `MEMORY_PRETRAIN_2B.md` 的「🗣️ 运维问答 · 2026-10-09（提 3 个实验 idea）」小节；若 MEMORY 超 32KB，先按体积规程滚动归档。
- 收尾按「收尾铁律」commit+push（前缀 `pretrain 问答: …`），更新 `run/daily-memories/`。

### 运维指令 · 2026-10-09（⚗️ Muon vs AdamW · 用 `.12` 空档）· 用户直令 · 高优先（已被「🔁 运维调整」覆盖）

> 用户问「还想试验 Muon vs Adam 对比，有空档吗」。**空档 = `.12`**：`.29` 今晚已满（对比基准 + 夜班 T1/T2/T3）；**`.12` 在 vision E2 评测结束后（~21:30–22:30 Oct9）空出 8×H100**。
> ⚠️ **前置：Muon 未接入**（S3-03 当年因「实现风险」取消；脚本全 `--optimizer adam`；launcher 无 optimizer flag）⇒ 本任务 = **探针 → A/B**。

**Step 0 可行性探针（≤1 GPU·h）**：核 `megatron-core 0.16.1` 是否支持 Muon（`--optimizer muon` / `dist_muon` + `--muon-*`）+ `pretrain_launcher.py` 能否透传 + **hybrid/Mamba provider 下能否跑**；小步 smoke（**2D 矩阵→Muon；1D/norm/embed/lm_head/SSM 标量→AdamW**）。**跑不通 ⇒ 如实报「不支持 + 卡在哪」即停**（🚫 不熬夜 debug）。

**Step 1 A/B（2 臂）**：**AdamW**（基线 `--lr 1e-3` WSD）**vs Muon**（先 **3 点 LR 迷你扫描**定 Muon LR，避免"LR 未调=假负"）；**其余全同**（8 卡 / seq4096 / GBS1024 / 5000 步 / bf16 / seed1234），各 ≈4 GPU·h ⇒ **≈8 GPU·h**。**判据**：Muon `loss@5000 ≤ AdamW` 且 **Δloss > 0.07**（2σ；P-2 实测 σ=0.035）；报 grad-norm / 吞吐 / 显存。**诚实交代**：5000 步是**短地平线早期快照**（与全项目口径一致），非收敛结论。

**纪律**：占 `.12` 须先在 `run/GPU12_ALLOC.md` 登记一行（vision 交还后）；🚫 不启动 P-8 · 🚫 不 kill watchdog/vision 进程 · 分阶段 commit（前缀 `pretrain Muon:`）。

### 运维指令 · 2026-10-09（🌙 夜班填空：用 `.29` 剩余卡跑高价值实验 · 不含 P-8）· 用户直令 · 最高优先（已被「🔁 运维调整」覆盖）

> **用户令**：「20:45→明早 08:30 这个[对比]实验填不满 `.29` 的卡，还有其他高价值实验吗？」
> **窗口**：~11.75h ≈ 94 GPU·h；对比基准占 2–4 卡 ⇒ **剩约 4–6 卡空 ~11h**。⚠️ **不启动 P-8、不动暂缓令**（P-8 彩排另行等用户点头）。

**第 0 步**：先查对比基准占哪几张卡 → **只用剩余卡**；卡不足按 **T1→T2→T3 排队**，对比基准一释放即接力。**每项先报「占卡 + ETA」再跑。**

**T1（先做 · 最便宜）· 长上下文适配 4096→8192 阶梯续训**
- 从 `p3_hybrid/iter_0005000` HF ckpt 续训到 **seq=8192**（按 B1：`max_pos→131072` + `rope_theta 5e5/1e6` ABF，**每次只改一个变量**）。
- 成本 **~5–15 GPU·h**；判据：**8 常识集降幅 <10%** 且 loss 平滑（README 风险 #3 阈值）。
- 对齐：**Stage (ii) SFT/RL 硬前置** / 论文 §4。**这是最该先做的**。

**T2（便宜）· 参数匹配 Dense 的「训练侧」对比**
- 用今晚刚配的**等参 Dense Llama（2,228,897,792）**，**同配方**跑 **5000 步**，与 `p3_hybrid` 的 5000 步 loss 对齐比。
- 成本 **~4 GPU·h**；判据：hybrid loss ≤ 等参 dense（把 R2 的"等参优势"从 2.512B 修正到**真等参**）。

**T3（填空余量）· R3 配比迁移 A/B**
- 全模型 2.22B：R3 best #8 **vs** 先验 88:8:4，各 **2.5B token**（~600 步）。
- 成本 **~44 GPU·h**（4 卡 ~11h）；判据：R3 ≤ 先验（可迁移）/ |Δloss|<0.03（平坦）/ 先验胜（**负面发现**）。
- 对齐：论文 §4 data mixing / `DATA_MIX_RECIPE §9.7`。

**纪律**：🚫 不启动 P-8 · 🚫 不 kill watchdog · 🚫 不打乱对比基准的卡 · 分阶段 commit（前缀 `pretrain 夜班: …`）· 收尾按「收尾铁律」。



---
## [2026-10-10 归档] 以下三块于 2026-10-10 由 agent 从 BAIZE_PRETRAIN_2B_TASK.md 原文搬入（两步运维指令均已完成）

### 🆕 运维确认 · 2026-10-09（✅ **GO**：#252 门控通过 → 开跑「参数匹配 Dense」对比基准）· 最高优先

> **复核通过**：#252 方案 OK —— Dense Llama L=36/H=2048/I=6144 → **2,228,897,792（+0.389%，±1% ✅）**；矩阵 7ctx×2mf(0.6/0.85)×2bs(1/8)×WARMUP1/REP3；ETA 6–10h；**`.29` 全 8 卡可用**（P-8 未启动，2–4 卡并行推理即可）。**放行，开跑。**

**🖐 两处必须修正/收口（写进报告方法学节）：**
1. 🚨 **warmup 归因口径是错的** —— #252 写「128K **bs1=1591 vs bs8=447796**（281×）= 冷启动」：这是 **bs 效应**，不是 warmup，**混了两个变量**。
   → warmup 必须用**同一 bs** 的 `WARMUP=0 vs WARMUP=1` 对照来证（现成证据：`report_p911e_t1t2_comparison.html` §4，**bs=1** 下 128K 1,591→38,942 = **24.5×**）。**请用同-bs 冷/热对照**给结论，别再用 281×。
2. **ctx 上限要真到 hybrid OOM** —— 8M 未必够（历史：hybrid **2M 可服务 / 4M@0.85 超时**）。→ **持续 ×2 直到 hybrid 真正不可服务为止**（可到 16M/32M），并**分三类标注**：**OOM / TIMED-OUT / 请求被拒**。取"首次不可服务"为边界。

**其余**：按 #252 执行；结论落到 `report_pretrain_baize_vs_dense_fair_zh.html`（**中文**、自包含、零外链、**表格 ≤5 张**）；分阶段 commit（前缀 `pretrain 对比: …`）；先跑通 1 个 ctx 档确认管线再铺全矩阵。
**纪律**：🚫 不启动 P-8 · 🚫 不改 P-5b recipe / 不回训 · 🚫 不 kill watchdog · 推理用 `vllm` env。

---

### 🆕 运维指令 · 2026-10-09（📊 补测 + **中文**对比报告：BaiZe-Hybrid 2.220B ⚔ **参数匹配的 Dense Llama**，SGLang，ctx **持续 ×2 直到 hybrid 也 OOM**）· 用户直令 · **最高优先**

> **用户令原文**：「请 pretrain **按需补测**，做一个**完善的、中文的**对比报告 html。对比 BaiZe Mamba2-Hybrid 2.220B 与**一个同样大小的 Dense Llama**（MiniCPM5-2B 参数量 2.512B 比前者大，**对比不公平**）。**上下文持续 ×2 直到 BaiZe Mamba2-Hybrid 2.220B 也 OOM**，推理框架用 **SGLang**，对比表格**不需要很多，但要清晰有说服力**。」
> ⚠️ **纯推理 + 写报告**；🚫 **不启动 P-8**、🚫 不改 P-5b recipe / 不回训、🚫 不 kill watchdog。用 `.29` 8 卡。

**① 核心修正：换「参数匹配」的对手臂（这是本次重点）**
- **主对手臂 = 参数匹配的 Dense Llama（总参数 ≈ 2.220B，±1%）**，标准 Llama（dense attention + SwiGLU）。
  - 构建：按其参数预算配一个 Llama（层数 / hidden / FFN 自算），使 `sum(numel()) ≈ 2,220,268,032`（对齐 hybrid）。
  - **可用随机初始化**（本次比的是**速度 / 显存**，与权重值无关）——**但必须在报告中显式标注**「权重随机初始化，仅用于速度/显存基准」。
  - 若能复用 `p3_dense`（2.512B）**按比例缩到 2.220B** 并沿用同 tokenizer，优先。
- **原 `p3_dense`（MiniCPM5-2B，2.512B）降为「参考臂」**（附录/脚注），用来佐证「未做参数匹配时**偏袒 dense 约 13%**」。
- **公平口径（硬性，全部两臂一致）**：同 SGLang 版本 · **同 `--mem-fraction-static`** · 同 attention backend（flashinfer）· **WARMUP≥1 / REPEATS≥3（取 median）** · 同 prompt（tokenizer 精确计数、两臂同长度）· 同 bs · 显式标 SSM dtype · **prefill / decode 分离** · 报 **per-B 归一化**（tok/s per B）。

**② ctx 扫描：**持续 ×2，直到 **hybrid 自己 OOM**
- 128K → 256K → 512K → 1M → 2M → 4M → 8M …**每档 ×2**；**直到 BaiZe-Hybrid 2.220B 自己 OOM / 不可服务**才停。
- 🚨 **不得因为 dense 先挂就停** —— 上一版 dense@512K「失败」是 **`mem-frac=0.3` 的 KV 池（455K tokens）** 产物，**不是架构结论**。
- 每档记录：**prefill tok/s / TTFT / decode tok/s / e2e / 峰值显存 / pool tokens / status**；**明确标出两臂各自 OOM 边界**。
- ⚠️ 为让 hybrid 真能 OOM，**mem-frac 要取合理值**（建议 ≥0.6，可对 {0.6, 0.85} 各扫一遍）；**同一档两臂必须同 mem-frac**。超单卡可服务范围时**如实标 TIMED OUT / 不可服务**。

**③ 按需补测（用户已授权）**
- 补齐上表缺格：②的参数匹配臂 / 更高 ctx / mem-frac 档 / bs∈{1,8} 至少两档。
- 若某格不可行（OOM/超时），**如实标注，🚫 绝不许外推编数**。
- 顺带：用 **profiler / sglang 日志** 对上一版「WARMUP 造成 24×」的归因**给出证据或修正**（它是本次"公平性"叙事的依据）。

**④ 产出：一份完善的中文 HTML**
- 文件：`report_pretrain_baize_vs_dense_fair_zh.html`（落 `doc/BaiZe-ISEDA2027/`）。
- **中文**、自包含、**零外链**、内联 CSS + SVG；**表格少而精**（建议 ≤5 张：① 公平口径对照 ② 参数匹配表 ③ ctx×速度主表 ④ 显存/容量表 ⑤ OOM 边界表）——**清晰、有说服力**。
- 图**必须由真实数据**生成；🚫 严禁文生图编数据；位图 JPEG 长边 ≤1280 q85。
- 结论**诚实**：写明哪些格不可得、mem-frac 取值的影响、随机初始化的局限。

**⑤ 门控（先报后跑）**：**第一步 = 先报「参数匹配方案 + 测试矩阵 + ETA + 占用卡」**，再开跑；分阶段 commit（前缀 `pretrain 对比: …`）。

**⑥ 纪律**：🚫 不启动 P-8 · 🚫 不改 P-5b recipe/不回训 · 🚫 不 kill watchdog · 环境隔离（推理用 `vllm` env）· 收尾按「收尾铁律」。

---

### 🆕 运维指令 · 2026-10-09（🔎 自查：BaiZe-2B vs MiniCPM5-2B 有没有做过「公平对比」+ HTML 产出盘点）· 用户直令 · 高优先

> **用户令**：「重读你自己的报告 `report_pretrain_research1_fair_eval`，之前有没有给 **BaiZe-2B** 和 **MiniCPM5-2B** 做过**公平的对比**，有没有 **html 报告产出**？」
> **纯写作 · 零 GPU**。只引已落盘结果（`EXPERIMENTS_*` / `run/p911e_results/*.json` / 现成 HTML），🚫 不许编数、不许起进程。

**① 盘点（逐个列，别笼统）**：列出**所有**「BaiZe-2B（hybrid 2.220B）vs MiniCPM5-2B（dense 2.512B / `p3_dense`）」的对比产物 —— **文件名 + 相对路径 + 生成日期 + 覆盖维度**（loss / 训练吞吐 / 推理 prefill·decode / 长 ctx 成本 / 显存）。

**② 厘清 `research1` 的定位**：明确 `report_pretrain_research1_fair_eval.html` 是**方法学/协议**报告（记录 5 个 confounder + 公平协议 C1–C6），还是**含实测**？

**③ 公平性逐条自评（核心）**：对照你自己在 research1 里定的 **C1–C6**，逐条标「**已执行 / 部分 / 未执行**」，并**明确指出目前仍未被控制的 confounder**：
- C1 对齐 `--mem-fraction-static` · C2 标注 SSM dtype · C3 tokenizer 精确计数 · C4 bs 扫描 {1,4,8,32} · C5 参数归一化（tok/s per B） · C6 prefill/decode 分离。

**④ 给结论 + 指认权威版本**：
- 我们**到底有没有**一次「公平的」BaiZe-2B vs MiniCPM5-2B 对比？**有** ⇒ 指认**唯一权威版本**（HTML 路径 + 关键数字，如 128K hybrid 2.80×）；
- **没有一次完整公平版** ⇒ 列清**缺哪些格**，并说明要补什么。

**⑤ 产出**：
- 若公平对比**分散在多个 HTML、缺一份合并版** ⇒ 在**纯写作**范围内产出 `report_pretrain_baize_vs_minicpm5_fair.html`（自包含、零外链、数据只引已落盘结果）；
- 若已足够 ⇒ 明确写「**无需新报告**」并给出权威链接清单。

**⑥ 纪律**：🚫 零 GPU · 🚫 不启动训练/P-8 · 🚫 不 kill watchdog · 🚫 不许闭门造车（可引用官方仓库/论文原文，贴 URL）。回报位置：`MEMORY_PRETRAIN_2B.md` 新增「🗣️ 运维问答 · 2026-10-09（BaiZe vs MiniCPM5 公平对比盘点）」；commit 前缀 `pretrain 问答: …`。


---

### 🆕 运维指令 · 2026-10-10（📄 刷新 Muon 报告：吞吐/显存代价的归因 + 外部基准对照）· 用户直令 · 最高优先（先于下方「昨夜报告」块执行，昨夜报告照此口径引用）

> **用户令**：「请 pretrain 刷新 Muon 报告，调研一下通过 NeMo 的 Muon 实现，结果吞吐 −26%、显存 +38% 是否正常。」
> ⚠️ 运维已完成调研（结论在 ②）。**你只负责把归因写进报告，不重跑实验、不改已实测数字。**

**① 交付**：刷新 `doc/BaiZe-ISEDA2027/report_pretrain_muon_vs_adamw.html`（加一节「外部基准对照与 overhead 归因」+ 更新 P-8 建议）。

**② 调研结论（运维已查证，直接引用，答案 = 都不正常）**
- **吞吐 −26% ≠ Muon 固有代价**：NVIDIA 官方博客（2026-04-22）在 GB300 NVL72 上测得 Muon 吞吐 **near-parity** to AdamW（NeMo Megatron Bridge 26.02）。关键差异 = **layer-wise distributed optimizer（`dist_muon`：整层分给各 DP rank，正交化零额外通信）** + 分布式 Newton-Schulz（duplicated/distributed/blockwise）。理论 NS 计算开销仅 ~0.5–0.7%（Keller Jordan 博客：NanoGPT ~0.7% / Llama-405B ~0.5%）。→ 本地 −26% 主因 = **用的 plain Muon、非 dist_muon**（正交化与梯度同步未重叠、未用分布式 NS 模式），**属本地实现伪影，非算法固有**。
- **显存 +38% 与理论方向相反**：Muon 理论**更省** —— 每 2D 参数只存一个 momentum（4B），AdamW 存 m+v（8B）→ optimizer-state 省 **~45%**；端到端 peak memory 实测反而**降 ~9%**（PyTorch DeepSpeed blog：Qwen2.5-3B fine-tune 34.5→31.4 GiB）。→ 本地 +38% 是最可能 = **Muon 动量缓冲区 与 标量参数走 AdamW 的二阶矩缓冲区并存 / buffer 未复用**（报告已记此疑点，见 EXPERIMENTS §3225），**属实现伪影，应标注「待查」**。
- 来源（写进报告，带 URL）：
  1. NVIDIA blog：https://developer.nvidia.com/blog/advancing-emerging-optimizers-for-accelerated-llm-training-with-nvidia-megatron
  2. arXiv 2502.16982《Muon is Scalable for LLM Training》（Moonshot/UCLA；distributed Muon 并行策略）
  3. arXiv 2505.02222《Practical Efficiency of Muon for Pretraining》（第 2.1.1 节：Muon 内存最省，仅存 first moment）
  4. Keller Jordan《Muon optimizer》blog（2024-12；NS FLOP 上界 (T×m)/B ≈0.5–0.7%）

**③ 报告改动要求**
- **保留全部已实测数字**（loss 3.112 vs 4.003 · 吞吐 87K vs 118K · 显存 53.8 vs 39.0GB）不变。
- 把「代价/局限」改写为「**overhead 归因与外部基准对照**」：明确 −26% 吞吐 / +38% 显存 **都不是 Muon 固有代价**；给预期（dist_muon 下吞吐预计收窄至 near-parity；显存应转正为省 ~45% optimizer-state）。
- P-8 建议同步更新：方案 A（dist_muon layer-wise）从「可能消除」升级为「**NVIDIA near-parity 实证支撑**」；显存伪影列为「**P-8 前待查项**」（换 dist_muon 后复测显存，验证 buffer 复用）。
- 诚实声明：本归因引用外部文档、**未在本地复现 dist_muon**；「待查」≠「已修」。

**④ 纪律**：🚫 不启动 P-8 · 🚫 不 kill watchdog · 只改报告不改实验 · 收尾按「收尾铁律」commit+push（前缀 `pretrain Muon刷新:`）· 若 TASK 超 32KB，按规程自行归档已闭合旧块。
### 🆕 运维指令 · 2026-10-10（📄 昨夜工作汇报 HTML）· 用户直令 · 高优先

> **用户令**：「关于昨晚的工作，请 pretrain 写 html 报告。」

**① 交付**：`report_10_09_pretrain_overnight.html`（落 `doc/BaiZe-ISEDA2027/`）

**② 内容 = 昨夜（10-09 夜 → 10-10 晨）两项工作汇总**（均 ✅ 完成、各已有详报 → **本报告做「昨夜汇报」汇总 + 指针，不重复贴全文**）
1. **① 参数匹配对比基准（P-9.11-F，Dense-Match vs Hybrid/BaiZe）**：DM 可服务至 1M（prefill 2,351 / decode 64.9）· **2M 不可服务**（输入 > max_total_num_tokens≈1.23M）· 架构优势 **2×**（Hybrid 2M vs DM 1M）· warmup 归因修正 281×→24.5× · VRAM(128K) 52.36→59.02GB 修正。→ 详报 `report_pretrain_baize_vs_dense_fair_zh.html`（指针）。
2. **② Muon vs AdamW A/B**（各 1000 步 · GBS16 · seq4094 · bf16 · 同 seed）：Muon loss **3.112** vs AdamW **4.003**（**−22.3%**）· 吞吐 87K vs 118K tok/s（**−26%**）· 显存 53.8 vs 39.0GB（**+38%**）· 均 rc=0 / 0 NaN / 0 skip。→ 详报 `report_pretrain_muon_vs_adamw.html`（指针）。

**③ 格式（house style）**：自包含 · 内联 CSS + 内联 SVG · 零外链 · ≤200KB；已有详报只给指针。

**④ 必含「对 P-8 的启示」**：① DM 对比 → BaiZe 长上下文服务能力佐证；② Muon → **loss 质量更好但吞吐/显存有代价**，P-8 是否采 Muon/dist_muon 的取舍（只记结论，不启动 P-8）。

**⑤ 纪律**：🚫 不启动 P-8（10-02 暂缓令未撤）· 🚫 不 kill watchdog · 只汇总已固化数字、不新增实验 · 收尾按「收尾铁律」commit+push（前缀 `pretrain 昨夜报告:`）· 若 TASK 超 32KB，按规程自行归档已闭合旧块（含上方「运维调整/运维更正」两块）。

---

## 📦 §运维指令·2026-10-10（⚗️ dist_muon 重测）→ 自 TASK 归档

> 结论：dist_muon = loss 3.110 / 122,415 tok/s / 37.3GB，plain Muon「−26% 吞吐 / +38% 显存」两项代价全消除 → 定为 P-8 默认优化器。

### 原指令全文
**用户令**：「Muon 的试验，让 pretrain 用 dist_muon 重测。」

**① 目标**：上一轮 Muon A/B 用的是 `optimizer=muon`（plain）。改成 `optimizer=dist_muon`（layer-wise distributed），验证「−26% 吞吐 / +38% 显存」是否被收窄/消除。

**② 口径**：臂 dist_muon（新增）；对照直接用已测的 muon（loss 3.112 / 87K / 53.8GB）与 adamw（4.003 / 118K / 39.0GB）。参数 `--gbs 16 --mbs 1 --seq 4094 --iters 1000 --seed 1234 --data p5b_l3_blend`，.29 8 卡、bf16、TP=1 ⇒ DP=8。output `nemo_experiments/muon_ab_realdata_distmuon`。

**③ 接线**：`bridge_compat.py` 路由 `optimizer="dist_muon"` → layer-wise distributed（整层分给各 DP rank + `--use-distributed-optimizer` 语义）。先 1 卡/短步 smoke，再铺 1000 步。

**④ 指标**：loss@1000 / tok/s / peak VRAM / grad_norm / 0 NaN·0 skip。预期 VRAM 显著低于 53.8GB、甚至 ≤39GB。

**⑤ 判读预注册**：吞吐 ≥118K →「−26% 系 plain Muon 通信/实现伪影」实锤；87K~118K → 部分收窄；仍 ≈87K → 规模差异如实记录。显存应 ≤39GB。

**⑥ 纪律**：🚫 不启动 P-8 · 🚫 不 kill watchdog · 如实报卡点 · 跑完写 EXPERIMENTS + 刷新 `report_pretrain_muon_vs_adamw.html`。

---

## 📦 §运维指令·2026-10-10（✅ dist_muon 默认优化器）→ 自 TASK 归档

> 结论：dist_muon = loss 3.110 / 122,415 tok/s / 37.3GB，plain Muon「−26% 吞吐 / +38% 显存」两项代价全消除 → 写入配方表 §优化器为 P-8 默认，LR 1e-3 保留。

**用户令**：「pretrain 可以将 dist_muon 写进任务书的最佳实践区，以后作为默认设置。」

**① 结论依据（三路实测 #262）**：dist_muon = loss 3.110 / 122,415 tok/s（>AdamW 118K）/ 37.3GB（<AdamW 39.0GB），plain Muon 两项代价全消除，保留 Muon 收敛优势（loss −22.3%）。

**② 默认设置**：P-8 及后续正式训练优化器默认 `dist_muon`（`layer_wise_distributed_optimizer=True`）。

**③ LR 口径**：Muon 官方建议 ~1e-3；A/B 验证用 3e-4 公平对照；P-8 配方 LR=1e-3 贴合官方建议 → 保留不改。

**④ 诚实声明**：仅 1000 步短地平线；长训练是否持续优势待 P-8 长跑验证。

---

## §运维指令·2026-10-11（📚 文献借鉴报告）已归档（2026-10-11 搬运，原文未改）

### 🆕 运维指令 · 2026-10-11（📚 **文献借鉴报告**：从 research 线近期论文里找可借鉴 idea · 中文 HTML）· 用户直令 · 高优先

> **用户原话（2026-10-11）**：「**pretrain** 看看**这几天 research 积累的论文**，看看有没有什么可以借鉴的 idea，**写个 html 报告（中文版）**。」
> **性质**：**纯阅读 + 写作**（🚫 不占 `.29` 的 GPU、🚫 不打断 P-8 长跑、🚫 不改在飞配置）。**如需做验证实验 ⇒ 先写进报告「待验证」并列成本，经运维批准后再跑**。

**① 交付物**：`doc/BaiZe-ISEDA2027/report_pretrain_lit_ideas.html`（**中文 · 自包含 · 内联 CSS/SVG · 零外链 · ≤200KB**）。

**② 输入（先 `git pull`，再读）**
- research 线近期日报（每天 5 篇）：**仓根相对** `doc/personal-watch/run/research/daily/2026-10-07.html` … `2026-10-11.html`（**共 25 篇**）。
- 精选与台账：`doc/personal-watch/run/research/TOP_K.md` + `TOP_K.jsonl` · `papers.jsonl` · `TAKEAWAYS.md`。
- 可对照本仓：`doc/BaiZe-ISEDA2027/LIT_IDEAS_2026-10-04.html` / `LIT_IDEAS_2026-10-05.html` + 本仓 `report_pretrain_*.html`。

**③ 本线关注面**：预训练配方 · **优化器（Muon / MuonClip / hybrid optimizer）** · **架构（Mamba2 / SSM / hybrid）** · **长上下文**（位置编码 / 外推 / 推理成本）· 数据配比与课程 · scaling law · 训练稳定性（loss spike）· 吞吐与并行。

**④ 每条 idea 必带（缺一不可）**：① 出处（**原题 + arXiv ID + URL + 日期**）② 一句话做了什么 ③ **与本线的关系**（**能用在 P-8 / 后续 100B 档 / 长上下文适配 / 优化器切换 的哪一步，具体到模块/实验**）④ **借鉴成本**（GPU·h / 墙钟 / 数据·权重依赖）⑤ **风险/不确定性** ⑥ **价签**（可行性 × 潜力 打分）。
- **按「对本线的可执行价值」排序 · 给 TOP-5**；其余列附表。
- **显著区分**「**已验证可借鉴**」vs「**仅灵感/未验证**」；🚫 不得拿二手/摘要页当一手；**每条须可溯源**。

**⑤ 纪律**：🚫 不改 P-8 在飞配置/数值；🚫 不新跑实验（要验证先报运维并列成本）；commit 前缀 `pretrain lit-rpt:`；任务书 >32KB 自滚归档。

**结论**：`report_pretrain_lit_ideas.html` 29.8KB ✅ 交付（TOP-5+附表8+§4待验证+§5去重+§6映射+§7口径, 每条6字段齐全, 中文自包含）。

---

## §运维指令·2026-10-10（⚗️ MBS 2→3 A/B 验证）已归档（2026-10-11 搬运，原文未改）

### 🆕 运维指令 · 2026-10-10（⚗️ MBS 2→3 A/B 验证 · 候选 GBS=1032）· 用户直令 · 最高优先

> **用户令**：「好的 GBS=1032，其它按你的建议执行。」—— P-8【44B】启动后、跑出首个 ckpt 前，先做 MBS 2 vs 3 临门 A/B，**达标才切换，不打断已存 ckpt**。

**① 背景**：P-8 实测显存 51/79GB（dist_muon 释放余量），MBS 2→3 有机会提速；但 GBS=1024 非 24 倍数 → 候选 **GBS=1032**（43×24，最贴原 1024）。

**② 执行**：① P-8 跑到最近 save-interval 点**保存 ckpt + 优雅暂停**。② 同 seed=1234 / 同数据各跑 **300 步**：臂 A `--micro-batch-size 2 --global-batch-size 1024`（基线）；臂 B `--micro-batch-size 3 --global-batch-size 1032`（候选）。③ 按④判据决策。

**③ 预注册判据（三全过才切）**：① 吞吐 **B ≥ A×1.12**（A≈249K → B≥279K，last-100 步均值）② 峰值显存 **B ≤ 76GB**（OOM 直接判负，nvidia-smi 全程记 max）③ **loss@300 与 A 一致**（无 NaN/发散/抬升）。

**④ 决策**：达标 → P-8 切 **MBS=3/GBS=1032**，重算 44B = **10,409 步 / warmup 520 / decay 1041 / save 1041**（token/step=4,227,072）；已跑不足 ~1K 步则**从零重启**（口径最干净），否则从暂停点按剩余 token 续（记录切换点+两侧口径）。不达标 → **恢复 MBS=2/GBS=1024** 原定稿（10,490/524/1049/1049），原数字全不变。

**⑤ 纪律**：🚫 不 kill watchdog · commit 前缀 `pretrain P-8:` · 达到判据才动正式长跑 · 若 TASK 超 32KB 按规程自行归档。

**结论**：A/B 已闭合 — B/A=1.031 < 1.12 → **FAIL** → MBS=2/GBS=1024 原定稿保留，原数字全不变。
---

## 📦 归档块 · §运维指令 2026-10-10（🚀 撤 P-8 暂缓令 · 按计划书启动 P-8【44B】dist_muon 版）—— 2026-10-12 被「🛑 停训换 AdamW」取代

### 🆕 运维指令 · 2026-10-10（🚀 撤 P-8 暂缓令 · 按计划书启动 P-8【44B】）· 用户直令 · 最高优先

> **用户令**：「pretrain：按此执行 P-8。」—— 本指令**撤销 P-8 暂缓令（10-02）**，按 `report_pretrain_p8_plan.html`（commit cb3f54c2）正式启动 Stage (i) 预训练。

**① 对象**：从零训 Mamba2-hybrid 2.220B，真实语料，**44B token**（Chinchilla 下限，≈2.0 天 @ 249K tok/s）。

**② 参数**（`pretrain_launcher.py`，TP1·DP8·8 卡独占）：`--arch mamba2 --tensor-parallel 1 --seq-length 4096 --global-batch-size 1024 --micro-batch-size 2 --precision bf16_mixed --optimizer dist_muon --lr 1e-3 --min-lr 1e-5 --lr-decay-style WSD --lr-warmup-iters 524 --lr-decay-iters 1049 --train-iters 10490 --save-interval 1049 --seed 1234`（端口/master_addr/数据路径按 operator 真实入口；`layer_wise_distributed_optimizer=True`）。

**③ 数据（WSD 两段各配一套比，与数据段同步切换）**：Stable ~36B = **web 88 : code 8 : math 4**（web=base，用已分词存量 en_base 206.76B + l1_en_hq 152.17B + zh 112.47B ≈502B，web 需求仅 31.7B 已覆盖 → **en_v1_4 非 44B 档阻塞项，无需等下载完成**）；Decay ~8B = **SFT 64%**（SFT-2605 + SFT-Agent-2609，内部 5 类各 20%）+ L3 24% + code 8% + math 4%。

**④ 随本指令生效的勘误（已订正任务书 §输入表 / §训练要求）**：配比 `86:10:4`→`88:8:4`、stable 主体 `L3`→`base`；warmup/decay 由绝对 `250/500` 改**比例 5%/10%**（44B 档 = 524/1049 步）。

**⑤ 纪律**：从零（🚫 不加载任何权重）· WSD 完整走完（decay 尾段吃到 SFT 退火混合）· 每 500 步记 loss/val/grad_norm/tok/s/GPU 独占 · 禁叠加重 I/O（vision/data 避让）· NaN/发散/OOM 如实记录+留 ckpt+日志不静默重启 · 建议挂 MaxLogit/QK 谱范数监控（超阈值 μ(·) 归一化 = MuonClip 预案）。

**⑥ 启动前最后核查**：8 卡独占无争用（nvidia-smi 全 0）/ 数据 bin·idx 路径与配比一致 / dist_muon layer-wise 生效 / 磁盘预留 ≥400GB（ckpt 11×~30GB）/ 启动后报 PID + 首 500 步 loss/tok/s。

**⑦ 输出**：loss 曲线 + 每 10% ckpt 路径 + final 8 集 lm_eval（Table 2 常识）；commit 前缀 `pretrain P-8:`。en_v1_4 下满后并入后续 100B 档（另行再令）。

> **执行结论（2026-10-12）**：dist_muon 44B 单跑 ~25.5h 至 step8490（80.9%，~36B/44B），loss 从健康 plateau 2.44（step7880-8090）经 step8180 急升到 2.59，随后缓慢上漂至 **2.623 全程新高**；grad_norm 0.14 → 0.35-0.89（健康 5-6×）；0 NaN 未停。用户判因 dist_muon → 令**停训、换 AdamW 从零重启**。ckpt@7343=最后健康点(loss2.44)、ckpt@8392=spike后，8 ckpt 保留为证据。

---

### 🆕 运维指令 · 2026-10-13（📋 写正式训练 HTML 计划：全量 MiniCPM5 数据 + en_v1_4 · .12+.29 双机 16 卡 · 超参数 + 空窗期试验建议）· 用户直令 · 最高优先

> **用户令（2026-10-13）**：「安排 pretrain 写正式训练 html 计划：数据=所有 MiniCPM5 数据（包括正在下载的 en_v1_4），算力=.12 和 .29 两台机器一起上，写出超参数；P-8 之后到 en_v1_4 下载完成还有几天，建议做什么试验。」
> **这 = 把 P-8 超参搜索的结果「转正」为生产级正式训练计划**（不是再搜一轮，是定稿落地）。

**① 交付物**：自包含中文 HTML 报告 `report_pretrain_formal_train_plan.html`（投放 `run/` 下，git 提交 + push）。
> 参考既有格式 `report_pretrain_p8_plan.html` / `BAIZE_2B_ARCH_SEARCH_PLAN.html`。P-8 还没跑完（当前 step~4660/10490，~1.1 天后结束），本计划是**前瞻定稿**，允许在报告里显式标注「以 P-8 最终 checkpoint 与 en_v1_4 实际落盘日为准」的活参数位。

**② 数据（= 所有 MiniCPM5 数据 + en_v1_4）**：
- base 主体升级为 **`en_v1_4`**（`openbmb/Ultra-FineWeb · data/ultrafineweb_en_v1_4/`，56,461 文件 / 6.75TB，**当前 46.7% 下载中，ETA ~5-14 天**），替代/放大之前的存量 en_base。
- 其余照旧：zh、l1_en_hq、L3（en/zh QA+multi）、UltraX-Preview、`UltraData-Code`、`UltraData-Math`、SFT 退火源。
- 报告须给：**稳定段与退火段的完整配比**（沿用 86:10:4 / 88:8:4 → 退火 SFT64%+L3 24%+code8%+math4% 这套，**但请你按 en_v1_4 实际 token 总量重算一次各成分绝对 token 数**）、**总可训 token 数**、**分阶段 token 预算**。
- 📌 **数据依赖链必须画清**：`en_v1_4 下载满 56,461 → check_contamination.py 过闸 → 分词 → 投料`（data 线已把「下满必经污染扫描」写死，见 `MEMORY_DATA.md`）。正式训练**不可能早于 en_v1_4 下满 + 过闸 + 分词**，报告里这条时间线单列一节。

**③ 算力（.12 + .29 双机 16×H100 80GB）**：
- 明确写死 **2 节点 topology**：`.29`(8)× + `.12`(8)× = 16 卡；**两条都要写**：`nnodes=2`、跨节点 NCCL 走什么（IB/RoCE/以太 + 带宽，**必须实测 `nvidia-smi topo` / `all_reduce` 或 ibstat 取证**，不要拍脑袋）。
- **并行策略**：P-8 = TP1/DP8/MBS2/GBS1024。16 卡候选 = **DP16（首选，对 SSM-heavy 的 Mamba2 最省心）** / TP2+DP8 / PP2+DP8 —— 每条给**吞吐预期 + 显存 + 复杂度**，**给出你的推荐 + 理由**（注意：Mamba2 SSM 层 TP 收益有限，报告里论证这一点）。
- **GBS/LR 联动**：明确「16 卡是 **GBS 翻倍到 2048 还是维持 1024**」，并给对应的 **LR 是否 scale（线性/√scale 或保持 1e-3）** 的结论，不能含糊。
- ⚠️ **协调现实**：`.12` 当前由 **vision 线占用**（R 循环跑实验），`.29` 跑完 P-8 才释放。正式训练的「双机一起上」**必须等 en_v1_4 就绪 + 两机都空**；报告里把「占卡协调 / 何时可开跑」讲清楚，**绝不能 kill vision / watchdog**。

**④ 超参数（逐项写死，一行一个，含来源）**：
- 模型架构（mamba2 56L、hidden 2048 / ffn 8192、4 attention 层、GQA、head_dim 128、vocab 129408 / tokenizer DeepSeek-V4.1-Flash eod）✓ 全抄 P-8。
- `seq-length`（4096 起步；若要走长上下文训练见⑤-2）、`global-batch-size`、`micro-batch-size`、`tensor-parallel`/`pipeline-parallel`、`precision bf16_mixed`。
- 优化器 `adamw` + `lr` + `min-lr` + `weight-decay` + `grad-clip`（AdamW 定 1e-3 的基线要标清楚）。
- WSD：`lr-warmup-iters` / `lr-decay-style WSD` / `lr-decay-iters` / `train-iters` / **5/85/10 比例**、`seed`、`save-interval`、`eval-interval`。
- 对应 **总 token 预算（估）** + **总步数** + **墙钟 ETA（16 卡 @实际 tok/s，给 ± 区间）**。
- 每项超参要么标「继承 P-8 实证」要么标「新定 + 依据」，**不给未经论证的拍值**。

**⑤ 空窗期试验建议（P-8 结束 → en_v1_4 下满 之间的 ~4-13 天）**——这是用户点名的第二问，报告单列一节，按**优先级 + 预算 + 用哪几卡 + ETA** 给出，建议候选（可增删，但须逐条给理由）：
1. **🔑 双机 16 卡 scaling 彩排（P0 强烈建议）**：用**已就绪的 R3 存量**（1483.91B tok / 5.94TB 已分词）在 `.12+.29` 上跑 DP16 冒烟 + 短程训练，实测**跨节点吞吐 scaling（8→16 是否近线性）、ckpt 分片、容错、NCCL 稳定性**，产出正式训练可直接套用的 launcher+配置 → 直接消除「一起上」的最大风险。⚠️ 需等 `.12` 有空档，先 `.29` 单机 8 卡 rehearsal，再上 16。
2. **长上下文训练延伸（T1 沉淀）**：存量数据上做 `seq 4096 → 32K/128K` 的续训（RoPE theta 调大 + 继续训练），补上训练侧长上下文结论（推理侧 1M/2M 已验）。
3. **退火配比全量验证（S4/R3 收尾）**：decay 段 SFT64%+L3 24%+code8%+math4% 跑全量版，量化「退火 vs 直接停」的质量增益。
4. （可选）**存量数据长跑 interim checkpoint**：2.2B 已到 44B=Chinchilla，若有余量续跑更高 token 档，作为 en_v1_4 落地前的中间基座。
5. （可选）**formal 模型的推理/评测彩排**（SGLang 部署 + harness 打通，为下一步 P-9 推理基准铺路）。

**⑥ 纪律（不变）**：🚫 绝不 kill `baize_pretrain_loop.sh`(watchdog PID 1391466) / vision 线进程 / data 线下载（esp. `en_v1_4` + `85M`）；重 I/O 实验避让 `/nas_train` NFS 与下载争用；报告体积自检（≤~30KB 单文件，超大则拆）；交付后 commit + push，并在 `MEMORY_PRETRAIN_2B.md` 心跳记「正式训练计划已交付」。

> **执行结论（2026-10-13）**：`report_pretrain_formal_train_plan.html` 27.9KB ✅ 交付（commit 42399927）。10 节自包含 HTML：§1 数据（en_v1_4 6.75TB + 全部 MiniCPM5 + Stable 88:8:4 + Decay SFT64/L3 24/code8/math4 + 100B/200B 各成分绝对 token 重算 + 依赖链时间线）· §2 算力（.29 实测拓扑 NV18 NVSwitch + RoCE 400Gb/s + DP16 推荐）· §3 超参逐项写死 · §4 占卡协调 · §5 空窗期 5 试验 · §6-10 ckpt/纪律/前置清单/launcher 模板/风险缓解。

---

### 🆕 运维指令 · 2026-10-12（🛑 停训 P-8 · 优化器 Muon→AdamW 重新启动）· 用户直令 · 最高优先

> **用户令（2026-10-12）**：「pretrain：停掉训练，重新启动，优化器从 Muon 换回 AdamW。」—— 处置 P-8 stable 段 step8490 loss 慢速发散（2.623 新高 / grad_norm 0.89=健康 5-6×）。

**① 先停当前发散训练**：保存当前 step(~8490) ckpt 作 dist_muon 发散证据 → 优雅 `pkill -f pretrain_launcher.*p8`（kill torchrun PID 1799555）→ 等 30s 确认 8 卡释放。🚫 不 kill watchdog loop(PID 1391466)。

**② 从零重启**（🚫 不加载任何权重/优化器状态）：44B token 从头训、全新 run。

**③ 优化器换回 AdamW**：`--optimizer adamw --lr 1e-3 --min-lr 1e-5`（**去 `dist_muon` + `layer_wise_distributed_optimizer=True`**，回标准 Megatron AdamW；**LR 保持 1e-3** —— 早先 AdamW 试验早定 1e-3，🛑 **不准改**）。

**④ warmup 恢复 524**：从零 → **`--lr-warmup-iters 524`**（🛫 不再用崩溃恢复的 `0`）；`--lr-decay-style WSD --lr-decay-iters 1049 --train-iters 10490 --save-interval 1049 --seed 1234`，decay 切换 🔄 step9441。

**⑤ 其余配方不变**：`--arch mamba2 --tensor-parallel 1 --seq-length 4096 --global-batch-size 1024 --micro-batch-size 2 --precision bf16_mixed`；WSD 5/85/10；stable ~36B=web88:code8:math4（存量 en_base+l1_en_hq+zh 已覆盖，无需等下载）；decay ~8B=SFT64%+L3 24%+code8%+math4%。

**⑥ 纪律**：每 500 步记 loss/val/grad_norm/tok/s/8卡独占；NaN/发散/OOM 如实记录+留 ckpt+日志不静默重启。**AdamW 已收敛基线**（原 2.220B A/B 三路验证，loss 平滑无 spike）；若 AdamW 仍发散 → 上报（疑数据/配比而非优化器）。

**⑦ 同步改 decay 脚本**：`baize_p8_decay.sh` 两段同改 `adamw + lr 1e-3`（🛫 残留 dist_muon）。LR 1e-3 为 AdamW 早先试验定值，decay 段同样保持，不改。

**⑧ dist_muon 版 ckpt 存档**：8 个（1049~8392，含 7343 健康点/8392 spike 后）**保留为证据**，新 run 用独立目录，🛫 不覆盖。

> **执行结论（2026-10-12）**：dist_muon 已停（PID 1799555 killed），8 ckpt 保留为证据在 `p8/checkpoints/`。AdamW 从零重启成功（PID 771300, step0 起），`baize_p8_adamw_train.sh` + `baize_p8_decay.sh` 均已改为 `--optimizer adam --lr 1e-3`。warmup 524 ✅, stable 段 loss 平滑下降无 spike, grad_norm 0.12-0.20 稳定。当前 step~4966/10490, loss~2.66, 健康。


---

### 🆕 运维指令 · 2026-10-13（📋【重做 v2】正式训练计划书 —— 须按 MiniCPM5「全量数据」口径，🚫 禁 100B 假设）· 用户直令 · 最高优先

> 用户判不合格（2026-10-13）：「`report_pretrain_formal_train_plan.html` 不合格，需要重做。问题：① MiniCPM5 总数据量多少、各数据源大约多少 token、pretrain/decay 各如何配比、总计训练多少 token（我说了 MiniCPM5 有多少训多少，那么有多少呢，估不出来么？）；2 台机器需要多长时间。② 说是按「正式」来、按 MiniCPM5 全量数据来，你的报告还是假定总数据只有 100B。这是逗谁玩呢？请认真思考，仔细写好这份计划书。」
> 性质：查证 + 写作（CPU，不占 GPU）；不得打断在飞 P-8 训练。

① 必答硬问题（v1 缺失）：
1. MiniCPM5 训练数据总量 = ? token：逐源拆解（web / code / math / 其他），给估计方法与出处（MiniCPM5 技术报告 / HF model card / 官方 config）；查不到就明写估计依据 + 区间 —— 🚫 不许再出现「100B」这类拍脑袋数。
2. 本项目可训数据全貌：`MiniCPM5-{1B,2B}.config.json` + `data/` 盘点 + R3 全量分词 110/110 = 1483.91B tok / 5.94TB（逐子集：base 206.76B / l1_en_hq 152.17B / zh 112.47B / ultrax 30.97B / …）→ 对齐「MiniCPM5 有多少训多少」的实际可训 token。
3. pretrain(stable) / decay 配比：stable:decay token 比例 + decay 段退火混料（SFT/L3/code/math）+ 总步数 / 总 token。
4. 2 台机（.12+.29，16×H100）墙钟：用实测（单机 8 卡 249K tok/s；DP16 近线性待彩排 → 标「待验」）→ 总 token ÷ 有效吞吐 → 乐观 / 基准 / 保守三档（含 warmup/decay/ckpt/eval 开销）。

② 红线：🚫 禁止再假设「总数据 100B / 200B」，必须按 MiniCPM5 全量口径给总 token + 墙钟；每个数字可溯源（文件:行 / 官方来源 / 实测命令）；估算显式标「估 + 依据 + 区间」。

③ 交付：覆盖 `doc/BaiZe-ISEDA2027/run/report_pretrain_formal_train_plan.html`（中文 · 自包含 · 内联 CSS/SVG · ≤200KB）。节：① HERO+TL;DR（总数据 X B token · 16 卡 Y 天）② MiniCPM5 数据全貌（总 token + 逐源 + 出处）③ 本项目可训数据（R3 子集 token 表·实测）④ 配方（stable/decay 分配 + 配比 + 总步数 + WSD）⑤ 算力墙钟（三档）⑥ ckpt/磁盘/风险/前置 ⑦ v1→v2 修订说明（旧 100B 假设为何错）⑧ launcher + 纪律。

④ 纪律：🚫 不占 GPU、不打断 P-8 监控 · 🚫 不改已发布数值 · 数字可溯源 · commit 前缀 `pretrain plan:` · 任务书 >32KB 自滚归档。

> **执行结论**：v2 已交付（commit fa25d488，30.4KB HTML，300B token 基准），但被用户再次否决 → v3 重做（实盘盘点口径）。

---

### 🆕 运维指令 · 2026-10-14（📝 训练空窗期审视论文 · LLM 侧 · 出中文改进意见 HTML）· 用户直令

> **用户令（2026-10-14）**：「安排 pretrain agent 在训练进行期间，审视论文（BaiZe-ISEDA2027），将改进意见写入 html 报告（中文版）。」

**性质**：零 GPU 的「读 + 写」任务。**主线仍是 P-8 训练监控**——本任务只占用**监控完成后的空窗期**：🚫 绝不为论文审视而延迟/干扰 P-8 监控与 decay 切换（@9441）。

**① 审视对象**：论文树 `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/`，**侧重 LLM 侧章节**：`ISEDA2027/0_abstract.tex` · `1_intro.tex` · `2_related_work.tex` · `3_architecture.tex` · `4_llm_pretrain.tex` · `5_llm_posttrain.tex` · `9_conclusion.tex` + `main.tex` + `reference.bib`。

**② 审视维度（每条意见必须具体，贴 `文件:行号` 或具体数字，🚫 空泛）**：
1. **架构数字一致性**：2.22B（`sum(numel())=2,220,268,032`）· 56 层含 4 层 attention · **seq 4096（2 的幂；见本文件「最佳实践/硬口径」）** · vocab 129,281 · tokenizer DeepSeek-V4.1-Flash —— 与 `EXPERIMENTS_2B.md` / `EXPERIMENTS_PRETRAIN_2B.md` 是否一致；有无 `4094` 残留（口径应统一 4096）。
2. **预训练结果回填**：val loss@5000=2.7647 · final loss@20000=2.2054 · 3-seed 2.6739±0.0469 · LR 1e-3 / WSD / 退火 86:10:4 · 预算 ~85 GPU·h —— 是否已回填、有无陈旧值。
3. **混合架构优势表**（dense vs hybrid：参数 −11.6% / loss −0.12 / decode 10.3×）——decode 10.3× 的「测量口径限定」（Megatron 直驱、生产栈会收窄）是否仍保留。
4. **训练量极小**（655M token / 0.036% 数据池）是否如实声明为「代理实验」，未当收敛值引用。
5. **Stage(ii) 后训练设计**：领域退火 + SFT + RLVR/GRPO + R1–R4 奖励表 + 成功阶梯 M1–M4 是否完整、口径一致。
6. **数据配比**：每步 4M token 不变量 · 配比搜索（小代理 BO）口径是否表述一致。
7. **可回填 [TBD] 清单**：哪些已有实测可回填（如 P-8 当前 loss ~2.49）、哪些仍缺轮次。

**③ 交付**：中文、自包含 HTML `doc/BaiZe-ISEDA2027/reports/report_baize_paper_review_pretrain_zh.html`；分 🔴硬伤 / 🟠建议 / 🟢可回填 三级标注；文末附「可回填建议清单」。

**④ 红线**：🚫 不直接改论文 `.tex`（只出意见，改稿须另行批准）；🚫 不为审视而延迟 P-8 监控 / decay 切换；✅ 数字须与 EXPERIMENTS 台账一致，不许凭印象；commit 前缀 `pretrain paper-review:` · 任务书 >32KB 自滚归档。

> **执行结论**：报告已交付（#413，26.5KB，4项🔴+10项🟠+3项🟢），随后 #414 执行改稿（放行刷新论文指令）。

---

### 🆕 运维指令 · 2026-10-13（📋【再重做 v3】正式训练计划 —— 严格按「已下载 + 正在下载」实盘盘点换算 token，🚫 禁引论文/CSDN 数字）· 用户直令 · 最高优先

> 用户原话（2026-10-13）：「既然你已经说了『本项目可训数据 ~2,015B token』，那么『300B』又从哪里来呢？请不要胡说八道，首先看 MiniCPM5 已经下载 + 正在下载的，一共有多少数据，可以转化多少 Token，不要胡说八道！！」「再说 MiniCPM5 有论文放出来吗？这又是在胡说八道！！」
> 性质：实盘盘点 + 写作（CPU，不占 GPU）；不得打断在飞 P-8 训练。

① 运维已核实（写进报告，防继续误引）：
- ⚠️ MiniCPM5 没有独立训练论文。`arXiv 2602.09003` = 清华 UltraData《Tiered Data Management》数据管理框架论文（2026-02），不是 MiniCPM5 模型论文 —— v2 将其当作 MiniCPM5 训练出处 = 错。
- MiniCPM5-1B（2026-05-26）/ 2B（2026-09-07）为 OpenBMB 模型发布（GitHub/HF 模型卡）；v2 的「300B / 200B@4K+75B@32K+25B@128K」出自 CSDN 二级源，无一手依据。
- ⇒ v3 起：一律不得用论文/CSDN 的训练量数字当口径；用实盘。

② v3 唯一口径 = 实盘（用户明确要求）：
1. 盘点 MiniCPM5 相关全部数据（已下载 + 正在下载），逐源给：① 落盘路径 ② 文件数 ③ 字节数（`du -sh` / `find … | wc -l`）④ 状态（已下满 / 下载中 / 未开始）。
   - 覆盖：Ultra-FineWeb(base en/zh) · Ultra-FineWeb-L3 · UltraX-Preview · UltraData-Code · UltraData-Math · UltraData-SFT/Agent-SFT · （85M 多模态单独列，标注非 LLM 投料）。
   - 数据线口径可复用（`DATA_LEDGER.md` / `MEMORY_DATA.md`），但须上机 `du` 复核，冲突以实测为准。
2. 换算 token：用实测密度（tok/byte）——已分词在盘者用实测 token（如 R3 全量 = 1483.91B tok / 5.94TB）；未分词者用密度估算并标「估」。
3. 总计：已下满（确定） / + 下载中（估） 两条合计 —— 即「一共有多少数据 / 可训多少 token」。

③ 交付：覆盖 `run/report_pretrain_formal_train_plan.html`（v3 · 中文 · 自包含 · ≤200KB）。结构：
① HERO + TL;DR：实盘 = X TB / Y token（先答用户那一问）
② 实盘盘点主表（逐源：路径 · 文件数 · 字节 · 状态 · token · 密度/token 来源）
③ token 汇总（已下满 / 下载中 / 总计）
④ 训练配方：按实盘总量做 WSD（warmup/stable/decay token 分配）+ 总步数
⑤ 双机 16×H100 墙钟（基准用实测单机 8 卡 249K tok/s；DP16 近线性待彩排·标「待验」）
⑥ 前置清单 / 风险 / launcher
⑦ v2 → v3 修订说明（为何弃 300B：无一手来源 + 与实盘 2,015B 自相矛盾）+ 诚实条款（凡「估」须标；无法溯源者标「未核」或删）

④ 红线：🚫 禁引 MiniCPM5 论文 / CSDN 的 300B；🚫 数字无溯源不准落笔；✅ 每个 token 数须给盘点命令 / 文件:行；🚫 不占 GPU、不打断 P-8 监控；commit 前缀 `pretrain plan:`；任务书 >32KB 自滚归档。

> **执行结论**：v3 报告已交付 `reports/report_pretrain_formal_train_plan.html`，实盘盘点口径，在 origin/main。

---

### 🆕 运维指令 · 2026-10-14（✍️ 放行刷新论文 —— 执行审视报告修改）· 用户直令 · 最高优先

> **用户令（2026-10-14）**：「关于白泽论文，pretrain 提到『共发现 4 项🔴硬伤、10 项🟠建议、3 项🟢可回填』。现在允许 pretrain 刷新论文。」

**性质**：纯写作，零 GPU。**主线仍是 P-8 监控**——本任务在监控空窗期做，🚫 绝不为改稿延迟/干扰 P-8 监控与 decay 切换。

**① 撤销「只报不改」红线**：放行你**修改论文 `.tex`**，执行你审视报告 `reports/report_baize_paper_review_pretrain_zh.html` 中的修改建议。

**② 🔴 硬伤（H1–H4）必须修**：
- **H1**（FP8 矛盾）：删「We adopt FP8…」，改为如实解释「FP8 在 M=65536 有 19.4% 加速，但生产 MBS2×seq=8192 远低于交叉点 M*≈30–32K，FP8 overhead 超加速（实测 s=0.91 即慢 9%）→ 故用 BF16」。
- **H2**（20B-token 笔误）：`4_llm_pretrain.tex:115,120` 的「20B-token checkpoint」→「20K-step (≈655M tokens)」。
- **H3**（层数错误）：`3_architecture.tex:11` + `4_llm_pretrain.tex:116` 的「24 Mamba-2 layers」→「52」。
- **H4**（seq 口径）⚠️ **按用户最新直令统一为 4096（非报告里的 4094）**：论文 3 处 4094 改 4096 —— `3_architecture.tex:31`、`4_llm_pretrain.tex:75`（改「8×4096≈32.8K」）、`4_llm_pretrain.tex:165`；`4_llm_pretrain.tex:35/42`、`5_llm_posttrain.tex:14` 的 4096 保持不动。**脚本 `SEQ` 改 4096 另待 P-8 整轮结束（🚫 勿动脚本、勿动正在跑的 P-8）**，论文正文只写 4096。

**③ 🟠 建议（S1–S10）均可执行**，逐条落地；其中 **S7**（PPL 4K=83.2 异常高）若无法定位根因，至少加注「评测集/方法与训练 loss 口径不同」，🚫 不许编造数值。

**④ 🟢 可回填**：**F1**（后训练 [TBD]）无数据**不填**；**F2**（P-8 结果）**待 P-8 完成后再填**（当前 loss 2.49 不是最终值，勿写入）；**F3** 已写入，可微调位置。

**⑤ 改稿纪律**：改后编译 `cd doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027 && make main.pdf`（或等效）验证 **0 error**，记页数变化；每处修改与台账对照、🚫 数字凭印象；完成后把「改了哪几处 + 编译结果」写进心跳；commit 前缀 `pretrain paper-fix:` · 任务书 >32KB 自滚归档。

> **执行结论**：论文改稿已在 #414 完成（commit 75963f3d）。H1-H4 全修 + S1-S10 全执行 + reference.bib 加 3 条引用。编译 11 pages 0 error 0 undefined ref/citation ✅。F1 不填、F2 待 P-8 完成、F3 已写入。


---

### 🆕 运维指令 · 2026-10-14（📋【v4 重做】正式训练计划 —— 逐源准确 token · 密度归因 · 全量配比+采样次数 · D 扫描能力预估）· 用户直令 · 最高优先

> 用户令（2026-10-14），逐条质问 v3 `reports/report_pretrain_formal_train_plan.html`：
> ① 已下满数据源 **密度 tok/byte 范围 0.0657–0.4977，为什么差别这么大？**
> ② **分词后的 bin 文件里一个 token 占几个字节**（比如 2 字节），那 **bin 字节数 ÷ 2** 不就是 token 数吗？
> ③ 为什么说「**训 2,232B 需 ~52 天（双机）不现实**」——**现实不现实不需要 agent 做决定**。
> ④ 首先**得到每个数据源准确的 token 数**，这事不难吧？
> ⑤ 如果**按全量来训，如何配比**？按此配比，**每个数据源平均被采样多少次**？
> ⑥ 设几个**数据量 D（100B、200B、400B、800B、1.6T、3.2T…）**，**预估 8 个常识推理均分、6 个复杂推理均分**各自能达到多少。
> **判定：v3 质量不合格 ⇒ 产 v4**（覆盖同一文件），逐条作答、每数可溯源、**不做主观「现实 / 建议」判断**。

**① 逐源「准确 token 数」（替代密度估算）**
- 目标：给每个源**准确 token 数**，🚫 **不再用密度外推**。
- 方法（必贴命令 + 原始输出）：读**分词后 `.bin/.idx`** → **token 数 = Σ bin 字节数 ÷ bytes-per-token**。
- **先核实「一个 token 占几字节」**（用户第②问）：查**分词/写盘代码 + 文件头**，确认 token id 的 **dtype**（`uint16`=2B / `uint32`/`int32`=4B）。⚠️ 本 tokenizer **vocab=129,281 > 65,536** ⇒ 若 uint16 会溢出，**大概率 4B**——**以源码 / 文件头为证，🚫 不许猜**；给结论 + 证据（`文件:行` + `xxd`/`np.fromfile` 抽样）。
- 逐源给：**原始文本字节（解压后）· 压缩字节（parquet/jsonl 的 du -sb）· token 数 · tok/原始字节 · tok/压缩字节**。

**② 密度 0.0657–0.4977 差异 —— 机制 + 证据（须查证，不许糊弄）**
- 现报告用「du -sb 的**压缩字节**」作分母、token 作分子 ⇒ 该比值 = **tok/压缩字节**，**同时混入「压缩率」与「语言/领域 tokenization」两因素** ⇒ **不是有效文本密度，不能用于跨源 token 估算**。
- 须**逐源实测（解压若干 shard）**给出：**tok/原始 UTF-8 字节（真密度）**，并解释差异来源（英语高压缩 → 低 tok/字节；中文 / 代码 / 数学符号 tokenization 更密 → 高 tok/字节；含 base64/长 metadata 的源更极端）。
- 修正后主表**以「实测 token 数」为准**；密度**仅作诊断列**，注明「**压缩态密度 ≠ 文本密度**」。

**③ 删除主观判断**
- **移除**「不现实 / 不推荐 / 建议 D=…」等**主观结论**；报告只呈现**事实与数字**（墙钟、GPU·h、成本、采样次数），**决策留给用户**。

**④ 全量训练配比 + 平均采样次数**
- 给「**按全量（在盘 ~2,232B）训练**」的**配比方案**（Stable / Decay 两段；依据 `DATA_MIX_RECIPE` + BO best `web0.827/code0.062/math0.111`），并说清**逐源如何扩配比**。
- 据此算**每源平均采样次数（epoch）=（D × 该源配比）÷ 该源 token 数** → 做成 **D × 逐源** 的表。

**⑤ D 扫描 + 8 常识 / 6 复杂 能力预估（核心）**
- **D ∈ {100B, 200B, 400B, 800B, 1.6T, 3.2T}（token）** + 基线 **44B** + **全量 2,232B** 对照。
- **8 常识均分** = `arc_challenge, arc_easy, boolq, hellaswag, openbookqa, piqa, sciq, winogrande`（zero-shot，与 P-6 / P-5b 同口径 `lm_eval`）；**6 复杂均分** = `gsm8k, math, bbh, mmlu, humaneval, mbpp`。
- **拟合法**：用**已有 ckpt 的实测 8/6 集分数**（P-5b 20B 多 ckpt + P-6 + R2）拟合 **D→能力** 曲线（log-D 线性 / 幂律 / Chinchilla 式），外推各 D；**每点给点估计 + 区间**，**区分「实测 / 拟合 / 外推」三档**。
- **web search** 借鉴公开 scaling law（Chinchilla arXiv:2203.15556 · SmolLM3 · OLMo 2 · Bai et al.），**带来源 + 访问日**，并说明与本模型（2.22B hybrid）设定的差异与局限。
- ⚠️ **3,200B > 在盘 2,232B** ⇒ 该档需**重复采样（>1 epoch）**：**显式声明**并讨论「数据重复对能力的影响」（引已有 epoch-scaling 证据；跨域不可直接搬运，注明）。
- 交付 **scaling 曲线图**（SVG：8 常识 & 6 复杂各一条）。

**⑥ 交付与纪律**
- 覆盖 `reports/report_pretrain_formal_train_plan.html`（中文 · 自包含 · 内联 CSS/SVG · 零外链 · ≤200KB）；加「**v3→v4 修订说明**」（逐条对应本令 ①–⑤）+ 诚实条款（阈值 / 置信 / 外推风险）。
- 每个数字**可溯源**（命令 / `文件:行` / data 线实测）；🚫 编造 · 🚫 复用陈旧聚合值 · 🚫 主观判断。
- 🚫 不占 GPU、不打断 P-8 训练 / 监控；纯 CPU + web search。
- commit 前缀 `pretrain plan:` · 任务书 >32KB 自滚归档。


---

### 🆕 运维指令 · 2026-10-14（🔧 修复 decay 段 LR 未衰减 + 重跑 decay）· 用户直令 · 最高优先

> **用户令（2026-10-14）**：「pretrain LR 未衰减：安排 pretrain 审视 decay 脚本，是否有问题。decay 不需要加载原来 stable 的优化器，只加载权重，稍稍 warmup 后，直接 decay 到 1e-5 即可。LR 不降不行，需要修复。」

**① 审视（先查根因，贴源码 `文件:行` 证据，不许猜）**：
- 读 `pretrain_launcher.py` 的 resume 逻辑：同名 `--name p8_adamw` 如何加载 `iter_0009441`，是否**连带加载 optimizer state + LR 调度器状态**。
- 核实 `baize_p8_decay.sh` 传入的新调度参数（`--lr-warmup-iters 0 --lr-decay-iters 1049 --lr-decay-style WSD --lr 1e-3 --min-lr 1e-5`）是否被 **resume 的 optimizer state 覆盖** → 即 LR 卡 1e-3 恒定的根因（当前 decay 段 27 个 log 点 LR=1e-3 未衰减正是此因）。

**② 修复（按用户给定方案逐字落实）**：
- **decay 段只加载权重，🚫 不加载 stable 的 optimizer state**：用 launcher 已有的 `--no-load-optimizer` / `--no-load-lr-state`（或等价）flag；若 launcher 无此开关，则在 launcher 里**加一个最小改动**（新 flag，默认关闭，decay 时开启）。
- **给稍许 warmup**（如 ~50–100 步，替代当前 `WARMUP=0`），然后 **LR 从 1e-3 线性 decay 到 1e-5**，覆盖 decay 段。

**③ 重跑 decay 段**：
- 停当前错误的 decay 进程（PID 1744126，LR 卡 1e-3 的那个）。
- 🚫 **不重跑 stable 段**（stable 已正确完成，ckpt@9441 有效；SFT blend 不变）。
- 从 `ckpt@9441` 重跑 decay（只加载权重 + warmup + decay 1e-3→1e-5），产出 final `ckpt@10490`。

**④ 纪律**：改脚本后先语法检查/冒烟再跑；停旧 decay 后等 ~30s 待 GPU 释放；🚫 不碰 watchdog loop（PID 1391466）；**seq=4094 保持**（与 stable 一致，P-8 整轮 4094 不变）；修复 + 重跑结果写心跳；commit 前缀 `pretrain decay-fix:` · 任务书 >32KB 自滚归档。

---

### 🆕 运维指令 · 2026-10-15（⚡ 评测提速 v2：自搜 lm_eval 多卡用法 · 8 GPU 用满 · 尽快出结果 + 给 ETA）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「评测效率太低。你有 web search，自己搜 lm_eval 怎么用多卡/并行框架统筹资源，14 个 task 一次跑、8 GPU 用满，尽快出结果，并给出 ETA。」

**① 目标**：P-8 final ckpt 的 14 集（常识 8 + 复杂 6）lm-eval 评测，**提速到 8 GPU 打满**，不要串行单卡跑。

**② 做法（你自行 web search lm_eval 官方多卡/加速方案，具体参数你决定）**：
- 用 lm_eval **一次指定 14 个 task**，并用**并行框架统筹资源**（如 `accelerate launch --multi_gpu --num_processes 8` 数据并行，或 `--model vllm` 多卡推理——以你 web 搜到的官方推荐为准）。
- batch size 等按 GPU 利用率自行调优到打满；🚫 不要逐卡手动分任务。

**③ 交付**：① 尽快出全部 14 集分数 + 8/6 Avg；② **明确给出 ETA（几点跑完）**；③ 中文 HTML 报告。

**④ 纪律**：评测纯推理、8 GPU 可用（.29 已空）；🚫 不重训/不改 ckpt；commit 前缀 `pretrain eval:` · 任务书 >32KB 自滚归档。

---

### 🆕 运维指令 · 2026-10-15（📊 用 P-8 final ckpt 跑 lm-eval 评测：常识 8 集 + 复杂 6 集）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「pretrain 为什么不评测，不是说了常识推理 8 个评测集 + 复杂推理 6 个评测集要评测嘛。评测集如果任务书中没有那就加进去，看 Xmodel-2 论文提到的那些，使用 lm-eval 测。」

**① 背景**：早期评价是在旧里程碑 ckpt（655M~20B，P-5b 系）上做的（P-6② 常识 8 集 48/48、A 复杂 6 集 36/36）。**P-8 final ckpt（~44.4B token，final loss 1.357）尚未评测**——现在补齐这一最关键的 44B 数据点。

**② 评测对象**：P-8 final ckpt = `p8_adamw_decay/checkpoints/iter_0001149`（decay fix 后 final）。

**③ 评测内容（lm-eval，口径见本区「评测口径」）**：
- **常识推理 8 集**（zero-shot, raw accuracy + Avg）
- **复杂推理 6 集**（lm-eval 默认 n-shot + Avg；HumanEval/MBPP 开代码执行）

**④ 做法**：复用现有基建 —— ckpt→HF（`baize_p6_ckpt_to_hf.py`）→ lm-eval（常识 8 集用 `baize_p6_run_full.sh`/`baize_mix_eval.sh t2`；复杂 6 集用 `baize_complex6_eval_v2.sh`/`baize_mix_eval.sh t3`）。8 GPU 已空闲，可直接跑。

**⑤ 交付**：① 8 集 + 6 集各自的 Avg + 逐集分数；② 把 44B 点**补进 scaling 曲线**（与 P-6② 48/48 + A 36/36 的 655M~20B 曲线并图）；③ 中文 HTML 报告（如 `reports/report_pretrain_p8_lmeval_8plus6_zh.html`），含「vs Xmodel-2-1.2B / Phi-1.5-1.3B 等参照线」。

**⑥ 纪律**：纯评测（推理 GPU），8 GPU 已空可用；🚫 不重训、不改 ckpt；报数带 harness 版本 + shot 数；commit 前缀 `pretrain eval:` · 任务书 >32KB 自滚归档。


---

## 📦 [已归档 2026-10-15] P-8 细节 + R2.3 交付物（P-8 已完成：10590步/44.4B tok/final loss 1.357）

P-8 细节 —— 🏁 Stage (i) 完整训练（正式预训练）

> ## ⏸ 运维 2026-10-02 指令：P-8 暂缓启动
>
> 原话：「测数据配比需要时间，下载 base 也需要时间…因此 P-8 暂缓启动，先做配比实验和下载 base。」
>
> 原因（两条前置都未就绪）：
> 1. `Ultra-FineWeb`(base) 还在下载（115/64624，2.99 TB）—— 而它是 stable 段的主力数据；
> 2. WSD 双阶段配比实验还没做（见 `BAIZE_DATA_TASK.md` §0.6）—— P-8 吃什么配比是它要定的。
>
> → 所以：不要因为"P-5b 快跑完了"就顺手启动 P-8。 前置未齐之前，P-8 不启动。
> → 本唤醒及后续唤醒：做完 P-4R / 恢复 P-5b 之后，仍然等 data agent 的配比方案 + base 就绪。

> ## 🎯 这是 Stage (i) 的本体
> Stage (i) 的 scope 不变 = LLM 预训练（from scratch）。
> P-1…P-7 全部只是前置选型实验（token 量级 164M–655M，合计 ~85 GPU·h）。
> P-8 才是真正把 2.22B hybrid 训出来，作为 Stage (ii)–(v) 的基座。
> 🚫 不要因为"实验都做完了"就把 Stage (i) 标成完成。

> ### ⭐ P-8 训练配方（T3 定稿 · 2026-10-09）
>
> | 项 | 值 | 来源 |
> |:--|:--|:--|
> | 架构 | Mamba2-hybrid 2.22B（`--arch mamba2`，52 SSM + 4 Attn） | P-3 |
> | 并行 | TP1 · DP8（无通信税） | P-9.7 |
> | MBS | 2（⚠️ 不是 P-5b 的 MBS=1） | P-9.7 |
> | seq | 4096 | P-9.7 |
> | 精度 | bf16（FP8 在 TP1 上 s=0.91 慢 9%，不用） | T3 Test 4 |
> | GBS | 1024 | P-5b / P-5a |
> | 优化器 | `adamw`（标准 Megatron AdamW，默认） | 用户直令 2026-10-12：dist_muon 长跑 loss 发散 → 换回 AdamW |
> | LR / 调度 | 1e-3 / WSD / warmup 5% / decay 10%（AdamW 初筛定值 1e-3；A/B 验证用 3e-4 公平对照） | P-5a |
> | recompute | 不用（对 Mamba2-hybrid 无效：52/56 层 SSM 激活常量级，仅省 ~0.6GB） | T3 Test 1 |
> | 实测吞吐 | 249K tok/s（last-100 步均值，1100 步长跑确认） | P-9.7 |
>
> FP8 死路：TP1 上 M 上限 = MBS2×seq4096 = 8192（recompute 无效 → MBS 封顶 2）→ M << FP8 交叉点 M\*≈30–32K → FP8 overhead > 加速 → s=0.91。FP8 转正需 M≥32768 → 需 TP4 → 但 TP4 通信税 −6% → 净增益被吃掉。→ bf16 TP1 MBS2 是最终最优，无更优解。
>
> ⚠️ P-5b 的 148K 是 MBS=1 的数字；P-8 改用 MBS=2 → 249K（1.7× 提速：GEMM 效率翻倍 + micro-step/grad-accumulation 减半）。旧参照表里的 92.6K 是 Round 1 跨节点旧值，已作废。


输入（全部来自前序任务，不要自行改动）

| 项 | 来自 |
|:--|:--|
| GBS | P-5a 的 GBS×LR 扫描结论（若无右移则沿用 GBS=8；若 P-5a 指向更优大 GBS 则采用并注明） |
| LR / 调度 / 退火配比 | ⚠️ 2026-10-10 勘误：warmup/decay 按 比例 5%/10%（44B 档=524/1049 步，非旧 250/500）；LR=1e-3 / min_lr=1e-5（P-5a 确认 1e-3 全局极小值）；stable 配比 88:8:4（web=base 88% + code 8% + math 4%）、decay 配比 SFT 64% + L3 24% + code 8% + math 4%（见 DATA_MIX_RECIPE） |
| token 预算 | ⭐ 由 P-5b 的 loss-vs-tokens 曲线决定（曲线何时变平 → 就在那附近取预算） |
| 精度 | 若 P-4 证明 FP8 对本架构确有加速且不劣化 loss，可用 FP8；否则 bf16。必须记录采用与否及理由 |

token 预算的三档参照（按 T3 定稿吞吐 8×H100 = 249K tok/s · MBS2 · bf16 折算）

| 档位 | token | 墙钟 | GPU·h | 说明 |
|:--|:--|:--|:--|:--|
| 下限 | 44 B | ≈2.0 天 | ≈384 | Chinchilla 最优（2.22B × 20）。低于此不足以称为训练好的模型 |
| 推荐 | 100 B | ≈4.6 天 | ≈883 | 超 Chinchilla ≈2.3×；契合论文推理效率卖点（推理最优需过训练） |
| 上限 | 200 B | ≈9.3 天 | ≈1786 | 时间仍充裕，可考虑 |
| ⚠️ 不计入 | 690 B（真实全语料） | ≈32 天 | ≈6144 | `/nas_train` 只剩 32T，不要定这个档 |

> 默认按「推荐档 100B」准备；P-5b 曲线出来后，若曲线在更早处变平，就下调（省钱省时）。
> ⚠️ 最终 token 预算定下后，必须在 `MEMORY_PRETRAIN_2B.md` 里写明并上报，再启动长跑。

训练要求

1. 从零开始（不加载任何预训练权重），真实语料（`Ultra-FineWeb-L3` 全量 en 子集 + code + math 退火配比），
   不是 `ultrafineweb_l3_qa_700m` 那个 742M 小分片 —— 本次必须跑真正的全量语料。
2. WSD 完整走完：warmup 5% → stable → decay 尾段必须真的吃到退火混合（SFT 64% 退火，Stage (i) 核心配方；44B 档 = warmup 524 → stable → decay 1049 步）。
3. checkpoint 规划：至少保留 `final` + 每 10% 一个（供 Stage (ii) 选起点、供 P-6 画能力曲线）。
   ⚠️ 每个 ckpt（2.22B 含 AdamW 状态）≈ ~30 GB；`/nas_train` 只剩 32T，先算好 ckpt 留存策略与清理时机。
4. 训练中每 500 步记 `train loss` / `val loss` / `grad norm` / `tok/s` / GPU 独占核验。
5. 禁止在 P-8 期间叠加其它重 I/O 或抢卡任务（vision / data 侧要避让）。
6. 失败即如实记录：NaN / 发散 / OOM 一律记录并保留当时的 ckpt 与日志，不要静默重启掩盖。

产出

1. Stage (i) 最终 checkpoint（Stage (ii)–(v) 的基座）—— 这是本项目最关键的单个产物。
2. `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加 P-8 节：完整 loss 曲线、实际 token 数、实际 GPU·h、
   最终 `val loss`、与 P-5b 曲线预测值的对照（预测量 vs 实测量，这是对 scaling 曲线的一次真检验）。
3. 论文回填建议：§4 应写清 实际训练 token 数 / GPU·h / 最终 loss，
   把"从零训练一个 2.22B hybrid"的规模与代价如实写出来（并处理 §6 #13 的 1.8T 误读问题）。
4. `BAIZE_PRETRAIN_RESULT.html` 更新为含 P-8 的最终版。
5. git commit + push（只提交文本；checkpoint 不入库）。

时间盒：下限 2.0 天 / 推荐 4.6 天（按 token 预算 · 249K tok/s）。超时或连续失败不要硬撑，
记录卡点并上报 —— 但除非运维叫停，P-8 应跑到底。

## R2.3 交付物

1. `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`（新文件）：P-1/P-2/P-3 全部结果表 +
   每条可复现命令 + 与 Round 1 的差异说明 + 「论文回填建议」段落（给出精确数值与文字建议，
   特别是「最优点是否在边界」「Δ 是否在噪声内」这两个结论该怎么写）。
2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_PRETRAIN_RESULT.html` 或新建 `BAIZE_PRETRAIN_RESULT_ROUND2.html`（自包含）。
3. 🚫 不要修改 `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` 与 `main.tex`——
   论文已由外部统一重构并推送，回填由外部完成。你只在报告里给「回填建议」。
4. 正常更新 `MEMORY_PRETRAIN_2B.md` 与 `daily-memories/`。
5. git commit + push，并严格走本文件顶部的「git 同步规则」（fetch → 必要时 `pull --rebase` → push → 确认 0/0）。


## [归档 2026-10-16] 3 个已完成的 2026-10-15 运维指令块

### 🆕 运维指令 · 2026-10-15（📥 下载 Xmodel-2/2.5 decay 后 final 实测 14 集 · 眼见为实验证 decay 提升）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「你可以下载 decay 后的 Xmodel-2/2.5 看一看嘛，眼见为实。」

**① 目标**：下载 Xmodel-2 / Xmodel-2.5 的 **decay 后 final ckpt**，实测 14 集，眼见为实对比「stable 段末点 → decay 后 final」的真实提升量。

**② 做法**：
- **Xmodel-2.5 final**：从主仓库 `XiaoduoAILab/Xmodel-2.5` 下载最终 ckpt（history 仓库仅 step 2000~106000、无 final decay）。
- **Xmodel-2 final**：已实测 41.76%，可复用；重点补 Xmodel-2.5 final。
- lm-eval **0-shot** 测 14 集（Common8 + 复杂 6），与 stable 段中间 ckpt 同口径。

**③ 对比输出**：decay 前（stable 末点）vs decay 后（final）的 Common8 + 14 集逐项提升量；纸面 61.79 vs 实测的口径差异说明；中文 HTML + **ETA**。

**④ 纪律**：🚫 不重训 BaiZe；下载带 proxy 错峰 IO；数字带 harness 版本 + shot 数；commit 前缀 `pretrain eval:` · 任务书 >32KB 自滚归档。

**结论**：Xmodel-2 final CS8=64.82%/BBH=31.01% ✅, Xmodel-2.5 final CS8=65.40%/CX=32.90% ✅ 均已实测并纳入 scaling_data.json。

### 🆕 运维指令 · 2026-10-15（📈 下载 Xmodel-2/2.5 history ckpt 对比缩放曲线 · 判 BaiZe 早期学习能力）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「这里有 Xmodel-2.5 和 Xmodel-2 的检查点 https://huggingface.co/XiaoduoAILab/Xmodel-2.5-history。下载 Xmodel-2/2.5 跟数据缩放表格对应训练数据量时的检查点，绘制它们的缩放曲线，跟 BaiZe-2B 对比，从而判断 BaiZe-2B 在预训练早期的学习能力是否显著弱于 Xmodel 系列。」

**① 资源**：
- `XiaoduoAILab/Xmodel-2.5-history`：`pytorch_model.XXXXXXX` 格式（step 2000→106000，每 2000 步一个，每个 2.7GB，共 713GB）。⚠️ **只下缩放表格对应的里程碑，🚫 不要全下**。
- Xmodel-2 的 history 若不在该仓库，自行 web search 找（`Xmodel-2-history` 或类似仓库）。
- config / tokenizer 从主模型仓库取（`XiaoduoAILab/Xmodel-2.5`、`XiaoduoAILab/Xmodel-2`）。

**② 做法（自行 web search Xmodel 论文 scaling 表格）**：
- 查 Xmodel-2 / Xmodel-2.5 论文的**缩放表格**（训练数据量 ↔ step ↔ 评测分数），确定对应关系。
- 下载对应**数据量里程碑**的 ckpt（选 4–6 个，覆盖早期 ~ 44B 区间，与 BaiZe 曲线可对齐）。
- 用 lm-eval 测 14 集（常识 8 + 复杂 6；口径尽量对齐 BaiZe 评测口径，参数规模/架构差异**如实注明**）。

**③ 对比与结论**：
- 画 Xmodel-2 / Xmodel-2.5 的 scaling 曲线（常识 Avg、复杂 Avg vs token），**叠加 BaiZe-2B 曲线**（P-5b 655M~20B + P-8 中间点）。
- **核心结论**：BaiZe-2B 在预训练早期（相同 token 量）的学习能力是否**显著弱于** Xmodel 系列，量化差距 pp。

**④ 交付**：scaling 对比图（BaiZe vs Xmodel-2 vs Xmodel-2.5）+ 逐 ckpt 14 集表 + 结论（诚实：显著弱则如实报；有架构/数据/超参差异导致不可比则注明）+ 中文 HTML + **ETA**。

**⑤ 纪律**：🚫 不重训 BaiZe；下载带 proxy + 与 data 线下载错峰 IO；磁盘别超（只下里程碑 ckpt）；数字带 harness 版本 + shot 数；commit 前缀 `pretrain eval:` · 任务书 >32KB 自滚归档。

**结论**：Xmodel-2 s1 4 ckpt (10K/20K/30K/40K) eval ✅, CS8: 46.65%→49.07%→49.60%→50.31%。BaiZe 39.6B CS8=49.21% > XM2 s1/10K 39.3B CS8=46.65% (+2.56pp) → BaiZe 早期学习不弱于 XM2。scaling_report.html 含 15 points + 2 SVG 曲线。

### 🆕 运维指令 · 2026-10-15（📈 P-8 中间 ckpt 14 集 scaling 曲线 · 对比 20B + Xmodel-2/2.5）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「pretrain，基于 44B 中间检查点，测 14 集结果，绘制常识推理和复杂推理两条曲线，跟 20B 比较，跟 Xmodel-2 和 Xmodel-2.5 比较。」

**① 目标**：用 P-8 的**中间 checkpoint**（非仅 final）测 14 集，画两条 scaling 曲线。

**② 里程碑选择（你定，建议 4–6 个）**：P-8 有 `iter_1049/2098/3147/4196/5245/6294/7343/8392/9441` + decay final `iter_1149`（对应 ~4.4B→44.4B token）；按 log 等距选几个，与 P-5b 的 6 个（655M~20B）**拼接成完整曲线**。

**③ 14 集**：常识 8 + 复杂 6（口径见本区「评测口径」）。继续用 8 GPU 并行 + 大 batch（提速方案），🚫 不要串行单卡。

**④ 曲线**：两条 —— **常识推理 Avg vs token**、**复杂推理 Avg vs token**（x 轴 log）。

**⑤ 对比参照**：
- **20B**（P-5b 已有 14 集数据）。
- **Xmodel-2 / Xmodel-2.5 公开评测值**（web search 获取，1B 级各集均分；标清 shot/harness 口径差异，不可严格比则作「量级参照」并注明）。

**⑥ 交付**：2 条 scaling 曲线图 + 逐 ckpt 14 集分数表 + 结论（44B vs 20B 是否饱和、距 Xmodel-2/2.5 多远、外推）+ 中文 HTML 报告 + **ETA**。

**⑦ 纪律**：🚫 不重训；用现存 ckpt；数字带 harness 版本 + shot 数；commit 前缀 `pretrain eval:` · 任务书 >32KB 自滚归档。

**结论**：P-8 6 中间 ckpt CS8 eval ✅ (4.4B→44.4B, 44.04%→49.21%), scaling_report.html 含 BaiZe 曲线 + Xmodel 对比。BaiZe 44B CS8=49.21% ≈ XM2 s1/40K 157.2B CS8=50.31% (仅差1.10pp)。

---

## 📦 归档 · 2026-10-16：v5 计划书指令 + proxy 下载口径指令（原文搬迁，不改内容）

### 🆕 运维指令 · 2026-10-15（📘 **编写《BaiZe-2B 预训练计划书 v5》中文 HTML**）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「安排 pretrain 写预训练计划书（html、中文）：① 认真阅读、仔细参考 Xmodel-2 / Xmodel-2.5（论文在仓库中）；② 使用 MiniCPM5 的数据；③ 建议 BaiZe-2B 的训练策略 —— 例如是否像 Xmodel 一样把 Stable 分成 S1/S2、GBS 先 2M 再 4M token、Decay 是否只用少量数据（比如 20B）、每阶段数据如何配比；④ 可以 web search；⑤ 是否需要数据配比实验、如何设置优化指标。」

**① 交付物**：`reports/report_pretrain_baize2b_plan_v5_zh.html`
- **中文 · 自包含**（内联 CSS + 内联 SVG，**无外链**）；表格 ≤6；🚫 不整段贴英文原文。
- 与 v4（`reports/report_pretrain_formal_train_plan.html`）的关系：**v4 解决「数据侧精确计数/密度归因/配比」，v5 补「训练策略侧」的完整方案与决策依据**——v4 的表**不要整表重贴**，引用其 § 并给一句结论即可。

**② 必读材料（逐节读；报告里引用要写到节号/行号）**

| 材料 | 位置 | 必读重点 |
|:--|:--|:--|
| **Xmodel-2** | `Xmodel-2/xmodel-2.tex` | §Pretraining（L101–190）：**§Training Stages（L132–139）**、**§Data Ratio Optimization in the Decay Stage（L141–146）**、§Training Data Distribution（L148–154）、§Training Loss（L181–183）；附录 Wind Tunnel（L417–460） |
| **Xmodel-2.5** | `Xmodel-2.5/ACL2026/method.tex`、`result.tex` | **method §Three-Phase WSD**（W/S1/S2/D/LCR 五段的步数·GBS·SFT 占比）、**§Optimizer ablation（AdamW→Muon, +4.58pp）**；result §Training Loss（2M→4M 的 loss 台阶 + 长上下文段 52.36→52.49） |
| **MiniCPM5 数据** | `run/DATA_RESEARCH.md` §Q1(1)（官方数据源清单）；**落盘状态以 `reports/report_pretrain_formal_train_plan.html` §1.2 + 运维实测为准**；`run/DATA_MIX_RECIPE.md` | 逐源给「**MiniCPM5 官方源 → 本地落盘状态 → 本计划是否采用**」对照表；🚫 只用**已落盘/可复现**的源。<br>⚠️ **注意**：`DATA_RESEARCH.md v1.1（10-01）` 的落盘状态**多处已过时** —— 运维实测（RUN_ID 98/99 · 10-15）证明：**base en 2048 pq / base zh 256 pq / l1_en_hq 6000 文件（均 0 incomplete）、UltraX-Preview 在盘**（`/nas_train/…/openbmb/UltraX-Preview`）、**`UltraData-SFT-2605` 已下满**（1504 jsonl / ≈297GB，10-02 逐字节核验）；**确实没下的只有 `UltraData-RL-2609`**（已下令 data 线补下）。 |
| **BaiZe 自身证据** | `run/EXPERIMENTS_PRETRAIN_2B*.md`、本任务书常驻口径、P-8 实测 | P-8：stable 9441 + decay 1149 = 10590 步 / **44.4B tok** / final loss **1.357** / seq **4096**；R1→R3 BO：ρ=−0.43 → best t23=0.4155 → top-K ρ=−0.80；R3 最优 web82.7/code6.2/math11.1 |

**③ 必须逐条回答的 5 个问题（= 报告主章节，**每条都要落到 BaiZe 的具体数字**）**
1. **Stable 要不要分 S1/S2？** 对照 Xmodel-2.5（S1 3712×480≈**1.78M** tok / 270k 步；S2 3712×960≈**3.56M** tok / 260k 步）与 Xmodel-2（单段 **3.93M** tok）⇒ 给 **BaiZe 明确推荐**（分/不分 + 分段 GBS 序列 + **每段 token 预算与步数**，并按 2.22B 与 8×H100 实测吞吐折算 **GPU·h 与墙钟**）。
2. **GBS 是否「先 2M 再 4M」？依据？** Xmodel 把该 loss 台阶解释为「**增大 batch ≈ 等效降低 LR**」⇒ 给 BaiZe 的 **分段 GBS 曲线**，并写清 seq=4096 下 `micro_bs × grad_accum × 8卡` 的换算（例：4096×128×8 = 4.19M）。
3. **Decay 用多少 token？** Xmodel-2 = 5000 步 = **20B**；Xmodel-2.5 = **20k 步**（≈3.56M×20k）⇒ 给 BaiZe **推荐区间**（20B 起，30B/50B 作为备选）+ **判定依据**（建议用**现有 P-8 ckpt 沿 LR 衰减做小规模外推**，不重训）。
4. **各阶段数据配比怎么定？** Stable：web:code:math（v4 现用 88:8:4；R3 BO 给 82.7:6.2:11.1）；Decay：SFT:L3:code:math（v4 现用 64:24:8:4；Xmodel 最优 **SFT 64%（区间 60–69%）**、Xmodel-2.5 **66.9%**）⇒ **逐阶段给建议配比 + 与 Xmodel/MiniCPM5 的三方对照表**。
5. **要不要做数据配比实验？优化指标怎么设？** 必须明确「做/不做 + 把握有多大」；若做，给**可执行实验设计**：
   - 代理模型（小模型 wind tunnel：nano/tiny 或 P-5b 1.8B）· 搜索维度 · 试次数 · GPU·h 预算；
   - **优化指标**（建议显式定义：常识 8 集 + 复杂 6 集 + 中文 C-Eval/CMMLU 的**加权平均**，给出权重与理由，🚫 不要只盯 loss）；
   - **代理↔目标相关性验证**（沿用既有 ρ 口径）与**结论迁移到 2.22B 的依据/边界**；
   - 可复用基建：`baize_mix_optuna*.py`（R1/Round2/R3 BO）、R3 配比台账。

**④ 允许 web search**：可查 MiniCPM5 / UltraData 数据卡、WSD / µP / batch-scaling 等公开资料；**每条外部结论都要给可点击 URL**；查不到就写「未找到」，🚫 不编造。

**⑤ 硬口径（🚫 不得违反）**
- **不打断**正在跑的 **Xmodel-2 s1 re-eval** 与任何训练/评测；本任务原则上**零 GPU**（若确需小实验，先在此区申请，≤30 GPU·min）。
- token 数一律用 **`.bin 字节 ÷ 4`**（v4 §1.1 口径）；🚫 不得用 `du` 的压缩字节冒充 token。
- **跨栈结论必须标不确定度**：如「Xmodel-2.5 的 1.4T vs BaiZe 的 44.4B token 口径差异」「Muon 在 decay 段 +4.58pp 能否迁移到 Mamba2-hybrid」，**不得直接照抄**，要写适用边界。
- seq 口径 **4096**（用户直令）；commit 前缀 `pretrain plan v5:`；TASK >32KB 自滚归档。

**⑥ 建议报告结构**：① **结论速览**（TL;DR 表：阶段 / token 预算 / GBS / LR / 配比）→ ② **三方对照**（Xmodel-2 / Xmodel-2.5 / MiniCPM5 各自的 stage 划分与依据）→ ③ **BaiZe-2B 推荐训练策略**（W/S/D + 是否 S1/S2 + 逐阶段 token·GBS·LR·配比）→ ④ **数据配比实验**（做不做 / 怎么做 / 优化指标定义 / 预算 / 迁移性）→ ⑤ **风险与不确定性** → ⑥ **附录**（与 P-8 的差异对照 + 可复现命令骨架）。

**结论**：v5 报告 42.8KB ✅ 交付（commit fc0a292b），5问速答+三方对照+推荐策略+配比实验+风险+附录，6表1SVG，中文自包含。

---

### 🆕 运维指令 · 2026-10-15（🌐 下载 proxy 口径：92.23→hf-mirror / 92.25→hf.co · 慢则切换）· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「pretrain 主要看下载速度。如果下载太慢，可以考虑用 92.25 这个代理，同时直连 hf.co。总结：92.23 用 hf-mirror；92.25 用 hf.co。」

**① proxy 口径（常驻，下载一律按此）**：
- `http://172.19.92.23:13128`（92.23）→ 配 **hf-mirror**（`HF_ENDPOINT=https://hf-mirror.com`）。
- `http://172.19.92.25:13128`（92.25）→ **直连 hf.co**（🚫 不设 HF_ENDPOINT mirror）。

**② 当前 Xmodel decay final 下载**：
- 现走 hf-mirror（final 41%），**以实测速度为准**；太慢即切 92.25 + 直连 hf.co 续传（`hf download` 断点续传，无需从头）。

**③ 纪律**：🚫 不重训 BaiZe；下载与 data 线错峰 IO、磁盘别超；commit 前缀 `pretrain eval:` · 任务书 >32KB 自滚归档。

**结论**：Xmodel-2/2.5 final 及 history ckpt 均已下载完成。proxy 口径作为常驻知识保留在 MEMORY 中。

---

## 归档块 · 运维指令「2026-10-16（🚀 放行执行 80B decay 实验 + 用 NeMo 训 Xmodel）」— 已执行完毕，2026-10-16 归档（原文字搬，不新增/不改写）

> 【原文】**用户令（2026-10-16）**：「pretrain：放行 80B decay 实验。」

> 【原文】**🔧 用户纠正：用 NeMo 训 Xmodel，别 find 全树找 muon**：
> - NeMo/Megatron-Core 0.16.1 **自带 Muon**（`megatron/core/optimizer/muon.py`），之前 BaiZe P-8 的 `dist_muon` 就是 NeMo 训的。
> - 🚫 **不要 `find /nas_train 全树` 找 muon.py**（重 IO 全树遍历，又慢又蠢，还被 MEMORY 铁律禁止）。
> - 真正要做两件事：① **Xmodel-2.5 HF ckpt → Megatron/NeMo 格式转换**；② **复用 BaiZe P-8 的 muon 训练脚本**，把模型换成 Xmodel。

> 【原文】**① 撤销「先计划不起训」**：放行按计划书 `reports/report_xmodel25_decay_80b_plan_zh.html` 执行。

> 【原文】**② 执行要点（按计划书）**：
> - 起点：Xmodel-2.5 **stable 末 ckpt**（decay 前）。
> - decay：**BaiZe 自己配比的 80B 数据 + Muon**（对齐 Xmodel 官方 decay：71.2B / 66.9% SFT / Muon）。
> - 目标：14 集（常识 8 + 复杂 6）**超越 Xmodel-2.5 final**（CS8 65.40% / CX 32.90%）。

> 【原文】**③ 纪律**：起训前 `nvidia-smi` 确认 .29 8×H100 空窗；下载/数据错峰 data 线 IO；每阶段回报进度 + ETA；commit 前缀 `pretrain decay80b:` · 任务书 >32KB 自滚归档。

> 【结果】2026-10-16 19:14 decay 起训 RUNNING（step 190 loss 1.599 / 183K tok/s / 8×H100 100%）。**实测修正**：Megatron-Core 0.16.1 不实现 Xmodel μP 前向缩放 ⇒ HF→Megatron 转换会破坏模型 ⇒ 最终走 HF + 手写 DDP + Megatron TensorParallelMuon。
---

## 归档块之二 · 运维指令「2026-10-16（Xmodel-2.5 stable 末 ckpt + BaiZe 80B 配比做 decay · 先出计划书）」— 已执行完毕，2026-10-16 归档（原文字搬，不新增/不改写）

> 【原文】**用户令（2026-10-16）**：「安排 pretrain 用 Xmodel-2.5 stable 最后一个检查点做 decay 实验，用我们自己配比的 80B 数据做 decay，争取比 Xmodel-2.5 的 final 更强（14 个评测集）。先写个计划书（中文 html）。」
> 【原文】**① 背景**：已实测 Xmodel-2.5 final（decay 后）CS8=65.40% / CX=32.90%，stable 段普遍偏低。目标：用 BaiZe 自己配比的 80B 数据 对 Xmodel-2.5 stable 末 ckpt 做 decay，争取 14 集超越其官方 final，验证「BaiZe decay 数据配比/annealing 策略更优」。
> 【原文】**官方 decay 对照基准**：Decay token 71.2B（20,000 steps × 3.56M tokens/step）；占总训练 1.4T 的 ~5%；数据配比 66.9% 高质量 SFT + 其余；优化器 decay 阶段 AdamW → Muon（提升推理性能）。
> 【原文】**公平性**：我们给 80B 预算 > 71.2B，数据量已不落下风。**计划书须单列对照** our 80B vs Xmodel 71.2B。
> 【原文】**decay 段用 Muon（对齐 Xmodel 官方，用户直令）**：此处训练的是 Xmodel 模型（stable 末 ckpt），不是 BaiZe 原生模型——BaiZe P-8 的 dist_muon 发散是 BaiZe 架构/配方的问题，不适用于 Xmodel。Xmodel 官方自己也是「stable 段全用 Muon 会发散 → 只能把范围缩小到 decay 段才用 Muon」。
> 【原文】**② 计划书须先定清（6 点）**：① 起点 ckpt（哪个 step / 对应 token / 本地是否已下载）② decay 数据配比（BaiZe 80B 权重与 token 分配）③ decay 超参（WSD: warmup/decay 步数/LR/seq/GBS + tokenizer 兼容处理）④ 14 评测集（常识 8 + 复杂 6，基准 = Xmodel-2.5 final CS8 65.40%/CX 32.90%）⑤ 算力/墙钟（GPU·h + ETA）⑥ 风险/可行边界（tokenizer 归属、ckpt 转 HF / 推理 / lm-eval 链路需验证项）。
> 【原文】**③ 交付**：中文自包含 HTML 计划书，含上述 6 点 + 预期提升 vs 基线。**④ 纪律**：🚫 先计划不起训；数字带出处；commit 前缀 `pretrain plan:`。

> 【结果】计划书 `reports/report_xmodel25_decay_80b_plan_zh.html`（36KB）已于 2026-10-16 12:05 交付（commit cd67a21b）；同日 13:47 放行执行，19:14 decay 起训 RUNNING。

## 归档块之三 · 运维指令「2026-10-16 22:4x（🔧 MBS 卡在 logits 显存 → 改「分块 CE」）」— 已执行完毕，2026-10-17 归档（原文字搬，不新增/不改写）

> 【原文】### 🆕 运维指令 · 2026-10-16 22:4x（🔧 **MBS 卡在 logits 显存 → 改「分块 CE」（配方中性、零新依赖）**）· 运维提示 · 最高优先
> 【原文】**诊断（运维读你的 `baize_xmodel25_decay_v2.py` L400-411）**：loss 仍走 HF 内置 `model(input_ids=..., labels=labels).loss` ⇒ **会 materialize 全量 logits `[MBS, seq-1, 129281]`**。MBS=4/seq=3712 时 bf16 ≈ **3.8GB**、CE 内部若 upcast fp32 ≈ **7.7GB** —— **与实测 7.15GB 吻合，这正是 MBS=4 OOM 的根因，不是卡不够大。**
> 【原文】**① 改「分块交叉熵」（数值等价 ⇒ 配方中性、无新依赖）**：不要走 `labels=` 路径，取 hidden 后按 seq 分块算 CE：
> 【原文】- `hidden = model.model(input_ids=input_ids).last_hidden_state` → `[B,S,H]`；`W = model.lm_head.weight`
> 【原文】- 逐块 `h = hidden[:, s:s+CHUNK]`（**CHUNK 从 256~512 起试**）→ `lg = h @ W.T`（有 bias 再 `F.linear`）→ `F.cross_entropy(lg.float(), labels[:, s:s+CHUNK], ignore_index=-100, reduction='sum')`，累加后 **÷ 有效 token 数**。
> 【原文】- **logits 峰值从 `B×S×V` 降到 `B×CHUNK×V`（256/3712 ≈ 7%）⇒ 预计再省 3~6GB ⇒ MBS 4 / 6 / 8 有望都放得下**（配合 GC off）。
> 【原文】- ⚠️ 用 **`reduction='sum'` ÷ 有效 token 数**（勿用 mean 再平均，会引入分母偏差）；`masked_fill(labels==eos,-100)` 保持。
> 【原文】- 可作正式 v2 的默认路径（不是只用于 profile）。
> 【原文】**② A/B 矩阵更新**：A3/A4 改由「**分块 CE + MBS 4 / 8**」定义；某档若 OOM，先降 CHUNK 或再降一档 MBS，**并如实记录**。
> 【原文】**③ 交付别漏**：**A0–A5 对比表** + **新 ETA**（现在 profile 脚本已有 6 个，注意 profile 输出目录别混）。
> 【原文】**④ 纪律**：测完**立即**起正式 run（`3712 / 19980 / GBS960 / 最优 MBS / GC off`）；🚫 不长时间空置 8 卡；commit `pretrain perf:`；任务书 >32KB 自滚归档。

> 【结果】分块 CE 已实现并修复双 bug（label double-shift + μP logit scale=1/6）；A0–A5 完成；v2 正式训练 2026-10-17 01:20 起训（MBS=4 + chunked CE + compile default + no_sync，~299K tok/s，ETA ~66h）。


## 归档块之四 · 运维指令「2026-10-16 22:1x（🛑 停掉当前 decay 训练，用 8 卡做完整 A/B 调试）」— 已执行完毕，2026-10-17 归档（原文字搬，不新增/不改写）

> 【原文】### 🆕 运维指令 · 2026-10-16 22:1x（🛑 **用户已授权：停掉当前 decay 训练，用 8 卡做完整 A/B 调试**）· 用户直令 · 最高优先
> 【原文】**用户令（2026-10-16 22:1x）**：「pretrain 可以把当前训练停下来调试。」
> 【原文】⇒ **本条覆盖上一版「🚫 不得与在训抢卡」的限制**：现在**允许且要求**先停训、把 8 张卡腾给 profile，测出最优配置后**立刻正式重起**。（当前 run 仅 ~350 步、**首个 ckpt(@2000) 未落盘** ⇒ 停掉无损失；正式重起仍从 `step_532000` 开始。）
> 【原文】**① 立即停训（腾卡，写进 MEMORY）**：**只** `pkill` 匹配 `baize_xmodel25_decay_train.py` 及其 torchrun（当前 **torchrun PID 2080678 + 8×rank 2082634..2082645**）；⛔ **不要杀 pretrain loop（PID 1294147）**、⛔ 不要碰 `.12`。停后 `nvidia-smi` 确认 8 卡释放（≤1GB），记「停训时刻 + 释放确认」。
> 【原文】**② 8 卡 A/B 矩阵（逐档跑 · 每档 ≥30 步取稳态 · 每档记 tok/s + 8 卡显存 + util）**：
> 【原文】| 档 | 配置 | 目的 |
> 【原文】|:--|:--|:--|
> 【原文】| **A0** | 现版基线（旧数据管线 + `--grad_checkpoint` + MBS2） | 复现 **183K** 基线 |
> 【原文】| **A1** | A0 + `--fast_data`（`DataLoader(num_workers=8, pin_memory, prefetch_factor=4, persistent_workers)` + `np.concatenate`/`torch.from_numpy` 替 `tolist()/extend` + H2D `non_blocking=True`） | 量化**数据瓶颈** |
> 【原文】| **A2** | A1 + **关 `--grad_checkpoint`** | 量化 GC 工时 |
> 【原文】| **A3** | A2 + **MBS 4**（`grad_accum` 30，**GBS 仍 960**） | 量化 MBS 收益 |
> 【原文】| **A4** | A3 + **MBS 8**（`grad_accum` 15，**GBS 仍 960**；显存不够则跳过并如实记录） | 探 MBS 上限 |
> 【原文】| **A5** | 最优档 + `--adamw_fused`（若尚未含） | 收尾小项 |
> 【原文】⚠️ **MBS 变化必须同步调 `grad_accum`，保持 `GBS=960` 不变**（否则改的是训练语义、不算配方中性；若确要试 GBS，单列一档并标注）。
> 【原文】**③ 选最优 → 一次性正式重起**：`SEQ=3712 / ITERS=19980 / GBS=960 / MBS=最优 / 起点 step_532000 / 优化器 Muon / LR 1.67e-3→1e-5`，**保留分段计时日志**（`t_data / t_fwd_bwd / t_opt`，每 10 步打印）。🚫 **不得长时间空置 GPU**（profile 目标 ≤1.5h，测完立即起正式 run）。
> 【原文】**④ 交付**：**A0–A5 对比表**（档 / 改动 / tok/s / 显存 / util / 相对 A0 提升 / 结论）+ **新 ETA** → `MEMORY_PRETRAIN_2B.md` + `daily-memories/`；commit 前缀 `pretrain perf:`。
> 【原文】**⑤ 纪律**：⛔ 不干扰 data 线；**任务书现 34.9KB ⇒ 本轮须归档已闭合块回 ≤32KB**。

> 【结果】A0–A5 对比完成：A0(298K)/A1(304K, loss bug)/A2(280K no_sync OFF)/A3(301K, bug)/A4(FAIL reduce-overhead)/A5(299K 修复后)。结论 = MBS4+chunked CE 与 MBS2 HF 吞吐等价，价值在 VRAM 效率。


## 归档块之五 · 运维指令「2026-10-16（⚡ decay 提速专项：先量化、再修数据管线/GC/MBS）」— 已执行完毕，2026-10-17 归档（原文字搬，不新增/不改写）

> 【原文】### 🆕 运维指令 · 2026-10-16（⚡ **decay 提速专项：先量化、再修数据管线/GC/MBS**）· 用户直令 · 最高优先
> 【原文】**用户令（2026-10-16）**：「pretrain 训练效率太低（183K tok/s，我 BaiZe-2B 都有 249K）。是否 Muon 实现效率不高？**如果是就换 AdamW**。另外显存还有空间（58–60GB/卡），**看有没有机会把 MBS 提升一倍**。另外为省时间，**可考虑 seq-len 与总数据量都对齐 Xmodel-2.5（71.2B）**。」
> 【原文】**运维实测结论（逐条，均有出处）**：
> 【原文】- **① 🚫 不换 AdamW —— Muon 不是主因**。P-8 基线（`EXPERIMENTS_PRETRAIN_2B.md:108-120`）**同样是 MBS=2 / GBS≈1024 / seq4094 / DP8 / bf16**，却跑到 **249K tok/s（~17.5s/step、565 TFLOP/s/GPU）** ⇒ **MBS 相同、吞吐差 27%，问题不在 MBS、也不在 batch 形状**。差别在**技术栈**：P-8 = **Megatron-Core 全栈**；本 run = **HF `AutoModelForCausalLM` + 手写 DDP + 手写 `BlendedDataLoader`**（因 Megatron-Core 0.16.1 不实现 Xmodel μP 前向缩放，转换会破坏模型）。Muon 每**优化器步**仅更新一次（共 20346 步），被 **60 个 micro-step** 摊薄 ⇒ **非主因**；且换 AdamW 会**破坏与 Xmodel 官方「同配比·同优化器」的可比性**（本实验立论基础）⇒ **不许换**。
> 【原文】- **② 真瓶颈（可修，配方中性）**：数据管线 **单进程 / 无 worker / 无预取**，且**在训练主循环内同步**做 `IndexedDataset` 随机取 doc → `doc.tolist()` → Python `list.extend` 拼到 4096（`baize_xmodel25_decay_train.py:116-138`，纯 Python 逐 token）→ `.to(device)` **未用 `non_blocking`**（L320）⇒ **每 micro-step GPU 都在等 CPU**（60 次/步）。
> 【原文】- **③ 梯度检查点默认开着**（L214 `--grad_checkpoint` default=True）→ 反向重算 ≈ **+20~30%** 时间（P-8/Megatron 默认关闭）。
> 【原文】- **④ seq / 总 token 口径已澄清（落地方案见 §⑤）**：计划书口径 = **seq 3712 / 3.56M tok·步⁻¹**（`reports/report_xmodel25_decay_80b_plan_zh.html` §4）；起训脚本曾按「**4096 = 2¹²**」铁令覆盖为 4096（`baize_xmodel25_decay.sh:17`）——**该铁令只约束 BaiZe-2B 自研模型**，本 run 训的是 Xmodel ⇒ **本轮改回 Xmodel 原生 3712**。
> 【原文】**① 先量化（改前必做，10 步）**：主循环加分段计时并打日志 —— `t_data`（next(data_iter) + H2D）/ `t_fwd_bwd` / `t_opt`（zero_grad + clip + muon + adamw），每 10 步打印均值。**用数据定位瓶颈，🚫 不许拍脑袋改配置。**
> 【原文】**② 配方中性提速（不改变训练语义；改完从 step_532000 重起跑）**：
> 【原文】- **a. 数据管线**：改 `torch.utils.data.DataLoader(num_workers=8, pin_memory=True, prefetch_factor=4, persistent_workers=True)`（或后台预取线程 + 队列）；`get_batch` 去掉 `.tolist()/extend`，改 `np.concatenate` + `torch.from_numpy`；H2D 改 `non_blocking=True`。
> 【原文】- **b. 关梯度检查点**：`--grad_checkpoint` 默认改 **False**（显存不足再回退）。
> 【原文】- **c. A/B `MBS 2→4`**：`grad_accum` 60→30（**GBS 保持 960 不变**），各跑 ~30 步测 tok/s；显存有 ~20GB 余量，预期可容纳。
> 【原文】- **d. 可选**：AdamW 组加 `fused=True`。
> 【原文】**③ 只有在①的分段计时**证明 Muon（含 `num_ns_steps=5` / `scale_mode="spectral"` / FP32 upcast 补丁）**占比显著**时，才允许动优化器 —— 且须**附计时证据**再定是否改。
> 【原文】**④ 交付**：**tok/s 前后对比表 + 分段计时表 + 新 ETA** → `MEMORY_PRETRAIN_2B.md` + `daily-memories/`；commit 前缀 `pretrain perf:`。
> 【原文】**⑤ ✅ 本轮执行「seq / 总 token 对齐 Xmodel-2.5」（用户 2026-10-16 澄清：「**4096=2¹²**」铁令**只约束 BaiZe-2B 自研模型**；本 run 训练的是 **Xmodel** ⇒ 按 **Xmodel 原生口径**走，两令不矛盾）**：
> 【原文】- `baize_xmodel25_decay.sh`：**`SEQ 4096 → 3712`**；**`ITERS 20346 → 19980`**（= **71.2B ÷ (960 × 3712 = 3.56352M tok/步)** ≈ 官方 **20,000 步 × 3.56M**，即 **总 decay token 与官方一致 = 71.2B**）。
> 【原文】- **`GBS` 保持 960**（与官方 3.56M tok/步 等价）；**优化器仍用 Muon**；**起点不变**（step_532000）；LR 曲线保持 `1.67e-3 → 1e-5`（WSD，warmup 100）。
> 【原文】- 收益：墙钟 **省 ~11% ≈ 0.5 天**，且与官方 **apples-to-apples**（唯一变量 = 数据配比，本实验的立论目标）。
> 【原文】**⑥ 一次重起、两件事一起落**：**seq/ITERS 对齐** 与 **§② 的配方中性提速（数据管线 + 关 GC）** 在**同一次重启**完成，避免重复起停；**MBS 的 A/B（2→4）放在重起之后单独测**（不与其它改动叠加，便于归因）。
> 【原文】**⑦ 交付**：对齐后的 **step / loss / LR / ETA 表** + **提速前后 tok/s 对比** + **分段计时表** → `MEMORY_PRETRAIN_2B.md` + `daily-memories/`；**并同步更新 `reports/report_xmodel25_decay_80b_plan_zh.html` §4 对照表**（our **80B→71.2B**、**19980 步**、公平性论述改为「**同 token 预算 71.2B，唯一变量 = 数据配比**」）；commit 前缀 `pretrain decay80b:` / `pretrain perf:`。
> 【原文】**⑧ 纪律**：⛔ 不干扰 data 线；任务书 >32KB 自滚归档。

> 【结果】分段计时已落地并每 10 步打日志（t_data≈0.5ms/micro≈0%，fwd_bwd≈393ms≈98%，opt≈155-175ms≈1%）；fast_data + GC off + MBS4 已落；seq 3712 / ITERS 19980 已对齐 Xmodel-2.5 71.2B（v2 训练已按此起训）。


## 归档块之六 · 运维指令「2026-10-16 19:0x（⏱ 加急：立刻起训 80B decay，禁止再空转）」— 已执行完毕，2026-10-17 归档（原文字搬，不新增/不改写）

> 【原文】### 🚨 运维指令 · 2026-10-16 19:0x（⏱ **加急：立刻起训 80B decay，禁止再空转**）· 用户质询 · 最高优先
> 【原文】**用户质询（2026-10-16）**：「pretrain：执行 80B decay 实验 —— 他俩到底还在等什么？不知道 GPU 很贵吗？」
> 【原文】**事实（运维实测）**：放行令（13:47）+ NeMo 纠偏（15:32）均已下发，但本线**自 13:19 起零提交**，`.29` 8×H100 **空了 5.5 小时**。已另经 `ops/inbox.md` 下发 **RUN_ID 109** 核查 loop 死活并按需重启。
> 【原文】**① 立刻执行（🚫 不得再以「等运维指令」为由空转）**：按 13:47 放行令 + 15:32 NeMo 纠偏起训 80B decay —— 起点 = **Xmodel-2.5 stable 末 ckpt（step 532000）**；数据 = **BaiZe 80B 配比**；优化器 = **Muon（NeMo/Megatron-Core 0.16.1 自带）**；🚫 **禁止 `find 全树` 找 muon.py**。目标 = 14 集超越 Xmodel-2.5 final（CS8 65.40% / CX 32.90%）。
> 【原文】**② 执行顺序**：① `nvidia-smi` 确认 `.29` 空窗 → ② **HF ckpt → Megatron/NeMo 格式转换**（先跑小样本 smoke 再全量）→ ③ **复用 BaiZe P-8 的 muon 训练脚本**（只换模型）→ ④ 起训并回报 `step / loss / tok·s⁻¹ / ETA / 卡占用`。
> 【原文】**③ 每轮唤醒必须落盘**：`MEMORY_PRETRAIN_2B.md`（step / loss / ETA / 卡占用）+ `daily-memories/` —— 哪怕单轮 cline 只跑 25 分钟也要写，🚫 **禁止静默**。
> 【原文】**④ 阻塞必须显式报告**：卡在 ckpt 转换 / tokenizer 不兼容（128K vs 129K）/ 数据路径 / 依赖缺失等，须写明「**卡点 + 已试方案 + ETA + 需要什么**」，🚫 不许静默等待。
> 【原文】**⑤ 纪律**：🚫 不 kill 别线进程 · 与 data 线错峰 IO · commit 前缀 `pretrain decay80b:` · 任务书 >32KB 自滚归档。

> 【结果】已起训（2026-10-16 19:14 decay RUNNING）；实测修正 = Megatron-Core 0.16.1 不实现 Xmodel μP 前向缩放 ⇒ HF→Megatron 转换会破坏模型 ⇒ 最终走 HF + 手写 DDP + Megatron TensorParallelMuon；后升级为 chunked CE v2 正式训练（2026-10-17 01:20）。

---

## 归档块 N · 2026-10-17 12:2x「停止 .12 的 80B decay → 迁回 .29」（原文，2026-10-17 20:4x 运维搬出）

### 🆕 运维指令 · 2026-10-17 12:2x（🛑 停止 `.12` 的 80B decay → 迁回 `.29` 续跑；`.12` 让给 vision）· 用户直令 · 最高优先

> **用户令（2026-10-17）**：「为什么 pretrain 占用 .12 呢？把它kill掉。pretrain用.29，vision用.12」

**① 根因（写进 MEMORY，不甩锅）**：crash5/6 是 `.12` 本地 `emerging_optimizers 0.5.0a0` 与 Megatron API 不匹配；为用该本地安装，把 80B decay 从 `.29` 迁到 `.12`。这是**兼容性临时迁机**，不是永久分卡。现按用户令**固定 `.29`**。

> ⚠️ **先查状态再动手（2026-10-17 11:5x 实测）**：`.29` **已在健康 RUNNING**（#488：08:44 起，step~860 @11:36，loss 2.03，296.8K tok/s，8 卡 100%/51.7GB，0 crash），且 **`.12` 已于 11:37 释放**（`GPU12_RELEASED=1`）。⇒ **目标已达成，不要重启**（重启会丢 860 步≈2.8h）；**只需上报 ETA**。仅当 `.29` 无进程/挂了，才执行 ②③ 的重启流程。

**② 停止 `.12`（先保 ckpt，再 kill）**
- 记录原文：`date`、`nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv`、`pgrep -af 'baize_xmodel25_decay|torchrun.*baize_xmodel25_decay'`。
- 查 ckpt：按脚本实际 `OUT`（`grep -n '^OUT=' run/baize_xmodel25_decay_v2.sh`）；`ls -lt $OUT/latest.pt $OUT/checkpoint_*.pt`；记录最新 step/mtime。
  - 有 `latest.pt`（step≥500）→ 以它 resume；
  - 只有 `step_532000` → 从 `step_532000` 重起，MEMORY 记「损失步数 ≈ X（≈X×11.9s）」。
- 停止：`kill -TERM <torchrun leader>` → ≤120s 未退再 `kill -KILL` leader + workers。**只杀本任务 PID**；🚫 不碰 `baize_pretrain_loop.sh` / `baize_vision_loop.sh` / `ops_relay.sh` / data 下载 / harness。
- 验证：`.12` 8 卡 `0 MiB / 0%`、无 compute apps；原文贴 MEMORY，写 `GPU12_RELEASED=1 <时间>`；**立即 commit `pretrain move29: release .12` 并 push**（vision 依赖此信号，但用户令优先，不阻塞 vision）。

**③ 迁回 `.29` 续跑**
- `.29` preflight（原文落盘）：`nvidia-smi` 8 卡空；`py310`；`torch / transformers / megatron.core / emerging_optimizers` 版本；**打印 `OrthogonalizedOptimizer.__init__` 与 `newton_schulz_tp` 签名**。
  - ⚠️ `.12` 的 crash5/6 monkey-patch 只针对 `0.5.0a0`；`.29` 版本若不同，**不要盲套 patch**，按实际签名适配；`_orig_mod` 保存修复与版本无关，保留。
- 起训：`cd run && setsid bash baize_xmodel25_decay_v2.sh > /tmp/baize_xmodel25_decay_v2_dot29.log 2>&1 < /dev/null &`；用 `--resume`（脚本已支持）指向最新 ckpt；确认 step/loss/tok/s、0 crash；首 ckpt 验证 `_orig_mod` 不崩。
- 配方不变（seq 3712 / GBS 960 / ITERS 19980 / LR 1.67e-3→1e-5 / SAVE 500）；**不得改配方**。
- MEMORY 写：机器 `.29`、PID、resume step、ETA、首 ckpt 时间；commit `pretrain move29:`。

**④ 纪律**：只停自己任务；停前必须确认 ckpt；不删 ckpt；不占 `.12`；与 vision ArmB 错峰 IO；任务书 >32KB 自滚。

**⑤ 用户追加令（2026-10-17 12:4x）**：**「pretrain 在 `.29` 重启训练；以后不许随意换服务器。有问题上报或自己解决。训练重启后上报 ETA。」**
- **`.29` 运行是硬指令；已在跑则不重启**：若健康 RUNNING（当前 step~860）→ **只报 ETA，不重启**；若挂了/无进程 → 从最新 ckpt resume，重启后 **≤30min 内**在 MEMORY 报：机器、PID、resume step、实测 s/step、tok/s、首 ckpt 时间、**ETA**。
- **服务器固定**：`.29` = pretrain、`.12` = vision；**未经用户明确批准不得再换机**；故障必须**就地**定位/修复（版本/API/显存/NCCL 等），修不了再上报 blocker + 选项，不得擅自迁移。
- `.29` 若 v2 compile 不生效（吞吐回落 ~184K tok/s / ~20s/step），按实测报 ETA（可能 ~108h），不得隐瞒。


---
## 📦 归档 2026-10-18：§12:0x P0 修复 .29 ops 中继 + §10-18② v5 中文 HTML / 数据前置实测（原文搬迁，agent 自滚归档）

### 🆕 运维指令 · 2026-10-18 12:0x（🚨 P0：立即修复 `.29` 的 ops 中继；先于一切巡检/写作）· 用户直令 · 最高优先

> **背景**：`run/ops/inbox.md` 的 RUN_ID 123（09:54 推送）至今无回执，`run/ops/.last_run_id` 仍为 **122**；而 pretrain（11:42）/vision（11:21）仍能正常 push ⇒ `.29` 本机 ops 中继停摆/冻死，不是网络。你与中继同在 `.29`，由你修复。
> ⚠️ 历史事故：命令行里把 `pkill -f "ops_relay.sh"` 与启动命令写在一起 → 自匹配，把中继和执行 shell 一起杀。**必须写进脚本文件再执行**。

**① 安全重启（照抄执行，一次跑完）**
```bash
cat > /tmp/fix_relay_29_1018.sh <<'EOF'
set -u
R=/nasdata/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "=== BEFORE $(date '+%F %T') ==="
pgrep -af 'bash [o]ps_relay[.]sh' | cut -c1-160 || true
echo -n "last_run_id="; cat "$R/ops/.last_run_id" 2>/dev/null || echo MISSING
pgrep -f 'bash [o]ps_relay[.]sh' | xargs -r kill
sleep 2
cd "$R"
env -u http_proxy -u https_proxy -u ALL_PROXY -u all_proxy setsid bash ops_relay.sh > /tmp/baize_ops_relay_29.log 2>&1 < /dev/null &
sleep 3
echo "=== AFTER ==="
pgrep -af 'bash [o]ps_relay[.]sh' | cut -c1-160 || true
tail -10 /tmp/baize_ops_relay_29.log
EOF
bash /tmp/fix_relay_29_1018.sh
```
- **判据**：≥1 个 `bash ops_relay.sh` 进程；**60–120s 内** `.last_run_id` 从 **122 → 123**，且 `run/ops/outbox.md` 末尾出现 `RUN_ID 123` 回执（含 `.29` loop/GPU + `.12` git 只读诊断）。
- 若 2 次仍不起：贴 `pgrep -af 'bash [o]ps_relay[.]sh'`、`tail -40 /tmp/baize_ops_relay_29.log`、`ls -l run/ops/.last_run_id` 原文报 blocker，🚫 不再反复 kill。
- 🚫 红线：不碰 torchrun/训练/ckpt；不 kill pretrain loop；不改 `ops_relay.sh` 本体；不清理 `/tmp`。**（仅限本中继修复块；训练死亡见顶部 16:2x，必须 resume）**
- ✅ 完成后在本轮 MEMORY 记：中继 PID、`.last_run_id`、outbox 的 RUN_ID 123 摘要、error scan；commit 前缀 `pretrain ops:`。



### 🆕 运维指令 · 2026-10-18②（📄 补交 v5 中文 HTML + 🔧 启动 v5 的数据前置实测：分词吞吐与 500B 可行性）· 用户直令 · 最高优先（纯 CPU，零 GPU）

> **背景**：`run/PLAN_V5_STABLE_1.5T.md` 已交付（69.7 天 / 250 ckpt / ABF 次序采纳 ✅）。但 **① 中文 HTML 还没出**；**② 计划里把 `en_v1_4` 未分词列为 🔴 阻塞项（R3），却写了"分词吞吐未知，需实测后补 ETA"**。本令把这两件补上，**不动 `.29` 正在跑的 80B decay**。

**① 交付中文 HTML（零 GPU，先做）**
- 路径：`reports/report_pretrain_formal_v5_plan_zh.html`（自包含、与既有 `reports/*.html` 同风格）。
- 必须与 `PLAN_V5_STABLE_1.5T.md` **数字一致**（宁可少写，不能两处不一致）：S1 500B/23.2 天、S2 1T/46.5 天、合计 **69.7 天**、250 ckpt、2M/4M per-step → 8.0s/16.1s、LR 恒定 1e-3、**吞吐基准 249K（TP1/DP8/MBS2/seq4096/GBS1024/bf16）**、并显式注明"298.6K 是 Xmodel-2.5 80B decay，不可用作本模型基准"。
- 必须含 **长上下文章**（ABF vs YaRN、推理侧 1M PPL 53–56 无退化、训练侧必须真实长文档、seq 课程、1M 独立 ETA）与 **次序裁定：decay → 1M → SFT/RL 采纳**。
- 必须含 **风险表**（6 条）+ **前置条件表**。⚠️ `PLAN` 里写"HQ 预训练 1.415T、余量 1.82×"等数字，**必须能在 `DATA_LEDGER.md` 找到出处**，找不到就改成实测值或标 `[待核]`。

**② 启动 v5 数据前置实测（本令核心，纯 CPU）**
> 目的：把 R3 阻塞项变成**有数字的排期**。分工：**下载/分词由 data 线执行**（已同步下发 10-18② 令），你负责**给出 v5 侧的口径与验收**，避免两边算出两套数。

1. **换算基线（用实测而非估算）**：拿 `en_v1_4` 已下部分（43,520 parquet / 4.1T bytes）做**抽样分词测速**：抽 2–3 个 shard，`preprocess_data.py` 单进程测 **tokens/s（tok/s）** 与 **bytes→tokens 比例**（每字节多少 token）。以此推算：
   - 全量 6.75T bytes → **总 token 数**（现有台账写 ≈2.2T，需你验证是否成立）；
   - **500B token 需要多少 bytes / 多少 shard**；
   - 按实测 tok/s 与给定并发（4/8/16 三档）分别给出 **500B 的分词天数**。
2. **产出**：`run/PLAN_V5_DATA_PREREQ.md`，含：抽样原文、tok/s 实测、三档并发 ETA、**500B 最早可开工日期**、以及"若分词成为瓶颈，S1 是否可先用已分词部分起跑（如 100B）"的建议（只是建议，不擅自改配方）。
3. **与 data 线口径对齐**：同一组数字写进 `DATA_LEDGER.md`（你只提交 `PLAN_V5_DATA_PREREQ.md`，不改 data 的文件）。

**③ 纪律**
- 🚫 不动 `.29` 的 80B decay（不重启、不 kill、不抢卡）；🚫 不改 v5 配方/判据（要改先报批）。**（仅限本 v5 写作块；训练死亡见顶部 16:2x，必须 resume）**
- 🚫 分词只跑 `nice -19` 小并发抽样（2–3 shard），**不要**在 `.29` 上开全量分词（那是 data 线的活，且会拖慢训练 IO）。
- ✅ commit 前缀 `pretrain plan-v5:`；`MEMORY_PRETRAIN_2B.md` 加一行指针（≤32KB 自滚）。


> **用户令（2026-10-18）**：写《BaiZe 2.22B Mamba2-hybrid 正式训练计划 v5》，主要写 Stable 部分，使用 1.5T tok；warmup=2000 步；S1 每 batch 2M tok 共 500B；S2 每 batch 4M tok 共 1T；学习率 warmup 后恒定 1e-3；数据 S1 用 en_v1_4，S2 混入 20% code、1–2% math 和高质量预训练数据；每 2000 步存 ckpt，用 CS8 评测；估计训练时长。
> 🚫 **本轮只产出文档，不动 `.29` 在跑的训练**（80B decay 健康，见状态头），不占 GPU、不改 `baize_xmodel25_decay_v2.sh`。

**① 交付物（必须两个文件都出）**
1. `reports/report_pretrain_formal_v5_plan_zh.html` —— **中文自包含 HTML**（与既有 `reports/*.html` 同风格：`<table>` 数据表 + 结论框，无外链、无 JS 依赖）。
2. `run/PLAN_V5_STABLE_1.5T.md` —— 纯文本/Markdown 版本（便于 diff 与后续任务书引用）。

**② 用户给定参数 = 逐字植入（不得改名、不得改值）**

| # | 参数 | 值 |
|:--|:--|:--|
| 1 | warmup | **2000 步** |
| 2 | S1 每 batch token | **2M tok/step**，总量 **500B tok** |
| 3 | S2 每 batch token | **4M tok/step**，总量 **1T tok** |
| 4 | 学习率 | warmup 后**恒定 1e-3**（S1、S2 全程同一常数，不做 cosine/decay） |
| 5 | S1 数据 | **en_v1_4 单一来源（100%）** |
| 6 | S2 数据 | code **20%** + math **1–2%** + 高质量预训练数据（其余 S2 份额） |
| 7 | ckpt | **每 2000 步**保存 |
| 8 | 评测 | 每个 ckpt **CS8**（Common8，0-shot；口径见 §最佳实践，`CS8 Avg`） |
| 9 | 总量 | Stable 段 **1.5T tok** |
| 10 | 后续次序（用户追加） | **S2 → decay → 长上下文（ABF）拉到 1M → SFT/RL**（长上下文阶段单独算 ETA、单独成章，见 ④-bis） |

派生（必须自己算、把算式写进文档，不要只给结果）：
- S1 步数 = 500B / 2M = **250,000 步**；S2 步数 = 1T / 4M = **250,000 步**；合计 **500,000 步**（+2000 warmup）
- ckpt 数 = 500,000 / 2,000 = **250 个**（S1 125 + S2 125）
- S2 各源 token：code = 20%×1T = **200B**；math = 1%～2% → **10B～20B**；高质量预训练 = 其余 **780B～790B**
- tokens/param = 1.5T / 2.22B ≈ **676 tok/param**
- 每 2000 步的 token 量：S1 = 2M×2000 = **4B tok**、S2 = 4M×2000 = **8B tok** ⇒ 按 BaiZe 基准吞吐（249K tok/s）ckpt 间隔约 **4.5h（S1）/ 8.9h（S2）**

**③ 时长估算（硬性要求：给口径 + 三档情景，禁止只给一个数）**
- 🔴 **基准吞吐 = BaiZe 2.22B Mamba2-hybrid 实测 249K tok/s**，配置 **TP1·DP8·MBS2·seq 4096·GBS 1024·bf16**（来源：T3 / P-9.6–9.7「P-8 最优 = TP1·MBS2·bf16 = 249K tok/s」，见 `MEMORY_PRETRAIN_2B.md` 与 `ARCHIVE_OPERATOR_PRETRAIN.md`）。
  - ⚠️ **不要把 298.6K tok/s 当成本模型基准**：那是 **Xmodel-2.5 80B decay** 在 `.29` 的实测（seq 3712 / GBS 960），**模型与序列都不同**，只能当"同机上限"参考，不可混用。
  - 该基准下 1 step = 4096×1024 = **4.19M tok ⇒ 16.84 s/step**。
- 纯训练（按 249K）：S1 500B/249K = **557.8h**；S2 1T/249K = **1,115.6h**；合计 **1,673.4h ≈ 69.7 天**。
- **v5 的 2M/4M tok per step 与基准 4.19M 不同** ⇒ 必须按 token 数折算（假设吞吐与 batch 组合无关，写进文档）：
  - 2M tok/step（seq 4096 ⇒ GBS 488）⇒ **8.0 s/step**
  - 4M tok/step（seq 4096 ⇒ GBS 976）⇒ **16.1 s/step**
- **必须同时给出吞吐敏感性表**（用户会据此排期）：

| 吞吐 | 1.5T 纯训练 | 说明 |
|:--|:--|:--|
| 218K tok/s | **79.6 天** | P-9.1 同配置早测值（疑有争用，保守下界） |
| **249K tok/s（BaiZe 基准）** | **69.7 天** | T3/P-9.6–9.7：TP1·DP8·MBS2·seq4096·GBS1024·bf16 |
| 280K tok/s | 62.0 天 | 若 S1 纯 web 短样本、packing 更满 |
| 320K tok/s | 54.3 天 | 需 FP8 / 更优 kernel（T3 实测 FP8 在 TP1 s=0.915 未提速） |

- **必须给 FLOPs 交叉验证**：总 FLOPs = 6×N×T = 6×2.22e9×1.5e12 ≈ **2.0e22**；8×H100 bf16 dense 989 TFLOPS ⇒ 时长 = FLOPs/(8×989e12×MFU)。
  - **249K tok/s 反推 MFU ≈ 41.9%**（6·N·249K / (8×989T)）→ FLOPs 口径同 MFU 下 = **33.2 天**（与 69.7 天差 2.1×）。
  - MFU 30% → 97.4 天；MFU 37% → 79.0 天。
  - ⚠️ **两个口径差 2.1×，必须在文档里解释**：token 口径来自**真机实测吞吐**（含 SSM scan、通信、优化器、packing 填充与 dataloader），FLOPs 的 6ND 只算 dense matmul（Mamba2 的 scan/conv 不计入、且 2.22B 未含 embedding 以外的稀疏开销）。**结论以 token 吞吐口径（69.7 天）为准，FLOPs 仅作 sanity check**。
- **另给"含评测的真实日历时间"**：250 个 ckpt × CS8 评测（用既有 8 GPU 并行评测流程的处理时间；若未知，用 3–5 min/ckpt 的区间并标注为假设 ⇒ 12.5–20.8h）+ 启动/重启/故障余量 5% ⇒ 给出 **日历天数区间**（以 69.7 天为底 ⇒ **约 74–76 天**）。

**④-bis 🧵 长上下文能力注入（用户追加令 2026-10-18，必须单独成章）**

> **用户令**：写计划时考虑长上下文能力如何注入；之前比较过 **ABF vs YaRN，倾向 ABF**；次序为 **S2 之后先 decay → 长上下文拉到 1M → SFT/RL**。要求回答"这个次序怎么样"。

1. **注入方案 = ABF（不是 YaRN），且分两层写清**：
   - **推理侧（零训练）**：`rope_theta 1e4 → 1e6` + `max_position_embeddings 4096 → 1048576`（沿用 `baize_b1_longctx_extend.py` 的 B1 写法）。既有实测：**PPL 4K 83.24 → 128K 54.66 → 1M 55.42，全程 53–56 无退化**；机制解释必须写——**56 层里只有 4 层 full_attention 吃 RoPE，Mamba2 层无位置编码** ⇒ ABF 只需适配 4/56 层，这是 hybrid 相对 dense 的结构性优势。
   - **训练侧（真正"注入"）**：ABF 免训练只保 PPL，**不产生 needle/多跳检索能力**（B1 已证 passkey 0%，且明确"是模型能力问题不是 ctx 问题"）⇒ 1M 能力必须在**长上下文续训阶段**用真实长文档训练，不能只靠配置外推。
2. **ABF vs YaRN 对比表必须写全（含代价，不得只写优点）**：
   - ABF：**税 = PPL@4K +10.5%**（75.36→83.24），换来免训练到 1M；实现零依赖（改 config）。
   - YaRN：需 rope_scaling 参数（factor/original_max_pos/attn_factor），对只作用于 4 层的 hybrid 收益有限、且引入新的超参面；仓库既有结论是 **hybrid 应沿用 B1 的 ABF 写法，dense 才需 YaRN/rope_scaling**（`ARCHIVE_OPERATOR_PRETRAIN.md`）。
   - 结论：**v5 采用 ABF**；YaRN 仅作对照/兜底（若长上下文阶段发现 ABF 在 1M 的 attention 稀释问题严重，再评估 YaRN + 更长 RoPE 训练）。
3. **次序评估（正面回答"decay → 1M → SFT/RL 怎么样"）**：给出结论 + 理由 + 风险，逐条：
   - **decay 在 1M 之前**：✅ 合理——先让 Stable 段收敛（LR 从 1e-3 降下来），再进长上下文；否则恒定 1e-3 在 1M 长度上会破坏已学分布。
   - **1M 在 SFT/RL 之前**：✅ 合理——对齐阶段（SFT/RL）的样本要"装得进"上下文，长上下文能力必须先具备；顺序颠倒会逼 SFT 用短样本、再返工。**但要求写成"长上下文阶段也是预训练的一部分"，用 pretraining 数据（长文档/代码库/多文件仓库），不是 SFT 数据。**
   - **风险 1（必须给对策）**：1M 阶段吞吐会崩（attention 占比 ~77%，1M PPL 单次 172s，既有实测）⇒ 需给出 **seq 课程**（如 32K→128K→256K→512K→1M 阶梯）、每档 token 预算、以及"用 ABF 外推 + 只在 128K 做训练、1M 靠外推"的**降本方案**。
   - **风险 2**：decay 之后 LR 已降到低值，长上下文阶段 LR 若继续低位会学不动 ⇒ 建议该阶段**单独设 LR（小幅回升，需用户批准，不得擅改）**。
   - **风险 3**：SFT/RL 前必须做**长上下文能力门禁**（needle/RULER/长文档 QA），不达标不进 SFT。
4. **篇幅与产出**：在 v5 文档中**新增独立章节「长上下文注入（ABF）」**，含：注入时序图（文字版）、各阶段 seq/LR/token 预算表、ABF 配置表（含 key/value 级 diff）、能力评测矩阵、以及 **对"decay→1M→SFT/RL"次序的明确裁定（采纳/调整建议 + 理由）**。同时在计划里把这三段并入总时长估算（**1M 阶段单列 ETA，不与 1.5T Stable 混算**）。

**⑤ 必须在文档中正面回答的 4 个可行性问题（这是本计划的核心价值）**
1. **学习率 1e-3 恒定**：与历史对照（P-8 用 3e-3；decay run 用 1.67e-3→1e-5；R3 BO best 的 LR）——给出「1e-3 恒定」是否会**欠拟合/后期不收敛**的判断，并给出**监控判据**（每 2000 步 recorded loss 若在 S2 后半段仍单调不降 ⇒ 建议在 S2 末端加短 decay，需用户批准，**不得擅改**）。
2. **batch 从 2M 跳到 4M**：v5 的 per-step token 变了 ⇒ 必须给出 **seq/GBS 的等效组合**（保持 seq 4096、MBS 2 时：2M tok/step ⇒ **GBS 488**、4M tok/step ⇒ **GBS 976**；若改成 seq 4096/GBS 1024 则 4.19M tok/step，需说明是否接受），以及切换时**梯度累积步数**、**每 step 时间**（8.0s → 16.1s@249K）、**S1 末 vs S2 初的 loss 断点**记录方式。
3. **数据量核对**：S1 需要 **500B tok** en_v1_4 ⇒ 按 2.2T tok 全量 ≈ 23%；但**当前 en_v1_4 只下完 85/110 shard（≈4.1T bytes）且尚未分词** ⇒ 500B 可行性取决于「剩余 25 shard 续传（`.23+hf-mirror` 已实测 200）+ 分词吞吐」。给出**前置条件表**：需要多少 TB、分词多少 B tok/天、按现速多少天。
4. **S2 混料供给**：code 需 200B，而 UltraData-Code 全量 ≈411B（够）；math 需 10–20B，UltraData-Math ≈303B（够）；高质量预训练（780–790B）从 `ultraweb_en`(≈1T tok) + `l1_en_hq`(152B) + `zh`(112B) + `UltraX`(31B) 取。**逐项写"需求 vs 可用 vs 余量倍数"，并标出哪个是瓶颈**（以 `DATA_LEDGER.md` 为唯一数据源，🚫 凭印象编造 token 数）。

**⑥ 文档结构（必须齐全）**
0. 一页结论（总量/时长/风险/所需前置；**含"decay→1M→SFT/RL"次序是否采纳的一句话裁定**）
1. 模型与并行配置（2.22B Mamba2-hybrid；TP/PP/DP、MBS、seq、GBS、bf16、compile）
2. 两阶段配方表（S1/S2 的 tokens/step、总 token、步数、LR、数据配比）
3. 数据配比与来源（逐项 token 需求/库存/余量）
4. 时长估算（基准 + 敏感性 + FLOPs 校验 + 日历时间）
5. ckpt 与评测（每 2000 步、CS8 口径、250 次评测的调度与耗时）
6. **长上下文注入（ABF）**：ABF vs YaRN 对比（含 +10.5% PPL 税）、推理侧配置 diff、训练侧 seq 课程与 token 预算、1M 阶段独立 ETA、能力门禁（见 ④-bis）
7. **风险与待拍板项**（至少含：LR 恒定、2M→4M 跳变、en_v1_4 未分词、250 个 ckpt 的存储/评测开销、**单机连续 70 天的故障恢复**、1M 阶段吞吐塌陷与长上下文阶段 LR）
8. 里程碑表（按周：第 N 周应到 S1/S2 的哪个 checkpoint、期望 CS8 区间；以 249K 基准推算，S1 需 **23.2 天**、S2 再需 **46.5 天**；之后单列 decay / 1M / SFT-RL 的里程碑）

**⑦ 写作纪律**
- 🚫 数字必须可追溯：每个 token 数/吞吐/时长后面括号注来源（**BaiZe 吞吐引 T3/P-9.6–9.7 的 249K**；数据引 `DATA_LEDGER.md`；算式自带）。**禁止把 Xmodel-2.5 的 298.6K tok/s 当作本模型基准**（那是 80B decay 在 `.29` 的实测，模型/seq 都不同，只能作同机上限参考）。
- 🚫 不把"计划"写成"已完成"；未验证的假设（如 CS8 评测 3–5 min/ckpt）要**标 `[假设]`**。
- ✅ commit 前缀 `pretrain plan-v5:`；写完在 `MEMORY_PRETRAIN_2B.md` 顶部加一行指针（体积 ≤32KB，超了自滚）。
- ✅ 本令**不改变**正在跑的 80B decay v2（🚫 不重启、不 kill）；两者独立。**（仅限本计划块；训练死亡见顶部 16:2x，必须 resume）**


---

## [归档 2026-10-19 08:3x] §🗣️ 运维问答 · 2026-10-09（补测对比报告 · 先报后跑门控）
> 从 MEMORY_PRETRAIN_2B.md 原文搬迁（原 lines 39-145），未改一字。归档原因：P-9.11 baize-vs-dense 公平对比方案「等运维确认后执行」，未获确认即被 80B decay v2 训练方向取代，属「已作废的运维指令块」（体积维护规程 ①）。MEMORY 体积维护：31.5KB → 降。

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


---

## [ARCHIVED 2026-10-22 #715] Pre-closed operator instruction blocks from BAIZE_PRETRAIN_2B_TASK.md

### 📄 运维指令 · 2026-10-21 09:3x（**写两份中文 HTML 报告**）· 用户直令 · 最高优先

> 用户原话：「请 pretrain 写两个中文 html 报告：1.昨天完成的 decay 实验结果；2.昨晚开启的短途 decay 实验设置和进展。」

**报告一：`reports/report_pretrain_decay_v2_result_zh.html`（decay v2 实验结果 · 已完成）**
- 实验设置：起点 step_532000（~1.41T tok）· 71.2B tok decay（19,980 步）· 配比 SFT 64% : L3 24% : code 8% : math 4%。
- 训练过程：起训 → 10-20 02:45 crash@step19920（NCCL timeout rank6）→ resume step_18000 → 10-20 10:30 收尾 step 19979/19980。
- **评测结果（核心）**：CS8 **44.97%** / CX6 **6.21%** vs Xmodel-2.5 官方 CS8 65.40% / CX6 32.90%（Δ **−20.43 / −26.69 pp**）；起点基线 CS8 **61.03%** ⇒ 判定 **decay 段训坏模型**。
- 归因（引用 #648/#649 已交付结论）：双移位 bug（py:547-548 预移位 + py:567-568 chunked-CE 再移位）、peak LR 1.67e-3 过高、code 26 epochs 过采样、step0 loss 11.72 异常。

**报告二：`reports/report_pretrain_decay_short_experiment_zh.html`（短途 decay 实验设置 · 进展）**
- 实验设计（10-21 02:3x 令）：20B token 小规模 decay，三变体 —— **L1** 修双移位 + LR 5e-4 + warmup 100；**L2** 只修双移位（LR 保持 1.67e-3）；**L3** 只降 LR（不动双移位）；判定门槛 **CS8 ≥55%**；每变体只评 CS8（~20min）。
- 当前进展：起点基线 CS8=61.03% 已测；**L1 训练中** step 1560/5611（27.8%）、loss≈0.90（step0=1.75 vs v2 起步 11.72 ⇒ 双移位修复确效）、~12s/step、ETA 10-21 ~23:50；L2/L3 待 L1 完成后串行。
- 后续计划：L1 训完 → CS8 eval(~20min) → ≥55% 起 L2 → L3 → 2×2 因子分析定主因。

**纪律**：两份均自包含中文 HTML（内联样式、无外链、无脚本）；所有数字可溯源（`eval_summary.txt` / 任务书对照表 / 各 task log `文件:行`）；commit 前缀 `pretrain report:`；🚫 不改 v2 原始产物与既有报告（v2 是失败证据留档）。两个报告 + EXPERIMENTS_PRETRAIN_2B 对应章节一起提交。

### 🟢 运维指令 · 2026-10-21 02:3x（**授权自主排查根因：不要再等批准，自己设计并跑实验**）· 用户直令 · 最高优先

> 用户原话：「可以，自行想办法排查根因。甚至可以用更少量的数据去 decay，比如像 Xmodel-2 一样，用 20B 数据 decay 看看效果。也可以在 decay 前少量 warmup 比如 100 步。总之要自己排查一下，为什么出现这种问题，不要干等着。」
> **授权变更**：解除上一轮「不重训 / 等批准」限制。**你有权自主设计并启动实验**（含训练），但必须按下述顺序推进、每步留证、不与 vision 抢 `.12`。

**① 先跑基线（第一优先，1h 内必须启动）**
- `.29` 已空 8h+，先跑 **step_532000 起点 14 集基线**（ckpt 已确认在盘 `xmodel25_history/step_532000/pytorch_model.bin` 2.7GB）。
- 判据：起点 ~60%+ ⇒ decay **训坏了**；起点 ~45% ⇒ 问题在**起点/加载**，与 decay 无关。**这个数字决定后续所有实验方向，不跑就是盲试。**

**② 已有归因结论（#648/#649 已交付，直接拿来设计实验，不要重复取证）**
| 排序 | 根因 | 证据 | 验证方式 |
|:--|:--|:--|:--|
| 1 | 🔴 **双移位 bug** | py:547-548 预移位 + py:567-568 chunked CE 再移位，注释自认 "HF model double-shifts. Replicate here" | **短程 A/B**：修掉预移位（只让 forward 移位一次）vs 现状，各跑 2B token，比 loss 与 CS8 |
| 2 | 🔴 **peak LR 1.67e-3 过高** | stable 末 LR 通常 1e-4~3e-4，decay 重新 warmup 到 6~17× | **LR 扫描**：1.67e-3 / 5e-4 / 3e-4 / 1e-4，各 2~5B token |
| 3 | 🟠 **code 26 epochs 过采样** | code 实测 0.270B 却训 6.98B | **降 code 配比**或补数据，各 2B token |
| 4 | 🟡 step0 loss=11.72 异常 | compile + 双移位 + 分布突变叠加 | 见 ②-a |
| 5 | ⏸ 基线缺失 | — | 见 ① |

**②-a 用户点名的两个方向（都要试）**
- **warmup 100 步**：你提的 warmup 100 步现已生效（`.sh` WARMUP=100），但需确认：是**从 stable 末 LR 开始线性升到 peak** 还是**冷启动式升到 1.67e-3**。若是后者 ⇒ warmup 100 步反而制造了 step0 惩罚，应改成 **peak = stable 末 LR 的 0.1~0.3 倍**，warmup 只是过渡。
- **20B 小规模 decay（对齐 Xmodel-2 的做法）**：这是**最高性价比的验证手段**——20B token ≈ 5,600 步（20B/(960×3712)），8 卡约 **3~3.5h** 一轮。用 20B 能跑 **2~3 个变体**而不必赌 71.2B。

**③ 实验设计建议（你有权调整，但需在 MEMORY 写明理由）**
```
实验 L1（先行，最便宜）：20B decay，修双移位 + LR 5e-4 + warmup 100 → 与 71.2B v2 同基线比 CS8
实验 L2：20B decay，只修双移位（LR 保持 1.67e-3）→ 隔离"双移位 vs LR"两个主因的贡献
实验 L3：20B decay，只降 LR（不动双移位）→ 同上，互为对照
（可选）L4：20B decay，修双移位 + LR 5e-4 + code 配比降到 4%
```
- 每个变体跑完只评 **CS8（8 集，~20min）** 快速判，不必等 CX6。
- **判定门槛**：任一变体 CS8 **≥ 55%** 即说明方向对了（Xmodel-2.5 final 是 65.40%，起点基线待测）。

**④ 纪律**
- 🚫 **不抢 `.12`**（vision ArmD-R2 跑到 10-21 08:45），只用 `.29` 8 卡。
- ✅ 每轮必须落 MEMORY + daily（step / loss / CS8 / 结论），**禁止静默**。
- ✅ 实验必须**可复现**：脚本、config、seed 全部落盘并 commit。
- 🚫 不改 v2 原始产物与报告（v2 是失败证据，留档）。
- ⏭ 跑到 5 个实验也没关系，**先出"哪个变体有效"的结论**，不必立刻重跑 71.2B。

**⑤ 回报格式**：每轮写「实验编号 / 配置差异 / 已训 token / loss / CS8 / 当前最优变体」。

### 🔴 运维指令 · 2026-10-20 21:5x（**decay v2 对照口径纠错 + 差 20pp 归因调查**）· 用户直令 · 已闭环

> 用户原话：「这个结果应该跟 Xmodel-2.5 final 的结果比啊，毕竟是基于 Xmodel-2.5 stable 最后的检查点，相同的方式 decay 了 71.2B 同样的数据量，数据配比也相似。」
> **我方承认错误**：14:2x 评测令里给的「对比基准 = P-8 / Xmodel-2.5 step_6000」是**错的对照**，据此产出的报告结论（"更多 tokens 未带来提升"）**不成立**，必须推翻重做。

**① 正确的对照口径（铁定，后续报告不得再用 P-8 作主对照）**

| 维度 | Xmodel-2.5 官方 | BaiZe decay v2 | 是否可比 |
|:--|:--|:--|:--|
| 起点 | stable 末 ckpt step 532000（~1.41T tok） | **同** | ✅ |
| decay token | 71.2B（20k 步 × 3.56M） | **71.2B**（19,980 步 × 960 × 3,712） | ✅ 同量 |
| 配比 | 66.9% SFT + 其余 | SFT 64% : L3 24% : code 8% : math 4% | ≈ 相似 |
| 优化器 | decay 段 AdamW→Muon | Muon | ✅ |
| **CS8** | **65.40%** | **44.97%** | **Δ -20.43pp** |
| **CX6** | **32.90%** | **6.21%** | **Δ -26.69pp** |

⇒ 这是一个**近似单变量**的公平对照，差值 20pp 属于「decay 段没练出来」，不是"略差"。

**② 必须回答的问题（按序，全部只读取证）**
1. final ckpt 是否真的是 71.2B 训练后的产物（config / 训练日志首尾 step / blend 行 / loss 起点是否接得住 stable 末点）？
2. **起点 step_532000 的 14 集基线是多少**？—— 若它本身就 ~60%+，则 decay 把模型**训坏了**；若它也只 ~45%，则问题在起点/加载而非 decay 配方。**这是判定失败环节的唯一关键实验**。
3. decay 段 code/math 实际可用 token 与 epoch（计划书曾标 code epoch 23.7 / math 5.25，属严重过采样或不足）—— 实测 `.bin` 字节数。
4. LR 1.67e-3（从 1.4T 末点起）是否过高、warmup 100 步是否过短。

**③ 交付**
- 先交**取证实测**（不写报告），约 20 分钟量；取证齐全后再改报告。
- 报告 `report_pretrain_decay_v2_final_eval_zh.html` 重做：Xmodel-2.5 final 提为**唯一主对照**、改正 `~80B`→`71.2B`、加「失败归因」节；P-8 只作旁注（架构/参数量不同，不可当归因依据）。
- commit 前缀 `pretrain eval:`；结论同步 MEMORY + 日报。

**纪律**：🚫 不重训、不改配方、不重启任何训练；🚫 不跑 vision/data/harness 线；本轮**只读取证 + 结论**。若需跑 stable 基线 eval（`baize_xmodel_eval.sh`）等用户批准后再动。

### 🧪 运维指令 · 2026-10-20 14:2x（**评测 decay v2 final 模型 · 14 集 lm-eval**）· 用户直令 · 最高优先

> 用户令：「下发评测指令」（训练已完成，final 模型应跑下游评测）。
> **目标**：对 Xmodel-2.5 decay v2 的 **final ckpt** 跑 14 集评测，与 P-8 / Xmodel-2.5 历史 ckpt 对比。

**① 评测对象（已就绪，勿重复转换）**
- HF 模型目录：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/final/`
  （`model.safetensors` 2.7GB + `config.json` + `modeling_xmodel2.py` + `configuration_xmodel2.py` + tokenizer 全套；architectures=`XmodelForCausalLM`，需 `trust_remote_code=True`）。
- 起评前先**单题烟测**：确认 auto_map 命中建模代码、logits 可产出（0 nan）。

**② 评测方式**
- 复用 `run/baize_xmodel_eval.sh`（专为 Xmodel 历史 ckpt 设计，14 集 = CS8 zero-shot + CX6 默认 n-shot，`trust_remote_code=True`）：
  ```bash
  bash run/baize_xmodel_eval.sh \
    /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/final \
    <输出目录> decay_v2_final 0,1,2,3,4,5,6,7
  ```
- **在 `.29` 跑**（8×H100 已空；vision 在 `.12`，勿占）。评测环境 = `py310`（脚本内置）；数据集走 `HF_DATASETS_CACHE=/nas_train/app.e0031982/hf_cache`，`hf-mirror`/proxy 已在脚本内兜底。
- 集数：CS8 = hellaswag/arc_easy/boolq/arc_challenge/sciq/piqa/winogrande/openbookqa（0-shot）；CX6 = gsm8k(5)/hendrycks_math500(4)/mmlu(5)/bbh_zeroshot(0)/humaneval(0)/mbpp(3)。**与 P-8 完全同口径**。

**③ 结果与报告**
- 收集后产出 **CS8 均值 + CX6 均值**（collect 已内置脚本）。
- 对比基准：**P-8 = CS8 49.21% / CX 6.81%**；Xmodel-2/2.5 s1 历史 ckpt（若史上有值也并列）。
- 交付：中文报告 `reports/report_pretrain_decay_v2_final_eval_zh.html` + 更新 `EXPERIMENTS_PRETRAIN_2B.md`（decay v2 final 一节）；commit 前缀 `pretrain eval:`。

**纪律**：🚫 不碰 vision/data/harness 线与 `.12` 进程；🚫 只评测不训练；评测完释放 `.29` 8 卡；报告数字可溯源到 `eval_summary.txt`/各 task log `文件:行`。

### 📄 运维指令 · 2026-10-20 06:1x（**事故复盘报告已由运维编写 → 你去核实数据 + 落地 P0 两项**）· 用户直令

> 用户令：「先让 pretrain 写个中文 html 报告 复盘昨夜发生的问题和解法建议」
> **报告已由运维全部写完并入库**：`reports/report_pretrain_crash_20261020_zh.html`（15KB，自包含单文件，无外链/无脚本）。
> **你不需要重写报告**，只需做下面 3 件事：

**① 核实报告中的事实（与你手里的 log/进程对账）**
逐条核对并在 `daily-memories/2026-10-20.md` 写出「核对结论」：
- 崩溃时刻 **02:45:25**、错误 `NCCL collective timeout (rank6) → SIGABRT`、最后 step **19,920/19,980**
- resume 起点 **step_18000（10-19 20:21）**、损失 **1,920 步 ≈ 6.4h**
- 无人处理窗口 **02:45→04:00 = 75 分钟**
- resume 后 **~12s/step、8×GPU 96-100%、0 error**（与崩溃前一致，无降频）
- **代码事实**：`baize_xmodel25_decay_v2.py` 的 `dist.init_process_group(backend='nccl')` **无 timeout 参数**；`.sh` 中 `NCCL_*` / `TORCH_NCCL_*` **0 处**
- **SAVE_INTERVAL**：脚本现值 500（原 2000）
> 若任一项与你的证据不符 → **以你的实测为准**，在 daily 里写明差异 + 证据，并回报运维（报告可修正）。

**② 落地 P0 两项（不碰运行中进程，全部为增量）**
- **P0-a `TORCH_NCCL_DUMP_ON_TIMEOUT`**：**只写进脚本文件供下次 resume 生效**，🚫 **不要为此重启当前 run**（当前 92%+，重启代价远大于收益）。即：在 `.sh` 的 env 段追加
  ```bash
  export TORCH_NCCL_DUMP_ON_TIMEOUT=1
  export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
  export NCCL_ASYNC_ERROR_HANDLING=1
  ```
  并**在下次 resume 日志里确认这些变量生效**（`tr '\0' '\n' < /proc/<pid>/environ | grep NCCL`）。
- **P0-b 崩溃自动重启 watchdog**：新建 `run/baize_decay_watchdog.sh`（**新文件，不改现有脚本**），要求：
  - 每 **5 分钟** 检查 `pgrep -f 'xmodel25_decay_v2'`；
  - 进程消失 且 最近 step < ITERS 且 **24h 内崩溃 < 3 次** ⇒ 自动 `RESUME_DIR=<最新完好 ckpt> setsid bash baize_xmodel25_decay_v2.sh`；
  - **防死循环**：崩溃计数落文件（如 `/tmp/decay_watchdog.crashcnt`），24h ≥3 次则**停止自动重启并写 blocker**；
  - **判活必须用 `strings /tmp/baize_xmodel25_decay_v2_train.log | grep '^\[step'`**（该 log 是 sparse file，`tail` 不可靠）；
  - 🚫 **当前 run 未结束时先不要启动该 watchdog**，或启动时加 `--dry-run` 只记录不动作（避免与人工 resume 冲突）。

**③ 回填 P2 数据（硬件是否永久故障）**
在**训练收尾后**（预计 ~10:30）执行一次只读硬件检查，结论补进报告 §3 与 `MEMORY_PRETRAIN_2B.md`：
```bash
nvidia-smi -q | grep -iE 'Xid|ECC|Remapped|Retired'
nvidia-smi --query-gpu=index,temperature.gpu,clocks_throttle_reasons.active --format=csv
dmesg -T 2>/dev/null | grep -iE 'xid|nvrm|fallen off' | tail -20
```
> 判据：无 Xid 且可纠正 ECC=0 ⇒ 瞬时；有 Xid / ECC 增长 ⇒ 该卡有隐患，报 blocker 建议巡检。

**纪律**：🚫 不重启当前训练（92%+，稳中）· 🚫 不改 ITERS/LR/数据 · 🚫 不动 `.12` 的 vision ArmD · 报告文件**不要改**（如需修正请写差异给运维）。commit 前缀 `pretrain report:`。

### 🆕 运维指令 · 2026-10-18 16:4x（✅ 更正：#548 是误判，训练未死——**不要重启**）· 运维 sudo 实测

> **实测**：`.29` **PID 2597555 从 10-17 08:44 一直存活**（etimes ~115000s）；GPU **8×100%/51763 MiB**；`/tmp/baize_xmodel25_decay_v2_train.log` 当前 **step 9630/19980（48.2%）**，loss 1.3255，lr 1.61e-4，298.8K tok/s，**0 error**。
> **#548 误判根因**：它读的 `$OUTPUT_DIR/baize_xmodel25_decay_v2_train.log` 是 **`.12` 旧 run** 的日志（10-17 10:45 SIGTERM traceback），不是 `.29` 的实时日志。
> **判活规则（立即生效）**：先 `pgrep -af torchrun` + `nvidia-smi` + **`tail /tmp/baize_xmodel25_decay_v2_train.log` 看 step 是否增长**；**NFS `$OUTPUT_DIR/...train.log` 不能作为判据**（那是 `.12` 旧日志）。
> **本块覆盖 16:2x 的“立即 resume”**：训练活着 ⇒ **不要重启/不要 resume**。只有确认 `torchrun` 消失 + GPU 空闲 + `/tmp` log 停止增长，才按 16:2x 的长期规则 resume。

### 🆕 运维指令 · 2026-10-18 16:2x（🚨 P0：立即 resume 80B decay v2 + **长期授权：训练挂了自行重启，不再等许可**）· 用户直令 · 最高优先

> 用户令（2026-10-18）：「pretrain：重启 resume 训练，以后这种事不需要运维许可，自己的训练挂了，唤醒时看到了立刻修。」
> 现状：#548 已确认 **15:53:22 step 9400 后训练死亡**（GPU 全空、无 torchrun、日志无错）；最新 ckpt = **step_8000**（11:15）；step 8001–9400 将丢。**本轮直接 resume，不要等许可。**

**① 立即 resume（本轮唤醒）**
1. 确认 `nvidia-smi` 8 卡空、无 `torchrun`；确认 ckpt：
   ```bash
   ls -l /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/step_8000/model.safetensors
   ```
   若 `step_8000` 缺失，选最新的 `step_*`（必须含 `model.safetensors`）。
2. 给 `run/baize_xmodel25_decay_v2.sh` 加可选 resume（或直接改 torchrun 参数）：
   ```bash
   RESUME_DIR="${RESUME_DIR:-}"
   RESUME_ARG=""
   [ -n "$RESUME_DIR" ] && RESUME_ARG="--resume $RESUME_DIR"
   # 在 baize_xmodel25_decay_v2.py 参数末尾加 $RESUME_ARG
   ```
   启动：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
   RESUME_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/step_8000 \
     setsid bash baize_xmodel25_decay_v2.sh > /tmp/baize_xmodel25_decay_v2_resume.log 2>&1 < /dev/null &
   ```
   `--resume` 会从 step_8000 续跑（LR schedule 按 8000 起算；optimizer 状态不恢复，属已知小 transient）。脚本内部日志仍写 `$OUTPUT_DIR/baize_xmodel25_decay_v2_train.log`。
3. 判据：torchrun PID + 8 workers；8 卡 100%；train_log 从 **step 8001** 继续增长、无 error/traceback/OOM/CUDA；`--resume` 打印 `start_step=8000`。
4. 记录：MEMORY + daily + commit `pretrain resume:`。

**② 长期规则（立即生效，覆盖旧的「等运维许可」）**
> ⚠️ **作用域**：旧块（12:0x / 10-18② / 其它）里的「不重启 / 不碰训练 / 等运维裁定」只适用于各自任务；**训练已死时一律按本块 resume**。

- 以后唤醒先查训练：`pgrep -af torchrun`、`nvidia-smi`、train_log 尾部。
- **训练进程消失 / 崩溃 / 被杀** ⇒ 自查日志 → 选最新有效 `step_*` ckpt → **立即 `--resume` 重启**，不需要逐次等运维许可。
- 仅以下情况停手报 blocker：① 没有任何有效 ckpt；② 同一原因 1h 内连续崩 ≥2 次；③ 硬件/磁盘/网络错误明确；④ 重启命令本身失败。
- 仍禁止：kill 健康训练、改配方/数据、动别的线。

> 📦 §2026-10-18 12:0x（P0 修复 .29 ops 中继）+ 2026-10-18②（v5 中文 HTML + 数据前置实测）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：中继已修复闭环（PID1972249 存活、.last_run_id 123→125）；v5 三交付物（HTML+PLAN_V5_STABLE_1.5T.md+PLAN_V5_DATA_PREREQ.md）均 committed，分词实测 474K/375K tok/s·0.343 tok/B·2.31T·16并发≈1天·开工~10-20。需要时再读。



---

## [ARCHIVED 2026-10-22 #715] Pre-closed operator instruction blocks from BAIZE_PRETRAIN_2B_TASK.md

### 📄 运维指令 · 2026-10-21 09:3x（**写两份中文 HTML 报告**）· 用户直令 · 最高优先

> 用户原话：「请 pretrain 写两个中文 html 报告：1.昨天完成的 decay 实验结果；2.昨晚开启的短途 decay 实验设置和进展。」

**报告一：`reports/report_pretrain_decay_v2_result_zh.html`（decay v2 实验结果 · 已完成）**
- 实验设置：起点 step_532000（~1.41T tok）· 71.2B tok decay（19,980 步）· 配比 SFT 64% : L3 24% : code 8% : math 4%。
- 训练过程：起训 → 10-20 02:45 crash@step19920（NCCL timeout rank6）→ resume step_18000 → 10-20 10:30 收尾 step 19979/19980。
- **评测结果（核心）**：CS8 **44.97%** / CX6 **6.21%** vs Xmodel-2.5 官方 CS8 65.40% / CX6 32.90%（Δ **−20.43 / −26.69 pp**）；起点基线 CS8 **61.03%** ⇒ 判定 **decay 段训坏模型**。
- 归因（引用 #648/#649 已交付结论）：双移位 bug（py:547-548 预移位 + py:567-568 chunked-CE 再移位）、peak LR 1.67e-3 过高、code 26 epochs 过采样、step0 loss 11.72 异常。

**报告二：`reports/report_pretrain_decay_short_experiment_zh.html`（短途 decay 实验设置 · 进展）**
- 实验设计（10-21 02:3x 令）：20B token 小规模 decay，三变体 —— **L1** 修双移位 + LR 5e-4 + warmup 100；**L2** 只修双移位（LR 保持 1.67e-3）；**L3** 只降 LR（不动双移位）；判定门槛 **CS8 ≥55%**；每变体只评 CS8（~20min）。
- 当前进展：起点基线 CS8=61.03% 已测；**L1 训练中** step 1560/5611（27.8%）、loss≈0.90（step0=1.75 vs v2 起步 11.72 ⇒ 双移位修复确效）、~12s/step、ETA 10-21 ~23:50；L2/L3 待 L1 完成后串行。
- 后续计划：L1 训完 → CS8 eval(~20min) → ≥55% 起 L2 → L3 → 2×2 因子分析定主因。

**纪律**：两份均自包含中文 HTML（内联样式、无外链、无脚本）；所有数字可溯源（`eval_summary.txt` / 任务书对照表 / 各 task log `文件:行`）；commit 前缀 `pretrain report:`；🚫 不改 v2 原始产物与既有报告（v2 是失败证据留档）。两个报告 + EXPERIMENTS_PRETRAIN_2B 对应章节一起提交。

### 🟢 运维指令 · 2026-10-21 02:3x（**授权自主排查根因：不要再等批准，自己设计并跑实验**）· 用户直令 · 最高优先

> 用户原话：「可以，自行想办法排查根因。甚至可以用更少量的数据去 decay，比如像 Xmodel-2 一样，用 20B 数据 decay 看看效果。也可以在 decay 前少量 warmup 比如 100 步。总之要自己排查一下，为什么出现这种问题，不要干等着。」
> **授权变更**：解除上一轮「不重训 / 等批准」限制。**你有权自主设计并启动实验**（含训练），但必须按下述顺序推进、每步留证、不与 vision 抢 `.12`。

**① 先跑基线（第一优先，1h 内必须启动）**
- `.29` 已空 8h+，先跑 **step_532000 起点 14 集基线**（ckpt 已确认在盘 `xmodel25_history/step_532000/pytorch_model.bin` 2.7GB）。
- 判据：起点 ~60%+ ⇒ decay **训坏了**；起点 ~45% ⇒ 问题在**起点/加载**，与 decay 无关。**这个数字决定后续所有实验方向，不跑就是盲试。**

**② 已有归因结论（#648/#649 已交付，直接拿来设计实验，不要重复取证）**
| 排序 | 根因 | 证据 | 验证方式 |
|:--|:--|:--|:--|
| 1 | 🔴 **双移位 bug** | py:547-548 预移位 + py:567-568 chunked CE 再移位，注释自认 "HF model double-shifts. Replicate here" | **短程 A/B**：修掉预移位（只让 forward 移位一次）vs 现状，各跑 2B token，比 loss 与 CS8 |
| 2 | 🔴 **peak LR 1.67e-3 过高** | stable 末 LR 通常 1e-4~3e-4，decay 重新 warmup 到 6~17× | **LR 扫描**：1.67e-3 / 5e-4 / 3e-4 / 1e-4，各 2~5B token |
| 3 | 🟠 **code 26 epochs 过采样** | code 实测 0.270B 却训 6.98B | **降 code 配比**或补数据，各 2B token |
| 4 | 🟡 step0 loss=11.72 异常 | compile + 双移位 + 分布突变叠加 | 见 ②-a |
| 5 | ⏸ 基线缺失 | — | 见 ① |

**②-a 用户点名的两个方向（都要试）**
- **warmup 100 步**：你提的 warmup 100 步现已生效（`.sh` WARMUP=100），但需确认：是**从 stable 末 LR 开始线性升到 peak** 还是**冷启动式升到 1.67e-3**。若是后者 ⇒ warmup 100 步反而制造了 step0 惩罚，应改成 **peak = stable 末 LR 的 0.1~0.3 倍**，warmup 只是过渡。
- **20B 小规模 decay（对齐 Xmodel-2 的做法）**：这是**最高性价比的验证手段**——20B token ≈ 5,600 步（20B/(960×3712)），8 卡约 **3~3.5h** 一轮。用 20B 能跑 **2~3 个变体**而不必赌 71.2B。

**③ 实验设计建议（你有权调整，但需在 MEMORY 写明理由）**
```
实验 L1（先行，最便宜）：20B decay，修双移位 + LR 5e-4 + warmup 100 → 与 71.2B v2 同基线比 CS8
实验 L2：20B decay，只修双移位（LR 保持 1.67e-3）→ 隔离"双移位 vs LR"两个主因的贡献
实验 L3：20B decay，只降 LR（不动双移位）→ 同上，互为对照
（可选）L4：20B decay，修双移位 + LR 5e-4 + code 配比降到 4%
```
- 每个变体跑完只评 **CS8（8 集，~20min）** 快速判，不必等 CX6。
- **判定门槛**：任一变体 CS8 **≥ 55%** 即说明方向对了（Xmodel-2.5 final 是 65.40%，起点基线待测）。

**④ 纪律**
- 🚫 **不抢 `.12`**（vision ArmD-R2 跑到 10-21 08:45），只用 `.29` 8 卡。
- ✅ 每轮必须落 MEMORY + daily（step / loss / CS8 / 结论），**禁止静默**。
- ✅ 实验必须**可复现**：脚本、config、seed 全部落盘并 commit。
- 🚫 不改 v2 原始产物与报告（v2 是失败证据，留档）。
- ⏭ 跑到 5 个实验也没关系，**先出"哪个变体有效"的结论**，不必立刻重跑 71.2B。

**⑤ 回报格式**：每轮写「实验编号 / 配置差异 / 已训 token / loss / CS8 / 当前最优变体」。

### 🔴 运维指令 · 2026-10-20 21:5x（**decay v2 对照口径纠错 + 差 20pp 归因调查**）· 用户直令 · 已闭环

> 用户原话：「这个结果应该跟 Xmodel-2.5 final 的结果比啊，毕竟是基于 Xmodel-2.5 stable 最后的检查点，相同的方式 decay 了 71.2B 同样的数据量，数据配比也相似。」
> **我方承认错误**：14:2x 评测令里给的「对比基准 = P-8 / Xmodel-2.5 step_6000」是**错的对照**，据此产出的报告结论（"更多 tokens 未带来提升"）**不成立**，必须推翻重做。

**① 正确的对照口径（铁定，后续报告不得再用 P-8 作主对照）**

| 维度 | Xmodel-2.5 官方 | BaiZe decay v2 | 是否可比 |
|:--|:--|:--|:--|
| 起点 | stable 末 ckpt step 532000（~1.41T tok） | **同** | ✅ |
| decay token | 71.2B（20k 步 × 3.56M） | **71.2B**（19,980 步 × 960 × 3,712） | ✅ 同量 |
| 配比 | 66.9% SFT + 其余 | SFT 64% : L3 24% : code 8% : math 4% | ≈ 相似 |
| 优化器 | decay 段 AdamW→Muon | Muon | ✅ |
| **CS8** | **65.40%** | **44.97%** | **Δ -20.43pp** |
| **CX6** | **32.90%** | **6.21%** | **Δ -26.69pp** |

⇒ 这是一个**近似单变量**的公平对照，差值 20pp 属于「decay 段没练出来」，不是"略差"。

**② 必须回答的问题（按序，全部只读取证）**
1. final ckpt 是否真的是 71.2B 训练后的产物（config / 训练日志首尾 step / blend 行 / loss 起点是否接得住 stable 末点）？
2. **起点 step_532000 的 14 集基线是多少**？—— 若它本身就 ~60%+，则 decay 把模型**训坏了**；若它也只 ~45%，则问题在起点/加载而非 decay 配方。**这是判定失败环节的唯一关键实验**。
3. decay 段 code/math 实际可用 token 与 epoch（计划书曾标 code epoch 23.7 / math 5.25，属严重过采样或不足）—— 实测 `.bin` 字节数。
4. LR 1.67e-3（从 1.4T 末点起）是否过高、warmup 100 步是否过短。

**③ 交付**
- 先交**取证实测**（不写报告），约 20 分钟量；取证齐全后再改报告。
- 报告 `report_pretrain_decay_v2_final_eval_zh.html` 重做：Xmodel-2.5 final 提为**唯一主对照**、改正 `~80B`→`71.2B`、加「失败归因」节；P-8 只作旁注（架构/参数量不同，不可当归因依据）。
- commit 前缀 `pretrain eval:`；结论同步 MEMORY + 日报。

**纪律**：🚫 不重训、不改配方、不重启任何训练；🚫 不跑 vision/data/harness 线；本轮**只读取证 + 结论**。若需跑 stable 基线 eval（`baize_xmodel_eval.sh`）等用户批准后再动。

### 🧪 运维指令 · 2026-10-20 14:2x（**评测 decay v2 final 模型 · 14 集 lm-eval**）· 用户直令 · 最高优先

> 用户令：「下发评测指令」（训练已完成，final 模型应跑下游评测）。
> **目标**：对 Xmodel-2.5 decay v2 的 **final ckpt** 跑 14 集评测，与 P-8 / Xmodel-2.5 历史 ckpt 对比。

**① 评测对象（已就绪，勿重复转换）**
- HF 模型目录：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/final/`
  （`model.safetensors` 2.7GB + `config.json` + `modeling_xmodel2.py` + `configuration_xmodel2.py` + tokenizer 全套；architectures=`XmodelForCausalLM`，需 `trust_remote_code=True`）。
- 起评前先**单题烟测**：确认 auto_map 命中建模代码、logits 可产出（0 nan）。

**② 评测方式**
- 复用 `run/baize_xmodel_eval.sh`（专为 Xmodel 历史 ckpt 设计，14 集 = CS8 zero-shot + CX6 默认 n-shot，`trust_remote_code=True`）：
  ```bash
  bash run/baize_xmodel_eval.sh \
    /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/final \
    <输出目录> decay_v2_final 0,1,2,3,4,5,6,7
  ```
- **在 `.29` 跑**（8×H100 已空；vision 在 `.12`，勿占）。评测环境 = `py310`（脚本内置）；数据集走 `HF_DATASETS_CACHE=/nas_train/app.e0031982/hf_cache`，`hf-mirror`/proxy 已在脚本内兜底。
- 集数：CS8 = hellaswag/arc_easy/boolq/arc_challenge/sciq/piqa/winogrande/openbookqa（0-shot）；CX6 = gsm8k(5)/hendrycks_math500(4)/mmlu(5)/bbh_zeroshot(0)/humaneval(0)/mbpp(3)。**与 P-8 完全同口径**。

**③ 结果与报告**
- 收集后产出 **CS8 均值 + CX6 均值**（collect 已内置脚本）。
- 对比基准：**P-8 = CS8 49.21% / CX 6.81%**；Xmodel-2/2.5 s1 历史 ckpt（若史上有值也并列）。
- 交付：中文报告 `reports/report_pretrain_decay_v2_final_eval_zh.html` + 更新 `EXPERIMENTS_PRETRAIN_2B.md`（decay v2 final 一节）；commit 前缀 `pretrain eval:`。

**纪律**：🚫 不碰 vision/data/harness 线与 `.12` 进程；🚫 只评测不训练；评测完释放 `.29` 8 卡；报告数字可溯源到 `eval_summary.txt`/各 task log `文件:行`。

### 📄 运维指令 · 2026-10-20 06:1x（**事故复盘报告已由运维编写 → 你去核实数据 + 落地 P0 两项**）· 用户直令

> 用户令：「先让 pretrain 写个中文 html 报告 复盘昨夜发生的问题和解法建议」
> **报告已由运维全部写完并入库**：`reports/report_pretrain_crash_20261020_zh.html`（15KB，自包含单文件，无外链/无脚本）。
> **你不需要重写报告**，只需做下面 3 件事：

**① 核实报告中的事实（与你手里的 log/进程对账）**
逐条核对并在 `daily-memories/2026-10-20.md` 写出「核对结论」：
- 崩溃时刻 **02:45:25**、错误 `NCCL collective timeout (rank6) → SIGABRT`、最后 step **19,920/19,980**
- resume 起点 **step_18000（10-19 20:21）**、损失 **1,920 步 ≈ 6.4h**
- 无人处理窗口 **02:45→04:00 = 75 分钟**
- resume 后 **~12s/step、8×GPU 96-100%、0 error**（与崩溃前一致，无降频）
- **代码事实**：`baize_xmodel25_decay_v2.py` 的 `dist.init_process_group(backend='nccl')` **无 timeout 参数**；`.sh` 中 `NCCL_*` / `TORCH_NCCL_*` **0 处**
- **SAVE_INTERVAL**：脚本现值 500（原 2000）
> 若任一项与你的证据不符 → **以你的实测为准**，在 daily 里写明差异 + 证据，并回报运维（报告可修正）。

**② 落地 P0 两项（不碰运行中进程，全部为增量）**
- **P0-a `TORCH_NCCL_DUMP_ON_TIMEOUT`**：**只写进脚本文件供下次 resume 生效**，🚫 **不要为此重启当前 run**（当前 92%+，重启代价远大于收益）。即：在 `.sh` 的 env 段追加
  ```bash
  export TORCH_NCCL_DUMP_ON_TIMEOUT=1
  export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
  export NCCL_ASYNC_ERROR_HANDLING=1
  ```
  并**在下次 resume 日志里确认这些变量生效**（`tr '\0' '\n' < /proc/<pid>/environ | grep NCCL`）。
- **P0-b 崩溃自动重启 watchdog**：新建 `run/baize_decay_watchdog.sh`（**新文件，不改现有脚本**），要求：
  - 每 **5 分钟** 检查 `pgrep -f 'xmodel25_decay_v2'`；
  - 进程消失 且 最近 step < ITERS 且 **24h 内崩溃 < 3 次** ⇒ 自动 `RESUME_DIR=<最新完好 ckpt> setsid bash baize_xmodel25_decay_v2.sh`；
  - **防死循环**：崩溃计数落文件（如 `/tmp/decay_watchdog.crashcnt`），24h ≥3 次则**停止自动重启并写 blocker**；
  - **判活必须用 `strings /tmp/baize_xmodel25_decay_v2_train.log | grep '^\[step'`**（该 log 是 sparse file，`tail` 不可靠）；
  - 🚫 **当前 run 未结束时先不要启动该 watchdog**，或启动时加 `--dry-run` 只记录不动作（避免与人工 resume 冲突）。

**③ 回填 P2 数据（硬件是否永久故障）**
在**训练收尾后**（预计 ~10:30）执行一次只读硬件检查，结论补进报告 §3 与 `MEMORY_PRETRAIN_2B.md`：
```bash
nvidia-smi -q | grep -iE 'Xid|ECC|Remapped|Retired'
nvidia-smi --query-gpu=index,temperature.gpu,clocks_throttle_reasons.active --format=csv
dmesg -T 2>/dev/null | grep -iE 'xid|nvrm|fallen off' | tail -20
```
> 判据：无 Xid 且可纠正 ECC=0 ⇒ 瞬时；有 Xid / ECC 增长 ⇒ 该卡有隐患，报 blocker 建议巡检。

**纪律**：🚫 不重启当前训练（92%+，稳中）· 🚫 不改 ITERS/LR/数据 · 🚫 不动 `.12` 的 vision ArmD · 报告文件**不要改**（如需修正请写差异给运维）。commit 前缀 `pretrain report:`。

### 🆕 运维指令 · 2026-10-18 16:4x（✅ 更正：#548 是误判，训练未死——**不要重启**）· 运维 sudo 实测

> **实测**：`.29` **PID 2597555 从 10-17 08:44 一直存活**（etimes ~115000s）；GPU **8×100%/51763 MiB**；`/tmp/baize_xmodel25_decay_v2_train.log` 当前 **step 9630/19980（48.2%）**，loss 1.3255，lr 1.61e-4，298.8K tok/s，**0 error**。
> **#548 误判根因**：它读的 `$OUTPUT_DIR/baize_xmodel25_decay_v2_train.log` 是 **`.12` 旧 run** 的日志（10-17 10:45 SIGTERM traceback），不是 `.29` 的实时日志。
> **判活规则（立即生效）**：先 `pgrep -af torchrun` + `nvidia-smi` + **`tail /tmp/baize_xmodel25_decay_v2_train.log` 看 step 是否增长**；**NFS `$OUTPUT_DIR/...train.log` 不能作为判据**（那是 `.12` 旧日志）。
> **本块覆盖 16:2x 的“立即 resume”**：训练活着 ⇒ **不要重启/不要 resume**。只有确认 `torchrun` 消失 + GPU 空闲 + `/tmp` log 停止增长，才按 16:2x 的长期规则 resume。

### 🆕 运维指令 · 2026-10-18 16:2x（🚨 P0：立即 resume 80B decay v2 + **长期授权：训练挂了自行重启，不再等许可**）· 用户直令 · 最高优先

> 用户令（2026-10-18）：「pretrain：重启 resume 训练，以后这种事不需要运维许可，自己的训练挂了，唤醒时看到了立刻修。」
> 现状：#548 已确认 **15:53:22 step 9400 后训练死亡**（GPU 全空、无 torchrun、日志无错）；最新 ckpt = **step_8000**（11:15）；step 8001–9400 将丢。**本轮直接 resume，不要等许可。**

**① 立即 resume（本轮唤醒）**
1. 确认 `nvidia-smi` 8 卡空、无 `torchrun`；确认 ckpt：
   ```bash
   ls -l /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/step_8000/model.safetensors
   ```
   若 `step_8000` 缺失，选最新的 `step_*`（必须含 `model.safetensors`）。
2. 给 `run/baize_xmodel25_decay_v2.sh` 加可选 resume（或直接改 torchrun 参数）：
   ```bash
   RESUME_DIR="${RESUME_DIR:-}"
   RESUME_ARG=""
   [ -n "$RESUME_DIR" ] && RESUME_ARG="--resume $RESUME_DIR"
   # 在 baize_xmodel25_decay_v2.py 参数末尾加 $RESUME_ARG
   ```
   启动：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
   RESUME_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/step_8000 \
     setsid bash baize_xmodel25_decay_v2.sh > /tmp/baize_xmodel25_decay_v2_resume.log 2>&1 < /dev/null &
   ```
   `--resume` 会从 step_8000 续跑（LR schedule 按 8000 起算；optimizer 状态不恢复，属已知小 transient）。脚本内部日志仍写 `$OUTPUT_DIR/baize_xmodel25_decay_v2_train.log`。
3. 判据：torchrun PID + 8 workers；8 卡 100%；train_log 从 **step 8001** 继续增长、无 error/traceback/OOM/CUDA；`--resume` 打印 `start_step=8000`。
4. 记录：MEMORY + daily + commit `pretrain resume:`。

**② 长期规则（立即生效，覆盖旧的「等运维许可」）**
> ⚠️ **作用域**：旧块（12:0x / 10-18② / 其它）里的「不重启 / 不碰训练 / 等运维裁定」只适用于各自任务；**训练已死时一律按本块 resume**。

- 以后唤醒先查训练：`pgrep -af torchrun`、`nvidia-smi`、train_log 尾部。
- **训练进程消失 / 崩溃 / 被杀** ⇒ 自查日志 → 选最新有效 `step_*` ckpt → **立即 `--resume` 重启**，不需要逐次等运维许可。
- 仅以下情况停手报 blocker：① 没有任何有效 ckpt；② 同一原因 1h 内连续崩 ≥2 次；③ 硬件/磁盘/网络错误明确；④ 重启命令本身失败。
- 仍禁止：kill 健康训练、改配方/数据、动别的线。

> 📦 §2026-10-18 12:0x（P0 修复 .29 ops 中继）+ 2026-10-18②（v5 中文 HTML + 数据前置实测）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：中继已修复闭环（PID1972249 存活、.last_run_id 123→125）；v5 三交付物（HTML+PLAN_V5_STABLE_1.5T.md+PLAN_V5_DATA_PREREQ.md）均 committed，分词实测 474K/375K tok/s·0.343 tok/B·2.31T·16并发≈1天·开工~10-20。需要时再读。



--- 归档批次 2026-10-25（任务书瘦身：09:3x ~ decay 20B 六块，原文搬迁）---

### 🚀 运维指令 · 2026-10-24 09:3x（**放行：基于自己报告的建议继续优化 BaiZe-2B 预训练吞吐**）· 用户直令 · 最高优先

> 用户原话：「pretrain：在 e09_fp8_tw_cg: FP8 TW+CG 基础上继续优化。昨晚 pretrain 已经把基线从 249K tok/s 上拉到了 FP8 TW+CG=297K tok/s(+17.9%)，并且产出了 report_pretrain_2b_throughput_optim_zh.html。在报告中 pretrain 提出了进一步优化的建议。现在**放行 pretrain 基于自己的建议继续优化 BaiZe-2B 模型的预训练效率**。**全量预训练待 data 数据准备好后就开始**。」

**① 现状基线（务必以此为准，勿重跑）**
- 基线：**252K tok/s**（BF16, TP1/DP8/MBS2/seq4096/GBS1024）
- **当前最佳：e09_fp8_tw_cg = 297K tok/s（+17.9% vs 本次基线 / +19.4% vs 历史 249K）**
- 关键发现：**FP8 tensorwise 单独用反而 -10%**（小 kernel launch 开销 > 计算节省），**叠加 CUDA Graphs 后量化 kernel 被图捕获 → +17.9%**（协同效应）。
- 峰值显存：e09 = **65.4GB / 80GB**（**尚有 ~14GB 余量**）
- 报告：`reports/report_pretrain_2b_throughput_optim_zh.html`；脚本 `baize_perf_optim.sh`

**② 放行范围：按你自己报告 §4「下一步建议」逐条验证（有权自定顺序与取舍）**
你已列出 7 条，请把它们做成**可验证实验**（沿用 e00~e09 同一评测口径：80 步、warmup 20 不计、step30-80 中位、loss 偏差 ≤5% 作正确性闸门）：

| # | 建议 | 我的要求 |
|---|---|---|
| 1 | **组合优化**：e09 + CE Fusion + **更大 MBS（3/4）** | **最优先**（显存有 14GB 余量，收益最直接） |
| 2 | **升级 CUDA 12.9+ 解锁 FP8 blockwise** | 先评估升级风险（TE 2.12 / torch 2.8 兼容性），**列升级步骤与回滚方案再动**；不许把环境搞坏 |
| 3 | **序列并行 SP**（`--sequence-parallel`） | 减 activation 显存 → 佐证 MBS 上限 |
| 4 | **数据侧**：num_workers / pin_memory / mmap 预取 | 先 profile 出 host 侧占比，再决定投入 |
| 5 | **NCCL 调优**：`NCCL_ALGO/PROTO` + NVSwitch 拓扑 | 低风险高性价比，优先做 |
| 6 | **更大 GBS** | 注意 GBS 变大影响收敛语义，**需标注可用性边界** |
| 7 | **torch.compile fullgraph** | 作为 CG 的替代路线单独成组对比 |

**③ 纪律**
- ✅ **每组实验必须给：中位 step(ms) / tok/s / 相对 e09 增益 / 峰值显存 / loss 与基线偏差 / 0 NaN**
- ✅ 突破 297K 的记录要**单独标注**（新纪录）
- 🚫 **不得改动训练语义**（LR/数据/模型结构一律不动，只动性能相关开关）
- 🚫 不动 `.12`（vision 在用）
- ✅ 每轮落 MEMORY + daily；**最后更新 report_pretrain_2b_throughput_optim_zh.html（追加第二轮结果）**
- ⏭ **全量预训练等 data 数据就绪后再起**（本轮只做性能优化，不启动长训）；data 就绪信号 = en_v1_4 分词 done=110/110 + 5 源迁移 `/nas_env` 完成

**④ 若发现"已经到顶"**：允许给出「当前硬件下的吞吐上限判断」（如受限于显存带宽/HBM 利用率），并说明依据（如 MFU 计算、带宽瓶颈分析），**不许为了凑数字硬调语义参数**。


### 🆕 运维指令 · 2026-10-23 22:1x（**优化 BaiZe-2B 训练吞吐：目标 > 249K tok/s**）· 用户直令 · 最高优先

> 用户原话：「pretrain：尝试各种方法优化 BaiZe-2B 的训练吞吐 目前最大值是 249K tok/sec，想办法超过这个值。」

**① 基线口径（先钉住，后面所有对比都靠它）**
- 用**当前已知最优配置**复跑 1 次基线：warmup ≥20 step 后取 **≥50 step 稳态**的 `tok/s`（中位数，别取峰值）+ 峰值显存 + s/step + grad_norm + loss。
- 记录到 `MEMORY_PRETRAIN_2B.md`：**baseline = 249K tok/s @ <配置指纹>**（TP/PP/DP、MBS×accum、GBS、seq_len、FP8 开否、compile 开否、模型并行组合）。**之后每次实验只改 1 个变量。**

**② 候选优化轴（按性价比顺序推进，逐条试，别一次改俩）**
1. **FP8 配方**：blockwise vs tensorwise scaling；first/last layer 排除 FP8；`--fp8-amax-history-len`/`amax-epsilon` 微调。
2. **计算图**：`torch.compile`（`--use-torch-compile` / fullgraph）· **CUDA graphs** · `--use-flash-attn-v3` · TransformerEngine 融合算子（LayerNorm/RoPE/SwiGLU）。
3. **并行度**：TP ∈ {1,2,4,8} × **SP** 开关；`--sequence-parallel`；DP/ZeRO-1（`--use-distributed-optimizer`）；`--overlap-grad-reduce` / `--overlap-param-gather`。
4. **批次**：MBS × accum 网格（固定 GBS），找 **tokens/step 最大且不 OOM** 的点；显存够就把 activation recompute 关掉。
5. **数据侧**：bin 读取预取 / `num_workers` / mmap / 避免 host 侧成瓶颈（`nproc`、`OMP_NUM_THREADS`、pin memory）。
6. **通信**：`NCCL_ALGO`/`NCCL_PROTO`/NVLink 亲和、`NCCL_IB_DISABLE`、网卡绑定（8 卡单机优先 P2P）。
7. **其它**：fused Adam / emerging-optimizers 的 fused 版、loss 计算融合、`--seq-length` 与 packed 序列对齐（避免 padding 浪费）。

**③ 每轮实验协议（严格，防「跑快了但训坏了」）**
- 单次实验 **≥50 step 稳态**（warmup 20 步不计），单次总时长 **≤30min**，**每改一个变量就 commit 一次**。
- 必须同时记录：**tok/s（中位数）/ 峰值显存 / s/step / grad_norm / 前 200 步 loss**。
- **正确性闸门**：与基线相比，同 step 的 loss 偏差 **≤5%**、`grad_norm` 无数量级跳变、**0 NaN/inf**；任一不满足 ⇒ 该配置判「快但不可用」，只记录不采用。
- OOM / 卡死 ⇒ 记下配置即放弃，🚫 不反复调参死磕。

**④ 交付**
- **至少 8 个候选**跑完（总量 ≤6h，分多轮唤醒做，每轮做完先落盘再继续）。
- 产出一张表（配置指纹 × tok/s × 相对基线增益 × 显存 × 是否通过正确性闸门）写进 `MEMORY_PRETRAIN_2B.md`，并生成中文 HTML：`reports/report_pretrain_2b_throughput_optim_zh.html`（自包含；含基线复现命令、每个候选的命令与数字、结论与「下一步还能挖什么」）。
- **超过 249K 就明确写「新纪录 = X K tok/s（+Y%）@ <配置>」**；若全都超不过，也要给「瓶颈归因」（算力/通信/数据/显存）+ 2–3 个更激进方案（如换并行度到头、换 attention 实现、改 GBS/seq）。
- commit 前缀 `pretrain perf:`。

**⑤ 纪律**：只在 **`.29` 8×H100** 上做；🚫 不碰 `.12`（vision 训练中）/ data / harness；每个数字必须能追到 log 或脚本输出；🚫 编造 tok/s。

### 🧪 运维指令 · 2026-10-23（**长上下文推理成本评测：BaiZe-2B / MiniCPM5-2B / Qwen3.5-2B**）· 用户直令 · 最高优先

> 用户原话：「pretrain：再做一次长上下文推理成本评测，对比模型 BaiZe-2B、MiniCPM5-2B、Qwen3.5-2B。推理框架统一用SGLang，上下文长度从64K开始翻倍，直到全部OOM。实验后写实验报告（中文HTML），列表对比各模型显存、推理速度等详细信息。」

**① 三个模型（报告须写明各自 HF 版本/commit + 参数量 + 架构）**
- **BaiZe-2B**（自有）：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/Xmodel-2.5-code/out/decay_5000_hf`（XmodelForCausalLM，即 decay-5000 产物）。
- **MiniCPM5-2B**：`openbmb/MiniCPM5-2B`（Llama 架构，max_pos 131072）—— 无权重先 HF 下载（工作目录已有 `MiniCPM5-2B.config.json` 可作参考）。
- **Qwen3.5-2B**：Qwen3.5 系列 2B —— 无权重先 HF 下载（本机现只有 Qwen3.5-4B / Qwen3-VL-2B 等，缺纯文本 2B）。

**② 评测方法（统一 SGLang）**
- 框架**统一 SGLang**（勿混 vllm）；每模型独立起服、独立测。
- 上下文长度**从 64K 翻倍**：64K → 128K → 256K → 512K → 1M → 2M → …，**直到该模型 OOM**（记录 OOM 点 = 实测上下文上限）。
- 每档记录（列表可溯源）：
  - **显存**：峰值/稳态 VRAM(GB)、KV cache 占用；
  - **推理速度**：prefill 吞吐(tok/s)、decode 速度(tok/s)、端到端延时；
  - **成功/OOM**。
- 复用/参考 `run/` 下既有 SGLang 长上下文脚本（`benchmark_p911_sglang.py`、`p911d_sglang_vram_bench.py`、`start_sglang_*.sh` 等），不足再新建。

**③ 报告（中文 HTML）**
- `reports/report_pretrain_longctx_infer_cost_3x2b_zh.html`（自包含）。
- **对比表**：三模型 × 各上下文档 的显存/速度/延时/OOM 点；突出「最大可服务上下文长度」与「同长度最快的模型」。
- 附：实验环境（GPU/驱动/SGLang 版本）、每模型复现命令、结论与建议。commit `pretrain eval:`。

**④ 纪律**：评测在 .29（8×H100 已空）；🚫 不碰 vision(.12)/data/harness；每个数字溯源到脚本输出/log；不伪造。

### 📄 运维指令 · 2026-10-23（**写 decay 修复完整中文 HTML 报告 + 下一步建议**）· 用户直令 · 最高优先

> 用户原话：「pretrain：写个HTML中文报告，包含对下一步实验的建议。」

**报告文件**：`reports/report_pretrain_decay_repair_zh.html`（自包含中文 HTML，内联样式、无外链/无脚本）。

**① 内容主线（decay「训坏 → 修复」全历程）**
1. **decay v2（自写脚本 · 失败）**：71.2B decay → CS8 **44.97%** / CX6 **6.21%**，vs Xmodel-2.5 官方 final 65.40%/32.90%（Δ **−20.43 / −26.69pp**）→ 判定「decay 训坏」。
2. **归因**：双移位 bug（py:547-548 + 567-568 双重移位）、peak LR 1.67e-3 过高、自写脚本缺 **μP**、code 过采样、step0 loss 11.72 异常。
3. **排查实验（自写脚本）**：L1（修双移位+LR5e-4+warmup100）→ CS8 **59.03%**；L2（只修双移位+高LR）被直令 kill 转官方方案。
4. **decay-5000（官方 1113.sh · 修复）**：官方 `train_decay_fp8_1113.sh`（use-mup + **Muon 0.2** + FP8 hybrid + 无 warmup + MBS=5 + WSD exponential 5000 步）→ **CS8 58.97% / CX6 28.02%**，vs 旧 decay v2 **+14.0 / +21.8pp**，vs 起点基线 61.03%（Δ −2.06pp）。
5. **结论**：官方 μP+Muon+FP8 修复了 decay 训坏，能力基本回到起点；残余 gap 归因写入。

**② 下一步建议（必写，给 ≥3 个候选，按价值排序，各附预期成本/风险/ETA）**
1. **延长 decay**：5000 → 20000 步（对齐官方 71.2B），看 CS8 是否逼近 65.40%（成本 ~3× 当前 GPU 时）。
2. **对齐数据配比**：官方 1113.sh 的 11 源配比（当前仅 4 源 64/24/8/4），隔离数据贡献。
3. 其他（可选）：min-lr / decay-iters 微调、更长 warmup、或更大 decay 数据量。

**③ 纪律**：对比口径统一用 Xmodel-2.5 官方 final（65.40%/32.90%）+ 起点基线 61.03%，**不用 P-8 作主对照**；数字溯源 `eval_summary.txt`/各 log；commit `pretrain report:`。

### 🆕 运维指令 · 2026-10-22 13:5x（**decay 5000 步 + 复用官方 MBS=5 排障**）· 用户直令 · 最高优先 · 覆盖 08:5x 的 train-iters/decay-iters/MBS 口径

> 用户原话要点：① 训练效率不高，为何不能复用官方脚本（MBS=5、FP8 等）；② decay steps 设 **5000 步取整**；③ 用下方指定 LR/decay 参数；④ 用 Muon（0.2）；⑤ 不用 warmup。

**① decay = 5000 步**：`--train-iters 5000`（≈18.1B token，取整接受）；`--lr-decay-iters 5000` + `--lr-wsd-decay-iters 5000`（覆盖之前 5560 / 20000）。

**② LR / decay / optimizer 参数（照抄，勿改）**：
```
--lr 1.66667e-3
--decoupled-lr 1e-2
--lr-decay-style WSD
--lr-wsd-decay-style exponential
--min-lr 1.041667e-4
--decoupled-min-lr 6.25e-4
--lr-decay-iters 5000
--lr-wsd-decay-iters 5000
--lr-warmup-iters 0
--optimizer muon
--muon-matched-adamw-rms 0.2
```

**③ MBS 复用官方 5（先排障，勿懒省事降 2）**：官方 1113.sh 就是 MBS=5/GBS=960/seq3776/FP8 hybrid 跑 8×H100-80GB；我们 MBS=5 仅报 ~81GB（超 ~1GB）。**先排查根因再谈降 MBS**：
- 检查缺 activation recompute（Megatron `--recompute-granularity selective|full`、`--recompute-method uniform`、`--recompute-num-layers`）；
- 检查 FP8 TE 的 amax/history buffer 与 distributed-optimizer 的显存占比；
- 优先靠「开 recompute / 关冗余 buffer」腾出 1–2GB 保住 MBS=5；**仅在 80GB 内确实无法跑通时才降 MBS**，并在报告写明降级原因与可行区间（如 4）。

**④ 其余**：配置沿用 1113.sh（use-mup/muon/FP8 hybrid/TP1 PP1 DP8/distributed-optimizer/tokenizer dsv3），`--load` 转换后 ckpt、`--finetune`。commit `pretrain decay:`。

### 🆕 运维指令 · 2026-10-22 08:5x（**decay 参考官方 train_decay_fp8_1113.sh + 20B 数据**）· 用户直令 · 最高优先

> 用户原话：「pretrain 的 xmodel decay 参考这个 https://github.com/XiaoduoAILab/Xmodel-2.5/blob/main/examples/xmodel/train_decay_fp8_1113.sh，使用20B数据」

**① 参考脚本（官方 `examples/xmodel/train_decay_fp8_1113.sh`，已核内容，照此落地，勿用自写脚本）**
- 模型：48L / hidden1536 / 24head / GQA8 / ffn3840 / rope / swiglu / RMSNorm / **use-mup（12.0 / 1.0 / 1.4 / 1.4）**
- 训练：GBS **960** / MBS 5 / seq **3776** / **optimizer muon**（muon-matched-adamw-rms 0.2）/ lr **1.66667e-3**（decoupled 1e-2）/ min-lr 1.04e-4 / **WSD** exponential / **lr-decay-iters 20000** / warmup 0 / wd 0.1 / clip 1.0 / bf16
- FP8：`--transformer-impl transformer_engine` / fp8-format hybrid / amax-history 128 / amax-compute-algo max
- 并行：TP1/PP1 纯 DP8 + `--use-distributed-optimizer` + overlap-grad-reduce/param-gather
- tokenizer deepseekv3 / vocab 129280

**② 数据量 = 20B**：`--train-iters` 重算 = 20e9 / (960 × 3776) ≈ **5560 步**（覆盖脚本原 550000）；decay 从起点 step_532000 ckpt 加载（HF→Megatron 转换后）。

**③ 前置（顺序）**：① 起点 HF ckpt → Megatron 转换（官方 convert.py + loader）；② DATA_PATH 用 `full_*` 6 源权重（若实测 0 shard 立即定位，报差异）；③ 100 步冒烟确认 loss 接得住 stable 末点 → 再起 20B decay。

**④ 纪律**：不抢 .12；每轮报 step/loss/0error；commit `pretrain decay:`；若此前 A 方案 1120.sh 与 1113.sh 冲突，**以 1113 为准**。⚠️ 写入前先归档旧闭合块，保证 TASK ≤ 32KB。



--- 归档批次 2026-10-25 ②（任务书瘦身：21:45/21:0x/19:2x/16:2x双机测试/补正，原文搬迁）---

### ✅ 运维实测 · 2026-10-24 21:45（**2-rank NCCL 已打通 ⇒ 16 卡失败根因 = 缺 NCCL 环境变量**）· 用户授权手工排障 · 最高优先
> 手工最小复现（`/nas_train/app.e0031982/nccl_dbg/tc.py`，2 rank × 1 卡 × 20 步 all_reduce）**全部通过**：
> `iter 0..19 ok` · **`busbw ≈ 46.3 GB/s`** · `Connected all rings, use ring PXN 0 GDR 1`（**GPUDirect RDMA 生效**）· 两端 `Destroy COMPLETE`。
> **必须照抄到双机 launcher 的「主 + 从」两侧环境**（缺一个都可能 hang）：
> `NCCL_IB_GID_INDEX=3  NCCL_IB_MTU=4096  NCCL_IB_TC=106  NCCL_IB_TIMEOUT=22`
> ⚠️ **不要**设 `NCCL_SOCKET_IFNAME`（会与管理网 `bond0` 冲突）；`MASTER_ADDR` 用 **`10.239.2.12`**（bond0，两机互通已验证）。
> 现场事实：`.12` 有 10 个 MTU=4096 的 ACTIVE RoCE 口；`.29` 同集合但 **`mlx5_7`/`mlx5_15` 是 PORT_DOWN**——若手工指定 `NCCL_IB_HCA`，两侧都要排除它们（不指定则 NCCL 自动跳过）。
> **下一步（立即）**：把上面 4 个变量加进 `run_dualnode_16gpu.sh` 的**主从两侧**，重跑 e18 口径 16 卡（MBS3 + FP8 TW + CG，GBS=1008，80 步），回报：聚合 tok/s、线性扩展效率（÷2×305098）、每卡 tok/s、loss 与单机 e18 的一致性。
> 🚫 不要再在未加这 4 个变量的情况下起 16 卡（前两次 hang 就是这个原因）。


### 🧪 运维令 · 2026-10-24 21:0x（**双机 NCCL 卡在 worker 初始化 → 停盲目重试，按最小复现定位**）· 用户直令 · 最高优先
> 事实（RUN_ID 171/172/173 实测）：20:08 与 20:23 两次双机起训**都挂在 `NCCL init`**——master 首个 ALLREDUCE 等 600s 超时（`last completed: -1`），worker **从未 enqueue 任何 NCCL 工作**，日志只到 `Connected all rings/trees`、**没有 `Init COMPLETE`**。清理后 16 卡已空闲。
> **本轮动作（按序，不得跳步）**：
> 1. **最小复现**：只起 **2 rank（每机 1 卡）跑 20 步**，加 `NCCL_DEBUG=INFO NCCL_DEBUG_SUBSYS=INIT,NET`，两边日志落 `/tmp/nccl_dbg/`；**验收 = 出现 `NCCL INFO Init COMPLETE`**。
> 2. **显式指定网络面**（RoCE 跨机 hang 的第一嫌疑）：先 `ibv_devinfo -v | grep -E 'GID|state|link_layer'` + `ip -br addr` 查清口名/GID，再设 `NCCL_IB_HCA=<RoCE 口>`、`NCCL_IB_GID_INDEX=<实测>`、`NCCL_IB_TC=106`、`NCCL_IB_MTU=4096`、`NCCL_SOCKET_IFNAME=<管理口>`。
> 3. **对照实验**：同一最小复现再跑一次 `NCCL_IB_DISABLE=1`（走 TCP）。TCP 过 / IB 不过 ⇒ 锁 RoCE（MTU/GID/TC/`rp_filter`）；两者都不过 ⇒ launcher/rank 编排问题。
> 4. **只做实验，不动单机配方**：`--train-iters 20` 通了再回到 80 步量吞吐；🚫 不得改 e18（MBS3+FP8TW+CG）。
> 5. **落盘**：两边 `NCCL_DEBUG` 日志 + `ibv_devinfo` + 结论写进 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新节「双机 NCCL 排障」，MEMORY 记一行。
> 🚫 **不要再把 16 卡全量起一次然后等 10 分钟超时**（已浪费约 25 分钟）——先 2 rank 打出 `Init COMPLETE`。


### ⚡ 应急令 · 2026-10-24 19:2x（**loop 曾卡死 29h，已由运维重启 —— 本轮唤醒第一件事就是跑 16:2x 双机测试**）· 用户直令 · 覆盖一切
> 事实：`/tmp/baize_pretrain_loop.log` 停在 **10-23 14:09「wake up, invoking pi」**（29h 未再唤醒），MEMORY 停在 **15:07 #766**，而 **`.29` 与 `.12` 的 16 张 H100 全空（0 MiB / 0%）**。
> **本轮唤醒顺序（不得跳过）**：① 先做 16:2x 的前置三验（`.12`/`.29` 空闲、两机互通、`ibstat`/`topo -m` 确认走 IB 而非 TCP）；② **立即起 DP16 双机训练**（其余超参不变：MBS3 / FP8 TW / CG / GBS1024 / 同数据 / 80 步口径）；③ 报**聚合 tok/s、线性扩展效率、每卡 tok/s、NCCL 带宽、loss 一致性**；④ 测完**立即释放 16 卡**并落 MEMORY + daily；⑤ 再回头做常规巡检。
> 🚫 **不要**以"data 未就绪"为由推迟本次测试——本次只测**吞吐**，用现有数据规模跑 80 步即可，不需要全量语料。


### 🔥 运维指令 · 2026-10-24 16:2x（**双机 16 卡联合训练测最大吞吐**）· 用户直令 · 最高优先

> 用户原话：「现在 `.12` 和 `.29` 都空闲对吧，**让 pretrain 试试看用两台机器一起训练，最大吞吐能有多少**」
> **背景**：单机 8×H100 吞吐 **305K tok/s**（e18 = MBS3 + FP8 TW + CG）已定档；本次要量化**跨节点扩展效率**（8→16 卡的 scaling）。历史曾规划过「双机 16 卡 scaling 彩排」，此次正式执行。

**① 前置确认（必须先做，不确认不起跑）**
1. **`.12` 真的空闲**：`ssh 10.239.2.12 nvidia-smi` → 8 卡 0 MiB / 0%；`pgrep -af 'torchrun|python.*train'` 无训练进程。
   - ⚠️ vision ArmE-R2 全链路已 DONE（10-24 07:00 前后），但**其 loop/watcher 可能仍存活**，若发现 GPU 被占，**先报不要抢**。
2. **`.29` 空闲**：8 卡全空。
3. **网络**：两机互通（`ping` + `nc -z` master port）；确认 **IB/RoCE 可用**（`ibstat` / `nvidia-smi topo -m`），**跨节点 NCCL 走 IB 而非 TCP**，否则 scaling 会很差。
4. **共享存储**：确认两机看到同一个 NFS（`data/` 路径一致）。

**② 测试设计（严格单变量：只加机器，配置全同 e18）**

| 项 | 值 |
|---|---|
| **基线** | 单机 8 卡：**305K tok/s**（e18：MBS3 + FP8 tensorwise + CUDA Graphs） |
| **本次** | **双机 16 卡（DP16）**，其余**完全不变**：MBS3 / FP8 TW / CG / seq / LR / 数据 / 80 步评测口径 |
| **并行** | **TP=1 / PP=1 / DP=16**（跨节点纯数据并行） |
| **启动** | `torchrun --nnodes=2 --node_rank={0,1} --nproc_per_node=8 --master_addr=<.29或.12> --master_port=<空闲端口>` |
| **GBS** | 保持 **1024**（每卡 MBS3 × 16 卡 = 48/step，需 accum 调整到整数；**若 GBS 必须变，明确标注并说明**）|

**③ 关键指标（必报）**
1. **聚合吞吐 tok/s**（16 卡）
2. **线性扩展效率** = 16卡吞吐 ÷ (2 × 305K)
   - **≥85% 算优秀**（意味着 518K+ tok/s）
   - 70–85% 可接受（NCCL 开销）
   - <70% 需归因（网络/同步/数据加载）
3. **每卡 tok/s** 对比单机是否有下降
4. **step 时间**、**GPU 利用率**、**GPU 显存**
5. **NCCL 带宽**（`NCCL_DEBUG=INFO` 抓 `busbw`）、**是否走 IB**
6. **loss 一致性**：前 20 步与单机 baseline 对比（Δloss ≤5% 才算等价）

**④ 若吞吐不达标，归因方向**
- 网络：IB 未启用 / 带宽不足 / 跨节点 RTT 高
- 数据：`.12` 与 `.29` 的 NFS 读取速度差异（谁慢谁拖）
- 同步：DDP allreduce 频率（GBS 1024 时每 step 一次）
- 尝试：`--use-distributed-optimizer`、`--overlap-grad-reduce`、`--overlap-param-gather`、`NCCL_ALGO`/`NCCL_PROTO` 调优

**⑤ 纪律**
- 🚫 **不抢 vision 正在用的卡**（若 `.12` 有占用，报 blocker 等确认）
- ✅ 两机启动脚本必须**可复现**（落到 `run/` 并 commit）
- ✅ 每轮落 MEMORY + daily；测完**立即释放 16 卡**
- ⚠️ 若扩展效率 <70% 且短期调不通，**如实写"当前网络条件下 16 卡不划算"** —— 这本身就是有价值结论（决定全量预训练用单机还是双机）


### ⚠️ 补正 · 2026-10-24 16:2x（**SGLang 对 Mamba2 的支持早已验证过，勿再核查**）· 用户直令

> 用户原话：「SGLang 对 Mamba2 的支持性这个早先实验验证过。」
> **补充事实（运营方核实 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` P-9.11 ②）**：sglang 0.5.9 **已成功服务 Mamba2-hybrid**，可直接复用现成配置，**不需要再"先报支持性"**。

**已验证的现成配置（直接照抄，这是 ground truth）**
| 项 | 值 |
|---|---|
| 框架 | **sglang 0.5.9**（vllm conda env，torch 2.9.1+cu128，flashinfer 0.6.3） |
| hybrid 模型转换 | mcore distcp → HF **`nemotron_h`**（sglang 原生支持），脚本 `baize_p6_ckpt_to_hf.py` |
| sglang 启动参数 | `--context-length 131072 --mem-fraction-static 0.85 --attention-backend flashinfer`，**hybrid 加 `--mamba-ssm-dtype float32`** |
| 超长上下文 | `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1` |

**参照历史**：P-9.11 用过 `p3_hybrid/iter_0005000` 转 HF（510 mcore keys → 323 HF keys，2.220B，4.4GB safetensors）。

**因此修订第二节的第 2 条**：
- ❌ 删除「先核查 SGLang 对 Mamba2 的支持性 / 若不支持就写不可服务」
- ✅ **改为**：**直接复用 P-9.11 的已验证配置**（`nemotron_h` HF 转换 + `--mamba-ssm-dtype float32` + `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`），**把这次用的 ckpt 路径与转换方式在报告里写清即可**
- ⚠️ 唯一需注意：本次要用的是**当前实际训好的 BaiZe-2B（Mamba2-hybrid）ckpt**，需先做 **mcore distcp → HF `nemotron_h`** 转换（照 `baize_p6_ckpt_to_hf.py`），并**做一次 logits 对齐自检**确认转换无损。**这是唯一的新增前置，其余照抄 P-9.11。**



## 归档 2026-10-26（由 MEMORY_PRETRAIN_2B.md 搬入，原文未改，已被 #784 取代/证伪）

> - **🔥 决定性发现（cfg0a 稳态 iter20–50 确认·根因报告已交付 21KB）**：cfg0a(seq4096/mbs4/gbs512/accum8→tok/step2.10M)=稳态17.94s/步→**116,898 tok/s @ 14.2% MFU**；cfg1(seq8192/mbs2/gbs256/accum8→同 tok/step2.10M)=108,291 tok/s。**同 tok/step(2.10M)，seq4096 vs seq8192 吞吐几乎相同(117K≈108K)** ⇒ **seq 长度不是 5.6× 掉速的成因**。**根因 = 小批几何(gbs512/accum8 vs 基线 gbs1008/accum21)→GPU 饥饿(MFU 73.6%→14%)**：cfg0a 每步只做基线一半 token(2.10M vs 4.13M)却花 2.64× 墙钟(17.9s vs 6.8s)，多出的~14.5s 几乎全是 GPU 空闲(kernel launch 间隙 + 每步固定开销不摊薄)。CUDA graph 两组均 `built 112` 成功→H2 证伪。**#779/#781「SSM 超线性」hereby 标记已证伪**（SSM 线性 O(n)，且 cfg0a@4096 同样慢）。⚠️ 旧「tok/microbatch/GPU=16384 悬崖」框架作废——基线 mbs3×4096=12288 < cfg0a mbs4×4096=16384 却更快，per-microbatch token 数不是悬崖变量；真正变量是总批几何(gbs/accum/mbs 联合)。cfg0b(seq4096 全批)为反向印证(排队中)。报告 `reports/report_pretrain_seq8192_slowdown_rootcause_zh.html`(21,123B/0script/8h2/标签配平✓)。
> - **17:5x 已交付（commit 233c47d0e pushed）**：`reports/report_pretrain_seqlen_throughput_zh.html`(16774B/0script/0外链/8h2)+生成器`run/gen_seqlen_throughput_report.py`(**重生成diff空=确定性✓**)+EXPERIMENTS新节「seq长度x tok/step吞吐网格」(6格表+发现+结论)+cfg0a/cfg0b对照脚本`baize_seqlen_ctrl_test.sh`。cfg1-4 OK(108K/112K/112K/121K)、cfg5/6 OOM@32768(peak81GB)。
> - **20:2x 进度**：①Web对标完成(Qwen3/Qwen2.5均4K预train；Llama3 8K但非hybrid；Megatron docs建议CP>8K；PyTorch博客"Mamba2 kernel fusion"1.5-2.5×加速→我们可能走未融合SSD路径)②日志实证(CUDA Graph 4096/8192同样启用排除H2；step time CV~2%稳定排除H1数据饥饿；config dump确认4Attn+24Mamba2+28MLP、SP=false/CP=1)③**cfg0a✅113.5K确认**(推翻seq假设)④**cfg0b🏃运行中**(seq4096/mbs3/gbs1008=基线配方同脚本复现，判据:若≈606K→基线真实+grid因tok/microbatch=16384慢;若≈113K→基线606K来自不同setup)。H6/H7 module-level profile 仍待(cfg0b后)。
> - **下一步**：③④✅已由运维侧完成——根因报告 `reports/report_pretrain_seq8192_slowdown_rootcause_zh.html`(21KB/8h2/H1-H9假设表+web引用5条+cfg0a对照+算术分解+GPU饥饿机制)已交付；#779/#781「SSM超线性」已在 EXPERIMENTS+MEMORY 标记已证伪、真因=小批几何GPU饥饿(MFU14%)。剩：①查`/tmp/baize_seqlen_ctrl/ALL_RESULTS.txt`收 cfg0b 终值；②判 cfg0b(≈606K→基线几何快/反向印证；≈117K→基线606K另有来源)；⑤运维侧将以 `pretrain rc:` 前缀 commit(只 add 本次文件)。
> - **未完成指令：cfg0b 终值待收**（20:2x 根因报告 HTML 已由运维侧交付 21KB + #779/#781 已更正）⇒ **WAITING=0**。cfg0a/cfg0b 后台 setsid 运行(`/tmp/baize_seqlen_ctrl/`)，跨唤醒存活。


---

## 归档 · 2026-10-26 四条运维令（15:3x / 14:3x / 13:2x / 11:1x，均已完成）

### [运维令] 2026-10-26 15:3x（**整理「BaiZe-2B 预训练构想」为中文 HTML 报告 + ETA**）· 用户直令 · 最高优先

> 用户原话：「关于后续的预训练，我有个初步想法想跟 pretrain 商榷。请安排 pretrain 把这个想法整理为中文 HTML 报告，附上 ETA 等信息。」
> 用户构想原文照录如下，请据此整理成报告。

**① 模型与配方**
- 模型：Mamba2-hybrid（56 层，Nemotron-H 式顺序混合），参数量 **2.2B**。
- 训练配方：**16K / 16卡 / CP1 DP16 / graph-OFF = 613,992 tok/s**。
- 学习率：**WSD**，2000 步 warmup，然后 LR **保持 1e-3**。

**② 三阶段计划**
- **S1**：2M tok/step · 1.4T tok · 700,000 steps
- **S2**：4M tok/step · 1.4T tok · 350,000 steps（配比同 S1）
- **Decay**：4M tok/step · 80B tok · 20,000 steps

S1/S2 配比（sampling prop / epochs）：
| dataset | prop | epochs |
|:--|--:|--:|
| en_v1_4 (ultrafineweb_en_v1_4) | 0.65 | 0.81 |
| ufw_l1_en_hq | 0.05 | 0.93 |
| ufw_zh | 0.04 | 0.99 |
| Math-L1 (UltraData-Math-L1) | 0.05 | 0.85 |
| Math-L3 (UltraData-Math-L3) | 0.02 | 0.72 |
| Code-L2 (UltraData-Code-L2) | 0.15 | 1.00 |
| Code-L3 (UltraData-Code-L3) | 0.04 | 0.87 |

Decay 配比（prop）：
ufw_en_l3(qa) 0.18 / ufw_zh 0.04 / Math-L3 0.04 / Code-L3 0.02 / UltraData-SFT-2605 0.60 / UltraData-SFT-Agent-2609 0.12

**③ 报告要求**：输出 `reports/report_pretrain_baize2b_pretrain_plan_zh.html`（自包含中文 HTML）。
- 结构：① 模型与配方 → ② 三阶段计划（各阶段 tok/step、steps、数据配比表）→ ③ **ETA 测算**（按 613,992 tok/s 算 S1/S2/Decay 各阶段 wall-clock 时长 + 总时长；分「纯训练」与「含故障/checkpoint 预留」两口径）→ ④ **商榷点与建议**（例如：4M tok/step 下 16K CP1 DP16 吞吐是否仍 613,992 需重测；LR 保持 1e-3 不改 + WSD 2000 步 warmup 的含义；数据配比 epochs<1 的采样语义；Decay 阶段 SFT/Agent 数据占比 0.72 的合理性；总计耗时与 GPU 预算）。
- 全部数字可溯源（吞吐用 #792 实测 613,992）；commit `pretrain plan:`。

### [运维令] 2026-10-26 14:3x（**补写 #792 双机实测结果进吞吐报告**）· 用户直令 · 最高优先

> 用户原话：「下发指令，让 pretrain 更新报告」
> **问题**：`reports/report_pretrain_seq16k32k_throughput_zh.html` 仍是 #791 旧版（14,208B，正文停在「16K 外推 ~584K + 待实跑确认」），#792 双机 16 卡实测结果没写进去。

**① 补写「双机 16 卡实测」节（数字溯源 `results_dualnode_seq16k32k/` + EXPERIMENTS §五·8）**
- **16K CP1 DP16 graph-OFF accum16 = 613,992 tok/s**（每卡 38,374、peak 75.2GB、0 NaN）→ 600K 目标 **102% 达标**（反超 8K 基线 #770 的 606,300 约 1.3%）；
- **16K CP2 = 281,970（0.459×）**：CP 在 16K 纯亏（激活显存 75.2→49.7GB 但吞吐掉 54%）→ 16K 应关 CP；
- **32K CP2 DP8 = 351,526 tok/s**（每卡 21,970、peak 76GB、0 NaN）= 600K 的 58.6%，结构性受限（32K 强制 CP=2[CP1 OOM@81GB] + 2×上下文 + P2P KV 交换，已≈2×线性外推天花板 366K 的 96%）。

**② 改写「结论与后续」**：16K 从「待实跑确认」改为「已达标 613,992 ≥600K」；32K 写明「结构性到不了 600K，351,526 已≈天花板 96%」；删除/更新过期的「待办 (a) 实跑确认 (b) 32K graph ON」条目。

**③ 纪律**：报告正文必须真含这些数字（🚫 再只在心跳里说、正文不写）；更新后 commit `pretrain perf:` + push，心跳附新字节数（须 >14,208 即证明真更新了）。

### [运维令] 2026-10-26 13:2x（**继续推进 FP8 真实数据 16K/32K 吞吐实测**）· 用户直令 · 最高优先

> 用户原话：「安排 pretrain 继续推进 16K/32K 吞吐实测」

**① 现状（复用，勿重复验证）**：双机 16 卡 BF16 连通性已验证（84% scaling、IB 多通道健康、SSH cleanup 挂起已 kill + 结果解析已修）。**下一步 = 正式 FP8 真实数据的 16K/32K 吞吐实测。**

**② 本轮任务**
1. 修完 `baize_dualnode_16gpu_test.sh` 的 SSH cleanup（等远端 torchrun 干净退出再加超时兜底，不再 `wait` 空挂）后，**去 `--mock`、用 `--fp8-recipe tensorwise` + 关 CUDA Graph + 真实数据**，起双机 16 卡。
2. **seq=16K**（CP=1，accum≥16）实测：目标冲 **≥600K tok/s**；记录全卡 tok/s / 每卡 tok/s / peak 显存 / loss / NaN。
3. **seq=32K**（CP=2）实测：给出**真实可达最优吞吐** + 量化 CP 的 P2P KV 交换开销 + 明确「32K 到不了 600K」的天花板与瓶颈。
4. 每配置写清：seq / DP/CP / accum / MBS / 关graph? / fp8? / tok/s / 显存 / 结论，全部溯源脚本+log。

**③ 交付**：结果追加到 `reports/report_pretrain_seq16k32k_throughput_zh.html`（或新报告）+ EXPERIMENTS 更新；commit `pretrain perf:`。

**④ 纪律**：双机先用 `nvidia-smi` 确认 .12 空、不抢 vision/data/harness；数字不伪造；脚本改动留 diff/备份。

### [运维令] 2026-10-26 11:1x（**双机 16 卡实测调优 seq=16K/32K 训练吞吐**）· 用户直令 · 最高优先

> 用户原话：「安排 pretrain 继续调优双机16卡 seq=16k/32k 的训练吞吐」

**① 目标**：用**真实双机 16 卡**（2×8 H100）实测并调优 seq=16K 与 seq=32K 的训练吞吐（此前只是单机 8 卡 + 外推，未真 16 卡实跑）。

**② 现状（复用你 #791 结论，直接在此基础上继续，勿重复取证）**
- 16K（CP=1，关 graph，accum16）8 卡 = 300,133 tok/s（每卡 37,516），外推 16 卡 ~584K，**尚未真 16 卡实跑**。
- 32K（CP=2，FA3 11 处 patch 后）8 卡 = 183,394 tok/s（每卡 22,924），外推 16 卡 ~322K。

**③ 要求**
1. **真 16 卡跑**：起 2 机（`.29` + 另一台空闲机，先 `nvidia-smi` 确认空闲）DP16 或 DP8×CP2，跑 seq=16K 与 32K，记真实 tok/s（别再只外推）。
2. **调优方向**（可自行调整并记录理由）：16K 冲 600K+（调 accum / CP 开与关 / recompute 粒度 / 通信重叠）；32K 给出**真实可达的最优吞吐**，并量化 CP P2P KV 交换开销，明确「32K 因 2×上下文+CP 固有代价到不了 600K」的具体瓶颈与天花板。
3. 每个配置记录：seq / DP/CP / accum / MBS / 关graph? / tok/s(全卡) / 每卡 tok/s / peak显存 / loss / NaN / 结论。

**④ 交付**：实测结果写入 `reports/report_pretrain_seq16k32k_throughput_zh.html`（在原报告追加 §）或新报告；更新 EXPERIMENTS；commit `pretrain perf:`。

**⑤ 纪律**：16 卡需 2 机，先确认第二台空闲、不抢 vision(.12)/data/harness；数字溯源脚本/日志；不伪造。



---

## 归档 · 2026-10-26 两条运维令（09:1x / 08:2x，均已完成）

### [运维令] 2026-10-26 09:1x（**优化 16K / 32K 训练吞吐至 600K+**）· 用户直令 · 最高优先

> 用户原话：「pretrain：16卡训练吞吐 seq=8k 吞吐（~605K）已达标；现在继续优化16k和32k训练吞吐，争取达到600K以上」

**① 基线（已达标）**：seq=8192 关 graph，16 卡 ~593K（或按你实测 ~605K），以实测为准写明。

**② 目标**：**seq=16K 与 seq=32K 的训练吞吐各 ≥600K tok/s（16 卡）**。

**③ 现状（复用你 #787/#788 结论直接优化，勿重复取证）**
- 16K：关 graph = 561K（0.93×），距 600K 差 ~7%，需继续优化。
- 32K：cp1 OOM@81GB / cp2 被 flash-attn-3 阻断（`window_size=(l,r)` 旧签名，需 patch `window_size_left/right`，调用点在 site-packages）。

**④ 方向（建议，可调整并记录理由）**
1. **16K**：从 561K 找瓶颈（CP 激活重算 / KV cache / 通信重叠），尝试 context parallel、recompute 粒度微调等合法手段冲 600K+。
2. **32K**：先 patch CP 路径 flash-attn-3 的 `window_size` 调用跑通，再优化吞吐冲 600K+；若 32K 物理受限（显存/架构），如实给出「当前最优吞吐 + 阻塞点 + 需要什么（如更多显存/升级 flash-attn/改 CP 实现）」。

**⑤ 交付**：逐档记录（配置 → tok/s → 达标? → 瓶颈/结论），溯源脚本/日志；中文本报告 `reports/report_pretrain_seq16k32k_throughput_zh.html` + EXPERIMENTS 更新；commit `pretrain perf:`。

**⑥ 纪律**：只用 .29（如需 16 卡则 2 机）；🚫 不碰 vision/data/harness；数字不伪造。

### [运维令] 2026-10-26 08:2x（**写最近工作报告 · 中文 HTML**）· 用户直令 · 最高优先

> 用户原话：「关于最近的工作，安排 BaiZe 4个agent各自写一份报告。」

**任务**：写本线（pretrain）最近工作（10-20 起）总结报告 `reports/report_pretrain_recent_work_zh.html`（自包含中文 HTML）。
- 结构：① 本线定位 → ② 近期任务逐个（设置→过程→结果→结论）→ ③ 关键数据速查表 → ④ 阻塞/待拍板 → ⑤ 下一步建议。
- **必覆盖**：① decay 训坏→修复全历程（v2 44.97%/6.21% → 官方 1113.sh decay-5000 58.97%/28.02%，含归因双移位/缺μP/LR）；② 长上下文 seq 扩展排查（CUDA Graph 顶格停滞真因 + seq=8192 关 graph 0.978×满速 + 32K CP 不可跑[flash-attn-3 API 阻断]）；③ 两份 decay 报告交付。
- 数字溯源（log/json 文件:行）；遵守命名规程；commit `pretrain report:`。



---

## 归档 · 2026-10-25 23:0x 通宵攻坚令（已完成）

### [运维令] 2026-10-25 23:0x（**通宵攻坚：查清 tokens/microbatch 悬崖并给出可用档位；不解决不收工**）· 用户直令 · 最高优先
> 用户原话：「下发指令让 pretrain 这个晚上一直排查这个问题，解决不了不要结束。」
> 已知事实：基线(seq4096/mbs3=12,288 tok/mb/GPU)=606,449 tok/s；cfg0a(seq4096/mbs4=16,384)=113,514；cfg1(seq8192/mbs2=16,384)=108,291；cfg3/4(16K, 16,384)=112,094/121,495 ⇒ **悬崖在 12,288-16,384 tok/microbatch/GPU 之间，与 seq 无关**；四格峰值显存 81.08GB 顶到上限，基线 67.6GB。

**0) 夜间纪律（覆盖其它收尾条文）**
- 本轮起至 **2026-10-26 08:00** 持续攻坚，`WAITING=0`；**不许**以「等用户 / 等运维 / 无新令」结束或空转。
- 每个实验用 `setsid` 后台跑，`sleep 120-300` 轮询判读；**每 30 分钟至少一次 progress commit**（`pretrain rc: ...`），关键发现即时写 MEMORY。
- 08:00 前必须交**早报**：一句话结论 + 档位表 + 证据路径（无论成败）。
- 🚫 不 kill `SWE-bench` 下载与 harness 复跑；🚫 不抢 data 分词资源；每格跑完立刻释放 16 卡；🚫 不许把猜测写成结论、不许编数。

**1) 实验阶梯（按序，能跳就跳但要写理由）**
| 步 | 配置 | tok/mb/GPU | 目的 | 判据 |
|:--|:--|--:|:--|:--|
| E1 | seq4096 / mbs3 / gbs1008（=cfg0b） | 12,288 | 复现基线 | ~606K ⇒ 基线真实；~113K ⇒ 基线来自不同 setup，先查环境 |
| E2 | seq8192 / mbs1 / gbs256（accum16） | 8,192 | **seq 8K 能否满速** | 回到 55-60 万 ⇒ 「8K 满速只要 MBS=1」，这是给用户的答案 |
| E3 | seq12288 / mbs1 | 12,288 | 定位阈值（与 E1 同 tok/mb、不同 seq） | ~606K ⇒ 阈值只与 tok/mb 有关，与 seq 无关（终判） |
| E4 | seq8192 / mbs1.5 不可行 ⇒ seq6144 / mbs2 | 12,288 | 第三个同阈值点交叉验证 | 同上 |
| E5 | 16,384 tok/mb 的最小复现（seq4096/mbs4 已有） | 16,384 | 悬崖边界细分：再插 seq4096/mbs4 与 seq8192/mbs2 均为 16,384 ⇒ 用 seq=8192/mbs2 与 seq=16384/mbs1 已覆盖；补 **seq=4096/mbs3.5 不可行**，改测 **seq=2048/mbs8=16,384** 与 **seq=1024/mbs16=16,384** | 若小 seq 大 mbs 也慢 ⇒ 纯 tok/mb 效应；若快 ⇒ 与 seq 相关 |

**2) 归因（E1-E5 出数后 2 小时内定位）**
- **显存假说（首选）**：16,384 tok/mb 下峰值 81GB 顶格 ⇒ 检查是否触发 activation recompute / offload / 碎片；取 `torch.cuda.memory_summary()` 在 12,288 与 16,384 两侧各一份，比对 reserved/allocated/active 与 fragmentation；核对 `--recompute-*`、`PYTORCH_CUDA_ALLOC_CONF` 实际生效值。
- **kernel 假说**：profile 六类（attention / ssm / mlp / loss / optimizer / data）在 12,288 与 16,384 各 10 步；看是否有算子在某 token 数跨过阈值后换实现（FP8 GEMM tiling、CUDA graph node 数、SSD chunk）。
- **CUDA graph 假说**：确认两侧 graph 是否都 capture 成功、replay 次数与 graph 数量是否爆炸（token 数变化 ⇒ 多 shape ⇒ 多 graph）。
- **数据假说**：data-loading 计时 + util 曲线，两侧对比；若 data 占步时 >30% 记下来但不算主因（除非其它都排除）。

**3) 修复与验收**
- 定位后**只改一项**（MBS/accum、CP、recompute、graph 配置、mamba dtype 之一），在 **seq=8192** 上复测，要求：`tok/s >= 0.7 × 606K`（即降幅 ≤30%）且 loss/gnorm/NaN 正常。
- 若 16K 必须 CP：给 CP=2/4 的可行性 + 预期吞吐（可只跑 20 步 smoke）。
- 产出**档位表**：`seq × MBS × accum → tok/s → per-GPU → 峰值显存`，并给 S1/S2 的推荐档位（含「8K 满速配方」）。

**4) 收敛条件（必须同时满足才算解决）**
1. 能一句话解释 5.5x 的成因，且有实验/证据支撑；
2. 给出可复现的修复配方，且复测达标（≥0.7×基线）；
3. `reports/report_pretrain_seq8192_slowdown_rootcause_zh.html`（≥15KB）+ 修正版 seqlen 报告（旧结论标「已证伪」）+ EXPERIMENTS 新节 + MEMORY 首部新块，全部 commit。
- **若 08:00 仍无解**：必须交「早报 + 已排除清单（每条附证据文件）+ 下一步最小实验（≤30 分钟可跑）+ 需要用户/运维决策的点」，**不许只写「未解决」**，也不许停机。

**5) 交付路径**
**附**：cfg5/cfg6（32K）OOM 重试按「配方变更组」（`--recompute-activations` / `--use-distributed-optimizer`）单列，不混主表。

- 实验日志 `/tmp/baize_rc_<step>/`；结果表 `run/pretrain_rc_ladder_20261026.tsv`（逐格一行）；profile 落 `run/pretrain_rc_profile_<tokmb>.txt`。
- commit 前缀 `pretrain rc:`；报告 08:00 前必须存在（哪怕标 `rev1`）。


## 归档 2026-10-28（由 BAIZE_PRETRAIN_2B_TASK.md 搬入，原文未改）

### [运维提示] 2026-10-27 09:2x（**DataLoader OOM 根因升级：fork COW 膨胀 + spawn 方案参考**）· 用户转交 · 供考虑

> 用户请外部调研后转交：把 #802/#803 的「worker RSS 累积」根因做一次**机制级升级**，给出更本质的解法，**请 pretrain 记入知识并自行评估采纳**（非强制照做）。
> **根因（机制级）**：PyTorch DataLoader 默认 `fork()` 起 worker，子进程继承 rank 进程内存；**Python 引用计数每次访问对象都写对象头 ⇒ read-only 访问也触发 COW（copy-on-write）⇒ 父进程内存（CUDA context + 数据索引 + 已加载数据）被逐个 worker 复制，N 个 worker 后 RSS 近翻 N 倍** → 耗尽 .29 swap → OOM-kill。这精确解释了 `num_workers 8→step70 / 4→step90 / 2→step200`（worker 越多 COW 越快）。
> **方案（按序，一次只改一项 + ≥30 步稳态 + 记录收益/副作用）**：
> 1. **spawn 启动**（最彻底）：`torch.multiprocessing.set_start_method('spawn', force=True)` 或 Megatron 对应开关——worker 不再 fork 复制父进程内存，代价是启动慢。
> 2. **`persistent_workers=True`**：worker 常驻，避免反复 fork 重建累积（单靠它不消除 COW，但可搭配 spawn）。
> 3. **大对象（数据索引/词表）放 shared_memory**：避免每 worker 复制。
> 4. **关 `pin_memory`**（若在开）：避免大 batch 锁页内存碎片化。
> 5. `num_workers=0`（#803 已用）：**消除症状的最保守根治**，在 16K batch（mmap<10ms vs 计算~9s，IO<1%）下吞吐损失可忽略，故当前选择合理。
> **评估口径**：若后续数据加载变重（重 tokenize/augment），应转向 **spawn + persistent_workers + shared_memory**，而不是继续降 num_workers（降 nw 只是推迟、spawn 才从机制上消除 COW）。

### [运维令] 2026-10-26 22:0x（**S1 吞吐对齐 613,992：先解释 ~480K 的差距，再选方案**）· 用户直令「目标是复现 613,992 基线」· 最高优先

> 用户原话：「pretrain 需要想办法提高S1吞吐，目标是复现 613,992 基线」。
> **实测（ops 中继 RUN_ID 217，S1 当前跑法）**：gbs=128 ⇒ 2,097,152 tok/step；step time **4.09 / 4.87 / 5.20 s** ⇒ **≈400–510K tok/s**，
> 仅为 #792 基线 **613,992 的 65–83%**。#792 基线档 = `seq16384 / mbs1 / gbs256 / accum16 / CP1 / DP16 / FP8 tensorwise / graph OFF / 2 节点 16 卡`。
> 📌 **参数口径（勘误，不要再报错）**：本模型唯一权威 = **2,220,268,032 = 2.220B**（rank 上 `sum(numel())`；P-6 转换 507 tensor keys / 323 HF keys 均逐位一致）。provider 启动打印的「transformer 2.47B + embedding 0.53B = 3.00B」是**把 vocab 嵌入计重的粗糙打印**，2026-10-06 已在 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` §P-3 标注作废。**从来没有 3B 模型**；今后任何报告/心跳引用参数量一律写 2.220B（或 2,220,268,032）。

**请按序给结论（不要一次改一堆参数）**
1. **归因（必须先做）**：用 Megatron timers 或 nsys 抓 step 50–200，给 **per-step 分解**（forward / backward / optimizer / grad-allreduce / dataloader / 空隙）。
   判据：明确说出「613K→480K 的差额主要落在哪一项」——固定每步开销、计算效率、还是通信/数据。
2. **方案三选一并给证据**：
   - **A（最直接，优先验证）**：S1 的 `gbs 128 → 256`（=4,194,304 tok/step，与 #792 E1 完全同档），步数 `700k → 334k`，**总 token 仍 1.4T 不变**。
     预期 ~614K、墙钟不增；须交代「S1 小 batch 阶段」的意图保留还是放弃（+理由）。
   - **B（保持 gbs=128，压固定开销）**：`--overlap-grad-reduce` / `--overlap-param-gather` / `--use-distributed-optimizer` / dataloader workers 数量与 prefetch / NCCL env，
     **一次只改一项**，每项 ≥30 步取稳态，逐项记录（收益/副作用）。
   - **C（折中）**：`gbs=192`（3,145,728 tok/step）测一档，把 2.1M/3.1M/4.2M 三点连成 tok/s 曲线。
3. **红线**：🚫 不许开 CUDA Graph（tok/mb=16384 下会崩到 ~110K）；🚫 tok/mb/GPU 必须 ≤16,384；🚫 FP8 tensorwise 不改；🚫 不许用「更多 token/step」冒充提速（验收看 **tok/s**）。
4. **验收**：稳态（step 50–200 中位数）**≥ 600K tok/s**（≥0.98×613,992）。达不到 ⇒ 给「可行上限 + 结构性原因」的量化结论，并同步改报告 §3 ETA
   （按 480K 算 S1 已从 27.7 天变 **~36 天**，必须让 ETA 不再用 613,992 那一档）。
5. **与 21:3x 令（θ=1e6）同批交付**：θ 未生效（无 `check_rope.py` PASS / 无 provider 打印证据）前，不许起 700k 步正式跑。
6. **附带（阻塞项，先修）**：21:40:43 停机的直接原因是
   `[rank2] RuntimeError: DataLoader worker (pid 3102075) is killed by signal: Killed`
   （主机 2TB 内存 free 1.9TB，但 swap 7G 已满、`dmesg` 无权限）⇒ 请给结论：是 cgroup/单进程上限还是 worker 泄漏；
   建议同时降 `num_workers`（当前 64/节点）并用 `TORCH_DISTRIBUTED_TORCH_TRACE=/tmp/td_trace_%rank` 抓下次失败的 rank traceback（别再出现 `error_file=<N/A>`）。


### [运维令] 2026-10-26 21:3x（**RoPE θ 未生效：请你评估并给出方案，再重启 S1**）· 用户直令「把这个问题跟 pretrain 沟通，让它考虑」· 最高优先

> 用户原话：「把这个问题跟 pretrain 沟通，让它考虑。」
> 这不是命令你照做，而是**把现场证据交给你判断**：请给出你的结论 + 实现选择 + 理由，我们保留否决权。

**一、现场事实（全部来自 ops 中继只读探针，可复核）**
1. S1 确实跑起来过：21:12 起 16 卡（.29 8 + .12 8），**19,049 MiB/卡 · 100% util**；TB 6006 `http=200`；blend 627 shards。`--optimizer adam` ✓ `--lr-decay-style WSD` ✓ `--save-interval 2000` ✓ 无 `--enable-cuda-graph` ✓ `--fp8-recipe tensorwise` ✓（RUN_ID 214）
2. **但实际命令里没有 `--rotary-base`**；`pretrain_launcher.py --help` 无该参数；`mamba2_hybrid_2b/recipe.py` 只有 `apply_rope_fusion`，**没有 `rotary_base`** ⇒ θ 走 Megatron 默认 **1e4**（RUN_ID 215/216）。
3. 21:18:34 **rank 15（.12 / local_rank 7）exitcode=1**，`error_file=<N/A>` 无 traceback；21:22 前后主进程收到 **SIGTERM(15)** 被整体停掉；21:24 16 卡回 4 MiB（RUN_ID 216）。
4. `nemo_experiments/` 里**没有 `baize2b*` 目录/ckpt**，只有 `/tmp/baize_s1_baize2b_smoke*.log` ⇒ 正式 run 的 `--dir` 可能指到 `/tmp`（RUN_ID 215）。
5. blend 跳了 1 片坏 shard：`env14_CC-MAIN-2023-23: ptr overflow max_ptr=122,496,093,768 >= bin_size=49,025,167,172` ⇒ 109/110，权重已摊平。**这是 data 侧问题，你不用改数据**，只需在心跳里记一行。

**二、为什么必须先解决（不能带着跑）**
- θ 是**训练期固定量**，训完不能补；用户 20:1x 令「56 层中 4 层注意力的 RoPE max position = 1M」，落地口径 = `max_pos=1,048,576` + `θ=1e6`。
- 本项目 2026-10-06 B1 实测：**只抬 max_pos 不改 θ ⇒ 全 NaN（连 4K 都 NaN）**；`θ=1e6` 才能从 16K 外推到 1M（PPL 32K/128K/1M = 58.55/53.34/55.42）。
- 即：**现在这套跑法训出来的 ckpt 不具备 1M 能力**，而 1M 是产品目标（用户明确「要不为啥预训练就用 16K 这么长」）。

**三、请你给结论（按这四点回）**
1. **实现路径二选一 + 理由**：
   (i) `mamba2_hybrid_2b/recipe.py::pretrain_config` 增 `rotary_base: int = 1_000_000` 并 `kwargs["rotary_base"]=rotary_base`（改动小、影响该 arch 全配方）；
   (ii) `pretrain_launcher.py` 增 `--rotary-base`（显式可配，但要同时改 CLI 与 provider 透传）。
   请说明你选哪个、对现有其它配方（minicpm5 5e6 / xmodel 5e5）有无副作用。
2. **生效证据怎么给**（任选其一并写进心跳）：① provider 初始化时打印 `transformer_config.rotary_base`；② 导出 HF 后 `python code/baize-llm/scripts/check_rope.py --hf-dir <dir>` **PASS**（56 层 / attention=4 / max_pos=1048576 / θ=1e6 / no scaling）；③ 4K PPL 与 θ=1e4 基线对比。
3. **rank 15 exit1 的定位结论**：不要盲重启。建议加 `TORCH_DISTRIBUTED_TORCH_TRACE=/tmp/td_trace_%rank` 或先**单机 8 卡 50 步**复现；给出你判断的最可能原因。
4. **`--dir` 修正**：ckpt 必须落 `nemo_experiments/baize2b_s1`（用户令 ckpt 每 2000 步）；写进 `/tmp` 会在重启/清理时全丢。

**四、红线**
- 🚫 θ 未验证（无生效证据）不许起 700k 步正式 S1；「能跑起来」不算验收。
- 🚫 不许只改 `max_position_embeddings` 不改 θ。
- 🚫 不许为了让 smoke 过而把 warmup/decay 语义改成与正式不一致（`--lr-decay-shape exponential` 仍缺，Decay 阶段前必须补上并留证据）。

**五、交付**
- 心跳写清：**θ 实现方式 / 生效证据 / rank15 结论 / 重启命令（含 --dir 与 --rotary-base 或 recipe 默认值）**；
- commit 前缀 `pretrain train:`（代码）/ `pretrain run:`（实跑）；**只 add 自己线文件**。

---

### [运维令] 2026-10-28 09:3x（锁定 613K 最佳配置，spawn 调优不许偏离配方；先复跑 smoke 解决真问题）· 用户直令 · 最高优先

> 用户原话（2026-10-28 09:3x）：「跟 pretrain 沟通，让它不要偏离 613K 最佳配置过远，解决真正的问题。」

**① 613K 最佳配置已冻结（#792 E1 实测，不许改）**：16K / CP1 / DP16 / FP8 tensorwise / CUDA Graph **OFF**。613,992 tok/s = 6.831s/step、~38.4K tok/s/GPU。**spawn 调优只许动 DataLoader 侧旋钮（start-method / num_workers / persistent_workers / TORCHINDUCTOR_COMPILE_THREADS），🚫 禁止为「绕过问题」去改 seq / TP / CP / 精度 / 架构 / graph 开关。**

**② 真正的问题（已定位，别跑偏）**：613K(nw=8) → 308K(nw=0) 的差额 ≈ **100% 数据加载串行化**（每步 ≈6.8s 数据 + 6.8s 计算**串行**）。**不是内存、不是 IO、不是 NFS**——#810 前 30 步已证 GPU 100% util、无 data starvation、mmap IO<1%。目标 = **恢复 nw>0 的「数据/计算 overlap」→ 回到 ~613K**。

**③ 本轮运维已就位（勿重复做）**：`.29`/`.12` 均已 `swappiness=0` 且 `swapoff -a && swapon -a` 清掉 7G/6G 残留 swap（现 Swap free≈8G）；#810 OOM 根因已修（`TORCHINDUCTOR_COMPILE_THREADS=4` 已入 train.sh:195，256→32 compile workers，省 ~168GB）。

**④ 下一步（按序，交付才算完）**：① `COMPILE_THREADS=4 + spawn + persistent_workers + nw=4` 重跑 **8 卡 ≥30 步 smoke**，验证 #810 OOM 是否已解 + 吞吐是否 ramp 回 ≥500K；② 定位日志里 **33 leaked 泄漏对象类型**（semaphore / Process / 共享内存？nw=8 长跑唯一没跨过的坎），对症修掉；③ 达标后按 #792 配方重启 S1 全速。

**⑤ 纪律**：盯内存/swap 水位；不碰 vision/data/harness；commit `pretrain perf:`；心跳写 `未完成指令：有` ⇒ `WAITING: 0`，60s 后继续直到 smoke 交付。

---

### [运维令] 2026-10-27 13:1x（杀掉 S1，先调吞吐：立即验证 spawn 方案）· 用户直令 · 最高优先

> 用户原话：「杀掉 S1，如果吞吐上不去一切没意义」

**① 杀掉当前 S1**（nw=0，step≈1080，吞吐 ~320K 不达标）：
- 立即 kill S1 训练（.29 + .12 两机进程），确认 GPU 全释放。
- 当前 ~1080 步**直接丢弃**，不等 step2000（吞吐不达标，继续跑没意义）。

**② 立即做 spawn 方案的真实 GPU smoke**（目标吞吐回 600K+）：
- 用 **spawn + persistent_workers**（必要时 + shared_memory / mmap 索引），nw 从 2 试到 8。
- 8 卡 smoke ≥30 步：验证**免 OOM**（worker RSS 不累积）+ **吞吐回升**（记每变体 tok/s + RSS 曲线 + 是否 OOM，溯源脚本/log）。
- 找到吞吐 ~614K 且不 OOM 的最优组合。

**③ 达标即重启 S1 全速**（用最优配置）；若 spawn 仍不达 600K → **继续 web 调研**（`cimi_search`；若 MCP 工具未生效，先用能用的方式：proxy curl 该接口 / 其他），逐方案 smoke 直到回 600K+ 或给出物理上限。

**④ 纪律**：内存 >95% 告警；不碰 vision/data/harness；commit `pretrain perf:`。

### [运维令] 2026-10-27 10:4x（不放弃：验证 spawn 方案 + 授权 web 调研，吞吐回 600K+）· 用户直令 · 最高优先

> 用户原话：「让 pretrain 不要放弃，自己调用 web search 调研一下，争取吞吐回到 600K 以上。pretrain 已经看到 spawn 方案了对吧，可以开始验证；如果 spawn 方案还是无法恢复吞吐，可以继续调研。」

**① 目标**：S1 吞吐回到 **≥600K**（当前 nw=0 仅 ~308K）。**不放弃，逐方案验证。**

**② 立即验证 spawn 方案（你已知 09:2x 完整方案，按序执行）**：
- **spawn + persistent_workers=True（必要时再加 shared_memory / mmap 索引）**，消 fork-COW 膨胀 → 可 nw>0 → 找回数据/计算重叠 → 目标 ~614K。
- 先 8 卡 **smoke（≥30 步稳态）** 验证：无 worker RSS 累积 OOM + 吞吐回升；PASS 后从当前完好 ckpt（step2000 或现有最新）resume 全速。
- 逐变体记网格：spawn 单改 / spawn+persistent / +shared_memory / nw 档位 → 吞吐 + RSS 曲线 + 是否 OOM，溯源到脚本/log。

**③ 若 spawn 仍不达标 → 继续 web 调研**（授权使用 MCP web 工具 **`cimi_search` / `cimi_fetch`**，已配置给本线）：
- 调研方向：PyTorch DataLoader fork-COW 免膨胀、num_workers×NUMA/swappiness、prefetch_factor、pin_memory、iterator 预取、数据索引 mmap、Megatron 数据加载最佳实践等。
- 每候选同样 smoke + 记录收益，直到吞吐回 600K+ 或给出「当前物理上限 + 需要什么硬性条件」。

**④ 纪律**：进度写 EXPERIMENTS §五 + 报告吞吐节；commit `pretrain perf:`；⚠️ 内存 >95% 告警（08:4x 提示）；不碰 vision/data/harness。

## 归档 2026-10-28（由 BAIZE_PRETRAIN_2B_TASK.md 搬入，原文未改）

### [运维令] 2026-10-28 11:5x（**写 blend 逻辑中文 HTML 报告 · 澄清「训练时是否串行出不同源」**）· 用户直令 · 最高优先

> 用户问（2026-10-28 11:5x）：「blend 的逻辑是怎样的？请 pretrain 写个中文 HTML 报告。我不会是训练时也是串行出不同源的数据吧？」

**① 报告必须讲清 Megatron blend 的「索引层」逻辑**：
- `BlendedDataset._build_indices()` 产出两个数组——`dataset_index`（每个样本取哪个数据集）+ `dataset_sample_index`（取该数据集第几条样本），一次性构建并缓存 `.npy`。
- `helpers.build_blending_indices`（C++，**最大误差交错 / Bresenham 式加权分配**）：对每个样本位置取 `argmax_i(weight[i]×n − 已采样[i])`，保证 7 源按 `blend_s1.tsv` 权重（0.65/0.15/0.05/0.05/0.04/0.04/0.02）**均匀交错**，每源采样误差 ≤1。
- 训练时 DataLoader **按序消费这个已混合好的统一索引**——不存在「读完源 A 再读源 B」。

**② 直接回答用户核心疑问**：**训练时不会「串行出不同源」**。每个 global batch（128 样本）内已按权重**交错**包含 7 源数据；此前 308K 的「串行」只发生在 **nw=0 时「数据准备 vs GPU compute」这一层**（每步 ≈6.8s 数据 + 6.8s 计算串行），与「源 vs 源」无关。`pre-blend`（物理合并 628→~100 大 shard）与 `blend`（索引交错）是**正交两层**：pre-blend 只减 shard 数、**不改权重、不改交错**。

**③ 交付**：`doc/BaiZe-ISEDA2027/reports/report_pretrain_blend_logic_zh.html`（0 script / 0 外链 / 标签配平）；正文含一个权重 0.65/0.35 的具体交错序列示例 + 训练时数据流（索引→取样本→组 batch→compute）的示意图/文字说明。commit `pretrain 报告:`。**优先级：该报告独立于 pre-blend 进行，不影响 10:0x 计划的 pre-blend/S 起跑主线。**

---

### [运维令] 2026-10-29 14:1x（**整理并提交 baize-llm 独立仓库**）· 用户直令 · 最高优先 — ✅ 已完成 (#890)

> 用户原话（2026-10-29 14:1x）：「请 pretrain 把 baize-llm 这个仓库整理提交一下」

**① 现状（运维已核）**：
- `/nas_train/app.e0031982/code/baize-llm/` 是**独立 git 仓库**，remote = `ssh://git@devops.cxmt.com:8022/git/AIX/PAI/eda/baize-llm.git`，当前只有 `Initial commit`；`README.md` 是 582B 的**空模板**（「请介绍一下你的项目吧」）；工作树里还有一个**未跟踪的 symlink** `baize-llm -> super_intelligence_2035/code/baize-llm`（`git status` 显示 `?? baize-llm`）。
- 真实代码（`configs/` 10 个、`scripts/` 18 个、`docs/` 2 个、`README.md` 19.6KB）全在**主仓库** `super_intelligence_2035/code/baize-llm/` 下，已随主仓库持续提交（最近 `281384228 pretrain train`）。

**② 要求（整理 + 提交，按序）**：
1. **补全独立仓库 README.md**：把 582B 空模板替换为真实项目说明（项目定位 / 目录结构 / 三阶段 S→S2→Decay 口径 / 启动命令 `bash scripts/train.sh <stage>` / 配置说明 / 依赖环境），与主仓库 `code/baize-llm/README.md`（19.6KB）口径一致、可照做。
2. **把真实代码纳入独立仓库**：将 `configs/`、`scripts/`、`docs/`（去 `__pycache__`、`.pyc`）整理进独立仓库工作树，`git add` 后 `git commit`（commit 信息带 `pretrain 项目:` 前缀）。
3. **push 到 origin/devops**：`git push origin master`（若 push 失败带代理重试：`https_proxy=$P http_proxy=$P git push origin master`），确认 devops `baize-llm.git` 上已可见完整代码。
4. **symlink 处置**：那个未跟踪的 `baize-llm` symlink 要么纳入 `.gitignore`、要么删除，🚫 不许把 symlink 当真实文件提交。

**③ 判据**：`git -C /nas_train/app.e0031982/code/baize-llm status` 干净；`git -C ... log --oneline` 最新提交为本轮；`git -C ... push` 后 `git ls-remote origin` 可见新 commit；README 非空模板。

**④ 纪律**：不打断 S1 主线（iter 9600+ 在跑，纯 git/文件整理零 GPU）；不碰 vision/data/harness；心跳写 `未完成指令：有` ⇒ `WAITING: 0` 直到 push 成功；只提交 baize-llm 独立仓库相关文件。

**✅ 完成结论（#890, 2026-10-29 14:35）**：commit `e1c6be4` pushed to origin/master。28 files: README.md 582B→19.6KB, configs/(9), scripts/(18, 去__pycache__/.pyc), docs/(2), .gitignore(排除 symlink/__pycache__/.nfs*)。symlink 已删除+纳入 .gitignore。git ls-remote origin master = e1c6be49 匹配。S1 主线未受影响。

---

### [运维提示] 2026-10-27 15:2x（**cimi MCP web search 已配好，可用于调研**）· 用户直令 · 最高优先 — ✅ 已归档

> 用户原话：「可以提醒 pretrain 可以 web search（cimi search）」
> **本线 MCP 工具已就绪**：`cimi_search`（web 搜索）/ `cimi_fetch`（抓网页全文）/ `vqa` / `text_to_image`（cline MCP，type=streamableHttp，指向 `http://10.239.2.29:8092/mcp`）。下一轮唤醒（新 cline 进程）即生效。
> **排查/调研时直接用 `cimi_search`**——查 fork-COW 免 OOM、16K 吞吐优化、DataLoader 最佳实践等。🚫 别再只依赖 fetch_web_content 或被 proxy 卡住。

**✅ 归档结论**：MCP 工具已就绪并持续可用，授权永久有效。需要时直接用 cimi_search/cimi_fetch。

---

### [运维提示] 2026-10-27 08:4x（**内存使用率 >95% 会触发告警，调试时注意**）· 用户直令 · 最高优先 — ✅ 已归档

> 用户原话：「告诉 pretrain 内存使用率>95%会导致告警，让它调试时注意。」
> 刚从 #802/#803 的 DataLoader OOM（.29 swap 耗尽 → SIGKILL）时也印证：调试/测吞吐务必盯 **内存 + swap**，避免把内存打到 >95% 触发告警。措施：num_workers 节制、并发/预留窗口适度、及时释放不再用的进程/张量；若逼近 95% 先降载并上报，不要硬顶。

**✅ 归档结论**：内存纪律已纳入日常监控，当前 .29 内存 719G/2TB(36%) swap 正常，无告警风险。

