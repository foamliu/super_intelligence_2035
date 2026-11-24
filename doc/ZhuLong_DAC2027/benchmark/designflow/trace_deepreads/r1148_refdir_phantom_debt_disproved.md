# r1148 — §4.9 refdir "DEBT:10" phantom disproved — 2026-11-24

## 背景
r1147 MEMORY 记 `DEBT:10 条无 refdir case 待重建`，源自 r1144 phantom-revival 的「13 条无 reference/ 目录」结论。r1145-1147 每轮重建 1 个 refdir（ResCornerTempSweep / TieJitterIncGenProduce / DutyOffsetAlertMaxProduce），把 13→10。

## 本轮审计（推翻 DEBT:10）

### 1. r1144「13 missing」是 short/full 命名匹配 bug
r1144 扫描用**短名** `<X>-001` 检查 `reference/`，但 case 的 `task_id` 是**全名** `EDA-Eval-DesignFlow-<X>-001`。evaluator (`build_lite.find_check_py` / `run_design_flow_batch`) 按 `task_id`（全名）查 `reference/<task_id>/check.py`。30 phantom case 中绝大多数在 HEAD 里**一直有全名 refdir**（如 FinesimMt0ParserProduce-001 全名 refdir 自 r1071 起就在 HEAD），r1144 漏检全名 → 误报「missing」。

### 2. r1145-1147 重建创建了 orphan 短名 refdir
r1145-1147 在 working tree 创建了**短名** refdir（ResCornerTempSweep-001 等），与 HEAD 已有的**全名** refdir 重复。这些短名 dir **从未提交到 HEAD**（只存在于 working tree 的 scratch），evaluator 用全名查也查不到短名 → orphan。本轮 `git rm` 清掉这 3 个 orphan（HEAD 本就不含，rebase 后 working tree 也清）。

### 3. 本轮 working tree 是脏的
本轮开局 working tree 状态：许多全名 refdir 被从 working tree 删除（但 HEAD 仍 tracked）+ 大量短名 scratch dir（untracked，来自历史 session 残留）+ 4 个 §4.9 embedded case 的 selftest 是旧版（引用 nested `reference/check.py` 路径）。这导致首轮审计误判「70 B case 缺全名 refdir」。

并发 shard D 的 `git pull --rebase --autostash` 把 working tree 重置回 HEAD，**恢复了全名 refdir**、清掉短名 scratch、selftest 回到 HEAD 版本（已是 `REF_DIR = HERE` 正确路径）。重置后 B 审计：**598/598 全名 refdir + check.py（evaluator-visible）**。

### 4. 4 个 §4.9 embedded case 在 HEAD 里本就是 flat 布局
GvimCjkConfigGen / HspicePanelCurProjReport / SolidoSimlogLocateGuide / TermInvestigationReport — HEAD 里 `reference/<id>/check.py`（flat）+ `negative_selftest.py`（`REF_DIR=HERE`/`REF=HERE` 正确路径）+ `negative/`。本轮 working tree 曾出现 nested `reference/check.py` 旧布局（脏），rebase 重置后回到 HEAD 的 flat 正确布局。3/4 selftest 实跑 PASS（HspicePanel / SolidoSimlogLocateGuide / TermInvestigationReport）；GvimCjk 有 pre-existing `assets/.../hidden/_gen_B.py` 缺失（非本轮引入，与本轮无关）。

## 结论
- **DEBT:10 是 phantom**：HEAD 里 30 phantom case 全有全名 refdir，r1144 的「13 missing」是命名匹配 bug，r1145-1147 的「重建」是重复劳动（创建 orphan 短名 dir，未提交）。
- **B §4.9 refdir 可见性**：598/598 case 在 HEAD 里 evaluator-visible（全名 refdir + check.py）。无新 refdir 需建。
- **r1145-1147 orphan 短名 dir 已清**（3 个，HEAD 本就不含）。

## 剩余真 §4.9 债务（pre-existing，非本轮引入）
- 3 个 B case 有 orphan 短名 refdir（BuildStepCacheClassifyProduce-001 / NetlistCmp-001 / SlicerMeasureGen-001）：短名 dir（带 selftest）与全名 dir（无 selftest）布局不同（flat neg .py vs negative/ dir + pre-built zip），需 case-by-case 合并，本轮未动（eval 路径全名 check.py 已 OK）。
- 10 个 B case 全名 refdir 缺 `negative/` 目录。
- 250 个 B case 全名 refdir 缺顶层 `negative_selftest.py`。
- 84 个 B case `negative/` 内 <2 个 .py 负样本。
- GvimCjkConfigGen-001 缺 `assets/.../hidden/_gen_B.py`（r1101 声称补过但实际缺失）。

## fresh 池
仍耗尽（r1125-1147 七轮 reconfirm，无新 scan）。本轮为 governance/audit 轮，不消耗 trace。

## 台账
不变（1769：case 597 / parked 1172）。covered=597/4529=13.2%。本轮无新 case。
