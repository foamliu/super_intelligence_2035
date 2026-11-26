# Deepread — t9g3z (lizwen / 10.129.2.12 / mc=22) — DNW pattern 生成

**Session**: `1790219742335_t9g3z`，user lizwen，host 10.129.2.11（lizwen home 在 .11 上也可读），cwd `/home/lizwen`，model glm-5.2，status `failed` exit_code 1，2026-09-24 03:15→06:14 UTC。文件 `t9g3z.messages.json` 122KB / 17 msgs (4 user-text + 4 assistant + 9 tool_result)。

## 用户真实意图

仅一条用户文本输入（U#0，逐字原文）：
> `DNW*产生pattern`

无后续用户文本（U#2..U#16 全是 tool_result）。session 在 assistant 仍处于 API 探索阶段时 failed 结束，**未交付脚本**。意图清晰：用 pyAether 生成 DNW（Deep N-Well，深 N 阱，CMOS 隔离层）的 layout pattern——即在 layout cellview 的 DNW 层上画一组矩形/图形（pattern），可能含 guard ring。

## assistant 工具链（仅 API 检索，无 editor/run 落地）

4 轮 assistant（A#1/A#5/A#9/A#13），全部是 `RAG_MCP_Server__search_apis` + `RAG_MCP_Server__get_api_details` + `search_codebase`，**无 run_commands/editor**，未生成任何脚本文件。检索揭示的 pyAether API 面（DNW pattern 生成的真实工具集）：

| API | 作用 | trace 出处 |
|---|---|---|
| `aeCreateRect(point=emyBoxF(x1,y1,x2,y2), layerName, purpose)` | 在当前 drawing area 画矩形（DNW 图形） | U#6/U#10 详情 |
| `aeSetActiveLayer` / `aeGetEntryLayerPurpose` / `aeIsValidLayerPurpose` | 设置/取/校验当前层（DNW 层） | U#12 |
| `aeCrtGuardring(cv, centerLine, templateName, type, justify, offset, ...)` | 创建 guard ring（DNW 常作隔离 guard ring） | U#11/U#14 详情 |
| `aeCrtLdmosLayout` | 生成 PowerMos layout（LDMOS 用 DNW） | U#7 |
| `dbCrtRect` / `dbCrtPolygon` | db 层图形创建 | U#6/U#8 |
| `techFindLayer` | 按名查层对象 | U#7 |
| `aeLeRepeatMoveCopyStretch` / `dbCreateViaShapeArray` / `leGuiRepeatCopy` | 重复/阵列拷贝（pattern 阵列化） | U#16 |
| `emyBoxF(x1,y1,x2,y2)` | 矩形坐标定义 | U#10 |

assistant thinking 明确识别：`DNW` = Deep N-Well，`pattern` = 在 DNW 层上画一组矩形/图形。

## 判定

- **真实用户意图** ✓：layout_aether 域，pyaether:341 keyword 主导，"DNW 产生 pattern" 是真实的版图生成任务（深 N 阱隔离层图形化）。trace_source 可溯源（user/session_file/host/mc 齐全）。
- **trace 偏薄**：单轮用户输入、session failed、无最终脚本。但意图清晰 + API 面充分，足以做 **档 B reframe**。
- **档 B reframe 必要性**：A 档 gold = pyAether 脚本（aeOpenDesign + aeCreateRect + aeCrtGuardring），需 live Aether session，沙盒不可跑 → 无 subprocess 牙；且 trace 根本没产出脚本。reframe = 抽离「DNW pattern 生成」算法核心（给定 cellview bbox + DNW 层 + pattern 参数 [grid/stripe, rows/cols, rect 尺寸, spacing, offset, 可选 guard ring] → 计算 DNW 矩形坐标 + guard ring + stats + 校验）成纯 stdlib `dnw_pattern_gen.py`（CLI `<spec.json> <out.json>`，sort_keys 确定性）。这承袭 r816 AnalogMatchLayoutGen / r819 V4PadGen 的 layout 生成器 reframe 范式。
- **意图审计**：keep — "DNW 产生 pattern" 是真实 layout_aether 用户意图（生成类，非 explain/Q&A），2026-11-15 §二 reaudit 下生成任务本就合法；reframe 捕获「DNW 层矩形阵列 + guard ring 边框 + bbox 校验 + 层合法性」算法核心。

## case 落库

`EDA-Eval-DesignFlow-DnwPatternGen-001`（layout_aether, L1, 档 B, k_check=16, 子型 `pyaether-dnw-deep-nwell-pattern-generator`）。visible A = grid 2×3 + guard ring（DNW/drawing）；hidden B = stripe vertical 5×1 + guard ring（DN/boundary）—— pattern_type/层名/purpose/尺寸/数量全不同 anti-hardcode。
