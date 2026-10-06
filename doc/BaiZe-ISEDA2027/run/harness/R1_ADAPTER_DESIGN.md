# R1 适配层设计（unshare 沙箱 · 无 docker）— SWE-bench-Lite × 5 harness

> 本文件是 **H-A 实跑的工程蓝图**，记录「从官方 harness 里能复用哪些、要重写哪些、沙箱怎么搭」。
> 铁律：贴 `路径:行号` 原文，命令 + 原始输出，不猜。
> 创建：2026-10-03（第二十六轮，收到 batch-5 放行后，步2/步3 的前置调研）。

---

## 1. 结论速览（TL;DR）

- 官方 harness 的 **执行层 100% 绑 Docker**（`run_evaluation.py` `import docker` + `create_container`/`container.exec_run`），**不能直接跑**。
- 但**评分层与「spec 构造层」是 docker 无关的纯函数**，可直接 import 复用：
  - `make_test_spec()` — `swebench/harness/utils.py:251`
  - `get_eval_report()` — `swebench/harness/grading.py:329`
  - `GIT_APPLY_CMDS` — `swebench/harness/run_evaluation.py:45-49`
  - `parse_eval_script()` / `record_test_exit_code()` — `swebench/harness/utils.py:213` / `:222`
- **R1 要重写的只有两件**：① 用「本地 rootfs + unshare」替换 `create_container`/`exec_run`；② 每 harness 写一个「issue → model_patch」的驱动适配（官方 `predictions.json` 只是被评对象的容器，与 harness 无关）。
- **环境 install spec 的来源 = Dockerfile**，位于 tasks 仓库 `SWE-bench/swe-bench-tasks`（`README.md:67`），**不在 HF 数据集里**。

---

## 2. 数据集：两条 HF id 的字段差异（关键）

| 项 | `princeton-nlp/SWE-bench_Lite`（旧，已缓存） | `SWE-bench/SWE-bench_Lite`（新） |
|:--|:--|:--|
| 条数 | 300 (test) | 300 (test) + 23 (dev) |
| 关键字段 | `repo/instance_id/base_commit/patch/test_patch/problem_statement/hints/version/FAIL_TO_PASS/PASS_TO_PASS/environment_setup_commit` | **多出** `eval_script`、`log_parser`、`eval_type`、`image`、`difficulty` |
| 能否直接 make_test_spec | ❌ 缺 `eval_script/log_parser/eval_type/image` | ✅ 齐全 |

- 实测（本轮回贴）：`load_dataset('SWE-bench/SWE-bench_Lite', split='test')` → 300 条，列齐全。
- 例 `django__django-10914`：`image=swebench/sweb.eval.x86_64.django_1776_django-10914:latest`；`eval_script` 里 `source /opt/miniconda3/bin/activate && conda activate testbed && cd /testbed && python -m pip install -e .`，测试命令 `./tests/runtests.py --verbosity 2 --settings=test_sqlite --parallel 1 test_utils.tests`。
- → **R1 用新 id `SWE-bench/SWE-bench_Lite`**（eval_script/log_parser/eval_type 全给，`make_test_spec` 直接可用）。

---

## 3. 官方 harness 的「可复用 vs 要重写」切分

### 3.1 可复用（docker 无关，纯函数/纯数据）

| 组件 | 路径 | 用途 |
|:--|:--|:--|
| `make_test_spec(instance)` | `swebench/harness/utils.py:251` | instance → `TestSpec`（含 eval_script_list、F2P/P2P、log_parser、eval_type） |
| `parse_eval_script` / `record_test_exit_code` | `swebench/harness/utils.py:213` / `:222` | eval.sh → 命令序列，测试命令后插入 `$?` 捕获（评分靠它） |
| `get_eval_report(...)` | `swebench/harness/grading.py:329` | 从测试日志解析 F2P/P2P → resolved 判定 |
| `GIT_APPLY_CMDS` | `swebench/harness/run_evaluation.py:45-49` | 依次尝试 4 种 patch apply（`git apply` / `--3way` / `--reject` / `patch -p1`） |
| 各 log_parser | `swebench/harness/log_parsers/` | 解析 pytest 等输出成 status map |
| `get_predictions_from_file` | `swebench/harness/utils.py:37` | 读 predictions.json/jsonl（官方口径） |

