# Deepread — svmca → ViaFeasWidenPlan-001 (layout_aether, r705)

## trace
- session: `1794723288564_svmca.messages.json` (jzeng @ hfhds201 = 10.129.32.75)
- mc: 575 (drc:3307; .gds:2132; calibre:532; pex:220; pyaether:186; netlist:130; aether:109)
- 627 msgs / 11 user-text-turns / 2026-11-15
- size: 3.5MB messages.json
- real script: /home/jzeng/Desktop/IMCleAutoVia.py (117KB, pyAether + PyQt5, auto-via generation, author Leozhao)

## user intent (verbatim, trace-faithful)
- U#0: `/home/jzeng/Desktop/IMCleAutoVia.py优化该脚本，使其在横向0.55um宽度的M4和纵向0.55um宽度的M5之间可以打出V4孔,V4长边沿着M5方向，可能需要在check DRC之前先沿纵向加宽M5，沿横向加宽M4`
- U#132: `还是无法生成V4，建议首先在M4 M5交叠的地方先生成一块横向长0.82um，纵向长0.88um的M4和一块横向长0.63um，纵向长1.7um的M5，都以M4 M5交点为中心`
- U#234: `需要先生成M4 M5，然后再生成V4，目前还是没法在0.55um宽度的M4 M5交叠处生成V4，且导出的GDS里面没有M4 fill`
- U#488: `需要先在layout上原本的M4 M5交叠处生成M4 M5，然后才能fill V4，现在还是没有办法生成V4`
- U#608: `M4 fill和M5 fill都改成2x2`
- U#624: `即使已经加到这么大了，还是无法生成M4 M5以及V4`

## trace agent behavior (key fix at A#607)
- Core bug fix: search M4∩M5 overlap (was wrongly searching y6.drawing = DRC output layer)
- Generate widened M4/M5 rectangles at overlap centers so DRC sees enough metal for V4 cut
- Final: M4/M5 fill 2×2μm (half-width 1.0, half-height 1.0)

## reframe (mock-behavioral, 新子型 via-feasibility-and-widening-plan)
真实任务 = 修改 pyAether 脚本使 V4 在窄 M4/M5 间生成（path-dependent，需真 Aether）→ reframe 为纯 stdlib via-feasibility-and-widening-plan 分析器：
- 输入 scenario JSON (m4_rects / m5_rects / v4{w,l,orientation} / drc{enclosure})
- 每对 M4∩M5 交叠：算 overlap_rect + center + V4 placement + 8-side enclosure check (M4 xl/xr/yb/yt + M5 xl/xr/yb/yt) + feasible + drc_violations + widening_plan (最小加宽矩形)
- 输出 JSON sort_keys 确定性

## asset / hidden / check
- asset A (visible): 3 M4 (height 0.55/0.80/0.55) × 2 M5 (width 0.55), V4 0.10×0.50 vertical, m4_enc=0.05 → 3 overlaps (1 feasible / 2 infeasible, M4 y-enclosure fail, 2 widening rects)
- hidden B (反 A): 4 M4 (0.40/0.90/0.40/0.95) × 2 M5 (0.45), V4 0.08×0.60, m4_enc=0.04 → 4 overlaps (2 feasible / 2 infeasible)
- hidden B2 (边角全可行): 2 M4 (h 1.0) × 1 M5 (w 0.60), V4 0.12×0.40 → 1 overlap (feasible)
- A∩B∩B2 disjoint: total(3/4/1), feasible(1/2/1), v4 w(0.10/0.08/0.12), m4_enc(0.05/0.04/0.05)
- check 19 cond a-s; 4 negatives first_fail c/e/f/h (4 distinct); gold 19/19 PASS; §4.9 三假全 FAIL

## jsonl_C 435→436; ledger_C covered 438→439; layout_aether domain +1
