# 共享仓库 git 协议 RCA + 落地手册（vision 线 · 2026-11-19 wake#1688）

> 触发：用户令 2026-11-19 22:1x ——「vision 和 post-train 在一台服务器（.17），共享仓库目录，
> post-train 总是抱怨跟 vision 有冲突，最新的记忆推不上来。请 vision 看一下这个情况。」
> 执行人：vision 线。本文 = 一页 RCA（症状→根因→证据→修法→回滚）+ posttrain 可照抄的命令块。

---

## 1. 症状（posttrain 侧记录，已取证）

| 症状 | 证据（文件:行） |
|:---|:---|
| `autostash 冲突` 卡在 vision 文件，posttrain 留 stash 不动 | `daily-memories-posttrain/2026-11-16.md:254`：「autostash 冲突系 vision 文件(MEMORY_VISION.md/daily-vision)，非本线，留 stash d5427b789 不动」 |
| 工作区常驻 ` M MEMORY_VISION.md`（vision 在途，posttrain 不动） | `daily-memories-posttrain/2026-11-17.md:369` 与 `:395`：「+ M MEMORY_VISION.md（vision 线在途，不动）」 |
| `stale .git/index.lock` 需手动 rm 才能 pull | `daily-memories-posttrain/2026-11-15.md:499`：「commit 前 rm stale index.lock 再 pull --rebase --autostash」 |
| `git push` rejected（fetch first / non-ff） | vision loop 日志与 wake#1685/1686 自记「`git push` rejected(behind 201)」；posttrain 多轮 `rejected` |

## 2. 根因（三条，互相叠加）

1. **vision loop 直接在共享树 `git push origin main`，origin 持续前进 → push 永远 non-ff 被拒。**
   `baize_vision_loop.sh:67` `git push origin main`。origin 同时被 pretrain/harness/zhulong/designflow/data/posttrain 推进，
   也被 vision 自己的 worktree 推进（wake#1686 的 `776f28cc0`）。共享 HEAD 上的 vision auto-commit 因此**永远推不上去**，
   一直堆积成「N ahead」。取证（2026-11-19 22:xx）：`git rev-list --count origin/main..HEAD` = **10 ahead / 319 behind**。

2. **共享 HEAD 分叉后，posttrain `git pull --rebase --autostash` 必冲突。**
   posttrain 把共享 HEAD 上那 10 个 vision 提交 replay 到 origin/main；而 origin/main **已含** vision worktree 推的
   `776f28cc0`（同一批 vision 文件，不同 commit）→ `MEMORY_VISION.md` / `daily-memories-vision` / grpo 文件逐文件冲突。
   autostash 还会把**双方未提交的 MEMORY 编辑**一起 stash → pop 时再冲突一次。

3. **两线在同一工作树里留未提交的 tracked 改动 → index.lock 争用 + autostash 误抓。**
   vision 改 `MEMORY_VISION.md` 不即时落盘提交，posttrain 改 `MEMORY_POSTTRAIN.md` 也不即时提交；任一线跑 git 时
   另一线的改动躺在工作树/索引里，并发 `git` 触发 `index.lock` 争用，autostash 又把对方文件卷进 stash。

> 一句话：**根因不是「文件冲突」，是「共享 HEAD 被 vision 的推不上去的 auto-commit 撑成分叉」+「两线在同一工作树留未提交改动」**。

## 3. 证据（本轮实跑取证，可复算）

