# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_PRETRAIN_2B.md` / `daily-memories/` / `EXPERIMENTS_*`）。本节为「无」时按下方 Round 2 默认顺序推进。

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

### 📉 记忆维护规程（2026-10-03 运维新增，**硬性**）
> 理由：`MEMORY_*.md` **每次唤醒都被 agent 全文读取** → 越大越烧 token。当前 `MEMORY_PRETRAIN_2B.md` ≈ **243KB（严重超标）**。
- **上限**：本线 `MEMORY_PRETRAIN_2B.md` 控制在 **≤ 32KB**；**下次唤醒立即执行一次滚动归档**。
- **滚动**：把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 最近 ~20 条流水。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变（正文/流水/快照里**不得**再出现以 `WAITING:` 开头的行）。

---



# ══════════════ ROUND 2 · **现行部分**（只保留仍未完成/仍有效的）══════════════

> R2.0/R2.1/R2.2 清单 · R9.0-bis · P-4R · P-5a 与 **Round 1（S0–S5）** 均已**完成并归档** →
> **`run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md`**（**需要时再去读，不要把整份读进上下文**）。

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

**P-6 细节 —— lm_eval 评测（第 1 步：8 集零样本摸底；第 2 步：**scaling law 曲线 + 外推**）**

> **目的**：Stage (i) 的定位是**通用模型**，**本任务不做 EDA-Eval**。
> 唯一目标是**摸底训练效果**——让 Stage (i) 的结论**不只是 loss 数字**。
>
> **口径严格对齐 Xmodel-2 论文**（`doc/BaiZe-ISEDA2027/Xmodel-2/xmodel-2.tex:198,207`）：
> - Harness：**EleutherAI Language Model Evaluation Harness（lm-eval）**
> - **zero-shot**、**raw accuracy**
> - **8 个评测集**（与 Table 2 的 8 列一致），另报 **Avg**：
>   `ARC-Challenge` · `ARC-Easy` · `BoolQ` · `HellaSwag` · `OpenBookQA` · `PiQA` · `SciQ` · `Winogrande`
> - ⚠️ 论文正文还提到 **TriviaQA**，但 **Table 2 里没有这一列** → **以表为准，只跑这 8 个**，并在报告里注明此差异。

**第 1 步（最便宜，先做）：评测现有的 20000 步 checkpoint**
- 它就是 Stage (i) 的最终产物；**先拿到它的 8 集分数**，立刻就有"摸底"数据。

**第 2 步（最有价值）⭐ —— 与 P-5b 结合 → 「能力 vs token」<u>scaling law 曲线 + 外推</u>**

> ## 🎯 运维 2026-10-02 明确要求
> 「**希望画出 scaling law 曲线，估计常识推理 8 任务和复杂推理 6 任务要达到更高的水平需要多少训练数据。**」
>
> **两条口径澄清（运维 2026-10-02，务必照做）**：
> 1. 🔧 **全部走 `lm_eval`，<u>不要换框架</u>** ——
>    Xmodel-2 是 **2 年前的论文**，当年 HumanEval/MBPP 要另配 `bigcode-evaluation-harness`；
>    **现在 `lm_eval` 已原生支持**，**无需引入第二套框架**。
> 2. 🔢 **n-shot 的 n 就用 `lm_eval` 的<u>默认值</u>** ——
>    **不必**去对齐 Xmodel-2 的 5/4/3/0-shot。

### (1) 数据点：P-5b 的 6 个 checkpoint
在 **655M / 1.3B / 2.6B / 5.2B / 10.5B / 20B token** 各跑一遍**下面两套**评测。

### (2) 两套指标（**都用 `lm_eval`**，n-shot 用默认值）

| 集 | 任务 | 说明 |
|:--|:--|:--|
| **常识推理（8）** | `ARC-C` `ARC-E` `BoolQ` `HellaSwag` `OpenBookQA` `PiQA` `SciQ` `Winogrande` | 与 **P-6 第 1 步同一套**（已跑通，Avg **0.4395**）→ **直接可比** |
| **复杂推理（6）** | `GSM8K` `MATH` `BBH` `MMLU` `HumanEval` `MBPP` | **`lm_eval` 原生支持全部 6 个**；⚠️ HumanEval/MBPP **需代码执行**（`lm_eval` 自带沙箱，按其文档开执行开关即可，**不要另起框架**）|

