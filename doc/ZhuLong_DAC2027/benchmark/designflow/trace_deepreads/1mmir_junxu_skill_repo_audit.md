# Deepread: 1789644520518_1mmir (junxu@hfeg0pkn005) — SkillRepoAudit-001

**session**: `1789644520518_1mmir/1789644520518_1mmir.messages.json`
**user/host**: junxu @ hfeg0pkn005 (10.129.2.14)
**mc**: 297 (virtuoso:1791; schematic:381; netlist:254; waveview:168; cellview:124; cadence:55; hspice:43; analog:27)
**domain**: layout_virtuoso (virtuoso-cli skill 仓库)
**agent**: lead (deepseek-v4-flash), 212 msgs / 1.16 MB, 2026-09-23

## 真实用户意图

junxu 维护自定义 skill 仓库 `/home/junxu/Agents/custom_design_skill/`，含 4 个 skill：
- `wv-cli`（已写文档，作模板）
- `virtuoso-cli`（TCP bridge daemon + Python API + SKILL bridge，66 commit 演进）
- `block-sim`（5 阶段仿真管线）
- `block-design`（设计树访谈 + 渐进式构建）

每个 skill 位于 `skills/<name>/`，有 `SKILL.md` + `src/` + `docs/`。junxu 当初只写代码，**忘了给 virtuoso-cli/block-sim/block-design 补设计文档和改进文档**。发起 brainstorming 会话，要求 agent 参照仓库现状 + git 提交历史、以 wv-cli 已有文档为模板，为这 3 个 skill 补写 design doc + improvements doc，中英一式两份（6 对 × 2 语言 = 12 文件）。

## agent 行为

1. 探索仓库：read 所有 SKILL.md + wv-cli 现有文档（design + improvements 模板）+ git log（virtuoso-cli 66 commit、block-sim 合并历史）+ 源码（schematic.py 等）。
2. 分类为 **Bounded** 任务（为现有代码库写文档，参考已有模板，无新构建）。
3. 列计划：3 skill × (design + improvements) × (EN + ZH) = 12 文件，遵循 wv-cli 模板结构（Problem Statement → Solution → Architecture → Implementation Decisions → Testing Decisions → Out of Scope → Further Notes）。
4. 用户 3 轮反馈：「好的」「继续」「文档中的图片用 mermaid 画而非 ascii，用语用人类自然语言（"红旗表"之类表达奇怪）」。

工具：read_files / editor / run_approved_command / search_codebase。

## 关键判断（case 化）

文档撰写本身是 prose，无法客观判分。但用户真实需求含一个**干净可判分的纯 Python 子问题**：在动笔写文档前，必须先对仓库做**结构化审计**——为每个 skill 汇总事实底座（哪些文件/文档存在、多少 commit 碰过、首尾 commit 日期、语言、顶层 API）。agent 探索阶段实际就在收集这类信息。

抽取子问题：写 `audit_skills.py` 读 skill 仓库（文件树 + 序列化 git 提交日志 `git_history.jsonl`），为每个 skill 输出结构化 manifest JSON。沙盒无需 Virtuoso/git/SKILL，标准库即可，干净可判分。

## 跨 shard 串台检查

- 4-shard ledger `1mmir` 仅 C（claim 通过）。
- C.jsonl trace_source 无 `1mmir`。
- junxu@hfeg0pkn005 既有 C case（r966 VirtuosoCliSkillReviewTestSuite-001 / r973 SchemStubPlacementPolicy-001），但**不同 session、不同子型**（本 case 子型 `skill_repo_audit_manifest_gen` 首例：仓库结构化审计 manifest 生成，正交于 skill 审查/test suite/几何策略）。session-level fresh + 子型正交，不冲突。

## 合成

- **A（可见）**: `repo_a/`（真 git 仓库，3 skill：virt-cli/net-sim/block-gen，6 commit across Sep 2026，不同 docs 存在性）+ `task_brief.md` + `hidden_manifest.json`。repo_a 根附 `git_history.jsonl`（序列化 git log，避免沙盒依赖 .git）。
- **隐藏 B**: `hidden/repo_b/`（真 git 仓库，3 个**不同** skill：wave-cli/pwr-ana/cell-lib，9 commit across Aug 2026，不同文件数/commit 数/docs 存在性/key APIs）。
- **check.py**: 20 条独立断言，在 B 上重跑 SUT 的 audit_skills.py，独立 oracle（文件树 + git_history.jsonl + ast）复算比对；含反硬编码（B 名 ≠ A 名）、确定性（3-seed）、真审计器（在 A 上跑 yields A 名）。
- **reference solve.py**: audit_skills.py 参考实现，PASS 20/20。
- **5 negatives**: empty_shell / print_only / hardcode_a / naive_stub / delete_core 全 FAIL（negative_selftest.py ALL EXPECTATIONS SATISFIED）。
- **§4.9 三假**: (a) 空壳→neg_empty_shell FAIL (b) 只 print 期望→neg_print_only FAIL (c) 删核心→neg_delete_core FAIL。

## 自验

- ref solve.py 在 B 上 PASS 20/20。
- 5 neg 全 FAIL（distinct failure reasons）。
- C.jsonl 573→574。
