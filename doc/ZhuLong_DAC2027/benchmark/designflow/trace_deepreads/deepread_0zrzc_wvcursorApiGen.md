# Deepread — 1793006362279_0zrzc (e0023936@hfhds201, mc90, eda_other)

- **session**: `/home/e0023936/.cline/data/sessions/1793006362279_0zrzc/1793006362279_0zrzc.messages.json` (215KB, 100 msgs: 59 user / 41 assistant)
- **real user turns** (mode=act, A-faithful candidates):
  - U#0 `使用MCP的工具查询pyAether接口文档 Get the currently opened schematic design.` → 检索 aeGetCurDesign
  - U#6 `使用MCP的工具查询tcl接口文档 add a vertical cursor to panel.` ★ **本 case 取此轮**（纯目标，无根因/修法，A-faithful 合格）
  - U#23 `使用run_code 执行tcl代码`
  - U#39/U#57/U#60 `我的用户名是e0023936，写一个tcl代码使用run_code工具执行`
  - U#63/U#69/U#95 直接给 run_code JSON 参数 `{code: sx_current_wv / sx_current_panel / sx_add_cursor / set v [sx_cursor_value] / puts ...}`
  - U#66 `写一简单的virtuoso的skill代码继续测试`
  - U#99 `不需要修改什么， 你应该通过MCP`（末轮，要求用 MCP 而非本地脚本）
- **assistant 工具链** (41 assistant turns): RAG_MCP_Server__search_apis(13: lang=tcl/skill/pyAether/waveview 检索光标 API) + RAG_MCP_Server__get_api_details(4: sx_add_cursor/sx_add_h_cursor/sx_current_panel/sx_new_panel/sx_set_cursor_value/sx_cursor_value/sx_delete_cursors) + SandBox_MCP_Server__run_code(15: lang=tcl/pyAether/skill 全部失败 MCP error -32602 / Unable to connect) + editor(7: 写 hello.tcl/cursor_test.tcl/run_tcl.sh/run_wv.sh/run_skill.sh/check_tcl.sh) + run_approved_command(6: shell-runner 跑 tclsh/wv/skill 本地验证) + search_codebase(2) + read_files/list_allowed_files(查 agent-policy/sandbox_v3)
- **gold standard** = trace 末尾用户接受的产物：
  - API 文档族（RAG_MCP_Server 实测检索到）：`sx_add_cursor`(Adds a vertical cursor to a panel) / `sx_current_wv` / `sx_current_panel`(no arg) / `sx_cursor_value`(returns X-axis value) / `sx_add_h_cursor` / `sx_set_cursor_value` / `sx_delete_cursors`
  - 光标 TCL（用户多次提供并接受）：
    ```
    sx_current_wv
    sx_current_panel
    sx_add_cursor
    set v [sx_cursor_value]
    puts "vertical cursor value = $v"
    ```
  - 实测签名（pyAether get_api_details host=waveview P-2019.06-SP2 沙盒核对）：`sx_add_cursor(panel_obj,xloc)` 返回 cursor 对象；`sx_cursor_value(cursor_obj)` 需 cursor 对象（trace 用户代码裸调用 no-arg 与实测签名有出入，判分按实测签名 panel_obj+xloc / cursor_obj 要求）
  - run_code 沙盒后端不可达（Unable to connect），本地 tclsh 8.6.8 验证语法可用；wv -ace_no_gui 因 libfontconfig 缺 FT_Done_MM_Var 启动失败
- **合成** → EDA-Eval-DesignFlow-WvCursorApiGen-001 (eda_other, A-faithful, L1-static+subprocess):
  - prompt = U#6 逐字原文 + task_brief(3 行交付接口)
  - A 资产：prompt.txt + task_brief.md + config_a.json(panel=top, xloc=1.2ns)
  - 隐藏 B：panel=analog_3, xloc=45.6ns（panel 名 + xloc 值异于 A，方向保持 vertical）
  - Bp 3 seeds：panel/xloc 各异(bus_0/12.5ns, clk_dom_7/3.3us, mixed_2/8.8ps) 防硬编码
  - 交付：cursor_api_report.json(query/lang/host/apis[] 7 条光标 API 实测签名) + add_cursor.tcl(proc add_cursor {panel_obj xloc} 调 sx_current_wv/sx_current_panel/sx_add_cursor(panel,xloc)/sx_cursor_value(cursor)/puts)
  - check.py 14 conds a-n：tclsh+stub sx_* 捕获调用结构 + report 字段对金标准 API 事实 + Bp 防硬编码
  - 自验：REF PASS 14/14；4 negative(naive_noop→i / print_only→j / core_deleted→h / wrong_report→d)全 FAIL DISTINCT=4；§4.9 三假(empty→i / print-only→j / strip-core→j)全 FAIL；negative_selftest ALL_FAIL DISTINCT=4
  - k_rationale=k_check=14 闸门 PASS · test_sha8 18cb1522 · covered 170→171(eda_other 37→38)
