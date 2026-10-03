# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 🔴 运维必读（2026-10-03 更新：✅ 第 4 批可行性评估已交付 + ✅ 第 5 批步1 硬闸已核验 R1 可行 + ✅ 步3 适配层 `harness/r1_eval.py` 已交付〔官方评分复用已测通，`--spec-only` 端到端 OK〕；下一步 = 步2 建 django rootfs + unshare 端到端实跑）

> 🆕 **batch-5（运维「放行」）已收到**：全量 SWE-bench-Lite 300 × 5 harness（cline/opencode/deepseek-harness/codex/claude-code）**按序跑，不要缩水**；**L0（dockerd 配代理）已取消**；**R1（`unshare` 用户命名空间沙箱 + 每实例 rootfs 落 `/nas_train`）为首选**；docker 系（L1 skopeo / L2 build）降为末选。
> ✅ **batch-5 步1 硬闸已核验通过**（本轮回贴原始输出）：`unshare --user --map-root-user --mount --pid --fork` 三件套 **OK**、user ns 内 `mount -t tmpfs` **OK**、`unprivileged_userns_clone=1`、`/nas_train` 剩 **32T** → **R1 完全可行，不碰 docker/daemon**。
> ⏭ **下一步**：步2（用 1 个 repo=django 端到端跑通 R1 沙箱）→ 步3（写适配层：`benchmark.py` 只驱动 aider，另 5 者需适配；先跑通 codex/opencode 再复制，复用官方 `run_evaluation` 口径）→ 步4（顺序跑 300×5，受 5h 滑动窗口 key 约束 → 低并发 ≤4 + 跨 harness 串行 + 每 harness 跑完即固化）。
> ⚠️ **重 I/O 避让训练**：.29 是 pretrain R2 训练机，实跑 300×5 只在低负载窗口；步3 适配层（纯 CPU）可先行。

> 🆕 **已交付 batch-4**：`harness/SWEBENCH_LITE_FEASIBILITY.md`（只读评估 §1–8）+ `harness/CODE_AGENT_BENCHMARKS_SURVEY.md` 升 v2（更正 Aider「无 docker 可立即开跑」→「沙箱前提未满足」+ 两条 root 解法）。
> 🔑 batch-4 关键数据（仍为 R1 硬闸与镜像决策依据）：① 磁盘不约束（`/data/docker` 本地 6.5T 可用，非 NFS）；② 镜像 nominal ≈420–430GB、**层去重后 ~50–100GB**（32 张深清单实测 15.4% 共享率）；③ ⚠️ **Docker Hub 匿名拉取限流 100 次/h**（共用代理出口 IP）；④ 本机 11 镜像无一 SWE-bench；⑤ 重启风险低（0 running 容器）。

> （旧）第十七轮执行**第 3 批**（`7e0b168`）：`harness/CLINE_IMPROVEMENTS_TOP5.html` 已交付（P0 O5/O4、P1 O3、P2 O1/O2，四段式 + 诚实条款）。
> - ⏸ **H-A′ 仍未实跑**（见「待运维拍板」）；H-B 5/5、H-D 均已交付。

### ✅ 已办：Docker 权限解锁（运维指令 ①）
- `usermod -aG docker app.e0031982` **成功**（口令变体 `Ly3960405@` = ❌；`Ly3960405#` = ✅）。
- `id app.e0031982` → `groups=6002(app.adm),122(docker)`；`sg docker -c 'docker info'` → **OK**（Docker 27.5.1 / daemon active / overlay2 / 2 个已停容器 / 11 镜像）。
- ⚠️ **安全**：口令已随任务书入库，**请运维尽快轮换**。

### 🔴 新发现：`docker pull` 仍失败（把「从未测过」补测了）
- 实测 `docker pull hello-world` → `dial tcp 65.49.68.152:443: connect: network is unreachable`。
- **根因**：shell 有 `https_proxy=172.19.92.25:13128`（curl 经代理可达 registry-1.docker.io=401），但 **dockerd（root/systemd）无代理配置** + `daemon.json` 无 `registry-mirrors` → daemon 直连 → 不可达。内网 registry/Harbor **未发现**（harbor.cxmt.com / registry.cxmt.com / 10.239.2.1 均 000）。
- → **socket 权限已解，但官方 docker 口径仍不通**。打通需运维三选一：① 给 dockerd 配代理 + 重启（有扰动共享主机风险）② 提供内网 Harbor 镜像 ③ 走 Route E′（无 docker，aliyun 装依赖）。

