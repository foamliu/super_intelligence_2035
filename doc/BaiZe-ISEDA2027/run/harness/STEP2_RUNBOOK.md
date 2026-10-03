# Step-2 执行手册（batch-5 步2：django 单个 env 端到端跑通 R1，无需 Docker）

> 创建：2026-10-03（第二十八轮）。本文件是**低负载窗口一到就能直接照抄执行**的 runbook。
> 铁律：贴 `路径:行号` 原文；命令 + 原始输出；不猜。
> 目标：建 1 个 `django__django-10914` 的 rootfs（落 `/nas_train`）→ `unshare` 沙箱跑 `eval.sh` → 复用官方 `get_eval_report` 复现 resolved 判定（对照 gold.patch）。

---

## 0. 本轮的「可行性再确认」结论（已实测，贴原始输出）

### 0.1 环境构建彻底 de-risk：conda 钉版 + pip wheel 全部在镜像里

**conda 侧**：`environment.yml` 里 20 个**精确 build-string 钉版**（`swe-bench-tasks/tasks/django__django-10914/environment.yml`，channels `defaults, conda-forge`），逐一 HEAD 探测 tsinghua 镜像 —— **20/20 全部 200**（`pkgs/main`，`.conda` 或 `.tar.bz2` 均命中）。
> 关键钉子：`python=3.6.13=h12debd9_1` → `pkgs/main/linux-64/python-3.6.13-h12debd9_1.tar.bz2` = **200**（旧 `.tar.bz2` 格式，conda 按 repodata 里的扩展名取）。
> 说明：上一份设计文档 §8 的「待验」项（这些钉版是否还在 tsinghua 快照里）**已证实：在**。

**pip 侧**：`pip:` 段 36 个包，抽查最难装的 C 扩展包（numpy/pillow/bcrypt/cffi/pylibmc/markupsafe/yarl/multidict/frozenlist/aiohttp）—— tsinghua/aliyun `simple` 索引里 **均有 cp36 manylinux wheel**。

**→ 结论**：`conda env create -f environment.yml` 的「装不上」风险基本排除。剩下的纯是**网络下载 + 磁盘写**（重 I/O），需避让训练。

### 0.2 ⚠️ gotcha：共享 `~/.condarc` 有 `offline: true` 且无 `defaults`

`/home/app.e0031982/.condarc` 当前内容（原文）：
```yaml
channels:
  - conda-forge
offline: true
always_copy: true
show_channel_urls: true
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```
- `offline: true` → conda **不联网**，`defaults` 通道未指到 tsinghua。
- 🚫 **不直接改共享 `~/.condarc`**（多 agent 共用）→ 用**本任务专用 `CONDARC`**（下 §2）。

### 0.3 rootfs 工具盘点（决定「怎么搭 base rootfs」）

```text
debootstrap : absent    mmdebstrap : absent    unshare : OK (/usr/bin/unshare)
proot       : absent    systemd-nspawn: absent  chroot  : OK (/usr/sbin/chroot)
bwrap/nsjail: absent
host OS     : Ubuntu 22.04.5 LTS (jammy)   ← 与 Dockerfile base `ubuntu:jammy` 完全一致
conda       : /nas_train/app.e0031982/miniforge3/bin/conda  (conda 25.7.0)
```
- **关键**：host = jammy，Dockerfile base = `ubuntu:jammy`（`Dockerfile:1`）→ **base rootfs 可从 host 播种**，绕开 `archive.ubuntu.com`（直连大概率不通）。

---

## 1. 目标 rootfs 布局（对齐官方镜像的绝对路径）

`eval.sh`（`swe-bench-tasks/tasks/django__django-10914/eval.sh`）硬编码的绝对路径：
```text
/opt/miniconda3/bin/activate   + env `testbed`
/testbed                        ← django repo @ base_commit e7fd69d…
/etc/locale.gen  + locale-gen   （eval.sh 会 sed 开 en_US.UTF-8 并 locale-gen）
/bin/bash, git, sed, python, pip（base 系统 + 工具）
```
→ rootfs 需含：base 系统（jammy）+ 全新 conda @ `/opt/miniconda3` + env `testbed` + `/testbed`（django）+ 可写 `/etc` + locale 数据。

---

## 2. conda 环境构建（专用 CONDARC，不碰共享 ~/.condarc）

