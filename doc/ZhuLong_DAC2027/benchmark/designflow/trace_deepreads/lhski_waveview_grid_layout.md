# 深读笔记 · 1794466033669_lhski · shaoyou @ hfeg0plg47 (mc=45, waveview:198/analog:19)

## trace 概览
- 50 msgs / 3 substantive user turns (act 模式)
- domain: waveform (WaveView ACE Tcl 窗口/信号/面板编排)
- trace 末用户接受九宫格布局结果（assistant 产 display_grid_3x3 proc）

## 用户轮（逐字原文）
- U#0: `<user_input mode="act">显示信号v(input_*)到当前窗口</user_input>`
- U#11: `<user_input mode="act">zoom到200ns附近</user_input>`
- U#24: `<user_input mode="act">将窗口中的五个信号的波形用九宫格形式显示</user_input>`

## assistant 工具链（每轮：RAG_MCP search_apis → get_api_details → SandBox run_code 验证）
### 子任务 1（U#0 → display_input_signals proc）
- API: sx_signal "v(input_*)" → sx_display $sigs
- 验证：返回 5 个 line 对象，error_log 空

### 子任务 2（U#11 → zoom_to_time proc）
- API: sx_current_panel → 解析带单位时间串(p/n/u/m/k→秒) → sx_set_x_range $panel $min $max
- 验证：zoom_to_time 200n → X 轴 1.5e-7 ~ 2.5e-7（150ns~250ns，±50ns）

### 子任务 3（U#24 → display_grid_3x3 proc）★ 本 case 取此子任务
- API 序列: sx_get_active_wv → sx_signal "v(input_*)" → sx_clear_wv → sx_set_wv_mode $wv rowcolumn → 循环(sx_append_panel $wv analog ${row}:${col} + sx_append_line $panel $sig) → sx_update_wv $wv
- 网格映射: row = idx/3+1, col = idx%3+1（行优先，3 列）→ 5 信号占 (1,1)(1,2)(1,3)(2,1)(2,2)
- 验证：sx_pick_panel 逐一核对 5 格位 ALL CELLS MATCH
- 附带发现：sx_pick_panel 真实签名 `<wv_obj> <row:col>` 两参数（与文档三参数描述不同）

## 金标准（trace 末用户接受的产物）
display_grid_3x3 proc（无参，硬编码 pattern="v(input_*)" + ncols=3）。本 case 泛化为 `display_grid {pattern ncols}` 参数化 proc（source signal_spec.tcl 读参数），使隐藏 B/B2 可换参数重跑。

## 合成决策
- 原 FSDB 私有二进制不可复现 → B 档 synthesized reframe
- 保留 WaveView ACE Tcl API 契约（tool-contract=original）→ L2 mock-shim（升级 L1 文本 dump）
- mock shim (wv_mock.tcl) 模拟 sx_get_active_wv/sx_signal/sx_clear_wv/sx_set_wv_mode/sx_append_panel/sx_append_line/sx_update_wv/sx_pick_panel，维护窗口状态(mode/panels/cleared/updated) + 记调用日志 + 末尾 dump wv_state.json
- 隐藏 B: pattern=v(data_q*) ncols=4 → 7 信号排 2 行 4 列（末行 3 格）；反硬编码（A 的 v(input_*)/ncols=3 不许出现）
- 隐藏 B2: pattern=v(GONE*) ncols=3 → 0 匹配，验健壮性(proc 抛错 + 不建面板)

## check.py 14 条件 (a-n)
a) 合法 zip 含 display_grid.tcl  b) source signal_spec.tcl + 无禁用 exec  c) B 上 tclsh exit 0  d) sx_get_active_wv 调用  e) sx_clear_wv 先于 sx_append_panel  f) sx_set_wv_mode rowcolumn  g) sx_signal 用 B pattern(反硬编码)  h) 7 面板格位==行优先 ncols=4 oracle  i) 每面板 1 line 信号按序  j) sx_update_wv 末尾  k) 反硬编码 A pattern 未泄漏 + B 列数=4  l) 无多余面板  m) B2 抛错  n) B2 不建面板

## 自验
- REF PASS 14/14
- 12 negatives 全 FAIL (NEG_RC=0), distinct first_fail labels {a,b,d,e,f,g,h,j,m} = 9 ≥ 7
- §4.9 degenerate (empty_zip/print_only/core_deleted) 全 FAIL 3/3
