# deepread: js4n1 — e0024852@hfeg0pkn005 — M1-via DRC co-optimization

- **session**: 1795075084116_js4n1.messages.json (e0024852@hfeg0pkn005/10.129.2.14, mc=214, lvs:1686/calibre:928/virtuoso:311/aether:122/.gds:48/pex:189 dominant → physical_verify)
- **msgs**: 304 (157 user / 147 assistant), 1.30 MB
- **user**: e0024852 (DRAM/SRAM bitcell DTCO engineer), platform CH252_FS_guojing SRAM bitcell
- **real task** (U#1/U#2/U#11/U#18 概括): design-rule + layout 联合优化。已有 `via_optim_gds_fixed.py` + `optimize_m1` 两脚本读 bitcell GDS (`CH252_HD_Bitcell_FS_pin.gds`)，对窄 M1 线 (L88 drawing, width≈18nm) 按候选宽度扫描 (M1_WIDTH_CANDS_NM) 加宽，对过孔同步处理，校验 DRC (width/space/pitch/via-enclosure)，违规的线保持原宽 (partial widen "widen 6/10 keep 4")，每个候选产出一个 variant GDS。Bug 报告：① "要么只写出来修改的过孔 要么版图没有变化" (只写 via 或 metal 丢失) ② DRC 阈值要按工艺实情调 (U#11 "我知道工艺不行 我要改我的 design rule") ③ 候选密度可配 (U#18 "把 M1_WIDTH_CANDS_NM 改成更密的扫描 22–40nm 步进 1nm = 19 个")。
- **assistant 工具链**: pyAether (dbGdsIn/dbGdsOut/dbGetLayerPurposeCount/emyFigGroupGetAllPinNets) + shell 跑 batch_pex.py (GloryEX PEX DSPF extraction, 17 GDS variants) + 多轮调试 (AttributeError: pyAether.optimize_m1 / NM_PER_DBU / M1_WIDTH_MIN_NM → 常量需自定义非 pyAether 内置)。输出 `[OK ] M1_w036 (width=36.0 nm, 6 lines widened) -> ...gds` / `[SKIP] M1_w046: M1 line at (cx=725,cy=2305) violates pitch/width/space/via rules` / `[strip] M1_w038: widen 6/10 lines; keep 4 at original width` + per-line `keep (cx=...,cy=...) space left=1.5nm <= min 6.0nm (wnew=38.0nm w_orig=18.0nm)`。
- **DRC 规则 (从 trace 提取)**: M1 on L88; NARROW_WIDTH_MAX=200nm (排除宽金属); M1_WIDTH_MIN≈16nm; M1_SPACE_MIN≈6nm; PITCH range (24, 168)nm; VIA_ENCLOSURE_MIN≈4nm; db_unit=0.1nm; 候选宽度 36/38/42/...nm。
- **关键决策点**: 每条窄 M1 线独立判定能否加宽到 w_new (邻居按原宽 w_orig=18 保守估算) → space = center_dist - (w_new+w_orig)/2 ≥ SPACE_MIN; via enclosure = w_new/2 - via_w/2 ≥ ENCLOSURE_MIN; pitch = center_dist to nearest M1 同向邻居 ∈ [PITCH_MIN, PITCH_MAX]; 任一违规 → KEEP 原宽 + reason; 全过 → WIDEN。partial widen: 一个 variant 内部分 WIDEN 部分 KEEP。
- **合成方向 (档 B reframe fixture-driven)**: agent 写 `m1_via_drc_co_optim.py` (纯标准库) 读简化 bitcell manifest JSON (m1_lines/vias/neighbor_metals/rules) → 按候选宽度列表逐线判定 WIDEN/KEEP (space/pitch/via-enclosure/width-min 4 类 DRC) → 产出 JSON 报告 (per-variant: width/lines_widened/lines_kept/verdicts[]; summary)。visible env_A + hidden env_B (不同 geometry/rules)。

## 子型
`m1_via_drc_co_optim` (M1-via width-scan DRC co-optimization, partial-widen variant generator) — physical_verify，首例。