- ⚠️ **论文正文提到 TriviaQA 但 Table 2 表里没有** → **以表为准**（8 个），报告注明。
- ⚠️ **报绝对值时要标 harness 版本与 shot 数**（因为与 Xmodel-2 的口径不同）。

### (3) ⭐ **参照线**（Xmodel-2 论文的公开数值，供"更高水平"定位）

> ⚠️ **口径不可严格比**（shot 数、harness 版本、模型规模均不同）→ **只作"量级参照"，必须标注**。

**常识推理 Avg（zero-shot）：**
| 模型 | Avg |
|:--|--:|
| TinyLLaMA1.1-1.1B | 55.24 |
| Llama-3.2-1B | 57.70 |
| OpenELM-1.1B | 56.95 |
| MiniCPM-1.2B | 59.45 |
| **Xmodel-2-1.2B** | **61.79** ← 同类论文直接对标 |
| Qwen2.5-1.5B | 63.14 |
| Phi-1.5-1.3B | **65.68** ← 强标杆 |

**我们起点**：**P-6 第 1 步已测 Avg = 0.4395（43.95%）** @ 20k 步 / **655M token**。
→ **距最弱的 1B 级（55.24）差 11.3 个点；距 Xmodel-2-1.2B（61.79）差 17.8 个点。**

**复杂推理 Avg：**
| 模型 | GSM8K | MATH | BBH | MMLU | HE | MBPP | **Avg** |
|:--|--:|--:|--:|--:|--:|--:|--:|
| OpenELM-1.1B | 0.45 | 1.06 | 6.62 | 25.52 | 8.54 | 6.80 | **8.16** |
| OLMo-1B | 2.35 | 1.46 | 25.60 | 24.46 | 5.49 | 0.20 | **9.93** |
| TinyLLaMA1.1-1.1B | 2.50 | 1.48 | 25.57 | 25.35 | 1.83 | 3.40 | **10.02** |

> 🚨 **预期校准（必须写进报告）**：**1B 级模型在这 6 个任务上基本贴地板** ——
> GSM8K **0.45–2.5%**、MATH **~1%**、MMLU **~25%（≈chance）**、BBH **~25%（≈chance）**。
> → **我们 2.2B / ≤20B token 跑出来很可能<u>全程贴地板</u>**。
> **若确实全程贴地板 → 「量不出斜率」本身就是结论**（说明复杂推理在**更晚**才涌现，
> 需要远超 20B 的训练量）—— **如实写，不要硬拟合**。

### (4) ⭐⭐ **画 scaling law 曲线**

- **x 轴：训练 token（log 轴）**；**y 轴：各集分数 + Avg**。
- **常识 8 集**：画 **1 张图**（8 条细线 + **Avg 粗线**），**叠加上述参照线**（虚线）。
- **复杂 6 集**：同一格式；若贴地板就**如实呈现**。
- **拟合**：对 **常识 Avg** 拟合幂律 `acc = a − b·N^(−c)` 或对数 `acc = a + b·log10(N)`，**报 R²**。
- **同时记** loss / grad norm / img/s，以对照"loss 曲线"与"能力曲线"的**不同饱和点**。

### (5) ⭐⭐ **外推**（决策价值所在）

1. 用拟合曲线外推：**常识 Avg 达到 50% / 55% / 60% 各需要多少训练 token？**
2. **对照我们的算力**：按实测 ~83K tok/s（P-7 修正后），
   **这些 token 预算分别要跑多少天**（8×H100）？
3. **一句话结论**：
   - 若在**可接受的天数内**可达 → 给"**需 X 万亿 token / Y 天**"，直接作为 **P-8 的 token 预算依据**
   - 若**远超可承受范围** → 明确写"**在当前算力窗口内达不到 55%（或 60%）**"
