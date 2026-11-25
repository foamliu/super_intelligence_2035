# SWE-bench-Lite 全量(300) 可行性 / 成本评估

> **🆕 2026-10-03 增补（batch-5 到达后）**：本报告 §8「推荐先做 20–30 子集」的结论**已被运维第 5 批指令覆盖**——
> 运维决定**「放行全量 300 × 5 harness，按序跑，不要缩水」**，且**取消 L0（dockerd 配代理）**、**以 R1（`unshare` 用户命名空间沙箱 + 每实例 rootfs 落 `/nas_train`）为首选路线**。
> 本报告 §1–7 的**实测数据依然是 R1 硬闸与镜像来源决策的依据**（磁盘/镜像体积/限流/重启风险等），仅 §8 的「规模」建议作废。
> **batch-5 步1 硬闸已核验通过**：`unshare --user --map-root-user --mount --pid --fork` 三件套 OK、tmpfs 挂载 OK、`/nas_train` 剩 32T → **R1 可行**。

> 依据 `BAIZE_HARNESS_TASK.md` 运维指令 2026-10-03 第 4 批（commit `c9f331a`）。
> **纪律**：只读为先；root 动作先报后做；每条贴命令 + 原始输出；不许猜。
> 核查时间：2026-10-03 · 主机：`whag0pgpuap29`（= 10.239.2.29，**pretrain R2 训练机**）。
> 本报告**只做只读评估**，**未执行**任何 dockerd 配置改动 / daemon 重启 / apt 安装。

---

## 结论速览（运维先看这几行）

| 维度 | 结论 |
|:--|:--|
| **磁盘** | ✅ 不是约束 —— Docker Root Dir `/data/docker` 落在本地 `/data`（**7.0T，剩 6.5T**，不是 NFS） |
| **镜像体积（nominal）** | 300 张 ≈ **420–430GB**（`sum(full_size)`，180/300 实测 257.24GB 外推） |
| **镜像体积（层去重后）** | ⚠️ **远小于 nominal**：32 张深清单实测「36.76GB → 5.68GB 独有层」= **15% 共享率**；全 12 repo 推算 **~50–100GB** 实际下载 |
| **本机已有镜像** | 11 个，**无一 SWE-bench**（全是 vllm/sglang/node 等训练/推理镜像） |
| **dockerd 配代理口子** | ✅ 干净可加：`Environment` 空、`daemon.json` 无 proxy/mirrors、无 drop-in 目录 |
| **重启风险** | 🟢 低 —— `docker ps -a` = **0 个 running 容器**（2 个 stopped 训练容器 13 天前退出） |
| **时间（真成本）** | 300 题 × 1 harness ≈ **75–225 串行小时**（3–9 天）；子集 django+sympy 20–30 ≈ **10–22 串行小时** |
| ⚠️ **新阻塞（第 4 批新发现）** | **Docker Hub 匿名拉取限流 = 100 次/小时**（共用代理出口 IP `203.127.181.131`），配好 daemon 代理后拉 300 张仍会被限流 |
| **推荐** | **先不做全量 300**；docker 打通 + 限流确认后，先 **django+sympy 20–30 子集**试点 |

---

## 1. 镜像总体积（任务书第 1 项：`sum(size)` + 按 layer digest 去重）

### 1.1 结论数字

| 口径 | 数值 | 依据 |
|:--|--:|:--|
| **nominal 总和** `sum(full_size)` | **≈ 420–430GB**（300 张） | 180/300 实测 = 257.24GB，均值 1.429GB/张 × 300 |
| **去重后实际下载** | **~50–100GB**（粗估） | 32 张深清单实测 15.4% 共享率（§1.4），推及 12 repo |
| 每张平均（nominal） | ~1.43GB | 实测 180 张 |

### 1.2 分 repo 实测（`full_size`，Hub 元数据 API）

> 每张图的 `full_size` 通过 `https://hub.docker.com/v2/repositories/swebench/sweb.eval.x86_64.<image>/tags/latest` 拿，**不走 registry 拉取**。

