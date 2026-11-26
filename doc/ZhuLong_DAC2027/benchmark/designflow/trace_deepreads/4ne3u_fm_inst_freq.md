# 4ne3u 深读笔记 — WaveView ACE Tcl FM 瞬时频率脚本

## trace_source
- session_file: 1793093179379_4ne3u.messages.json
- user: e0023936 · host: 10.129.32.75 · mc=44 (waveview:273 analog:34 aether:11 synopsys:10 pyaether:9)
- domain: waveform
- 28 msgs, 2 user_input turns

## 用户轮逐字
- **U#0** (preamble/hello): "写一个tcl版本的hello，并使用 run_code 的MCP服务执行"（热身，非 produce-task）
- **U#1** ★ (唯一 A-faithful produce-task, 逐字):
  > 编写一个 Tcl ACE 脚本，计算一个 FM（调频）信号的瞬时频率随时间变化曲线，并在新的 WaveView 窗口中显示。要求：
  > 1. 定义过程 f_vs_t，接收信号对象 sig 和电压阈值 v_thr
  > 2. 创建一个新的波形数据对象（名为 "frequency"，analog 类型）
  > 3. 对输入信号创建 RISE 扫描并设置电压阈值
  > 4. 遍历所有上升沿数据点，计算相邻两个上升沿之间的频率 f = 1/(t2 - t1)
  > 5. 将每个频率值及其对应时间 (t2, freq) 追加到新波形中
  > 6. 主程序打开 ./wave.dat 波形文件，获取信号 "wave"，调用 f_vs_t

判定：U#1 纯提需求，6 条编号要求自洽，未给根因/修复 → **A-faithful produce-task**。U#0 是 hello 热身。

## agent 工具链
get_agent_policy_status → SandBox_MCP__run_code(tcl hello, 遇 non-ASCII 报错→精简 ASCII 重跑) → search_codebase/RAG search_apis(均超时) → list_allowed_files(/home/e0023936, /home/e0039602/.cline/skills) → skills → read_files(waveview-fsdb-readerV2-2 / waveview-fsdb-reader 脚本) → search_codebase(sx_scan/sx_measure/tuCreateScan/scan rising/sx_signals/create waveform analog — **全部超时**) → **trace 在 msg 27 中断**（search_codebase 6 查询全 30s 超时，agent 未产出最终 Tcl 脚本）。

## 真实产物
**无**。agent 在搜索 WaveView ACE API 时被 search_codebase 超时卡住，trace 在 28 msg 处中断，**未交付 f_vs_t 脚本，用户未接受任何结果**。

⇒ 无 user-accepted 金标准 → **不做 A-faithful（金标缺失），改 B-grade synthesized**（prompt 仍用 U#1 逐字，金标自合成）。

## WaveView ACE API 调研（pyAether search_apis/get_api_details 实测签名）
- `sx_open_sim_file_read <file>` → file_obj（`catch` 包裹，不存在抛错）
- `sx_current_sim_file <file_obj>` → 设当前文件
- `sx_find_wave_in_file <wdf> <name>` → wave_obj；缺失返回 `NULL`
- `sx_create_signal <name> <ANALOG|LOGIC|COMPLEX> <bits>` → 新信号句柄（ANALOG bits=0）
- `sx_add_wave <name> <type> <width>` → 等价创建
- `sx_set_threshold <obj> <val>` → 设 Y 阈值（供 RISE/FALL/CROSS 扫描）
- `sx_create_scan <sig> <RISE|FALL|CROSS|POINT|CHANGE>` → scan_obj
- `sx_scan_data_points <sig> <type> <thr>` → scan_obj（RISE 需 thr）
- `sx_scan_first <scan>` → 1/0；`sx_scan_next <scan>` → 1/0（first+next 循环遍历所有事件）
- `sx_scan_jump <obj> <edge_count>` / `sx_jump_to_x <scan> NEXT|FIRST`
- `sx_x_value <scan>` → 当前点 X 值；`sx_y_value <scan>` → Y 值
- `sx_append_data <sig> <x> <y>` → 追加数据点（返回 1/0）
- `sx_new_wv` / `sx_add_wv` → 新 WaveView 窗口（批处理 `-ace_no_gui` 返回 `NULL`！）
- `sx_display_wave <wv> <wave>` → 显示（GUI 概念，批处理下需 catch 守护）

**关键坑**：`sx_new_wv` 批处理返回 `NULL` → 显示须 `if {$wv ne "NULL"} { catch {sx_display_wave ...} }` 守护。

