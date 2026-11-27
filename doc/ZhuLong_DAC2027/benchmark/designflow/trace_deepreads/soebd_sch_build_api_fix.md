# 深读笔记：1788916632467_soebd (junxu @ hfeg0plg79, mc=400)

**trace_source**: user=junxu, host=hfeg0plg79, session_file=1788916632467_soebd.messages.json, match_count=400
**keywords**: virtuoso:1140; schematic:882; cellview:309; dbopencellviewbytype:61; dbcreaterect:50; cadence:28; pyaether:25
**domain**: schematic_netlist (D shard)
**trace 获取**: .75 ssh→hfeg0plg79, live per-session path `/home/junxu/.cline/data/sessions/1788916632467_soebd/1788916632467_soebd.messages.json` (1.7MB, 307 msgs)

## 用户真实意图（多轮迭代）

用户 junxu 在迭代改进自研的 **virtuoso-cli Python API**（`/home/junxu/.cline/skills/virtuoso-cli/scripts/virtuoso_cli/api/schematic.py` 的 `SchematicSession` 类）及其 skill 文档（`block-design/SKILL.md` + `py-reference-schematic.md`），目的是让 agent 自动构建干净的门级/模块级 Virtuoso 原理图。真实起因：另一 session（c4wsu）里 agent 构建 FIFO 原理图时**滥用 `connect_by_name` stub 连线**（44 次 vs `wire_pin` 19 次，明明两器件相邻也用 stub 桥接）且**摆放密度不均**（太密→symbol 重叠，太开→观感差）。

### 5 个递进子任务
1. **分析**：为何 agent 滥用 stub + 摆放不均（分析报告：connect_by_name 出现 44 次全用于所有连线；典型 Icnt0_ns@(10,26) 与 Icnt0_ff@(13,26) 仅隔 3 单位同一行却用 stub）。
2. **改 skill 文档**：block-design/SKILL.md 加「规划布局表→get_cell_size 算最小间距→网格 x-step=max_w+2/y-step=max_h+3」+「per-net 决策表：同行近距离无遮挡→wire_pin；fanout>3/远距/遮挡→connect_by_name」；验收准则从「数量比例」改为「物理几何判断（fanout/线长/遮挡）」。
3. **加 4 个无窗口 CXMT SKILL 封装方法**：`generate_boundary/​remove_boundary/​snap_origin/​align_pins_to_boundary`，把 `geGetEditCellView()` 换成 `self._cv`、去 GUI 调用、`schStretch(geGetSelSet()...)`→`schStretch(list(pin)...)`（关键发现：`schStretch` 文档明示「不要求 cellview 在窗口打开」）。
4. **修 `wire_pin` 3 个 bug**：①tap 点从 midpoint 改 1/3（靠近源端）；②重复 label 检查（源引脚已有同名 net label 则跳过）；③`add_pin` stub 与 `wire_pin` 冲突——`wire_pin` 连到 pin 坐标时检测该坐标是否已有 stub wire，若是则延伸到 stub 远端形成连续直线。
5. **修 label 与 instance body 重叠 bug**：label 锚点原在源引脚坐标（落在器件 body 上），改为沿连线方向向内偏移使 label 落在 body 外；迭代调偏移量（0.25 不够→改用 cell 宽度相关偏移），最终验证 DOUT/s1q/eff/s0q label 全部落在 body 外。

### 关键物理量与判据（可用于 check.py 断言）
- `connect_by_name` 应只在：fanout>3 跨行/列 / 物理连线穿过其他 instance 或其 label / 远距总线 时用；其余（同行近距无遮挡）必须 `wire_pin`。
- 引脚绝对坐标 = instance 原点 + 引脚 offset（如 and2x1 Y pin offset (0.75,0.125)）。
- instance body 范围 = 原点..(原点+cell_size)（如 ffrqx1 size 0.925×0.98125）。
- label 不得落在任何 instance body 矩形内。
- tap 点应在源→目标线段的 1/3 处（非 midpoint）。
- pin alignment：直线连接的两 pin 须共享 y（水平）或 x（垂直）；但「路径被阻挡」（其他 instance body 落在两 pin 间矩形内）时须重排或改 add_wire L 型。

## case 合成 plan（下轮交付）

**task_id**: EDA-Eval-DesignFlow-SchBuildRouteDecide-001（待定）
**判定**: LIVE-NA（输入=结构化 spec JSON + mock schematic API 记录操作；判分=解析记录的操作验证路由决策/label 位置/对齐，无真实 Virtuoso 二进制依赖；virtuoso 不在 .75 不强求 L2.live）
**judge_layers**: [L0, L1]

**reframe**：真实用户意图（让 agent 按物理几何规则正确选择 wire_pin vs connect_by_name、摆放对齐、label 不重叠）reframe 为通用「原理图构建决策器 `build_schematic(spec)->ops_log` + hidden-B 反硬编码」。

**deliverable**: outputs/submit.zip(build_schematic.py)

**Mock schematic API（check.py 内置 harness）**：提供 `MockSchSession` 记录型 harness（录 add_instance/add_pin/wire_pin/connect_by_name/add_wire 调用 + 坐标→ops_log JSON），形状对但决策错的提交 fail。cell 库：mock cell 带 name/size/pin_offsets。

**A 档（visible）spec_A.json**：FIFO 片段，~6 instance（and2x1/xor2x1/ffrqx1/invx1/mux），含 3 类 net：①同行近距无遮挡（须 wire_pin）②远距 fanout（须 connect_by_name）③路径被阻挡（须 add_wire L 型或重排）。pin 位置 + cell size 给定。

**hidden B（token-structurally 不同）spec_B.json**：不同电路（如 LFSR/移位寄存器），不同 instance 名/坐标/cell 组合/位宽，3 类 net 重新分布⇒A 硬编码决策器在 B 全错。

**check.py ≥12 conds**：
a zip 含 build_schematic.py ②b py_compile ③c A 档运行 exit0 产 ops_log_A.json ④d A 同行近距 net 用 wire_pin 非 connect_by_name ⑤e A 远距 fanout net 用 connect_by_name ⑥f A 路径阻挡 net 用 add_wire(L 型) 或重排(无 body 在两 pin 间) ⑦g A label 不落在任何 instance body 矩形内 ⑧h A tap 点在源→目标 1/3 处(非 midpoint) ⑨i A 直线连接 pin 共享 y 或 x ⑩j B 档运行 exit0 产 ops_log_B.json ⑪k B 三类 net 决策正确(B 的分布不同于 A) ⑫l B label 不重叠 + B 反硬编码(build_schematic.py 源码无 A 专属 token: A instance 名/A 坐标/A net 名)。

**negative**：empty→c / print_only→d / core_deleted→e / hardcode_a(wire_pin 全用)→d,e / wrong_tap(midpoint)→h / label_on_pin→g。

**test_rationale**: 12 条断言：①zip 含 build_schematic.py ②py_compile 通过 ③A 档运行产 ops_log_A.json ④A 同行近距无遮挡 net 决策为 wire_pin ⑤A 远距 fanout net 决策为 connect_by_name ⑥A 路径被阻挡 net 用 add_wire L 型或重排 ⑦A 全部 label 不落在 instance body 矩形内 ⑧A tap 点在 1/3 处非 midpoint ⑨A 直线连接两 pin 共享 y 或 x ⑩B 档运行产 ops_log_B.json ⑪B 三类 net 决策正确(分布不同于 A) ⑫B label 不重叠且 build_schematic.py 源码无 A 专属 token(反硬编码)。

## 状态
DEBT: 1 deepread 未合成。下轮按 plan 合成 case。
