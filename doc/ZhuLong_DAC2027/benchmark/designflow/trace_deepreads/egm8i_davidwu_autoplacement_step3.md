# deepread: egm8i — davidwu — aeAutoPlacementFromDesign Step3 (pg_layout/floorplan)

- session: `1789975385741_egm8i` (messages.json, 332KB, 99 msgs)
- user: davidwu @ hfeg0pkn004 (10.129.2.13) [also hfeg0pgn019/10.129.35.118, hfeg0pjn200/10.129.40.209]
- mc=98, keywords: aether:704; schematic:283; pyaether:126; floorplan:124; dbopencv:78; drc:47; verilog:19; cmos:18
- agent: lead, deepseek-v4-flash, cwd `/proj/train/V0_fillimplant_drgqa/workdir/davidwu`
- status: idle (job still running at end per U#57)
- 台账: was parked in shard D ("weak/non-D-domain/debug/skill-invoke") — **误判**, 实为 C 域 pg_layout flow-driving; r1027 force-claim 到 C

## 真实任务 (58 user_input, 核心 3 条)

- **U#0 (主任务)**: 「帮我将打开的电路 test3/AF_PPRCntEnd floorplan view 完成布局。请使用 script/data/placementConfig_v13.json 文件执行 step 3 aeAutoPlacementFromDesign.」
- **U#7 (skill 说明)**: 用户提供 pyAether Automatic-Place-Route 编排 skill 文档，6 步工作流 (Step1 init env / Step2 gen config / Step3 aeAutoPlacementFromDesign / Step4 RouteBaseOptions 17项 / Step5 RouteNetOptions 7项 / Step6 ...)。用户只要 Step 3。
- **U#55/56**: 「继续」
- **U#57**: 「job还在执行吗？」

## agent 工具链 (主线)

1. `skills` ae-auto-placement-from-design + `list_allowed_files` 探 /home/davidwu
2. `run_commands` find test3 / placementConfig_v13.json / script dir
3. `RAG get_api_details` [aeAutoPlacementFromDesign, dbOpenCV, openDesign, aeGetCurDesign]
4. `list_allowed_files` /home/davidwu/test3, /home/davidwu/script (不存在)
5. `search_codebase` placementConfig_v13.json / test3.*AF_PPRCntEnd
6. 发现 `/home/davidwu/.cline/scripts/data/placementConfig_v13.json` + 已有 `step3_aeAutoPlacementFromDesign.py` + `run_step3_placement.sh`
7. `read_files` 读取 config + 现有 step3 脚本 + shell wrapper
8. `run_approved_command` (shell-runner) 跑 run_step3_placement.sh → **SEGV** (Qt could not connect to display)
9. `editor` 改 wrapper 加 `QT_QPA_PLATFORM=offscreen` → 仍 SEGV
10. `editor` 写 find_display.sh 查 running Aether 进程 / DISPLAY / X sockets → 无 X display
11. `editor` 写 check_display_tools.sh 查 Xvfb → 无 Xvfb
12. `editor` 写 inspect_pythone.sh 查 pythone wrapper 的 batch/nograph 选项 + `RAG search_apis` emyInitAether batch mode
13. `RAG get_api_details` [emyInitAether, aeIpcBatchProcess, aeIpcActivateBatch]
14. `editor` 写 inspect_pythone2.sh 看 pythone wrapper case 段 + `editor` 写 find_xvfb.sh (find /apps 超时)
15. `editor` 写 quick_find_xvfb.sh → **关键发现**: `DISPLAY=:99` + `QT_QPA_PLATFORM=offscreen` 让 `pythone -c "print('hello')"` 成功
16. `editor` 改 wrapper 加 DISPLAY=:99 → 跑 → 仍 SEGV (因为脚本调 `emyInitAether('-adv')`)
17. `editor` 写 test_eminit.sh → 确认 `emyInitAether('-adv')` 是崩溃点 (需真实 X display), 但 `import pyAether` 本身成功
18. `editor` 写 test_no_eminit.sh (跳过 emyInitAether, 直接 dbOpenCV/openDesign) → 成功打开 schematic+floorplan, 但 `aeAutoPlacementFromDesign` 返回 False: **"No SDL relationship between schDesign and leDesign!"**
19. `RAG get_api_details` [dbSdlMapSchematic2Layout, aeFindSDLSchematicForLayout, aeAddDesignMapping] + `RAG search_apis` SDL mapping
20. `editor` 写 step3_place_final.sh + step3_place_final.py: 打开 schematic (dbOpenCV) + 打开 floorplan (aeGetCurDesign/openDesign) + **建立 SDL 映射 (aeAddDesignMapping)** + 调 `aeAutoPlacementFromDesign(le, se, config)` + 保存
21. `read_files` 验证脚本 + `run_approved_command` 跑

## 关键产物

- **config**: `/home/davidwu/.cline/scripts/data/placementConfig_v13.json` — list of 36 single-key dicts (placement options: preserveBoundaryEnabled, firstRatioType/Value, secondRatioType/Value, xSpace, ySpace, hornorPinPlacement, pinAutoPlacement, digitalModeEnabled, sharedCell, powerTermEnabled/Name/Spacing, groundTermEnabled/Name/Spacing, tapCellEnabled/Names, fillerCellEnabled/Names ["TECHLIB/spacer/layout"], capCellEnabled, hierarchyEnabled, ...)
- **deliverable**: `step3_place_final.py` — pyAether 脚本，读 config path，打开 schematic + floorplan，建立 SDL 映射，调 aeAutoPlacementFromDesign，保存
- **wrapper**: `step3_place_final.sh` — source setup.bash + export DISPLAY=:99 + QT_QPA_PLATFORM=offscreen + pythone step3_place_final.py

## 关键 API (验证签名)

- `dbOpenCV(lib, cell, view="layout", mode="a", viewType="layout") -> emyDesign` (deprecated, 用 dbOpenCVByType 替代)
- `aeGetCurDesign() -> emyDesign` (当前 drawing area)
- `openDesign(lname, lcell, lview, viewty, namespace, mode) -> emyDesign`
- `aeAddDesignMapping(schematic, layout) -> bool` (建立 SDL 关系, **参数顺序 schematic, layout**; 必须在 aeAutoPlacementFromDesign 之前)
- `aeAutoPlacementFromDesign(le, se, config) -> bool` (自动布局; le=floorplan, se=schematic, config=配置路径/对象)
- `dbSaveCV(cv, lib="", cell="", view="layout") -> bool` / `dbCheckAndSaveDesign(cv, filename="") -> bool` / `dbSaveAll() -> bool`

## 关键洞察 (case 设计要点)

1. **headless 模式**: `emyInitAether('-adv')` 在无 X display 时 SEGV; 解决方案 = 跳过 emyInitAether + `DISPLAY=:99` + `QT_QPA_PLATFORM=offscreen` (pythone 启动时已加载 Aether 运行时)
2. **SDL 映射是前置条件**: aeAutoPlacementFromDesign 无 SDL 关系时返 False "No SDL relationship"; 必须先 `aeAddDesignMapping(se, le)`
3. **调用顺序**: dbOpenCV(schematic) → openDesign/aeGetCurDesign(floorplan) → aeAddDesignMapping(se, le) → aeAutoPlacementFromDesign(le, se, config) → dbSaveCV/le

## case 合成方向

- **case_id**: EDA-Eval-DesignFlow-AutoPlacementStep3-001
- **domain**: pg_layout / auto_placement_from_design
- **形态**: 离线 mock-pyAether 版本 (pyAether 沙盒不可达), 交付 `step3_placement.py` (读 deck.json: lib/cell/floorplan_view/schematic_view/config_path) + `run_step3.sh` (headless wrapper)
- **判分**: mock pyAether 录制 API 调用序列, 断言 dbOpenCV/openDesign/aeAddDesignMapping(BEFORE)/aeAutoPlacementFromDesign/save 顺序与参数; hidden deck_b/deck_c 反硬编
- **与 r1023 RnodeScatterScript 区别**: 域不同 (pg_layout/floorplan auto-placement vs layout_aether rnode scatter), API 链不同 (aeAutoPlacementFromDesign+SDL mapping vs dbCrtLabel/dbCrtInst), 产物不同 (placement 编排脚本 vs rnode scatter 脚本), trace 不同 (egm8i davidwu vs dp48n junweiw)
