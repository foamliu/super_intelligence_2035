# r837 意图审计 — v1-v2 对照批 (11-15 用户令续做)

**轮次**: r837 (shard A, 0-case 意图审计轮)
**任务**: 2026-11-15 最高优先令「意图审计」续做，DEBT(a) 优先 v1-v2 对照
**审计范围**: A.jsonl 全部 40 个 `-v2` case + 其 v1 base（共 80 条 audit 行）
**审计前进度**: 40/415 ≈ 9.6% → **审计后: 120/415 ≈ 28.9% (+80)**

## 一、v1-v2 重做模式识别

40 对 v1/v2 全部呈现**一致的重做模式**（11-15 reaudit 落地的典型形态）：

| 版本 | 形态 | 判分对象 | 典型 k | 是否忠实用户意图 |
|:--|:--|:--|--:|:--|
| **v1** | produce-task | 候选 `*.py` 脚本 (py_compile + 真跑产 JSON) | 13–25 | ❌ 把用户「分析/解释/诊断」意图塞进旧 L2/L3 produce-task 模具 |
| **v2** | analysis-Q&A | 直接交付 `*_report.json` / `*_catalog.json` 结论 | 15–19 | ✅ 用 USER 原话，还原用户「只要分析结论不要脚本」真实意图 |

**判据**：v1 test 含 `py_compile` + `.py`（强制写脚本）；v2 test 无 py_compile，直接校验报告 JSON 字段。
样本核对（4 对）：CdlNetlistAnalyze / FuseUncalledAudit / SvClockblockAudit / PTVersionRecon — V1 全 produce-task，V2 全 analysis-Q&A，模式 100% 一致。

## 二、判定分布（本批 80 行）

| judgment | count | 含义 |
|:--|--:|:--|
| keep | 40 | 40 个 v2 — 忠实还原用户 analysis/Q&A/debug-Q&A 意图，11-15 reaudit 后此类任务合法 |
| downgraded | 34 | 34 个 v1（v1+v2 共存对）— 用户分析意图被旧配额降级为 produce-task，V2 已重做 → **处置=下线(retired)**，jsonl 行保留作口径变迁证据，不计通过率分母 |
| obs | 6 | 6 个 v1 base **不在 A.jsonl** — 见 §三 异常 |

**off_intent = 0, over_constrained = 0**：本批未发现为凑配额硬加步骤或判分超意图的题。v2 的 reframe 反向修正了 v1 的 over_constrained（强制脚本化），属正向修复。

## 三、异常：6 个 v1 base 不在 A.jsonl

| case_id (v1 base) | cases/A 有 v1 source? | reference/ 有 v1? | 推断 |
|:--|:--|:--|:--|
| PRStartMethodSelect-001 | ❌ 仅 -v2 | ✅ -001 + -v2 | v1 曾建(reference 在)→ jsonl 行被删 |
| PkgVarPassDutTb-001 | ❌ 仅 -v2 | ❌ 仅 -v2 | v1 从未建或全删 |
| RdcViolCatalog-001 | ❌ 仅 -v2 | ✅ -001 + -v2 | v1 曾建→ jsonl 行被删 |
| RedBistFlowRecon-001 | ❌ 仅 -v2 | ✅ -001 + -v2 | v1 曾建→ jsonl 行被删 |
| ToolRcFormatMapQa-001 | ✅ -001 + -v2 | ✅ -001 + -v2 | v1 source 在但 **jsonl 行被 rebuild 丢** ← phantom-revival bug |
| WtmWriteArrayScope-001 | ❌ 仅 -v2 | ✅ -001 + -v2 | v1 曾建→ jsonl 行被删 |

**关键发现**：5/6 v1 的 `reference/<id>-001/` 目录在磁盘上存在，说明 v1 **曾被完整构建**，但 A.jsonl 里没有 v1 行。
- ToolRcFormatMapQa-001 是明确的 **phantom-revival bug**（cases/A source 在，rebuild 时却被丢出 jsonl）——与 r828 ZtypeWave / r916(D) 同模式，印证 DEBT(c)「build_jsonl.py source-missing guard」需求。
- 其余 4 个（PRStartMethodSelect/RdcViolCatalog/RedBistFlowRecon/WtmWriteArrayScope）v1 source json 不在 cases/A 但 reference 在，可能是更早期被「删 jsonl 行 + 删 cases/A source」的退役操作（违反 11-15「不删 jsonl 行」纪律），或早期 rebuild 双丢。

