# SHARED_REPO_GIT_PROTOCOL.md — 一台机器上一份工作副本、多条 agent 线并发提交

> 运维文档（2026-11-19 22:0x）。**适用对象**：`.17` 上 `vision` 与 `posttrain`（以及任何后续加入的线）共用同一个
> `/nas_data/.../super_intelligence_2035` 工作副本的情况。
> 触发背景（用户 2026-11-19）：「vision 和 post-train 在一台服务器，共享仓库目录。之前 post-train 总是抱怨跟 vision 有冲突，
> 最新的记忆推不上来。」

---

## 1. 症状清单（都是同一根因的不同表现）

| 症状 | 典型报错 / 现象 | 出现在 |
|:--|:--|:--|
| 拉取被本线未提交改动挡住 | `error: Your local changes to the following files would be overwritten by merge/checkout` | posttrain 每轮 `pull` |
| rebase/autostash 冲突 | `Applying autostash resulted in conflicts`，stash 不敢 pop 也不敢 drop | posttrain 2026-11-16（stash `d5427b789` 卡在 `MEMORY_VISION.md` / `daily-memories-vision`） |
| 索引锁争用 | `Unable to create '.git/index.lock': File exists`；崩溃后残留锁让**整机所有线**都动不了 | 多线 10 分钟一轮时高发 |
| 推不上去 | `! [rejected] main -> main (fetch first)`，且 rebase 又会撞上面的冲突 | 落后几十个提交之后 |
| 半途 rebase | `.git/rebase-merge/` 残留，之后所有 git 命令报错 | 被超时/打断的 rebase |
| 提交里混入别线文件 | 一次 commit 的 `--stat` 里出现本线没碰过的路径 | 早期 `git add -A` 造成 |

## 2. 根因（4 条，按影响排序）

1. **单工作树 = 单 index + 单 HEAD**：两条线共用 `.git`，A 线 `add/commit/checkout/rebase/reset` 会读到并改动 B 线的**未提交改动**，反之亦然。这是冲突的第一性原因，跟谁"手重"无关。
2. **`git add -A` / `git add .` 把别线在途改动卷进自己的提交**：之后该提交与别线后续提交必然文本冲突；vision wake#1686 已记录"8 个 ahead 提交因旧 `-A` 卷入大量跨线文件 → rebase 必冲突"。
3. **长轮询周期 + 落后积累**：某线 3 天不唤醒（posttrain 11-17→11-19）→ behind 几十~上百提交 → 一次唤醒要 rebase 一大批，冲突概率与修复成本都放大。
4. **并发 git 进程抢 `index.lock`**：4+ 条线各 ~10 分钟一轮，撞锁概率不低；被 kill 的进程留下 stale lock，阻塞全部线。

## 3. 协议（A 方案 · 推荐 · 已实证）

**共享工作树只用于「读 + 跑」，不用于「提交」。所有推送在隔离 worktree 里做。**

```bash
SHARED=/nas_data/app.e0031982/code/super_intelligence_2035
WT=/tmp/gitpush_<line>            # 每线一个，互不干扰

# 0) 清理 stale 锁（仅在确认没有 git 进程时！）
pgrep -x git >/dev/null || { [ -f $SHARED/.git/index.lock ] && find $SHARED/.git/index.lock -mmin +2 -delete; }

# 1) 取最新远端
git -C $SHARED fetch origin main

# 2) 建/重建隔离 worktree（独立 index/HEAD，完全不动共享树）
git -C $SHARED worktree remove --force $WT 2>/dev/null
git -C $SHARED worktree add --detach $WT origin/main

# 3) 只把本线文件复制进去（白名单路径）
cd $SHARED && rsync -aR <本线文件相对路径...> $WT/

# 4) 只 add 白名单路径 + 提交
git -C $WT add -- <本线路径...>
git -C $WT -c user.name=<line>-agent -c user.email=<line>-agent@local commit -m "<line>: ..."

# 5) 推送（失败则本 worktree 内 rebase 远端后重试）
git -C $WT push origin HEAD:main

# 6) 可选：共享树干净时才快进共享 HEAD（脏就跳过，绝不 reset）
[ -z "$(git -C $SHARED status --porcelain)" ] && git -C $SHARED merge --ff-only origin/main
```

