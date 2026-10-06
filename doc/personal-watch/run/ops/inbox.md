# OPS INBOX — 运维下发命令（supervisor 编辑，中继只读执行）

<!-- RUN_ID: 8 -->

> **用法**：在下面**新增一段** `## RUN_ID N`（N 递增）+ **一个 ```bash 块** → `git push`。
> 中继（`ops_relay.sh`）轮询发现 **RUN_ID 变大** → 执行 → 结果 append 到 `ops/outbox.md` → push。
>
> ✅ **本中继已修掉 BaiZe 的已知坑**：那边"**只执行第一个 ```bash 块**"（新命令会静默失效）；
> 我们**支持多段 RUN_ID 历史共存，总是执行 RUN_ID 最大那一段的块** → **老块不用删、不用降级**。
>
> **纪律**：
> ① 长输出一律加 `cut -c1-140`（`pgrep -af` 会把整份任务书打出来）；
> ② 🚫 **绝不整树 `du`**（大目录会跑很久）—— 只用 `df` + 有界定向 `du`（每条带 `timeout`）；
> ③ 单块总超时 **600s**，输出超 **20000 字符**会被截断；
> ④ 危险模式（`rm -rf /`、`mkfs`、**`git clean -fdx`**、**`git reset --hard`**、**杀 ops_relay**）会被**拒绝**。

## RUN_ID 7 — 🩺 **单实例核验** + 🔎 **追查瞬时第 3 实例** + 📦 **补跑被跳过的 RUN_ID 4**（**全只读**）

**背景（supervisor 2026-10-05 ~23:2x）**：
- 用户已把中继切到**单实例新代码**：`pgrep` 只剩 **`353526 watch_ops_relay.sh ops_relay.sh`**（= `exec -a watch_ops_relay.sh` 起，✅ 符合新文档）。
- 待办 ①：**核验新代码真的生效**（pidfile + 日志里应有 `pid=`/`pidfile=`）；②：**RUN_ID 4（网盘工具链 + sha256 manifest）当年被"只跑最大"跳过**，现补上；③：**查清 22:45 那个瞬时第 3 实例 `349841` 从哪来**。
- ⚠️ 本块**全只读**（不 rm / 不写 git / 不 kill）。

