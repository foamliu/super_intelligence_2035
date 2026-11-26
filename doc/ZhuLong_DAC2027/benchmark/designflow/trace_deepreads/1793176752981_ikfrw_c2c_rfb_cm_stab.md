# deepread — 1793176752981_ikfrw (joeyl @ hfeg0plg49, mc=34, spice_sim)

## trace_source
- user: joeyl · host: hfeg0plg49 · session_file: 1793176752981_ikfrw.messages.json · match_count: 34
- real_task_summary: 统计 finesim 45-corner tran 结果中 Tran_RFB vs Tran(NON-RFB) 两个目录里 v(xi_wck_c2c_19.out) 在 2n~5n 窗口的 avg 电平，对照 RFB 相对 NON-RFB 是否在 PVT 下稳定共模电平（mean±std 跨 corner 比较）。

## 用户意图（原话）
- U1: `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/m2701/C2C 这是目录，其下Tran_RFB&Tran内有45corner的tran结果，请帮我统计两者v(xi_wck_c2c_19.out)这点在2n～5n间的avg电平，旨在对照RFB相对NON RFB是否有在PVT下稳定共模电平的作用。`
- U2-U5: 请继续 / 继续（agent 中途需要多轮催促，因脚本编辑器被外来内容污染、文件创建 ENOENT 等环境问题）

## agent 工具链（56 次工具调用，115 msgs）
- get_agent_policy_status / list_allowed_files：探查 `/rundata/.../C2C/{Tran_RFB,tran}` 两个结果目录
- read_files：读 netlist / 45corner.sp / mt0.csv → 确认 mt0.csv 只有电流/duty，无 v(xi_wck_c2c_19.out) AVG
- editor × 多次：写 `/home/joeyl/inspect_tr0.py`（探查 tr0 格式）→ `zhulong_c2c_probe.py` → `zl_c2c_probe.py`（正式解析脚本，唯一命名避免污染）
- run_approved_command × 多次：运行探查 + 正式解析

## 关键事实（agent 自述核实）
- **45 corner = 5 模型角（tt/ff/ss/fs/sf）× 3 温度（-40/45/130）× 3 电压（0.79/0.875/0.96）**，用 `.alter` 实现
- 两目录各有 46 个 `.tr0`（base + #1~#45），mt0.csv 的 `alter#1`=base run，`alter#(N+1)`=`#N.tr0`，temper 列验证了 corner 顺序
- `.tr0` 是 Synopsys 二进制格式，头部有 ASCII 变量类型码段（1=电压，8=电流），后接变量名段 + 二进制数据
- 需要自己解析 `.tr0` 取 `v(xi_wck_c2c_19.out)` 在 2n~5n 的 avg（mt0.csv 没有）

## 产物
- 解析脚本：`zl_c2c_probe.py` —— 解析二进制 tr0，定位 `xi_wck_c2c_19.out` 信号，按 2n~5n 窗口求 avg，对 45 corner × 2 目录共 90 个波形批量计算
- 对照统计：RFB vs NON-RFB 各 45 个 avg 的 mean/std，判断 RFB 是否 std 更小（稳定共模）

## 合成计划（B 档 · A 档不可行）
**A 档不可行**：真实 `.tr0` 是 Synopsys 二进制 + `/rundata/m2701/...` 项目私有 DDR4 设计，不可移植（同 VwlpPumpReport 理由）。
**B 档合成**：用可移植 level-1 NMOS HSPICE tran deck `c2c_cm_probe`，复刻**同一测量任务结构**：
- 子电路 `c2c_probe`（差分对 M1/M2 + 尾电流镜 Mbias/Mtail + 负载 RL），内部节点 `out` 即探针点；实例名固定 `xi_wck_c2c_19`，测 `v(xi_wck_c2c_19.out)` 在 2n~5n 的 avg
- **RFB 变体**：强反馈电阻 Rfb 从 out 接到 vref=vdd/2 分压器 → out 被钳到 ≈vdd/2，跨 PVT 只随 vdd 变（std 小）
- **NON-RFB 变体**：Rfb=1g（断开）→ out=vdd-I_tail·RL，I_tail 随 vto/temp/vdd 强漂移（std 大）
- 45 corner = 5 vto 角（0.45/0.48/0.50/0.52/0.55）× 3 temp（-40/45/130）× 3 vdd，用 `.tran sweep data=` 实现
- 候选脚本 `c2c_cm_probe.py <netlist> <config> <out_dir>`：对 rfb / nonrfb 两个变体（sed 改 rfb_r 参数）各跑一次 HSPICE，从 .lis 解析 45 个 AVG_CM，算 mean/std/min/max，产 report.json（corners / stats_rfb / stats_nonrfb / comparison / conclusion）
- A（可见）vs B（隐藏）：vdd 三档不同（A 0.81/0.9/0.99，B 0.79/0.875/0.96）、temp 三档不同、Rfb/RL/w 比例不同、probe 实例 sizing 不同 → 反硬编码
- check.py 14 条 a..n：a zip+compile / b B 跑出 report / c 5 节键 / d hspice_ran+.lis / e n_corners=45 / f 数值字段 / g RFB std<NON-RFB std（稳定结论） / h 45 个 avg 不全同（PVT 漂移） / i RFB mean 落合理带且 ≈vdd/2 / j 跨输入 A 也通 / k A/B vdd+temp+rfb_r 不同（反硬编码） / l 稳定因子 nonrfb_std/rfb_std>1 且有裕度 / m L2 独立重跑 HSPICE corner0 / n 重跑 avg 与候选偏差<5%
- 5 negatives：nosim_stub(@d 无 .lis) / constant_stub(@h 全同) / hardcoded_A_values(@h B 全同 A) / empty_report(@c 缺键) / ref_core_deleted(@b KeyError)
- domain: spice_sim · 难度 L2（真跑 HSPICE tran + 跨 45 corner 统计）· k_rationale==k_check==14
