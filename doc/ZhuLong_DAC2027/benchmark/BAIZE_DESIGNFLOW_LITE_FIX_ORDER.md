# BAIZE_DESIGNFLOW_LITE_FIX_ORDER.md — Lite 集（500）优先修复令 · 4 shard 共享规格

> **下发**：2026-11-24 21:5x · 用户令「安排 designflow 4 shard 优先修复 lite 集」
> **适用范围**：designflow shard A / B / C / D（`BAIZE_DESIGNFLOW_BENCH_TASK_<shard>.md` 顶部有指针）
> **优先级**：本令 **高于**造新题 / 扩池 / 治理 / intent_audit / stop-loss 轮次的排期，但**不改变**任务初衷与三条铁律（不改题面、不降难度、不删题凑数）。
> **体量**：本文件 ≤ 8KB；各 shard 只在任务书顶部留 4 行指针。

---

## 0. 一句话

**把 `cases_lite.txt` 里的 500 条，逐条修到「参考解必 PASS + ≥3 neg 必 FAIL + 判分契约合规 + 评测机（36.15）真能跑 + 无泄漏/无硬编码」；在 500/500 全绿之前，4 个 shard 不再开新题。**

---

## 1. 口径（必须先冻结，写进 MEMORY）

1. **Lite 清单来源**：以 zhulong 实际评测用的那份为准 —— 先 `find /nasdata/app.e0031982/code/EDA-Flow-Bench -maxdepth 3 -name 'cases_lite*'`，把 **绝对路径 + 行数 + md5 + 首次读取时间** 记进 MEMORY 顶部一行。🚫 不许自己另造一份 Lite 清单。
2. **Lite = 500**（论文宏 `\LiteSet=500`，冻结，见 `doc/AGENTS.md` §10）。**任何增删都必须"退一补一"**，总条数恒 500；换题记录进 `designflow/lite_manifest_diff.tsv`（`ts / shard / removed_id / added_id / reason`），并向 A（汇总人）+ zhulong 报备。
3. **只修自己的槽位**：只动 `cases/<本 shard>/` 下**且在 Lite 清单里**的条目 —— **"条目"包含该 case 的 `reference/<全名>/`（`check.py` / `negative/` / `negative_selftest.py` / `solve.py`）**，这些是修 L0–L4 的主战场，不是"别线文件"；**别 shard 的 case 与 reference 一律只读**（发现缺陷 → 在 `designflow/lite_health_<本shard>.tsv` 记 `cross_shard: <id> <问题>`，交回对应 shard）。
   - **id 归一化**：Lite 清单可能写短名（`<TaskId>-001`）或全名（`EDA-Eval-DesignFlow-<TaskId>-001`）⇒ 匹配前统一剥离 `EDA-Eval-DesignFlow-` 前缀，把归一化规则与"本 shard Lite 条数"一起写进 MEMORY 一行。
4. **共享仓提交纪律**（血泪条款）：🚫 `git add -A`；只 `git add -- <本 shard 明确路径>`；push 前 `git diff --stat origin/main...HEAD` 自查**不得含别线删除**（参考 2026-11-24 `df04b80945` 事故）。
5. **先盘点后修**：每 shard 第一轮先产出 `designflow/lite_health_<shard>.tsv` 全量 500 行的本 shard 部分（含 `status` 分类），再按 §3 的优先级动手。

---

## 2. 六项验收判据（L0–L5，逐条打勾）

