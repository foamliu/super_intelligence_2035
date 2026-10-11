# recruit/ — recruit 线目录（记忆/任务/能力 **已融入本仓** + 本线产物）

> 本目录是 **recruit 线**（观察哨第 3 条线）的目录。
> 🧬 **原 HR 招聘 agent 的记忆与能力已整体「融入」本仓** → **`recruit/hr/`**（**自包含，不依赖任何本地目录**；原 `C:\Users\liuyu\HR` 已不参与）。
> 🖥️ 本线 loop 跑在 **腾讯云 Ubuntu `106.54.228.191`**（浏览器走该机 Chrome + CDP，见任务书 §0.4）。
> 🚫 **本目录只放非 PII**；原始 PII/凭据（`securityId` / 简历 PDF / 截图 / cookie）**未入仓**（见 `.gitignore`）。

## 🖥️ 执行环境（腾讯云 VM · **已就绪 2026-10-11**）

> 本线的**浏览器执行侧 + loop 宿主机** = 腾讯云 Ubuntu。环境已装并**端到端验证**；详见任务书 **`../../WATCH_RECRUIT_TASK.md §0.4`**（本节为速览）。⚠️ **尚未做真实 Boss 登录**（登录态由 VNC 人工扫码建立，落 `~/.hr-chrome-profile`）。

| 项 | 值 |
|:--|:--|
| 主机 / 账号 | `106.54.228.191`（腾讯云 CVM `VM-0-6-ubuntu`）· **Ubuntu 24.04.4 LTS** · 用户 **`liuyang`**（`sudo` 组） |
| 资源 | **2 vCPU / 3.6 GiB RAM + swap 6.0 GiB / 69 G 盘**；虚拟显卡（无 GPU → 软件渲染）；⚠️ 与 personal-watch 的 cline daemon **共驻** |
| 桌面 | **XFCE 4.18**（`:1`）· **TigerVNC 1.13.1**（`:1 → 127.0.0.1:5901`，**仅绑本机**） |
| 浏览器 | **Google Chrome 155.0.8059.39**（可见 + headless 双模式）· **CDP `127.0.0.1:9222`** |
| 已关服务 | `lightdm` / `cups` / `colord` / `ModemManager`；默认 target `multi-user` |

**访问（一律 SSH 隧道；🚫 不开公网端口 / 安全组不开 5901·9222）**
```bash
ssh -N -L 5901:127.0.0.1:5901 -L 9222:127.0.0.1:9222 liuyang@106.54.228.191
```
VNC 客户端连 `127.0.0.1:5901`（口令见任务书 §0.4⑦）；CDP 连 `http://127.0.0.1:9222`（Playwright `connect_over_cdp` / Puppeteer `connect{browserURL}`）。

**两种模式（★ 共用 profile `~/.hr-chrome-profile` ⇒ 登录一次长期复用）**

| 服务器脚本 | 用途 |
|:--|:--|
| `~/hr_start.sh` | 确保 VNC 桌面在跑 |
| `~/hr_login.sh` | **登录模式**：桌面里开**可见** Chrome + CDP → 人工扫码/短信/滑块 |
| `~/hr_headless.sh` | **自动化模式**：**headless** Chrome + CDP（省内存） |
| `~/start_recruit_loop.sh` | **本线 loop 启动器**：`cd` 到 `run/` + 补 PATH（nvm bin）+ `WATCH_INTERVAL_MIN=30` |

> ⚠️ 同一时刻**只跑一个 Chrome**（都占 9222）；清理必须用 `pkill -f '[r]emote-debugging-port=9222'`（**括号技巧**，否则会连执行命令的 shell 一起杀）。
> 🔁 **loop 重启**：`pkill -f '[w]atch_recruit_loop.sh'` → `setsid nohup bash ~/start_recruit_loop.sh > /tmp/watch_recruit_loop.log 2>&1 < /dev/null &`；存活标记 `/tmp/watch_recruit_loop.hb`。
> ⏱ **节律**：当前 **`WATCH_INTERVAL_MIN=30`（每 30 min，临时）**；置空即回退任务书默认的 **06:00/18:00**。

## 目录约定

| 路径 | 内容 | 入 git |
|:---|:---|:---:|
| `hr/` | ⭐ **融入的 HR agent 记忆 / 任务 / 能力**（含**姓名级**候选表与台账 —— 见下方「数据边界」） | ✅ |
| `STATE.md` | **招聘现状快照**（达标者数 / 批次进度 / 待办；**非 PII 概述**） | ✅ |
| `drafts/` | **话术草案**（对外发送前；实际发送原文以 `$HR_DIR/发送记录.md` 为准） | ✅ |
| `reports/` | **对外工作汇报 HTML**（自包含 · 内联 CSS · 零外链 · 离线可开） | ✅ |
| `files.md`（可选） | **大文件清单**（路径 / 字节数 / sha256 / 存放位置 `网盘:<路径>`）—— 数据本体不在 git | ✅ |
| `简历/`、`*.pdf`、`boss_candidates.*`、`*.png` | 🚫 PII / 凭据 / 大文件 | ⛔ 见 `.gitignore` |

