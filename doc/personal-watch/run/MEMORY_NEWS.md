# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 0

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义：`0` = 有近期待办（短睡 30min 续跑）；`1` = 无近期待办（常态，睡 1h 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        prep_api（前期任务 T1–T4，尚未开工）
已完成:       无（首轮因模型名写错而空转，已修）
当前动作:     等待 loop 重启（模型名已改为 deepseek-v4-pro）；随后执行任务书运维指令区第2批 T1–T4
下一步:       T1+T3 调研 → T2 配置并实测 web search MCP → T4 产出 news/API_COMPARISON.html
本轮新增:     0 条
阻塞:         无（模型名问题已修：本机网关仅支持 deepseek-flash / deepseek-v4-pro；WAITING 已置 0）
ERROR_COUNT:  1（首轮：模型名 deepseek-v4-pro-fp4 不被网关支持 → cline 报错退出、白睡一轮；已修）
```

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- （暂无）

---

## 1. 状态头

- **线**：news（新闻采集）
- **任务书**：`WATCH_NEWS_TASK.md`（只读）
- **产物**：`news/<YYYY-MM-DD>.md`（当日摘要）· `news/SEEN.md`（去重台账）· `news/INDEX.md`（索引）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：常态每小时一轮上限（`WAITING=1` 睡 1h）；有近期待办 `WAITING=0` 短睡 30min
- **上次采集窗口**：`<尚未开始>`
- **累计收录**：`0` 条

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-03** —— 建线。任务书 / loop / 记忆 / 产物目录就位。
- **2026-10-03** —— ⚠️ **首轮空转（已修）**：loop 拉起后 cline 报
  `The supported API model names are deepseek-flash, deepseek-v4-pro, but you passed deepseek-v4-pro-fp4`
  → 本轮什么都没干却 `exit 0`，且 `WAITING:1` 触发长睡。修复：① loop `MODEL` 改 `deepseek-v4-pro`；
  ② `WAITING` 置 `0`；③ loop 增加"抓 cline 致命错→强制短睡重试"兜底；④ `SLEEP_LONG` 6h→1h。
  **待 loop 重启后执行前期任务 T1–T4。**

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-news/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
