# trace_deepread: ru6mx — DC UPF-440 低功耗综合 (e0046913@hfeg0pkn003, mc=108)

**scan source**: ssh_eda_search_20261105_192825/summary.tsv
**keyword profile** ($6): `rtl:391;verilog:315;synopsys:204;dc_shell:184;virtuoso:162;netlist:58;synthesis:47;skipper:22`
**tools col** ($7, sparse): `58 netlist 47 synthesis 17 hspice 10 calibre` → 仅按 $7 排序会被埋没（r150-r172 BLOCKER ③ 的盲点）
**真实域判定**: digital (dc_shell:184 + synopsys:204 + synthesis:47 = 真·DC 综合)，virtuoso:162 是 incidental（用户读 netlist 时附带）。

## trace 概览
- 144 msgs (78 user / 66 assistant), 803KB, 10 个真实用户轮（其余为 plugin/policy/file-list tool_result 注入）。
- ip=10.129.2.12 (hfeg0pkn003), 用户 e0046913，工作区 `/proj/lacaa/TV1_TestChips/CXTV1_DBC001A/frontend/SramPwrTcqGrp0/`。

## 真实用户轮（A档候选）

| # | ts | 原文（逐字） | A档? | 备注 |
|---|----|------|-----|------|
| 0 | 1793795209488 | `/proj/lacaa/.../syn/dc.log 分析第695行的warning产生原因 Warning: PG netlist to UPF conversion is not done, as there is no UPF data. (UPF-440)` | ✅ 提需求 | clean A-faithful，log 分析 |
| 1 | 1793844227243 | `我确实要做真正的低功耗/UPF 综合，需要在综合前补充电源意图（提供 .upf 文件并执行 load_upf）。帮我写出这个upf并说明思路。` | ✅ 提需求 | **最佳 A档候选** — UPF 生成 |
| 2 | 1793845366498 | `/proj/lacaa/TV1_digital/simdir/yutingq/lowpowerDC_for_IP 分析此目录下现有配置，我是否可以通过source run去顺利跑综合？如果想读入上述upf文件，又该如何修改设置？` | ✅ 提需求 | flow 配置分析 |
| 3 | 1793846156434 | `检查现有环境是否可以正常跑综合` | ✅ | 太泛 |
| 4 | 1793846537748 | `/proj/lacaa/TV1_digital/simdir/yutingq/lowpowerDC_for_IP 分析本次综合情况` | ✅ | 综合结果分析 |
| 5 | 1793847145127 | `/proj/lacaa/.../scripts 分析现有脚本是否可以解决上述问题` | ✅ | 脚本审查 |
| 6 | 1793847564887 | `如何查看我的可用LSF?什么情况下需要用LSF跑任务？` | ✅ | LSF 问答（泛） |
| 7 | 1793847744315 | `Nov  5 11:01:59 2026 41700 3 3.4.0 lsb_init: initenv_:fopen(/etc/lsf.conf) failed... 分析报错` | ✅ 给根因 | LSF 报错分析 |
| 8 | 1793848206938 | `/apps/synopsys/SRB/dc/V-2023.12-SP5/linux64/syn/bin/common_shell_exec: error while loading shared libraries: libpulse-mainloop-glib.so.0... 解释报错原因` | ✅ 给根因 | DC 启动 lib 缺失 |
| 9 | 1793848572008 | `[sudo] password for e0046913: e0046913 is not in the sudoers file...` | 🚫 报错粘贴 | 无任务意图 |

## 设计上下文（assistant 深读产出）

**设计**：`SramPwrTcqGrp0`（TV1 DBC001A 功耗测量组），顶层 RTL `SramPwrTcqGrp0.v`。
**电源架构**（13 PG 端口）：
```
inout VDD, VDDI0..VDDI5 ;  // 独立供电测量 6 个 "big" SRAM
inout VSS, VSSI0..VSSI5 ;
```
- 主域 TOP (VDD/VSS)：所有 glue logic（Decode4to16, tm_measure_Tcq*, vmux*/wsmux13to1）+ 6 个 "main-VDD" SRAM (i3/i4/i5/i7/i9/i11)。
- 6 个独立功耗域 PD_I0..PD_I5：每个对应一个 "big" SRAM macro（hcsp8kx160cm4b8c1r1_.._i0 等），独立 VDDIx/VSSIx 供电。
- 全部 0.75V always-on → 跨域信号同电压，**不应插 level shifter**。

**UPF-440 根因**（USER#0）：DC 默认开 power-aware，看到 PG netlist 想做 PG→UPF 转换，但流程从未 `load_upf`（dc.tcl/dc_setup.tcl 里 upf 相关全注释掉）→ 跳过转换打 warning。无害信息类警告，不中断综合。

## assistant 交付的 UPF（USER#1 答案，ASST#21-24）

