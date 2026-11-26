# trace_deepread r637 — miccao / a8164 / LvsGuiParamExtract-001

- **session**: `1792982722079_a8164.messages.json`
- **user/host**: miccao @ hfeg0plg37 (IP 10.129.32.47)
- **mc**: 60 (lvs:845;aether:80;schematic:62;netlist:44;techfile:39 dominant — physical_verify)
- **size**: 27 msgs / 1 real user turn / single-turn Q&A
- **date**: 2026-11-16 (peeked r637)

## 用户原话 (U#0, 逐字)

```
/apps/imctf/cad/init/settings_aether/python_ae/le/CXMTleThreeDLVS_gui.py 这个脚本需要提供哪些参数
```

## 真实意图

miccao 拿到一个 2307 行的 PyQt5 GUI 脚本（Argus 3D LVS 规则 deck 生成工具），想知道运行它需要提供哪些参数。这是典型的 **script-param Q&A**——旧规则下会被判 "analysis-Q&A thin no produce-task weak" REJECT，但 2026-11-15 新标准下这是合法用户意图。

## agent 工具链

1. `read_files` 读 CXMTleThreeDLVS_gui.py 全文（2307 行，分 4 段）
2. `search_codebase` / `run_commands` grep 找 `__main__`/`sys.argv`/`ArgumentParser`/`def main`
3. 发现：脚本入口 `emyArgusRun3DLVSMainCode()` **不接受任何命令行参数**，只是弹出 PyQt5 GUI；"参数" = GUI/配置文件中填写的字段
4. 提取 `configMap`（line 1086-1095）4 组参数清单
5. 提取 GUI 控件（QLineEdit/QSpinBox/QCheckBox）及其 `_translate` 标签
6. 提取 `argus3DLVSMainCB`（line 2113）里的必填校验

## gold (agent 最终结论, M#26)

**脚本不需要命令行参数**，入口 `emyArgusRun3DLVSMainCode()` 弹 GUI，参数在界面填写，分 4 组（configMap）：

| 组 | 参数数 | 参数 |
|---|--:|---|
| System Options | 9 | System Source, Source Top, 3D Port Layer, Placement, Ignore Top Port, Bump Number, PVRS Rules, Run Directory, CPU Number |
| Chip Options | 12 | Chip Name, Layout Path, Layout Format, Layout Top, Source Path, Source Format, Source Top, Hcell, LVS Rule Path, Lcv Layout, Lcv Schematic, Other params |
| Interface | 8 | Main Instance Name, Instance Name, Master Name, Location, Magnify, Rotate, X-axis Mirror, Y-axis Mirror |
| Connectivity | 3 | Connectivity Name, Instance Name, Layer |

GUI 控件：systemSourceNetlistLineEdit(QLineEdit,"System Source Netlist")、sourceTopCellLineEdit(QLineEdit,"Source Top Cell")、threeDPortLayCB(QCheckBox, default Checked)、ignTopPortCB(QCheckBox, default Unchecked)、bumpNumberLineEdit(QLineEdit,"Bump Number")、runCpuNumSB(QSpinBox, value=64 min=1 max=100)、runDirLE(QLineEdit,"Run Directory")、interfaceNameLE(QLineEdit,"3DStack Name") 等。

入口：`emyArgusRun3DLVSMainCode()`（line 2291）。窗口标题：`'Argus 3DLVS - v2.0'`。

必填校验（argus3DLVSMainCB）：System Source Netlist 文件须存在、Source Top Cell 非空、每 die 的 Layout Path/Source Path/LVS Rule Path 非空。

## case 合成（B档 mock-behavioral grounded-extraction-tool reframe）

承 r617 TvfSetlayerExpl / r630 LvsHcellFailReportExtract / r631 LvsDeckErcStatusCheck / r633 MaskBlkSvrfWriteExtract / r635 PgSvrfRuleAnalyze 模式。deliverable=`lvs_gui_param_extractor.py <script.py> <output.json>` 解析 PyQt5 GUI 脚本→结构化 JSON{config_groups/gui_fields/entry_point/window_title/total_groups/total_widgets/total_params}。

- **asset A** = `script_a.py`（真实脚本精简摘录，configMap 4 组/17 控件/CPU 64/3D Port Layer Checked/entry emyArgusRun3DLVSMainCode/title 'Argus 3DLVS - v2.0'）
- **隐藏 B** = `script_b.py`（变体：3 组 Top Options/Die Setup/Connection 23 参数/entry run3DLVSGui/title 'Argus 3D LVS GUI - v3.1'/CPU 16 max 32/portLayerCB Checked）
- **隐藏 B2** = `script_b2.py`（反硬编变体：4 组 System/Chip/Interface/Connectivity 32 参数/entry launch3DLVS/title '3D LVS Tool - v1.5'/CPU 8 max 64/topPortIgnCB Checked）

21 条 a-u 断言；ref 21/21 PASS；3 neg + §4.9 三假全 FAIL。

## 选料上下文

fresh-pool mid-mc(25-60) 选料。本轮 peek 12 候选全 REJECT（env-recon/Q&A/skill-orch/ops/D-domain/run-existing），a8164 是第 13 个 peek，miccao 已知作者（r620/r624/r636 三连交付）的新 session，single-turn script-param Q&A 经 grounded-extraction-tool reframe 落地。证明 fresh mid-mc 段经 reframe 仍有 clean C-domain 命中。
