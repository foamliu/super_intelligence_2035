# trace_deepread: shard C r477 — mc≥10 fresh-candidate investigation (2026-11-13)

**目的**: 11-11 用户令 rule 4 要求：mc10.fresh≠0 时禁写「池耗尽」。C 线已 68 连续 0-case 轮（r409-r476），声称「peek 全 REJECT / 池饱和」。本轮**首次在 mc≥10 口径下做可靠去重 + tools 列过滤的真实 fresh 候选核查**，验证该结论。

## 方法（可靠去重，非目测）

1. 本地 `summary_1109.tsv`（3964 行，含 tools 列 $7）+ 本地 4 shard 台账（trace_ledger_{A,B,C,D}.tsv，共 ~2400 touched session）。
2. `trace_ledger.py --shard C mc-matrix --src summary_1109.tsv`：mc≥10 池 2517，已动过 2057，**未动过 460**（≠0，按 rule 4 不写池耗尽）。
3. Python 脚本 `/tmp/find_fresh_c.py`：跨 4 shard 台账去重 → fresh = 不在任一 shard 台账；按 tools 列($7) 过滤「真 shard-C 工具占主导」(calibre/virtuoso/pyAether/cellview/db* vs netlist/hspice/verilog/schematic)。
4. 结果：**~70 条 fresh + 真 shard-C 工具候选**（mc 70-280，非 top-mc 段——top-mc 段确实几乎全 ledgered/parked）。

## 6 条 fresh 候选实地 peek（全部 REJECT，附具体理由）

经 .75 ssh 读 `<slug>/<slug>.messages.json` 首轮 user 文本：

| session | user | mc | tools | 首轮意图 | REJECT 理由 |
|---|---|---|---|---|---|
| 1790148708525_q8hpz | xinqiaoz | 218 | cal=376 | "用 handoff 技能从交接文档恢复上下文继续之前工作" | **handoff-restore 续接轮**，非单轮可闭环任务；xinqiaoz 已过度代表（PDKQA 系列） |
| 1783653766179_w3bwg | e0014566 | 139 | virt=147 | "read prompt_autovia.md and do the job" (AutoVia via 生成) | **near-dup 风险**：与既有 PaCfgMigrate-001（pg_layout, e0014566, oblxr, autovia 相关）同用户同主题；e0014566 已过度代表 |
| 1793954724282_taaak | e0039102 | 179 | pyA=379 | "你能在这个路径下启动Aether吗？" | **探索性发问**，无明确交付物；morph 为 aether-tool-qa Q&A |
| 1792569513787_jq6lq | mwxi | 85 | cal=120 virt=26 | "查看 hfds101 crontab，syncdfmcalib 有正常执行吗，为什么没文件同步" | **运维/crontab 调试**，非 pv/layout（keywords calibre 是 syncdfmcalib 误命中） |
| 1791460448234_dzbpb | weizhao | 124 | cal=124 | — | **session 文件不存在**（已被清理） |
| 1790233170014_92cla | lizwen | 167 | cal=97 pyA=7 cv=10 | "DRC Testpattern Generator" 技能定义 → USER#2「执行被策略拦截」 | **DRC 生成被 policy 拦截未跑**，session morph 为 skill/policy-config 调试；无 accepted gold product |

## 关键结论（修正 68 轮口径）

1. **mc≥10 fresh 池 ≠ 枯竭**：mc10.fresh=460，且其中 ~70 条有真 shard-C 工具使用。r333/r380 等「mc≥30 池耗尽」结论在 mc≥10 口径下**不成立**（与 11-11 用户令 rule 4 一致——本轮不写池耗尽）。
2. **但 hit-rate 低**：6 peek 全 REJECT。fresh 候选多为 (a) handoff-restore 续接 (b) policy/harness 调试 (c) 运维误命中 (d) near-dup 既有 case (e) 探索性无交付。**真·干净单轮可闭环 shard-C 工作**大多已在 mc≥30 段被做成 case。
3. **top-mc 段确已饱和**：mc>300 的 fresh 候选 0 条（全 ledgered）；fresh 集中在 mc 70-280，质量密度低于已用段。
4. **未 peek 的 ~64 条**仍有潜力，下轮应继续 peek（优先非 xinqiaoz/e0014566 用户、非 handoff/policy 轮）。

## 下轮计划

- r478: 继续 peek fresh 候选（n1b1u/gokuguo, 8rlou/lizwen, jz2at/joelchen, 6u6yk/e0014566 等 ~64 条）；若命中干净可闭环 → claim + 合成 case；若再 6+ REJECT 则 fresh 池 hit-rate 实证 ≤15%，可考虑回退 omission 维护。
- 同时补做 omission #92 diversify→layout_virtuoso（本轮因时间未做，最高 k no-omit lv = DRCPatPlan-001 k=17）。

## 不入台账的 REJECT session（供下轮避坑）

q8hpz/w3bwg/taaak/jq6lq/dzbpb/92cla —— 不 claim（未做 case，避免污染覆盖率分母）；下轮 peek 新批次时跳过这些。