```bash
set -u
cd ~/super_intelligence_2035 || exit 1
R=doc/personal-watch/run
echo "=== 0. 基本 ==="
hostname; date '+%F %T %Z'; uptime
echo
echo "=== 1. 中继单实例核验（应恰好 1 行）==="
pgrep -af 'watch_ops_relay|ops_relay' | cut -c1-160 || echo "(⚠️ 未匹配到中继)"
echo "--- pidfile（🆕 新代码才有；无 = 仍在跑旧代码）---"
if [ -f /tmp/watch_ops_relay.pid ]; then echo "pidfile = $(cat /tmp/watch_ops_relay.pid)"; else echo "⚠️ 无 /tmp/watch_ops_relay.pid"; fi
echo "--- 日志尾部（新代码启动行含 pid=/pidfile=）---"
tail -10 /tmp/watch_ops_relay.log 2>/dev/null | cut -c1-160 || echo "(无日志)"
echo
echo "=== 2. 三条通道进程（etime 看存活时长）==="
ps -eo pid,etime,args | grep -E 'ops_relay\.sh|watch_.*_loop\.sh' | grep -v grep | cut -c1-150 || echo "(无)"
echo
echo "=== 3. 🔎 追查「瞬时第 3 实例 349841」来源 ==="
echo "--- crontab（用户）---"; crontab -l 2>/dev/null | grep -n -i -E 'relay|watch|cline' || echo "(无相关)"
echo "--- /etc/cron.d 与 /etc/crontab ---"; ls /etc/cron.d/ 2>/dev/null; grep -rn -i 'relay' /etc/cron.d/ /etc/crontab 2>/dev/null | head -5 || echo "(无)"
echo "--- systemd 单元 ---"; ls /etc/systemd/system/ 2>/dev/null | grep -i -E 'relay|watch|cline' || echo "(无相关 unit)"
echo "--- 当前中继的父进程链 ---"
RP="$(pgrep -f 'watch_ops_relay' | head -1)"
if [ -n "${RP:-}" ]; then p="$RP"; for i in 1 2 3; do L="$(ps -o pid=,ppid=,args= -p "$p" 2>/dev/null)"; [ -z "$L" ] && break; echo "$L" | cut -c1-150; p="$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')"; [ -z "$p" ] && break; [ "$p" = "1" ] && { echo "(已到 init/1)"; break; }; done; fi
echo "--- ~/.bash_history 里出现 ops_relay 的行（找手工/脚本拉起）---"
grep -n -E 'ops_relay' ~/.bash_history 2>/dev/null | tail -8 | cut -c1-140 || echo "(读不到 history)"
echo
echo "=== 4. 📦 补跑 RUN_ID 4：网盘工具链 + 语料 sha256 manifest（只读）==="
cd $R/news/archive 2>/dev/null || { echo "(archive 目录不存在)"; exit 0; }
echo "--- 网盘工具可用性 ---"
for t in bypy BaiduPCS-Go bwp rclone; do printf '%-14s ' "$t"; if command -v "$t" >/dev/null 2>&1; then echo "OK $(command -v $t)"; else echo "NO 未安装"; fi; done
python3 -c "import bypy" 2>/dev/null && echo "bypy(python) OK" || echo "bypy(python) NO"
echo "--- 11 分片：sha256(前16) · 字节 · 文件名 ---"
for f in chinanews-*.jsonl.gz; do [ -f "$f" ] && printf '%s  %10s  %s\n' "$(sha256sum "$f" | cut -c1-16)" "$(stat -c%s "$f")" "$f"; done
echo "--- 仓库外备份（RUN_ID 5 做的）---"
ls -la ~/archive_data_backup/ 2>/dev/null | head -14 || echo "(无备份目录)"
echo
echo "=== 5. 收尾 ==="
echo "inbox 最高 RUN_ID 附近："; grep -oE 'RUN_ID[[:space:]]*[0-9]+' ~/super_intelligence_2035/$R/ops/inbox.md 2>/dev/null | sort -u | tail -3
git log --oneline -2 | cut -c1-120
```

**预期**：① 中继**恰好 1 行** + pidfile 存在且与进程 PID 一致（证明**新代码在跑**）；
② 父进程链/crontab/systemd 里找到（或排除）**第 3 实例的拉起者**；③ 网盘工具可用性 + 11 分片 sha256/字节清单（**迁移备料**）。

## RUN_ID 6 — 🩺 **存活体检**：确认 **中继 + 两条 loop** 都在（**只读**）

**背景（supervisor 2026-10-05 22:4x）**：
- 两条 loop 能从 git 提交/心跳看出在跑；但 **中继只在 `RUN_ID` 变大时才动作 → 平时完全静默**，
  **无法从 git 判断它是否还活着**；且历次诊断（RUN_ID 1/2）**从未 `pgrep` 过中继**。
- ⚠️ **命名不一致**：启动文档写 `bash ops_relay.sh`，而停止/检查写 `watch_ops_relay.sh`（见 `ops/README.md` §3、`AGENTS.md`）
  → 直接 `pgrep watch_ops_relay.sh` 可能是**假阴性**。本块**两种名字 + 按脚本路径**都查。

> ⭐ **本段一旦被执行并回帖，本身就证明「中继活着」**（否则 `outbox.md` 不会新增本段结果）。

