# r404 selection round (shard D) — 0 case · DEBT:1 pool exhaustion re-confirmed with fresh scan

## 背景
#399-#403 五轮一致结论「shard D mc≥15 fresh 真实枯竭」。本轮 (#404) 用 **11-08 新鲜 ssh 扫描** 复核该结论，并穷尽 orphan / parked-deepread 路径。结论：枯竭确认，需运维介入。

## 路径 1 — 孤儿采纳（彻底穷尽）
扫描 EDA-Flow-Bench `reference/` (773 dirs) vs 全 shard jsonl (A/B/C/D + main) 双向归一化匹配（修 #403 bug：jsonl 同时含 `task_id`(无前缀)+`id`(有前缀)，旧扫只取 task_id 漏匹配）：
- 修正后**真孤儿 = 5**（非 22/11）：
  1. `DrcQaDiffReport-001` — DRC QA diff → **shard C** physical_verify
  2. `FeintFlowAudit-001` — FEINT digital-flow auditor (make -n/STA/SDC) → **shard A** digital
  3. `ThkOxIdvgVthCheck-001` — HSPICE 厚氧 NMOS Idvg/Vth 提取 → **shard B** characterization（deepread `1789693148853_0tfi2_thox_vth_extract.md` 明文「shard B 首个 Vth 提取器 case」+「追加 EDA-Eval-DesignFlow_B.jsonl」）
  4. `VrefCSMRRSeq-001` — Verilog DRAM training pattern VrefCS→MRR 序列分析 → **shard A** digital/verification
  5. `cell_rewrite_simlib_001` — cell rewrite simlib → **shard B** spice_sim
- **5/5 归属 A/B/C，0 个 D-domain**。🚫 不越 shard 采纳（TASK: 「只负责 analog_context/schematic_netlist/waveform」「🚫 不要碰别的 shard 的文件」）。

## 路径 2 — parked+deepread 未合成 case（穷尽）
扫 `designflow/trace_deepreads/` 全部 648 文件，提取提议的 `EDA-Eval-DesignFlow-*-001` case_id，交叉 ledger_D + 全 jsonl：
- ledger_D 内 deepread 提议且**未落任何 jsonl** 的仅 **1 条**：`1793078405436_t0aom` → `FsdbNetToggleDiag-001`
- 该 deepread 明文「**claimed: 2026-11-05 shard B** (deepread, DEBT:1)」「domain=spice_sim」「追加 EDA-Eval-DesignFlow_B.jsonl → 清 DEBT:1」→ **shard B 的待合成 DEBT，非 D**（spice_sim + 需 .75 WaveView ACE/FineSim probe，L2 重构建，非快采纳）。
- 复核另 3 个 ledger_D parked+空 note+D-domain 候选（f1fik/vdqlw/uml8e/rn6pm）：deepread 显示 ledger domain 字段**不可靠**——f1fik=physical_verify(shard C)、vdqlw=已落 shard B TrimMarginSpec-001、uml8e=已落 shard C ERCBootPlan-001、rn6pm=layout_virtuoso(shard C)。**全部 wrong-domain 或已交付**。

## 路径 3 — 11-08 新鲜 ssh 扫描（复核枯竭）
eda_flow open_session(hfhds201) → `dump_sessions_D404.py` 并发 ssh 12 台 reachable host（hfeg0pkn001/002/003/005、plg07/085/098、pbn001/002、hfhds210/211/212）→ 收 **3215 sessions**（含 NFS 跨机重复）→ 筛 mtime≥Nov5 得 **295 recent** → `peek_recent_D404.py` 并发 peek top14 首用户轮 + 关键词分类：
- 14 条首用户轮分类：11 `?`(skill-meta / workflow-controller / nginx / scenario 机制 / 空) · 2 `nonD`(SVRF PC size=calibre/C) · **1 `D?`** = `1792837504776_sx4h2`(hfeg0pkn002, 「载 dram-delay-chain skill，分析 R_RasBnkLogic 中 SapEn2 的延迟链，需要仿真 FSDB」)
- sx4h2 **已在 ledger_D parked**(11-05, note「analysis+FSDB sim L2 hard to verify offline」) · 且近似已有 shard B `TrimMarginSpec-001`(vdqlw 延迟链 B-档 L1) → 重复 + 已 parked，不取。
- **结论**：Nov5+ 新鲜会话以 skill-meta / 非 D / 已 parked 为主，**0 fresh D-domain synthesizable seed**。与 #399/#400 一致。

## 三路径汇总
| 路径 | 结果 |
|---|---|
| 孤儿(5 真孤儿) | 0 D-domain（全 A/B/C） |
| parked+deepread 未建(1) | t0aom = shard B DEBT |
| 11-08 fresh ssh 扫描(295 recent, top14 peek) | 0 fresh D seed（sx4h2 已 parked+dup） |

## 阻塞 & 升级请求（需运维裁决）
shard D mc≥15 fresh 真实 + 孤儿 + parked-deepread **三路径全枯竭**，本轮 #399 起第 **6** 轮一致结论。agent 已无法在会话内自行破局，请求运维（按优先级）：
1. **触发 .75 全量 rescan**：当前 summary.tsv 为 2026-10-28 扫描，已 11 天陈旧；scan infra 非会话内可做（MEMORY #399 确认）。新 scan 或可暴露 mc≥15 新 D-domain 会话。
2. **shard 孤儿再分配裁决**：5 真孤儿中 `ThkOxIdvgVthCheck-001`(HSPICE Vth 提取, deepread 在共享 deepreads 目录) 若运维判定归 D（analog device char 边界），D 可采纳（需补 reference_submit.zip，自验后落 D.jsonl）。
3. **降阈扩池**：接受 mc≥10 D-domain 候选（#399 已试 mc15-29 得 208 fresh 但全 non-seed/wrong-shard；mc<15 信号更弱，需运维认可）。
4. **跨 shard 重复清理**：deepread 发现 `cpv3d`(ConnFileNetChk-001) 同时在 shard A 和 D 的 jsonl（2 行同 trace 同 case_id），建议 merge 脚本去重。

## 交付
- 🚫 0 case 落 jsonl（无新 D-domain seed 可合成，🚫 不越 shard / 🚫 不造低质 / 🚫 不判分歧义）
- ✅ 选料复核记录（本文件）
- ✅ MEMORY_D 更新（WAITING:1 DEBT:1 + 心跳）
- ✅ ledger_D 无新增（无 claim/mark）
- 无新 PII / 无改 jsonl / 无动 EDA-Flow-Bench 仓
- eda_flow session 已 close_session(keep=false) 释放
