# GIT_SYNC_README.md — 本仓 `git pull/push` 故障的根因与修法

> 2026-11-07 运维诊断与修复记录。适用于 `D:\Users\Administrator\code\super_intelligence_2035`（Windows 工作树）。

## 1. 症状（修复前）

- `git pull` / `git rebase` 经常**卡 30s 以上被超时打断**，留下半途 rebase；
- 之后所有 git 命令报 `Unable to write index` / `It seems that there is already a rebase-merge directory`；
- `git push` 反复 `! [rejected] main -> main (fetch first)`；
- `git count-objects` 报 `garbage found: .git/objects/pack/tmp_pack_*` ×17。

## 2. 三个根因

| # | 根因 | 证据 | 后果 |
|:--|:--|:--|:--|
| 1 | **`blob:none` 部分克隆** | `git config remote.origin.partialclonefilter` = `blob:none`，`promisor=true` | 每次 merge/rebase 都要按需 `fetch --filter=blob:none` 把改动文件的 blob 从 GitHub 逐个/分批拉回（走 SSH + 代理），133 个提交的合并要花数分钟，容易被 30s 超时打断 |
| 2 | **同一工作树三方并发** | robot loop（整点兜底 sync）、cline agent（自己 commit）、运维（手工提交）都用 `D:\...\super_intelligence_2035` | `index.lock` 争用 → `Unable to write index`；被 kill 的 rebase 留下 `rebase-merge/` |
| 3 | **pack 碎片化** | 1760 个 `.pack` + 4415 个松散对象 + 17 个 `tmp_pack_*` | 每次操作要扫大量 pack；tmp_pack 是打断的 fetch 残留 |

## 3. 修法（已落地）

1. **脚本 `run/ops/git_sync.ps1`**（本目录）：
   - `-Status`：体检（promisor/filter/ahead-behind/pack 数/锁/是否有 git 在跑）；
   - 默认：`fetch -> merge --no-edit -> push`，每步**最多重试 5 次**，指数退避；
   - 失败时自动判断错误类型：`index.lock`/`Unable to write index` → 仅在**没有 git 进程**时清残留锁与 `rebase-merge/`；`rejected/fetch first` → 先 fetch 再试；
   - `-Maintenance`：清 `tmp_pack_*` → `fetch --refetch --filter=blob:limit=200k`（把小文件 blob 一次性取回，之后 merge 不再逐个懒拉）→ `gc --prune=now` → `repack -a -d` → 设 `gc.auto=0`。
2. **不用 rebase 用 merge**：多 agent 高频提交下 rebase 容易留半途状态；merge 一次成型，冲突只出现在文件级。
3. **`gc.auto=0`**：避免评测/训练跑到一半触发自动 gc 抢锁，改为手工 `-Maintenance`。
4. **日志**：`run/ops/logs/git_sync_YYYYMMDD.log`（已在 `run/ops/.gitignore` 忽略，不入库）。

## 4. 已知坑（踩过的）

| 坑 | 现象 | 正确做法 |
|:--|:--|:--|
| PowerShell 5.1 读无 BOM 的 UTF-8 `.ps1` | 中文注释/字符串变乱码，报"字符串缺少终止符" | 脚本保存为 **UTF-8 with BOM** |
| 函数参数命名为 `$Args` | 与 PowerShell 自动变量冲突，git 收到空子命令（打印 `usage: git ...`） | 改名为 `$GitArgs` |
| `& git ... 2>&1 \| Out-String` | stderr 被吞、`$LASTEXITCODE` 误判为 1 | 用 `& cmd /c "git ... 2>&1"` 取真实退出码 |
| 直接删 `index.lock` | 若真有 git 在跑会损坏索引 | 先 `Get-Process git,ssh` 确认为空再删 |
| 冲突文件是**生成物**（如 `ZhuLong_DAC2027/reports/*.html`） | 手工合并没有意义 | `git checkout origin/main -- <path>` 取远端版，交给生成器下次覆盖 |

## 5. 用法

```powershell
# 体检
powershell -NoProfile -ExecutionPolicy Bypass -File run\ops\git_sync.ps1 -Status

# 日常同步（可后台：Start-Process powershell -ArgumentList ...）
powershell -NoProfile -ExecutionPolicy Bypass -File run\ops\git_sync.ps1

# 维护（建议在整点唤醒的间隙跑，例如每小时 :15-:45）
powershell -NoProfile -ExecutionPolicy Bypass -File run\ops\git_sync.ps1 -Maintenance
```

## 6. 并发约定（建议所有线遵守）

- **整点 :00–:05 是 robot loop 唤醒/收尾窗口**，运维手工提交尽量避开；
- 任何线在**同一工作树**做 git 操作前先 `git_sync.ps1 -Status`，看到 `gitBusy=True` 就等 30s；
- 提交只 `git add` 自己这条线的文件，🚫 不要 `git add -A`（会把别的线在途文件带进提交）。