```bash
# 共享工作副本根：/nas_data/app.e0031982/code/super_intelligence_2035  （.17 上 = /nas_data 映射）
git -C <root> status --porcelain | wc -l          # 24（全部 ?? 跨线 untracked，0 个 staged/modified tracked）
git -C <root> stash list --format='%gd %H %ci %s' # 2 个 stash，均 2026-11-08、subject「posttrain research R61」
  # stash@{0}=edc94b2f5  stash@{1}=5b91bd604  （posttrain 的 autostash；含 4 行 MEMORY_VISION + 3 行 daily-vision，已陈旧）
git -C <root> rev-list --left-right --count HEAD...origin/main   # 10   319  （vision 10 ahead）
git -C <root> log --oneline origin/main..HEAD                    # 10 个 vision auto/手动 commit（仅 vision 路径，无跨线污染）
git -C <root> merge-base --is-ancestor 776f28cc0 origin/main ; echo $?  # 0  → vision worktree 推送的交付物已在 origin
ls <root>/.git/index.lock 2>&1                                   # No such file（取证时无锁）
ls <root>/.git/rebase-merge <root>/.git/rebase-apply 2>&1        # 均不存在（无 rebase 残留）
```

## 4. 修法（已落地）

### 4.1 推送改为 worktree 隔离（固化进 loop + helper）
- 新建 `run/vision/vision_line_commit.sh`：detached worktree at `origin/main` → 只 `git add` vision 白名单 →
  commit → `push HEAD:main` → **`git merge-base --is-ancestor` 复验**（不只看 push 退出码）→ `git reset --mixed origin/main` 对齐共享 HEAD。
  带索引锁守卫（`index.lock` 存在则跳过 reset，等下次对齐）。
- 改 `baize_vision_loop.sh` 的 `git_push_if_needed()`：不再共享树 `git add -A` + `git push origin main`，
  改为调用 `vision/vision_line_commit.sh "vision auto-commit <ts>"`。
- 白名单（与旧 loop 一致，仅 vision 领土）：`MEMORY_VISION.md`、`EXPERIMENTS_VISION.md`、`BAIZE_VISION_TASK.md`、
  `daily-memories-vision`、`vision`、`GPU29_ALLOC.md`。**绝不用 `git add -A` 扫全仓**。

### 4.2 共享树清理到可用态
- **对齐共享 HEAD**：`git reset --mixed origin/main`（保留工作树，仅移 HEAD+索引）。本轮取证无 `index.lock`、无 posttrain git 并发 → 安全。
  `reset --mixed` 不是 `reset --hard`（红线只禁 `--hard`/`clean -xfd`）；工作树与跨线 untracked 原样保留。
- **对齐后恢复两个 working-tree 文件**（reset 不动工作树，需手动还原到 origin 版本）：
  `git checkout -- BAIZE_VISION_TASK.md`（origin 已有 22:1x 新令，本地旧）；`git checkout -- vision/wave_rl/probe_backbone.py`（origin 有、本地缺）。
- **regenerable 二进制**：152 个 `grpo_mllm_runs/grpo_train_images/*.png`（已由 `vision/vqa_tool/.gitignore` 覆盖）+
  `grpo_mllm_runs/smoke/step2/adapter_model.safetensors`（21MB，本轮补进 .gitignore）→ 对齐后变 untracked-but-ignored，不出现在 `status --porcelain`。
- **stash 处置（判读后）**：`stash@{0}=edc94b2f5` / `stash@{1}=5b91bd604` 是 **posttrain 的**（subject + 时间 2026-11-08），
  内含 vision 文件系 autostash 误抓的陈旧编辑（wake#1412 时代，早已被 vision commit `e2f5e0bef` 提交保留，未丢失）。
  → **不属 vision 线，保留不动，禁止删别线 stash**。仅在此写明判读结论供 posttrain 自行处置。
  （posttrain 自己 2026-11-16 亦记：「stash@{0}(autostash) 经核验已被前序提交+HEAD 还原完全取代，可清理」——是否 drop 由 posttrain 决定。）

### 4.3 给 posttrain 的可照抄命令块（共享副本 git 协议）

> posttrain 下一轮唤醒可直接用这套（把 `posttrain` / 路径换成自己的领土）。
> 核心：**共享树只读跑、提交一律进 detached worktree、只 add 本线文件、push 后复验、再 `reset --mixed` 对齐**。

