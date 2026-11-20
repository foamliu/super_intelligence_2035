# 5fjwc deepread — schematic pin-add (colinxu@hfeg0plg55, mc=102)

- session: 1792563529955_5fjwc, colinxu@hfeg0plg55=10.129.35.74, mc=102
- keywords: cellview:127/schematic:118/pyAether:102/dbopencv:63/aether:37/dbget:36/analog:31/drc:28
- domain: D-pure schematic_netlist (schematic/cellview/dbopencv dominant)
- fetch: path-bug revival r971 — flat path `~/.cline/data/sessions/<id>.messages.json` = NOFILE (D263-peek 误判 parked); 子目录 path `~/.cline/data/sessions/<id>/<id>.messages.json` = 162,647 B 可读 ✓
- msgs: 63, user_inputs: 1 unique (U#0=U#1 verbatim 重复)

## U#0 (idx=0, verbatim A-faithful 原话)

> 帮我在drcqa_analog lib - AG_AmpsUpBankFar cell - schematic_1021 view内添加一个TESTPIN这个pin

## assistant 工具链 (L2 真跑 pyAether 沙盒)

1. RAG search_apis: "create a pin in schematic view" → symGuiCreatePin / dbCreateSchPinEx / dbSchDrawSymbolPin
2. get_api_details: dbCreateSchPinEx, dbSchDrawSymbolPin, dbOpenCV, aeGetCurDesign, dbSchGetPinOrder
3. SandBox run_code: dbOpenCV(drcqa_analog/AG_AmpsUpBankFar/schematic_1021, mode='a', viewType='schematic') → cv OK; dbSchGetPinOrder → 30 pin names
4. 探索现有 pin 结构: cv.terminals (tuple of 30), t.name/t.direction, t.pins[0].figs[0].libName/cellName/viewName
5. **关键发现 (master convention)**: 现有 input pin master=`basic in symbol`, output=`basic out symbol`, inputOutput=`basic io symbol` → sym_map = {input:in, output:out, inputOutput:io}
6. 探索 pin fig 位置: VblhSFREn_W origin (0.0625,15.4375) bbox ... orient R0
7. **创建 TESTPIN** (idx=50):
   - master = dbOpenCV(lib='basic', cell='in', view='symbol', mode='r')
   - p = dbCreateSchPinEx(cv, master, 'TESTPIN', 'input', (0.0625, 16.0625))
   - 结果: terms 30→31, TESTPIN present=True
8. **反向验证** (idx=52): TESTPIN term found, direction=input, net.name=TESTPIN, master=basic in symbol, origin=(0.0625,16.0625), orient=R0, netCount=61, cv.save()=saved OK
9. 交付 add_test_pin.py (idx=54 editor): 通用函数 add_test_pin(lib, cell, view, pin_name='TESTPIN', direction='input', point) with sym_map + dbCreateSchPinEx + reverse verify + save
10. 最终确认 (idx=59): termCount=31, TESTPIN terminals=1, dir=input, net=TESTPIN, master=basic in symbol, origin=(0.0625,16.0625)

## GOLD (用户实际接受的结果, idx=53/59/62)

- termCount: 30 → 31 (exactly +1)
- TESTPIN terminal: 存在且唯一 (count=1)
- direction: input
- net name: TESTPIN (== pin_name)
- master symbol: basic/in/symbol (sym_map input→in)
- origin: (0.0625, 16.0625), orient R0
- design saved (cv.save() OK)
- 交付物: add_test_pin.py (通用函数定义)

## 判读

- **真实意图**: 在指定 schematic cellview 内添加一个具名 pin (D 域 schematic 操作, L2 真跑 pyAether)
- **可造性**: ✓ clean falsifiable — gold 有明确数值/结构断言 (termCount+1, terminal 唯一, direction, net==name, master sym_map, save)
- **reframe (B档 synthesized produce)**: SUT 产出一个通用 pyAether 脚本 add_schematic_pin.py (定义 add_schematic_pin(lib,cell,view,pin_name,direction,point) 遵循 basic-lib master convention) + report.json; check 在 mock pyAether harness 上跑隐藏 B (不同 lib/cell/view/pin/direction) 验证 recorded ops 结构
- **anti-hardcode**: B 用与 A 完全不同的 lib/cell/view/pin_name/direction (含 output/inputOutput → out/io), 硬编码 A 的 TESTPIN/drcqa_analog/input 会在 B 上 FAIL
- **harness for teeth**: mock_pyAether 记录 dbOpenCV/dbCreateSchPinEx/save 调用 + 维护 fake cv.terminals/termCount/net, check 逐字段比对 recorded ops vs B 期望
- 2nd-case-same-user: colinxu 已有 r970 fz05e case, 本 case 不同 session 不同 task (schematic pin-add vs ndjson scanner), 允许 (jjrak precedent r937/r939)
