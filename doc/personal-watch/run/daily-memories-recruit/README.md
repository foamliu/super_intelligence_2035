# daily-memories-recruit/ — recruit 线每日流水（归档）

> 本目录是 **recruit 线**的**每日流水归档**，**不进每次唤醒的 prompt**（省 token）。
> 范式同 `daily-memories-news/` / `daily-memories-research/`。

## 用途

- `MEMORY_RECRUIT.md` 超 32KB 时，把**较早的流水条目**（保留最近 ~20 条）**原文追加**到 `daily-memories-recruit/<条目日期>.md`，再从 `MEMORY_RECRUIT.md` 删除。
- 也可直接按天记：每轮唤醒在 `daily-memories-recruit/<YYYY-MM-DD>.md` **追加**本次心跳（做了什么事 + 关键证据 1–3 行）。

## 文件命名

- `YYYY-MM-DD.md` —— **日期用 Boss 页面时间**（本机时钟慢约 8 小时；与 `$HR_DIR/memory/` 口径一致）。

## 纪律

- 🚫 **不写 PII / 凭据**（同 `$HR_DIR/memory/` 与任务书 §4）：cookie、`securityId`、简历里的身份证/手机号/邮箱/住址一律不写。
- ✅ **可溯源**：结论要能追到证据（Boss 会话原文关键句 / 简历 publication list / `$HR_DIR/发送记录.md` 行号）。
- ✅ **归档不改变任何结论**；原文照搬。
