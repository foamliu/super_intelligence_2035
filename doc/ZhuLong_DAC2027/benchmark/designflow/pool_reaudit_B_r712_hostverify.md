# pool_reaudit_B r712 host-verify (2026-11-17)

## 背景
r618 意图审计判 182 条「可造」。r619-r711 已变现 87 条。剩 95 条「未入 jsonl 且 ledger 非 case」。
r712 对剩余 9 条「有真实 user/host/mc>0」候选逐条 host-verify，结论：**0 条为干净 B 域可造**。

## mc-matrix 证据（mc>=10 fresh=0，四快照结构性饱和）
```
# 扫描快照: designflow/summary_1115_081559.tsv
# 数据行 = 4543 → 去重 session = 1103（shard B keywords 过滤后）
# 台账已动过 session = 3642（case/seeded=1017, parked=2508）
mc>=10  943  943  0   ← fresh=0
```

## 9 条 host-verify 结果

| session | user@host | mc | 旧判 | r712 新判 | 证据 |
|---|---|--:|---|---|---|
| 1793949156546_i6kg9 | t0002607@hfeg0pkn005 | 28 | 可造 | 不可造 | ssh 10.129.2.14：sessions 列表无 i6kg9（仅 2sjlh/so62z/jxx24）→ stale pool entry, no-trace |
| 1793870006104_003q6 | shaoyou@hfeg0pkn003 | 4 | 可造 | 不可造 | trace 存在（32KB/8msgs）但用户原话「分析我的 ~/.bashrc文件」= env-config，非 spice_sim/characterization → wrong-domain |
| 1788845510771_5xxsm | sophiaw@hfeg0plg09 | 15 | 可造 | 不可造 | trace 存在但 pool_reaudit domain 标 non_spice → 非 B 域 wrong-domain |
| 1794202571966_v87lq | e0030760@hfhds201 | 941 | 可造 | 不可造 | r658 已改判 no-trace 不可造（MEMORY 已记），r712 confirm |
| 1794293298759_nk0hg | e0042624@hfeg0pkn001 | 5 | 可造 | 不可造 | trace 存在（312KB/76msgs）但用户任务=「Spice-Agent」软件项目的 Codex/LLM provider 连接检测（go to project / how to start / detect LLM provider），非 spice 仿真/characterization → wrong-domain (software-infra) |
| 1794309772651_z3xy1 | mwxi@hfhds228 | 5 | 可造 | 不可造 | ssh 10.129.32.112：sessions 无 z3xy1 → stale, no-trace |
| 1792547194816_gsmj2 | adaml@hfeg0pkn002 | 58 | 可造 | 不可造 | ssh 10.129.2.11：host 仅有 1791980431476_gsmj2（已入 jsonl TspcNetlistAnalyze-001），pool entry 1792547194816 不存在 → stale-dup |
| 1793864695856_gxlr2 | shunlinp@hfeg0pkn002 | 71 | 可造 | 不可造 | ssh 10.129.2.11：host 仅有 1793587429686_gxlr2（已入 jsonl），pool entry 1793864695856 不存在 → stale-dup（r658 已记） |
| 1792204849864_ly0mw | e0039516@hfeg0plg76 | 19 | 可造 | 不可造 | trace 存在（531KB/19msgs）但用户原话「DDJOB Auto 315B」+ search CXMTleFillM0UForddjob（fill metal 任务）→ 属 physical/layout 域（shard C），非 spice_sim/characterization → wrong-domain |

## 结论
- 9 条 real-trace 候选：4 stale/no-trace（host 上 session 不存在）+ 5 wrong-domain（trace 存在但非 B 域）
- 剩余 ~84 条「无 user/host/mc」候选 = scout 条目（无 host 信息不可 ssh 验证，非真实可造 trace）
- **B 域 revival pool real-trace 候选已耗尽**：r619-r711 变现 87 条，r712 host-verify 后剩 0 干净 B 域可造
- pool_reaudit_B.tsv 可造数 182 → 174（r712 剔除 8 条；v87lq 已是 不可造 未计入）

## 复活池进度更新
- r619-r711 变现 #1-#87
- r712：0-case（host-verify 后无干净 B 域候选）
- 可造剩余 174 条中：~84 scout 条目（无 host 不可造）+ ~90 ledger-parked 但已入 jsonl 或 stale-dup 或 wrong-domain
- 结论：B 域 revival pool **实质性耗尽**（与 mc>=10 fresh=0 四快照结构性饱和一致）
