# trfp9 — WaveView probe-signal reuse across waveforms how-to Q&A

**session**: 1793929018140_trfp9 · **user**: xiaoyu1d · **host**: hfeahpc501 (10.129.33.24)
**match_count**: 40 (waveview:265; synopsys:9; analog:9; aether:7; schematic:6; pyaether:5)
**agent**: deepseek-v4-flash (cxmt-deepseek-flash), interactive, status=cancelled
**cwd**: /home/xiaoyu1d · **started**: 2026-11-06T01:36:58Z · **ended**: 01:53:26Z (≈16 min)
**ledger**: D-parked 2026-11-12 (r560 peek) → revived case r886 (2026-11-18) — non cross-shard dup (trfp9 only in D ledger)

## 用户原话（A档任务说明 · 逐字）

> 现在我已经用wavevie打开了6个速率为1067的fsdb波形，然后probe了好多信号，然后我准备打开6个10667的波形，我现在不想到原理图里面一个一个probe了，我就是还是看刚刚在1067里面probe的那些信号，有没有什么简单的方法可以实现

## 真实意图

WaveView how-to Q&A：已在 6 个 rate=1067 fsdb 波形里 probe 了一堆信号；准备再开 6 个 rate=10667 的波形；不想回原理图逐个重 probe，想直接复用 1067 上 probe 过的信号列表。纯 how-to 解释，无脚本产物（用户后续「没有找到 tcl console」显示其无 Tcl 入口 → session 在 assistant 询问澄清时被 user 取消，status=cancelled）。

## 对话流（6 msgs）

- **U0 (msg 1, user_input mode=act)**：上引原话（提出需求）。
- **assistant msg 8/12/16/19/23/27/31**：连续 7 轮 RAG API 检索（search_apis + get_api_details）+ thinking。检索覆盖：sx_display / sx_display_wave / sx_add_wave / sx_signal_add_mode / sx_signal / sx_save_session / sx_load_session / sx_save_signal / sx_first_panel / sx_next_panel / sx_first_line / sx_next_line / sx_get_wave_fullname / sx_get_name / sx_get_wave / sx_find_wave_in_file / sx_open_sim_file_read / sx_current_sim_file / sx_current_wv / sx_get_wdf / sx_clear_wv / sx_export_data / sx_export_fsdb / sx_reload。并调用 skill `waveview-fsdb-readerV2-2`（V2-2 FSDB reader 上下文）。
- **assistant msg 31（金标准最终答复）**：给 3 方案，**方案一（Tcl 脚本提取+重放）最推荐**：
  - Phase 1 提取：`sx_current_wv` → `sx_first_panel $wv`/`sx_next_panel` 循环 → `sx_first_line $panel`/`sx_next_line` 循环 → `sx_get_wave_fullname $wv $line` 取全路径名 → 写 `/tmp/signal_list_1067.txt`。
  - Phase 2 切文件：`sx_clear_wv` 清当前；手动 File→Close 旧 / Open 新 fsdb；或 `sx_open_sim_file_read <path> replace|append`。
  - Phase 3 重放：读 signal list → `sx_signal_add_mode single` → `foreach sig {sx_display $sig}` 逐个显示（新文件须有同名信号）。
  - 方案二 `sx_save_session`/`sx_load_session`：**有局限**——session 存 FSDB 绝对路径，load 会去开旧文件而非新文件，不适用本场景。
  - 方案三（被截断）：`sx_export_data` 导出信号值（离线分析向，非显示复用）。
- **U (msg 32)**：「没有找到tcl console」→ 用户无 Tcl 入口。
- **assistant msg 33**：`ask_question` 工具问澄清（ACE 单行命令行？Window 菜单？终端 `wv -ace_no_gui`？）→ tool_result `code_sidecar_sigterm` → session cancelled。

## 金标准事实（从 RAG get_api_details 原文提取 · 判分依据）

