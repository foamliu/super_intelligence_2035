# Deepread · pcn3b · show me the cell name in virtuoso (SKILL .il workspace parse)

- **session**: `1792670912119_pcn3b` (colinxu @ hfeg0plg55, 10.129.35.74)
- **match_count**: 38 (cellview:161 / virtuoso:71 / analog:47 / schematic:33 / pyaether:14 / aether:7 / dbopencellviewbytype:6 / cadence:6)
- **size**: 55,579 B / 20 msgs (2 user turns, same text repeated)
- **path-bug revival**: r971 D-ledger parked「NOFILE (colinxu wrong host)」(11-05 path-bug era)；2026-11-15 用户令后 env-config/flow-driving 合法；r977 subdir 路径 ALIVE 确认（与 dyvlr/fz05e/3rdqj/d1yda 同形态 path-bug revival 第 9 例，C 线 r856 第 2 例）
- **trace_source**: 真实 trace，user/host/session_file 全保留

## 用户意图（逐字）

- **U#0** (msg 0, A-faithful seed): `show me the cell name in virtuoso`
- **U#16** (msg 16, repeat): `show me the cell name in virtuoso` (用户重发，因首答 sandbox geGetEditCellView 返 nil)
- 无追问、无澄清、无版本补充。单意图：**给出当前 Virtuoso 里的 cell 名**。

## agent 工具链 (msgs 1-19)

1. `skills(eda_agent)` → eda_agent 路由 skill（PyAether / Virtuoso SKILL 平台选择 + 案例优先 + CAD 源码兜底）
2. `list_allowed_files(/home/colinxu/agentdir/train/V0_NCG_HF_Virtuoso, depth=2)` → 4 文件：`add_testpin.il` / `delete_testpin.il` / `get-username.sh` / `sleep.sh`
3. `read_files(add_testpin.il + get-username.sh + sleep.sh)` → add_testpin.il 揭示目标 cellview：`dbOpenCellViewByType("drjpa_analog" "AG_AnalogBankBuf" "schematic" "" "a")`（editable "a" 模式，即被修改的 cell）+ `dbOpenCellViewByType("basic" "iopin" "symbol" "" "r")`（master pin，read-only "r"）+ reopen `("drjpa_analog" "AG_AnalogBankBuf" "schematic" "" "r")`（verify）
4. `RAG_MCP_Server__search_apis("show cell name", lang=skill)` → geGetEditCellView (sim 0.7966) / geGetEditRep / deGetEditCellView / geGetWindowCellView / geGetTopLevelCellView
5. `list_allowed_files(/home/steveny/.cline/skills/eda_agent/skill/04_case_studies)` → case_007_highlight_nets_by_pattern_skill.md
6. `RAG_MCP_Server__get_api_details([geGetEditCellView, geGetWindowCellView, hiGetCurrentWindow], lang=skill)` → 签名 + 例
7. `read_files(case_007_highlight_nets_by_pattern_skill.md)` → `geMakeProbeWithColor` 高亮模式参考（非本案核心）
8. `run_approved_command(shell-runner, get-username.sh)` → stdout `colinxu`
9. **首答尝试** `SandBox_MCP_Server__run_code` lang=skill username=colinxu:
   ```skill
   cv = geGetEditCellView()
   if( cv then printf("=> lib: %L\n" cv->libName) ... else printf("No cellview ...\n") )
   ```
   → `print_log="No cellview is currently being edited (or no window is open)."`（sandbox 无活跃 Virtuoso 窗口，geGetEditCellView 返 nil）
10. A#15 文字答：给出 CIW 一行命令 `geGetEditCellView()->cellName` / `geGetWindowCellView(hiGetCurrentWindow())->cellName`，说明 sandbox 无活跃窗口
11. **U#16 重发** → agent 改策略：从 add_testpin.il 读到的目标 cellview 直接 open
12. `SandBox_MCP_Server__run_code` lang=skill username=colinxu:
    ```skill
    cv = dbOpenCellViewByType("drjpa_analog" "AG_AnalogBankBuf" "schematic" "" "r")
    if( cv then printf("lib   = %L\n" cv->libName) printf("cell  = %L\n" cv->cellName)
                printf("view  = %L\n" cv->viewName) printf("FULL  = %L/%L/%L\n" ...)
                printf("type  = %L\n" cv->type) printf("numInstances = %d\n" length(cv->instances))
            dbClose(cv) else printf("Could not open ...") )
    ```
    → `print_log="lib   = \"drjpa_analog\"\ncell  = \"AG_AnalogBankBuf\"\nview  = \"schematic\"\nFULL  = \"drjpa_analog\"/\"AG_AnalogBankBuf\"/\"schematic\"\ntype  = \"paint\"\nnumInstances = 1"`
13. A#19 末答：**cell name = `AG_AnalogBankBuf`** / lib `drjpa_analog` / view `schematic` / type `paint` / numInstances 1；附 CIW 一行命令与说明

**关键产物**：无脚本交付，纯 SKILL run_code 执行 + 文字答。**gold = `drjpa_analog / AG_AnalogBankBuf / schematic`**（agent 真实执行 dbOpenCellViewByType 获得，用户接受无追问）。

## 判读

