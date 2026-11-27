# deepread — 1795791197331_3690n (taodu@hfeg0plg91, mc=335)

trace: `/home/taodu/.cline/data/sessions/1795791197331_3690n/1795791197331_3690n.messages.json` (1.63MB, 245 msgs, 142 user/103 asst)
domain: schematic_netlist (schematic:1041+pyaether:808+cellview:754+aether:593 dominant)
FRESH, NEW user (taodu 在 4-shard 台账无前例)

## 用户真实意图

用户(taodu)在 Aether/pyAether 平台把 Virtuoso SKILL `generate_boundary`（schematic 模块边界生成）移植成 Python agent skill。参考站点脚本 `/apps/imctf/cad/init/settings_aether/python_ae/se/innoCreateSchBndry.py`。目标产物 `/home/taodu/.cline/skills/circuit_assistant/generate_boundary/innoCreateSchBndry.py`。

核心工作流（5 个真实 user prompt）：
1. U#0：基于 Virtuoso 平台 skill `/home/taodu/.cline/skills/circuit_assistant/generate_boundary`，继续开发 Aether 平台 agent skill
2. U#66：给参考脚本路径 `/apps/imctf/cad/init/settings_aether/python_ae/se/innoCreateSchBndry.py`
3. U#115：明确移植要求——参考 innoCreateSchBndry.py，其他逻辑跟 Virtuoso 类似，将 cv 替换成 `ae.ae.dbOpenCVByType`
4. U#171：测试 `CADTest dlyg2GSs1_gutb`
5. U#189：修 bug——应 `ae.dbOpenCVByType` 输入 libName/cellName，不是下层的 inv

## pyAether API 表面（助手经 search_apis/get_api_details + SandBox MCP 探针验证）

- `ae.emyInitAether("-adv")` — 初始化
- `ae.dbOpenCVByType(lib, cell, view, viewType="schematic", mode="a")` — 开 cellview（append 写权限）
- `ae.emyDesignIsSchematic(design)` — 校验是 schematic 视图
- `ae.aeGetCurDesign()` / `design.getBlock()` — 取当前设计/block
- `ae.emyBoxF(l,b,r,t)` — bbox 构造；属性 `.l/.b/.r/.t`；方法 `.lowerLeft()/.upperRight()` 返回 `emyPointF`；`.merge(other)` 原地合并；`.hasNoArea()`；`.getWidth()/.getHeight()`
- `ae.emyPointF(x,y)` — 点；方法 `.x()/.y()`
- `ae.dbCrtRect3X(design, layer, box)` — 在指定层画矩形
- `ae.aeCreateNoteText(design, text, point, height=0.0625, font="stick", ...)` — 放 note text
- `ae.addProp(fig, True, "InnoBndy")` — 加属性标记
- `ae.etGetLogin()` — 取登录名
- `ae.aeEnableUndo()` / `ae.dbIsValidBBox(box)` / `ae.aeChangeCellView(design)`
- 层名：`hardFence`（边界）/ `instance`（instance 矩形）
- grid = 0.0625
- block 遍历：`block.getShapes()`（`shape.pin`/`shape.bbox`）/`block.getPins()`（`pin.bbox`）/`block.getInsts()`（`inst.bbox`）
- helper（替换 Lisp car/xCoord/yCoord）：`_car/_xCoord/_yCoord/_lowerLeft/_upperRight/_cons`

## 落地脚本结构（A#95/A#126 editor 写入）

`innoCreateSchBndry.py`：
- `innoCheckSchematic(design)` — emyDesignIsSchematic 校验
- `innoGetLogin()` — etGetLogin
- `innoCollectPinBBoxes(block)` — 收集 pin bbox（getShapes+getPins）
- `innoCreateSchBndry(instAlso)` — 主函数，对 aeGetCurDesign 当前设计：收集 inst+pin bbox → merge → margin → grid-snap → dbCrtRect3X(hardFence) → 可选 dbCrtRect3X(instance) → aeCreateNoteText + addProp(InnoBndy) → design.save()
- `innoCreateSchBndryForLCV(lib, cell, view, instAlso)` — 包装：dbOpenCVByType(mode=a) → aeChangeCellView → 调 #1
- `innoCreateSchBndrySimple(lib, cell, view)` — alias(instAlso=True)

trace 后段（U#171 之后）陷于 cell 打开权限/lib 可见性排障（CADTest 库在 pyAether SandBox 不可见、emyDMGetOpenLibs/aeCphGetLibList 试探），不合成。

## case 合成（synthesized-reframe）

把「移植到 Aether + 真实打开 cellview 跑」（强依赖 Aether DB）reframe 为 **spec-JSON 驱动操作序列 + 脚本生成器** `gen_sch_boundary(spec) -> report`——纯 Python 结构化判分，无真实 EDA 二进制依赖。

- task_id: SchBoundaryGenProduce-001
- domain: schematic_netlist
- judge_layers: [L0, L1]（LIVE-NA：deliverable=Python 脚本产 ops_log+script_text，check 解析+独立复算 bbox/grid-snap，无真实 EDA 工具二进制依赖；Aether 不在 .75 不强求 L2.live）
- spec schema: `{lib, cell, view, layer, inst_layer, grid, margin, inst_also, note_text, init_flag, instances[{name,cell,x,y,w,h}], pin_shapes[{net,bbox:[l,b,r,t]}]}`
- A(visible) spec_A.json: CADTest/dlyg2GSs1_gutb/schematic, layer=hardFence, inst_layer=instance, grid=0.0625, margin=0.5, inst_also=true, note_text=bndry_taodu, 3 instances(I0 invx1/I1 nand2x1/I2 bufx1), 3 pin_shapes(vdd/gnd/out)
- hidden B spec_B.json: AnalogCore/amp_top_v2/schematic, layer=softFence, grid=0.125, margin=1.0, inst_also=false, note_text=bndry_e005, 5 instances(U0-U4 pmos/nmos/cap), 5 pin_shapes(VDDA/GNDA/INP/INN/OUT) — token-structurally 全不同 ⇒ A 硬编码器在 B 全错
- reference `gen_sch_boundary_ref.py` spec 驱动通用实现（_validate 必填+malformed raise → _snap round(v/grid)*grid → _merge_bboxes → raw_bbox(inst+pin) → margin → gridSnap=boundary_bbox → inst_bbox(仅 inst, 无 margin) → ops_log 15 步 init..close → _build_script_text 含 5 API token）
- check.py 14 conds(a-n)：独立复算 boundary_bbox/inst_bbox 再断言
- LIVE-NA, 14 conds, 5 negs distinct first-fail {c,d,f,j,m}
