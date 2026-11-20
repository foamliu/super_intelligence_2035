# Deepread — r667 stewieg jia3m routing track finder

- **session**: `1794295625900_jia3m.messages.json` (stewieg @ hfeg0plg89, 217 msgs, match_count=300)
- **scan**: `ssh_eda_search_20261116_072610/summary.tsv`, C-keyword single-host revival candidate
- **ledger history**: r537 parked「peek REJECT (Q&A/sim/run-existing/done)」→ 2026-11-15 用户令 pool_reaudit 标「可造」(旧判 Q&A 现合法) → r666 second-look peek → revival → case

## 用户轮（20 user turns，217 msgs）
- U#1-2: meta Q&A（what is cdl/gds, how to input chinese）
- U#3-4: LVS Q&A（BCENTERCA 层 LVS input/output 设置, 为何错比别人多）
- U#5-7: PEX/寄生 Q&A（标准寄生格式提取做什么, 用实际数据解释寄生, spfb 形式）
- **U#8-11: 核心 PRODUCE-TASK**
  - U#8: 「我现在用aether连线画版图到时候经常遇到线道资源紧张到问题，如何开发一个脚本帮我找出线道，主要用于中层金属，大概是输入金属到线宽后自动根据DRC分析出可以利用到线道，并高亮出来」
  - U#9 细化: 「分析金属层的范围就是该金属上层最上下左右的边界，同时有了间距和线宽之后，要按照固定的间距和线宽显示出每一个线道，而不是一整个范围」
  - U#10: 「以脚本代码的形式输出给我，并给出 aether 脚本代码的使用方法和快捷键设置方法，按 aether 风格设计一个简洁的操作 UI，之后整体复盘一下这个设计，优化改善一些不合理的地方」
  - U#11: 「有这个代码怎么运行啊，给出具体具体的操作方法」
- U#12-13: SGD 层修 DRC Q&A（贴 DRC rule，问冲突/修复）
- U#14: who r u
- U#15-20: SGD/NSD/PSD DRC rule Q&A（贴 rule，问冲突/修复/选择性跑）

## assistant 产物（U#8-11 对应）
经 5 次 editor 修订（msg 83/85/87/89/91）产 `/home/stewieg/.cline/skills/eda_agent/pyaether/cxmt_find_routing_tracks.py`（最完整版 msg85, 7591B）。核心算法：
1. `pitch = wire_width + spacing`
2. 方向：`metal_index % 2 == 0` → 水平扫描（按 y 步进）；奇数 → 垂直扫描（按 x 步进）
3. 轨道基线从 `cell_low + spacing` 起，按 `pitch` 步进，循环条件 `基线 + wire_width <= cell_high - spacing`
4. 每条轨道：障碍若在 y 方向（水平扫描）与 `[y_low - spacing, y_high + spacing]` 相交 → 投影到 x 轴 `(exl - spacing, exh + spacing)` 为 blocked 区间
5. `merge_intervals` 合并 blocked 区间
6. 从 `x_start = cell_xl + spacing` 起，对每个 blocked `(bstart, bend)`：若 `x_start < bstart - 0.001`，`free_end = min(bstart, cell_xh - spacing)`，若 `free_end - x_start >= wire_width` → 输出空闲段 `(x_start, y_low, free_end, y_high)`；`x_start = max(x_start, bend)`
7. 末尾：若 `x_start < cell_xh - spacing - 0.001` 且 `(cell_xh - spacing - x_start) >= wire_width` → 输出最后空闲段
8. 垂直扫描对称（x/y 互换）
9. 高亮 `highlight_free_tracks`（GUI，沙盒不可达）

## revival 判定（r537 误杀纠正）
r537 旧判「Q&A/sim/run-existing/done」把整个 session 归为 Q&A 不可造——**系旧 weak 筛子误杀**。second-look peek 实证：
- U#8-11 是清晰的 produce-task（开发脚本 + 交付代码 + 使用方法）
- assistant 产真实 gold 脚本（5 次修订，可解析算法）
- 算法核心（pitch 扫描 + 障碍 clearance + 区间合并 + 空闲段输出）是**纯计算**，可 B档 reframe 为纯 stdlib（剥离 pyAether GUI 依赖）
- check() 可写「牙」：结构化 JSON + reference 重算逐条匹配 + 不变式（边界余量/障碍 clearance/最小段长/确定性/反硬编 B 方向反转）

## B档 reframe
真实脚本依赖 pyAether GUI（dbGetTrueOverlaps / aeCellViewBBox / dbGetDrdMinSpacing）沙盒不可达 → reframe 为通用纯 stdlib `routing_track_finder.py`：读 JSON config（cell_bbox/wire_width/spacing/metal_index/obstacles）→ 计算 → 结构化 JSON。
- **asset A**：config_A.json（bbox 0,0,30,20 / ww 2.0 / sp 1.0 / metal_index 2 水平 / 4 障碍）+ cxmt_find_routing_tracks_A.py（trace 原物作算法/schema 参考）+ prompt.md（用户原话 U#8-10）+ task_brief.md
  - 期望：horizontal / pitch 3.0 / total_tracks 6 / 14 free_segments / total_free_length 126.0
- **hidden B**（反硬编，方向反转）：config_B.json（bbox 0,0,24,18 / ww 1.5 / sp 0.8 / metal_index 3 **垂直** / 5 障碍）
  - 期望：vertical / pitch 2.3 / total_tracks 10 / 14 free_segments / total_free_length 83.6
- **hidden B2**（退化）：config_B2.json（bbox 0,0,8,6 / ww 1.0 / sp 0.5 / metal_index 2 / 1 障碍）
  - 期望：horizontal / pitch 1.5 / total_tracks 3 / 6 free_segments / total_free_length 15.0

## check() 16 条件 a-p
①(a) zip+py_compile ②(b) B 跑通合法 JSON+8 顶层键 ③(c) direction==vertical（反硬编 A horizontal）④(d) pitch==2.3==ww+sp ⑤(e) total_tracks==10 ⑥(f) free_segments list+每项 6 键类型正确 ⑦(g) 段数==14 ⑧(h) summary.total_free_segments==len ⑨(i) total_free_length==sum==83.6 ⑩(j) 每段 length>=wire_width ⑪(k) 每段在 [cell_low+sp, cell_high-sp] 边界内 ⑫(l) 障碍 clearance 无相交 ⑬(m) free_segments 与 reference 逐条匹配 within 0.01 ⑭(n) 确定性 3x ⑮(o) 反硬编 sentinel（B≠A: direction/pitch/total_tracks）⑯(p) B2 退化 total_tracks==3/段数==6/length==15.0

## 自验
- gold_ref.py PASS 16/16 ✓
- 4 negatives（empty_shell/print_expected_A/core_deleted/always_pass_stub）全 FAIL ✓，first_fail labels b/c/g/g（3 distinct ≥3 ✓）
- §4.9 三假（empty-shell/print-expected/core-deleted）全 FAIL ✓
- k_rationale = k_check = 16 ≥ 8 GATE PASS ✓
