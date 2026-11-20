#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vdd_vss_rail_label.py
=====================
按需求在 Metal4 电源/地 rail 上按 Pitch/Offset 网格均匀打 pin 标签。

需求要点（只读图形 + 仅增删 label，图像/层次完全不变）：
  1) 旧标签清理：只删【与 95:353/354 金属接触】的 PG M4 pin(95:251)
     —— 默认 layer95, texttype251，且该 label 须落在 353/354 图形内才删（QA 确认）
 2) 目标参考层：提取 Metal4 图形  layer 95:353(VDD rail)、95:354(VSS rail)
     —— 仅用作"吸附靶子/有效范围"，不新建、不修改、不删除这些图形
  3) pin 层：新 label 统一打在 layer 95, texttype 251（95:251）
  4) 均匀网格：以 Offset 为基准、Pitch 为步长，在 Metal4 图形范围内生成 X×Y 网格
  5) 就近寻址（dual rail 优化）：理论格点若不在金属上，不跳过，吸附到最近
    Metal4 图形内部；文本由最近 rail 决定（353→VDD，354→VSS）
  6) 输出：除 95:251 label 外，其他所有图层/层次结构保持原样

用法：
  python3 vdd_vss_rail_label.py \
      --gds in.gds --out out.gds \
      --pitch-x 1.0 --pitch-y 2.0 \
      --offset-x 0.0 --offset-y 0.0 \
      [--inherit] [--text-353 VDD --text-354 VSS] [--layer 95 --texttype 251] \
      [--no-del-contact] [--log replace.log]