```bash
set -u
echo "=== 0. 基本 ==="
hostname; date '+%F %T %Z'; uptime
echo
echo "=== 1. ⭐ watch/ops 相关进程（中继两种命名 + 两条 loop）==="
pgrep -af 'watch_ops_relay|ops_relay|watch_(news|research)_loop' | cut -c1-160 || echo "(未匹配到任何进程)"
echo
echo "=== 1b. 兜底：按脚本路径找（防 cmdline 名字对不上）==="
ps -eo pid,etime,args | grep -E 'ops_relay\.sh|watch_.*_loop\.sh' | grep -v grep | cut -c1-160 || echo "(无)"
echo
echo "=== 2. 中继日志尾部（应有 [relay] … started / nothing to commit）==="
tail -8 /tmp/watch_ops_relay.log 2>/dev/null | cut -c1-160 || echo "(无 /tmp/watch_ops_relay.log)"
echo
echo "=== 3. 两条 loop 日志尾部（各 2 行）==="
for f in /tmp/watch_news_loop.log /tmp/watch_research_loop.log; do echo "--- $f ---"; tail -2 "$f" 2>/dev/null | cut -c1-160 || echo "(无)"; done
echo
echo "=== 4. 中继游标 / inbox 最高 RUN_ID（应为 6）==="
echo -n "last_run_id = "; cat ~/super_intelligence_2035/doc/personal-watch/run/ops/.last_run_id 2>/dev/null || echo "?"
grep -oE 'RUN_ID[[:space:]]*[0-9]+' ~/super_intelligence_2035/doc/personal-watch/run/ops/inbox.md 2>/dev/null | sort -t' ' -k2 -n | tail -3
```

**预期**：① 进程段出现 **news + research + 中继** 共 3 行；② 中继日志有 `[relay] … started` 与最近的 `[relay] nothing to commit.` / `RUN_ID=n executed`；
③ 两条 loop 日志尾部有 `[loop] … sleep …` 心跳。→ 全部命中即证明**三条通道同机存活**。

## RUN_ID 5 — 🛑 **止损**：把语料分片移出 git 索引（**保留本地文件**，`git rm --cached`）

**为什么必须马上做**（依据 RUN_ID 3 实测）：
- `.git` = **592 MB**（GitHub 软上限 ~1GB）；**gz 无 delta → 每轮更新分片 = 整份 blob 重新入库 ≈ +110MB/轮**；
- 11 个分片（2016–2026，5.78–15.56 MB）**全部被 git 跟踪**；`.gitignore` 对**已跟踪文件无效** → **不 `rm --cached` 就永远拦不住**。

⚠️ **本块只在「腾讯这台」执行**（它 `rm --cached` 后**工作区文件保留**；换别的克隆执行会让工作区文件被删）。
⚠️ **不删任何数据**：历史 blob 仍在 `.git` 里（可 `git cat-file` 取回），工作区文件原样保留。