| 编号 | 判据 | 怎么验 | 判定 |
|:--|:--|:--|:--|
| **L0** | evaluator 可见的 reference 目录存在，且是**全名** `reference/EDA-Eval-DesignFlow-<TaskId>-001/`（短名 refdir = orphan，不算） | `ls reference/EDA-Eval-DesignFlow-<TaskId>-001/check.py` | PASS/FAIL |
| **L1** | `check()` 返回值形状符合判分契约（`True`/`False` 或 `{'pass':bool}` / `{'ok':bool}`） | `python3 scripts/audit_check_returns.py --shard <X>` 该条 = OK | PASS/FAIL |
| **L2** | **参考解必 PASS**：用 `reference/` 的参考解打包提交，`check()` 判 PASS（k/k 断言） | `SKIP_RUN=1 eval/run_one.sh <task_id> --shard <X>`；或端到端 `zip reference → 提交 → check()` | PASS/FAIL |
| **L3** | **≥3 个负样本必 FAIL 且失败轮廓 distinct**（不同 neg 首次失败断言不同），§4.9 三假（空壳/只 print/删核心）全 FAIL | `python3 reference/<全名>/negative_selftest.py` | PASS/FAIL |
| **L4** | **评测机可跑**：在 36.15 eval 宿主真跑通；不依赖 GUI 二进制（`wv`/`Innovus`/`Virtuoso`/`Calibre` 等）；波形/图形类必须走 mock（先例：D r1275 的 `wv → tclsh + MOCK_SX_TCL`，14 条断言全保留）；`hidden_manifest.check_runs_wv=false`；单题耗时 < 超时阈 | 实跑 `eval/run_one.sh`（非 SKIP_RUN）+ 记录 wall_s | PASS/FAIL |
| **L5** | **防泄漏/防背题**：hidden-B 与 A 判别 token 零相交；SUT 沙箱不含 `reference/`、`.jsonl`、`test` 字段；按 `case_id` 反查源码 0 命中；assets 离线可复跑、无外网 | `grep -r <case_id>` 沙箱 + hidden token 差集 + 断网跑一次 | PASS/FAIL |

> **口径铁律**：L0/L1 是"能不能判"，L2/L4 是"判得对不对（假阴性）"，L3 是"判得有没有牙（假阳性）"，L5 是"能不能背题"。**六项全 PASS 才算这条 Lite case 修好。**

---

## 3. 修复顺序（严格按这个优先级，别按字母序）

| 级别 | 内容 | 理由 |
|:--|:--|:--|
| **P0** | **L2 或 L4 FAIL**（参考解跑不过 / 评测机缺工具 / 路径错 / 缺 ref / parse error / 超时） | 直接制造**假阴性**，把 Pass@1 打成 5.44% 这类失真值 |
| **P1** | **L3 FAIL**（neg 不 fail / 失败轮廓不 distinct / 无 neg） | 直接制造**假阳性**，题变送分 |
| **P2** | **L0/L1 FAIL**（缺全名 refdir / 契约形状违规） | 判分器直接判 FAIL，与能力无关 |
| **P3** | **L5 FAIL**（泄漏 / 硬编码 / 需外网） | 结论不可用于论文 |
| **P4** | 文档类（test_rationale / hidden_manifest / L_level 标注） | 不影响分数，最后补 |

**单轮预算**：40 min / 轮。**每轮目标 15–25 条**（P0 优先），修完立刻自验六项，不攒批。

---

## 4. 允许的修法 / 禁止的修法

✅ **允许**（都属于"修判分"，不改任务）：
1. `check()` 返回值形状（tuple/str/None/dict 非法键 → 契约形状）；
2. 评测机缺失的 GUI 工具 → **mock**（`tclsh`/`python` 桩，忠实还原被调 API 的语义），**断言条数与严格度一条不降**；
3. 路径/编码/时区/换行等**可移植性**修复；
4. 补 `negative/`（≥3，distinct）与 `negative_selftest.py`；
5. 补 `test_rationale` / `hidden_manifest` / `L_level` 标注；
6. 参考解本身的 bug 修复（**必须与 trace 用户意图一致**，且修复前后都能解释）。

🚫 **禁止**：
1. 降低断言条数 / 放宽阈值 / 把"看图"改成"读数值" / 删断言；
2. 改 prompt 语义、改 assets 难度、改用户原话；
3. **直接删 case** 凑绿 —— 坏到不可修只能 `status=retired_broken` + **补一条替换**（500 恒定）并报备；
4. 动 Full 集、动别 shard 的 case、动论文宏（`\LiteSet`/`\Neval`/`\MzeroPass`/`\ScriptPass`）；
5. 用 `--skip-done` / 复用旧 status 刷分。

