# deepread: fjcqx — schematic vertical-corridor wire router (free_x)

- trace: `1795487677261_fjcqx.messages.json` (1.64MB live + 4.89MB archive, 599 msgs) @ jiashengz/hfeg0plg92, mc=674
- session type: **continuation/handoff** (U#1 = context summary from prior session)
- domain: schematic_netlist (Aether/pyAether schematic 几何布线)
- claimed: r1638 (2026-11-28), domain=schematic_netlist
- status: **DEBT — 深读完成，plan 落盘，下轮合成**

## 真实任务（trace 核心）

用户(jiashengz)在 Aether/pyAether 重建 `LATCH05C` latch schematic 的几何布线。核心痛点是 `fix_LATCH05C_geom.py` 里的 `free_x` 函数——**给一组垂直走线网（trunk）分配互不冲突的 x 列通道**——原来只避让器件 body、不避让引脚/端口/其它 net 列，且行互异断言对任何输入恒假；调用处用硬编码覆盖其输出。用户要求根治根因 + 按 placement guide 把 3 个 `TRI_NOTAD_*` symbol 的 B/C terminal 几何对调 + 重建布线使 DB 与网表一致、check&save 0 errors。

电气契约（guide 第 821–825 行 SPICE）：
```
X567 CK  CKn  NOT_W03_W05_L008
X559 Qn  D  CKn  CK  TRI_NOTAD_W05_W10_L008
X554 Qn  Q  CK   CKn TRI_NOTAD_W03_W05_L005
X564 Qn  Q  NOT_W05_W10_L005
```
4 器件 + 4 端口（ipin_CK/ipin_D/opin_Q/opin_Qn）。6 条垂直通道由 `free_x` 分配，等距 0.25：`ck-rail=7.50, B-drop=7.75, Q=8.00, Q-ladder=8.25, AD-spine=8.50, Qn=8.75`，全部避开 body/引脚 x/端口 x，两两不同。29 段实体线 + 10 命名 stub，check&save 0 errors，12/12 instTerm 与网表一致。

关键算法语义（`free_x`/`compute_plan`/`verify_plan`）：
- **free_x**: 给 corridor{lo,hi,spacing,count,step,margin,grid} 与 banned（body x 区间、pin x 点、port x 点），找 `count` 条等距 `spacing` 的垂直通道 x，全部避开 banned（带 margin）、落在 [lo,hi]、grid-snap、两两不同；从 lo 起按 step 搜索首个可行 x0（lo 本身可能被 banned ⇒ 需 shift）。
- **compute_plan**: 把 channel[i] 分配给 nets[i]；每网生成 1 条 trunk（垂直，x=channel，y∈[min pin y, max pin y]）+ 每 pin 1 条 tap（水平，y=pin.y，从 pin.x 到 channel.x）。
- **verify_plan**: 每条 channel 避开 banned、等距 spacing、distinct、∈[lo,hi]、grid-snap；trunk 垂直、tap 水平、每网 pin 全连；无 violation。
- 几何坑：Aether DBU vs UU（dbuPerUU=160）；B/C terminal 几何对调用 setBBox 翻坐标符号；时钟网必须命名 stub（走廊内 0 解，Aether 交点焊接会短路 CK/CKn）。

## case 合成 plan（下轮交付）

- **task_id**: `SchWireCorridorRouteProduce-001`
- **deliverable**: `route_wires.py` 暴露 `route_wires(spec) -> report`
- **judge_layers**: [L0, L1] (LIVE-NA — deliverable=Python 脚本产 channels/segments，check 跑候选 + 独立 free_x 复算断言，无真实 EDA 工具二进制依赖；Aether 不在 .75 不强求 L2.live)
- **spec schema**: `{instances[{name,cell,x,y,w,h}], ports[{name,x,y}], pins[{net,x,y}], nets[{name,pins[{x,y}]}], corridor{lo,hi,spacing,count,step,margin,grid}}`
- **report**: `{valid, channels[{net,x}], segments[{net,x1,y1,x2,y2,kind}], violations[], ops_log[], errors[]}`
- **A**(visible) spec_A.json: LATCH05C-like，4 inst（bodies [0,1.5]∪[3,5]∪[6,7]），corridor lo=7.5/hi=10/spacing=0.25/count=6/step=0.25/margin=0.2/grid=0.25 → channels=[7.5,7.75,8.0,8.25,8.5,8.75]（lo 不被 banned，无需 shift）
- **hidden B** spec_B.json: 不同电路（mux-like），不同 inst 布局（一 body [7,8] 侵入 corridor）+ 不同 corridor 参数（lo=7.5/hi=11/spacing=0.5/count=4/margin=0.3）→ lo=7.5 被 banned，free_x 须 shift 到 x0=8.5 → channels=[8.5,9.0,9.5,10.0]；token-structurally 全不同（net 名/inst 名/cell 名）⇒ A 硬编码器在 B 全错，且 no-shift 实现在 B 失败（测 search）
- **reference** `route_wires.py`: spec 驱动通用实现（_validate 必填字段→malformed raise+valid=False；_banned 收集 body 区间+pin/port 点；free_x 从 lo 起按 step+grid-snap 搜索首个可行 x0；compute_plan 生成 trunk+tap；verify_plan 收集 violations）
- **check.py 16+ conds(a-r)**: 独立 free_x 复算每网 channel 真值再断言候选匹配：
  a zip 含 py ②b py_compile ③c A 运行 exit0 valid==True ④d A channels count==6 ⑤e A channels==check 独立复算([7.5..8.75]) ⑥f A 每 channel 避开 banned ⑦g A channels 等距 spacing ⑧h A distinct ⑨i A ∈[lo,hi] ⑩j A grid-snap ⑪k A 每网 1 trunk(垂直,x==channel,y∈pin y range) ⑫l A 每 pin 1 tap(水平,y==pin.y,span pin.x→channel.x) ⑬m A violations 空 ⑭n B 运行 exit0 valid==True ⑮o B channels==check 独立复算([8.5,9.0,9.5,10.0]) 且 ≠A channels(反硬编码) ⑯p B count==4 ⑰q malformed spec(count=0/lo>hi/无解 corridor)→valid==False+errors 非空 ⑱r 源码无 A 专属字面量 token(7.5/7.75/ck_rail/LATCH05C/I567 等)
- **negatives(5)**: missing_py→a / empty→c / print_only→c / core_deleted(valid True+channels 空)→d / hardcode_a(硬编码 A channels+segments)→o(B mismatch) / no_shift(只取 lo+i*spacing 不 search)→o(B mismatch) — distinct first-fail {a,c,d,o}
- **自验**: ref check.py on reference_submit.zip → PASS 16+/16+；negative_selftest 5 neg ALL-FAIL distinct；SKIP_RUN=1 eval/run_one.sh → workdir leak 自检通过；3-way sha sync；k_check==k_rationale

## 与既有 case 的区分

- SchBuildRouteDecide-001 (r1622, soebd/junxu): per-net **连线方式决策**（wire_pin vs connect_by_name vs add_wire L-detour）+ label 不落 body + tap 1/3
- SchBoundaryGenProduce-001 (r1637, 3690n/taodu): schematic **模块边界矩形**生成（bbox merge + margin + grid-snap）
- **本 case (fjcqx)**: 垂直 **trunk 通道分配**（free_x 走廊搜索避让 banned 列）+ trunk/tap 段生成 + verify

三者是 schematic 几何的不同子问题，本 case 核心（走廊搜索 + shift）与前两者不重叠。任务初衷第 1 条：真实用户意图决定任务形态，fjcqx 是真实 trace，合法。

## .75 REACH_OK

eda_flow MCP open_session(r1638_D) 秒级 + run_commands 秒级 + scp→hfeg0plg92 trace 直读(1.64MB) + close cleaned（spec §2 证据三件套）

## 下轮 ETA

r1639 按 plan 合成 SchWireCorridorRouteProduce-001 落库（spec_A/B + ref + check.py 16+conds + 5 neg + selftest + sha sync + eval + 台账 mark + MEMORY/daily + commit）。