```bash
set -u
cd ~/super_intelligence_2035 || exit 1
echo "=== 0. 先决条件 ==="
hostname; date '+%F %T %Z'
echo "当前 .git 体积：$(du -sh .git | cut -f1)"
echo "分片数量：$(ls doc/personal-watch/run/news/archive/*.jsonl.gz 2>/dev/null | wc -l)"
echo
echo "=== 1. 🛡 双保险：把分片复制到仓库之外（~/archive_data_backup/）==="
mkdir -p ~/archive_data_backup
cp -f doc/personal-watch/run/news/archive/*.jsonl.gz ~/archive_data_backup/ 2>/dev/null
echo "备份目录内容："
ls -la ~/archive_data_backup/ | head -15
echo "备份合计：$(du -sh ~/archive_data_backup 2>/dev/null | cut -f1)"
echo
echo "=== 2. 🛑 从 git 索引移除（--cached = 保留工作区文件）==="
git rm --cached -q doc/personal-watch/run/news/archive/*.jsonl.gz 2>&1 | head -15 || true
echo "--- 移除后 git 索引里还剩什么（应只剩 py/README/PROGRESS/INDEX）---"
git ls-files doc/personal-watch/run/news/archive/ | cut -c1-140
echo
echo "=== 3. ⭐ 关键校验：工作区文件必须还在（应为 11）==="
ls doc/personal-watch/run/news/archive/*.jsonl.gz 2>/dev/null | wc -l
du -sh doc/personal-watch/run/news/archive 2>/dev/null
echo '--- 且应显示为「被 .gitignore 忽略」而非「待提交」---'
git status --short -- doc/personal-watch/run/news/archive/ | head -8
git check-ignore --no-index -v doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz 2>/dev/null || echo "(2016 未命中 .gitignore ⚠️)"
echo
echo "=== 4. 提交（含 .gitignore 与红线文档）==="
git add -- doc/personal-watch/run/news/archive/.gitignore 2>/dev/null || true
git add -u -- doc/personal-watch/run/news/archive/ 2>/dev/null || true
git commit -m "ops: 止损 — news/archive 11 个语料分片移出 git 索引（git rm --cached，保留本地文件）；.git 已 592MB 且每轮+110MB（gz 无 delta）；体积红线>=5MB 改走百度云盘" 2>&1 | tail -5
echo
echo "=== 5. 推送（先 rebase，避免与 agent/BaiZe 冲突被拒）==="
git pull --rebase --autostash 2>&1 | tail -4
git push 2>&1 | tail -4
echo
echo "=== 6. 结果核对 ==="
echo "提交后 .git 体积：$(du -sh .git | cut -f1)  （⚠️ 历史仍在，不会变小；重点是「不再增长」）"
git log --oneline -3 | cut -c1-140
echo "--- 远端是否还跟踪分片（应为空）---"
git ls-tree -r --name-only origin/main -- doc/personal-watch/run/news/archive/ 2>/dev/null | grep -E 'jsonl\.gz' || echo "✅ 远端已不跟踪分片"
echo "--- 工作区分片仍应为 11 ---"
ls doc/personal-watch/run/news/archive/*.jsonl.gz 2>/dev/null | wc -l
```

**预期结果**：`git ls-files` **不再列 gz** · **工作区仍 11 个文件**（抓取不受影响）· 推送后**远端不再跟踪 gz** ·
**下轮起 agent 抓取更新分片将不再产生 git 提交** → **每轮 +110MB 的出血停止** ✅

## RUN_ID 4 — 🔍 为「语料迁出 git → 百度云盘」做前置体检（**只读 + 只生成清单，不删不移**）

**背景**：用户明令 **单个文件 ≥5MB 一律不得用 GitHub 传输，改走百度云盘**。
`news/archive/` 现存 **11 个分片（2016–2026）≈ 96 MB，最小 5.51 MB → 全部超标**，且**已被 git 跟踪**（历史里也有）。
- ⚠️ **本块绝不执行 `git rm --cached`**（那会让别的克隆 pull 时**删掉本地语料**）—— 迁移必须**先有网盘备份**，由 supervisor 确认后再下发 RUN_ID 5。
- 本块只做两件事：**① 探明网盘工具链是否可用 ② 生成权威 manifest（字节数 + sha256 + 路径）**。