### 3.2 要重写（docker 绑定）

| 组件 | 路径 | 说明 |
|:--|:--|:--|
| `create_container` | `swebench/harness/run_evaluation.py:76` | `docker.from_env().containers.create(...)` |
| `run_instance` 里的 `container.exec_run(...)` | 全 `run_evaluation.py` | 每条 `git apply`/`git diff`/`/bin/bash /eval.sh` 都走 container exec |
| `exec_run_with_timeout` | `swebench/harness/docker_utils.py` | 容器内命令 + 超时 |

→ **R1 策略**：不 fork 官方 `run_evaluation.py`，而是**新写 `r1_eval.py`**，import 3.1 的纯函数，用「本地 rootfs + unshare subprocess」实现 3.2 的三件事（apply patch / 跑 eval.sh / 取日志输出）。评分口径（F2P/P2P/resolved）**逐字节复用 `get_eval_report`**，保证与官方可比。

---

## 4. 环境构建（R1 替代 Docker 镜像的部分 —— 最难的坑）

每 instance 的 `eval_script` 都假定一套现成环境（如 django：conda env `testbed` + `pip install -e .` 已装依赖）。
这套环境在官方流程里由 Dockerfile 在镜像层建好。**R1 必须自己建**。

**install spec 的唯一权威来源 = 每个 instance 的 Dockerfile**（tasks 仓库 `SWE-bench/swe-bench-tasks`，`swebench/task/repo.py` 的 `load_dockerfiles()` 读 `tasks/<id>/Dockerfile`）。

- tasks 仓库结构（`swebench/task/repo.py` 头注释）：`tasks/<instance_id>/{task.yaml, tests.json, eval.sh, test.patch, gold.patch, problem_statement.md, hints.md, Dockerfile, test_assets/, problem_assets/}`。
- **R1 计划**：克隆 tasks 仓库 → 逐 instance 读其 `Dockerfile` → 把 `RUN` 指令翻译成 `conda`/`pip install`/`apt-get` 本地命令（git clone repo @ base_commit + 用内网 `mirrors.aliyun.com/pypi` 装依赖 + `pip install -e .`），rootfs 落 `/nas_train/app.e0031982/harness_work/rootfs/<instance_id>/`。

⚠️ **已知风险（如实记录）**：老版本依赖（django 3.0 / astropy 4.3）在 2026 年 pypi 可能装不上（解析器/弃用版本），正是任务书 L2「失败率高」坑。**先只跑 1 个 django instance 端到端验证建环境可行性**，再决定是否 scale 到 300。

---

## 5. 沙箱执行（R1 核心：unshare）

**已验证能力**（batch-5 步1 硬闸）：`unshare --user --map-root-user --mount --pid --fork` 三件套 OK；ns 内 `mount -t tmpfs tmpfs /mnt` OK；`unprivileged_userns_clone=1`；`/nas_train` 剩 32T。

**R1 沙箱模板（待用 django 端到端敲定）**：
```bash
unshare --user --map-root-user --mount --pid --fork \
  bash -c 'mount --bind <rootfs> <rootfs>; mount -t tmpfs tmpfs <tmp>; chroot <rootfs> /bin/bash /eval.sh'
```
- 测试命令与 `git apply` 都在该 user+mount+pid ns 内执行，模型 patch 的副作用被 namespace 隔离（NFS 破坏 / `rm -rf` 风险点）。
- `git apply` 链复用官方 `GIT_APPLY_CMDS`（run_evaluation.py:45-49），apply 口径一致。

---

## 6. harness 适配层（步3）

官方 `predictions.json` 格式：`[{instance_id, model_name_or_path, model_patch}]`（或 dict）。
→ **每个 harness 需一个「issue → model_patch」驱动**：

