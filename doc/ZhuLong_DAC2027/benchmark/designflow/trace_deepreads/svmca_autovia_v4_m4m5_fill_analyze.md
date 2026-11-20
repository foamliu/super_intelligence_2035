# Deepread — svmca (1794723288564_svmca, jzeng @ hfhds201 = .75 本机)

- **session**: `/home/jzeng/.cline/data/sessions/1794723288564_svmca/1794723288564_svmca.messages.json` (3.56 MB, 627 msgs, agent=lead, 2026-11-15)
- **user / host**: jzeng @ hfhds201 (10.129.32.75 = .75 本机)
- **mc**: 575 (20261116 scan); keywords: drc:3307;.gds:2132;calibre:532;pex:220;pyaether:186;netlist:130;aether
- **shard / domain**: A / eda_other (pyAether AutoVia via-generation script optimization)
- **ledger**: fresh (not in any ledger prior to r675 claim)

## 用户真实意图 (U#0 verbatim, A-faithful seed)

> /home/jzeng/Desktop/IMCleAutoVia.py优化该脚本，使其在横向0.55um宽度的M4和纵向0.55um宽度的M5之间可以打出V4孔,V4长边沿着M5方向，可能需要在check DRC之前先沿纵向加宽M5，沿横向加宽M4

U#32 (follow-up, not used as seed): "测试之后还是无法在0.55um宽度的M4和0.55um宽度的M5交叠处生成V4，优化一下"

## assistant 回答要点 (msg#31 summary)

**Problem**: V4 via between horizontal M4 (0.55um) and vertical M5 (0.55um). Existing code handled `botEncChoice='DIR_3D_Y'` + `topEncChoice='NONE'` → force `orient='R90'` + M4 fill in X. But **missing M5 fill** for top enclosure.

**Changes** (added M5 fill logic in 2 locations):
1. `IMCleGetRectProp` (~L1307-1325 in original / L1374-1420 in post-fix): after M4 fill, added M5 fill extending in Y when orient=R90/R270, using `abs(topEncVia)` as enclosure.
2. `gen_via_from_y` (~L1841-1852 / L1918-1955): same M5 fill using `ybox` bbox, extends in Y when orient=R90.

**Mechanism**: M4 (horizontal) fill extends in X (along M4 length); M5 (vertical) fill extends in Y (along M5 length); V4 long side along M5 → orient forced R90.

## 关键代码事实 (verified from /home/jzeng/Desktop/IMCleAutoVia.py on .75, 2149 lines, post-fix mtime Nov 16 21:03)

### Section 1: IMCleGetRectProp_fill_section (L1374-1420)
- Condition: `re.search(r'V4', layer) and botEncChoice.upper()=='DIR_3D_Y' and topEncChoice.upper()=='NONE'`
- Forces `orient='R90'`
- M4 fill: `if botEncY != 0.0: enc=abs(botEncY); if orient in ('R90','R270'): fillBBox=emyBoxF(l_-enc,b_,r_+enc,t_)` → X extension
- M5 fill: `if topEncVia != 0.0: enc=abs(topEncVia); if orient in ('R90','R270'): fillBBox=emyBoxF(l_,b_-enc,r_,t_+enc)` → Y extension
- Both: `ae.dbCrtRect(cv, fillBBox, 'M4'/'M5', 'drawing')`

### Section 2: gen_via_from_y_fill_section (L1918-1955)
- Same condition with `viaName` instead of `layer`
- Forces `orient='R90'`, `direct='horizontal'`
- M4 fill: extends in X using `ybox` bbox, `abs(botEncY)`
- M5 fill: extends in Y using `ybox` bbox, `abs(topEncVia)`
- No orient-branch (single path, always R90)

## Case 设计 (r675 合成)

- **Case ID**: EDA-Eval-DesignFlow-AutoViaV4M4M5FillAnalyze-001
- **Domain**: eda_other
- **Form**: code-comprehension / analysis-Q&A (mock-behavioral, 纯 stdlib)
- **A-faithful**: verbatim U#0
- **Asset A**: `autovia_v4_fill_excerpt_A.py` (2 functions, V4 dir_3D_Y + NONE, M4/M5 fill, from .75 真实脚本重建)
- **Hidden B**: `autovia_v4_fill_excerpt_B.py` (V3 dir_3D_X + NONE, M3/M4 fill, R0 forced, 10 维全异: via/2 layers/orient/choice/param/2 fill-directions/wire-desc/direct-label/default-orient)
- **Candidate**: `autovia_v4_fill_analyze.py` (regex 解析 code → 14-key JSON, sort_keys 确定性)
- **check.py**: 16 条件 a-p (zip/exit/json/via_pattern/bot_enc_choice/top_enc_choice/forced_orient/bottom_fill_layer/top_fill_layer/bottom_fill_param/top_fill_param/2 fill_directions/function_count/fill_uses_abs_enclosure)
- **自验**: ref 12/12→16/16 PASS on B + 3 neg FAIL (d/e/p distinct) + NEG_RC=0 + jsonl test==disk round-trip
- **k_rationale == k_check == 16 ≥ 8 GATE PASS**

## 资产可达性

- 原始脚本 `/home/jzeng/Desktop/IMCleAutoVia.py` 在 .75 本机 (e0031982 可读, 117KB/2149 lines, post-fix mtime Nov 16 21:03)
- trace 文件 `/home/jzeng/.cline/data/sessions/1794723288564_svmca/...` 在 .75 本机 (3.56MB, 627 msgs)
- Asset A 从 .75 真实脚本 L1370-1425 + L1915-1965 重建 (post-fix version, 展示 M5 fill 逻辑)

## 泄漏隔离

- SUT 沙箱只含 asset A (autovia_v4_fill_excerpt_A.py + task_brief.md); hidden B + check.py + reference/ 不进沙箱
- check() 只跑 B (V3/M3-M4/R0), A (V4/M4-M5/R90) 不参与判分 → 反硬编码