4. **如实报外推不确定性**（**用 ≤6 个点外推**，且我们处在曲线**陡升段**，误差会很大）。



**执行路径（⚠️ 以你们**自己已查证过的结论**为准，不要另起炉灶）**

> 你们在 **2026-09-29** 已经查清过这条路
> （`run/daily-memories/2026-09-29.md:201,207,223` 与 `run/BAIZE_2B_ARCH_SEARCH_TASK.md:218`）：
> - **既定路径就是「ckpt → HF → SGLang 起服」**；当时的阻碍只是 **vLLM（`_C.abi3.so` 崩）与 `sglang`（未装）**，
>   于是退到 mcore 直驱，并明确注明那是**下界测量**（"如需精确 decode 数后续 SGLang 起服复核"）。
> - 那次也写明：**真正的坑是「mcore 分布式 ckpt → HF 格式转换」**（无现成 bridge，需把
>   `NVIDIAMambaHybridModelProvider2B` 权重映射到 **Nemotron-H / Llama HF 结构** + DeepSeek tokenizer）；
>   **mcore 手写前向只是 fallback**。
> - **SGLang 原生支持 `nemotron_h`**（`--mamba-ssm-dtype float32` / `--mamba-full-memory-ratio`）——
>   这正是当初选 SGLang 的原因。

**推荐路径（标准做法；不需要写自定义 lm_eval model 类）**

1. **转 HF**：mcore 分布式 ckpt → **Nemotron-H HF 结构**（含 DeepSeek-V4.1-Flash tokenizer）。
2. **SGLang 起服**（若 `sglang` 未装，先 `pip install sglang`）：
   `python -m sglang.launch_server --model-path <hf> --port 30000 --mamba-ssm-dtype float32 --mamba-full-memory-ratio <按需>`
3. **lm_eval 用内置模型类型直连，无需改接口**：
   `lm_eval --model local-completions --model_args base_url=http://localhost:30000/v1,model=<name>,tokenizer=<hf> --tasks arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande --num_fewshot 0`
   （`local-completions` / `local-chat-completions` 可接**任何 OpenAI 兼容服务**——这是标准用法。）

**⚠️ 先验证一件事（成败所系，第一步就做）**
这 8 个任务里 **7 个是 multiple-choice**，lm_eval 的 `local-completions` 靠 **`loglikelihood`** 打分，
即需要服务端在 `/v1/completions` 上支持 **`echo=True` 且返回 prompt 的 `logprobs`**。
→ **先用一个最小请求验证这一点**；若不支持，再考虑 `local-chat-completions`，
**最后**才回退到自定义 model 类包 mcore 前向。

**时间盒**：转换 + 起服 **≤ 2 小时**；超时就记录卡点并转 fallback，不要无限调试。

**产出**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加一节；
并给出**论文回填建议**（§4 是否加一张"通用能力零样本"表）。

**P-7 细节 —— 训练吞吐幅度核查（P-3 的补充，**必须查明**）**

> **问题**：论文 `tab:archcomp` 写 **dense 89K vs hybrid 72K（dense +24%）**；
> 而 **P-3 在同一口径下**（6 卡 / TP1/DP6 / GBS=6 / seq 4096）实测
> **dense 89.7K vs hybrid 85.6K（dense 仅 +4.8%）**。
> - dense 侧几乎一致（89K → 89.7K）✅
> - **是 hybrid 从 72K 涨到 85.6K（+19%）**，即 ms/iter 由 ~340 降到 ~287。
>
> **为什么必须查明**：**训练吞吐代价是 hybrid 论证里唯一的「成本侧」数字**。
> 若真值接近 +5% 而非 +24%，hybrid 的性价比论证会**明显更强**；
> 反之若是 Round 1 的测量本身有问题，论文里那个 `+24%` 就**站不住**。两种情况都直接决定 `tab:archcomp` 怎么写。

**要做的核查**
1. **先算一笔账**：Round 1 是 **1000 步**短跑；若把 SSM 首步编译开销（记录中的 **~12.3s**）摊进平均，
   相对稳态只抬高约 **3.6%**（12.3s ÷ (1000 × 0.34s)）——**不足以解释 340ms → 287ms 的 16%**。
   → 因此**一定还有别的原因**，继续查。
