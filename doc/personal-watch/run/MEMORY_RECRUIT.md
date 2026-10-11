# MEMORY_RECRUIT.md — 观察哨 · **recruit agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_recruit_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-11 起沿用定时节律：每天 2 次 · 06:00 / 18:00 本地时区**，由 loop 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
已完成:       [第 0 轮 · 2026-10-11 立线] 建立 recruit 线脚手架（任务书 `WATCH_RECRUIT_TASK.md` + loop `watch_recruit_loop.sh` + 本记忆 + `daily-memories-recruit/` + `recruit/`）；**继承源锁定** `$HR_DIR = C:\Users\liuyu\HR`（记忆 4 层 + Boss 能力 SOP + 脚本/话术）；**继承摘要内嵌**任务书 §0.2（长期记忆）/§0.3（能力 SOP），唤醒即「已记得」；**对外动作闸门**确立（默认保守，发送/同意/抓简历需运维授权）。**【待首轮唤醒】**：读 `$HR_DIR` 记忆 + 巡检 Boss + 写 `recruit/STATE.md` 现状快照。**2026-10-11 追加：浏览器执行环境（腾讯云 Ubuntu）已建并端到端验证** —— XFCE+TigerVNC+Chrome155+CDP（任务书 **§0.4**）；**待办：VM 装 driver + 真实 Boss 登录 + 开机自启/免密 SSH（待批）**。
当前动作:     第 0 轮（立线）：仅落脚手架与继承规约，**未对 Boss 做任何页面操作、未对候选人发任何消息**；**另完成 §0.4 执行环境搭建**（装桌面/VNC/Chrome/CDP + 扩 swap，**只读/装软件，未碰 Boss**）；**并把 loop 起在 VM 上**（`WATCH_INTERVAL_MIN=30` 临时 30min 节律；修掉两个启动坑：**cwd 错** + **PATH 缺 nvm bin → `cline: command not found`**）。
下一步:       ① **首轮唤醒（下一次 06:00/18:00 时窗）**：按任务书 §1 第 1 步读 `$HR_DIR/MEMORY.md`+`USER.md`+`AGENTS.md`+近 2 天 `memory/*.md`（读不到→内嵌摘要兜底并如实记）；② **环境自检（§0.4）**：SSH/VNC(5901)/CDP(9222) 是否可达；③ 巡检 Boss 登录态（新标签读 `.chat-message-list`：只读）；④ 复核 `$HR_DIR/发送记录.md` 尾部（近批次送达 / 有无风控）；⑤ 产出 `recruit/STATE.md`（达标者数 / 批次进度 / 待办；**非 PII 概述**）；⑥ 汇总 `$HR_DIR` §八 未决口径 + README 待办；⑦ **不做**任何对外发送（除非运维指令区下「授权批次」）。**§0.4 待办（需拍板）**：a) VM 装 Playwright/Puppeteer（用系统 Chrome）；b) VNC 人工扫码建 `~/.hr-chrome-profile` 登录态；c) 开机自启 `@reboot ~/hr_start.sh`；d) 免密 SSH（装公钥）；e) Boss 反自动化/ToS 合规口径（建议首期**只读+草稿+人工确认发送**）。
本轮新增:     0（立线轮，无采集、无对外动作）＋ **执行环境 1 套**（§0.4，未触 Boss）。
阻塞:         无（⚠️ 待核验：① 本机 Git Bash/WSL + cline；② `$HR_DIR` 可达性；③ **VM 上尚无 Playwright/Puppeteer driver**、**尚无真实 Boss 登录态**）。
ERROR_COUNT:  0
```

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（第 1 批登记）**：recruit 线**与 `C:\Users\liuyu\HR` 的关系**是「复制一份」还是「引用」？
  **A（本线）**：**引用（以 HR 为唯一权威）**。理由：HR `README.md §三` 铁律「同一事实只在一个地方有权威版本」—— 若仓库再存一份，会与 HR 原文件**分叉打架**；且 HR 目录含 `securityId`/简历等 **PII**，不入本仓库。故：**记忆与能力以 `$HR_DIR` 为准**，本仓库只放**编排 + 本线记忆（含继承摘要）+ 产物（非 PII）**。若 supervisor 另需「快照复制」，请在运维指令区明示。

- **Q（第 1 批登记）**：无人值守时，recruit 线**要不要自动给候选人发消息**？
  **A（本线）**：**默认不发**。本线是**唯一有对外副作用**的线 → 默认保守：**采集/分级/复核/起草/归档/记忆更新** 自主做满；**对外发送 / 抓简历 / 代点「同意·拒绝」** 一律要运维指令区**显式授权一批**（格式见任务书 §3）；**约面控件永不碰**。理由：无人值守误发真人不可撤回，且 Boss 反骚扰风控极严。

---

## 1. 状态头

- **线**：recruit（Boss 直聘招聘链路 · 继承 `C:\Users\liuyu\HR`）
- **任务书**：`WATCH_RECRUIT_TASK.md`（只读）
- **继承源（规范）**：`$HR_DIR` = `C:\Users\liuyu\HR` —— 记忆：`MEMORY.md` · `USER.md` · `AGENTS.md` · `DREAMS.md` · `memory/` · `发送记录.md`；能力：`screen.py` · `city_scan.py` · `话术-最终版.md` · `候选人筛选报告.md`
- **产物（本线）**：`recruit/STATE.md`（现状快照 · 非 PII）· `recruit/drafts/`（话术草案）· `recruit/reports/`（汇报 HTML）
- **日流水**：`daily-memories-recruit/<YYYY-MM-DD>.md`
- **运行位置（两段式）**：① **控制侧 = 本 Windows 机**（loop + `$HR_DIR` 记忆/台账 + 仓库；Git Bash/WSL）；② **浏览器执行侧 = 腾讯云 Ubuntu `106.54.228.191`（`liuyang`）** —— XFCE 桌面 + TigerVNC（`:1→127.0.0.1:5901`）+ **Chrome 155** + **CDP `127.0.0.1:9222`**；**登录走 SSH 隧道 + VNC**，**自动化走 CDP + 持久 profile `~/.hr-chrome-profile`**；**loop 亦跑在该 VM 上**（launcher `~/start_recruit_loop.sh`；**临时节律 `WATCH_INTERVAL_MIN=30`**）—— ★ 详见任务书 **§0.4（含 ⑧ loop 运行方式 + 「VM 读不到 `$HR_DIR`」缺口）**
- **对外动作**：默认 `关闭`（需运维授权一批才开；见任务书 §3）


---

## 2. 🧬 继承摘要（**指针** · 正文以 `$HR_DIR` 为准）

> 完整继承的**长期记忆**与**能力 SOP** 已内嵌在任务书 **`WATCH_RECRUIT_TASK.md` §0.2 / §0.3**（那才是每次唤醒读进上下文的版本）。
> 本节只留**指针 + 同步规约**，避免在本文件里重复一遍导致分叉。

| 继承物 | 规范源 | 本线读取时机 | 同步规约 |
|:---|:---|:---|:---|
| 判定口径 / 平台事实 / 铁律 / 教训 | `$HR_DIR/MEMORY.md` | 每轮唤醒（任务书 §1 第 1 步） | HR 更新 → **以 HR 为准**，回头同步任务书 §0.2 摘要 |
| 用户模型（偏好 / 授权边界） | `$HR_DIR/USER.md` | 每轮唤醒 | 同上 |
| 情景记忆（近 2 天） | `$HR_DIR/memory/*.md` | 每轮唤醒 | 只读 |
| 整理审核面 | `$HR_DIR/DREAMS.md` | 按需 | 只读 |
| 原始台账（已发/送达/风控） | `$HR_DIR/发送记录.md` | 每轮（读尾部） | **只追加**，本线不改历史 |
| Boss 能力 SOP | `$HR_DIR/AGENTS.md` | 每轮（细读） | 任务书 §0.3 为精简摘要，冲突以 HR 为准 |
| 分级 / 捞上海系脚本 | `$HR_DIR/screen.py` · `city_scan.py` | 需重分级时 | 于 `$HR_DIR` 内运行（读其 csv） |

> 🖥️ **执行环境（另一处外部依赖）**：见任务书 **§0.4** —— 腾讯云 Ubuntu `106.54.228.191`（XFCE 桌面 + TigerVNC `:1→127.0.0.1:5901` + Chrome 155 + CDP `127.0.0.1:9222`；登录走 SSH 隧道+VNC，自动化走 CDP+持久 profile）。**与 `$HR_DIR` 并列**，二者都**不在本仓库**。

> ⚠️ **数据边界**：`boss_candidates.csv/.json`（含 `securityId`）、`候选人筛选结果.csv`、`简历/*.pdf`、`boss_chat*.png`、cookie 凭据 —— **一律不进本仓库**（任务书 §0.1③ / §4-7、`recruit/.gitignore`）。

---

## 3. 流水（倒序，保留最近 ~20 条）

- **2026-10-11（第 0 轮 · 追加 2：loop 起在 VM + 30min 节律）** —— 用户令：「招聘 loop 已启动，但因唤醒时窗是早 6 晚 6 似乎没执行；**改 loop 暂设每 30 min，并经 SSH 重启**」。**诊断**：① VM 上 **news/research 两条 loop 在跑，recruit 的没在跑**（`/tmp/watch_recruit_loop.log` 只有 `bash: watch_recruit_loop.sh: No such file or directory` = **启动时 cwd 不对**）；② 本机 Windows **无任何 bash/node 进程**（loop 不在本机）。**改动（repo）**：`watch_recruit_loop.sh` 新增 **`WATCH_INTERVAL_MIN` 间隔模式**（优先级 `interval > schedule(6,18) > adaptive`；置空即回退），含 `sleep_until_next_interval()` + 三路横幅 + `[mode=…]` 标注；header 文档同步。**发布**：commit `cf53c5f9`（索引 LF 已核验 `git ls-files --eol` = `i/lf`）。**VM 侧**：`git pull` → `bash -n` ✅ → 写 launcher `~/start_recruit_loop.sh`（`cd` 到 `run/` + **补 PATH `~/.nvm/versions/node/v24.21.0/bin`** + 默认 `WATCH_INTERVAL_MIN=30`）→ `setsid nohup` 启动。**验证**：`[mode=interval:30min]` ✅；**cline 成功调起**（此前 `cline: command not found`，exit 127）；hb `/tmp/watch_recruit_loop.hb` 在刷新；agent 已在按「继承 + 状态」流程作业。**🔴 关键发现（未解）**：开机横幅显示 **`HR_DIR=C:/Users/liuyu/HR · 存在：缺`** —— **loop 跑在 Linux VM 上，读不到 Windows 的 `$HR_DIR`** ⇒ 只能用任务书 §0.2/§0.3 **内嵌摘要兜底**，且**无法回写 `$HR_DIR`**。**已写入任务书 §0.4⑧ + 列「待拍板」三条**（loop 跑 Windows / 同步 HR 到 VM / 维持只读兜底）。

- **2026-10-11（第 0 轮 · 追加：执行环境）** —— **建 recruit 浏览器执行环境（腾讯云 Ubuntu `106.54.228.191`）**：目标 = 给本线一台**常驻可远控**的浏览器机（Boss 登录 + 自动化），把「浏览器跑在哪」与「loop 跑在哪」**解耦**。**已做**：SSH 上机探测（Ubuntu 24.04 / **2 vCPU / 3.6 GiB / 69 G 盘** / Cirrus 虚拟显卡 / `liuyang`∈`sudo`）；装 **XFCE 4.18 + TigerVNC 1.13.1 + xvfb/x11vnc + fonts-noto-cjk + Google Chrome 155.0.8059.39**（**不用 GNOME**，避免 OOM）；**swap 1.9G→6.0G**（`/swap2.img`）；关 `lightdm`/`cups`/`colord`/`ModemManager`，默认 target→`multi-user`。**验证**：XFCE 桌面在 `:1`（`xlsclients` 可见）；**VNC `127.0.0.1:5901`（仅本机）**；**CDP `127.0.0.1:9222`**，targets 含 `https://www.zhipin.com/`；全开占用 ≈ **1.2 G / 3.7 G**。**产出**：服务器 `~/hr_start.sh` / `hr_login.sh` / `hr_headless.sh` + **共用 profile `~/.hr-chrome-profile`**（★ 登录一次长期复用）。**踩坑**：`pkill -f 'remote-debugging-port=9222'` 会**把执行命令的 shell 一起杀掉**（自匹配）→ 必须用 **`[r]emote…` 括号技巧**。**写入任务书 §0.4**（访问方式 / 两模式 / 与 §0.3 cookie 路径的关系 / 铁律 13-14 / 凭据 / 故障速查）。**未做**：真实 Boss 登录、VM 装 Playwright/Puppeteer。**全程未碰 Boss、未发任何消息**。

- **2026-10-11（立线轮 · 第 0 轮）** —— **建立 recruit 线（观察哨第 3 条线）→ 继承 `C:\Users\liuyu\HR` 记忆与能力**：新建 `WATCH_RECRUIT_TASK.md`（只读任务书；§0.1 继承映射 · §0.2 继承的长期记忆摘要 · §0.3 继承的 Boss 能力 SOP · §1 工作流 · §3 对外动作闸门 · §4 铁律 · §5 记忆维护）+ `watch_recruit_loop.sh`（照抄 research 模板三防坑 + 定时 6,18 + `$HR_DIR` 自检横幅）+ 本记忆 + `daily-memories-recruit/` + `recruit/`（README/`.gitignore`/STATE 占位/`drafts/`/`reports/`）；登记 `../AGENTS.md §1` + `../README.md §2/§3` + `run/README.md`。**规约决定**：① **引用式继承**（HR 为唯一权威，仓库不复制其 4 个记忆文件）；② **对外动作默认关闭**（发送/抓简历/代点同意·拒绝需运维授权；约面永不碰）；③ 运行位置 = 持 Boss 登录态的机器。**本轮未做任何 Boss 页面操作、未发任何消息**。

---

## 4. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-recruit/<条目日期>.md`（原文不改），再从本文件删除。
- **任务书自己滚**：`WATCH_RECRUIT_TASK.md` 超限时，把**已闭合**的历史轮次/已执行完的运维块原文搬入 `WATCH_RECRUIT_TASK_ARCHIVE.md`（留 1 行指针，不新增/不改写指令）。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条。
- **归档不改变任何结论**；`WAITING:` 纪律不变。
- **回写 `$HR_DIR`**：招聘结论（新达标者 / 口径变化 / 教训）同时按 HR `AGENTS.md §10` 写回 `$HR_DIR`。

