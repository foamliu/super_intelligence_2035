# Deepread — 4w3lo (e0039786 @ hfeg0pkn003, mc58, characterization)

**session**: `1794815686198_4w3lo.messages.json` (49 msgs / 134KB / 2026-11-16 07:54–08:11, deepseek-v4-flash, completed)
**user_prompt**: `<user_input mode="act">动态功耗扫描</user_input>` (dynamic power scanning)
**cwd**: `/home/e0039786/Desktop` (only Aether config files: 1.lyp / lib.defs / libManager.log — no waveforms/reports present)

## 对话流（关键转折）

1. **msg0-4**: 用户问"动态功耗扫描"。agent 列工作目录→只有 Aether 工程配置，无 FSDB/报告。请求澄清。
2. **msg5 ask_question**: 用户选 "在 Aether/pyAether 环境下做动态功耗分析（自动开关翻转、activity/Power 分析 API）"。
3. **msg6-17**: agent 多轮检索 pyAether API（power/activity/toggle/waveform/电流/EM/netlist），结论：**pyAether 无现成动态功耗 API**。命中的只有 se 系列 GUI 触发器（`seGuiRunSimulation`/`seGuiCrtSimProbe`/`seGuiSimSelectSignals`/`seGuiTraceNet`/`seGuiShowNetlist`，全部无参，基于当前打开的 schematic/SE 触发 GUI 动作，不回读波形做数值积分）和 EM/电流密度 Emy* 系列。
4. **msg18 ask_question**: agent 给出两条口径（① 总功耗=VDD×mean(i(VDD)) ② 每 net 翻转活动度=0.5·CL·VDD²·f·α），用户选 "两者都要"。
5. **msg20-22**: agent 核对 seGui* API 详情（确认无参、返回 bool），结论：pyAether seGui* 只编排（建探针→设输出→跑 sim），数值计算必须从 dump 的 FSDB 里算。
6. **msg23-30**: agent 写出 **`dynpower_scan.py`**（数值引擎）+ **`gen_demo.py`**（演示数据生成器），用 python-runner 跑通验证：
   - VDD=3.3, f=1MHz, CL=20fF, 窗口 [0,1ms]
   - supply mean 10mA → P_dyn = 33.0 mW（= 3.3V × 10mA ✓）
   - net_a 1MHz 方波 → 1999 toggles, alpha=1.999, P_net=217.7 nW
   - net_b 500kHz → 999 toggles, alpha=0.999, P_net=108.8 nW
7. **msg32-40**: 用户透露 "我的cell在Virtuoso里" → `test_3/Ring_OSC_TOP_Rev06_ulvt/layout`（环振 TOP）。agent 转 SKILL 路线，检索 SKILL API（cpf/dbGetTermSupplySensitivity/geAddNetProbeFromTo 等功率意图/探针 API），给出 Virtuoso/Spectre 下的对应方案（`getData("i(vdd)" ?result "tran")` + `average` + `cross`）。
8. **msg42-48**: agent 尝试 SKILL 沙箱 `dbOpenCellViewByType("test_3" "Ring_OSC_TOP_Rev06_ulvt" "layout" nil "r")` → **Connection refused** (10.129.35.73:57301，SKILL 桥接服务未启动)。用户选 A（启动桥接），重试仍 refused。session 末尾卡在等桥接启动。

## 交付物（agent 实际写出，已 scp 确认 5653B）

**`dynpower_scan.py`** 结构：
- `read_wave(path)` — 读 (t,value) CSV，跳 header/`#`/`t`/`time` 行
- `trapezoid_integral(times, vals, t0, t1)` — 梯形积分，窗口边界线性插值，窗口外跳过
- `total_dynamic_power(supply, vdd, t0, t1)` — P = VDD × (integral/[t1-t0])，返回 (P, i_avg, win)
- `toggle_count(vals, vdd, lo=0.5)` — 归一化 v/vdd，阈值 0.5 判 1/0，统计**所有**状态变化（上升+下降都算）
- `net_dynamic_power(path, vdd, freq, cl, t0, t1)` — alpha = toggles/(span×freq)，P_net = 0.5·CL·VDD²·f·alpha
- main: argparse（--vdd/--freq/--cl/--t0/--t1/--supply/--net(append)/--out），报告含 [A] 总功耗 + [B] 每 net + [B] 热点 TOP 排序

**关键实现细节（判分器要复刻）**：
- toggle_count 统计**所有**翻转（`cur != prev`），不只上升沿
- alpha 用 `span = t1-t0`（窗口），但 toggle_count 遍历**整个** CSV（不按窗口过滤）→ 本 case 让 net CSV 只覆盖 [t0,t1] 以消除歧义，窗口齿只放在 supply 上
- supply 梯形积分**按窗口**截取（边界插值）→ 本 case 让 supply_B 延伸到窗口外测试此齿

## reframe（程序化）

**case = EDA-Eval-DesignFlow-DynPowerScanProduce-001**：`dynpower_scan.py <CLI>` 按契约读 supply + net CSV，算总动态功耗（窗口梯形）+ 每 net 翻转活动度（归一化阈值0.5，统计所有翻转，alpha=toggles/(span·freq)，P_net=0.5·CL·VDD²·f·alpha）+ 热点 TOP。L1 纯 Python 标准库，domain=characterization（环振动态功耗表征）。

**A**（可见，对齐 demo）：VDD=3.3/f=1MHz/CL=20fF/窗口[0,1ms]，supply 均值 10mA→33mW，2 nets（net_osc_out_A 1MHz / net_div_clk_A 500kHz）。
**hidden B**（六重 anti-hardcode）：①VDD 1.2 vs A 3.3 ②freq 2e9 vs A 1e6 ③CL 5fF vs A 20fF ④窗口 [10ns,510ns] vs A [0,1ms] ⑤4 nets vs A 2，名全异（ro_stage_out/ro_tap1/ro_tap2/clk_buf_out）⑥supply ~2mA vs A ~10mA，且 supply 延伸到窗口外（pre 100mA inrush + post decay）测窗口齿。

**near-dup 自查**：现有 B case 中静态分析器/报告生成器类（BuildStepCacheClassify/Mt0CornerPivot/MosComparaReport/CornerBlockGen/ProbeCovAnalyzer）—— 无动态功耗波形扫描+翻转活动度计算 near-dup。本 case 独特齿：supply 窗口梯形积分 + net 翻转活动度 alpha 计算。

**check.py 12 条**：①(a)zip+py_compile+size>200 ②(b)B exit0+非空report ③(c)报告头含B参数 ④(d)P_dyn==VDD·i_avg窗口值 ⑤(e)i_avg==窗口oracle ⑥(f)窗口生效(P_dyn匹配窗口值非全范围值,supply延伸窗口外全范围3.4mA vs窗口2.0mA差>30%) ⑦(g)每net翻转==oracle(精确整数) ⑧(h)每net alpha==oracle ⑨(i)每net P_net==oracle ⑩(j)热点排序==oracle ⑪(k)anti-hardcode(A net名缺席+B net名在场+A VDD3.3不出现) ⑫(l)3-seed打乱--net顺序,toggles/alpha/P_net三次一致且==oracle。

**3 negs**: neg_empty(→a/b) / neg_print_only(硬编A报告→c/d/e/f/g/h/i/j/k/l 10齿) / neg_core_removed(真解析B但只数上升沿+忽略窗口→d/e/f/g/h/i/l 6齿)。§4.9 三假全 FAIL ✓。