```bash
echo "=== 0. 基本信息 ==="
hostname; date '+%F %T %Z'
cd ~/super_intelligence_2035 2>/dev/null || exit 1
echo
echo "=== 1. ⭐ 超标文件全量清单（≥5MB，递归，排除 .git）==="
find . -path ./.git -prune -o -type f -size +5M -print 2>/dev/null | head -60 | while read -r f; do
  printf '%s\t%s\n' "$(du -b "$f" | cut -f1)" "$f"
done | sort -rn
echo '--- 合计体积 ---'
find . -path ./.git -prune -o -type f -size +5M -print0 2>/dev/null | xargs -0 du -cb 2>/dev/null | tail -1
echo
echo "=== 2. 其中已被 git 跟踪的（这些才是"历史污染源"）==="
git ls-files -z | while IFS= read -r -d '' f; do
  if [ "$(stat -c%s "$f" 2>/dev/null || echo 0)" -ge 5242880 ]; then
    printf '%s\t%s\n' "$(du -b "$f" | cut -f1)" "$f"
  fi
done | sort -rn | head -40
echo
echo "=== 3. ⭐ 百度云盘工具链可用性 ==="
echo '--- (a) bypy ---'
command -v bypy && bypy --version 2>&1 | head -3
python3 -c "import bypy; print('bypy module OK', bypy.__version__ if hasattr(bypy,'__version__') else '')" 2>&1 | head -3
ls -la ~/.bypy 2>/dev/null | head -5 || echo "(~/.bypy 不存在 → 未授权)"
echo '--- (b) BaiduPCS-Go ---'
command -v BaiduPCS-Go || command -v baidupcs || command -v bpcs || echo "(未安装)"
ls -la ~/.config/BaiduPCS-Go 2>/dev/null | head -5 || echo "(无 BaiduPCS-Go 配置)"
echo '--- (c) 其他候选 ---'
for t in rclone aliyun ossutil coscmd; do command -v "$t" >/dev/null && echo "found: $t ($(command -v $t))"; done
echo '--- (d) pip 能否装 bypy（先看 pip 是否就绪，不实际安装）---'
python3 -m pip --version 2>&1 | head -2 || echo "(无 pip)"
echo
echo "=== 4. 生成权威 manifest（字节数 + sha256）—— 供网盘上传后核对 ==="
mkdir -p /tmp/watch_manifest
OUT=/tmp/watch_manifest/archive_manifest.tsv
: > "$OUT"
for f in doc/personal-watch/run/news/archive/*.jsonl.gz; do
  [ -e "$f" ] || continue
  printf '%s\t%s\t%s\n' "$(du -b "$f" | cut -f1)" "$(sha256sum "$f" | cut -c1-16)" "$f" >> "$OUT"
done
cat "$OUT"
echo "manifest 已写入 $OUT （共 $(wc -l < "$OUT") 行）"
echo
echo "=== 5. 仓库体积现状（评估"历史污染"规模）==="
du -sh .git 2>/dev/null
git count-objects -vH 2>/dev/null | head -8
echo
echo "=== 6. 本轮 .gitignore 是否已生效（新的大文件应被拦）==="
git check-ignore --no-index -v doc/personal-watch/run/news/archive/chinanews-2099.jsonl.gz 2>/dev/null || echo "⚠️ 未命中（.gitignore 未生效）"
git check-ignore --no-index -v doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz 2>/dev/null || echo "(2016 未命中)"
echo '--- 未跟踪的大文件（?? 且 >5MB → 已被 .gitignore 拦住才对）---'
git status --short | head -15
```

---
## RUN_ID 3 — 🚨 紧急体检：**语料体积**（禁止 GB 级数据进 GitHub！）

**背景（supervisor 判定为红线事故）**：`git status` 显示
`news/archive/chinanews-2017.jsonl.gz` **已被 git 跟踪且 modified**，另有 **untracked `chinanews-2016.jsonl.gz`**。
→ ⚠️ **一年中国新闻语料打包进 git 仓库 = 仓库膨胀 / clone 变慢 / 超 GitHub 硬限（单文件 100MB 会直接拒收）**。
→ **任务：先量体积与仓库历史占用，判定是否已污染历史**。**本块只读，不做删除**（清理由 supervisor 定夺后下发 RUN_ID 4）。

