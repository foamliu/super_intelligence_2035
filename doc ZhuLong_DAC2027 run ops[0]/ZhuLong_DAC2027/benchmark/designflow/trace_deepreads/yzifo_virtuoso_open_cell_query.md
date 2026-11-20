# trace_deepread: yzifo — Virtuoso "当前打开的 cell" 查询脚本生成 (layout_virtuoso)

- **session**: 1793100700946_yzifo.messages.json
- **user / host**: colinxu @ hfeg0plg55 (10.129.35.74)
- **match_count**: 46 (cellview:151;virtuoso:138;analog:26;dbget:25;schematic:16;pyaether:14;aether:7;dbopencellviewbytype:5)
- **size**: 72KB / 21 msgs / 2 真实 user_input 轮
- **C ledger 旧记录**: `yzifo colinxu hfeg0pkn002 85 physical_verify parked 2026-11-09 20:39 view-current-cell 1-turn recon`（host/domain 均错；11-15 reaudit 前按"非 produce"口径 parked）
- **D ledger 旧记录**: `1793100700946_yzifo.messages.json ... parked 2026-11-05 NOFILE (colinxu wrong host)`（cross-shard wrong-domain）

## 真实用户意图（逐字）

- **U#0**: 「帮我查看virtuoso当前打开的cell」
- **U#50**: 「你能访问电路吗」

## 助手工具链（21 msgs）

1. `skills(eda_agent)` → 调出 EDA 自动化技能路由
2. `run_commands` 被 policy 拒（Raw shell tool disabled）→ 改 `list_allowed_files(/home/colinxu/agentdir/train/V0_NCG_HF_Virtuoso)`
3. `read_files(_sandbox_status.py / add_testpin.il / delete_testpin.il / get-username.sh / sleep.sh)` + `get_agent_policy_status`
4. `run_approved_command(python-runner, _sandbox_status.py)` → SIGKILL/timeout（/proc 扫描超时）
5. `RAG_MCP_Server__search_apis("get current open cellview windows hiGetCurrentWindow dbGetOpenCellViews", lang=skill)` → 返回 dbGetOpenCellViews / deOpenCellView / geGetCellViewWindow / geGetWindowRep
6. `run_approved_command(python-runner, _sandbox_status.py, args=["--no-proc-scan"])` → 成功：user=colinxu uid=200329，cwd=/home/colinxu/agentdir/train/V0_NCG_HF_Virtuoso，CDS_LOAD_ENV=CSF，CDS_LIC_FILE=5980@hl07:...，Virtuoso 二进制 IC617ISR23 `/apps/cdsmgr/CRB/IC617ISR23/tools/dfII/bin/virtuoso`，**本机无正在运行的 Virtuoso GUI 会话**（/proc 只匹配到 sidecar 守护进程）
7. `RAG_MCP_Server__get_api_details([dbGetOpenCellViews, hiGetCurrentWindow, geGetWindowCellView, geGetWindowId], lang=skill)` → 确认 API 用法：
   - `dbGetOpenCellViews()` => `(d_cv d_cv ...) / nil` — Returns all opened cellviews in virtual memory
   - `hiGetCurrentWindow()` — focused window
   - `geGetWindowCellView(w)` — cellview displayed in window w
8. `editor(create get_current_cell.il)` → 写出 SKILL 脚本
9. `read_files(get_current_cell.il)` → 校验写入

## ★ gold 产物：`get_current_cell.il`（2246 chars，逐字）

```skill
;====================================================================
; get_current_cell.il
; Purpose  : report the cellview currently open/focused in Virtuoso,
;            plus a summary of every open cellview in the session.
; Usage    : load("get_current_cell.il")   -> runs CCSGetCurrentCell()
;            or call  CCSGetCurrentCell()  directly from the CIW.
; Info     : - current window  : hiGetCurrentWindow()   (focused window)
;            - displayed cell  : geGetWindowCellView(w) (what the window shows)
;            - all open views  : dbGetOpenCellViews()   (session-wide)
;====================================================================

procedure( CCSGetCurrentCell()
  let( (w cv cvs curLib curCell curView n modTime saved editFlag)
    ; Part A : the cell currently open in the focused (current) window
    w = hiGetCurrentWindow()
    printf("== A. Current (focused) window ==\n")
    if( w then
      printf("window ID  = %L\n" w)
      cv = geGetWindowCellView( w )
      if( cv then
        curLib  = cv->libName
        curCell = cv->cellName
        curView = cv->viewName
        printf(">> current cell = %s/%s/%s\n" curLib curCell curView)
        printf("   editCellView = %L\n" geGetEditCellView( cv ))
        printf("   wasModified  = %L   saved   = %L\n" cv->isModified cv->isSaved)
      else
        printf("   warning: current window is empty (no cellview displayed)\n")
      )
    else
      printf("   warning: no current window defined\n")
    )

    ; Part B : every cellview currently open in this session
    cvs = dbGetOpenCellViews()
    printf("\n== B. All open cellviews in this session ==\n")
    if( cvs then
      n = 0
      foreach( cv cvs
        n = n + 1
        printf("   %2d. %s/%s/%s\n" n cv->libName cv->cellName cv->viewName)
      )
      printf("   total open cellviews = %d\n" n)
    else
      printf("   (no cellview is open)\n")
    )
    t
  ) ; let
) ; procedure

CCSGetCurrentCell()
```