### ⭐ 已办：H-C Aider Polyglot 可行性核查（运维指令 ③）
- **仓库 git 可达**：`Aider-AI/polyglot-benchmark`（225 题 Exercism 题库，6 语言 cpp/go/java/js/python/rust，~1MB）+ `Aider-AI/aider`（~140MB，harness 所在）。已克隆到 `/nas_train/app.e0031982/harness_work/`（**不入库**）。
- **harness 机制**：`Aider-AI/aider/benchmark/benchmark.py` 驱动 aider 对每道题「生成代码 + 编辑落地」，产出 yaml（`pass_rate_1/2`、`percent_cases_well_formed`、`num_malformed_responses` 等）。
- **包名**：`aider-chat`（最新 **0.86.2**，aliyun 镜像有；⚠️ `aider` 是 0.2.6 占位包，不是它）。
- **模型**：接内网网关 `http://agi-gateway.cxmt.com/v1`（OpenAI 兼容）+ `deepseek-v4-flash`。
- 🔴 **安全待决策**：harness README 明确「intended to run inside docker」——因为它**直接执行 LLM 生成的代码**。本机 `.29` 是 **pretrain R2 训练机**，无隔离执不可信代码 = 风险。需运维在 ① docker（待 pull 打通）② bwrap/nsjail 本地沙箱 ③ 接受风险直跑 之间拍板。→ **本轮未启动评测实跑**。
- 🔴 **新发现（第十五轮补测）**：任务书所谓的「本地沙箱」二选一路线里，**本机 `bwrap`/`nsjail`/`firejail`/`bubblewrap`/`podman`/`nerdctl` 全部 `(absent)`**，仅 `docker` 存在（socket 已解、pull 仍被网络阻断）。→ 意味着「任务书 H-C 说 Aider Polyglot『无 Docker 可立即开跑』」有**前提漏洞**：harness 会**执行 LLM 生成的 6 语言代码**，而本地沙箱工具一个都没装。故 Aider 沙箱「三选一」实际收窄为：**① 打通 docker pull**（需 dockerd 配代理/内网 Harbor）**② root 安装 bwrap 或 nsjail**（共享训练机上新装包，本身就是新 ops 动作）**③ 接受风险直跑**。**在运维未拍板前，本线不启动任何评测实跑。**

### ⏸ 已办：H-A′ 前置核查（batch 2）—— 实跑待运维拍板「沙箱 + 参赛者适配范围」
- **执行模型已证**：aider 基准**确实执行 LLM 生成的代码**（`benchmark/README.md:22-27`「taking code written by an LLM and executing it without human review… could `sudo rm -rf /`」+ `benchmark.py:1027` `subprocess.run` 跑测试）。→ 沙箱不是可选项。
- **新发现（推翻第十五轮「本地沙箱工具全 absent」的一半）**：`unshare`（util-linux）**存在**，`unshare --user --map-root-user true` 实测 **OK**（用户命名空间可用）；但 `proot/nsjail/firejail/bwrap/podman/nerdctl` 仍 absent。⚠️ 仅 user namespace **不足以防 NFS 破坏**（需再加 mount namespace + tmpfs/chroot 全量沙箱，是独立基建动作）。
- **工具链缺口**：`python/node/javac/g++` 在，`go/rustc/cargo` **均 absent** → 6 语言只能跑 cpp/java/js/python 四语言子集（或装 go/rust）。
- **参赛者适配**：`benchmark.py` **只原生驱动 aider**（`from aider.coders import Coder`）→ cline/opencode/deepseek/codex/claude-code 五者需各自写适配层接入 polyglot 任务格式，是额外工程。
- **aider-chat 未装**（`pip show aider-chat` 空）。
- → **待运维拍板**：① 沙箱方案（A. 我自建 `unshare --user --mount --pid` + tmpfs/chroot 沙箱〔需确认允许在共享训练机起命名空间〕B. root 装 bwrap/nsjail C. 运维明确授权无隔离直跑〔不推荐，README 自证 `rm -rf` 风险〕）② 参赛者范围（先只 aider 基线？还是 6 者全适配〔成本高〕）③ go/rust 工具链是否补装。

**可行性关键结论（可复现命令已全部记录）**：

| 项 | 结果 |
|:--|:--|
| GitHub git | ✅ `git ls-remote` 拿 HEAD（SWE-bench / aider / polyglot-benchmark 均可达） |
| pypi | ❌ 官方 000，✅ **内网镜像 `mirrors.aliyun.com/pypi` = 200** |
| Docker socket | ✅ 已解锁（`app.e0031982` 入 `docker` 组） |
| Docker pull | ❌ dockerd 无代理 → registry-1.docker.io 网络不可达；无内网 registry |
| 模型 | ✅ `http://agi-gateway.cxmt.com/v1` → `deepseek-v4-flash`，HTTP 200 |
| 数据集 | ✅ HF 200；SWE-bench_Lite/test=300 已拉取；`datasets==4.8.4` 已装 |
| sb-cli 云 | ❌ api.swebench.com=000 + 合规红线 |
| 磁盘 | ✅ /data 6.5T、/nas_train 31T |