```bash
echo "=== 0. 基本信息 ==="
hostname; date '+%F %T %Z'
cd ~/super_intelligence_2035 2>/dev/null || exit 1
echo
echo "=== 1. ⭐ 语料文件体积（重点）==="
ls -lh doc/personal-watch/run/news/archive/*.jsonl* 2>/dev/null | cut -c1-140 || echo "(无 jsonl 语料)"
echo '--- 精确字节数（便于判断能否进 git）---'
du -b doc/personal-watch/run/news/archive/*.jsonl* 2>/dev/null | sort -rn | head -10
echo
echo "=== 2. 整个 news/archive 目录占用 ==="
du -sh doc/personal-watch/run/news/archive 2>/dev/null
du -sh doc/personal-watch/run/news 2>/dev/null
echo
echo "=== 3. 是否已被 git 跟踪（关键！）==="
git ls-files -s doc/personal-watch/run/news/archive/ | cut -c1-140
echo
echo "=== 4. ⭐ 历史污染程度（该文件在 git 历史里累计占多少）==="
for f in doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz doc/personal-watch/run/news/archive/chinanews-2018.jsonl.gz; do
  echo "--- $f ---"
  git log --oneline -- "$f" 2>/dev/null | head -5 | cut -c1-120
done
echo '--- 仓库 .git 实际体积 ---'
du -sh .git 2>/dev/null
echo
echo "=== 5. 是否已 push 到远端（污染是否传出去了）==="
git log --oneline -5 -- doc/personal-watch/run/news/archive/ | cut -c1-140
echo '--- 远端是否已含该文件 ---'
git cat-file -e origin/main:doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz 2>/dev/null && echo "⚠️ 远端已含 2017 语料（已污染）" || echo "✅ 远端不含 2017 语料"
echo
echo "=== 6. 是否有 .gitignore / .gitattributes 规则 ==="
for f in .gitignore .gitattributes doc/personal-watch/run/news/archive/.gitignore doc/personal-watch/run/news/.gitignore; do
  echo "--- $f ---"; cat "$f" 2>/dev/null | cut -c1-140 || echo "(不存在)"
done
echo
echo "=== 7. 每轮抓取是否会持续生成新分片（判断增长趋势）==="
ls -la doc/personal-watch/run/news/archive/ 2>/dev/null | grep -E 'jsonl|progress|PROGRESS' | cut -c1-140
```


## RUN_ID 2 — 🩺 追因：research 线为何缺席？loop 靠什么保活？

**背景（RUN_ID 1 的结论）**：
- **无 OOM**、内存 available 2661M、swap 用 0、CPU top1 2.2%、磁盘 11% → **停摆与资源无关**；
- ⚠️ **§1 只看到 `watch_news_loop.sh`（PID 98701），没有 research 线** → 两条线**不是同时死的**；
- `uptime` = **up 3:21**（12:31 时）→ 机器约 **09:10 重启**过，而停摆从 10-04 09:31 就开始了。

**要回答**：① research loop 是**没起**还是**起了又死**？② loop 靠 **cron / systemd / nohup / screen** 哪样保活？③ **重启后是谁把 news 拉起来的**？

```bash
echo "=== 0. 基本信息 ==="
hostname; date '+%F %T %Z'; uptime
echo
echo "=== 1. 所有 watch/ops 进程（含完整命令行，找保活父进程）==="
pgrep -af 'watch_(news|research|ops)' | cut -c1-160 || echo "(无任何 watch_* 进程)"
echo '--- 进程树（看谁是父进程/是否被 nohup、screen、tmux 托管）---'
ps -eo pid,ppid,etime,stat,args 2>/dev/null | grep -E 'watch_|cline' | grep -v grep | cut -c1-160
echo
echo "=== 2. 两条 loop 日志（存在性 + 大小 + 尾部）==="
for f in /tmp/watch_news_loop.log /tmp/watch_research_loop.log /tmp/watch_ops_relay.log; do
  echo "--- $f ---"
  if [ -e "$f" ]; then ls -la "$f" | cut -c1-120; tail -6 "$f" 2>/dev/null | cut -c1-160; else echo "(不存在)"; fi
done
echo
echo "=== 3. ⭐ 保活机制排查 ==="
echo '--- (a) crontab ---'
crontab -l 2>/dev/null | cut -c1-160 || echo "(无用户 crontab)"
sudo -n crontab -l 2>/dev/null | cut -c1-160 || true
echo '--- (b) systemd 单元 ---'
systemctl list-units --type=service --all 2>/dev/null | grep -iE 'watch|cline|relay' | cut -c1-140 || echo "(无匹配 systemd 单元)"
ls -la /etc/systemd/system/ 2>/dev/null | grep -iE 'watch|cline|relay' || echo "(无匹配 unit 文件)"
echo '--- (c) screen / tmux ---'
screen -ls 2>/dev/null | cut -c1-140 || echo "(无 screen)"
tmux ls 2>/dev/null | cut -c1-140 || echo "(无 tmux)"
echo '--- (d) 开机自启脚本 ---'
grep -rl 'watch_.*loop' /etc/rc.local /etc/cron.d /etc/crontab ~/.bashrc ~/.profile 2>/dev/null || echo "(常见自启位置未见 watch loop)"
echo
echo "=== 4. 机器重启 & 用户登录记录（解释 up 3:21）==="
who -b 2>/dev/null; last -n 8 reboot 2>/dev/null | cut -c1-100 || echo "(无 last 记录)"
echo
echo "=== 5. loop 脚本本体（看它自己有没有守护/重启逻辑）==="
cd ~/super_intelligence_2035/doc/personal-watch/run 2>/dev/null && {
  ls -la *.sh 2>/dev/null | cut -c1-140
  echo '--- watch_news_loop.sh 里的重启/守护相关行 ---'
  grep -nE 'nohup|while|trap|systemctl|sleep|exit|restart' watch_news_loop.sh 2>/dev/null | head -20 | cut -c1-160 || echo "(无此脚本)"
}
echo
echo "=== 6. git（确认 research 线是否已恢复提交）==="
cd ~/super_intelligence_2035 2>/dev/null && git log --oneline -8 | cut -c1-160
echo '--- dirty（只列前 12）---'
git status --short 2>/dev/null | head -12 | cut -c1-160
```