2. **比对两次测量的差异项**：micro-batch / gradient-accumulation 设置、`--recompute` 档位、并行度、
   mcore / `transformer_engine` / 容器版本、以及**当时的集群争用状态**——是同一套配置吗？**逐项列出**。
3. **在同一环境、同一配置下重测一遍** hybrid 与 dense 的**稳态** ms/iter（各 ≥300 步，**剔除首步**），
   得到可复现的干净数字；记录 **GPU 独占核验原文**（沿用 R2-4 做法）。
4. **给结论**：`tab:archcomp` 的 "Training tok/s" 一列应写**哪两个值**、差距**百分之几**；
   并说明 Round 1 的 72K 究竟属于「含首步开销的短跑均值」还是「另一环境下的值」。

**产出**：写入 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 的 P-3 节 + 更新「论文回填建议」，
明确指出 `tab:archcomp` 该改成什么。**时间盒 ≤1h。**

**P-8 细节 —— 🏁 Stage (i) 完整训练（正式预训练）**

> ## ⏸ **运维 2026-10-02 指令：P-8 暂缓启动**
>
> **原话**：「**测数据配比需要时间，下载 base 也需要时间…因此 P-8 暂缓启动，先做配比实验和下载 base。**」
>
> **原因（两条前置都未就绪）**：
> 1. **`Ultra-FineWeb`(base) 还在下载**（115/64624，2.99 TB）—— 而它是 **stable 段的主力数据**；
> 2. **WSD 双阶段配比实验还没做**（见 `BAIZE_DATA_TASK.md` §0.6）—— **P-8 吃什么配比是它要定的**。
>
> **→ 所以：不要因为"P-5b 快跑完了"就顺手启动 P-8。** 前置未齐之前，P-8 不启动。
> **→ 本唤醒及后续唤醒：做完 P-4R / 恢复 P-5b 之后，仍然等 data agent 的配比方案 + base 就绪。**

> ## 🎯 这是 Stage (i) 的**本体**
> **Stage (i) 的 scope 不变 = LLM 预训练（from scratch）。**
> P-1…P-7 全部只是**前置选型实验**（token 量级 164M–655M，合计 ~85 GPU·h）。
> **P-8 才是真正把 2.22B hybrid 训出来**，作为 Stage (ii)–(v) 的基座。
> 🚫 **不要**因为"实验都做完了"就把 Stage (i) 标成完成。

**输入（全部来自前序任务，不要自行改动）**

| 项 | 来自 |
|:--|:--|
| **GBS** | P-5a 的 GBS×LR 扫描结论（若无右移则沿用 GBS=8；若 P-5a 指向更优大 GBS 则采用并注明） |
| **LR / 调度 / 退火配比** | Round 1 胜出配置（LR 1e-3 / WSD / warmup 250 / decay 500 / min_lr 1e-5 / L3(86%)+code(10%)+math(4%)）；若 P-5a 给出新 LR 则改用并注明 |
| **token 预算** | ⭐ **由 P-5b 的 loss-vs-tokens 曲线决定**（曲线何时变平 → 就在那附近取预算） |
| **精度** | 若 P-4 证明 FP8 对本架构确有加速且**不劣化 loss**，可用 FP8；否则 bf16。**必须记录采用与否及理由** |

**token 预算的三档参照（按实测吞吐 8×H100 ≈ 92.6K tok/s 折算）**

| 档位 | token | 墙钟 | GPU·h | 说明 |
|:--|:--|:--|:--|:--|
| **下限** | **44 B** | **≈5.5 天** | ≈1056 | Chinchilla 最优（2.22B × 20）。**低于此不足以称为"训练好的模型"** |
| **推荐** | **100 B** | **≈12.5 天** | ≈2400 | 超 Chinchilla ≈2.3×；契合论文**推理效率**卖点（推理最优需过训练） |
| **上限** | 200 B | ≈25 天 | ≈4800 | 仅在预算与时间都宽裕时 |
| ⚠️ 不计入 | 690 B（真实全语料） | **≈86 天** | ≈16560 | **2027-02-01 前不可能** + `/nas_train` 只剩 32T，**不要定这个档** |

