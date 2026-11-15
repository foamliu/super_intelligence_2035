# trace_deepread: a8164 — ScriptParamExplainQA-001

## 来源
- session: `1792982722079_a8164`
- user: `miccao`
- host: `hfeg0pkn004 (10.129.32.47)`
- match_count: 60
- domain: schematic_netlist
- 真实路径: `/apps/imctf/cad/init/settings_aether/python_ae/le/CXMTleThreeDLVS_gui.py` (2307 行, PyQt5 GUI)

## verbatim U#0 (逐字原话)
```
/apps/imctf/cad/init/settings_aether/python_ae/le/CXMTleThreeDLVS_gui.py 这个脚本需要提供哪些参数
```

## trace 上下文
- 1 substantive user turn (U#0 提问)。
- 助手 read_files 分段读完整 2307 行（MSG#1-25），最终产结构化回答（MSG#26）：
  - 脚本本身**不需要任何命令行参数**，是 PyQt5 GUI 工具（Argus 3DLVS）
  - 入口函数 `emyArgusRun3DLVSMainCode()`（无参），在 Aether DM 中调用
  - 参数通过 GUI/配置文件填写，分 4 组（configMap）：
    1. **System Options**: System Source / Source Top / 3D Port Layer / Placement / Ignore Top Port / Bump Number / PVRS Rules / Run Directory / CPU Number
    2. **Chip Options** (per-die): Chip Name / Layout Path / Layout Format / Layout Top / Source Path / Source Format / Source Top / Hcell / LVS Rule Path / Lcv Layout / Lcv Schematic / Other params
    3. **Interface**: Main Instance Name / Instance Name / Master Name / Location / Magnify / Rotate / X-axis Mirror / Y-axis Mirror
    4. **Connectivity**: Connectivity Name / Instance Name / Layer
  - 系统选项中 Source CDL 路径会被 `argus3DLVSMainCB` 校验 `os.path.isfile`；Chip Options 中 layout/layTop/source/cdlTop/lvs_rule 会被 `argus3DLVSAddDieCB` 校验

## case 设计
- **pattern**: #254 v2 code-grounded answer-extraction reframe（同族 vwgeo GenRunFuncExplainQA-001 function-explain / 636qr refactoring-summary / i33cs script-catalog，本例=script-param-explain sub-type）
- **reframe**: 用户意图=问"需要哪些参数"，design_flow 契约需在隐藏 B 上跑候选 → reframing 成 code-grounded script-param-explain tool（读脚本源码+问题→结构化 JSON: question/script_summary/entry_point/is_gui/has_cli_args/parameter_groups[{name,param_count,params[{name,group,type,required,default,description,cited_identifiers}]}]/cited_identifiers/overall_assessment）
- **grounding**: cited_identifiers 必须 grounded 于真实源码（函数名/类名/configMap 键/LineEdit/CheckBox/SpinBox 控件名/argparse flags）
- **data-driven 2×2+degenerate**:
  - A: Argus 3DLVS PyQt5 GUI, 4 groups (System Options/Chip Options/Interface/Connectivity), entry emyArgusRun3DLVSMainCode
  - B1: StarExpoGui PyQt5 GUI (中性命名), 3 groups (Run Control/Netlist/Output), entry starExpoMainEntry
  - B2: CalDfmRptGen CLI argparse (中性命名), 2 groups (Input/Report), entry main
  - B3: simple_counter trivial (无 GUI/无参数), 优雅降级 parameter_groups=[]
- **反硬编码**: A 专属标识符 (emyArgusRun3DLVSMainCode / EmyArgus3DLVSGuiMainCls / argus3DLVSMainCB / Argus / 3DLVS / PVRS / systemSourceNetlistLineEdit / dieChipNameLE 等) 不泄入 B1/B2/B3 输出

## 源可达性
- `/apps/imctf/cad/init/settings_aether/python_ae/le/CXMTleThreeDLVS_gui.py` 对 e0031982 world-readable (sosadmin:sosadmin 0644)
- 完整源码 scp 到 .75 workdir 后提取 focused subset 作 script_A.py（~240 行保留真实标识符 + 结构）

## 判分
- check.py: 15 条独立条件 a-o
- 自验: REF PASS 15/15 ✓ / NEG 3/3 全 FAIL (neg1→e 硬编码A泄漏 / neg2→d stub空 / neg3→c 无合法JSON) ✓ / §4.9 退化 (empty→a / garbage→b / print-only→c) 全 FAIL ✓
- k_rationale == k_check == 15 ≥ 8 ✓
- test field == disk check.py ✓

## 交付记录
- r738: 造题轮，1 case 落库 EDA-Eval-DesignFlow-ScriptParamExplainQA-001 (schematic_netlist, k=15)
- 台账: mark 1792982722079_a8164 → case
- pool_reaudit: a8164 行标 DELIVERED r738
