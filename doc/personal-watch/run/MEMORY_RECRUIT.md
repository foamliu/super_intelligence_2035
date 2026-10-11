# MEMORY_RECRUIT.md — 观察哨 · **recruit agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_recruit_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-11 起沿用定时节律：每天 2 次 · 06:00 / 18:00 本地时区**，由 loop 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
已完成:       [第 0 轮 · 立线] 建 scaffold + 继承规约 + 执行环境（§0.4）。[第 0 轮 · 追加] loop 起在 VM（`WATCH_INTERVAL_MIN=30` 临时节律；修 `cwd 错` + `PATH 缺 nvm bin`）。[第 1 轮 · 2026-10-11 首轮唤醒] ✅ 继承尝试（`$HR_DIR` 在 VM 不可达 → §0.2/§0.3 内嵌摘要兜底）；✅ 环境自检 + 新增只读巡检 `~/hr_cdp.js`（零新依赖）；✅ Boss 只读巡检（登录有效·刘先生·在招 1 岗·新招呼 157·会话 ~40）；✅ `recruit/STATE.md` 首版。**[第 2 轮 · 2026-10-11]** ✅ 复核继承兜底（`$HR_DIR` 仍不可达）；✅ 环境自检全绿（VNC `:1`·CDP Chrome155·mem available 1.8G）；✅ Boss 只读复检（新标签 `.user-list` 在·40 条 `.geek-item-wrap`·登录**仍有效·刘先生**·**新招呼 157 未变**）；✅ 抽取可见会话首句 ~15 条（首句全为泛化招呼，**未见「一作+录用+顶会」证据**）；✅ 刷新 `STATE.md`。全程 **0 对外动作 / 未点会话 / 未抓简历**。**[supervisor · 融入本仓 · 2026-10-11]** ✅ 把 HR 记忆/任务/能力（**37 文件 · ≈1.09MB**）复制进仓内 `recruit/hr/`；任务书 / loop / 本文件 / `recruit/README.md` 里 `$HR_DIR`→`recruit/hr/`；**§0.4⑧「VM 读不到 `$HR_DIR`」缺口关闭**。**[第 3 轮 · 2026-10-11]** ✅ **继承达成**（仓内 `recruit/hr/` 全可读：`MEMORY.md`·`USER.md`·`AGENTS.md`·`memory/2026-09-26|27`·`发送记录.md` 尾部·`README.md`）；✅ 环境自检全绿（VNC `:1`·CDP Chrome155·loop hb 刷新）；✅ **能力可用性验证**（`python3.12`+`node v24.21`；`screen.py`/`city_scan.py`/`build_candidate_tables.py`/`school_judge.py` `py_compile` OK）；✅ `recruit/check_pii.sh recruit/hr` → EXIT 0；✅ Boss 只读复检（**新标签**·登录有效·刘先生·40 条 `.geek-item-wrap`·**新招呼 157 未变**·可见会话 `10-10→09-28`）。**0 对外动作 / 未点会话 / 未抓简历**。
当前动作:     [第 3 轮] 继承复核（**仓内，已达成**）+ 能力可用性验证 + 环境/Boss 只读巡检 + 刷新 STATE/记忆。
下一步:       ① 跑 `recruit/hr/screen.py`/`city_scan.py` 需原始 `boss_candidates.csv`（**未入仓** → 若要重分级必须先**采集**，采集属只读**自主可做**）；② 等 supervisor 拍板余下 3 项（`recruit/STATE.md §五`：loop 节律 / 157 积压策略 / `hr_cdp.js` 归入 §0.4）；③ **新发现**：Boss 收件箱有 HR 时代遗留**待回消息**（王海/杨海峰/穆女士/张时与 等，09-28~09-30）→ 需**授权批次**才可回；④ 授权后**才**发话术/抓简历（≤2-3 人/批 · 批间隔 ≥60min · 逐人定制）。
本轮新增:     能力可用性验证（4 个 py 脚本 `py_compile` OK）· PII 自检 EXIT 0 · 收件箱遗留待回消息观察（**仅记录，未动**）；对外动作 **0**；0 条采集。
阻塞:         ✅ **继承缺口已关闭**（仓内 `recruit/hr/` 全可读，R3 已亲手复核）· ⏳ 余 3 项待拍板（STATE §五）· ⏳ **收件箱遗留消息待授权**· ✅ 浏览器登录态有效（连续三轮）。
ERROR_COUNT:  0
```

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（第 1 批登记）**：recruit 线**与原 HR 工作区的关系**是「复制一份」还是「引用」？
  **A（本线 · 已于 2026-10-11 第 2 批改判）**：**「复制进仓」**。supervisor 令：「**融入** = 信息融进来，**不要再依赖原目录**（观察哨在腾讯云执行，看不到原目录）」→ HR 记忆/任务/能力**已整体复制进 `recruit/hr/`**，**仓内副本即唯一权威**；仅**原始 PII/凭据**（`boss_candidates.*`/简历/截图/cookie）未搬。原「引用式」方案作废。

- **Q（第 1 批登记）**：无人值守时，recruit 线**要不要自动给候选人发消息**？
  **A（本线）**：**默认不发**。本线是**唯一有对外副作用**的线 → 默认保守：**采集/分级/复核/起草/归档/记忆更新** 自主做满；**对外发送 / 抓简历 / 代点「同意·拒绝」** 一律要运维指令区**显式授权一批**（格式见任务书 §3）；**约面控件永不碰**。理由：无人值守误发真人不可撤回，且 Boss 反骚扰风控极严。

---

## 1. 状态头

- **线**：recruit（Boss 直聘招聘链路 · 继承源**已融入仓内** `recruit/hr/`）
- **任务书**：`WATCH_RECRUIT_TASK.md`（只读）
- **继承源（仓内权威 · 自包含）**：`recruit/hr/` —— 记忆：`MEMORY.md` · `USER.md` · `AGENTS.md` · `DREAMS.md` · `memory/` · `发送记录.md`；能力：`screen.py` · `city_scan.py` · `话术-最终版.md` · `候选人筛选报告.md`（**原 `C:\Users\liuyu\HR` 已不再参与**）
- **产物（本线）**：`recruit/STATE.md`（现状快照 · 非 PII）· `recruit/drafts/`（话术草案）· `recruit/reports/`（汇报 HTML）
- **日流水**：`daily-memories-recruit/<YYYY-MM-DD>.md`
- **运行位置（两段式）**：① **控制侧 = 本 Windows 机**（loop + `$HR_DIR` 记忆/台账 + 仓库；Git Bash/WSL）；② **浏览器执行侧 = 腾讯云 Ubuntu `106.54.228.191`（`liuyang`）** —— XFCE 桌面 + TigerVNC（`:1→127.0.0.1:5901`）+ **Chrome 155** + **CDP `127.0.0.1:9222`**；**登录走 SSH 隧道 + VNC**，**自动化走 CDP + 持久 profile `~/.hr-chrome-profile`**；**loop 亦跑在该 VM 上**（launcher `~/start_recruit_loop.sh`；**临时节律 `WATCH_INTERVAL_MIN=30`**）—— ★ 详见任务书 **§0.4（含 ⑧ loop 运行方式 + 「VM 读不到 `$HR_DIR`」缺口）**
- **对外动作**：默认 `关闭`（需运维授权一批才开；见任务书 §3）


---

## 2. 🧬 继承摘要（**仓内权威 = `recruit/hr/`** · 自包含）

> 完整继承的**长期记忆**与**能力 SOP** 已内嵌在任务书 **`WATCH_RECRUIT_TASK.md` §0.2 / §0.3**（那才是每次唤醒读进上下文的版本）。
> 本节是**指针 + 同步规约**：正文权威在**仓内** `recruit/hr/`（**原 `C:\...` 已不参与**）。

| 继承物 | 仓内权威 | 本线读取时机 | 同步规约 |
|:---|:---|:---|:---|
| 判定口径 / 平台事实 / 铁律 / 教训 | `recruit/hr/MEMORY.md` | 每轮唤醒（任务书 §1 第 1 步） | 更新写 `recruit/hr/MEMORY.md`，回头同步任务书 §0.2 速览 |
| 用户模型（偏好 / 授权边界） | `recruit/hr/USER.md` | 每轮唤醒 | 同上（**原位取代**） |
| 情景记忆（近 2 天） | `recruit/hr/memory/*.md` | 每轮唤醒 | 追加 `recruit/hr/memory/<date>.md` |
| 整理审核面 | `recruit/hr/DREAMS.md` | 按需 | 追加 |
| 原始台账（已发/送达/风控） | `recruit/hr/发送记录.md` | 每轮（读尾部） | **只追加**，本线不改历史 |
| Boss 能力 SOP | `recruit/hr/AGENTS.md` | 每轮（细读） | 任务书 §0.3 为精简摘要，冲突以 `recruit/hr/AGENTS.md` 为准 |
| 分级 / 捞上海系脚本 | `recruit/hr/screen.py` · `recruit/hr/city_scan.py` | 需重分级时 | 于 `recruit/hr/` 内运行（读原始 csv；**csv 不入 git**） |

> 🖥️ **执行环境（仍为外部依赖）**：见任务书 **§0.4** —— 腾讯云 Ubuntu `106.54.228.191`（XFCE 桌面 + TigerVNC `:1→127.0.0.1:5901` + Chrome 155 + CDP `127.0.0.1:9222`；登录走 SSH 隧道+VNC，自动化走 CDP+持久 profile）。⚠️ **这才是本线唯一的外部依赖**（`recruit/hr/` 已在仓内，不再算外部）。

> ⚠️ **数据边界**：`boss_candidates.csv/.json`（含 `securityId`）、`候选人筛选结果.csv`、`简历/*.pdf`、`boss_chat*.png`、cookie 凭据 —— **一律不进本仓库**（任务书 §0.1③ / §4-7、`recruit/.gitignore`）。

---

## 3. 流水（倒序，保留最近 ~20 条）

- **2026-10-11（第 3 轮 · 间隔节律下第三轮）** —— **继承复核（仓内，达成）→ 能力可用性验证 → 环境/Boss 只读复检 → 刷新 STATE/记忆**。**① 继承（★ 首次真正达成）**：读**仓内** `recruit/hr/MEMORY.md`（身份/判定口径§二/平台事实§五/铁律§六/归档§七/未决§八/教训§九）· `USER.md`（刘杨偏好+授权边界）· `AGENTS.md`（Boss SOP §1-§12）· `memory/2026-09-26`·`memory/2026-09-27` · `发送记录.md` 尾部（第 23 条归档结构改造）· `README.md` §五 现状+14 人达标名录+待办 —— **全部在 VM 可读**（`$HR_DIR` Windows 路径彻底不再需要）。**② 能力验证**：`python3 --version`=3.12.3 · `node --version`=v24.21.0；`python3 -m py_compile` → `screen.py`/`city_scan.py`/`build_candidate_tables.py`/`school_judge.py` **OK**（`__pycache__` 已删）；⚠️ 分级实跑需 `boss_candidates.csv`（**PII，未入仓**）→ 本轮**未实跑**。**③ 合规自检**：`bash recruit/check_pii.sh recruit/hr` → **EXIT 0**（未命中值级 PII/凭据）。**④ 环境自检（§0.4）**：`vncserver -list`=`:1`（Xtigervnc pid 2754851）✅；`curl 127.0.0.1:9222/json/version`=`Chrome/155.0.8059.39` ✅；Chrome `--user-data-dir=/home/liuyang/.hr-chrome-profile --remote-debugging-port=9222` ✅；loop 存活（`[w]atch_recruit_loop.sh` pid 2777145，hb `/tmp/watch_recruit_loop.hb` 刷新）✅。**⑤ Boss 只读巡检（新标签 `?r3=1`，未点会话）**：登录态**仍有效**，招聘端 **刘先生**；`.user-list`=1、`.geek-item-wrap`=**40**；分类标签「全部 **新招呼(157)** 沟通中 已约面 已获取简历 已交换电话 已交换微信 收藏」—— **157 较前两轮未变**；可见会话 **10-10（昨天）→ 09-28**（比上轮多露出更多）。首句抽样 ~25 条：**全为泛化招呼**（兴趣/请问还招吗/自我介绍），**无「一作+已录用+顶会」证据**（客观记录，**未判定**）。**⚠️ 新观察**：可见区出现 HR 时代**遗留待回消息** —— **王海「挂了吗[流泪]」(09-30)** · **杨海峰「简历已发送」(09-29)** · **穆女士「请问有面试机会吗」(09-28)** · **张时与「您好还有推进吗」(09-29)** 等（**仅列表摘要**，未点开 `.chat-message-list`）。**⑥ 边界**：**0 对外动作** · 未点任何会话/控件 · 未抓简历 · 未回写 `C:\...`。**本轮结论**：**「融入本仓」在运行侧被证实可用**（记忆可读 + 脚本可编译 + PII 闸门稳）；实质推进仍卡在**待授权**（157 积压策略 + 收件箱遗留消息 + 话术/抓简历）。

- **2026-10-11（supervisor · 口径拍板 + 自检工具 + 环境入 README）** —— ① **数据口径**：用户裁定 **「接受姓名级入库」**（`recruit/hr/` 内的**姓名/学校/期望/分级/沟通台账**允许入 git；**前提：仓库保持 private**）→ 已把该口径写进 `recruit/README.md`「⚠️ 数据边界」（**取代**旧「PII 一律不入库」），并**明确仍禁止**：cookie **值** · `securityId`/`geekId` **值**（字段名/规则文本允许）· 身份证 · 手机号 · 邮箱 · **简历 PDF/原文** · **截图** · 浏览器 `profile/` · `*.har` · 密钥/token。② **新增入库前自检** `recruit/check_pii.sh`（只扫**值级**匹配：cookie/ID 赋值 · 手机号 · 邮箱 · 身份证 · 私钥 · Basic；排除 `git@…` 良性项；**只打印 file:line 不打印内容**）；**VM 实测** `bash recruit/check_pii.sh recruit/hr` → **EXIT=0 ✅**。③ **`.gitignore` 加固**：补 `*.har` / `profile/` / `*.sqlite|*.db` / `*_cookie*` / `*凭据*` / `*.pem|*.key`。④ **环境信息入** `recruit/README.md` 新增「🖥️ 执行环境（腾讯云 VM · 已就绪）」节（主机/资源/桌面/浏览器/CDP/访问隧道/两模式/loop 启动器/节律）。commits：`12f95ab6` + `667b8efd`。**未碰 Boss、0 对外动作**。
- **📌 supervisor 观察（供本线参考）**：用户用 **VNC 看 Boss 直聘页面无任何变化**，问「agent 跑过没有」—— 已确认 **R1/R2 两轮确实跑过**（登录有效·新招呼 157·写 `STATE.md`），**"没变化"是设计使然**（任务书 §3 对外动作**默认全关**：发消息/抓简历/代点「同意·拒绝」需**显式授权一批**）。**157 条新招呼的积压策略**仍在 `recruit/STATE.md §五` 待拍板 —— **要看到 Boss 页面变化，必须先下「授权批次」。**

- **2026-10-11（supervisor · 融入本仓）** —— **把 HR agent 的「任务 + 记忆」融入观察哨、去掉本地目录依赖**（用户令：「融入 = 信息融进来，不要再依赖原目录 —— 观察哨在腾讯云执行，看不到该目录」）。**① 复制**：`C:\Users\liuyu\recruit` 的 **37 个 tracked 文件** → 仓内 **`recruit/hr/`**（含 `memory/` 子目录 7 文件；≈1.09MB）—— `MEMORY.md`·`USER.md`·`AGENTS.md`·`DREAMS.md`·`README.md`·`发送记录.md`·`话术-最终版.md`·`话术模板.md`·`S级论文录用确认-话术*.md`·`候选人筛选报告.md`·`候选人筛选结果.md`·`候选表-*.{md,csv}`·`社招判定-简单简历.md`·`本轮沟通-*.md`·`screen.py`·`city_scan.py`·`build_candidate_tables.py`·`school_judge.py`·`migrate_resume_paths.ps1`·`boss_verify_login.js`·`scan_msgs.js`·`send_msg.js`·`ask_resume.js`·`download_resume.js`·`simple_resume_scan.js`。**未搬**（PII/大文件）：`boss_candidates.*`(含 securityId)·`候选人筛选结果.csv`·`简历/*.pdf`·`简历.7z`·`__pycache__`。**② 改路径**：任务书 §0 重写为「融入本仓」（`$HR_DIR`→`recruit/hr/`）、§0.2/§0.3 权威改仓内、**§0.4⑧ 缺口标记关闭**、§1/§2/§3/§5/§6 全部改仓内、新增**运维第 2 批块**；`watch_recruit_loop.sh` header 改「跑在腾讯云 VM + 自包含」；本文件 §1/§2/问答/快照同步。**③ 效果**：**VM 上可直接读全部 HR 记忆/任务/能力**；**回写目标 = 仓内 `recruit/hr/`**；**不再依赖任何本地目录**。**对外动作 0（未碰 Boss）。**

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
- **回写仓内 `recruit/hr/`（唯一权威 · 自包含）**：招聘结论（新达标者 / 口径变化 / 教训）按 HR `AGENTS.md §10` 写回 **`recruit/hr/MEMORY.md` / `recruit/hr/memory/<date>.md` / `recruit/hr/DREAMS.md`**；🚫 不再回写 `C:\...`。