> **默认按「推荐档 100B」准备**；**P-5b 曲线出来后，若曲线在更早处变平，就下调**（省钱省时）。
> ⚠️ **最终 token 预算定下后，必须在 `MEMORY_PRETRAIN_2B.md` 里写明并上报**，再启动长跑。

**训练要求**

1. **从零开始**（不加载任何预训练权重），**真实语料**（`Ultra-FineWeb-L3` 全量 en 子集 + code + math 退火配比），
   **不是** `ultrafineweb_l3_qa_700m` 那个 742M 小分片 —— **本次必须跑真正的全量语料**。
2. **WSD 完整走完**：warmup 250 → stable → **decay 尾段必须真的吃到退火混合**（这是 Stage (i) 的核心配方之一）。
3. **checkpoint 规划**：至少保留 `final` + **每 10% 一个**（供 Stage (ii) 选起点、供 P-6 画能力曲线）。
   ⚠️ 每个 ckpt（2.22B 含 AdamW 状态）≈ **~30 GB**；**`/nas_train` 只剩 32T**，先算好 ckpt 留存策略与清理时机。
4. **训练中每 500 步**记 `train loss` / `val loss` / `grad norm` / `tok/s` / **GPU 独占核验**。
5. **禁止在 P-8 期间叠加其它重 I/O 或抢卡任务**（vision / data 侧要避让）。
6. **失败即如实记录**：NaN / 发散 / OOM 一律记录**并保留当时的 ckpt 与日志**，不要静默重启掩盖。

**产出**

1. **Stage (i) 最终 checkpoint**（Stage (ii)–(v) 的基座）—— 这是本项目**最关键的单个产物**。
2. `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加 **P-8 节**：完整 loss 曲线、实际 token 数、实际 GPU·h、
   最终 `val loss`、与 P-5b 曲线预测值的对照（**预测量 vs 实测量**，这是对 scaling 曲线的一次真检验）。
3. **论文回填建议**：§4 应写清 **实际训练 token 数 / GPU·h / 最终 loss**，
   把"从零训练一个 2.22B hybrid"的**规模与代价如实写出来**（并处理 §6 #13 的 1.8T 误读问题）。
4. `BAIZE_PRETRAIN_RESULT.html` 更新为**含 P-8 的最终版**。
5. git commit + push（**只提交文本**；checkpoint 不入库）。

**时间盒**：**下限 5.5 天 / 推荐 12.5 天**（按 token 预算）。**超时或连续失败不要硬撑**，
记录卡点并上报 —— 但**除非运维叫停，P-8 应跑到底**。


## R2.3 交付物

1. **`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`**（新文件）：P-1/P-2/P-3 全部结果表 +
   每条可复现命令 + 与 Round 1 的差异说明 + **「论文回填建议」段落**（给出精确数值与文字建议，
   特别是「最优点是否在边界」「Δ 是否在噪声内」这两个结论该怎么写）。
2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_PRETRAIN_RESULT.html` 或新建 `BAIZE_PRETRAIN_RESULT_ROUND2.html`（自包含）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` 与 `main.tex`——
   论文已由外部统一重构并推送，回填由外部完成。你只在报告里给「回填建议」。
4. 正常更新 `MEMORY_PRETRAIN_2B.md` 与 `daily-memories/`。
5. **git commit + push，并严格走本文件顶部的「git 同步规则」**（fetch → 必要时 `pull --rebase` → push → 确认 0/0）。

## R2.4 约束

- **总预算**（分三档）：
  - **P-1 / P-2 / P-3 / P-4 / P-6 / P-7**：短程实验，≤ 5 小时墙钟（P-6 视加载路径难度可到 6 h；P-7 ≤1h）。
  - ⭐ **P-5 是独立长任务，≤ 8 天墙钟**（P-5a 4–5 h + P-5b 20B token ≈ 2.5 天；预算允许可延到 60B ≈ 7.5 天）。
  - 超时按 **P-5a > P-6 第 1 步（现有 ckpt 的 8 集）> P-1/P-2 > P-4 > P-5b > P-6 第 2 步** 逆序裁剪，并在报告记录裁剪决策。
- **GPU**：只用 `10.239.2.29` 的 **GPU 0–7**（8 卡）。**绝不杀他人进程**。
  ⚠️ 另有 vision 任务在 **`10.239.2.12`**（另一台机器）跑——**与你无关，不要去动那台**。
- **每次启动训练前后都要记录 GPU 占用核验结果**（`nvidia-smi --query-compute-apps=...`）。
- ⚠️ **NFS 与 vision 任务共享（重要）**：两台 GPU 节点用的是**同一块 `/nas_train` 盘**。
  vision 任务的 **R2-4 需要"无争用的干净吞吐测量"**，而你启动训练同样会打这块盘。
  → **启动 P-1 之前**，先读 `run/MEMORY_VISION.md`（共享盘，你直接可见）看它的 R2 进度：
  - 若 **R2-4 尚未完成**：先做**不占 GPU** 的准备工作（代码/数据核对、P-3 的 Round 1 基线复核、脚本落地），
    **每轮唤醒重查一次**它的进度；
  - **最多等 2 小时**；超过 2 小时则照常启动 P-1，并在报告里注明"当时 vision 任务在并发"。
  → 你的**每次测量都要记录"当时 vision 任务在跑什么"**。
- 数据：P-1/P-2 沿用现有 200k docs / 165M token 即可（5000 步 ≈ 164M）；
  **P-3 若需更长的数据覆盖，先核对再启动**，不要中途断数据。
- **收尾不杀 loop（关键）**：R2 的 P-1/P-2/P-3 全部完成（或按预算裁剪到只剩需等待的项）后，把结果写进报告并 git push，然后**停在原地**：`MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（30 分钟长轮询）；🚫 **绝不 kill / pkill `baize_pretrain_loop.sh`**。loop 必须持续运行，以便运维远程下发新任务（会改写本任务书，下次唤醒即按新指令执行）。