| repo | Lite 条数 | 实测 N | sum(GB) | 平均(MB) | 状态 |
|:--|--:|--:|--:|--:|:--|
| django | 114 | ✅114 | 134.92 | 1183.5 | 实测 |
| matplotlib | 23 | ✅23 | 70.85 | 3080.4 | 实测（含 C 扩展，最重） |
| pytest-dev | 17 | 13 | 13.34 | 1026.3 | 部分（缺 4） |
| pydata (xarray) | 5 | ✅5 | 10.24 | 2047.1 | 实测 |
| astropy | 6 | ✅6 | 6.78 | 1129.4 | 实测 |
| pylint-dev | 6 | ✅6 | 6.49 | 1082.2 | 实测 |
| psf (requests) | 6 | ✅6 | 6.09 | 1015.2 | 实测 |
| mwaskom (seaborn) | 4 | ✅4 | 5.12 | 1281.0 | 实测 |
| pallets (flask) | 3 | ✅3 | 3.42 | 1138.4 | 实测 |
| **sympy** | 77 | ❌0 | (缺) | ~1100（估） | 未测（429） |
| **scikit-learn** | 23 | ❌0 | (缺) | ~2300（估） | 未测（429） |
| **sphinx-doc** | 16 | ❌0 | (缺) | ~1000（估） | 未测（429） |

> 缺的 120 张（sympy 77 + sklearn 23 + sphinx 16 + pytest 4）被 429 阻断，见 §1.5。缺项 repo 均值是**类比估计**（sympy≈django、sklearn≈xarray、sphinx≈轻量），标注「估」。
### 1.3 镜像命名规则（已实测还原）

SWE-bench Lite instance_id → Docker 镜像名（`__` → `_1776_`）：

```text
instance_id  = django__django-11099
docker repo  = swebench/sweb.eval.x86_64.django_1776_django-11099
              （swebench/sweb.eval.x86_64. + instance_id.replace('__','_1776_')）
```

> 实测取证：`GET registry-1.docker.io/v2/swebench/sweb.eval.x86_64.django_1776_django-11099/manifests/latest` → HTTP 200（OCI index，含 amd64 + attestation）。

### 1.4 ⚠️ 层去重实测（32 张深清单）—— 层共享率极高

对 32 张（6 astropy + 26 django）逐张拉 **amd64 manifest**，按 layer digest 去重：

| 口径 | 数值 |
|:--|--:|
| 32 张 nominal 总和 | **36.76 GB** |
| 独有 layer 数 | **84 个** |
| 去重后（按 digest） | **5.68 GB** |
| 共享率 | **nominal 的 15.4%** |

→ **「300 张 ≠ 300 倍体积」成立**：12 个 repo 共享 python/conda/apt 底座 + numpy/scipy 等公共 layer，每张真正独有的是「该 repo @ 该 base_commit + 测试 patch」的最后一层。全 12 repo 独有底座叠加后，**实际下载 ~50–100GB**，与 nominal 420GB 差一个数量级。

### 1.5 ⚠️ 新阻塞：Docker Hub 匿名拉取限流（本批核查新发现）

```bash
curl -sS -D - https://registry-1.docker.io/v2/.../manifests/latest \
     -H "Authorization: Bearer $T" -H 'Accept: application/vnd.oci.image.index.v1+json' | grep -i ratelimit
# → docker-ratelimit-source: 203.127.181.131
#   x-ratelimit-limit: 100;w=3600        ← 100 次/小时
#   x-ratelimit-remaining: 0;w=3600
# HTTP/2 429  {"code":"TOOMANYREQUESTS","message":"You have reached your unauthenticated pull rate limit..."}
```

- **匿名拉取 = 100 次/小时**，且**按出口 IP 计**。本机 `https_proxy=172.19.92.25:13128` 出口 IP = `203.127.181.131`，是**全体走该代理的用户共享**的桶。
- 即便 §6 配好 dockerd 代理，**拉 300 张（每张 manifest + N 个 blob = 多次 pull）也会被限流**，且与他人共享桶。
- 缓解：① Docker Hub **账号登录**（免费 200 次/6h，付费更高）——需运维提供凭据；② 分多日/错峰；③ 只拉子集（20–30 张，100 次/小时足够）。

---

## 2. Docker Root Dir + 剩余空间（任务书第 2 项）

```bash
sg docker -c 'docker info' | grep 'Docker Root Dir'   # → /data/docker
df -h /data/docker /data
# → /dev/mapper/vgdata-lv_data  7.0T  510G  6.5T   8% /data   （本地 LVM，非 NFS）
```

| 项 | 值 |
|:--|:--|
| Docker Root Dir | `/data/docker` |
| 所在盘 | 本地 `/dev/mapper/vgdata-lv_data`（**不是 NFS**） |
| 总量 / 已用 / 可用 | 7.0T / 510G / **6.5T**（8% used） |
| 判定 | ✅ **镜像落在本地盘**（任务书强调的硬约束）；**6.5T >> 需求**，磁盘不是约束 |

