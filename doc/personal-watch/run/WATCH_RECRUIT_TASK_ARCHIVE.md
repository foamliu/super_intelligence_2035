# WATCH_RECRUIT_TASK_ARCHIVE.md — recruit 任务书归档

> **用途**：按 `WATCH_RECRUIT_TASK.md` §5「任务书自己滚」规约，把**已闭合的历史轮次 / 已执行完毕的运维块【原文】搬入本文件**（**不改写任何指令**），任务书正文只留 **1 行指针**。
> **纪律**：本文件是**原文归档**，**不新增、不改写任何指令**；一切以 `WATCH_RECRUIT_TASK.md` 现行版本 + `recruit/hr/` 仓内权威为准。
> 归档原因：任务书 = **每次唤醒的 prompt**，须控制体积（目标 ≤ 32KB，红线 40KB）。

---

## 归档块 A · 运维指令「第 1 批」（2026-10-11 · 立线）— 已执行完毕，2026-10-11 第 4 轮归档

> ⚠️ 原文照搬；其「对外动作闸门」条款**已被第 3 批取代**（见任务书运维指令区）。

### 🆕 运维指令 · 2026-10-11（**【第 1 批 · P0】立线：继承 HR 记忆与能力 + 常态化招聘推进**）· ⭐ **每轮先读**（⚠️ 其「对外动作闸门」条款已被第 3 批取代）

> **用户原话（2026-10-11）**：「**personal-watch 目录下，已经有 research 和 news 两个任务书 + agent loop，现在建第三个（recruit），agent 记忆和能力继承：`C:\Users\liuyu\HR`。**」
> **本批目标（三件事，按序）**：
> ① **继承记忆**：唤醒后先读 `$HR_DIR/MEMORY.md` + `$HR_DIR/USER.md` + `$HR_DIR/AGENTS.md` + 最近 2 天 `$HR_DIR/memory/*.md`（`$HR_DIR` = `C:\Users\liuyu\HR`，可用环境变量 `WATCH_HR_DIR` 覆盖）。**读到才算继承**；读不到（路径不存在）→ 如实记进 `MEMORY_RECRUIT.md`，并用 §0.2/§0.3 的**内嵌摘要**兜底。
> ② **继承能力**：按 `$HR_DIR/AGENTS.md` 的 **Boss 页面操作 SOP** 驱动浏览器（**登录态只在 MCP 默认 context**）；复用 `$HR_DIR/screen.py` / `city_scan.py` / `话术-最终版.md`。
> ③ **常态化推进**：按 §1 工作流**继续招聘链路**（采集 → 分级 → 复核口径 → 起草话术 → 收简历归档 → 交 HR），并把结论回写 `MEMORY_RECRUIT.md` + `daily-memories-recruit/` + `$HR_DIR` 记忆。
> **⚠️ 对外动作闸门（本批硬性）**：**无人值守默认保守** —— 采集/分级/复核/起草/归档/记忆更新 **自主**；**对外发送消息 / 代点「同意·拒绝」 / 约面** 一律要 **本区显式授权一批** 才可执行（授权写法：`【授权批次 · <日期>】名单=<…> 动作=<发送话术|同意收简历>`）。🚫 **未授权绝不对候选人发任何消息、绝不点任何改变对方会话状态的控件**。
> **优先级**：本批 = **本线当前 P0**。额度/时间紧张时，**先做「继承 + 状态汇报」**（①②），再谈对外推进（③）。
> **首次唤醒必须做**：写 `MEMORY_RECRUIT.md` 状态头 + 进度快照 + 1 条流水；写当日 `daily-memories-recruit/<YYYY-MM-DD>.md`；`git add` 本线文件 → commit → push（见 §5）。
> **完成后**：更新 `MEMORY_RECRUIT.md`（快照 + 流水）+ 当日 `daily-memories-recruit/<date>.md` 心跳；commit → push（只加本线文件）。

---

## 归档块 B · 运维指令「第 2 批」（2026-10-11 · 融入本仓）— 已执行完毕，2026-10-11 supervisor 归档

> ⚠️ 原文照搬；其要点已由任务书运维指令区 **1 行指针** 概括。

### 🆕 运维指令 · 2026-10-11（**【第 2 批 · P0】把 HR 记忆与能力「融入」本仓 —— 去掉本地目录依赖**）· ⭐ **每轮先读**

> **用户原话（2026-10-11）**：「把 `C:\Users\liuyu\recruit` 中 agent 的**任务和记忆融入**观察哨 agent loop……**融入的意思是信息融进来，不要再依赖原目录** —— 观察哨在腾讯云执行，根本看不到这个目录。」
> **已做（supervisor）**：把 HR agent 的 **37 个记忆/任务/能力文件**（`MEMORY.md` · `USER.md` · `AGENTS.md` · `DREAMS.md` · `README.md` · `memory/*` · `发送记录.md` · 话术 · 报告 · 候选表 · `screen.py`/`city_scan.py` 等脚本）**整体复制进仓内 `recruit/hr/`**；任务书 / loop / `MEMORY_RECRUIT.md` / `recruit/README.md` 里**所有 `$HR_DIR`、`C:\...` 引用已改为仓内相对路径**。
> **生效**：**`recruit/hr/`（仓内）= 唯一权威**；**原 `C:\Users\liuyu\HR` 目录不再参与**（离线 / 不可达都能跑）。**§0.4⑧ 的「VM 读不到 `$HR_DIR`」缺口就此关闭**。
> 📌 **历史块路径换算**：本区「第 1 批」及更早出现的 `$HR_DIR/xxx` **一律读作仓内 `recruit/hr/xxx`**（老块不改，仅在此换算）。
> **铁律不变**：🚫 **原始 PII/凭据不进仓** —— `boss_candidates.*`（含 `securityId`）、`简历/*.pdf`、`boss_chat*.png`、cookie **均未复制进本仓**（**第 4 批起：这些 PII 落在 VM 本地 `~/hr_resumes/`，仓外、不进 git**）。对外动作闸门见 §3 + 第 3/4 批。
> **回写改向**：记忆更新**写仓内 `recruit/hr/`**（`MEMORY.md` / `memory/<date>.md` / `DREAMS.md`），**不再回写 `C:\...`**。