完整 UPF（5731 字符）结构：
1. `set_design_top SramPwrTcqGrp0`
2. `create_supply_port` × 13（VDD/VSS/VDDI0-5/VSSI0-5，`-direction in`）
3. `create_supply_net` × 14（VDDN/VSSN/VDDI0N..VSSI5N）
4. `connect_supply_net ... -ports {...}` × 13（net 绑顶层端口）
5. `create_power_domain TOP -include_scope` + `set_domain_supply_net TOP -primary_power_net VDDN -primary_ground_net VSSN`
6. `create_power_domain PD_I0..PD_I5 -elements {<sram_inst>}` + `set_domain_supply_net PD_Ix -primary_power_net VDDIxN -primary_ground_net VSSIxN`
7. （注释掉的）`create_power_state_set all_on` 单 0.75V 状态
8. `save_upf .../SramPwrTcqGrp0.upf.check`

6 个 "big" SRAM 实例名：
- PD_I0: `hcsp8kx160cm4b8c1r1_dbc_big_pwr_tcq_g0_i0`
- PD_I1: `hc1prf1kx144cm2b2c1r1_dbc_big_pwr_tcq_g0_i1`
- PD_I2: `hc2prf1kx72cm4b4c1r1_dbc_big_pwr_tcq_g0_i2`
- PD_I3: `hd2prf1kx72cm4b4c1r1_dbc_big_pwr_tcq_g0_i6`
- PD_I4: `hd1prf1kx144cm2b2c1r1_dbc_big_pwr_tcq_g0_i8`
- PD_I5: `hdsp8kx160cm4b8c1r1_dbc_big_pwr_tcq_g0_i10`

## case 合成评估（A档 USER#1 → UPF 生成）

**难度**：L2-static（UPF 语法 + 电源架构推理，不需真跑 DC）。
**A档任务说明**：USER#1 逐字原文（"我确实要做真正的低功耗/UPF 综合...帮我写出这个upf并说明思路"）。
**资产 A**：`SramPwrTcqGrp0.v`（顶层 RTL，含 PG 端口 + SRAM 实例）+ dc.log 片段（UPF-440 warning 上下文）+ dc_setup.tcl 片段（被注释的 upf 设置）。
**隐藏 B**：换一个不同 PG 端口数 / 不同 SRAM 数的设计（如 4 个独立供电域而非 6 个，或 2 组电压而非单电压），防硬编码。
**check.py 思路**（≥8 条断言）：
- ①(a) submit.zip 含 `<design>.upf` 一件
- ②(b) UPF 语法合法（`pyupf`/正则：`set_design_top` 存在 + 每个域有 `set_domain_supply_net`）
- ③(c) `create_supply_port` 数 == RTL PG 端口数（B 侧）
- ④(d) `create_power_domain TOP -include_scope` 存在
- ⑤(e) 每个独立供电 SRAM 实例都在某个 PD_Ix 的 `-elements` 里（B 侧 SRAM 名不同）
- ⑥(f) 每个非主域 PD_Ix 的 primary_power_net != VDDN（独立供电）
- ⑦(g) `connect_supply_net` 把每个 supply_net 绑到对应顶层端口
- ⑧(h) 无 level shifter 插入（同电压，不应有 `add_level_shifter`）— 静态扫描 UPF 文本
- ⑨(i) `set_design_top` 指向 B 侧真实 top（不是 A 的 SramPwrTcqGrp0）
- ⑩(j) UPF 可被 `python3 -c "import upf_parser; parse(...)"` 或简单 regex 解析无异常
- ⑪(k) 主域 supply_net == VDDN/VSSN
- ⑫(l) 隐藏 B 的独立供电域数 == B 设计的独立 SRAM 组数

**可行性**：✅ 真·digital/DC 综合，A档 faithful，L2-static（纯 UPF 文本生成 + 静态断言，无 .75 工具依赖）。下一轮可合成交付。

## 重要发现：BLOCKER ③ 盲点修正（$7 vs $6 排序）

r150-r172 的 BLOCKER ③ "digital fresh 池结构性枯竭" **部分基于错误的排序方法**：
- 旧法：按 $7 (tools col, sparse, 只列 calibre/virtuoso/hspice/netlist/synthesis 等少数工具词) 排序 → 高 mc 的全 analog-dominant（netlist/schematic 多）。
- **新法**：按 $6 (keywords col, 完整词频) 的 digital 词频和排序 → 发现 19 个 digi>ana 的 fresh，其中 ru6mx(c084j/qo3pd 等) 含真 dc_shell/synopsys/verilog 命中。
- **结论**：BLOCKER ③ 需降级 —— 真 digital fresh 候选**存在**（经 $6 重排后可见），但 $7 排序掩盖了它们。下轮起应按 $6 digital 词频排序选料。
- 本轮 ru6mx 已 claim，r174 起可基于此发现继续出 case（不再被 BLOCKER ③ 阻塞）。