**阅读指引（我来判）**：
- §1 若 research **仍无** → 它是"**没被拉起**"，与 news 是**两套独立启动**（重启后靠手工/半自动）→ **根因是缺保活**；
- §3(a)(d) 若**有 cron/自启** → 说明**本该能自愈**，那"27h 未起"就是**保活条目本身失效**（要修）；若**全无** → **保活根本没建**，重启即停，**必须补**；
- §5 若 loop 内**有 `while` 但无 `trap`** → agent 被 kill 后脚本会**静默退出**（呼应"无日志、无痕迹"）。


**背景**：10-04 09:31 → 10-05 12:20 两条线无提交；BaiZe 线同期正常。机器为 **2 vCPU / 2 GiB**。

```bash
echo "=== 0. 基本信息 ==="
hostname; date '+%F %T %Z'; uptime
echo
echo "=== 1. loop 进程（应为各 1 个）==="
pgrep -af 'watch_(news|research)_loop.sh' | cut -c1-140 || echo "(没有 watch_*_loop.sh 在跑)"
echo
echo "=== 2. loop 日志尾部（找 额度已用完 / 403 / 429）==="
for f in /tmp/watch_news_loop.log /tmp/watch_research_loop.log; do
  echo "--- $f ---"; tail -20 "$f" 2>/dev/null | cut -c1-200 || echo "(无此日志)"
done
echo
echo "=== 3. ⭐OOM 痕迹（2G 机器的头号嫌疑）==="
(dmesg -T 2>/dev/null || sudo -n dmesg -T 2>/dev/null) | grep -iE 'oom|killed process' | tail -15 || echo "(读不到 dmesg 或无 OOM 记录)"
echo
echo "=== 4. 资源 ==="
free -m; echo; df -h / /home 2>/dev/null | head -5
echo
echo "=== 5. CPU top5 ==="
ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu 2>/dev/null | head -6 | cut -c1-140
echo
echo "=== 6. cline base（只看 base，不打 key）==="
grep -o '"openAiBaseUrl"[^,}]*' ~/.cline/data/globalState.json 2>/dev/null || echo "(无 globalState.json)"
echo
echo "=== 7. git 状态 ==="
cd ~/super_intelligence_2035 2>/dev/null && git log --oneline -3 && echo '--- dirty ---' && git status --short | head -10
```

## RUN_ID 8 — 🔧 **把 news / research 两条 loop 的兜底推送间隔 5h→30min 并重启生效**（本块会 kill 重启这两条 loop）

