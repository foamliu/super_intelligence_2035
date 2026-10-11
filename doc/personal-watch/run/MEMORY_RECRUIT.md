# MEMORY_RECRUIT.md — 观察哨 · **recruit agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_recruit_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-11 起沿用定时节律：每天 2 次 · 06:00 / 18:00 本地时区**，由 loop 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
已完成:       [第 0 轮 · 2026-10-11 立线] 建立 recruit 线脚手架（任务书 `WATCH_RECRUIT_TASK.md` + loop `watch_recruit_loop.sh` + 本记忆 + `daily-memories-recruit/` + `recruit/`）；**继承源锁定** `$HR_DIR = C:\Users\liuyu\HR`（记忆 4 层 + Boss 能力 SOP + 脚本/话术）；**继承摘要内嵌**任务书 §0.2（长期记忆）/§0.3（能力 SOP），唤醒即「已记得」；**对外动作闸门**确立（默认保守，发送/同意/抓简历需运维授权）。**【待首轮唤醒】**：读 `$HR_DIR` 记忆 + 巡检 Boss + 写 `recruit/STATE.md` 现状快照。
当前动作:     第 0 轮（立线）：仅落脚手架与继承规约，**未对 Boss 做任何页面操作、未对候选人发任何消息**。
下一步:       ① **首轮唤醒（下一次 06:00/18:00 时窗）**：按任务书 §1 第 1 步读 `$HR_DIR/MEMORY.md`+`USER.md`+`AGENTS.md`+近 2 天 `memory/*.md`（读不到→内嵌摘要兜底并如实记）；② 巡检 Boss 登录态（新标签读 `.chat-message-list`：只读）；③ 复核 `$HR_DIR/发送记录.md` 尾部（近批次送达 / 有无风控）；④ 产出 `recruit/STATE.md`（达标者数 / 批次进度 / 待办；**非 PII 概述**）；⑤ 汇总 `$HR_DIR` §八 未决口径 + README 待办 → 本文件「待拍板」；⑥ **不做**任何对外发送（除非运维指令区下「授权批次」）。
本轮新增:     0（立线轮，无采集、无对外动作）。
阻塞:         无（⚠️ 待核验：本机是否具备 Git Bash/WSL + playwright-mcp + cline；`$HR_DIR` 是否可达）。
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
- **运行位置**：**持 Boss 登录态 + playwright-mcp 的机器**（当前 = 本 Windows 机；用 Git Bash/WSL）
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

> ⚠️ **数据边界**：`boss_candidates.csv/.json`（含 `securityId`）、`候选人筛选结果.csv`、`简历/*.pdf`、`boss_chat*.png`、cookie 凭据 —— **一律不进本仓库**（任务书 §0.1③ / §4-7、`recruit/.gitignore`）。

---

## 3. 流水（倒序，保留最近 ~20 条）

- **2026-10-11（立线轮 · 第 0 轮）** —— **建立 recruit 线（观察哨第 3 条线）→ 继承 `C:\Users\liuyu\HR` 记忆与能力**：新建 `WATCH_RECRUIT_TASK.md`（只读任务书；§0.1 继承映射 · §0.2 继承的长期记忆摘要 · §0.3 继承的 Boss 能力 SOP · §1 工作流 · §3 对外动作闸门 · §4 铁律 · §5 记忆维护）+ `watch_recruit_loop.sh`（照抄 research 模板三防坑 + 定时 6,18 + `$HR_DIR` 自检横幅）+ 本记忆 + `daily-memories-recruit/` + `recruit/`（README/`.gitignore`/STATE 占位/`drafts/`/`reports/`）；登记 `../AGENTS.md §1` + `../README.md §2/§3` + `run/README.md`。**规约决定**：① **引用式继承**（HR 为唯一权威，仓库不复制其 4 个记忆文件）；② **对外动作默认关闭**（发送/抓简历/代点同意·拒绝需运维授权；约面永不碰）；③ 运行位置 = 持 Boss 登录态的机器。**本轮未做任何 Boss 页面操作、未发任何消息**。

---

## 4. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-recruit/<条目日期>.md`（原文不改），再从本文件删除。
- **任务书自己滚**：`WATCH_RECRUIT_TASK.md` 超限时，把**已闭合**的历史轮次/已执行完的运维块原文搬入 `WATCH_RECRUIT_TASK_ARCHIVE.md`（留 1 行指针，不新增/不改写指令）。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条。
- **归档不改变任何结论**；`WAITING:` 纪律不变。
- **回写 `$HR_DIR`**：招聘结论（新达标者 / 口径变化 / 教训）同时按 HR `AGENTS.md §10` 写回 `$HR_DIR`。

