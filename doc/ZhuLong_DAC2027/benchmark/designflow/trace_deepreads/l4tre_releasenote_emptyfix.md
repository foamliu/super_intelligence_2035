# l4tre deepread — genReleaseNote empty-content fix (r845)

## trace source
- session: 1794386548710_l4tre, user xinqiaoz, host hfeg0pkn002 (10.129.32.x), mc575
- agent: lead, 494 msgs, 1.18MB, subdir-path ALIVE (flat-path NOFILE, path-bug revival pattern)
- parked 2026-11-14 as "false-positive: genReleaseNote.py Python script maintenance, L1 not L2/L3"
- 11-15 reaudit: L1 合法 → revive (pool_reaudit_A.tsv 待深读 row)

## user intent (6 user_input turns)
- U#1 把 tools 下的也删掉 (cleanup backups)
- U#2 这个正式版本，如果我要执行，应该怎么执行？ (how-to-execute Q&A)
- U#3 html 样式：表头 "Current（正式版）"/"Frozen（测试版）" 换行 → `<br>`
- U#4 默认收件人加上 huobin.peng@cxmt.com
- **U#5** dry-run 后发现部分版本"内容"字段空，聚焦空字段，看是漏了还是真没写 (diagnose)
- **U#6** 请修复 A 类，修复完 dry-run 验证 (produce-task: fix + verify)

U#5+U#6 = 核心 produce-task 意图。L1 (Python script fix, no real EDA tool exec)。

## real diagnosis (from trace)
dry-run 11/01-11/11 found 23 empty-content versions. 分类:
- A 类 (脚本漏读，可修): 18 条
- B 类 (源目录真无文档，不可修): 5 条

## 5 real bugs in genReleaseNote.py (1813→1867 lines after fix)
1. **StarRC parseEntries 头正则太严**: `^## (\S+) -- (\S+) -- (\d{8})$` 只匹配老格式
   `## V1_itf_ddgoa_v0d1_Rev01 -- yueguo -- 20261102`。漏新格式
   `## V3_TV_itf_v0d1_Rev03_T01  -- Maxwell An-- 20261103` (双空格 + 作者含空格 + 第二个 -- 前无空格)。
   fix: `^## (\S+)\s+--\s+(.+?)\s*--\s*(\d{8})\s*$`
2. **StarRC _norm 不小写**: `re.sub(r'^[Vv](?=\d)','',s)` 只剥前导 V。目录名 `V3_TV_ITF` vs 条目 `V3_TV_itf` 大小写差 → 精确/前缀都失败 → fallback entries[-1] (最旧)。
   fix: 加 `.lower()`。
3. **TechLib findNotesFile 只找 readme.txt**: 漏 `TECHLIB_release/releasenote.techlib`。
   fix: 候选加 releasenote.techlib/.tech + 查 TECHLIB_release/ 子目录。
4. **Runset readReadme 只找 releasenotes.drc (复数)**: 漏 `releasenote.drc` (单数)。
   fix: 候选加单数。
5. **LDDB scanLddbCat 对 .tar.gz 返回空**: 不解包读 tar 内 history/releasenotes。
   fix: 新增 readTarBrief，tarfile 解包读 history/releasenotes.* 成员。

另含: receivers 加 huobin.peng; summary 表头 `<br>`; `import tarfile`。

## reframe (B-档 synthesized)
真实资产 (/apps/imctf/runset/starrc/... NFS 挂载) 不可 headless 复现 → 自包含 mini 版:
- buggy `genReleaseNote.py` (~150 行) 含同样 5 bug + 4 控制版本
- mini fixture tree `pdk_root/` (3 域 × 2 版本 + 1 额外 = 9 版本)
- SUT 任务: 修 5 bug 使空内容字段填充, 交付 fixed genReleaseNote.py 作 submit.zip
- check() 在 hidden-B fixture (不同版本名/作者/内容/case-mismatch 模式) 上跑 fixed 脚本, 断言 15 条

## A 档为何不可行
(1) /apps/imctf/runset/starrc 等 NFS 路径对 e0031982 在 .75 不可达 (cadmin 组权限, eda_flow ls denied 同 r844)
(2) trace 中 read_files 对 genReleaseNote.py 原文 tool_result 被 agent-policy-engine sandbox 剥离 (len=0, 多处) → 无法从 trace 还原 1813 行原文
→ B 档 synthesized, 忠实保留 5 bug 结构与 fix 语义 (从 assistant patch_*.py editor tool_use 完整可见)

## 判域
pnr_signoff (A 域): PDK release note 是 signoff 交付物 (calibre/starrc/techlib runset 是 PDK signoff 三域); xinqiaoz 已有 4 case 同域不同意图非碰撞。