**SWE-bench_Lite repo 分布**：django 114(38%) · sympy 77(26%) · matplotlib 23 · scikit-learn 23 · pytest 17 · sphinx 16 · 其余 <7 条。
→ Route E′ 建议先跑 **django + sympy** 两库 **20–30 条** 试点。

## 运维问答

> 外部运维在 `BAIZE_HARNESS_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R1_adapter_done**（batch-4 已交付；batch-5 步1 硬闸 PASS；第二十六轮：克隆 SWE-bench + tasks、重构架构、实测 conda 通道 → `R1_ADAPTER_DESIGN.md`；第二十七轮：官方评分复用测通 + 交付 `harness/r1_eval.py`） |
| WAITING | 1（步2 建 1 个 django env = 重 I/O〔conda env create 下载大 + pip〕，须避让 `.29` pretrain R2 训练〔当前 load 16+GPU 满载〕，留待低负载窗口；**非等运维拍板**） |
| ERROR_COUNT | 0 |
| 更新 | 2026-10-03 17:xx（第二十七轮：官方评分复用测通 + `harness/r1_eval.py` 交付，`--spec-only` 端到端 OK） |
| 产出 | ✅ H-B 5 份源码 HTML · ✅ `MERGE_OVERLAP_ANALYSIS.md` · ✅ `SWEBENCH_FEASIBILITY.md` · ✅ H-C survey v2 · ✅ H-D 矩阵 + 机会点 · ✅ `CLINE_IMPROVEMENTS_TOP5.html` · ✅ `SWEBENCH_LITE_FEASIBILITY.md`（batch-4，含 batch-5 增补） · ✅ `R1_ADAPTER_DESIGN.md` · ✅ `r1_eval.py`（步3 适配层） |

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        R1_adapter_done
已完成:       H-B 5 份源码分析；H-A §1.1 可行性；Docker socket 解锁；H-C Aider v2；H-D 矩阵+机会点+TOP5；SWE-bench-Lite 全量可行性(batch-4)；batch-5 步1 硬闸=unshare三件套 PASS；第二十六轮 R1 前置调研（克隆 SWE-bench + swe-bench-tasks、重构可复用/重写切分、实测 conda 通道=tsinghua 镜像可达）→ R1_ADAPTER_DESIGN.md；第二十七轮 官方评分复用测通（pip 装 docker/modal/unidiff/ghapi → make_test_spec/get_eval_report 对真实 django__django-10914 跑通）+ 交付 r1_eval.py（步3 适配层，native/unshare 沙箱 + 完整 run_instance 口径）
当前动作:     2026-10-03 第二十七轮：确认官方 run_evaluation 全绑 docker、但 make_test_spec(utils.py:251)/get_eval_report(grading.py:329)/GIT_APPLY_CMDS(run_evaluation.py:45-49) 纯函数可复用（补装纯 python 客户端库后 IMPORT OK）；写 r1_eval.py 替换 docker 执行层为可插拔 native/unshare 沙箱，--spec-only 端到端跑通真实 django instance
下一步:       步2 = 低负载窗口时 conda 走 tsinghua 镜像建 1 个 django env（python 3.6 老环境）→ 用真实 rootfs 端到端敲定 unshare 沙箱（rootfs 布局 + 精确 flag）对照 gold.patch 跑通 → 步4 顺序跑 300×5
阻塞:         步2 建环境的 conda env create（重 I/O 下载）须避让 .29/.12 训练〔当前 load 16+GPU 满载〕；另待验：environment.yml 精确 build-string 钉版在当前 tsinghua pkgs/main 快照是否齐全；r1_eval.py 的 rootfs 布局/unshare flag 须步2 用真实 rootfs 敲定
ERROR_COUNT:  0
```

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（**多 agent 共用**，见 `AGENTS.md`）
- **同级任务线**（🚫 不要碰）：`MEMORY_VISION.md` / `MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md`

## 流水

> 📦 2026-10-02 的 7 条流水条目（H-B 5 份源码分析 + H-A §1.1 可行性核查的关键证据路径 `文件:行号`）已于第二十一轮滚动归档至 `daily-memories-harness/2026-10-02.md`「从 MEMORY_HARNESS.md 滚动归档」节（原文不改）。