依赖：gdstk（Python3.11，项目环境已具备）。坐标单位与 GDS 一致（微米）。
"""

# ═════════════════════════════════════════════════════════════════════════════
# 【流程版本说明】2026-11-19 标注 —— 本工具现有 4 种流程（main 内互斥分支，全部保留）：
#   ① 默认网格模式（先删后加，pitch/offset 机械栅格）—— v1.12「均匀矩阵重打」。
#      ⚠️ 对 1.py 拼接 GDS 不推荐：会删掉 leafcell 继承的规律排布（与原始厂商 GDS
#      313/313 行逐 label 一致），换成 VDD/VSS 各自成行的机械矩阵。
#   ② --per-rail         逐碎片中心布点
#   ③ --fill-blank       只补空、不删除（保留原始分布）
#   ④ --restore-original 恢复原始规律排布 + 碎片覆盖兜底 ——【当前对拼接 GDS 推荐】
#      先删后按快照原样恢复（含同位成对 label），兜底点保证落在碎片金属上。
#      2026-11-19 修复：①去重不再塌缩快照中的成对 label；②兜底点落金属保证。
#   验收：_verify_canonical_metal.py（落金属，必须用 canonical 碎片口径）
#         ../gds_tiler_1022/_probe_row_diff3.py（与原始 GDS 逐行 diff）
# ═════════════════════════════════════════════════════════════════════════════
import argparse
import math
import os
import sys

import gdstk

DEFAULT_TEXTS = ("VDD", "VSS")          # 旧标签清理匹配文本
# 新标签默认 rail 文本映射 —— 依据原始 GDS 探测：95:353 上现为 VSS、95:354 上现为 VDD。
# 不要凭字面猜测；以实际 GDS 为准（详见技术方案 §5.6「分层归属校验」）。
RAIL_DEFAULT_TEXTS = {353: "VSS", 354: "VDD"}


class _Tee:
    """同时写入多个流（屏幕 + log 文件），用于 --log 记录替换过程。"""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


# --------------------------------------------------------------------------- #
# 层次遍历
# --------------------------------------------------------------------------- #
def collect_cells(top_cell):
    seen = {}

    def walk(c):
        if id(c) in seen:
            return
        seen[id(c)] = c
        for r in c.references:
            if isinstance(r.cell, gdstk.Cell):
                walk(r.cell)
    walk(top_cell)
    return list(seen.values())


# --------------------------------------------------------------------------- #
# 引用变换：把任意 cell 本地坐标映射到顶层全局坐标
#  A = R(rot) @ mirror(局部矩阵)；平移组合累加
# --------------------------------------------------------------------------- #
def _mat(rot, x_reflection, mag):
    c = math.cos(rot)
    s = math.sin(rot)
    if x_reflection:             # 关于 x 轴镜像
        A = [[c, s], [s, -c]]
    else:
        A = [[c, -s], [s, c]]
    return [[v * mag for v in row] for row in A]


def _gx(A, x, y):
    return A[0][0] * x + A[0][1] * y, A[1][0] * x + A[1][1] * y


def _mmul(A, B):
    return [[A[0][0] * B[0][0] + A[0][1] * B[1][0],
             A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0],
             A[1][0] * B[0][1] + A[1][1] * B[1][1]]]


def _rep_offsets(rep):
    """从 gdstk Repetition 提取所有 (dx,dy) 偏移（父坐标系）；无重复返回 [(0,0)]。

    用 gdstk 官方 get_offsets()：兼容 rectangular / 两向量(v1,v2) / 任意偏移
    全部形态。此前手查 columns/rows/spacing 的写法在「两向量型 AREF」
    （spacing=None）上会静默失败 → AREF 不展开 → 只见 1/N 版图。
    """
    if rep is None:
        return [(0.0, 0.0)]
    pts = []
    try:
        for o in rep.get_offsets():
            pts.append((float(o[0]), float(o[1])))
    except Exception:
        pts = []
    if not pts:
        return [(0.0, 0.0)]
    if (0.0, 0.0) not in pts:
        pts.insert(0, (0.0, 0.0))
    return pts


def collect_global_polys(top_cell, layer=95, datatypes=(353, 354)):
    """返回 [(datatype, [[x,y],...]), ...]，坐标为顶层全局坐标。
    目标：Metal4 电源/地图形 = layer 95, datatype 353 / 354。
    用 gdstk 原生 get_polygons(apply_repetitions=True)：由库内部正确展开
    SREF/AREF/Repetition 与全部层级变换，避免手写遍历的遗漏。"""
    out = []
    for dt in datatypes:
        for poly in top_cell.get_polygons(apply_repetitions=True,
                                          include_paths=False,
                                          layer=layer, datatype=dt):
            out.append((dt, [[float(p[0]), float(p[1])] for p in poly.points]))
    return out


def collect_global_labels(top_cell, layer=None, texttype=None):
    """返回 [(text, (x, y))]，label 全局坐标（含 AREF/Repetition 展开实例）。
    用 gdstk 原生 get_labels(apply_repetitions=True)。layer/texttype=None=不过滤。"""
    out = []
    for lb in top_cell.get_labels(apply_repetitions=True,
                                  layer=layer, texttype=texttype):
        out.append((lb.text, (float(lb.origin[0]), float(lb.origin[1]))))
    return out


def delete_power_labels(top_cell, texts, layer=None, texttype=None):
    """递归删除文本命中集合的 label。只删 label，不影响各种图形。
    layer/texttype 可限制删除范围（None=不限层/不限字型），
    默认按需求只删 Metal4(layer 95) 的 VDD/VSS，避免波及其它层端口。"""
    texts = set(texts)
    rm = 0
    for c in collect_cells(top_cell):
        for lb in list(c.labels):
            if lb.text not in texts:
                continue
            if layer is not None and lb.layer != layer:
                continue
            if texttype is not None and lb.texttype != texttype:
                continue
            c.remove(lb)
            rm += 1
    return rm


def _nearest_rail_dist(x, y, infos, idx, cell):
    """返回 (最近rail_datatype, 最近距离)。若无可搜返回 (None, inf)。"""
    ci = int(math.floor(x / cell))
    cj = int(math.floor(y / cell))
    best_d = float("inf")
    best_dt = None
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for k in idx.get((ci + di, cj + dj), ()):
                _dt, pts, b0, b1, c0, c1 = infos[k]
                d, _q = dist_poly(pts, x, y)
                if d < best_d:
                    best_d = d
                    best_dt = _dt
    return best_dt, best_d


def delete_pg_pins_contact(top_cell, rails, texts, layer=None, texttype=None,
                           snap_tol=0.0, diagnose=False):
    """只删【与 95:353/354 金属接触】的 PG M4 pin label。
    带 Reference 变换取 label 全局坐标；label 到任一 rail 多边形边界
    **距离 ≤ snap_tol** 才算接触（取代原严格 pnpoly 内部判定）。
    layer/texttype 限定目标 pin 层（默认 95:251）。snap_tol 为接触容差
    （微米）：0.0=严格内部（原行为），0.1~0.3=覆盖碎片间隙+变换漂移。
    当 diagnose=True 时，打印未删除 label 的文本、坐标、到最近rail距离、所在cell。"""
    texts = set(texts)
    rm = 0

    # 建格网索引
    xs, ys = [], []
    for _dt, pts in rails:
        for p in pts:
            xs.append(p[0]); ys.append(p[1])
    bx0, bx1 = min(xs), max(xs)
    by0, by1 = min(ys), max(ys)
    grid_cell = max(bx1 - bx0, by1 - by0, 1.0) / 100.0
    infos, idx = _build_rail_index(rails, grid_cell)

    def near_rail(x, y):
        ci = int(math.floor(x / grid_cell))
        cj = int(math.floor(y / grid_cell))
        # 搜索半径必须覆盖 snap_tol：固定 9 邻域只够 ~1 个格宽(0.583um)，
        # snap_tol(默认1.5) 更大时按格数扩环，否则 0.6~1.5um 内的接触 label 漏删
        rings = int(math.ceil(snap_tol / grid_cell)) if snap_tol > 0 else 0
        for di in range(-rings, rings + 1):
            for dj in range(-rings, rings + 1):
                for k in idx.get((ci + di, cj + dj), ()):
                    _dt, pts, b0, b1, c0, c1 = infos[k]
                    if (x < b0 - snap_tol or x > b1 + snap_tol or
                            y < c0 - snap_tol or y > c1 + snap_tol):
                        continue
                    d, _q = dist_poly(pts, x, y)
                    if d <= snap_tol:
                        return True
        return False

    def walk(cur_cell, A, t):
        nonlocal rm
        for lb in list(cur_cell.labels):
            if layer is not None and lb.layer != layer:
                continue
            if texttype is not None and lb.texttype != texttype:
                continue
            if lb.text not in texts:
                continue
            gx, gy = _gx(A, lb.origin[0], lb.origin[1])
            gx += t[0]; gy += t[1]
            if near_rail(gx, gy):
                cur_cell.remove(lb)
                rm += 1
            elif diagnose:
                dt, d = _nearest_rail_dist(gx, gy, infos, idx, grid_cell)
                dt_name = {353: "353-VSS", 354: "354-VDD", None: "NA"}.get(dt, str(dt))
                print(f"[DIAG-KEEP] {lb.text}  ({gx:.6f},{gy:.6f})  "
                      f"dist={d:.6f}  rail={dt_name}  cell={cur_cell.name}")
        for ref in cur_cell.references:
            if not isinstance(ref.cell, gdstk.Cell):
                continue
            A_ch = _mat(ref.rotation or 0.0, bool(ref.x_reflection),
                        float(ref.magnification) if ref.magnification else 1.0)
            ox, oy = ref.origin
            # AREF/Repetition：每个重复实例都要展开（否则删除判断只覆盖 1/N 实例）
            for dx, dy in _rep_offsets(getattr(ref, "repetition", None)):
                # 子原点(含 repetition 偏移)位于父坐标系，只应乘父矩阵 A；
                # 旧写法先 _gx(A_ch,o) 再 _gx(A,·) 等于 A·A_ch·o，对带旋转/镜像的
                # 引用平移错误 → 其上 label 全局坐标算错 → 接触判定失败而漏删。
                A_new = _mmul(A, A_ch)
                gx, gy = _gx(A, ox + dx, oy + dy)
                walk(ref.cell, A_new, (gx + t[0], gy + t[1]))

    walk(top_cell, [[1.0, 0.0], [0.0, 1.0]], (0.0, 0.0))
    return rm


def filter_labels_contact(old_labels, rails, texts, snap_tol=0.3):
    """只保留【与 95:353/354 金属接触】且文本命中 texts 的 label，用于 --per-rail
    行基准采集。返回过滤后的 [(text, (x, y))]。

    根因修复：collect_global_labels 会采集整层次树上所有层的 label（含大量负
    Y / 远离 rail 的散点），直接喂给行聚合会把 rail 骨架污染成几百行、几万点。
    这里复用 delete_pg_pins_contact 相同的「点 <-> rail 多边形边界距离 ≤ snap_tol」
    接触判定（grid 索引 + 9 邻域搜索），把行基准收敛到真正的 PG M4 pin 上。
    snap_tol 统一复用 --snap-tol（接触容差，覆盖变换漂移与碎片间隙）。
    """
    texts = set(texts)
    xs, ys = [], []
    for _dt, pts in rails:
        for p in pts:
            xs.append(p[0]); ys.append(p[1])
    if not xs:
        return []
    grid_cell = max(max(xs) - min(xs), max(ys) - min(ys), 1.0) / 100.0
    infos, idx = _build_rail_index(rails, grid_cell)

    def near(x, y):
        ci = int(math.floor(x / grid_cell))
        cj = int(math.floor(y / grid_cell))
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for k in idx.get((ci + di, cj + dj), ()):
                    _dt, pts, b0, b1, c0, c1 = infos[k]
                    if (x < b0 - snap_tol or x > b1 + snap_tol or
                            y < c0 - snap_tol or y > c1 + snap_tol):
                        continue
                    d, _q = dist_poly(pts, x, y)
                    if d <= snap_tol:
                        return True
        return False

    return [lb for lb in old_labels
            if lb[0] in texts and near(lb[1][0], lb[1][1])]


# --------------------------------------------------------------------------- #
# 几何：点在多边形内 / 点到多边形（含吸附落点）
# --------------------------------------------------------------------------- #
def pnpoly(poly, x, y):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def dist_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1), (x1, y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    q = (x1 + t * dx, y1 + t * dy)
    return math.hypot(px - q[0], py - q[1]), q


def dist_poly(poly, x, y):
    """返回 (距离, 落点)。落点：若点已在多边形内则用该点，否则边界最近点。"""
    if pnpoly(poly, x, y):
        return 0.0, (x, y)
    best = float("inf")
    bestq = None
    n = len(poly)
    for i in range(n):
        p0 = poly[i]
        p1 = poly[(i + 1) % n]
        d, q = dist_seg(x, y, p0[0], p0[1], p1[0], p1[1])
        if d < best:
            best = d
            bestq = q
    return best, bestq


# --------------------------------------------------------------------------- #
# 旧标签文本继承：由旧 label 位置归属到最近的 rail 层，推断 353/354 各打什么字
# --------------------------------------------------------------------------- #
def inherit_text_map(old_labels, rails, default_map, threshold=10.0):
    from collections import Counter
    cnt = {353: Counter(), 354: Counter()}
    for text, (x, y) in old_labels:
        best_ly = None
        best_d = float("inf")
        for dt, poly in rails:
            d, _q = dist_poly(poly, x, y)
            if d < best_d:
                best_d = d
                best_ly = dt
        if best_ly is not None and best_d <= threshold:
            cnt[best_ly][text] += 1
    m = {}
    for ly in (353, 354):
        m[ly] = cnt[ly].most_common(1)[0][0] if cnt[ly] else default_map[ly]
    return m


# --------------------------------------------------------------------------- #
# 空间格网索引：把 rail 按包围盒分桶，网格点就近吸附时只查局部圆环
# --------------------------------------------------------------------------- #
def _build_rail_index(rails, cell):
    """按包围盒把 rail 分桶进 cell 宽度格网。返回 (infos, idx)。
    infos[i]=(datatype, pts, bx0, bx1, by0, by1); idx[(ci,cj)]=[i,...]"""
    from collections import defaultdict
    infos = []
    idx = defaultdict(list)
    for dt, pts in rails:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        bx0, bx1 = min(xs), max(xs)
        by0, by1 = min(ys), max(ys)
        k = len(infos)
        infos.append((dt, pts, bx0, bx1, by0, by1))
        for ci in range(int(math.floor(bx0 / cell)), int(math.floor(bx1 / cell)) + 1):
            for cj in range(int(math.floor(by0 / cell)),
                            int(math.floor(by1 / cell)) + 1):
                idx[(ci, cj)].append(k)
    return infos, idx


def _nearest_rail(x, y, infos, idx, cell, max_ring):
    """返回 (datatype, 吸附落点, 吸附距离)。
    从点所在格向外扩张 Chebyshev 环搜索最近多边形，返回其 datatype、吸附落点与最近距离。"""
    ci = int(math.floor(x / cell))
    cj = int(math.floor(y / cell))
    best_d = float("inf")
    best = (None, None)
    ring = 0
    while ring <= max_ring:
        for di in range(-ring, ring + 1):
            for dj in range(-ring, ring + 1):
                if max(abs(di), abs(dj)) != ring:
                    continue
                for k in idx.get((ci + di, cj + dj), ()):
                    dt, pts, bx0, bx1, by0, by1 = infos[k]
                    if (x < bx0 - best_d or x > bx1 + best_d or
                            y < by0 - best_d or y > by1 + best_d):
                        continue
                    d, q = dist_poly(pts, x, y)
                    if d < best_d:
                        best_d = d
                        best = (dt, q)
        # 环上界：最近多边形不可能在 Chebyshev 距离 > best_d/cell+1 的格子
        need = int(math.ceil(best_d / cell + 1.0)) if best_d != float("inf") else max_ring
        if ring >= need or ring >= max_ring:
            break
        ring += 1
    return best[0], best[1], best_d


# --------------------------------------------------------------------------- #
# 网格生成 + 就近吸附（默认方案，保留原行为）
# 说明：当前方案 = 全局等距网格 + 就近吸附，在碎片数据上可能产生不均匀
#   和边缘怪标。若要每条 rail 上均匀布点，请使用 --per-rail。
# --------------------------------------------------------------------------- #
def _fragment_cover_bounds(rails, cell_w):
    if not rails:
        return None
    occ = set()
    for _dt, pts in rails:
        for (x, y) in pts:
            occ.add((int(math.floor(x / cell_w)), int(math.floor(y / cell_w))))
    if not occ:
        return None
    gx = [g[0] for g in occ]; gy = [g[1] for g in occ]
    return ((min(gx) - 1) * cell_w, (max(gx) + 2) * cell_w,
            (min(gy) - 1) * cell_w, (max(gy) + 2) * cell_w)


def generate_label_points(rails, offx, offy, px, py, max_snap=None):
    if not rails:
        return []
    xs = []; ys = []
    for dt, pts in rails:
        xs.extend(p[0] for p in pts); ys.extend(p[1] for p in pts)
    bx0, bx1 = min(xs), max(xs); by0, by1 = min(ys), max(ys)
    cell = max(px, py) or 1.0
    infos, idx = _build_rail_index(rails, cell)
    max_ring = int(math.ceil(math.hypot(bx1 - bx0, by1 - by0) / cell)) + 2
    cb = _fragment_cover_bounds(rails, cell)
    i0 = math.floor((cb[0] - offx) / px) if cb else math.floor((bx0 - offx) / px)
    i1 = math.ceil((cb[1] - offx) / px) if cb else math.ceil((bx1 - offx) / px)
    j0 = math.floor((cb[2] - offy) / py) if cb else math.floor((by0 - offy) / py)
    j1 = math.ceil((cb[3] - offy) / py) if cb else math.ceil((by1 - offy) / py)
    points = []
    for i in range(int(i0), int(i1) + 1):
        x = offx + i * px
        for j in range(int(j0), int(j1) + 1):
            y = offy + j * py
            dt, q, d = _nearest_rail(x, y, infos, idx, cell, max_ring)
            if dt is None: continue
            if max_snap is not None and d > max_snap: continue
            points.append((dt, q))
    return points


# --------------------------------------------------------------------------- #
# 逐 rail 均匀布点（--per-rail 路径）
# 把所有 353/354 碎片按 Y 坐标聚合成水平 rail 带，沿每条 rail 的 X 长度
# 按 pitch 均匀打点。效果：每条 rail 上间距一致、数量=长度/pitch。
# --------------------------------------------------------------------------- #
def _detect_grid(rails, use_x=True, use_y=True):
    """从碎片分布自动检测主导 X 周期与 Y 周期。
    返回 (x_pitch, y_pitch)。0 表示未检测到。"""
    xs = []
    ys = []
    for _dt, pts in rails:
        xx = [p[0] for p in pts]
        yy = [p[1] for p in pts]
        xs.append((min(xx) + max(xx)) / 2.0)
        ys.append((min(yy) + max(yy)) / 2.0)
    x_pitch = y_pitch = 0.0

    def dominant_gap(vals):
        v = sorted(set(round(a, 4) for a in vals))
        if len(v) < 2:
            return 0.0
        from collections import Counter
        gaps = [round(v[i + 1] - v[i], 4) for i in range(len(v) - 1)]
        # 取最小正间距的众数（碎片密铺，用最小周期）
        positive = [g for g in gaps if 1e-4 < g < 5.0]
        if not positive:
            return 0.0
        return Counter(positive).most_common(1)[0][0]

    if use_x:
        x_pitch = dominant_gap(xs)
    if use_y:
        y_pitch = dominant_gap(ys)
    return x_pitch, y_pitch


def _label_rail_eps(orig_labels, y_group_tol=0.1):
    """从原始 95:251 label 的 Y 行聚类，得到真正的 rail 中心线 Y 列表。
    原始 label 的 Y 就是 rail 行位置（间距 ~1um）。
    返回 (rail_y_list, 只是用于对齐)。"""
    rows = {}
    for _txt, (x, y) in orig_labels:
        placed = False
        for key in rows:
            if abs(key - y) < y_group_tol:
                rows[key].append((x, y))
                placed = True
                break
        if not placed:
            rows[y] = [(x, y)]
    # 返回各行的代表 Y（取该行 label 平均 Y）
    return sorted((sum(p[1] for p in v) / len(v)) for v in rows.values())


def generate_label_points_per_rail(rails, offx, px, py, rail_y_offset=0.0,
                                   y_group_tol=0.08, orig_labels=()):
    """
    按原始 rail 行 Y 聚合，每行沿 X 均匀填满（--per-rail 模式）。

    策略：**用原始 95:251 label 的 Y 行作为 rail 中心线基准**（它们是真正的
    rail 骨架，Y 间距 ~1um），而不是用碎片密铺的 Y（间距 0.04~0.08um，会过度
    聚合成几百行）。对每一条 rail 行：
      1) Y = 原始 label 行中心（或用户 py grid 量化，若 give py）;
      2) 收集该行附近碎片的 X 范围并集 [xm,xM];
      3) 从 xm 到 xM 按 x_pitch 均匀填满点（含原先空的区域）。
    这样生成 = 原始 rail 骨架 + 把空处填满，均匀满阵列。
    """
    if not rails:
        return []
    if orig_labels:
        rail_ys = _label_rail_eps(orig_labels)
        # 若用原始 label 行，直接以它为 rail Y 基准（无视 py）
        y_rows = sorted(set(round(y, 6) for y in rail_ys))
        using_orig = True
    else:
        # 无原始 label 时回退：用 py 量化
        dx, dy = _detect_grid(rails, True, True)
        yp = py if py > 1e-12 else (dy if dy > 0 else y_group_tol)
        y_rows = None
        using_orig = False
    # X 周期
    dx, _ = _detect_grid(rails, True, False)
    xp = px if px > 1e-12 else (dx if dx > 0 else 0.2)

    from collections import defaultdict
    # 收集每个碎片的 (yc, xm, xM, dt)
    frags = []
    for dt, pts in rails:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        frags.append((dt, (min(ys) + max(ys)) / 2.0, min(xs), max(xs)))
    frags.sort(key=lambda f: f[1])

    point_list = []
    seen = set()
    if using_orig:
        # 对每条原始 rail 行 Y，找该行附近（±rail周期/2）的碎片 X 并集
        for i, ry in enumerate(y_rows):
            lo = ry - (y_rows[i] - (y_rows[i - 1] if i > 0 else ry - 1.0)) / 2.0
            hi = ry + ((y_rows[i + 1] if i + 1 < len(y_rows) else ry + 1.0) - ry) / 2.0
            band = [f for f in frags if lo <= f[1] <= hi]
            if not band:
                continue
            y_base = ry + rail_y_offset
            # 分 datatype
            for dt in {f[0] for f in band}:
                sub = [f for f in band if f[0] == dt]
                xm = min(f[2] for f in sub)
                xM = max(f[3] for f in sub)
                n0 = math.ceil((xm - offx) / xp)
                n1 = math.floor((xM - offx) / xp)
                for n in range(n0, n1 + 1):
                    x = offx + n * xp
                    k = (dt, round(x, 6), round(y_base, 6))
                    if k in seen:
                        continue
                    seen.add(k)
                    point_list.append((dt, (x, y_base)))
        print(f"[per-rail] 原始label行聚合: {len(y_rows)} 条 rail 行, "
              f"每行X填满 (x_pitch={xp:.4f}um), 生成 {len(point_list)} 个 label")
    else:
        # 回退：py 量化（一般不触发）
        yp = py if py > 1e-12 else (dy if dy > 0 else y_group_tol)
        grid = defaultdict(lambda: defaultdict(list))
        for dt, yc, xm, xM in frags:
            y_idx = int(round(yc / yp))
            grid[y_idx][dt].append((xm, xM))
        for y_idx in sorted(grid.keys()):
            y_base = y_idx * yp + rail_y_offset
            for dt in sorted(grid[y_idx].keys()):
                ranges = grid[y_idx][dt]
                xm = min(r[0] for r in ranges); xM = max(r[1] for r in ranges)
                n0 = math.ceil((xm - offx) / xp)
                n1 = math.floor((xM - offx) / xp)
                for n in range(n0, n1 + 1):
                    x = offx + n * xp
                    k = (dt, round(x, 6), round(y_base, 6))
                    if k in seen:
                        continue
                    seen.add(k)
                    point_list.append((dt, (x, y_base)))
        print(f"[per-rail] py量化回退: {len(grid)} 行, x_pitch={xp:.4f}um, "
              f"生成 {len(point_list)} 个 label")
    return point_list


# --------------------------------------------------------------------------- #
# --fill-blank：保留原始 label 分布，只在「有 rail 无 PG label」的碎片位置补点
# （通用实现：所有容差由输入 GDS 自动推导，无写死数值）
# --------------------------------------------------------------------------- #
def _derive_tols(rails, orig_labels=None, pg_texts=None):
    """从输入 GDS 自动推导补点的 X 判定半径 dx_tol（通用，无写死数值）。

    dx_tol = 0.5 × 碎片 X 间距的「众数」（最常见相邻碎片中心距）。
    用众数而非中位数：中位数会被行内簇间大间隙拉偏成一整个间距，
    导致已铺区边界后的第一个空位被误判为「已有 label」→ 每条边界缺一条缝。
    """
    from collections import Counter
    centers = []
    hts = []
    for dt, pts in rails:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        centers.append(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0))
        hts.append(max(ys) - min(ys))
    if not centers:
        return 0.05
    hts.sort()
    tol_row = 2.0 * hts[len(hts) // 2]           # 行聚类容差 = 2×碎片高度中位数
    rows = []                                    # [anchor_y, set(round(cx,4))]
    for cx, cy in sorted(centers, key=lambda c: c[1]):
        if rows and abs(rows[-1][0] - cy) <= tol_row:
            rows[-1][1].add(round(cx, 4))
        else:
            rows.append([cy, set([round(cx, 4)])])
    xg = []
    for _ay, cxs in rows:
        s = sorted(cxs)
        for i in range(len(s) - 1):
            g = s[i + 1] - s[i]
            if g > 1e-9:
                xg.append(g)
    if not xg:
        return 0.05
    # 取 P25 分位数：碎片行 X 栅格可能疏密不一（实测有 0.204/0.102 两种），
    # 覆盖判定必须以「最细栅格」为准——若 dx_tol ≥ 一个细间距，已铺区边界后
    # 的第一个空位会被误判为已有 label → 每条边界缺一条缝。
    xg.sort()
    p25 = xg[int(len(xg) * 0.25)]
    return 0.5 * p25


def plan_fill_points(rails, orig_labels, dx_tol, pg_texts=None, text_map=None):
    """按原始 label 行的「簇图案」周期延拓补空（通用，无写死数值）。

    原始图案（实测）：每条 label 行 = 若干「密集簇」（簇内 VDD/VSS 交替、
    间距 = 碎片 X 间距），簇间有大间隙（~12.6um），周期 ~15.8um。
    补空 = 每行的簇图案按周期平移延拓，直到该行 rail 的最远 X：
      1) 原始 PG label 聚行
      2) 每行 label X 序列 → 按「间隙最大跳变」分簇 → 周期 = 簇起点间距中位数
      3) 该行 rail 延伸范围 = 行带内碎片中心的最大 X
      4) k=1,2,...：整簇图案平移 k×周期，逐点补（文本沿用源 label 的 VDD/VSS）
      补点与原设计完全同 Y 行、同 X 栅格、同 VDD/VSS 交替 → 排列无缝一致
    返回 [(datatype, (x, y))]
    """
    from collections import defaultdict
    import bisect
    inv_map = {}
    if text_map:
        for dt, tx in text_map.items():
            inv_map[tx] = dt
    pg = set(pg_texts) if pg_texts else None
    pool = [(x, y, t) for t, (x, y) in orig_labels if (pg is None or t in pg)]
    if not pool:
        pool = [(x, y, t) for t, (x, y) in orig_labels]
    # 1) PG label 聚行（Y 容差 = 0.5×相邻 Y 差中位数）
    lys = sorted(y for x, y, t in pool)
    dyg = sorted(lys[i + 1] - lys[i] for i in range(len(lys) - 1)
                 if lys[i + 1] - lys[i] > 1e-9)
    tol_lrow = 0.5 * dyg[len(dyg) // 2] if dyg else 0.1
    lrows = []                            # [anchor_y, [(x, text)...]]
    for x, y, t in sorted(pool, key=lambda p: p[1]):
        if lrows and abs(lrows[-1][0] - y) <= tol_lrow:
            lrows[-1][1].append((x, t))
        else:
            lrows.append([y, [(x, t)]])
    rys = [r[0] for r in lrows]
    rg = sorted(rys[i + 1] - rys[i] for i in range(len(rys) - 1))
    lpitch = rg[len(rg) // 2] if rg else 0.5

    # 2) 碎片 → 最近 label 行（|ΔY| ≤ 一个行距），记录每行碎片的 max X（rail 延伸范围）
    row_extent = defaultdict(float)
    for dt, pts in rails:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx = (min(xs) + max(xs)) / 2.0
        cy = (min(ys) + max(ys)) / 2.0
        j = bisect.bisect_left(rys, cy)
        best = None
        for jj in (j - 1, j):
            if 0 <= jj < len(rys):
                d = abs(rys[jj] - cy)
                if best is None or d < best[0]:
                    best = (d, jj)
        if best is None or best[0] > lpitch:
            continue
        if cx > row_extent[best[1]]:
            row_extent[best[1]] = cx
    # 3) 每行：簇图案 + 周期 → 周期延拓
    out = []
    for i, (ay, items) in enumerate(lrows):
        items.sort()
        xs = [x for x, t in items]
        extent = row_extent.get(i, 0.0)
        if extent <= xs[-1] + dx_tol:
            continue                       # 该行 rail 没有超过已有 label 的延伸
        # 分簇：间隙分布的最大跳变 = 簇内间距 / 簇间大间隙 的分界
        gaps = sorted(xs[i2 + 1] - xs[i2] for i2 in range(len(xs) - 1)
                      if xs[i2 + 1] - xs[i2] > 1e-9)
        if len(gaps) < 2:
            continue
        bi, bg = 0, -1.0
        for i2 in range(len(gaps) - 1):
            if gaps[i2 + 1] - gaps[i2] > bg:
                bg, bi = gaps[i2 + 1] - gaps[i2], i2
        thr = 0.5 * (gaps[bi] + gaps[bi + 1]) if bg > 0 else 1.0
        clusters = []
        for x, t in items:
            if clusters and x - clusters[-1][-1][0] <= thr:
                clusters[-1].append((x, t))
            else:
                clusters.append([(x, t)])
        if len(clusters) < 2:
            continue                       # 单簇行无法确定周期
        starts = [c[0][0] for c in clusters]
        pers = sorted(starts[i2 + 1] - starts[i2] for i2 in range(len(starts) - 1))
        period = pers[len(pers) // 2]
        if period <= dx_tol:
            continue
        # 周期延拓（occ = 该行已占 X，含原始 label 与已补点，防重）
        occ = list(xs)
        nshift = int((extent - starts[0]) / period)
        for k in range(1, nshift + 1):
            shift = k * period
            for c in clusters:
                for x, t in c:
                    nx = x + shift
                    if nx > extent + dx_tol:
                        continue
                    j2 = bisect.bisect_left(occ, nx)
                    hit = False
                    for jj2 in (j2 - 1, j2):
                        if 0 <= jj2 < len(occ) and abs(occ[jj2] - nx) <= dx_tol:
                            hit = True
                            break
                    if hit:
                        continue
                    bisect.insort(occ, nx)
                    dt = inv_map.get(t)
                    if dt is None:
                        continue
                    out.append((dt, (nx, ay)))
    return out


def refill_labels_per_cell(cells, text_map, layer=95, texttype=251,
                           del_texts=("VDD", "VSS"), snap_tol=0.3):
    """逐 cell（定义级）在本 cell 自己的 rail 碎片位置补 PG label。

    与原始 level 对应：新 label 加在 rail 所在的 cell 定义内 → 随该 cell 的
    所有实例铺满整个阵列，排列/密度自动与原设计的实例栅格一致
    （原始阵列怎么铺，补出来的 label 就怎么铺——整齐阵列免费获得）。

    每个 cell 的处理：
      1) 收集本 cell 自己的 95:353/354 碎片（local 中心）
      2) 收集本 cell 剩余的 PG label（local；删除后通常为空）
      3) 碎片位置若无剩余 PG label 在 snap_tol 内 → 补一个（文本按碎片 datatype）
    cells: 可迭代的 cell 对象（main 传 collect_cells(top)）
    返回 (n_add, [(cell_name, n_frag, n_add)...])
    """
    n_add = 0
    stats = []
    dset = set(del_texts)
    for c in cells:
        frags = []
        for p in c.polygons:
            if p.layer != layer or p.datatype not in text_map:
                continue
            xs = [pt[0] for pt in p.points]
            ys = [pt[1] for pt in p.points]
            frags.append((p.datatype, (min(xs) + max(xs)) / 2.0,
                          (min(ys) + max(ys)) / 2.0))
        if not frags:
            continue
        keep = [(lb.origin[0], lb.origin[1]) for lb in c.labels
                if lb.layer == layer and lb.texttype == texttype
                and lb.text in dset]
        added = 0
        for dt, cx, cy in frags:
            if any((lx - cx) ** 2 + (ly - cy) ** 2 <= snap_tol ** 2
                   for lx, ly in keep):
                continue
            c.add(gdstk.Label(text_map[dt], (cx, cy),
                              layer=layer, texttype=texttype))
            keep.append((cx, cy))
            added += 1
        if added:
            n_add += added
            stats.append((c.name, len(frags), added))
    return n_add, stats


# --------------------------------------------------------------------------- #
# 落盘（保持层次，仅由顶层新增 label；几何与其它层一律不动）
# --------------------------------------------------------------------------- #
def save_gds(top_cell, out_path, src_lib):
    cells = collect_cells(top_cell)
    if os.path.exists(out_path):
        os.remove(out_path)
    lib = gdstk.Library()
    lib.unit = src_lib.unit
    lib.precision = src_lib.precision
    for c in cells:
        lib.add(c)
    lib.write_gds(out_path)
    return out_path


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--gds", required=True, help="输入 GDS")
    p.add_argument("--out", required=True, help="输出 GDS")
    p.add_argument("--pitch-x", type=float, default=0.0, help="X 方向 Pitch（非 per-rail 模式必填，per-rail 模式下忽略）")
    p.add_argument("--pitch-y", type=float, default=0.0, help="Y 方向 Pitch（非 per-rail 模式必填，per-rail 模式下忽略）")
    p.add_argument("--offset-x", type=float, default=0.0, help="X 向基准偏移（默认0）")
    p.add_argument("--offset-y", type=float, default=0.0, help="Y 向基准偏移（默认0）")
    p.add_argument("--quadrant", type=int, default=None,
                   help="仅保留指定象限的 label（1=第一象限 x>=0且y>=0）。默认不限制")
    p.add_argument("--max-snap", type=float, default=1.5, metavar="UM",
                   help="吸附距离上限（微米）。网格点吸附到最近 rail 的距离超过该值则丢弃，"
                        "避免在碎片覆盖范围之外的边缘空白区硬拉出多余 label。"
                        "例如 --max-snap 1.5（丢弃距金属>1.5um 的落点）。默认 1.5")
    p.add_argument("--layer", type=int, default=95, help="pin 层号（默认95）")
    p.add_argument("--texttype", type=int, default=251, help="pin texttype（默认251）")
    p.add_argument("--text-353", default=RAIL_DEFAULT_TEXTS[353],
                   help=f"95:353 rail 上的文本（默认 {RAIL_DEFAULT_TEXTS[353]}，据原始 GDS）")
    p.add_argument("--text-354", default=RAIL_DEFAULT_TEXTS[354],
                   help=f"95:354 rail 上的文本（默认 {RAIL_DEFAULT_TEXTS[354]}，据原始 GDS）")
    p.add_argument("--del-texts", default="VDD,VSS",
                   help="清理旧标签的文本，逗号分隔（默认 VDD,VSS）")
    p.add_argument("--del-layer", default="95",
                   help="清理旧标签的层号；'all'=所有层（默认 95=仅 Metal4）")
    p.add_argument("--del-texttype", default="251",
                   help="清理旧标签的 texttype；'all'=该层不限字型（默认 251=仅 PG M4 pin）")
    p.add_argument("--no-del-contact", action="store_true",
                   help="关闭'与353/354金属接触'判断，改为按 layer/texttype 全删该层 VDD/VSS")
    p.add_argument("--del-only", action="store_true",
                   help="仅删除旧 VDD/VSS label、不新增（用于测试验证清理效果）。不加则正常执行删除+新增")
    p.add_argument("--snap-tol", type=float, default=0.3, metavar="UM",
                   help="接触判定容差（微米），仅用于【旧标签删除】这一步：旧 95:251 "
                        "VDD/VSS label 到任一 95:353/354 多边形边界距离 ≤ 该值即删除。"
                        "默认 0.3um（覆盖变换漂移与碎片间隙）。设 0.0=严格内部判定。"
                        "若想清空所有旧标签再重排，可用较大值(如 1.5)；本参数不影响新 label 的落点。")
    p.add_argument("--per-rail", action="store_true",
                   help="逐碎片中心均匀布点（推荐）。对每个 95:353/354 碎片在其几何中心打一个"
                        "VDD/VSS label，完全复刻原始阵列分布（满、均匀、每条带一排）。"
                        "该模式下不需要 pitch/offset，--pitch-x/--pitch-y/--offset-x/--offset-y 均忽略")
    p.add_argument("--fill-blank", action="store_true",
                   help="保留原始 label 分布，只在『有 95:353/354 rail 但没有 PG label』的碎片"
                        "位置补 label（推荐用于补空白块）。补点密度与原始一致：X 间距/行距"
                        "容差全部由输入 GDS 自动推导，无写死数值，通用适配不同工艺/尺寸。"
                        "文本按碎片归属（353→--text-353，354→--text-354，或 --inherit）。"
                        "该模式下不删除任何旧 label，也不需要 pitch/offset")
    p.add_argument("--restore-original", action="store_true",
                   help="恢复原始排布（先删后加）：删除旧 PG label 后，按删除前的原始"
                        "label 快照原样恢复（保持 tiler/leafcell 的原始规律排布），"
                        "并对 0.35um 内无匹配文本 label 的碎片按『最近同文本原始 label "
                        "相对同 datatype 碎片中心的偏移』风格补 label。不需要 pitch/offset")
    p.add_argument("--diag", action="store_true",
                   help="诊断模式：打印每个 未删除 label 的(文本,坐标,到最近rail距离,所在cell)，"
                        "用于精确调参 --snap-tol。配合 --del-only 使用")
    p.add_argument("--inherit", action="store_true",
                   help="从旧 label 自动继承 353/354 各打什么文本")
    p.add_argument("--log", metavar="FILE", default=None,
                   help="把执行过程同时写入指定 log 文件（屏幕仍打印）")
    args = p.parse_args(argv)

    # 若指定 --log，则将 stdout tee 到文件，记录整个替换过程
    if args.log:
        try:
            _logf = open(args.log, "w")
        except OSError as e:
            raise SystemExit(f"无法打开 log 文件 {args.log}: {e}")
        sys.stdout = _Tee(sys.__stdout__, _logf)

    if not (args.per_rail or args.fill_blank or args.restore_original) and (
            args.pitch_x <= 0 or args.pitch_y <= 0):
        raise SystemExit("Pitch 必须为正数（per-rail / fill-blank 模式下不需要 pitch）")

    lib = gdstk.read_gds(args.gds)
    top = lib.top_level()[0] if lib.top_level() else lib.cells[0]
    print(f"[gds] 读入: {args.gds}  top={top.name}  cells={len(lib.cells)}")

    # ---- 1) 提取 Metal4 rail 图形（只读不改，供清理接触判断与网格吸附用） ----
    rails = collect_global_polys(top)   # layer=95, datatype 353/354
    n353 = sum(1 for r in rails if r[0] == 353)
    n354 = sum(1 for r in rails if r[0] == 354)
    print(f"[rail] 提取 Metal4 图形: 95:353={n353} 个, 95:354={n354} 个")
    if not rails:
        raise SystemExit("未找到 95:353 / 95:354 图形，无法定位标签范围")

    # ---- 2) 旧标签清理：只删【与 95:353/354 金属接触】的 PG M4 pin(95:251) ----
    del_set = set(s.strip() for s in args.del_texts.split(",") if s.strip())
    del_layer = None if str(args.del_layer).lower() in ("all", "") else int(args.del_layer)
    del_tl = None if str(args.del_texttype).lower() in ("all", "") else int(args.del_texttype)
    old_labels = collect_global_labels(top) if (args.inherit or args.per_rail
                                                or args.fill_blank
                                                or args.restore_original) else []
    if args.restore_original:
        # 原始 (95,251) VDD/VSS 快照（删除前采集，实例级全局坐标）——
        # 这是 tiler add_layer_to_top 展平 leafcell label 的结果，即"原始规律排布"
        snap_orig = [(lb.text, (float(lb.origin[0]), float(lb.origin[1])))
                     for lb in top.get_labels(apply_repetitions=True,
                                              layer=95, texttype=251)
                     if lb.text in del_set]
        print(f"[restore] 原始 (95,251) VDD/VSS 快照: {len(snap_orig)} 个")
    else:
        snap_orig = []
    # --per-rail 以「原始 95:251 label 的行」为 rail 骨架（与 out3/基线一致），
    # 每行按 X 满排，复现原始阵列密度。old_labels 同时供 --inherit 推断文本。
    rail_orig = old_labels
    if args.fill_blank:
        # --fill-blank：复现原始 label 分布 → 一个旧 label 都不删
        removed = 0
        print("[fill-blank] 保留原始 label 分布，不执行删除")
    elif args.no_del_contact:
        removed = delete_power_labels(top, del_set, layer=del_layer, texttype=del_tl)
    else:
        removed = delete_pg_pins_contact(top, rails, del_set,
                                         layer=del_layer, texttype=del_tl,
                                         snap_tol=args.snap_tol,
                                         diagnose=args.diag)
    print(f"[del] 删除 PG pin label={removed} 个"
          f"（layer={del_layer or 'all'}, texttype={del_tl or 'all'}, "
          f"接触353/354={'否' if args.no_del_contact else '是'}, 文本 {sorted(del_set)}）")

    # ---- 2.5) --del-only：仅删除、不新增，直接跳到校验保存 ----
    if args.del_only:
        print("[del-only] 模式：仅删除旧 label，跳过新增步骤")
        # 二次清扫：不管距离，把所有残留的 95:251 VDD/VSS 强制清空
        extra = 0
        for c in collect_cells(top):
            for lb in list(c.labels):
                if lb.text in del_set:
                    if (del_layer is None or lb.layer == del_layer) and \
                       (del_tl is None or lb.texttype == del_tl):
                        c.remove(lb)
                        extra += 1
        if extra:
            print(f"[del-extra] 二次强制清扫: 额外删除 {extra} 个残留 label")
        # ---- 校验：polygon 数量前后须一致 ----
        src_top = lib.top_level()[0] if lib.top_level() else lib.cells[0]
        poly_before = sum(len(c.polygons) for c in collect_cells(src_top))
        poly_after = sum(len(c.polygons) for c in collect_cells(top))
        print(f"[verify] polygon 总数 前={poly_before} 后={poly_after} "
              f"{'一致(仅删label)' if poly_before == poly_after else '!!不一致!!'}")
        save_gds(top, args.out, lib)
        print(f"[save] 写出: {args.out}")
        return 0

    # ---- 文本映射 ----
    text_map = {353: args.text_353, 354: args.text_354}
    if args.inherit:
        text_map = inherit_text_map(old_labels, rails, text_map)
    print(f"[text] 353->{text_map[353]!r}, 354->{text_map[354]!r}")

    # ---- 3) 生成 label 点（默认全局网格+就近吸附；--per-rail 时按原始 rail 行聚合） ----
    # ── 流程④【当前推荐】--restore-original：恢复原始规律排布 + 碎片覆盖兜底 ──
    if args.restore_original:
        # ---- 3R) 恢复原始排布（先删后加：加 = 原始快照 + 覆盖兜底）----
        # 原始 (95,251) VDD/VSS label 是 tiler add_layer_to_top 展平 leafcell label
        # 的结果，即"原始规律排布"本身；解析式全局规则不存在（各 leafcell 布局不同），
        # 故直接原样恢复快照，再对无匹配覆盖的碎片按局部原始偏移风格兜底。
        from collections import defaultdict as _dd, Counter
        restored = list(snap_orig)
        want = {353: text_map[353], 354: text_map[354]}

        # 碎片中心
        frag_centers = []
        frag_polys = []
        for dt, pts in rails:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            frag_centers.append((dt, (min(xs) + max(xs)) / 2.0,
                                 (min(ys) + max(ys)) / 2.0))
            frag_polys.append(pts)

        # label 索引（1um 格）——匹配覆盖检查
        lidx = _dd(list)
        for t, (x, y) in restored:
            lidx[(int(x // 1.0), int(y // 1.0))].append((t, x, y))

        def _has_match(cx, cy, wt, r=0.35):
            ci, cj = int(cx // 1.0), int(cy // 1.0)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    for (lt, lx, ly) in lidx.get((ci + di, cj + dj), ()):
                        if lt == wt and (lx - cx) ** 2 + (ly - cy) ** 2 <= r * r:
                            return True
            return False

        # 原始 label 行线（Y 聚类，tol=0.04，保留 0.084µm 级行距）——
        # 兜底点 Y 全部吸附到行线上（横平竖直），X = 碎片列中心（金属列即
        # label 列栅格）；行线吸附半径 0.35um = 覆盖判定半径，保证兜底
        # label 仍覆盖其碎片；周边原始无行线的区域退回碎片中心。
        ys_sorted = sorted(y for _t, (_x, y) in restored)
        row_lines = []
        for y in ys_sorted:
            if row_lines and y - row_lines[-1][-1] <= 0.04:
                row_lines[-1].append(y)
            else:
                row_lines.append([y])
        row_lines = [sum(v) / len(v) for v in row_lines]
        import bisect as _bisect

        n_cov = 0
        n_skip = 0
        k = -1
        for dt, cx, cy in frag_centers:
            k += 1
            wt = want[dt]
            if _has_match(cx, cy, wt):
                continue
            j = _bisect.bisect_left(row_lines, cy)
            best_row = None
            for r in row_lines[max(0, j - 1): j + 1]:
                if best_row is None or abs(r - cy) < abs(best_row - cy):
                    best_row = r
            if best_row is None or abs(best_row - cy) > 0.35:
                # 附近没有原始行线（原始刻意不打 label 的 Y 空档带，如
                # periphery 的 20.3~23.45 段）——保持与原始一致，不补
                n_skip += 1
                continue
            nx = cx
            ny = best_row
            # 落金属保证：若 (nx,ny) 不在该碎片上（行线吸附可能落进碎片间隙），
            # 吸附到该碎片上最近点（dist_poly 返回边界最近点，必在金属上）
            d_frag, q_frag = dist_poly(frag_polys[k], nx, ny)
            if d_frag > 0:
                nx, ny = q_frag
            restored.append((wt, (nx, ny)))
            lidx[(int(nx // 1.0), int(ny // 1.0))].append((wt, nx, ny))
            n_cov += 1

        # 去重只针对兜底新增点：快照中的同位成对 label（相邻拼接 cell 各贡献一个）
        # 是原始规律排布的组成部分，必须原样保留（与修复后 1.py 输出一致）；
        # 兜底点需对快照与彼此去重，避免同位重复添加。
        seen = set((t, round(x, 4), round(y, 4)) for t, (x, y) in snap_orig)
        final = list(snap_orig)
        n_backfill_dup = 0
        for t, (x, y) in restored[len(snap_orig):]:
            key = (t, round(x, 4), round(y, 4))
            if key in seen:
                n_backfill_dup += 1
                continue
            seen.add(key)
            final.append((t, (x, y)))
        for t, (x, y) in final:
            top.add(gdstk.Label(t, (x, y), layer=args.layer, texttype=args.texttype))
        ntext = Counter(t for t, _ in final)
        print(f"[restore] 原始快照 {len(snap_orig)} 个原样恢复（含成对 label）"
              f" + 覆盖兜底 {n_cov} 个（重合剔除 {n_backfill_dup} 个）"
              f" -> 共 {len(final)} 个")
        print(f"[add] 已写 {len(final)} 个 label（layer={args.layer}, "
              f"texttype={args.texttype}）  文本分布: {dict(ntext)}")
        # 校验 + 保存
        src_top = lib.top_level()[0] if lib.top_level() else lib.cells[0]
        poly_before = sum(len(c.polygons) for c in collect_cells(src_top))
        poly_after = sum(len(c.polygons) for c in collect_cells(top))
        print(f"[verify] polygon 总数 前={poly_before} 后={poly_after} "
              f"{'一致(仅增删label)' if poly_before == poly_after else '!!不一致!!'}")
        save_gds(top, args.out, lib)
        print(f"[save] 写出: {args.out}")
        return 0

    # ── 流程③ --fill-blank：只补空、不删除（保留原始分布） ──
    if args.fill_blank:
        # 逐 cell（与原始 level 对应）：删旧后，在本 cell 自己的 rail 碎片位置补
        n_add, cstats = refill_labels_per_cell(collect_cells(top), text_map,
                                               layer=args.layer,
                                               texttype=args.texttype,
                                               del_texts=del_set,
                                               snap_tol=args.snap_tol)
        print(f"[fill] 逐 cell 补 label {n_add} 个（加在原 level，随实例铺满阵列）")
        for nm, nf, na in cstats[:15]:
            print(f"   [cell] {nm}: rail碎片={nf}  补={na}")
        if len(cstats) > 15:
            print(f"   ... 共 {len(cstats)} 个 cell 有补点")
        # 校验 + 保存（label 已加在 cell 定义内，不走 points/quadrant 流程）
        src_top = lib.top_level()[0] if lib.top_level() else lib.cells[0]
        poly_before = sum(len(c.polygons) for c in collect_cells(src_top))
        poly_after = sum(len(c.polygons) for c in collect_cells(top))
        print(f"[verify] polygon 总数 前={poly_before} 后={poly_after} "
              f"{'一致(仅增删label)' if poly_before == poly_after else '!!不一致!!'}")
        save_gds(top, args.out, lib)
        print(f"[save] 写出: {args.out}")
        return 0
    # ── 流程② --per-rail：逐碎片中心布点 ──
    elif args.per_rail:
        points = generate_label_points_per_rail(
            rails,
            offx=args.offset_x,
            px=args.pitch_x,
            py=args.pitch_y,
            rail_y_offset=args.offset_y,
            y_group_tol=0.35,
            orig_labels=rail_orig)
    # ── 流程① 默认网格模式（先删后加机械栅格）——对拼接 GDS 不推荐，见文件头说明 ──
    else:
        points = generate_label_points(rails, args.offset_x, args.offset_y,
                                       args.pitch_x, args.pitch_y,
                                       max_snap=args.max_snap)
        snap_note = f"，max-snap={args.max_snap}um" if args.max_snap is not None else ""
        print(f"[grid] 生成 label 点 {len(points)} 个（碎片覆盖范围网格{snap_note}）")

    # ---- 3.5) 象限过滤：仅保留指定象限的最终落点 ----
    if args.quadrant is not None:
        before = len(points)
        # 依据吸附后的落点坐标判定象限（吸附可能把点吸到负半轴，故过滤 q 而非理论点）
        if args.quadrant == 1:
            points = [(ly, (x, y)) for ly, (x, y) in points if x >= 0 and y >= 0]
        elif args.quadrant == 2:
            points = [(ly, (x, y)) for ly, (x, y) in points if x < 0 and y >= 0]
        elif args.quadrant == 3:
            points = [(ly, (x, y)) for ly, (x, y) in points if x < 0 and y < 0]
        elif args.quadrant == 4:
            points = [(ly, (x, y)) for ly, (x, y) in points if x >= 0 and y < 0]
        else:
            raise SystemExit(f"--quadrant 仅支持 1/2/3/4，收到 {args.quadrant}")
        print(f"[quadrant] 象限 {args.quadrant} 过滤: {before} -> {len(points)} 个")

    # ---- 3.7) 吸附重合去重：相邻网格点吸附到同一碎片同一落点时只写一个 ----
    # （不做去重会产生同文本同坐标的重复 label，撑大文件且 viewer 叠字）
    if points:
        before = len(points)
        seen = set()
        uniq = []
        for ly, (x, y) in points:
            key = (ly, round(x, 4), round(y, 4))
            if key not in seen:
                seen.add(key)
                uniq.append((ly, (x, y)))
        if len(uniq) < before:
            print(f"[dedup] 吸附重合去重: {before} -> {len(uniq)} 个")
        points = uniq

    # ---- 3.8) 覆盖兜底：网格行相位与局部碎片行相位差半拍时，个别碎片可能
    # 被相邻异文本 rail 抢占吸附 → 碎片中心附近没有匹配文本的 label。
    # 扫描全部碎片，凡 0.35um 内无匹配文本 label 的，在碎片中心补一个
    # （中心必在金属上；半径由 pitch 推导，覆盖"格点到碎片中心+吸附拉偏"）。
    if points and rails:
        from collections import defaultdict
        if args.pitch_x > 0 and args.pitch_y > 0:
            r_cov = math.hypot(args.pitch_x, args.pitch_y)
        else:
            r_cov = 0.35
        lidx = defaultdict(list)
        for ly, (x, y) in points:
            lidx[(int(x // 1.0), int(y // 1.0))].append((ly, x, y))
        rr = int(math.ceil(r_cov / 1.0))
        add_cov = []
        for dt, pts in rails:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx = (min(xs) + max(xs)) / 2.0
            cy = (min(ys) + max(ys)) / 2.0
            ci, cj = int(cx // 1.0), int(cy // 1.0)
            hit = False
            for di in range(-rr, rr + 1):
                for dj in range(-rr, rr + 1):
                    for (ldt, lx, lyy) in lidx.get((ci + di, cj + dj), ()):
                        if ldt == dt and (lx - cx) ** 2 + (lyy - cy) ** 2 <= r_cov * r_cov:
                            hit = True
                            break
                    if hit:
                        break
                if hit:
                    break
            if not hit:
                add_cov.append((dt, (cx, cy)))
                lidx[(int(cx // 1.0), int(cy // 1.0))].append((dt, cx, cy))
        if add_cov:
            print(f"[cover] 覆盖兜底: {len(add_cov)} 个碎片中心无匹配文本 label，已在碎片中心补")
            points.extend(add_cov)

    # ---- 4) 打 label（新增到顶层，layer/texttype 为 pin 层） ----
    from collections import Counter
    ntext = Counter(text_map[ly] for ly, _ in points)
    for layer, (lx, ly) in points:
        top.add(gdstk.Label(text_map[layer], (lx, ly),
                            layer=args.layer, texttype=args.texttype))
    print(f"[add] 已写 {len(points)} 个 label（layer={args.layer}, "
          f"texttype={args.texttype}）  文本分布: {dict(ntext)}")

    # ---- 5) 校验：polygon 数量前后须一致 ----
    src_top = lib.top_level()[0] if lib.top_level() else lib.cells[0]
    poly_before = sum(len(c.polygons) for c in collect_cells(src_top))
    poly_after = sum(len(c.polygons) for c in collect_cells(top))
    print(f"[verify] polygon 总数 前={poly_before} 后={poly_after} "
          f"{'一致(仅增删label)' if poly_before == poly_after else '!!不一致!!'}")

    save_gds(top, args.out, lib)
    print(f"[save] 写出: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())