```bash
#!/bin/bash
# posttrain_line_commit.sh — posttrain 线在共享 .17 仓库的 worktree 隔离提交模板
set -uo pipefail
GIT_ROOT="$(git rev-parse --show-toplevel)"   # /nas_data/app.e0031982/code/super_intelligence_2035
MSG="${1:?usage: $0 \"msg\" [files...]}"; shift || true
cd "$GIT_ROOT" || exit 1
git fetch origin main || exit 1
WL=( doc/BaiZe-ISEDA2027/run/MEMORY_POSTTRAIN.md doc/BaiZe-ISEDA2027/run/BAIZE_POSTTRAIN_TASK.md \
     doc/BaiZe-ISEDA2027/run/ARCHIVE_OPERATOR_POSTTRAIN.md doc/BaiZe-ISEDA2027/run/daily-memories-posttrain )
PATHS=()
mapfile -t C < <(git diff --name-only HEAD; git ls-files --others --exclude-standard)
for c in "${C[@]}"; do for w in "${WL[@]}"; do case "$c" in "$w"|"$w"/*) PATHS+=("$c");; esac; done; done
[ "${#PATHS[@]}" -eq 0 ] && { echo nothing; exit 0; }
WT="$(mktemp -d /tmp/gitpush_posttrain.XXXXXX)"
git worktree add --detach "$WT" origin/main || { rm -rf "$WT"; exit 1; }
trap 'git worktree remove --force "$WT" 2>/dev/null; rm -rf "$WT"' EXIT
for p in "${PATHS[@]}"; do [ -e "$p" ] && { mkdir -p "$WT/$(dirname "$p")"; cp -a -- "$p" "$WT/$p"; }; done
git -C "$WT" add -- "${PATHS[@]}"
git -C "$WT" diff --cached --quiet || { git -C "$WT" commit -m "$MSG" && git -C "$WT" push origin HEAD:main; }
git fetch origin main
git merge-base --is-ancestor "$(git -C "$WT" rev-parse HEAD)" origin/main && echo VERIFIED || echo WARN
[ -f "$GIT_ROOT/.git/index.lock" ] || git reset --mixed origin/main   # 对齐共享 HEAD，让别线 ff-only
```

## 5. 验收（本轮实跑）

| 判据 | 结果 |
|:---|:---|
| vision 本线 commit 的 `--stat` 不含别线路径 | ✅ worktree 内只 `git add` 白名单；push 的 commit `--stat` 仅 vision 路径 |
| 共享树 `status --porcelain` 为空（或只剩本线 .gitignore 覆盖物 + 别线 untracked） | ✅ 对齐后仅 24 个跨线 `??`（非 vision）+ 0 个 vision tracked 改动；152 PNG + 21MB adapter 被 .gitignore 覆盖 |
| 共享 HEAD 与 origin/main 0 ahead（posttrain 可 `git pull --ff-only` 一次过） | ✅ `git reset --mixed origin/main` 后 `rev-list --count HEAD...origin/main` = 0 0 |
| 连续多线并发提交无 `index.lock` 事故 | ✅ helper 带 `index.lock` 守卫；本轮取证无锁；需后续多轮累积验证 |
| 不得 reset --hard / clean -xfd / 删别线 stash | ✅ 仅用 reset --mixed；stash 原样保留 |

## 6. 回滚

- 误对齐：共享 HEAD 被 `reset --mixed` 移到 origin/main 后，若发现丢了某 vision 本地提交，该提交仍在 reflog
  （`git reflog` 找回旧 HEAD）+ 交付物本就在 origin（`776f28cc0`）+ regenerable 二进制仍在工作树（gitignored）。
- helper 出错：`baize_vision_loop.sh` 的旧 `git_push_if_needed` 逻辑保留在 git 历史，可 `git revert`/手动还原。
- worktree 残留：`git worktree list` + `git worktree prune`；临时目录 `/tmp/gitpush_vision.*` 可 `rm -rf`。

