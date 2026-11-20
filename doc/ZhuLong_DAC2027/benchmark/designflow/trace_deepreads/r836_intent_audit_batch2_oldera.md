# r836 意图审计 batch 2 — 旧规则时代 generic-named cases（2026-11-20）

## 背景
2026-11-15 用户令（最高优先）：用新标准重审已造的题与候选池。intent_audit_A.tsv 此前 25/415（全 keep）。本轮续审 15 条旧规则时代 generic-named cases（最可能带旧配额痕迹）。

## 本批审计（15 条，全 keep）
Digital-010/021/022/023, CosimSetup-001, TotemSC-001, Verification-001, WaveSig-001, TimingECO-001, CoreTimingSig-001, InnovusAudit-001, PTSignoff-001, PwrGlobals-001, SynLintFlow-001, TLEFRules-001

### 关键观察
1. **旧规则未扭曲已造题的意图保真**：旧 L1≤30%/L2≥50%/L3≥20% 配额主要影响**选题门槛**（把 Q&A/analysis/env-config 判 weak 不造），而非扭曲**已造题**的内容。本批 15 条均能溯源到真实 trace 用户原话，case 交付物与用户意图一致。
2. **env-config/audit 类已正名**：CosimSetup-001（env setup）、InnovusAudit-001（只调查不实现）—— 旧规则下可能被判 weak，11-15 reaudit 后属合法真实意图，本批 keep。
3. **near-dup 发现（非 intent 问题）**：WaveSig-001 与 CoreTimingSig-001 同 trace（hengbow/mc407/DDR5 fullchip coretiming），同意图（找 WL/BL/coretiming 信号写 .sig），两 case check 路径不同（WaveSig 直接 fsdb，CoreTimingSig 用 manifest+hidden_B 真跑路径校验）。**flag 给 cross-case dedup**：覆盖率分子可能重复计，建议下轮 dedup 核查（retire 弱版或合并）。非 intent 违反，两 case 各自判分有牙。
4. **InnovusAudit-001 判分守「不实现」语义**：用户原话明确「本轮只调查现状和可行性，不进行任何正式实现」，case 严格守此边界，未因「L2 真跑工具」配额强转实现——这是旧规则下**正确抗配额**的范例。
5. **单轮裁剪 ≠ downgraded**：TLEFRules-001 锁定 trace 首条意图（汇总布线规则），trace 后续多轮宽线打孔调试未纳入——单轮裁剪合理，非 downgraded。

## A.jsonl v2 版本清点
A.jsonl 已含 **40 条 -v2 版本**（11-15 reaudit 重做产物，如 RedBistFlowRecon-001-v2/RdcViolCatalog-001-v2）。v2 = 11-15 令「重做不删旧」的落地。审计需覆盖 v1+v2；v2 的 intent 审计待后续 batch。

## 进度
- intent_audit_A.tsv: 25 → 40 行（40/415 ≈ 9.6%）
- pool_reaudit_A.tsv: 20 行（未动）
- 判定分布: keep=40 / off_intent=0 / over_constrained=0 / downgraded=0
- 下批：继续旧规则时代 cases（剩余 ~375），优先覆盖 v2 版本对（v1 vs v2 intent 对照）

## 纪律
- 审计结论逐条可溯源（case_id → metadata.trace_source.real_task_summary + prompt + test_rationale）
- 🚫 不删旧 case、不改 jsonl（审计只产出 TSV 判定）
- near-dup flag 走 cross-case dedup 流程，非本审计范围