## 🧬 继承映射表（recruit 线 ← 仓内 `recruit/hr/`，**自包含**）

> **唯一权威 = `recruit/hr/`（仓内）**；原 `C:\...` 已不参与。权威说明见 **`../../WATCH_RECRUIT_TASK.md §0`**（本节为速览），同步规约见 `../../MEMORY_RECRUIT.md §2`。
> ℹ️ 表中路径以**仓库根 `doc/personal-watch/run/`** 为基准（如 `recruit/hr/MEMORY.md`）。

### 记忆（唤醒先读）

| 继承物 | 仓内路径 | 说明 |
|:---|:---|:---|
| 长期记忆 | `recruit/hr/MEMORY.md` | 身份 / 判定口径 / 达标者花名册 / 平台事实 / 铁律 / 教训 |
| 用户模型 | `recruit/hr/USER.md` | 刘杨的偏好 / 沟通风格 / 授权边界 |
| 情景记忆 | `recruit/hr/memory/<YYYY-MM-DD>.md` | 每天一个文件（近 2 天自动带） |
| 整理审核面 | `recruit/hr/DREAMS.md` | 什么被提升进 `MEMORY.md` |
| 原始台账 | `recruit/hr/发送记录.md` | 已发 / 送达 / 风控（**只追加**） |

### 能力（照做）

| 能力 | 仓内路径 | 说明 |
|:---|:---|:---|
| Boss 页面操作 SOP | `recruit/hr/AGENTS.md` | 登录注入 / 切会话 / 读消息 / 发消息 / 下载简历 / 采集（精简摘要见任务书 §0.3） |
| 候选分级 | `recruit/hr/screen.py` | `boss_candidates.csv` → `候选人筛选结果.csv/.md`（**仅关键词初筛**） |
| 捞上海系 | `recruit/hr/city_scan.py` | 从打招呼文本提上海系 |
| 建候选表 / 学校判定 | `recruit/hr/build_candidate_tables.py` · `recruit/hr/school_judge.py` | 生成候选表 / 学校档判定 |
| Boss 脚本（node） | `recruit/hr/*.js`（`boss_verify_login` / `scan_msgs` / `send_msg` / `ask_resume` / `download_resume` / `simple_resume_scan`） | 从 `process.env.BOSS_COOKIE` 读（**产物中无真实 cookie**） |
| 话术库 | `recruit/hr/话术-最终版.md` · `recruit/hr/话术模板.md` · `recruit/hr/S级论文录用确认-话术*.md` | PI 口吻 + 地点策略 + 上海系名单 |
| 报告 / 候选表 | `recruit/hr/候选人筛选报告.md` · `recruit/hr/候选人筛选结果.md` · `recruit/hr/候选表-*.{md,csv}` · `recruit/hr/社招判定-简单简历.md` | 分级方法论 + 重点名单 + 风险提示 |

## ⚠️ 数据边界（红线 · **2026-10-11 supervisor 拍板：「接受姓名级入库」**）

> **背景**：原 HR 工作区已整体融入本仓（`recruit/hr/`），含**候选人姓名 / 学校 / 期望薪资 / 分级判定 / 沟通台账**。
> **裁定**：**接受「姓名级」数据入库**（⚠️ 前提：**本仓库必须保持 private**）。本条**取代**旧口径「PII 一律不入库」。

**✅ 允许入库**：候选人**姓名** · 学校/学历/专业 · 期望薪资 · 分级与判定结论 · 打招呼/沟通**摘要** · 已发消息台账（`hr/发送记录.md`）· 候选表（`hr/候选表-*.{csv,md}`）· HR 记忆与脚本。

**🚫 仍然禁止入库（**值级**凭据 / 直接标识符）**：
`cookie` **值**（`wt2`/`wbg`/`zp_at`/`bst` 的取值） · **`securityId` / `geekId` 的取值**（⚠️ 作为**字段名 / 规则文本**出现是允许的，值不行） · 身份证号 · **手机号** · **邮箱地址** · **简历 PDF / 简历原文** · **聊天截图**（`*.png/jpg`） · 浏览器 `profile/` · 网络抓包（`*.har`） · 任何密钥 / token。

- 📦 **单文件 ≥ 5MB**（简历 PDF 常见）：🚫 不 `git add`（含 `hr/`）；只登记 `files.md`（路径 / 字节数 / sha256 / 存放位置）。
- ✅ **入库前自检（必做）**：`bash recruit/check_pii.sh` —— 扫**值级**匹配（cookie/ID 赋值 · 手机号 · 邮箱 · 私钥 · Basic 认证）；**命中即停、人工复核**。
- 🚫 **对外动作**：默认关闭 —— 发消息 / 抓简历 / 代点「同意·拒绝」需运维指令区**显式授权一批**；**约面控件永不碰**（见任务书 §3）。
