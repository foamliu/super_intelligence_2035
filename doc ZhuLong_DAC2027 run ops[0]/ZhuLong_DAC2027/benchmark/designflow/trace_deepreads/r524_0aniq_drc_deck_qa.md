# r524 deepread: 1793878425402_0aniq — Calibre DRC deck-update QA (physical_verify L2) · 2026-11-13

**状态**: CASE DELIVERED (r524, physical_verify, mc=111) — EDA-Eval-DesignFlow-DrcDeckUpdateQa-001。
第 2 个连 fresh C 域 produce-task case（r523 DrcQaAutoPipe-001 后）。

## session 元数据
- **session_id**: 1793878425402_0aniq · user=kenwang · host=hfeg0plg16 (172.16.8.192)
- **mc**: 111 · **domain**: physical_verify
- **messages.json**: 4401 行
- **cwd**: /home/kenwang (work under `/rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/`)
- **title** (推断): QA Calibre DRC deck update (1P22M Rev13_S12_1030) against `.bak` rule spec
- **keywords**: drc / calibre / SVRF / rule deck / 1P22M / Rev13 / SKIP / metal stack

## 用户意图（真实任务摘要）
用户更新了一份 Calibre DRC rule deck（`35H_DRC_Cal_V0d1a_Rev13_1P22M_16F...drc`，~176K 行，
1P22M 金属栈 Rev13_S12_1030 版本），需要对照一份更新规格说明（`backup/update_1030_rules`，
~857 行，89 条 rules）做 QA：检测遗漏 (OMITTED)、描述变更 (DESC_CHANGED)、代码更新缺失
(CODE_MISSING)、以及隐藏问题（HIDDEN_SKIP — 应对新 metal stack 激活但被 SKIP 的 rules）。

## 真实资产（172.16.8.192, permission restricted）
| 文件 | 路径 | 大小 | 用途 |
|:--|:--|--:|:--|
| DRC deck | `.../Rev13_S12_1030/35H_DRC_Cal_V0d1a_Rev13_1P22M_16F...drc` | ~176K 行 | 更新后的 rule deck (SVRF blocks) |
| rule spec | `.../backup/update_1030_rules` | ~857 行, 89 rules | 更新规格说明 (`.bak`) |
| (确认方式) | session messages 引用 + grep 行号 | — | 直接 ls permission denied，经 session 确认存在 |

## case 合成方案（DrcDeckUpdateQa-001）
真实文件 too large/proprietary → **SYNTHESIZED fixtures** modeled on 真实任务结构：
- **spec format** (`update_rules.bak`): header `METAL_STACK:`/`METALS_DEFINED:` + `@@RULE id|status|desc|code_hint|skip_reason` 行
- **deck format** (`drc_deck_*.drc`): header `// METAL_STACK:`/`// METALS_DEFINED:` + `<blockid>{@rule @desc code...}` blocks
- **A fixture** (visible): 1P12M, 10 rules (6ok/1omit/1desc/1code/1hidden)
- **B fixture** (hidden, check runs on B): 1P22M, 13 rules (5ok/2omit/2desc/2code/2hidden)

**candidate** `drc_deck_qa.py`: parse_spec + parse_deck + classify(rule, deck_metals, blocks) → 6 values
(verdict, detail, block_found, desc_match, code_found, hidden_skip) → JSON report。

## check.py 16 条件 a-p（k_check=16, k_rationale=16, ≥8✓）
- a: zip 解压 + 无路径泄露 + drc_deck_qa.py 存在
- b: compile + stdlib-only + --help exit0 / no-args exit!=0
- c: B run exit0 + output 生成
- d: report 必填 fields (rules, summary)
- e: verdict 计数对齐 (OK/OMITTED/DESC_CHANGED/CODE_MISSING/HIDDEN_SKIP)
- f: OMITTED 条目数正确
- g: DESC_CHANGED 条目数正确
- h: CODE_MISSING 条目数正确
- i: HIDDEN_SKIP 条目数正确
- j: block_found 字段
- k: desc_match 字段
- l: cross-input sha256 防硬编码（A run report sha256 ≠ B run report sha256）
- m: determinism（同 B 输入两次 run sha256 相同）
- n: A≠B report diff（防硬编码 A）
- o: A run exit0
- p: reason 含 rule_id

## 防硬编码设计
- B metal_stack=1P22M ≠ A 1P12M
- B 13 rules ≠ A 10 rules (different ids/counts/status 分布)
- check.py 内联 A/B fixtures 为 gzipped base64 blobs (BLOB_A/BLOB_B)
- cross-input guard (cond l/n): A report 必须与 B report 不同

## 自验
- GOLD PASS 16/16 ✓ (check.check returns True)
- negative_selftest 5 fakes NEG_RC=0 ALL-FAIL ✓
  - fake_empty → b · only_print_expected → b · fake_core_deleted → d · naive_hardcode_a → d · wrong_regex → e
- §4.9 三假 (empty/print/core-deleted) 全 FAIL ✓
- k_rationale==k_check==16≥8 ✓

## 台账
- claim: r523 `trace_ledger.py --shard C claim --session 1793878425402_0aniq --user kenwang --host hfeg0plg16 --match 111 --domain physical_verify`
- mark: r524 `--status case --case-id EDA-Eval-DesignFlow-DrcDeckUpdateQa-001` ✓ (physical_verify 124→125)

## 覆盖率
- C.jsonl: 311→312 entries
- physical_verify: 124→125
- trace 覆盖率: 312/3260=9.6% (target_mc=10, src=summary_1109.tsv)
- mc≥10 fresh pool: 396 ≠ 0 (不写池枯竭)
