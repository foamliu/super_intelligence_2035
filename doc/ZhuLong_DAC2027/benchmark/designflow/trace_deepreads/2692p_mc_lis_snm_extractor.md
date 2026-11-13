# Deepread: 2692p — e0030760 6T SRAM 5000-MC HSPICE .lis 蝶形分析

**trace**: 1794459639804_2692p.messages.json (129 msgs, 1.0MB, dir-format, 10.129.2.13/hfeg0pkn004)
**user**: e0030760 | **mc**: 105 | **domain**: spice_sim | **shard**: B

## Session arc

1. **msg[42]** 用户原话: 分析 /proj/lacaa/sim/sram6t_mc5000/sram6t_mc5000.lis (5000 次 MC), 提取每样本 RSNM/HSNM, 画 butterfly 图, 标最大内接正方形
2. **msg[78]** 用户反馈: 提取样本数是 0, 明明有 5000 样本, 查 bug fix
3. Agent 定位 bootstrap 死锁: `mc_snm_analyzer.py` 的 `extract_snm_from_lis()` 中 `vin voltage` 列头仅在 `st["cur"] is not None` 时才 arm pending, 但实际 .lis 中每个列头出现时无表打开 → 0 样本
4. Fix: 无条件 `st["pend"] = True` (不依赖 cur is not None)
5. 双 marker 陷阱: 每 MC 样本两个 `*** monte carlo index = N ***` marker (DC 蝶形段 + transient/measure 段), `build_lis_index` 只提交后跟 q_rnm 表的 marker (pending 机制)
6. SNM = Seevinck 最大轴对齐内接正方形边长: `snm_butterfly` (binary-search + sliding-window min, O(n))
7. `snm_square` 返回 (x0, y0, side) 几何
8. `read_butterfly_at(path, offset)` seek+offset 随机读取单样本蝶形表

## Key code: mc_snm_analyzer.py (30985B, fixed version on .75)

### Bootstrap deadlock fix (extract_snm_from_lis)
```python
# BUG (old): vin voltage header only armed when cur is not None
if low.startswith("vin") and "voltage" in low:
    if st["cur"] is not None:  # ← NEVER true at header → 0 samples
        st["pend"] = True
    st["cur"] = None

# FIX: arm unconditionally
if low.startswith("vin") and "voltage" in low:
    st["pend"] = True       # ← unconditional arm
    st["cur"] = None
```

### Dual-marker index (build_lis_index)
```python
# Only commit marker when q_rnm table follows (pending mechanism)
if pending is not None:
    if s in NODES:
        if s == "q_rnm":
            idx[pending[0]] = pending[1]  # commit
        pending = None
    elif s.startswith("***") and "monte carlo" in s:
        # next marker supersedes uncommitted (transient) one
        ...
```

### SNM butterfly (snm_butterfly)
- Left curve: (vin, V(Q)) — falling sigmoid
- Right curve: (V(QB), vin) — axes-swapped, sorted by x
- `ad[k] = |y_l[k] - y_r[k]|` — vertical gap at each grid point
- `max_square(ad, grid)` — binary-search side s + sliding-window min deque, O(n) per probe

### snm_square geometry
- Returns (x0, y0, side) where side == SNM
- x0 = x_right - s, y0 = y_r[pinch] (right curve value at pinch point)
- Square: bottom on right curve, extends upward by side

## .lis format (per MC sample)
```
*** monte carlo  index = 1 ***
temperate = 25.00
vin          voltage
             q_rnm
 0.0000e+00  9.0000e-01
 ...
vin          voltage
             qb_rnm
 ...
vin          voltage
             q_hnm
 ...
vin          voltage
             qb_hnm
 ...
*** monte carlo  index = 1 ***       ← transient marker (NO butterfly tables)
.tran 1ns 100ns start=0
* transient + measure section
```

## A 档不可行
- /proj/lacaa 项目目录对 e0031982 权限受限
- 381MB .lis 无法拉取

## B 档合成
- _gen_lis.py: both-falling sigmoid VTC (V_out = VDD/2 * (1 + tanh((Vm - vin)/k)))
- Per-sample Gaussian perturbation of (Vm, k) emulates MC spread
- RSNM: shallower k (larger) → smaller eye; HSNM: steeper k (smaller) → larger eye
- Input A: 6 samples, 200pt, VDD=1.0V, seed=11
- Hidden B: 8 samples, 180pt, VDD=0.9V, seed=29, + stray marker
- A RSNM mean=0.4363, HSNM mean=0.4891; B RSNM mean=0.3928, HSNM mean=0.4368

## Case: EDA-Eval-DesignFlow-McLisSnmExtractor-001
- k=13 conditions (a-m)
- check.py: independent O(n²) brute-force SNM + independent dual-marker index builder + --sample containment (min/max, curves cross 3x) + A≠B + 3seed md5 + degenerate empty .lis
- Self-verify: ref 13/13 PASS + 3 degenerate FAIL + 3 negative FAIL
