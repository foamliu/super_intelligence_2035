# MEMORY_RECRUIT.md — 观察哨 · **recruit agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_recruit_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-11 起沿用定时节律：每天 2 次 · 06:00 / 18:00 本地时区**，由 loop 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
已完成:       [第 0 轮 · 立线] 建 scaffold + 继承规约 + 执行环境（§0.4）。[第 0 轮 · 追加] loop 起在 VM（`WATCH_INTERVAL_MIN=30` 临时节律；修 `cwd 错` + `PATH 缺 nvm bin`）。[第 1 轮 · 2026-10-11 首轮唤醒] ✅ 继承尝试（`$HR_DIR` 在 VM 不可达 → §0.2/§0.3 内嵌摘要兜底）；✅ 环境自检 + 新增只读巡检 `~/hr_cdp.js`（零新依赖）；✅ Boss 只读巡检（登录有效·刘先生·在招 1 岗·新招呼 157·会话 ~40）；✅ `recruit/STATE.md` 首版。**[第 2 轮 · 2026-10-11]** ✅ 复核继承兜底（`$HR_DIR` 仍不可达）；✅ 环境自检全绿（VNC `:1`·CDP Chrome155·mem available 1.8G）；✅ Boss 只读复检（新标签 `.user-list` 在·40 条 `.geek-item-wrap`·登录**仍有效·刘先生**·**新招呼 157 未变**）；✅ 抽取可见会话首句 ~15 条（首句全为泛化招呼，**未见「一作+录用+顶会」证据**）；✅ 刷新 `STATE.md`。全程 **0 对外动作 / 未点会话 / 未抓简历**。
当前动作:     第 2 轮：继承复核 + 环境/Boss 只读巡检 + 刷新 `STATE.md`；**未对候选人发任何消息、未点任何会话/控件**。
下一步:       ① 等 supervisor 拍板 4 项阻塞（`recruit/STATE.md §五`：`$HR_DIR` 不可达 / loop 节律 / 157 积压策略 / `hr_cdp.js` 归入 §0.4）；② 若 `$HR_DIR` 可达（或授权同步副本）→ 读其记忆 + `发送记录.md` 尾部，跑 `screen.py`/`city_scan.py`；③ 授权后**才**发话术/抓简历（≤2-3 人/批 · 批间隔 ≥60min · 逐人定制）。
本轮新增:     0 条采集（纯只读）＋ `STATE.md` 复检刷新；对外动作 **0**。
阻塞:         ⚠️ `$HR_DIR` 在 VM 不可达（继承源缺失 → 内嵌摘要兜底）· ⏳ 4 项待拍板（STATE §五）· ✅ 浏览器登录态已确认有效（连续两轮）。
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

- **2026-10-11（第 2 轮）** —— **继承复核 + 环境/Boss 只读巡检 + 刷新快照**（间隔节律下第二轮，`[mode=interval:30min]`）。**① 继承**：`WATCH_HR_DIR` 仍为空、`$HR_DIR=C:\Users\liuyu\HR` 在 VM 仍**不可达**（`find /home /root /mnt /srv` 无 HR 记忆/脚本）→ 沿用任务书 §0.2/§0.3 **内嵌摘要兜底**，如实记；未读 `发送记录.md`、未跑 `screen.py`/`city_scan.py`。**② 环境自检（§0.4）**：`vncserver -list`=`：1`（Xtigervnc，pid 2754851）✅；`curl 127.0.0.1:9222/json/version`=`Chrome/155.0.8059.39` ✅；Chrome `--user-data-dir=/home/liuyang/.hr-chrome-profile --remote-debugging-port=9222` ✅；`free -h` used 1.8G/3.6G、available 1.8G（健康）；`date`=`2026-10-11 11:08 CST` ✅。**③ Boss 只读巡检（新标签，未点会话）**：`newtab https://www.zhipin.com/web/chat/index` → `.user-list`=1、`.geek-item-wrap`=40；招聘端 **刘先生**；分类标签「全部 **新招呼(157)** 沟通中 已约面 已获取简历 已交换电话 已交换微信 收藏」—— **157 较上轮未变**。**④ 可见会话首句抽样（~15 条，仅列表摘要文字）**：最近活跃 **10-10（昨天）→ 09-30**；岗位多为 AI+EDA（DRAM）少数 大模型/Agent；首句**全为泛化招呼**（「非常感兴趣希望进一步沟通」「请问还在招吗」等），**无任何「一作+已录用+顶会」证据**（客观记录，未做判定）。**⑤ 产出**：刷新 `recruit/STATE.md`（顶部时间 + §二数字复检）。**对外动作 0；未点任何会话/控件、未抓简历、未回写 `$HR_DIR`。**

- **2026-10-11（第 1 轮 · 首轮唤醒）** —— **继承 + 只读巡检 + 首次现状快照**。**① 继承**：在 loop 宿主机（腾讯云 VM，Linux）上，`$HR_DIR=C:\Users\liuyu\HR` **不可达**（无 Windows 挂载、全盘无 HR 记忆/脚本）→ **如实记**，按任务书 §0.2/§0.3 **内嵌摘要兜底**（本轮「已记得」= 任务书摘要本身）；**未能读** `MEMORY.md`/`USER.md`/`AGENTS.md`/`memory/`/`发送记录.md`/`话术-最终版.md`，**未能跑** `screen.py`/`city_scan.py`。**② 环境自检（§0.4）**：`vncserver -list` 有 `:1`（Xtigervnc）✅；`curl 127.0.0.1:9222/json/version` = Chrome 155 ✅；Chrome 进程 `--user-data-dir=/home/liuyang/.hr-chrome-profile --remote-debugging-port=9222`（可见桌面 `DISPLAY=:1`）✅；**VM 时钟经 HTTP `Date` 核验正确**（本机 `2026-10-11 11:04 CST` == `03:04 GMT`）—— 说明任务书「本机时钟慢 8h」**不适用本 VM**（疑指 Windows 控制机在 UTC）。**③ 新增能力**：自建 **`~/hr_cdp.js`**（极简 CDP 客户端，**仅用 cline 自带 `ws` 模块，零新依赖**；支持 `list`/`newtab`/`eval`；**不新建 context**，只 attach 既有浏览器）—— 补上「VM 侧只读巡检 driver」。**踩坑**：CDP WebSocket 若带 `Origin: https://www.zhipin.com` 头 → Chrome 拒（日志提示需 `--remote-allow-origins`）⇒ **连接不带 Origin 头即可**（本 helper 已这么做）。**④ Boss 只读巡检（新标签，未点会话）**：`https://www.zhipin.com/web/chat/index` **登录态有效**，招聘端显示 **刘先生**；`.user-list` 在、`.geek-item-wrap` 40 条；岗位：**AI+EDA研究员（DRAM设计方向）· 上海 · 40-60K · 在招** + 大模型/Agent算法工程师（关闭）+ 大模型预研实习生（关闭）；沟通页 **新招呼(157)**；会话列表可见 ~40 条，活跃 **10-09 → 09-28**。**⑤ 产出**：`recruit/STATE.md` 首版（非 PII 概述 + 4 项待拍板）。**对外动作 0；未点任何会话/控件、未抓简历、未回写 `$HR_DIR`**。

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

