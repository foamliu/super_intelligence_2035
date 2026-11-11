# 深读笔记 · 1790241096712_s0t3i · WaveView panel 高度 bug

- trace_source: user=rongjiez / host=hfeg0pkn005(10.129.2.14) / session=1790241096712_s0t3i.messages.json / mc=23
- domain: spice_sim (waveform 分析工具链)
- 文件位置(.75 经 ssh 10.129.2.14): /home/rongjiez/.cline/data/sessions/1790241096712_s0t3i/1790241096712_s0t3i.messages.json (349439B)
- agent: zhulong (deepseek-v4-flash), 9/24-9/28 对话

## 用户真实意图（原话节选）
`/home/rongjiez/jira_dev/mpqa/mp_2/ModelQA_0924170807/openSignal.tcl这个tcl文件是通过下面这个脚本生成的：[openWave.pl]...然后会通过wv -ace_gui打开这个tcl，我发现打开的波形只有前7个PANEL的HEIGHT被正确设置为150，最后两个PANEL高度非常低，是什么原因`

## 关键产物
1. **openWave.pl**（Billy.Luo 2021-12-09）：Perl 脚本，扫描 waveDir 下的 FineSim(*#*.sw0)/PrimeSim(.dc)/Hspice(.sw@\*)/Nanospice(.output/*.sw*) 波形，生成 openSignal.tcl，再 `bsub -q wv_queue wv -ace_gui` 打开 WaveView。
2. **openSignal.tcl**（生成结果，9 个 PANEL）：每文件一组 `set dbFile / sx_open_sim_file_read / sx_display / wv_select_waveview / wv_select_wv_item WV1.PANEL{i}:1.HEIGHT / wv_set_size WV1.PANEL{i}:1.HEIGHT 150`。9 个 panel 全部设了 HEIGHT 150，但用户观察到最后 2 个 panel 偏矮。

## assistant 诊断与修复（终解）
**根因**：`wv_select_wv_item` + `wv_set_size` 在循环内逐条输出，紧跟 `sx_display` 之后。WaveView 基于 Tcl/Tk 事件模型，可滚动区域中尚未"realize"的 panel widget 未完成几何布局计算，`wv_set_size` 作用于未实现的 widget 会被默认高度覆盖——前 7 个 panel 已实现故生效，最后 2 个尚未实现故保持默认矮高度。

**修复**：两阶段——
- Phase 1：循环内只输出 setup 命令（dbFile/sx_open/sx_display/wv_select_waveview），把 `wv_select_wv_item` + `wv_set_size` 暂存到 `@heightCmdList`（不再立即 print OUT）。
- Phase 2：循环后先 `print OUT "update idletasks\n"`（强制 Tk 处理所有空闲回调 = 几何布局 + widget realization + 显示更新），再 `print OUT @heightCmdList` 输出全部高度命令。

**为什么 `update idletasks` 能解决**：处理所有挂起 idle callbacks（geometry propagation / widget realization / 显示更新），此时再 `wv_set_size`，高度能正确作用于全部 panel（含可滚动区不可见的）。`after 5 destroy .` 只安排 5ms 回调不阻塞；`update idletasks` 只处理 idle 不触发 `after` 定时器，窗口不会提前销毁。

## 造题方向（L2 spice_sim）
- A 档 trace-faithful：用真实 openWave.pl + 生成出的 9-panel openSignal.tcl 作附件；prompt 写真实场景（rongjiez/ModelQA_0924170807/wv -ace_gui/前7对后2矮）。
- hidden B：不同 waveDir（如 idvg 子目录 + 14 个 .sw0），验泛化（不同 panel 数）。
- check 真跑候选 Perl 脚本生成 Tcl，解析结构断言（`update idletasks` 位置 / `wv_set_size` 全 panel / A≠B 防硬编码）。
- 12 条断言；negative = 原脚本(inline 无 update idletasks) / only_print / hardcode14。
