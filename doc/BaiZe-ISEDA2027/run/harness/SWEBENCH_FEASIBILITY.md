# H-A SWE-bench 横评 —— §1.1 可行性核查报告

> 依据 `BAIZE_HARNESS_TASK.md` §1.1 / §1.1-bis。**每条结论 = 命令 + 可复现输出**。
> 核查时间：2026-10-02 · 主机：`whag0pgpuap29`（= 10.239.2.29，**pretrain R2 训练所在机**）
> 结论：✅ 连通性/模型/数据集大多可用；❌ **Docker 无权限（阻塞官方口径）**；**Route E′（无 Docker）技术可行**，但需运维拍板两件事（见 §4）。

---

## 1. 连通性实测（§1.1-bis 清单，逐条贴原始输出）

### A. GitHub git 通道 —— ✅ 可用
```bash
timeout 20 git ls-remote https://github.com/SWE-bench/SWE-bench.git HEAD
# → 02e7a74ffd0b707aab73d203fe87bdc7c76afc8e	HEAD
```

### B. 依赖源 —— ⚠️ 官方 pypi 不通，**但内网镜像通（✅）**
```bash
# 官方源（直连）：
https://pypi.org/simple/          : 000   ❌
https://files.pythonhosted.org/   : 000   ❌
# pip 实际配置（内网镜像）：
pip config list
# → global.index-url='https://mirrors.aliyun.com/pypi/simple/'
#   global.trusted-host='mirrors.aliyun.com'
#   global.timeout='120'
# 内网镜像实测：
curl -sS -m 10 -o /dev/null -w '%{http_code}\n' https://mirrors.aliyun.com/pypi/simple/
# → 200   ✅
```
→ **装依赖走 aliyun 内网镜像，完全可行。**

### C. Docker —— ❌ **守护进程 running，但当前用户无 socket 权限**
```bash
which docker dockerd       # → /usr/bin/docker  /usr/bin/dockerd   （CLI 存在）
systemctl is-active docker # → active                                （守护进程在跑）
id                          # → uid=6218(app.e0031982) gid=6002(app.adm)  ← **不在 docker 组**
ls -la /var/run/docker.sock # → srw-rw---- 1 root docker            （root:docker，0640）
docker info                 # → permission denied while connecting to the Docker daemon socket
sudo -n -l                  # → sudo: a password is required        ← **无免密 sudo**
docker pull hello-world     # → permission denied (dial unix /var/run/docker.sock ...)
```
```bash
# 镜像仓库可达性：
curl ... https://registry-1.docker.io/v2/  # → 401   （可达，需鉴权，不是不可达）
curl ... https://ghcr.io/v2/               # → 000   （不可达）
# /etc/docker/daemon.json 里 **没有 registry-mirrors**（只有 data-root/runtime/storage-driver）
```
→ **关键更正**：RUN_ID 5 记录「docker 不可用」实为**权限问题**（守护进程在跑、socket 是 `root:docker`），
**不是没装 docker**。当前用户 `app.e0031982` **不在 `docker` 组**、无 sudo。
**解除方式 = 运维执行 `usermod -aG docker app.e0031982`**（需重登生效），否则我这边无法用 docker。

### D. SWE-bench 云（sb-cli 命门）—— ❌ 不可达
```bash
https://api.swebench.com/   : 000
https://www.swebench.com/   : 000
```
→ **sb-cli 路线不可行**（云不可达 + §1.1 已标合规红线：predictions.json 上传外部服务需运维/合规批准）。

---

## 2. §1.1 六项核查表

| # | 查什么 | 结果 |
|:--|:--|:--|
| 1 | 有哪些 harness / 形态 | 5 个，**全是 CLI 工具**：`@cline/cli`（apps/cli）、`@opencode-ai/cli`、`@openai/codex`（codex-cli）、`@deepseek-ai/dsh`（apps/cli，含 landlock 沙盒 addon）、`claude-code`（泄漏源码，见 H-B） |
| 2 | 怎么启动 / 接什么模型 | 均 OpenAI 兼容接口（读 `OPENAI_API_URL` 等环境变量） |
| 3 | 模型可用性 | ✅ **内网网关** `http://agi-gateway.cxmt.com/v1`，模型 `deepseek-v4-flash`（vllm-0.28.0-tp8-ep 后端）；最小调用 **HTTP 200**（见下） |
| 4 | SWE-bench 数据集 | ✅ HF 可达（`huggingface.co`/`hf-mirror.com` 均 200）；`datasets==4.8.4` 已装；`swebench` 包**未装**（可 pip 装）；**SWE-bench_Lite/test = 300 条已实测拉取** |
| 5 | 评测容器/沙箱 | ❌ **Docker 无权限**（见 §1-C）；需走 §1.1-bis 无 Docker 路线 E′ |
| 6 | 磁盘/时长 | ✅ `/data` 剩 6.5T、`/nas_train` 剩 31T；但 **本机 .29 是 pretrain 训练机（I/O 冲突，见 §4）** |

