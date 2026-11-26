# Deepread: 0xwjx — SelectByLineGroup (haiquanp pyAether point-to-line + figGroup)

**trace**: 0xwjx (haiquanp@hfeg0plg66/10.129.8.202, mc=72, aether:199;pyaether:177;waveview:19;dbget:15;mixed-signal:13;floorplan:11;calibre:9;virtuoso:8)
**size**: 695KB, 113 msgs, 7 user turns, assistant editor×25 + RAG×11 + run_approved×10
**A档**: USER#1 (原话) "cv=ae.aeGetCurDesign()...补全代码，这里的 point 是特殊封装的类型，获取值需要通过 points.x()、points.y()，新建通过 ae.emyPointF(x,y)" = **produce-task author-code-complete** (提需求未给根因/方案)

## 意图演进
- **U#1 produce-task**: 给 pyAether 代码骨架 (aeGetCurDesign/aeGetSelSet/dbCrtFigGroup + for shape in shapes loop)，`...` 处需补全 point_list→line_list 转换（相邻点连线含首尾闭合 + 线长+0.002）+ aeSelectByLine/dbAddFigToFigGroup 循环
- U#2 "输出去掉所有注释的完整代码" = format request
- U#3 "aeSelectByLine(points, mode='Vertex') 各个 mode 的区别" = Q&A
- **U#4 modify-existing**: "把它们选中后又包进 group 里...可以把选中的对象加进一个 list 里暂存...在大数量级场景下能够优化执行效率" (用户给根因+方案 → B档-only)
- **U#5 modify-existing**: "实测 ae.aeSelectFigs 执行效率不如预期...需要回到上一版，统一进一个 group" + 拆分两函数 + 增加 fig_filter 参数 (用户给根因+方案 → B档-only)
- U#6 "build_line_list() 的输入参数移除...给我一个调用例子" = refine API (B档-only)

## assistant 交付 (editor×25, 最终版 msg#94 select_by_line_group.py)
```python
import math
EXT = 0.001
_line_list_cache = []

def _extend_line(p1, p2, ext):
    x1,y1 = p1.x(),p1.y(); x2,y2 = p2.x(),p2.y()
    dx,dy = x2-x1,y2-y1; length = math.hypot(dx,dy)
    if length < 1e-12: return None
    ux,uy = dx/length, dy/length
    return (ae.emyPointF(x1-ux*ext, y1-uy*ext), ae.emyPointF(x2+ux*ext, y2+uy*ext))

def build_line_list(ext=EXT):
    global _line_list_cache
    shapes = ae.aeGetSelSet()
    lines = []
    shape_cnt = 0
    for shape in shapes:
        point_list = shape.points
        n = len(point_list)
        if n < 2: continue
        shape_cnt += 1
        edge_cnt = n if n > 2 else 1  # n>2: n edges (含首尾闭合); n==2: 1 edge (无闭合)
        for i in range(edge_cnt):
            p1 = point_list[i]; p2 = point_list[(i+1)%n]
            ext_pts = _extend_line(p1, p2, ext)
            if ext_pts is not None:
                lines.append([ext_pts[0], ext_pts[1]])
    _line_list_cache = lines
    print('build_line_list: %d shape(s) -> %d line(s)' % (shape_cnt, len(lines)))

def _fig_match(fig, fig_filter):
    if fig_filter is None: return True
    try: return bool(fig_filter(fig))
    except AttributeError: return False

def select_lines_to_group(fig_filter=None):
    fig_group = None; fig_cnt = 0
    for line in _line_list_cache:
        ae.aeSelectByLine(line)
        for fig in ae.aeGetSelSet():
            if _fig_match(fig, fig_filter):
                if fig_group is None:
                    fig_group = ae.dbCrtFigGroup(ae.aeGetCurDesign(), ae.emyPointF(0,0))
                ae.dbAddFigToFigGroup(fig, fig_group); fig_cnt += 1
    if fig_group is not None:
        ae.aeSelectFig(fig_group)
        print('select_lines_to_group: %d fig(s) -> new group (selected)' % fig_cnt)
    else:
        print('select_lines_to_group: 0 fig matched, no group created')

undo = ae.aeEnableUndo()
build_line_list()
select_lines_to_group(lambda fig: str(fig.objType) == 'CustomVia')
undo.disable()
```

## 核心算法 (B档 mock-behavioral 保留)
1. **edge count 规则**: n>2 → n edges (含首尾闭合 head-to-tail); n==2 → 1 edge (无闭合); n<2 → skip
2. **line extension**: 两端各延 ext (沿单位向量), 总长 = 原长 + 2*ext
3. **degenerate skip**: length < 1e-12 (重合点) → _extend_line 返回 None → 不入 line_list
4. **figGroup lazy create**: 仅首个匹配 fig 时才创建 group; 无匹配 → 无 group
5. **fig_filter**: 可选过滤 (如 str(fig.objType)=='CustomVia'); 不匹配 fig 不入 group
6. **select by line**: aeSelectByLine 选中线上的对象 → mock 为 fig 点是否在 extended 线段上 (共线 + 投影 t∈[0,1])

## 陷阱设计 (check.py 条件)
- closure trap: n>2 闭合 vs n==2 不闭合
- extension trap: 线段延长后才能选到的 fig (V4/VE/SD 在延长段)
- degenerate trap: 重合点 → 0 edges
- filter trap: 在线上但不匹配 filter 的 fig 不入 group
- lazy-create trap: 无匹配 fig → has_group=false
- anti-hardcode: B2 不同 deck 全不同
