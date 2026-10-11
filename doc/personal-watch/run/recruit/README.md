# recruit/ — recruit 线目录（记忆/任务/能力 **已融入本仓** + 本线产物）

> 本目录是 **recruit 线**（观察哨第 3 条线）的目录。
> 🧬 **原 HR 招聘 agent 的记忆与能力已整体「融入」本仓** → **`recruit/hr/`**（**自包含，不依赖任何本地目录**；原 `C:\Users\liuyu\HR` 已不参与）。
> 🖥️ 本线 loop 跑在 **腾讯云 Ubuntu `106.54.228.191`**（浏览器走该机 Chrome + CDP，见任务书 §0.4）。
> 🚫 **本目录只放非 PII**；原始 PII/凭据（`securityId` / 简历 PDF / 截图 / cookie）**未入仓**（见 `.gitignore`）。

## 目录约定

| 路径 | 内容 | 入 git |
|:---|:---|:---:|
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

## 📁 目录约定

| 路径 | 内容 | 入 git |
|:---|:---|:---:|
| `hr/` | ⭐ **融入的 HR agent 记忆/任务/能力**（见上表） | ✅ |
| `STATE.md` | 招聘现状快照（非 PII 概述） | ✅ |
| `drafts/` | 话术草案（实际发送原文以 `hr/发送记录.md` 为准） | ✅ |
| `reports/` | 对外工作汇报 HTML（自包含） | ✅ |
| `files.md`（可选） | 大文件清单（路径 / 字节数 / sha256 / 存放位置） | ✅ |

## ⚠️ 数据边界（红线 · 与 HR `AGENTS.md §11` / `MEMORY.md §七` 一致）

- 🚫 **未入仓（仅存于原 Windows 目录）**：`boss_candidates.csv/.json`（含真实 **`securityId`**）、`候选人筛选结果.csv`、`简历/*.pdf`、`boss_chat*.png`、`简历.7z`、一切 cookie/凭据、playwright `profile/`。
- 📦 **单文件 ≥ 5MB**（简历 PDF 常见）：🚫 不 `git add`（含 `hr/`）；只登记 `files.md`（路径 / 字节数 / sha256 / 存放位置）。
- ✅ **记忆/能力在 `recruit/hr/`，账在 git；原始数据本体仍在「原 Windows 目录 / 外部盘」**。
- 🚫 **对外动作**：默认关闭 —— 发消息 / 抓简历 / 代点「同意·拒绝」需运维指令区**显式授权一批**；**约面控件永不碰**（见任务书 §3）。
