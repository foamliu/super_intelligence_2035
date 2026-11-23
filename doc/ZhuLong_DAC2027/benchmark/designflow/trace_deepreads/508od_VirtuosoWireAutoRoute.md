# trace_deepread: 1787217250604_508od (junxu @ hfeg0plg79) — VirtuosoWireAutoRoute

- session: `1787217250604_508od.messages.json` (junxu @ hfeg0plg79 / 10.129.8.122)
- mc=2514, 1213 msgs, 3.55MB, schematic_netlist 域 (virtuoso:4200 / schematic:2518 / cellview:879)
- 跨 shard 状态：C 曾以 layout_virtuoso 域 claim 为 `LayoutLabelArgOrderFix-001`（2026-11-21），
  但该 case_id 不在任何 jsonl（abandoned）且 508od 是 schematic-dominant（NO layout keyword）→
  C 误判域 + 弃单。D 按 dr7mm r1165 先例 cross-shard reclaim，合成 VirtuosoWireAutoRoute-001。

## 用户意图演进（genuine user_input 序列）
1. U0: 改进 virtuoso-cli skill（Agent 写 skill 语句常出错）
2. U11: 先实际运行 virtuoso-cli 再说
3. U24/U26: 封装业务层（按 schematic/layout/ocean 模块划分）
4. U30/U38: 研究 virtuoso 与 pyAether 能否共用 python 顶层 API
5. U52: 先做 virtuoso 业务封装（列 window/lib/cell + schematic CRUD：创建/加器件/连线/属性）
6. U258: layout/ocean 先建框架
7. U352: 用封装好的 api 搭一个简单电路，过程中完善 api
8. U498/U566/U662/U704/U745/U801: 搭建中暴露问题（check error、pin 类型、连线怪、save 缺失、归纳 pin/wire 命名 api）
9. **U1132（本 case 意图）**: 「这种走线布局的方式有没有办法通过代码实现，并加入到 api 中，让 api 连出来的线自动就是这种不经过任何器件，符合人类习惯的走线」
10. U1191/U1206: 后续询问 virtuoso 是否有 auto-router，最终决定先用 auto-router

## 关键产物（A[1185] 算法解释）
`_route_around()` 自动避障走线规划：
- 障碍物 = `get_instance_bboxes()` 拿到所有 instance 的 bBox
- 路径策略（依次尝试，取第一个不穿过器件的）：
  - L 路径（2 段）：水平优先 + 垂直优先
  - Z 路径-垂直绕行（4 段）：在最左/右侧找 x 列走垂直
  - Z 路径-水平绕行（4 段）：在最上/下方找 y 行走水平
- 碰撞检测 `_seg_hits_rect`：水平线 y=c 是否穿过矩形 (ry1< y <ry2 且 x 重叠)；垂直线同理
- 首尾段豁免：pin 在器件 bBox 内部，Z 路径（3+段）跳过首尾段只检查中间段；L 路径（2 段）全检查

## 合成决策
抽 U1132 的自动避障走线规划意图，做成 L1 离线几何算法 case
（`seg_hits_rect` + `route_around` + `connect_wire`）。
- 不依赖 live Virtuoso（纯 Python 几何，可隐藏 B 判分）
- A/B1/B2/B3 结构性不相交：障碍数 0/1/2/1，路径形状 H-L / V-L / Z / Z(p1-in-obstacle 豁免)
- 15 条独立断言，3 负样本（print_only/core_deleted/hardcode_a）全 FAIL
- 真实 trace 溯源 metadata.trace_source 齐全
