# 深读笔记 · 1793845474118_uno3l · ethan5c @ hfeg0pkn005 · mc=115 · layout_aether

**trace_source**: user=ethan5c, host=hfeg0pkn005 (10.129.2.14), session_file=1793845474118_uno3l.messages.json, match_count=115, keywords=pyaether:228;aether:140;cellview:123;rtl:75;transistor:53;drc:47;.gds:47;schematic:32; tools=102 pyAether 31 schematic 20 pyAether-lang 14 dbGet 9 cellview 6 calibre 4 netlist 3 dbCreateInst 1 dbCreateRect
**real_task_summary**: 用户 ethan5c（NEW user）要求"生成一个由 1 个 NMOS 和 1 个 PMOS 组成的反相器版图，以 gds 格式保存到 /home/ethan5c/Prj/ZL_test/case1"。assistant 调 eda_agent skill → 读 pyAether skill 文档（01_foundation/04_case_studies）→ 搜 pyAether API（dbNewCellView/dbGdsOut/aeExportStream/aeCreateRect/leGuiCrtTransistor/aeCreateLabel/aeLeCreatePin/aeSaveDesign/emyInitAether）→ 在 SandBox 跑 `import pyAether` 发现 pyAether sandbox 未运行 → 改用 **gdspy 1.6.13**（本机 Python GDS 库）直接生成 → 写 gen_inverter_gds.py（8652 字节）→ 生成 inverter.gds（1994 字节）→ 写 verify_gds.py 反读校验 → 多次修 Label API 属性名 bug（label.x→label.origin[0]→最终用 label 坐标）→ 校验通过（cell INV，8 层多边形 + 6 labels）→ 给最终总结。

## 对话流（108 msgs：63 user / 54 assistant — 含 tool_result）
- **msg[0] USER（act）**：「帮我生成一个由1个NMOS和1个PMOS组成的反相器版图，该版图以gds格式保存在/home/ethan5c/Prj/ZL_test/case1 目录下面」← **提出需求 / 表达目标**轮，eligible for A-档候选
- msg[1] assistant：调 `skills(eda_agent, "generate inverter layout gds")` + list_allowed_files(case1) → 空目录
- msg[4-7]：读 pyAether skill 文档（overview / case_studies），search_codebase（createCell/gdsExport/inverter/createInst）
- msg[10-32]：搜 pyAether API：createCellView / gdsExport / createInstance / mos transistor / rectangle / pin / label / save / openDesign / emyInitAether / dbCrtRect / dbCrtLabel / dbCrtPin / dbCrtNet / contact via cut / dbOpenCV
- msg[35]：run_commands（whoami / ls case1 / cat cds.lib）+ SandBox run_code `import pyAether` → **pyAether 不可用**
- msg[38-44]：check_gdspy.py 探测 → gdspy 1.6.13 available
- **msg[46] assistant 关键决策**：「pyAether sandbox is not running, so I'll use **gdspy** to generate the inverter layout GDS directly」→ 转 L1（纯 Python gdspy）
- msg[46-77]：editor 写 gen_inverter_gds.py（多次追加：tech params → 坐标 → contacts → metal routing → labels → GDS write）→ run_approved_command 跑生成
- msg[79-105]：写 verify_gds.py 反读校验；3 次 Label API bug（label.x 不存在 → label.origin 不存在 → 最终用兼容写法）；msg[104] **status=completed**，输出：
  ```
  Cell: INV
  Layer (1,0): 1  (2,0): 1  (3,0): 1  (4,0): 1  (5,0): 1  (6,0): 1  (7,0): 9  (8,0): 8
  Labels (6) on layer 10:
    'VDD' @ (0.00, 5.75)  'VSS' @ (0.00, -5.75)
    'Vin' @ (-3.70, 4.50)  'Vout' @ (3.20, 0.00)
    'PMOS(W=4u L=0.5u)' @ (0.50, 5.30)  'NMOS(W=2u L=0.5u)' @ (0.50, -5.30)
  OK!
  ```
- msg[106]：list_allowed_files → 产物：check_gdspy.py / gen_inverter_gds.py / inverter.gds / verify_gds.py
- msg[107] assistant：最终总结「✅ 反相器版图 GDS 生成完成」，inverter.gds (1.9 KB) + gen_inverter_gds.py
- **trace 末尾无用户明确接受（msg[107] 是最后一条，assistant 总结后无 user 回复）**→ 不适用 A-档，取 **B-synthesized**

## 真实产物（已 scp 到 workdir 核对）
- **gen_inverter_gds.py**（8652 字节，真实参考解）：layer map = NW(1)/ND(2)/PD(3)/PO(4)/NS(5)/PS(6)/CO(7)/M1(8)/TXT(10)；LAMBDA=0.25um；NMOS W=2.0 L=0.5（diff -1..1 × -3.5..-1.5），PMOS W=4.0 L=0.5（diff -2..2 × 1.5..3.5）；共享垂直 poly gate @ x=0（宽 0.5um，y 跨两 diffusion ±POLY_EXT）；9 contacts（4 PMOS src/drn + 4 NMOS src/drn + 1 poly）；M1 routing：VDD rail(top y=4.75) + VSS rail(bot y=-4.75) + Vout(right x=2.0) + Vin(to poly) + 4 source straps；6 labels on layer 10
- **inverter.gds**（1994 字节，gold artifact）：cell INV；layer (1,0)=1 (2,0)=1 (3,0)=1 (4,0)=1 (5,0)=1 (6,0)=1 (7,0)=9 (8,0)=8 polygons；6 labels on (10,0)

## 合成方向（B-档 synthesized, L1-boundary, layout_aether）
**任务**：SUT 写 config-driven 的 Python gdspy 生成器 `gen_inverter_gds.py`（CLI 1 参 <config.json>），按 config 的 cell_name / NMOS/PMOS W&L / layer_map / labels / output_gds 生成 CMOS 反相器版图 GDS（PMOS 上 / NMOS 下 / 共享 poly / contacts / M1 rails+straps / text labels）。交付 `outputs/submit.zip`（含 gen 脚本 + 生成的 GDS）。
**隐藏 B**：cell_name='INV_B' / NMOS W=3.0 L=0.4 / PMOS W=6.0 L=0.4 / layer_map 全错位(11-18,20) / labels=VCC/GND/IN/OUT / output_gds='inv_b.gds' → 强制 config-driven，硬编码 A 值的解必 FAIL。
**判分**：check.py 用 gdspy 反读 B 的 GDS，按 B config 验结构（cell 名 / 8 层齐全 / 各层 polygon 计数 / diffusion bbox 与 W/L / poly gate 长度 / contact ≥9 / M1 ≥8 / nwell 覆盖 PMOS 不覆盖 NMOS / VDD label y>0 VSS y<0 / labels 齐全）≥8 独立条件。
**DISTINCT**：既有 layout_aether case 多为 audit/find/check 既有版图（HierCellPatternFind r199 / CentroidPlace r201 / AntPattern r202 / DupVia r206 / QaWidth r207 / NoOverlap r211），本案首次 ground on **从零生成 CMOS 反相器版图 GDS（gdspy 参数化）**，主题互补不重叠。与 r206 DupVia（gdspy+calibre LVS 连通性校验）工具栈近但任务相反（生成 vs 校验）。
