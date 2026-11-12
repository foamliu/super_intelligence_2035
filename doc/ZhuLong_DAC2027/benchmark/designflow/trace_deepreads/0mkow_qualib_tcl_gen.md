# trace_deepread: 0mkow — Qualib TCL template generation (yixiaow)

- **session**: `1792474615638_0mkow` / yixiaow / 10.129.2.14 / mc26
- **keywords**: verilog:78; .lef:44; netlist:27; .gds:26; .cdl:13; lvs:4 (top=verilog)
- **file**: `/home/yixiaow/.cline/data/sessions/1792474615638_0mkow.messages.json` (163 KB, 51 msgs, 4 real user turns)
- **agent**: deepseek-v4-flash (lead), invoked `qualib-tcl-generator` skill

## User turns (A-faithful produce-task)
- U#1 `qualib tcl` — triggers qualib-tcl-generator skill
- U#2 `生成一个检查STD的tcl文件` — generate a TCL file to check STD (standard-cell library)
- U#3 `我就检查TT corner 电压1.8v 温度常温25度` — single corner TT/1.8V/25°C
- U#4 `全部编一个，我就要个模板` — compile all sections, just want a template

User gives the **spec** (IP=STD, check=inspect, corner=TT/1.8V/25°C, "want a template") but NOT the implementation → **A-faithful produce-task 合格**.

## Agent work
- `skills` invoke qualib-tcl-generator → `ask_question` for details → user supplies minimal spec
- `editor` ×~10 writing `/home/yixiaow/qualib_std_check.tcl` (179 lines, 13 sections)
- file had "ordering issues / duplicate sections due to incremental insertions" → agent `rm` + rewrite + `read_files` ×several to clean up
- final deliverable: `qualib_std_check.tcl` — a Qualib TCL inspection template

## Deliverable structure (13 sections)
1. create_workspace + create_session(-vendor -version)
2. create_corner(-process -voltage -temperature) + set_reference_corner
3. link_library -view tmlib (.lib)
4. link_library -view lef (tech + cells)
5. link_library -view gds
6-7. verilog / cdl (commented `#` placeholders — null in this spec)
8. set_power_pin_name / set_ground_pin_name
9-10. GDS label/boundary (commented)
11. set_parameter (tmlib_timing_arc_definition, tmlib_sequential_delay_definition, table_sampling_method, evaluation_principle)
12. check_library_information + inspect
13. export_report (html + text)

## B档 synthesis rationale
Agent produced a **static TCL file** for one specific spec (STD/TT/1.8V/25°C), not a reusable generator. To test per-spec generation (hidden B with different IP/corner/views/params), the deliverable must be **parameterized** → synthesize `gen_qualib_tcl.py` (reads spec JSON → emits TCL template). Demand (Qualib TCL template generation) fully traceable.

**TFC (trace-faithfulness coverage)** = 6/6 = 100%:
1. workspace/session creation ← U#2 + agent create_workspace/session
2. corner with P/V/T ← U#3 "TT corner 电压1.8v 温度25度" + agent create_corner
3. library linking (tmlib/lef/gds/verilog/cdl) ← agent link_library sections + keywords (.lef/.gds/.cdl)
4. power/ground pin names ← agent set_power_pin_name section
5. set_parameter (4 params) ← agent section 11 (11a-11d)
6. inspect + export_report ← U#2 "检查STD" + agent section 12/13

## Case
**EDA-Eval-DesignFlow-QualibTclGen-001** (eda_other L1 spec-driven code generator, B档, k=16)
- deliverable = `gen_qualib_tcl.py` (stdlib, reads spec JSON → emits Qualib TCL template)
- A = spec_A.json (STD/inspect/TT/1.8V/25°C, verilog+cdl null)
- B = hidden spec_B.json (IO/xcheck/SS/1.2V/-40°C, verilog enabled, cdl null, different params/pins/report)
- 16 conditions (a-p): zip+compile+run / workspace / session / corner PVT / reference_corner / tmlib / lef tech+cells / verilog-active / cdl-commented / power+ground pins / 4 params / check_type verb / export_report / cross-input guard