**自检一问**（照 §7.4 原话）：**"一个不会看波形的 DE，能不能靠纯文本做对？"** 答案是"能" ⇒ 这条被你降级了，退回去。

---

## 5. 产出物（每个 shard 每轮必须留痕）

1. `designflow/lite_health_<shard>.tsv`（**增量追加**，TSV 表头固定）：
   `ts	case_id	shard	L0	L1	L2	L3	L4	L5	status	fix_note	wall_s`
   - `status ∈ {green, p0_fixed, p1_fixed, p2_fixed, p3_fixed, retired_broken, cross_shard}`
2. `designflow/lite_manifest_diff.tsv`（仅换题时写，见 §1-2）；
3. MEMORY 顶部 **一行**：`LITE_FIX: <shard>=<已全绿数>/<本shard Lite 条数> · P0 余 <n> · 本轮修 <m> 条 · 清单 md5=<...>`；
4. daily 里本轮修了哪些 id + 每条的六项结论（可简写 `id:L0-L5=111111`）。

---

## 6. 汇总与验收（A 召集人负责）

1. **A** 每轮把 4 个 `lite_health_<shard>.tsv` 合并成 `designflow/lite_health_all.tsv`，并在 `designflow/reports/lite500_health_<date>.md` 出**一张总表**（500 行：green / p0 / p1 / p2 / p3 / retired）。
2. **整体验收（缺一不可）**：
   - [ ] **500/500 六项全 PASS**（`green=500`，`retired_broken=0`）；
   - [ ] 清单 md5 与 zhulong 评测用清单**逐字节一致**；
   - [ ] zhulong 用这份 Lite 500 跑 **1 次 3-run**（doubao-pro，口径不变），**broken=0 / infra=0**，Pass@1 落在可解释区间（与 §7 历史锚点的差要能用 case 修复解释）；
   - [ ] `eval/run_batch.sh` 全量 500 无 `infra`、无 `check.py exception`、无 `timeout>阈值`；
   - [ ] 报告 + TSV 均已 commit（只 add 本线路径）。
3. 未达以上任一项 ⇒ **不许报"Lite 修完"**，按 §1 继续。

---

## 7. 与既有工作的关系（别重复劳动）

- **判分契约**：A r1122（584/584 OK, 0 VIOL）、B r1162（VIOL 5→0）+ r1164（PARSE_ERROR 0）、C r1064（608 OK, 0 VIOL）、D r1271（606/606 compliant）已基本清零 ⇒ **L1 主要是复核，不是重做**。
- **已知 P0 先例**：D r1274/r1275 `SineScanStdout-001`（eval 机无 `wv` ⇒ 参考解必 FAIL）已用 `tclsh+MOCK_SX_TCL` 修好；**其它 shard 请按同一模式自查"check.py 里出现 GUI 二进制名"**（`grep -nE '\b(wv|verdi|innovus|virtuoso|calibre|vcs)\b' reference/*/check.py`）。
- **池已近枯竭**（A/C 明确 exhausted、B/D 有 DEBT）⇒ 本令期间**暂停选料/扩池**，把 40min 预算全给 Lite 修复；池相关工作等 500/500 后再议。
- **zhulong 侧**：修复期间 zhulong 的 Lite 评测结果**只作趋势参考**，不作论文数字；全绿后再跑的那 3-run 才入账。

---

## 8. 汇报

- 每轮 MEMORY 顶部一行 + daily 明细（§5）。
- 每 10 轮（或 100 条）向 A 提一次进度；A 汇总后同步 zhulong（评测口径变更）与论文线（避免论文引用未修复前的分数）。
- 卡住（例如某条依赖外部 trace 恢复不了）⇒ 立即标 `retired_broken` + 提替换需求，**不许静默留着**。