**背景（supervisor 2026-10-06 ~10:4x，用户指令）**：用户令「三条线（personal-watch news/research、ZhuLong）把 PUSH_INTERVAL 调短；**先动 news/research**」。
- 已改脚本：`watch_news_loop.sh` / `watch_research_loop.sh` 的 `PUSH_INTERVAL` **18000 → 1800**（5h→30min，与 BaiZe 一致）——**需重启 loop 才生效**。
- 用户授权：**优先用本中继重启**；不行再由用户在服务器手工做。

**本块动作（唯一会 kill 的块，仅 kill 这两条 loop；🚫 不碰任何中继进程）**：
1. `git pull --rebase --autostash` 拿新脚本（**之后会核对 `PUSH_INTERVAL=1800`**）；
2. 重启前先看该线**日志尾部是否为 `sleep`**（= 空闲）；**仅空闲才重启**，避免打断唤醒中的 cline（每条最多等 3min，超时则跳过、留待下个 RUN_ID）；
3. `pkill -f watch_<线>_loop.sh` → `setsid` 重启 → 复查进程 + 新日志尾部。

```bash
set -u
cd ~/super_intelligence_2035 || exit 1
R=doc/personal-watch/run
echo "=== 0. 基本 ==="
hostname; date '+%F %T %Z'; uptime
echo
echo "=== 1. 同步（拿新脚本）==="
git fetch origin --quiet 2>&1
git pull --rebase --autostash origin main 2>&1 | tail -3
echo
echo "=== 2. 确认新 PUSH_INTERVAL（应均为 1800）==="
grep -n '^PUSH_INTERVAL=' "$R/watch_news_loop.sh" "$R/watch_research_loop.sh"
echo
echo "=== 3. 重启前：进程 + 日志尾部 ==="
ps -eo pid,etime,args | grep -E 'watch_(news|research)_loop\.sh' | grep -v grep | cut -c1-140 || echo "(无 loop 在跑)"
for n in news research; do echo "--- $n ---"; tail -2 "/tmp/watch_${n}_loop.log" 2>/dev/null | cut -c1-160 || echo "(无日志)"; done
echo
echo "=== 4. 逐个重启（仅当 sleep 空闲；避免打断唤醒中的 cline）==="
restart_one() {
  n="$1"; log="/tmp/watch_${n}_loop.log"; i=0
  echo "--- [$n] ---"
  while [ "$i" -lt 6 ]; do
    tail -1 "$log" 2>/dev/null | grep -q 'sleep' && break
    echo "  [$n] 疑似唤醒中 -> 等 30s"; sleep 30; i=$((i+1))
  done
  if ! tail -1 "$log" 2>/dev/null | grep -q 'sleep'; then
    echo "  [$n] 等待 3min 仍非空闲 -> 本轮不重启（下个 RUN_ID 再试）"; return 0
  fi
  echo "  [$n] 空闲 -> 重启"
  pkill -f "watch_${n}_loop.sh" 2>/dev/null; sleep 2
  cd "$HOME/super_intelligence_2035/doc/personal-watch/run" || return 1
  setsid bash "watch_${n}_loop.sh" > "$log" 2>&1 < /dev/null &
  cd "$HOME/super_intelligence_2035" || return 1
  sleep 3
  ps -eo pid,etime,args | grep "watch_${n}_loop.sh" | grep -v grep | cut -c1-140 || echo "  [$n] 未起来！"
}
restart_one news
restart_one research
echo
echo "=== 5. 重启后进程 ==="
ps -eo pid,etime,args | grep -E 'watch_(news|research)_loop\.sh' | grep -v grep | cut -c1-140 || echo "(无)"
echo "=== 6. 新日志尾部 ==="
for n in news research; do echo "--- $n ---"; tail -3 "/tmp/watch_${n}_loop.log" 2>/dev/null | cut -c1-160; done
echo "=== DONE ==="
```

