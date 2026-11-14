# r567 ki6z0 — WireWidthSpaceRuler 深读

**trace**: 1794557401043_ki6z0 (junweiw@hfeg0plg67/10.129.2.13, mc=181, aether:732;pyaether:353;rtl:71;schematic:39;virtuoso:32;mixed-signal:15;floorplan:12;dbget:12)
**size**: 549KB, 4 user turns. asst: editor×54, run_approved_command×20, read_files×18, RAG search_apis×18, get_api_details×8, skills×4, SandBox run_code×2.
**域**: layout_aether (pyAether ruler/geometry annotation)

## 用户意图演进
- U#0(原话)「帮我写一个脚本，通过我选中的线，启动脚本，可以帮我在layout中用标尺标注出这些线的width和space」= **A档合格 produce-task author-new-script**（提需求未给根因/方案）
- U#1「我选中一把线，怎么启动这个脚本」= how-to 运行
- U#2「添加一个快捷键吧，方便运行，将数字1作为快捷键」= 加 bindkey
- U#3「备占用就算了吧，我就用命令启动吧」= bindkey 被占，改命令启动

## 真实算法（mark_width_space.py 最终版，msg#23 editor new_text 6767B）
1. `get_box(fig)`: 稳健提取 bbox → (x0,y0,x1,y1) DBU 整数（兼容 tuple/list/属性 xMin..lowerLeft..）
2. `get_layer(fig)`: 提取层名（layer.name / lpp / layerName，fallback "UNKNOWN"）
3. `to_uu(cv, v)`: DBU→UU(微米) via `ae.emyDesignDbuToUU`，fallback /1000
4. `Annotator.ruler(p1,p2)`: aeCreateRuler(emyPointF vector) 优先，失败回退 dbCrtRuler(emyPointArrayF)，count++
5. `annotate_width(ann, boxes)`: 每个 box，width=窄向；`dw=x1-x0, dh=y1-y0, xm=(x0+x1)//2, ym=(y0+y1)//2`；`if dw>=dh`（横向线）→ ruler (xm,y0)-(xm,y1)（垂直标尺跨窄向 y）；`else`（纵向线）→ ruler (x0,ym)-(x1,ym)（水平标尺跨窄向 x）
6. `annotate_space(ann, boxes)`: **sorted-adjacent** 策略（避免 O(n²)）：
   - 横向线（dw>=dh）按 y0 升序排序；相邻对 (p,q)：x 投影重叠 `ox=min(p.x2,q.x2)-max(p.x0,q.x0)>0` 且 gap `q.y1? q[1]-p[3]>0` → ruler 于 xm=(max(p.x0,q.x0)+min(p.x2,q.x2))//2，从 (xm,p.y1) 到 (xm,q.y0)
   - 纵向线（dw<dh）按 x0 升序排序；相邻对：y 投影重叠 `oy>0` 且 gap `q.x0-p.x2>0` → ruler 于 ym，从 (p.x2,ym) 到 (q.x0,ym)
7. `main()`: emyInitAether → aeGetCurDesign → aeGetSelectedSet(cv) → 按 layer 分组 groups{layer:[bbox]} → 每层调 annotate_width + annotate_space → 打印统计

## 关键陷阱（判分用）
- **width 取向**：横向线（dw>=dh）width=dh → 垂直标尺；纵向线 width=dw → 水平标尺；**正方形 dw==dh 走横向分支**（dw>=dh 含等号）→ 垂直标尺
- **space 同层同向**：space 仅在同 layer、同取向（h 组 / v 组分开）的相邻对间算；跨取向（h vs v 同层）无 space
- **space 跨层**：不同 layer 的线即使 bbox 相同也无 space（按 layer 分组）
- **space 投影重叠**：相邻但 x（或 y）投影不重叠 → 无 space
- **space gap>0 严格**：gap==0（接触）→ 无 space（gap>0 才画）
- **sorted-adjacent**：只查排序后相邻对，非 O(n²) 全对（A-C 即使重叠，若 B 在排序中间隔开则不算）

## case 设计（B档 synthesized mock-behavioral）
- mock pyAether（无 live Aether/GUI），核心 get_box/annotate_width/annotate_space 几何不变
- 输入 layout_deck.json（figures: [{id,layer,bbox:[x0,y0,x1,y1]}]）→ 输出 rulers.json（width_rulers + space_rulers + summary，确定性排序）
- dual-hidden-fixture B/B2 反硬编（不同坐标/层/图数）
