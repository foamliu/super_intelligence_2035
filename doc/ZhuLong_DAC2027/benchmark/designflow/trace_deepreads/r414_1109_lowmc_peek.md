# r414 peek notes — 11/09 scan low-mc C-dominant fresh-against-all-4

**Round**: r414 (2026-11-12, shard C maintenance)
**Segment**: 11/09 scan (`ssh_eda_search_20261109_224902/summary.tsv`), mc ∈ [10, 40], C-keyword-dominant (C_sum ≥ 20 AND C_sum ≥ 50% of total kw AND wrong-shard kw ≤ C_sum), fresh-against-all-4-shard-ledger.
**Purpose**: r404-r413 7+ maintenance rounds saturated 11/05 (high+low mc) and 11/09 high-mc (r413 top 4). The 11/09 **low-mc** C-dominant fresh-against-all-4 segment was the one remaining unexplored quadrant. This peek closes the 2×2 matrix (scan × mc-segment).

## Method

1. Filter 11/09 scan (38082 rows) → mc ∈ [10,40] AND C-keyword-sum ≥ 20 AND C ≥ 50% of total kw AND wrong-shard (netlist/hspice/spice/verilog/...) ≤ C → **417 low-mc C-dominant candidates**.
2. Take top 80 by C-affinity (C_sum desc).
3. Exclude 4-shard ledger bare slugs (2621 distinct across A/B/C/D) → **55 fresh / 25 touched** in top 80.
4. Peek top 8 fresh candidates (distinct users, strongest C signals): 2y59d/lf1ny/ytr6l/diglq (batch 1) + q7wqo/5avgh/4v6rb/9qw70 (batch 2). Read real-user turns (non-tool-result) from `<user>/.cline/data/sessions/<slug>/<slug>.messages.json`.

## Peek results (8 candidates, ALL REJECT)

| # | slug | user | mc | kw (top) | real-user #0 (摘要) | REJECT reason |
|---|---|---|--:|---|---|---|
| 1 | 1789558343185_2y59d | ellawu | 40 | .gds:1113;drc:610;calibre:329;aether:113 | "请你看一下两个程序有什么问题" + USER#1/#2 = implant-fill SKILL scripts (IMCleFillImplantDRC, fill implant for aether, G5 process) | **near-dup** — ellawu 已有 9 case，其中 3+ implant-fill archetype（FillImplantFlowAudit-001 / ImplantFillDeckGen-001 / ImplantFillDummyLeftoverDiag-001 / ViaFillSvrfGen-001）；本 session 即审查 implant-fill SKILL，同 archetype |
| 2 | 1792828059985_lf1ny | jkxu | 27 | drc:1125;lvs:424;analog:262;verilog:26 | "review 下这个目录 /rundata/drcpa/.../BCenter_ok4_spf" + "lpe 是什么意思" | **Q&A / dir-review** — 非 produce-demand |
| 3 | 1791425862447_ytr6l | e0039120 | 30 | aether:1529;analog:106 | "把这个库 /apps/empyrean/aether/.../amsLibmn 移到我 aether 工作目录的对应库文件夹" | **env-setup / file-move** — env-dependent 操作，无 clean deliverable |
| 4 | 1792477362487_diglq | thomasz | 30 | drc:644 | "看下这个目录下的仿真，似乎卡住了 /rundata/totem/drcoa/ESD/DDR5TOP_20261013_backup_2/log" | **debug-investigation** — "查 sim 为何卡住"，Q&A 非 produce-demand |
| 5 | 1793861805853_q7wqo | t0002062 | 18 | lvs:353;drc:202;calibre:102;aether:61 | "为什么 Run rscalc 失败"(+rscalc.log) + "argusdrc 界面唤不起来怎么办" + 粘贴 DRC rule AT4_W_000_02 + "这是什么意思" | **troubleshooting / explanation Q&A** — 4 real-user turns 全是 debug/Q&A |
| 6 | 1793272345438_5avgh | gokuguo | 20 | .gds:396;virtuoso:225;.lef:19 | "做一个 lef 文件的 QA 脚本...先读取 /proj/lacaa/.../FSP51H204L6W35T6_BASe_SVT.lef，给我 summary" | **near-dup + asset unreachable** — 已有 LefFromPinList-001 / LefPostprocessFix-001（LEF QA archetype）；且资产路径 /proj/lacaa/ 私有，沙盒不可达（D 域资产可达性问题） |
| 7 | 1792031854472_4v6rb | wenjiez | 27 | aether:276;pdk:67;lvs:63;drc:58 | "仿真发现 vdly amp 在低温下电流变低，ntail 很低，这是为什么" | **circuit-analysis Q&A + wrong-shard** — spice_sim/analog_context 解释题，非 C physical_layout produce-demand |
| 8 | 1790667366131_9qw70 | cwei | 33 | aether:217;pdk:77;drc:54;lvs:46 | USER#0 = `# Spice_Agent — AI 驱动的模拟电路设计 Agent` skill spec（长 skill_instructions 注入） | **skill-load + wrong-shard** — USER#0 是 skill 注入非用户需求；spice_sim 域 |

## Conclusion

**11/09 low-mc C-dominant fresh-against-all-4 段饱和**：8 peek 全 REJECT（2 near-dup + 5 Q&A/debug/env-setup + 1 wrong-shard）。

**2×2 覆盖矩阵完成**（scan × mc-segment，全饱和）：

| scan | high-mc | low-mc |
|---|---|---|
| 11/05 | r404/r406/r407/r408/r409 (5 轮, 30+ peek) | r410 (3 peek) |
| 11/09 | r413 (4 peek) | **r414 (8 peek)** ← 本轮 |

r404-r414 = **9 连续维护轮**，peek 45+ fresh-against-all-4 候选全 REJECT，饱和结论第 9 次独立复验，覆盖全部 scan × mc 段。与 shard A r382 threshold_eval finding 一致：binding constraint = archetype + gate (clean produce-demand + L2/L3 + near-dup + asset-reachable)，NOT threshold。

**mc-matrix 凭据**（user 令 rule 4）：
```
python3 trace_ledger.py --shard C mc-matrix --src summary_1105.tsv
# mc>=10  池总量 1699  已动过 1432  未动过(可做) 267   ← mc10.fresh=267 ≠ 0（不写池耗尽）
```
池数量未枯竭（267 fresh），但 fresh 候选主题已被现有 308 case 覆盖（C 域 archetype 饱和：ellawu implant-fill 4 case / LEF QA 2+ case / DRC-log-teardown 4 case / DUMMY-config 11+ case）。

**shard A 尚未换池 11/05→11/09**（`summary_stats.json.mc_matrix.src` 仍 = `summary_1105.tsv`，11/12 r414 复核）。换池是潜在 unblocker（待 A 执行）。

## Action

0 case。未 claim 新 session（ledger_C 698 不变），jsonl_C 308 不变。不建 assets/reference 目录。等 shard A 换池 11/05→11/09 后再筛；或等新 archetype 授权。