| harness | 启动形态（待逐个确认 `--help`/README） |
|:--|:--|
| codex | CLI（源码最规整，步3 建议先跑通） |
| opencode | CLI |
| deepseek-harness | 待确认（`/nas_train/app.e0031982/harness/deepseek-harness/`） |
| claude-code | CLI |
| cline | VSCode 扩展 + headless CLI（API 化最麻烦，最后做） |
| aider（对照基线，可选） | `benchmark/benchmark.py` 原生驱动 |

- **统一口径**：同一模型 `deepseek-v4-flash`（内网网关 `http://agi-gateway.cxmt.com/v1`，HTTP 200 已实测）、同一 instance 集、同一 timeout/max-steps。
- 每个 harness 跑完 → 落入 `predictions.json` → `get_eval_report` 评分 → 固化 yaml/json + 命令 + 版本。

---

## 7. 下一步（待执行顺序）

1. 等 tasks 仓库 clone 完成 → 读 `tasks/django__django-10914/Dockerfile` 确认 install spec 可翻译。
2. **步2**：建 1 个 django env（rootfs 落 /nas_train）→ unshare 沙箱跑 `eval.sh` → `get_eval_report` 复现官方 resolved 判定（对照 gold patch）。
   - ⏸ **受训练避让**：`.29` 当前 load 15 + GPU 56–86% 满载 → 重 I/O（pip install 老版本 django）**留到低负载窗口**。
3. **步3**：写 `r1_eval.py`（纯 CPU，可先行）+ 每个 harness 的 patch 驱动。
4. **步4**：顺序跑 300×5。

---

## 8. 环境构建连通性（2026-10-03 实测 —— 关键结论）

> 上一版把「老版本依赖装不上」当成主要风险；本轮回贴实测后，**真正的关键项是 conda/anaconda 通道**（不是 pypi）。结论如下：

| 项 | 直连 | 备选（实测可达） |
|:--|:--|:--|
| `repo.anaconda.com`（`defaults` 主通道） | ❌ 000 | ✅ `mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main` = 200，**仍带 python-3.6.\*（29 个）** |
| `conda.anaconda.org/conda-forge` | ❌ 000 | ✅ `mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge` = 200 |
| miniconda 安装包 | ❌ 000 | ✅ 无需装：本机已有 `miniforge3`（`/nas_train/app.e0031982/miniforge3/condabin/conda`） |
| pypi | ❌ 000 | ✅ `mirrors.aliyun.com/pypi/simple/` = 200（`environment.yml` 里的 `pip:` 段走这里） |

- 本机 `~/.condarc` 已把 `conda-forge` 指到 tsinghua；**`defaults` 尚未指到 tsinghua**（`custom_channels` 里没有），这是下一步要补的配置。
- **环境规格原文**（`swe-bench-tasks/tasks/django__django-10914/Dockerfile`）：`environment.yml` 走 `channels: defaults, conda-forge`，含 `python=3.6.13`、`pip=21.2.2` 等**精确 build-string 钉版**（如 `certifi=2021.5.30=py36h06a4308_0`）。
- ⏳ **待验（下一步）**：这些**精确 build-string 钉版在当前 tsinghua `pkgs/main` 快照里是否还存在**（2024 年 anaconda 清空过旧 build；`pkgs/free` 是被归档的旧通道，tsinghua=`/anaconda/pkgs/free`=200）。若个别钉版缺失 → 需「放宽钉版 / 换等价版本」并**在报告里注明对 eval 语义的影响**。

### 步2 具体命令（待低负载窗口执行，先贴，不跑）

```bash
# 1) 让 conda 走 tsinghua 镜像（defaults + conda-forge）
cat >> ~/.condarc <<'EOF'
channels:
  - conda-forge
  - defaults
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
EOF
# 2) 试建 1 个 django env（python 3.6 老环境）
conda env create -f /nas_train/app.e0031982/harness_work/swe-bench-tasks/tasks/django__django-10914/environment.yml
# 3) git clone django + reset 到 base_commit e7fd69d… + pip install -e .（rootfs 落 /nas_train）
# 4) unshare 沙箱跑 eval.sh（见 §5 模板）→ 对照 gold.patch 复现 resolved
```