# s6n9d — RHR xyz budget-derived enumerator (xuluo, 2026-11-12 r428 deepread)

**session**: `1793605575195_s6n9d` (xuluo @ 10.129.2.10, mc54)
**domain**: digital (DDR Row-Hammer-Refresh regression; Python PyRHR ↔ SV RTL alignment)
**ledger**: claimed r428 (digital), 4-shard truly-fresh (P-004 cross-checked: not in A/B/C/D ledger)
**msgs**: 159 / user_turns 82 / 18 real user asks / agent tool_use: run_approved_command×29, editor×27, read_files×2

## User intent (real asks)

U#0 (mode="act"): pastes a full 对话总结 (Python PyRHR vs Verilog RTL RHR regression 参数/行为对齐) and asks "看下这段对话". Then 17 follow-up Q&A:
- U#19 "dlut_top.v wrapper 未实现 under2 的 skip 门控...是什么意思"
- U#20 "gen_paralist_sv_aligned.py 在哪"
- U#22/U#23: pastes a gen_paralist csv-generator script (template read → copy → override xyz → tab CSV)
- U#32 "所有参数都对齐了吧"
- U#34/U#39: "SV 中并不是 4408 全部统计" / "没进入仿真的对应 paralist 中大于 4336 的部分吗"
- U#44 "python 跑出来结果比 sv 差很多, 特别是 xyz=1/1/255 下 rhr 比 norhr 还差, 为什么"
- U#45/U#52/U#53: "a=0.25 这个是对+2/-2 的影响因子, 在 SV 中是多少" (Row-Hammer ±2 neighbor attack weight)
- U#54: pastes own analysis of `a` (attack weight) with code evidence
- U#65 "你先提供一个表格, 对比 SV 和原来 python 的 xyz 取值逻辑"  ← produce-task
- U#70/U#77/U#78/U#81: "act_max 怎么得来的" / "为什么要多减去一个 tRC" / "实际运行用的哪一个" / "解释为什么 act_max 是这样定义的"

→ Mostly Q&A/analysis, but U#22/U#23 + the agent's rewrite of `gen_paralist_sv_aligned.py` (msg#43/#49 editor) is a **clean produce-task** (user asked to rewrite the script in the pasted style, keep SV-aligned logic). **A档** (deliverable = agent's actual output, parameterized).

## Core spec (extracted from agent msg#34/#40/#51/#59 + the actual file /home/xuluo/gen_paralist_sv_aligned.py)

```
def act_max(burty, trefi, trfc, trc):
    return (burty*(trefi - trfc) - trc)//trc + 1

def enumerate_xyz(trefi, trfc, trc, burty_values):
    for burty in burty_values:
        am = act_max(burty, trefi, trfc, trc)
        y1_emitted = False
        for xnum in range(1, am+1):
            y_max = am // xnum + 1          # KEY bound (not am)
            for ynum in range(1, y_max+1, 2):  # y odd only, step 2
                znum = am // xnum // ynum + 2  # back-derived
                if xnum*ynum*znum < am: continue      # window-full filter
                if ynum == 1 and y1_emitted: continue # y==1 dedup (only x=1)
                yield burty, xnum, ynum, znum
                if ynum == 1: y1_emitted = True
```

CSV: tab-separated, header = config keys in insertion order, each row = template.copy() with xyz_normal_xnum/ynum/znum + burty_num overridden; list values space-joined.

## Reference behavior (config_A: tREFI=15600, tRFC=380, tRC=60, burty=[1,2,3])

- act_max = 253 / 507 / 761
- **4408 combos** (burty dist 636 / 1446 / 2326) — reproduced exactly by reference
- product x*y*z range 255..2283
- 1/1/1 structurally absent (z = am+2 > 1 for x=y=1)
- key points: (1,1,1,255) (1,1,169,3) (2,1,1,509) (3,29,5,7) (3,29,7,5) (2,3,85,3)
- old unconstrained 3D cartesian = 3900 combos, 35-64% under-budget, includes 1/1/1 (msg#129)

## Hidden B (config_B: tREFI=20000, tRFC=500, tRC=64, burty=[1,2,3])

- act_max = 304 / 609 / 914
- **5455 combos** (burty dist 791 / 1790 / 2874)
- different template keys (extra_param_alpha/beta, amplitude_e, noise_c, random_active_d, longer lfsr_seq) → defeats hardcoded_A

## Synthesis: XyzBudgetEnum-001 (digital L2 spec-driven code generator, A档, k=16)

- **deliverable**: `gen_paralist_sv_aligned.py` (pure stdlib, argv-parameterized)
- **A**: config_A.json + spec.md
- **B (hidden)**: config_B.json + hidden_manifest.json
- **check.py**: 16 conditions (a-p) + independent oracle (set-comprehension + post-drop dedup, vs reference's generator-with-flag)
- **negatives**: naive_empty / print_only / core_removed (drops window-full filter + y==1 dedup) / hardcoded_A
- **TFC**: 9/9 = 100% (act_max formula / y odd step-2 / y_max bound / z back-derive / window-full filter / y==1 dedup / 4408+burty dist / 1/1/1 impossible / CSV template-copy format — all directly traceable to agent msg#34/#59 + actual script)

## Self-verify

- ref PASS 16/16; 4 negatives FAIL; §4.9(a)(b)(c) FAIL; core_removed surgical (fails i/l/m/o); hardcoded_A fails e/n + cross-input guard (o); k_rationale = k_check = 16 ≥ 8 ✓
