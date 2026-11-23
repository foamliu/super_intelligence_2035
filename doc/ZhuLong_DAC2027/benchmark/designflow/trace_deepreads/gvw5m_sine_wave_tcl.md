# trace_deepread: gvw5m — 正弦波 TCL 脚本（WaveView sx_equation）

- session: `1795160037277_gvw5m` (e0023936 @ hfeg0plg97 / 10.129.8.229)
- mc=29, 36 msgs, 95KB, domain=waveform
- trace_source: user=e0023936, host=hfeg0plg97, session_file=1795160037277_gvw5m, match_count=29
- claim: r1211 D-shard (claimed in trace_ledger_D)

## 真实用户意图
用户 3 次重复同一请求：「使用 search_apis 查询一个如何画正弦波的接口文档，然后帮我写 tcl 代码执行」。
中间穿插：U#2 "hi hello"（连通测试）、U#4 询问是否有 KB_RAG_Server 的 kb_query 工具（assistant 无此工具）。
真实意图 = doc-search + code-gen：用 API 检索找到画正弦波接口，写 TCL 在 WaveView 执行。

## assistant 工具链与产物
1. `RAG_MCP_Server__search_apis`（lang=tcl，query "生成正弦波信号"/"创建虚拟信号波形"）→ 命中核心接口 `sx_equation`（波形计算器，表达式内可用 sin()）+ 配套 `sx_create_signal`/`sx_add_wave`/`sx_add_wave_to_plot`/`sx_release`。
2. `RAG_MCP_Server__get_api_details`（sx_equation/sx_create_signal/sx_add_wave/sx_add_wave_to_plot/sx_release）→ 拿到参数与示例。
3. `SandBox_MCP_Server__run_code`（lang=tcl）→ **Connection refused by sandbox [tcl]**（TCL/WaveView 桥未启动），全程 4 次重试均拒绝。
4. `editor` 写 `/home/e0023936/devops/wv_demo/draw_sine.tcl`：用 `sx_open_sim_file_read` 取 time 轴 → `sx_equation "v_sin = A*sin(2*pi*f*time)"` → `sx_add_wave` → `sx_add_wave_to_plot` → `sx_save_signal` → `sx_release`。
5. 用 pyAether 沙箱交叉验证正弦数学（amp=1.0, freq=1e6, phase=0, t=[0,0.25,0.5,0.75,1.0,1.5]），但 pyAether 也 Connection refused。

## 可判分性评估（关键）
- 可离线抽取的纯计算内核 = 正弦波采样：y = A*sin(2*pi*f*t + phase)，给定 A/f/phase/time 轴 → (t, y) 序列。
- **但内核过于平凡**（一行 math.sin），难以构造 ≥8 条独立有牙断言而不退化成「仅数值/仅子串」式（违反 §4.3）；hidden B 只能换 A/f/phase/点数，结构性变化空间窄。
- 真实交付物（TCL 调 sx_equation 画波）依赖 WaveView 在线，无法离线判分；TCL 沙箱全程不可连，trace 里也无「跑通」证据。
- 判定：**thin trace，不适合造有牙 case**。按 §4.9/§4.3 与「🚫 不为凑数造 weak case」原则，parked。

## 处置
- r1211: parked（note: thin sine-wave TCL trace, no teeth-able offline kernel ≥8 indep assertions; WaveView sandbox unreachable, no run-passed evidence）。
- 后续：waveform 域需找更丰富的 trace（fsdb 解析、波形测量、多信号对比、总线波形展开等），mc≥5 池 top-200 已被 4 shard 瓜分殆尽，需下探 mc 5-30 或换 keyword。

## 与既有 D case 不相交确认
本 trace 的内核（正弦采样）即便合成，也与 r1206-r1210（SPICE subckt 解析 / Verilog 层次追踪 / FIFO 生成 / async-risk waive / 命令分类 / 信号层次）不相交；但因其 thin，不入库。