**与 11-15 纪律的冲突**：11-15 令明确「🚫 不删旧 case、不删 jsonl 行——旧题是旧规则下产物的证据」。这 6 个 v1 的 jsonl 行缺失属**口径变迁前的旧操作结果**，本批仅记录观察，**不在本轮修复**（修复需逐条核 git history 判定是「bug 丢」还是「旧退役」，且 v1 是否值得恢复取决于 v2 是否已完整覆盖意图——多数 v2 已覆盖，v1 恢复价值低，倾向正式标 retired 而非恢复）。

→ 新增 DEBT(g): 6 个 v1-missing 案的 jsonl 行恢复/正式 retired 标注（需 git history 核查 + 拟统一在 jsonl 加 `retired` 状态字段）。

## 四、样本深核（确认 v2 忠实）

**PRStartMethodSelect-001-v2** (pnr_signoff, zhigangw@hfeg0pkn002, mc53):
- 用户原话逐字 `how to start pr job` → v2 prompt 用原话 + bundle_A.json 真实探查快照
- check 18 条校验 `pr_start_method_report.json` 的 verdict/blocked_paths/available_methods — 直接映射「怎么启动 PR」问题，无加难
- ✅ keep

**RdcViolCatalog-001-v2** (verification, e0045144@hfeg0pkn002, mc129):
- 用户原话 `帮我列出setup/corruption中的violation类型` → v2 prompt 逐字引用
- check 15 条校验 `violation_catalog.json` 的 SETUP/CORRUPTION Tag 集合 — 忠实「列出违例类型」意图
- ✅ keep

**SacapSignalMissingDiagnose-001-v2** (eda_other, rongtaoy, mc154):
- 用户原话 `你帮我看看...run_single.sh为什么没有识别...SapEnA/SanEnA` → debug-Q&A
- check 16 条校验 root_cause=regex_routing_before_signame — 忠实「为什么没识别」诊断意图
- ✅ keep

**SvTbBugFix-001-v2** (verification, xy1zhang, mc360):
- 用户原话 `阅读...位置的所有代码，帮我分析我的代码的错误，提出修改意见。根据你的修改意见，写出修改版本...新建一个文件夹，不要修改我的文件` → 混合 analysis+produce
- check 15 条校验 `cmds_readsig_fixed/` 新文件夹 + 具体 FIX — 忠实「分析+改+新建文件夹」意图
- ✅ keep（注：此 v2 实际是 analysis+fixed-code 混合，非纯 analysis-Q&A，但与用户意图完全一致）

## 五、结论

1. **40 个 v2 全部 keep** — 11-15 reaudit 的 reframe 落地正确，analysis/Q&A/debug-Q&A/doc-search 类任务按任务初衷合法保留，未发现 off_intent/over_constrained。
2. **34 个 v1 全部 downgraded → 下线** — 旧配额把用户分析意图强制脚本化，v2 已忠实重做。v1 jsonl 行保留作口径变迁证据，建议从通过率分母剔除（需统一 retired 标注机制）。
3. **6 个 v1-missing 异常** — 5 个 reference 在但 jsonl 行缺，1 个明确 phantom-revival bug。新增 DEBT(g)。
4. **本批未发现需重做的新题** — v1-v2 对照证明 reaudit 已正向落地，旧配额扭曲是「选题模具」问题非「已造题内容」问题（与 r836 第一批 40 题结论一致）。

## 六、下一步

- 审计进度 120/415 ≈ 28.9%。剩 295 条（历史存量非 v1-v2 对的题）。
- 下批优先：剩余 eda_other / pnr_signoff 域历史存量题（审计覆盖最薄的域）。
- DEBT(g) 新增：6 v1-missing 案的 jsonl 行恢复/retired 标注。