## 3. 本机已有镜像（任务书第 3 项）

`sg docker -c 'docker images'` → **11 个**，无一 SWE-bench：

| REPOSITORY | TAG | 大小 |
|:--|:--|--:|
| pixelprune-vllm | 0.29.0 | 24.8GB |
| argus | latest | 2.09GB |
| vllm/vllm-openai | v0.29.0-cu129 | 24.8GB |
| node | 24.12.0-slim | 278MB |
| uv-python-3.12-ubuntu-22.04 | v0.0.1 | 1.12GB |
| lmsysorg/sglang | v0.5.13.post1-cu129 / v0.5.12.post1 | 33.6–37GB |
| vllm/vllm-openai | v0.20.2 / v0.9.1 / v0.9.1-benchmarks / v0.8.5 | 17.7–26.7GB |

→ 全是训练/推理栈，**无可用 SWE-bench base，须从零拉取**。

---

## 4. dockerd 配置口子（任务书第 4 项，只读）

```bash
systemctl show docker -p Environment         # → Environment=（空）
cat /etc/docker/daemon.json                  # → 仅 data-root / runtimes(nvidia) / storage-driver / address-pools
ls -la /etc/systemd/system/docker.service.d/ # → No such file or directory（无 drop-in）
systemctl cat docker | head                  # → 默认 /lib/systemd/system/docker.service，ExecStart 标准，无 override
```

| 项 | 值 | 判定 |
|:--|:--|:--|
| daemon `Environment` | **空** | 无代理 |
| `daemon.json` | 无 `registry-mirrors`、无 `proxies` | 需加代理 |
| drop-in 目录 | **不存在** | 可干净新建 |
| 内网 registry | `Insecure Registries:` 空 | 无内网 Harbor |

→ **口子是干净的**：只需新建一个 systemd drop-in + `daemon-reload` + `restart`（命令见 §6，**本轮不执行**）。

---

## 5. 重启风险（任务书第 5 项）

```bash
sg docker -c 'docker ps -a'
# → CONTAINER ID  IMAGE                 STATUS
#    755684c8dd84  pixelprune-vllm:0.29.0  Exited (0) 13 days ago  funny_goodall
#    106f2436b7c2  pixelprune-vllm:0.29.0  Exited (0) 13 days ago  nice_gauss
```

→ **0 个 running 容器**（2 个 stopped，都是 13 天前退出的 pixelprune-vllm 训练容器）。重启 dockerd **不会打断任何正在运行的工作负载**，风险**低**。仍须「先报方案 + 精确命令，运维批准后再执行」。

---

## 6. 给 daemon 配代理的精确命令（**🚫 本轮不执行**）

> 前提已实测：经代理 `https://registry-1.docker.io/v2/` 返回 **401（可达、待鉴权）**，即代理能让 dockerd 出网打到 Docker Hub。
> ⚠️ 下方命令为**方案草稿，本轮不执行**；sudo 口令**运维已确认且已入库**，但按安全铁律**此处不落盘**（下文用 `sudo -S` 占位，执行时由运维/交互终端提供口令）。

```bash
# ① 建 drop-in（本轮不执行；口令不落盘）
sudo -S mkdir -p /etc/systemd/system/docker.service.d
sudo -S tee /etc/systemd/system/docker.service.d/http-proxy.conf >/dev/null <<'EOF'
[Service]
Environment="HTTP_PROXY=http://172.19.92.25:13128"
Environment="HTTPS_PROXY=http://172.19.92.25:13128"
Environment="NO_PROXY=localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,agi-gateway.cxmt.com,.cxmt.com"
EOF

# ② 重载 + 重启（有扰动，须运维批准）
sudo -S systemctl daemon-reload
sudo -S systemctl restart docker

# ③ 验证（重启后）
docker pull hello-world    # 期望：不再 network unreachable，而是正常拉取 / 或 401 鉴权态
```

**⚠️ 免重启替代（走 client 侧代理）—— `skopeo copy` + `docker load`**：

- `skopeo` **当前未装**（`which skopeo` 空）。可 ① `apt install skopeo`（需 root + 内网 apt 镜像，见 §附）② 下载静态二进制（github 可达）。
- 流程（**不重启 dockerd**）：
  ```bash
  export HTTPS_PROXY=http://172.19.92.25:13128
  skopeo copy docker://swebench/sweb.eval.x86_64.django_1776_django-11099 \
               docker-archive:/data/swb_django_11099.tar
  docker load < /data/swb_django_11099.tar
  ```