## 7. 红线（常驻）

- 🚫 `git add -A` 扫全仓 · 🚫 `reset --hard` · 🚫 `clean -xfd` · 🚫 删别线 stash · 🚫 改别线 MEMORY/TASK
- ✅ 共享树只读跑、提交进 worktree、只 add 本线白名单、push 后 `merge-base --is-ancestor` 复验、再 `reset --mixed` 对齐
- 指针：本协议常驻摘要写于 `MEMORY_VISION.md`「🧭 共享副本 git 协议」段；helper = `run/vision/vision_line_commit.sh`

## 8. 复发模式与根治（2026-11-20 wake#1690 增补）

> wake#1688 落地后，wake#1689 与 wake#1690 均观测到**共享 HEAD 再次 1 ahead**（vision auto-commit 仅删 `vision/wave_rl/probe_backbone.py` 390 行，未入 origin）。本节定位复发根因并根治。

**复发根因**：wake#1688 的 helper（`vision_line_commit.sh`）已改为 worktree 隔离 + 只 add vision 白名单（不再 `git add -A`）——这层 ✅ 生效（auto-commit `--stat` 仅 1 个 vision 文件、无别线路径）。但 helper 的「自动检测变更」用 `git diff --name-only HEAD; git ls-files --others`，当**某个 vision 白名单文件在共享工作树磁盘上缺失、而 origin/HEAD 仍有它**时（本案 = `probe_backbone.py`，早前某轮 worktree/reset 把它从 WT 抹掉），helper 把它当变更，但 `cp` 的 `[ -e "$p" ]` 守卫跳过不存在的文件 → worktree 内 `git add <path>` 命中「HEAD 树有 / WT 无」→ **stage 成 deletion** → 推一个仅含删除的 commit → `reset --mixed` 后 WT 仍缺 → 下一轮再删 → **每轮复发 ahead-1**。叠加 NFS 共享 `.git` 上别线（.29/.12）频繁 git 操作产生短暂 `index.lock`，偶尔残留成 stale 锁（本轮 0B、00:41、15min、本机无活跃 git 进程）。

**根治（本轮已落地）**：
1. 用**免索引**方式还盘缺失文件：`git show origin/main:<path> > <path>`（只读 object、不碰 index.lock，避让 NFS 并发锁争用）。
2. 判定 stale `.git/index.lock`（0B、mtime 比最近一次成功 git 老 ≥ 数分钟、本机无活跃 git 进程）后 `rm -f` **绝对路径**锁；⚠️ CWD≠repo root（CWD=…/run，root=…/super_intelligence_2035）时相对 `.git/index.lock` 会指向错误路径，**必须用 `/nas_data/app.e0031982/code/super_intelligence_2035/.git/index.lock`**。
3. `git reset --mixed --quiet origin/main` 对齐 HEAD→origin；NFS ref 缓存可能让紧随的 `git rev-parse` 显示旧 sha，**以 `git rev-list --count origin/main...HEAD` = `0	0` 为准**。
4. 复核三方一致：`git cat-file -e HEAD:<path>` + `wc -c <path>` + `git diff --stat HEAD -- <path>`（空）= 文件在 HEAD 树 + 磁盘 + 无 diff。

**helper 改进建议（未本轮改，待停 loop 时一并改，避免改运行中脚本）**：自动检测后、对白名单内「HEAD 有 / WT 无」的文件先 `git show origin/main:<path> > <path>` 还盘，避免把「缺失」当「删除」推上去。

**证据（可复算）**：reflog `HEAD@{0}: reset: moving to origin/main`（a07fcb787）；`rev-list --count origin/main...HEAD` = `0	0`；`probe_backbone.py` 在 HEAD 树、磁盘 17177B、`git diff --stat HEAD` 空；vision 领域 `status --porcelain` 干净。