- `sx_get_wave_fullname`：签名 `sx_get_wave_fullname <list_obj> <line_obj>`；返回 `<name_string>`（信号全层级名）。**复用机制的 crux**：从已显示的 line object 反查全路径名，才能在新 fsdb 上 `sx_display` 重放。
- `sx_current_wv`：`sx_current_wv <wv_obj>` → 返回当前 waveview object；后续 panel/line 遍历的起点。
- `sx_first_panel`/`sx_next_panel`：面板链表遍历；`sx_first_line <panel_obj>`/`sx_next_line`：line 链表遍历。
- `sx_display`：`sx_display <list_of_sig_obj | signal_name_pattern_string> -auto_new_wv -noreload -showalias -pwc`；显示一组信号、返回 line object 列表；按 `sx_signal_add_mode` 加入。
- `sx_signal`：`sx_signal <name_pattern_string> <level=n>` → 返回匹配通配符的信号名列表（仅当前已打开文件）；可作 `sx_save_signal`/`sx_export_data` 入参。
- `sx_signal_add_mode`：`single | overlap`（默认 SINGLE）；新信号加入 waveview 的方式。
- `sx_open_sim_file_read`：`<file_name_pattern_string> <filepath> <replace|append> <spice_pwl> connect_files=true|false` → 读开波形文件，返回 file object 列表。
- `sx_save_session`：保存当前会话到文件（含 FSDB 绝对路径）。
- `sx_load_session`：加载 Custom WaveView session 文件。
- `sx_export_data`：导出选中信号值到文本文件（X 轴范围由 `sx_export_range` 定，精度由 `sx_set_precision` 定）。
- `sx_clear_wv`：清当前 waveview 内容。
- `sx_save_signal`：把信号保存到波形文件。

## 复用策略分类（用于 manual-grounded answer-extraction）

| 策略 | primary enabler | 适用 |
|---|---|---|
| extract_replay | `sx_get_wave_fullname`（提取全名）+ `sx_display`（重放） | 跨 fsdb 复用 probe 列表（用户场景，方案一最推荐） |
| session_save | `sx_save_session` | 整个 waveview 会话持久化（含路径，切文件不适用） |
| session_load | `sx_load_session` | 恢复已存会话 |
| export_values | `sx_export_data` | 导出信号采样值到文本（离线分析，非显示复用） |
| wildcard_match | `sx_signal` | 通配符匹配当前文件信号名（批量 display 前置） |

## 资产设计（A档 trace-faithful + 隐藏 B/B2/B3 反硬编码）

- **A（真实输入）**：`waveview_manual_A.md`（综合复用手册：含全 5 策略命令）+ `question_A.txt`（用户原话逐字）。
  - 期望 primary_command = `sx_get_wave_fullname`（extract_replay 策略的 crux enabler）。
- **B（session_save）**：`waveview_manual_B.md`（强调 sx_save_session/load/write_open/save_preference）+ `question_B.txt`「把当前 waveview 的会话保存到一个文件里，下次直接加载恢复所有显示的信号」。期望 primary = `sx_save_session`。
- **B2（export_values）**：`waveview_manual_B2.md`（强调 sx_export_data/fsdb/range/precision + 提取链）+ `question_B2.txt`「把当前已经显示的信号的采样值导出成一个文本文件方便离线分析」。期望 primary = `sx_export_data`。
- **B3（wildcard_match）**：`waveview_manual_B3.md`（强调 sx_signal/display/add_mode/load_signal/find_wave_in_file）+ `question_B3.txt`「在当前打开的波形文件里用通配符匹配所有名字以 ADDR 开头的信号」。期望 primary = `sx_signal`。

反硬编码标记：A 的 `sx_get_wave_fullname` 不得作为 B/B2/B3 的 primary；A 的策略标志 `extract_replay` 不得泄漏进 B（session_save）的 command_parameters。

## 套用原型

r711 AetherNetHighlightQA-001 manual-grounded answer-extraction 范式 + r880 WvSignalDisplayGuideQA-001 WaveView 同族 howto Q&A（同族补充 case，区别：r880=信号显示/格式化，本例=probe 信号跨波形复用）。判分 16 条断言 a-p（k_check=k_rationale=16 ≥8 硬闸门过）。