### 模型最小调用实测（§1.1 第 3 项）
```bash
curl -sS -m 30 -w 'HTTP %{http_code}\n' "$OPENAI_API_URL/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"'"$MODEL_VERSION"'","messages":[{"role":"user","content":"ping"}],"max_tokens":8}'
# → HTTP 200
#   {"model":"deepseek-v4-flash","choices":[{"message":{"content":null,...,"reasoning":"..."}}],
#    "system_fingerprint":"vllm-0.28.0-tp8-ep-ca389c44", ...}
```
⚠️ **注意**：`deepseek-v4-flash` 是 **reasoning 模型**—— `max_tokens` 很小时回的是 `message.reasoning`（`content:null`），
harness 需按 reasoning 模型接口取 final content（`reasoning` 单独字段）。评测时要给足 `max_tokens`。

### SWE-bench_Lite (test / 300 条) repo 分布（Route E′ 挑库依据）
| repo | 数量 | 占比 | | repo | 数量 | 占比 |
|:--|--:|--:|:--|:--|--:|--:|
| **django** | 114 | 38% | | requests | 6 | 2% |
| **sympy** | 77 | 26% | | pylint | 6 | 2% |
| matplotlib | 23 | 8% | | xarray | 5 | 2% |
| scikit-learn | 23 | 8% | | seaborn | 4 | 1% |
| pytest | 17 | 6% | | flask | 3 | 1% |
| sphinx | 16 | 5% | | astropy | 6 | 2% |
→ **django(114) + sympy(77) = 191/300 = 64%**。Route E′ 按任务书建议挑 **django / sympy**（+可选 matplotlib/sklearn）。

---

## 3. 路线判定（任务书「连通性之后据此执行」的表）

| 路线 | 判定 | 依据 |
|:--|:--|:--|
| 原路（docker） | ❌ 阻塞 | 无 docker 组权限 / 无 sudo；需运维 `usermod -aG docker` |
| **Route E′（推荐）** | ✅ **技术可行** | git clone ✅ + aliyun 镜像装依赖 ✅ + 内网模型 ✅ + HF 数据集 ✅ + 磁盘 ✅，**全程不需要 docker** |
| sb-cli（云评测） | ❌ | api.swebench.com 000 不可达 + 合规红线 |
| 自建 bwrap/nsjail 沙箱 | 备选 | 若 E′ 的「本地环境」隔离不够再考虑 |

---

## 4. 🔴 需运维拍板的两件事（否则 H-A 不能安全推进）

1. **Docker 权限（二选一）**：
   - (a) 走官方 docker 口径 → 请执行 `usermod -aG docker app.e0031982`（并 `newgrp docker` / 重登）；
   - (b) 走 **Route E′（无 docker）** → 无需改权限，我方直接 `git clone` + aliyun 镜像装依赖。
2. **运行主机**：我方当前在 **`.29`（10.239.2.29）**，这是 **pretrain R2 P-1~P-8 训练机**（`AGENTS.md` §4）。H-A 实跑要 `git clone` + 逐 repo `pip install` + 跑 harness agent 与测试 = **重 I/O**，与训练冲突。请确认：**在 `.29` 上轻量推进**，还是**换到 `.12`**（vision 已收敛、R9 也在 `.12`，同样要避让），或**给出专用仓位**。

> 我方**不会**在未获确认前启动 H-A 实跑评测（遵守「先报预算再跑」「重 I/O 避让训练」）。

---

## 5. 我方建议的下一步（待确认后执行）

- **Route E′ 小规模试点**：django + sympy 两个 repo，共 **20–30 个 instance**（django 15 + sympy 15，从 Lite 抽样）。
- 同一批 instance、同一 `deepseek-v4-flash` 模型、同一 timeout，跑 2–3 个 harness（cline CLI / opencode CLI / codex CLI）对比。
- 产出 `harness/SWEBENCH_COMPARE.html` + 原始日志（`harness/swebench_runs/` 不入库）。
- ⚠️ 报告明确标注：**内部横评口径，非标准 SWE-bench 分数，不与 leaderboard 直接比**。