# r241 deepread — t4gfl (joyc) — SAQP DRC `INT (ANGLE) ==` enforcement

- **trace**: `1793607379592_t4gfl` · joyc @ hfeg0pkn005 (10.129.2.15) · mc=270 · kw=37 calibre (pure physical_verify)
- **NEW user** · 259 msgs · agent=lead · continuation session (U#0 = auto Context summary)
- **real file**: `/home/joyc/zl/SMxa_saqp_gen.drc` (715 lines, 36 SAQP rules, M3=SMxa)

## 用户真实意图
"根据 `Mxa_CS_1_3`/`Mxa_CS_1_9` 参考格式，修正 `SMxa_saqp_gen.drc` 中所有含 edge length 规则的代码。"
关键修正点（trace Highlights + msg258 总结）：
1. 格式统一：MINP→`M3_H_Edge`/`ANGLE==0`；NMINP→`M3_V_Edge`/`ANGLE==90`
2. 通道命名：`M3CA`/`M3CB`（实际层），CHK 变量 `M3A_WH`/`M3B_WH`（MINP）/`M3A_WV`/`M3B_WV`（NMINP）
3. PRL>0 用 `PROJ > X`；PRL<0 用 `EXTENDED X`
4. **`INT (ANGLE ...) ==` 强制**：CS_18/CS_19 原始 `INT (ANGLE M3CA == 0) >= 0.100 < 0.140` 非法（`INT(ANGLE)` 只允许 `==`），需拆为 `==0.100` + `==0.120`，`OR` 聚合

## assistant 工具链（120 tool calls）
- 60× `editor`（增量改 deck）· 30× `read_files`· 10× `search_codebase`· 8× `run_approved_command`（跑 gen_main.py / fix_saqp_gen.py / grep）· 2× `ask_question`
- msg6-msg206: 逐条修正 edge-length 规则（CS_3_3/3_5/3_9/3_11/3_13/CS_7/CS_15-19）
- msg234-msg258: 扫全文件确认 `INT (ANGLE ...)` 只用 `==`（msg258 总结：CS_18 拆 `==0.100`+`==0.120`，CS_19 拆 `==0.140`+`==0.156`+`==0.180`+`==0.260`）

## 真实金标（CS_18/CS_19 已修正，lines 599-660）
```
Mxa_CS_18 {
  @...
    M3_100_CA = INT (ANGLE M3CA == 0) == 0.100 ABUT<90 OPPOSITE REGION
    M3_120_CA = INT (ANGLE M3CA == 0) == 0.120 ABUT<90 OPPOSITE REGION
    M3_100_120_CA = OR M3_100_CA M3_120_CA
    M3_20_CA = INT (ANGLE M3CA == 0) == 0.020 ABUT<90 OPPOSITE REGION
    M3_22_CA = INT (ANGLE M3CA == 0) == 0.022 ABUT<90 OPPOSITE REGION
    M3_24_CA = INT (ANGLE M3CA == 0) == 0.024 ABUT<90 OPPOSITE REGION
    M3_20_24_CA = OR M3_20_CA M3_22_CA M3_24_CA
    ... (CB 对称 + DFM SPACE/PROPERTY/COPY)
}
Mxa_CS_19 {
  @...
    M3_140_CA = INT (ANGLE M3CA == 0) == 0.140 ABUT<90 OPPOSITE REGION
    M3_156_CA = ... == 0.156 ...
    M3_180_CA = ... == 0.180 ...
    M3_260_CA = ... == 0.260 ...
    M3_GE140_CA = OR M3_140_CA M3_156_CA M3_180_CA M3_260_CA
    ... (CB + DFM)
}
```
**离散宽度值集**（从全 deck 抽取）：`[0.020, 0.022, 0.024, 0.100, 0.120, 0.140, 0.156, 0.180, 0.260]`
**变换规则**：
- `INT (ANGLE V == D) >= w1 < w2` → 值集中 `w1 <= w < w2` 的每个 w：`M3_<w*1000>_SUF = INT (ANGLE V == D) == w ABUT<90 OPPOSITE REGION`，末行 `<LHS> = OR <members>`
- `INT (ANGLE V == D) >= w1`（无上界）→ 值集中 `w >= w1`
- `INT (ANGLE V == D) <= w2` → 值集中 `w <= w2`
- `INT (ANGLE V == D) == w`（已合法）→ 原样保留

## DISTINCT from 现有 physical_verify 系
- r240 WlAdjacentPairParse（.rep PAIR 邻接表）/ r239 DrcRuleTimeRank（log per-rule time）/ r237 DrcLogTeardownReport（log 四模块拆解）/ r208 DrcUnusedVarClassify / r218b DrcQaWidthTypeGeom
- 本案**首次 ground on Calibre SVRC deck `INT(ANGLE)==` 语法强制重写**（range→离散 `==`+`OR`），互补不重叠

## 选料结论
- **采纳**：B-synthesized（continuation session，Context summary 非有机 user 轮 → A 档禁用）
- **case**: `EDA-Eval-DesignFlow-SaqpIntAngleEqSplit-001`（physical_verify, L1, k=16 a-p）
- **聚焦** `INT(ANGLE)==` 强制子变换（最可编程、最可验），edge-length COIN EDGE 重格式化留后续 case
