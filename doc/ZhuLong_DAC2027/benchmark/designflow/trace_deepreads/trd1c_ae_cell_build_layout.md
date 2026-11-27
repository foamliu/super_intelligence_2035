# trd1c 深读笔记 — AeCellBuildLayoutProduce-001

## trace 溯源
- session: `1789521487986_trd1c.messages.json`
- user: e0020134 @ hfeg0plg86 (mc=416, aether:4950 + pyaether:1444 + cellview:144 + analog:103 + netlist:54 + schematic:44 主导)
- domain: schematic_netlist (D 域)
- 获取: .75 eda_flow open_session(r1635) 秒级 + scp hfeg0plg86 per-session subdir → 1.09MB / 233 msgs (144 user / 89 assistant)

## 用户真实意图（全程）
用户(e0020134)在 Aether/pyAether 中搭建「烛龙(Zhulong AI) → Aether 直接控制」流程，分四阶段：
1. **msg 0-58** 排查本地 Aether 连接性：pyAether 模块位置、`aetherstartup` 脚本、`-nograph` 选项、`pythone` 可执行机制（list_allowed_files/read_files/RAG search_apis 反复探查）。
2. **msg 59-85**「不要桥接，要本地连接控制 Aether」：探索直接控制方案。
3. **msg 86-172**「让烛龙和 Aether 通信，直接控制画图」→ 落地 `zhulong_aether_control.py` 控制层 + `zhulong_aether_batch.sh`/`run_aether.sh` 包装 + 文件队列实时监听 `aether_command_listener.py`；再要「下发指令→解析→画图一全套流程」→ `zhulong_draw.py` 命令解析+auto_draw 流水线。
4. **msg 173-232**(核心可合成)「在 hrz_test 中创建一个新 cell，调用 hrz_test lib 下的一些 cell 把他们 copy 到新 cell 中，再在新 cell 中画 3 个新的 pattern，横向排列，大小不一 10-30 之间」→ 落地 `build_hrz_cell.py`。

## 核心 pyAether API 表面（build_hrz_cell.py，经多轮迭代修签名）
- `ae.emyInitAether("-adv")` — Aether 初始化
- `ae.aeGetLibList()` → 库名 list；`ae.aeGetCellList(lib)` → cell 名 list
- `ae.aeDelCell(lib=, cell=, view=[view])` — 删除已有 cell（重建前清理）
- `ae.dbNewCellView(lib, cell, view, viewType)` → 新 cellview
- `ae.emyPointF(x, y)` → 点；`ae.dbCrtInst(cv=, point=, lib=, cell=, view=, inst=)` → 实例（横向排列，spacing 15）
- `ae.emyBoxF((x1,y1),(x2,y2))` → bbox（迭代修：试过 emyBoxF(x1,y1,x2,y2) 与 emyBoxF(x,y,w,h)，最终两 tuple 形式）
- `ae.dbCrtRect(cv=, bbox=, layer=, purpose=)` → 矩形（3 个 pattern: 10x10/20x15/30x25，横向排列在实例右侧）
- `ae.dbCheckAndSaveDesign(cv)` / `ae.aeSaveDesign()` — 保存（迭代修：dbSave→aeSaveDesign→dbCheckAndSaveDesign）
- `ae.dbCloseCV(cv)` / `ae.aeCloseDesign()` — 关闭

## case 设计（synthesized-reframe, LIVE-NA, L0+L1）
把「生成 pyAether 脚本驱动 Aether 建 cell+例化+画图」reframe 为 **spec-JSON 驱动操作序列生成器** `build_cell(spec) -> ops_log`，纯 Python 结构化判分，无真实 EDA 二进制依赖（Aether/pyAether 不在判分沙盒不强求 L2.live）。
- **A**(visible) spec_A.json: hrz_test/zhulong_combined, 3 source cells(nand2x1/invx1/bufx1), spacing 15, inst_y 0, prefix I_, 3 patterns(M1 10x10/M2 20x15/M3 30x25)
- **hidden B**(token-structurally 不同) spec_B.json: ddr6_io/zhulong_io_combo, **4** source cells(iodrvx1/iorcvx1/esdx2/bufx4), spacing 20, inst_y 5, prefix U_, 3 patterns(M4 12x12/M5 18x22/M6 28x16) → A 硬编码器在 B 全错
- **reference** `build_cell_ref.py` spec 驱动通用实现（validate 必填字段→malformed raise；init→new_cell→inst(idx*spacing)→rect(base_x=len*spacing+offset+pattern.x)→save→close）
- **check.py 15 conds(a-o)**：a zip 含 py ②b py_compile ③c A 运行返回非空 ops_log 首 init 末 close ④d A init flag 匹配 ⑤e A new_cell lib/cell/view/view_type 匹配 ⑥f A inst 数+cell/inst_name/x(idx*spacing)/y 匹配复算 ⑦g A rect 数+w/h∈[10,30] ⑧h A rect 横向排列(x1 递增不重叠) ⑨i A rect bbox(base_x+pattern.x,+w/h,layer)匹配复算 ⑩j A save/close 存在且顺序(save 在 rect 后/close 在 save 后) ⑪k B 运行返回非空+inst/rect 数匹配 ⑫l B inst 位置+rect bbox 匹配 B-spec 复算(反硬编码) ⑬m B w/h∈[10,30]+横向排列 ⑭n malformed spec→raise ⑮o 源码无 A 专属 token 字面量
- **LIVE-NA**(deliverable=Python 操作序列, check 跑候选+独立复算断言, 无真实 EDA 工具二进制依赖; pyAether 沙盒不在线不强求 L2.live) judge_layers=[L0,L1] 无 check_live

## 自验全绿
- ref check.py on reference_submit.zip → **PASS 15/15**
- negative_selftest 6 neg ALL-FAIL distinct first-fail{c,c,h,k,f,g}（§4.9 trio full: empty→c/print_only→c/core_deleted→h + hardcode_a→k/wrong_inst_x→f/bad_size→g）
- workdir leak 自检通过（无 check.py/reference/hidden 泄漏）
- 3-way sha sync（disk check.py == JSON test == metadata.check_sha256=4642580c76bc... size 14292）
- k_check=15=k_rationale=15
- judge dir 端到端 PASS（reference_submit.zip → check.py → PASS）
