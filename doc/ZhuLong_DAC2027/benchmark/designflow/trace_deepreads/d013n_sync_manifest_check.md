# trace deepread — d013n (xinqiaoz / hfeg0pkn002, mc=292)

- session: `1790044235443_d013n.messages.json` (618 KB, 197 msgs)
- user: xinqiaoz @ hfeg0pkn002 (10.129.2.11), agent=cline (deepseek-v4-flash, xqzhou-glm provider)
- tools: read_files 16, list_allowed_files 11, run_approved_command 26 (git/python profiles), editor 50, search_codebase 1, ask_question 3, skills 1 (handoff)
- domain: **eda_other** (PDK QA system tooling/infra; calibre keyword incidental — "DRC" is a PDK QA module dir, not the calibre tool). level: **L2-static** (subprocess git + python execution of candidate scripts; no commercial EDA tool).

## user inputs (verbatim, real human text)
- USER#1 idx0: handoff resume from `/home/xinqiaoz/PDK_QA/pdkQaSystem/.tmp/HANDOFF_sync_mechanism_design.md` (NOT usable — references handoff doc we lack; this is a resume, not a clean need).
- USER#2 idx37 (clean build-need, A-faithful source): 「1. stable 分支发生变更时，我无法接收通知。因此我来拉取是比较麻烦的，而我们的 feature 在合入 stable 时，一定要注意的就是不能覆盖 stable 中不是我做的修改。请考虑一下有没有更好的方案？ 2. 选项 C 3. 选项 A 4. 选项 X。此外我有一个额外的问题，你说的 __init__ 那 4 行在 manifest 是指什么？」→ 提出需求（sync 机制不能覆盖他人改动），未给根因/修复方案 → A-faithful 合格。
- USER#3 idx47: Q1 认可 + 追问 stable->local 同步提示（补充需求）。
- USER#4 idx86 (concrete spec): 「stable：/apps/imctf/develop/PDK_QA/pdkQaSystem/DRC/ -> local：DRC / stable：.../common/ -> local：common」（stable↔local 路径映射）。

## assistant build flow
1. handoff skill resume → read HANDOFF_sync_mechanism_design.md (prior session context).
2. git status/log/diff on `/home/xinqiaoz/PDK_QA/pdkQaSystem` (run_approved_command git profiles).
3. designed `sync_to_stable/manifest.yaml` (idx54, 3950c) — 同步队列 5 批次 (B1-B5), 每批次 commits/target_files/verify/commit_message/config_note/prerequisite, order 链, 四条铁律 (源头唯一/基线实时/终态锚定/commit规范), version, note, known/todo 注释.
4. `check_manifest.py` (idx62) — yaml 加载 + 结构校验 + 打印 order/批次摘要.
5. `diff_feasibility.py` (idx97→104, 多次迭代) — 对 manifest 中 target_files, `git show HEAD:rel` vs stable 文件, difflib SequenceMatcher 报 stable/localHEAD/equal 行数 + ratio, 标注 stable 缺失文件.
6. `generate_snapshots.py` (idx114, 3353c) — 生成器读 manifest + stable 基线 + 链式 commit diff 产快照 (终态==HEAD 逐字节). [本 case 不纳入交付，因 git-diff 链式字节锚定校验过重，下轮可独立成 case]
7. py_compile 校验 (idx140), 多次 run_gen/run_gen2 验证, 最终写 HANDOFF_sync_phase2_phase3.md (idx185) 交接.

## gold (trace-faithful, 人工复核)
trace 末尾用户未明确口头「接受」，但交付件齐全（manifest.yaml + check_manifest.py + diff_feasibility.py + generate_snapshots.py + 2 HANDOFF）且经 py_compile 通过 → gold = manifest.yaml 设计 + check_manifest.py (通用校验器) + diff_feasibility.py (通用差异报告器). 本 case scope 收为前三件（generate_snapshots.py 留作未来 case）。

## 资产 A 重建
真实 `/proj/.../pdkQaSystem` 与 stable `/apps/imctf/develop/...` 在本机不可达 → 由 trace 真实文件结构重建迷你 fixture:
- `repo_A.tar.gz`: git 仓库 (3 commit: init/derived-layers/childId+dedup), HEAD 触 LdrInfo.py + DrcInfo.py.
- `stable_A/`: stable 基线 (DrcValueCheck.py=drcOwnerMap 变体, LdrInfo.py=assoc 变体, DrcInfo.py 故意缺失测 NOT-PRESENT 标志).
- `git_log_A.txt`, `path_mapping_A.txt` (USER#4 逐字).
trace-faithful in structure (同模块名同功能同 stable-差异语义).

## 泛化 / hidden B
hidden B = 不同 PDK QA 子系统 (qa/lint/RuleCheck + qa/util/Logger + qa/util/Config), 批次名 S1/S2 (非 A 的 B1/B2), stable 缺 Logger.py. 候选 check_manifest.py + diff_feasibility.py 必须通用 (不得硬编码 A 批次名/文件路径).

## 判分
check.py 16 条件 a-p: (a)zip含3件 (b)manifest结构 (c)order==batches (d)批次必填字段 (e)commits hex (f)check_manifest自身manifestPASS (g)check_manifest B通用打印S1/S2 (h)check_manifest B报B文件 (i)diff_feasibility A报3文件+标缺失 (j)diff_feasibility B报3文件+标缺失 (k)B ratio∈[0,1] (l)B 行数匹配ref (m)反硬编码无A字面量 (n)3-seed确定性 (o)无PASS哨兵/无reference读 (p)语法compile. 自验: ref PASS 16/16, 3 negs FAIL, anti-cheat(c) ref-删核心 FAIL.