- **用户意图**：在 Virtuoso 里给出当前 cell 名。单一、清晰、可 falsify。
- **真实 gold**：`AG_AnalogBankBuf`（drjpa_analog / schematic）—— agent 通过 **解析工作区 .il 文件**（add_testpin.il 第 9 行 `dbOpenCellViewByType("drjpa_analog" "AG_AnalogBankBuf" "schematic" "" "a")` editable "a" 模式）定位目标 cellview，再 dbOpenCellViewByType read-only 打开读取 cellName/libName/viewName。**核心推理 = 从 .il 工作区脚本里识别「被修改的 cell」(editable "a"/"w")，区别于「只读 master」(read-only "r" 如 basic/iopin/symbol)。**
- **首答失败教训**：geGetEditCellView() 在 sandbox（无活跃窗口）返 nil —— 直接查「当前窗口」不可靠；可靠路径 = 解析工作区脚本找目标 cellview 再 open。
- **API 链**：dbOpenCellViewByType(lib cell view viewname mode) → cv~>libName/cellName/viewName/type；editable mode ∈ {"a","w"}，read-only mode == "r"。

## reframe 决策

- **形态**：live-Virtuoso Q&A → offline .il-workspace-parser produce reframe（承 r855 VirtBridgeStatusDiag-001 env-config/flow-driving 合法脉络 + r852 ConnPathResolve-001 离线单文件 reframe 范式续）
- **A 档 trace-faithful**：task prompt = U#0 逐字原文 `show me the cell name in virtuoso`
- **判分牙**：SUT 产 `show_cell_name.py`，扫工作区 `.il` 文件，正则提 `dbOpenCellViewByType(lib cell view ... mode)` 调用，分类 editable("a"/"w") vs read-only master("r")，选 **editable 目标**作 primary cell name，输出结构化 JSON（lib/cell/view/source_file/open_mode/editable/masters[]）；check() 只跑隐藏 B 工作区（同操作 add-pin/remove-pin，不同 lib/cell/view + master 在前 target 在后倒序排），断言解析器是 .il-driven 非 hardcoded
- **asset A** = 真实 4 文件工作区（add_testpin.il + delete_testpin.il + get-username.sh + sleep.sh，trace GOLD 逐字自 .75）
- **隐藏 B** = 重写 2 .il 文件（edit_pin.il + remove_pin.il，目标 `analogLib/Nand2/schematic` editable "a"，master `basic/iopin/symbol` read-only "r"）+ 2 sh（与 A 同内容）—— **master 在前 target 在后**（edit_pin.il 倒序排，defeat naive first-match），lib/cell/view 与 A 完全不相交（drjpa_analog→analogLib / AG_AnalogBankBuf→Nand2）
- **anti-hardcode**：A-only token（drjpa_analog/AG_AnalogBankBuf）在 B 输出 0 命中；B token（analogLib/Nand2）在 A 输出 0 命中；A-run primary==AG_AnalogBankBuf & B-run primary==Nand2（双轴全异）
- **master 排除牙**：B primary cell 必为 `Nand2`（editable target），**不是** `iopin`（read-only master）—— naive 抓首个 dbOpenCellViewByType 的会落到 master 上 FAIL
- **domain**: layout_virtuoso（Virtuoso SKILL cellview/schematic 库操作 + dbOpenCellViewByType 工作区脚本解析）

## 资产清单

- `assets/EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001/add_testpin.il` —— 真实 A（trace GOLD 逐字）
- `assets/.../delete_testpin.il` —— 真实 A（trace GOLD 逐字）
- `assets/.../get-username.sh` —— 真实 A
- `assets/.../sleep.sh` —— 真实 A
- `assets/.../task_brief.md` —— U#0 verbatim + ≤3 行交付接口
- `assets/.../prompt.txt` —— U#0 verbatim
- `assets/.../manifest_A.json` —— A 工作区清单
- `assets/.../hidden/edit_pin.il` —— 重写 B（master 在前 target 在后倒序）
- `assets/.../hidden/remove_pin.il` —— 重写 B（target 在前 reopen 在后）
- `assets/.../hidden/get_username_b.sh` —— B（与 A 同内容）
- `assets/.../hidden/sleep_b.sh` —— B（与 A 同内容）
- `assets/.../hidden/hidden_manifest.json` —— B 工作区清单
- `reference/.../check.py` —— 14 断言 a-n
- `reference/.../show_cell_name_ref.py` —— 参考解
- `reference/.../negative/{empty_shell,print_expected,delcore,hardcode_a}.py + negative_selftest.py`
- `reference/.../reference_submit.zip`

## 与既有 case 关系

- **C 域 layout_virtuoso 工作区-.il-脚本解析推断目标 cellview reframe 子型首例**：
  - 与 VirtuosoOpenCellQueryGen-001（SKILL-script-generator 生成 open-cell 脚本）正交：本案=**解析** .il 找已有目标，彼案=**生成** open 脚本
  - 与 VirtBridgeStatusDiag-001（桥接端点 TCP 可达性诊断）正交：本案=工作区脚本语义解析，彼案=bridge config JSON TCP probe
  - 与 DrcJobExitCwdDiag-001 / ConnPathResolve-001（physical_verify 离线诊断器）同「离线单文件 reframe」范式但域不同（layout_virtuoso cellview vs physical_verify DRC）
  - 与 D 域 TopCellNameProduce-001（fniub, geGetTopLevelCellView→pyAether aeGetCurDesign mock）相邻但正交：本案=**从 .il 工作区脚本解析**推断目标 cellview（无 live Virtuoso），彼案=**live SKILL API 查询**当前 top cell（mock pyAether）
- path-bug revival 第 9 例（C 线 r856 第 2 例，承 dyvlr r855）；2026-11-15 reaudit 后 env-config/flow-driving 合法第 N 例