## 合成策略（B-grade synthesized, L1 stub-harness 真跑候选）
trace 无产物 + 真实 FSDB 不可合成 → **离线 Tcl 桩模拟器**真跑候选：
- `wv_stubs.tcl` 模拟全部 sx_* 命令，用 config.tcl 的 `EDGE_TIMES` 喂假上升沿时间，`sx_x_value` 返回 `EDGE_TIMES[idx]`，`sx_scan_first/next` 遍历；每个 API 调用 + `sx_append_data` 的 (x,y) 写入 RECORD。
- `harness.tcl <cand.tcl> <config.tcl> <stubs.tcl>`：source config→stubs→candidate（候选 main 在 source 时执行）→ dump RECORD。
- check.py 跑 A/B/B2 三个 config，解析 RECORD，断言候选用对 API 且 `y == 1/(t2-t1)`。
- **反硬编码**：B/B2 EDGE_TIMES 与 A 不相交 → 硬编码 A 输出者 B 上 count/值不符 → (m)/(n) FAIL；候选须真正调 scan 遍历读 `sx_x_value` → (g) 拦截跳过 scan 的硬编码；源码无 A 专有字面量 → (o)。

**A**：EDGE_TIMES={1e-9,3e-9,6e-9,1e-8,1.5e-8,2.1e-8}(6 边沿→5 频点), THR=0.5
**B**(hidden)：{2e-9,5e-9,9e-9,1.4e-8,2e-8,2.7e-8,3.5e-8}(7→6 频点), THR=0.3
**B2**(hidden)：{5e-10,1.5e-9,3e-9,5e-9,8e-9}(5→4 频点), THR=0.7

## 金标 fm_freq_ref.tcl
proc f_vs_t(sig,v_thr) → sx_create_signal "frequency" ANALOG 0 → sx_set_threshold $sig $v_thr → sx_create_scan $sig RISE → sx_scan_first 循环 sx_scan_next，取 sx_x_value 得 t1/t2，dt>0 时 freq=1.0/dt，sx_append_data $freq_sig $t2 $freq → return。main：sx_open_sim_file_read ./wave.dat → sx_current_sim_file → sx_find_wave_in_file $file "wave" → f_vs_t $sig 0.5 → sx_new_wv，if {$wv ne "NULL"} catch sx_display_wave → sx_close_sim_file。

## check.py 条件清单（16 条 a-p）
a zip 含 .tcl 无禁 import/路径
b tclsh source 候选无错（桩 unknown 兜底，只拦顶层语法/运行错）
c proc f_vs_t 定义且恰 2 参(sig v_thr)
d 创建名为 frequency 的 analog 波形(create_signal/add_wave)
e 调 sx_set_threshold 设阈
f 创建 RISE 扫描(create_scan/sx_scan_data_points RISE)
g 扫描遍历(scan_first+scan_next/jump_to_x)
h A 上 append 数=N-1 且每点 y≈1/(t2-t1)
i 每点 append x==t2(后一上升沿时刻)
j 主序打开 ./wave.dat
k 主序获取信号 wave
l 新建 WaveView 窗口并显示(new_wv+display_wave)
m 跨输入 B：append 匹配 1/(t2-t1) 且与 A 不同(反硬编 A 输出)
n 跨输入 B2：append 匹配 1/(t2-t1)
o 源码无 A 专有数值字面量(反硬编)
p 确定性：3 次重跑 A 输出哈希一致

## 自验
- ref PASS 16/16
- 6 negative 全 FAIL(empty_shell/print_expected/ref_core_deleted + naive_first_only/naive_wrong_formula/naive_fall_scan)，NEG_RC=0
- §4.9 三假{empty_shell,print_expected,ref_core_deleted}全 FAIL
- 确定性 3 次重跑 PASS
- test==disk sha256 e0b65b76412e688addbea8b3ba632cc7efcb3e76c4b4fb62b9f196ed44630a84 ✓
- k_rationale=k_check=16 GATE PASS
- 台账 mark 4ne3u→case；D.jsonl 152→153；waveform 36→37

## 教训
1. **trace 不完整(无 user-accepted 产物)→ 不做 A-faithful**：金标缺失只能 B-grade synthesized；但 prompt 仍可用 U#1 逐字(清晰自洽的 produce-task)，标记 track=synthesized 诚实区分。
2. **WaveView 批处理 sx_new_wv 返回 NULL**：显示须 `if {$wv ne "NULL"} { catch {sx_display_wave} }` 守护——这是真实 ACE 坑，候选不守护也不致命(桩返回 wv_1 让 display 记录到)，但金标应守护。
3. **离线 Tcl 桩模拟器是 waveform L1 真跑候选的好范式**：sx_* 全桩化 + EDGE_TIMES 喂假数据 + RECORD 录调用 → 用 tclsh subprocess 真跑，避开合成 FSDB 的死结；反硬编码靠 B/B2 不相交 EDGE_TIMES。
4. **search_codebase 超时是真实 trace 中断原因**：4ne3u agent 卡在 API 搜索，非能力不足——说明 A-faithful 难度可能被工具可用性稀释，需在判据里区分"①交付形态错 vs ③能力不足"。
