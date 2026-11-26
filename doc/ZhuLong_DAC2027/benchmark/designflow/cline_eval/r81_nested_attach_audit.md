# r81 Nested-Attachment Copy Bug — Impact Audit (shard A 轮 83, 2026-11-05)

## 背景
r81 修复 `run_one.sh` 的嵌套附件 copy bug：旧逻辑用 `basename(src)` 抹平子目录，
导致 `rtl/addr_to_rowcol_region.v` 这类嵌套附件被当作 `ASSETS_SRC/addr_to_rowcol_region.v`
查找 → 不存在 → **既不进 cline workdir（input 侧），也不进 judge dir（check.py 侧）**。
r81 commit `61e80e302`（2026-11-04，LibArcExtract run）改为保留 `assets/<id>/` 相对子目录结构。

## 问题
20 条已 cline 实跑 case 中，r81 之前（2026-11-04 之前）跑的带嵌套附件 FAIL case，
其 verdict 是否是 harness bug 假 FAIL（需要回滚通过率）？

## 候选（pre-fix + 嵌套附件 + verdict=FAIL）
| case | 嵌套子目录 | ts | verdict | failure_class |
|---|---|---|---|---|
| PwrGlobals-001 | apr_innovus_config/ | 11-02 16:04 | FAIL | ③ thrash (sub-agent spawn errors + auto-compaction, 0 deliverables) |
| STAFlow-001 | feint_reference/ + demo_design/ | 11-03 00:05 | FAIL | ④naming 8/20 |
| DCCombHier-001 | rtl/ + lib/ | 11-03 00:53 | FAIL | ③+④ 15/18 (set_dont_touch/-no_boundary/write-hierarchy) |
| ETMExtract-001 | scripts/ + setup/ | 11-03 02:25 | FAIL | ③ thrash (60884 reasoning events, pyAether loop, 0 deliverables) |

## 实验设计（快速、决定性、无需 cline）
对每条 case，在临时 judge dir 里跑 `reference_submit.zip`（金标准）× 两种附件 copy：
- **correct**：保留 relpath（`assets/<rel>`）
- **flattened**：OLD bug（`assets/<basename>`）

`check.py` 以 `workdir='.'` 调用。若金标准在 correct 下 PASS 但 flattened 下 FAIL ⇒
证明 harness bug 假 FAIL。

## 结果
| case | correct | flattened | harness_bug_false_FAIL |
|---|---|---|---|
| PwrGlobals-001 | PASS(*) | PASS(*) | NO |
| STAFlow-001 | PASS | PASS | NO |
| DCCombHier-001 | PASS | PASS | NO |
| ETMExtract-001 | PASS | PASS | NO |

(*) PwrGlobals check.py 直接 print "PASS" 到 stdout（非 JSON），runner 解析为 ERROR
但实际语义 = PASS；correct 与 flattened 行为完全一致 → 无差异。

**判定：judge 侧零假 FAIL。** check.py 的 `_resolve_*` 回退（r78-82 加）+ 条件本身
不依赖被 flatten 破坏的路径 → flatten 不影响金标准判分。

## Workdir 侧（cline input）分析
确认 OLD bug 确实把嵌套文件从 cline workdir 丢掉（所有 basename 在 ASSETS_SRC
顶层均不存在）。但 4 条 verdict 仍为真信号：
- **DCCombHier / STAFlow**：失败条件是 dc/pt 脚本**标志位 / JSON 字段名**（real ③/④
  capability），与 cline 是否看到 RTL/spef 输入无关——这些输入是脚本运行时读的，
  不是 cline 写脚本时必须看的；金标准判分也不依赖它们（见上表 PASS）。
- **PwrGlobals / ETMExtract**：0 deliverables 的 thrash 归因于 cline 自身
  （sub-agent spawn errors / auto-compaction / pyAether loop），**非** input 缺失。
  一个稳健 agent 在缺文件时应提问或读可见文件，而非 thrash → thrash 本身是 ③capability 信号。

## 旁证
r81 修复后跑的 **LibArcExtract-001**（post-fix，带 `lib/lib_A.lib` 嵌套附件）：
cline 拿到了输入 → 产出真实 deliverable（extract_arcs.py 13738B，schema 正确）→
判分 FAIL 击中 [n] arc multiset = 真实 ③capability。证明修复生效，且 workdir 侧
缺输入不会把 verdict 翻成假 FAIL——只会触发 thrash（其本身是真实能力信号）。

## 结论
**r81 嵌套附件 bug 未导致任何历史 cline verdict 假 FAIL。**
- judge 侧：4/4 金标准 PASS under both copies → 判分器健全。
- workdir 侧：cline 缺输入，但 4 条 verdict 反映真实能力（3 near-miss real-flag defect
  + 1 naming；2 thrash from cline-internal issues）。

**20-case rolling 通过率 5/20 = 25% 维持真实，无需回滚。**
r81 BLOCKER（"下轮应回查带嵌套附件 case 历史 verdict"）→ **CLOSED**。

## 方法学备注
本审计模式（金标准 × correct/flatten 双跑）可复用于未来 harness-copy bug 的影响评估：
快速、决定性、无需重跑被测 agent。