**已提供脚本封装**：`run/ops/git_line_commit.sh`

```bash
bash run/ops/git_line_commit.sh --line vision -m "vision wake#NNNN: ..." --dry-run   # 先看会提什么
bash run/ops/git_line_commit.sh --line vision -m "vision wake#NNNN: ..."              # 真推
bash run/ops/git_line_commit.sh --line vision -m "..." --sync-shared                  # 推完顺便快进共享树（仅当干净）
```

脚本内置：stale 锁检测（**只在无 git 进程且锁 >120s 时**清）、路径白名单（越界直接拒）、推送重试（fetch+rebase+retry ×3）、
`--dry-run`、以及"共享树脏就不快进"的保护。

## 4. 禁止事项（硬红线）

1. 🚫 在共享工作树上执行 `git reset --hard` / `git clean -xfd` —— 会静默销毁别线在途改动。
2. 🚫 在共享工作树上执行 `git rebase` / `git pull --rebase --autostash`（多线并发下极易留半途状态）；同步只用 `merge --ff-only`。
3. 🚫 `git add -A` / `git add .` / `git commit -a`；只允许显式路径或白名单。
4. 🚫 删/清别线的 `git stash`（`d5427b789` 这类卡住的 stash 必须由**其主人**判读后处理）。
5. 🚫 在不确定是否有 git 进程时删 `index.lock`（先 `pgrep -x git`）。

## 5. 各线路径白名单（脚本默认值）

| 线 | 允许路径（相对仓库根） |
|:--|:--|
| vision | `doc/BaiZe-ISEDA2027/run/vision/`、`doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md`、`doc/BaiZe-ISEDA2027/run/daily-memories-vision/`、`doc/BaiZe-ISEDA2027/run/reports/report_vision_*`、`doc/BaiZe-ISEDA2027/reports/report_vision_*`、`doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md`（只读，运维写） |
| posttrain | `doc/BaiZe-ISEDA2027/run/MEMORY_POSTTRAIN.md`、`doc/BaiZe-ISEDA2027/run/BAIZE_POSTTRAIN_TASK.md`、`doc/BaiZe-ISEDA2027/run/ARCHIVE_OPERATOR_POSTTRAIN.md`、`doc/BaiZe-ISEDA2027/run/daily-memories-posttrain/`、`doc/BaiZe-ISEDA2027/run/baize_posttrain_*`、`doc/BaiZe-ISEDA2027/run/attribution_3615_run*`、`doc/BaiZe-ISEDA2027/reports/report_posttrain_*`、`doc/BaiZe-ISEDA2027/run/POSTTRAIN_*` |
| pretrain | `doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md`、`run/daily-memories/`、`run/reports/report_pretrain_*`、`reports/report_pretrain_*`、`run/BAIZE_PRETRAIN_2B_TASK.md` |
| harness | `run/MEMORY_HARNESS.md`、`run/daily-memories-harness/`、`run/harness/`、`reports/report_harness_*`、`run/BAIZE_HARNESS_TASK.md` |
| data | `run/MEMORY_DATA.md`、`run/daily-memories-data/`、`run/data*/`、`run/reports/report_s1s2_*`、`run/BAIZE_DATA_TASK.md` |

> 需要临时跨线（如运维改别线任务书）时，**用运维身份在 Windows 侧提交**，不要在多线共享树上做。

## 6. 验收（这条令是否真的解决了）

- [ ] posttrain 下一次唤醒：`pull` → 改 MEMORY → `commit` → `push` **一次过，0 冲突，无 index.lock 等待**；
- [ ] 连续 3 轮多线并发（vision/posttrain/pretrain/harness 同时提交）不出现 `index.lock` 事故；
- [ ] 共享树 `git status --porcelain` 在每轮结束时为空（或只剩本线 `.gitignore` 覆盖物）；
- [ ] 任一线 commit 的 `--stat` 中**不含别线路径**（可用脚本的白名单保证）。

## 7. 回滚

若 worktree 方案在某台机器不可用（如 `/tmp` 空间不足或 NFS 上 `worktree` 有坑）：
退化为「**每线独立 clone + 只在 clone 里提交**」（`git clone --shared` 可省对象体积），共享树仅作只读镜像。
无论哪条路，**都不允许**回退到"多线共用一个 index 提交"的旧做法。