---



> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 **BaiZe Stage(i) LLM 预训练**（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

## ⚠️ git 同步规则（**必读，2026-10-01 新增，每次唤醒都要走**）

### 前提：这是一个**共享工作副本**

vision 任务的 agent 与本任务**共用同一份工作副本**——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

**因此：**
- **只需一个人 pull，另一个立刻看到**：vision agent 拉取后，你读到的 `$TASK_MD` 与所有文件都会同步更新。
  **不要重复 pull**，也不要因为"工作区里出现了别的任务的改动"而困惑。
- 工作区里**陌生的未提交改动很可能是 vision 任务的在途文件**。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。
- 两个 loop 每 5 小时各自 `git add -A && commit && push`，**会互相把对方在途的文件一起提交**。
  这是既有设计的已知副作用，**不要试图"修正"它**。

### 但 loop 本身**只 push 不 pull**

`baize_pretrain_loop.sh` 的 `git_push_if_needed()` 只做 `add → commit → push`。
一旦远端被别人推进，它的 push 会 `! [rejected] (fetch first)` 失败、每 5 小时重试一次、永远失败。
**所以 pull 必须由你（agent）来做。**

**每次唤醒按顺序执行：**

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. **提交时显式指定你自己的文件**：
   `git add MEMORY_PRETRAIN_2B.md EXPERIMENTS_PRETRAIN_2B_ROUND2.md daily-memories/`
   🚫 **不要用 `git add -A`**——那会把 vision 任务的在途文件卷进你的提交。
3. 若显示 **behind / diverged**：`git pull --rebase origin main`。
   - 报 `cannot rebase: You have unstaged changes` → 是**双方的在途改动**：
     先把你自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。
   - 报 `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：
     等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并**跳过本次 git 操作**，下次唤醒再试。
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` **无 ahead/behind** 才算闭环。
5. 流水记一行 git 结果（沿用你已有格式）。

> 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式
> `git pull --rebase` 合并远端后 push 成功——**沿用同一做法**。

---


---