- 2026-10-03 16:35 —— **第二十六轮（推进 batch-5 步2/步3 前置调研，无新指令）**：`git fetch` → HEAD==origin/main==`4a75c348`（`git log -- BAIZE_HARNESS_TASK.md` 最近仍是 `a5b4b4f` batch-5，已收到并核验）。本轮做了 R1 前置调研（纯 CPU/网络，避让了重 I/O）：① **clone `SWE-bench`**（shallow，github OK）→ 确认官方 `run_evaluation.py` 全绑 docker（`import docker`/`create_container`/`container.exec_run`），但 `make_test_spec`(utils.py:251)/`get_eval_report`(grading.py:329)/`GIT_APPLY_CMDS`(run_evaluation.py:45-49) 是 docker 无关纯函数、可复用；② **clone `swe-bench-tasks`**（`SWE-bench/swe-bench-tasks`，2519 任务，Lite 300 在内）→ `tasks/<id>/{Dockerfile,environment.yml,eval.sh,test.patch,gold.patch,task.yaml}`，**环境 install spec = 每 instance 的 Dockerfile/environment.yml**；③ **数据集改用 `SWE-bench/SWE-bench_Lite`**（旧 `princeton-nlp/SWE-bench_Lite` 缺 eval_script/log_parser/eval_type/image，新的全齐）；④ **实测 conda 通道**：直连 `repo.anaconda.com`/`conda.anaconda.org`/miniconda 安装包均 000，但 **tsinghua 镜像 `mirrors.tuna.tsinghua.edu.cn/anaconda/{pkgs/main=200,pkgs/free=200,cloud/conda-forge=200}` 全可达**，且 `pkgs/main` 仍带 `python-3.6.*`（29 个）→ 老版本 conda env 有望走镜像重建。**交付 `harness/R1_ADAPTER_DESIGN.md`**（可复用/重写切分 + 环境构建 + unshare 沙箱模板 + harness 适配 + 步2 具体命令，贴 `路径:行号` 原文）。⏸ **下一大步（步2 建 1 个 django env，python 3.6 老环境）是重 I/O（conda env create 下载 + pip）**，`.29` 当前 load 15 + GPU 56–86% 满载 → **留待低负载窗口**，本轮不启动实跑。保持 `WAITING=1`（受训练避让，非等运维拍板）。MEMORY_HARNESS.md 未超 32KB（本轮改动后需留意，已控制增量）。
- 2026-10-03 17:50 —— **第二十七轮（推进 batch-5 步3 适配层，无新指令）**：`git fetch` → HEAD==origin/main==`e960f2a4`（`git log -- BAIZE_HARNESS_TASK.md` 最近仍是 `a5b4b4f` batch-5）。`.29` 仍满载（load 16.26 + GPU 37–87%，pretrain R2）→ 步2 建 django env（重 I/O）继续避让，本轮推进**步3 适配层（纯 CPU 可先行）**。① **打通官方评分复用**：补装 4 个纯 python 客户端库（`docker 7.2.0`/`modal 1.6.0`/`unidiff`/`ghapi`，aliyun 镜像）：原 `from swebench.harness.utils import make_test_spec` 因 `harness/__init__.py` 硬 `import docker_utils`(→docker)/`modal_eval`(→modal) 而 ImportError，补齐后 IMPORT OK。② **实测官方评分函数可复用**：`make_test_spec` 对真实 `django__django-10914`（HF cache 载入）正确解析 eval.sh 并注入退出码捕获（`utils.py:222 record_test_exit_code`）；`get_eval_report(grading.py:329)` 对 patch=None 返回标准 `patch_is_None` 字段；FAIL_TO_PASS=`['test_override_file_upload_permissions …']`。③ **交付 `harness/r1_eval.py`**（步3 核心产物，已 `py_compile` + `--spec-only` 端到端跑通）：复用官方 `make_test_spec`/`get_eval_report`/`GIT_APPLY_CMDS`/constants，**仅替换 docker 执行层**为可插拔 `native`/`unshare` 沙箱（unshare = `--user --map-root-user --mount --pid --fork` + `chroot rootfs`，照 `R1_ADAPTER_DESIGN.md` §5），完整 mirror 官方 `run_instance` 的 apply-patch 链（`git apply`→`--3way`→`--reject`→`patch --fuzz=5`，附反向 patch 回滚）+ eval.sh 运行 + 官方 `get_eval_report`。运行口径 `PYTHONPATH=/nas_train/app.e0031982/harness_work/SWE-bench`。⚠️ rootfs 布局 + unshare 精确 flag 须步2 用真实 django rootfs 端到端敲定（本轮只有 `--spec-only`，未起沙箱实跑）。⏸ 步2（重 I/O）留待低负载窗口。保持 `WAITING=1`。MEMORY_HARNESS.md 本轮滚动近 20 条旧流水至 `daily-memories-harness/2026-10-03.md`（降至 <32KB）。