- `skopeo` 在 client 侧走 `HTTPS_PROXY`（绕过 daemon 的 `Environment`），`docker load` 只本地导入、不联网 → **代理目的绕开 daemon、也不需 restart**。但**同样受 Docker Hub 100 次/小时 匿名限流**（除非登录）。

---

## 7. 时间估算（任务书第 6 项）—— 时间才是真成本

> ⚠️ 以下为**估算**（未实跑任一 SWE-bench instance，遵守「不许猜」→ 明确标注为工程估算，非实测）。

| 阶段 | 单条耗时（估） | 依据 |
|:--|:--|:--|
| agent 推理（生成 patch，多轮 tool-call） | 10–30 min | 内网 `deepseek-v4-flash`（reasoning 模型，需给足 max_tokens）+ 20–50 轮 |
| 测试评测（跑 FAIL_TO_PASS / PASS_TO_PASS） | 5–15 min | django/sympy 测试套件较重 |
| **合计 / 条** | **15–45 min** | |

| 规模 | harness 数 N | 串行墙钟（估） | 说明 |
|:--|:--|:--|:--|
| 全量 300 | 1 | **75–225 h ≈ 3–9 天**（串行） | 可并行（instance 独立），但本机是训练机、并行度受限 |
| 全量 300 | 3 | 225–675 h ≈ 9–28 天（串行） | ×N 线性放大 |
| **子集 django+sympy 20–30** | 1 | **10–22 h 串行** | 任务书建议的对照规模 |
| 子集 20–30 | 3 | 30–66 h 串行 | |

- 实际墙钟还叠加：**镜像拉取**（§1.5 限流 100 次/h，20–30 张 ≈ 分钟级；300 张 ≈ 数小时 + 重试）+ 逐条 `git clone`/装依赖（若走 Route E′）。
- **并行**可达 4–8× 加速，但**必须避让 `.12`/`.29` 训练**（低负载时段跑），本机 `.29` 是 pretrain R2 训练机。

---

## 8. 结论与推荐规模（任务书第 7 项）

1. **磁盘**：✅ 不约束（本地 `/data` 6.5T 可用，镜像 ~50–100GB 去重后）。
2. **全量 300 是否值得**：**❌ 现阶段不值得** —— 三重阻塞：① docker pull 仍被网络阻断（需 §6 配代理 + 重启，待批）；② **Docker Hub 匿名 100 次/h 限流**（300 张必超，需账号登录或分日）；③ 墙钟 75–225 h/单 harness（在共享训练机上更慢）。
3. **推荐**：
   - 第一：运维批准 §6 配代理（或 skopeo 免重启路）→ 打通 `docker pull`；
   - 第二：先 **django + sympy 20–30 子集 × 2–3 harness** 试点（时间/限流都可控，100 次/h 足够）；
   - 第三：拿到结果 + 运维决定后，再评估是否扩到全量 300（届时也需**Docker Hub 登录凭据**突破限流）。

---

## 附：本批同时完成的更正（任务书第 B 项）

`harness/CODE_AGENT_BENCHMARKS_SURVEY.md` 已升 **v2**，把「Aider Polyglot 无 docker 可立即开跑」**更正为「沙箱前提未满足」**：
- 依据：`benchmark/README.md:22-27`（「intended to run inside docker … executing code written by an LLM without human review → 可能 `sudo rm -rf /`」）+ `benchmark.py:1027`（`subprocess.run` 执行测试）。
- 实测：本地 `bwrap`/`nsjail`/`firejail`/`bubblewrap`/`podman`/`nerdctl` **全部 absent**（仅 `unshare` 存在）。
- 两条 root 解法：① `apt install bubblewrap` —— ✅ **已实测内网 apt 镜像 `172.16.13.24/repository/porxustc_ubuntu22.04` 有 `bubblewrap 0.6.1-1ubuntu0.1`**，可直接装；② 用已实测可用的 `unshare --user --map-root-user --mount` + tmpfs/chroot。



→ **0 个 running 容器**（2 个 stopped，都是 13 天前退出的 pixelprune-vllm 训练容器）。重启 dockerd **不会打断任何正在运行的工作负载**，风险**低**。仍须「先报方案 + 精确命令，运维批准后再执行」。