```bash
ROOTFS=/nas_train/app.e0031982/harness_work/rootfs/django__django-10914
WORK=/nas_train/app.e0031982/harness_work

# 2.1 本任务专用 condarc（tsinghua defaults + conda-forge，去掉 offline）
cat > $WORK/harness.condarc <<'EOF'
channels:
  - defaults
  - conda-forge
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
show_channel_urls: true
always_copy: true
EOF

# 2.2 建 env（prefix 直接指进 rootfs；pip 段走 aliyun）
export CONDARC=$WORK/harness.condarc
export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
mkdir -p $ROOTFS/opt/miniconda3
/nas_train/app.e0031982/miniforge3/bin/conda env create \
    -p $ROOTFS/opt/miniconda3/envs/testbed \
    -f $WORK/swe-bench-tasks/tasks/django__django-10914/environment.yml
```

⚠️ **执行前提（重 I/O 避让）**：仅在 `.29`/`.12` 低负载窗口跑。下载 ≈ 20 conda 包 + 36 pip 包（numpy/pillow 等，~100–200MB）。

---

## 3. base rootfs（从 host 播种，避开 archive.ubuntu.com）

> host = jammy = Dockerfile base。方案优先级 A > B > C：

**A（首选）host 播种**：host 就是 jammy，git/sed/bash/locale-gen 已装。`/usr` 大（几 GB），可在 mount ns 内 `--rbind` 只读 + 可写部分（`/usr/lib/locale`）单独 overlay/copy。
```bash
for d in bin sbin lib lib64 usr; do cp -a /$d $ROOTFS/ 2>/dev/null || true; done
cp -a /etc $ROOTFS/            # 可写副本（eval.sh 要 sed /etc/locale.gen）
mkdir -p $ROOTFS/{proc,sys,dev,tmp,run}
```

**B（备选）**：`skopeo copy docker://ubuntu:jammy ...`（L1 路线，client 侧代理）抽 rootfs。
**C（备选）**：`sudo apt install debootstrap` + `debootstrap jammy $ROOTFS`（须 archive.ubuntu.com 可达，待验）。

---

## 4. django 仓库落位 /testbed

```bash
git clone https://github.com/django/django $ROOTFS/testbed
cd $ROOTFS/testbed
git reset --hard e7fd69d051eaa67cb17f172a39b57253e9cb831a   # base_commit（task.yaml）
git config --global --add safe.directory $ROOTFS/testbed
# pip install -e . 在 env 内做（eval.sh 本身也会做）
```

---

## 5. unshare 沙箱跑 eval.sh（对照 gold.patch）

```bash
# 5.1 三件套复跑确认（batch-5 步1 已 OK）
unshare --user --map-root-user --mount --pid --fork true && echo UNI_OK

# 5.2 沙箱内 bind + chroot + 跑 eval.sh（模板，须用真实 rootfs 敲定精确 flag）
unshare --user --map-root-user --mount --pid --fork bash -c '
    mount -t proc proc  '$ROOTFS'/proc
    mount -t tmpfs tmpfs '$ROOTFS'/tmp
    mount --bind /dev '$ROOTFS'/dev
    chroot '$ROOTFS' /bin/bash -c "source /opt/miniconda3/bin/activate && conda activate testbed && cd /testbed && bash /eval.sh"
  ' 2>&1 | tee eval.django10914.log
```

> 真实隔离的两条坑（待实测敲定）：
> ① NFS 安全检查：`/nas_train` 的 rootfs 在 user ns 映射为 root 后，对 NFS 写变 `nobody` → 可能 `pip install -e .` 报 EACCES。若命中，`/testbed`/env 的可写部分用 tmpfs/overlay 遮蔽。
> ② `locale-gen` 写 `/usr/lib/locale`（只读 bind 会失败）→ locale 数据须预拷进 rootfs 或让 `/usr` 可写副本。

---

## 6. 评分（复用官方口径，逐字节一致）

```bash
cd /nas_train/app.e0031982/harness_work
PYTHONPATH=$PWD/SWE-bench python \
  /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/r1_eval.py \
  --instance django__django-10914 \
  --predictions <gold-or-empty-predictions.json> \
  --rootfs $ROOTFS --sandbox unshare --run-id R1_SMOKE --timeout 1800
```
> 预期：gold patch → `resolved=True`（FAIL_TO_PASS 全过 + PASS_TO_PASS 不挂）；空 patch → `resolved=False`（`test_override_file_upload_permissions` 挂）。

---

## 7. 打通后的下一步

1. 记录 django10914 的 **env 准备耗时 + 失败率**（batch-5「必须记录」项）。
2. 用同一 rootfs 模板 **scale 到 sympy 1 个**，验证模板跨 repo 可复用。
3. 把 `r1_eval.py` 的 rootfs 布局/unshare flag 回写为**实测敲定值**（现在「可信但未实测」）。
4. 进入步3（per-harness `issue→model_patch` 驱动，先 codex/opencode）。