## 助手末轮总结（msg[20]）

- Virtuoso = IC617ISR23（`/apps/cdsmgr/CRB/IC617ISR23/tools/dfII/bin/virtuoso`）
- 本机**无正在运行的 Virtuoso GUI 会话**（/proc 只匹配 sidecar）
- 「当前打开的 cell」信息在 Virtuoso 会话内部，必须让 Virtuoso 自己 SKILL 查询
- 已生成 `get_current_cell.il`：Part A `hiGetCurrentWindow()+geGetWindowCellView(w)` 打印 `lib/cell/view` + `geGetEditCellView(cv)` + `cv->isModified/isSaved`；Part B `dbGetOpenCellViews()` 枚举所有打开 cellview（`lib/cell/view` + 总数）
- 用法：Virtuoso CIW `load("get_current_cell.il")`，末尾自动 `CCSGetCurrentCell()`

## reframe 决策（B 档 synthesized）

A 档 gold = 单个静态 `get_current_cell.il`，依赖运行中的 Virtuoso GUI 不可离线复现，且**无 input 参数化**无法做 hidden B 输入对换 → 无 ≥8 独立硬断言牙。

B 档 reframe = **按需 SKILL-script 生成器**：输入 query spec JSON，按 spec 动态生成 SKILL `.il`。trace 里助手检索并选择的 6 个 SKILL API（hiGetCurrentWindow / geGetWindowCellView / dbGetOpenCellViews / geGetCellViewWindow / geGetWindowId / deOpenCellView）被 spec 字段参数化：
- `procedure_name` / `header_comment`
- `current_window`(bool) → Part A
- `current_cell_fields`(list ⊂ {libName,cellName,viewName,isModified,isSaved,cellViewType}) → Part A 打印哪些 cv 字段
- `include_edit_cellview`(bool) → geGetEditCellView(cv)
- `all_open_cellviews`(bool) → Part B
- `list_fields`(list) → Part B 每个 cellview 打印哪些字段
- `include_window_id`(bool) → geGetCellViewWindow(cv) per-cellview window id
- `print_total`(bool) / `auto_run`(bool)

**trace-faithful**: A spec 输出的 .il 与真实 trace 产物 `get_current_cell.il` 结构等价（同 procedure 名 CCSGetCurrentCell / 同字段 libName,cellName,viewName / 同 editCellView / 同 isModified,isSaved / 同 Part B 枚举+total / 同 auto_run）。

**teeth**: 16 条独立条件 a-p：
- a zip 合法+单 .py 候选；b py_compile+stdlib-only；c B 运行 exit0+非空 .il；d B .il 定义 procedure(CCSListOpenCellviews())；e hiGetCurrentWindow()；f geGetWindowCellView(；g cv->cellViewType（B 独有）；h dbGetOpenCellViews()；i geGetCellViewWindow(（B 独有）；j libName/cellName/viewName；k isModified+isSaved；l total；m auto-run B 过程名；n 反硬编 A 守卫（A 运行 .il 不含 cellViewType/geGetCellViewWindow）；o 缺 spec 非零退出；p 3-seed 确定性。

**visible A**（忠实 trace）: procedure_name=CCSGetCurrentCell, current_cell_fields=[libName,cellName,viewName], include_edit_cellview=true, all_open_cellviews=true, list_fields=[libName,cellName,viewName], include_window_id=false, print_total=true, auto_run=true

**hidden B**（全反相）: procedure_name=CCSListOpenCellQueryGen-001 改 CCSListOpenCellviews, current_cell_fields=[libName,cellName,viewName,isModified,isSaved,cellViewType], include_window_id=true → 10+ 轴全异（procedure 名 / current_cell 字段集多 cellViewType+isModified+isSaved / list_fields 多 window id 映射）防硬编 A。

## 意图审计判定

**keep** — colinxu 真实意图（查看 Virtuoso 当前打开的 cell）完全保留。reframe 是 grounding（把单次手写脚本沉淀为按需生成器 + 离线化 + 参数化），非加难。trace 里 U#50「你能访问电路吗」助手的"能力/限制说明" prose 是真实用户意图但属 prose Q&A 无 ≥8 独立硬断言牙，未入本案判分。本案是 **C 域 layout_virtuoso SKILL 脚本生成器 reframe 子型首例**（与 VirtuosoStartupDiag 启动诊断 / VirtuosoPollWait 轮询 / VirtuosoLaunchRecipeGen 启动配方 / VirtuosoToolLocator 工具定位 / VirtuosoPreSimNetlistLocate 网表定位 / VirtuosoErrorDiag 错误诊断 / VirtuosoMosaicRowColAdjust mosaic 调整 / VirtuosoSfeLangDiag 语言诊断 / LayoutVirtuoso 版图操作 正交：本案 = open-cellview 查询脚本按需生成）。2026-11-15 reaudit 后 env-config/flow-driving 合法第 N 例。
