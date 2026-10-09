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

