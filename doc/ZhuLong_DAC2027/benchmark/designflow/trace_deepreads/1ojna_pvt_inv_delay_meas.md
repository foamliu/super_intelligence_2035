# 深读笔记 — 1ojna PVT inverter-chain delay measurement

- **anchor**: `1794292585610_1ojna`（curryxu @ hfeg0plg07 / hfeg0plg99 / hfeg0plg08，mc=148，mtime 11-10 14:36–15:04）
- **session 文件**: `/home/curryxu/.cline/data/sessions/1794292585610_1ojna/1794292585610_1ojna.messages.json`（116418B，29 msgs，agent=lead）
- **台账**: shard B，已 claim（11-10 16:26），domain=spice_sim
- **扫描源**: fresh-window 80 plg/pfn/hfeahpc 主机直扫 → fresh_hits_1110_1506.tsv（530 fresh/176 unique/108 un-ledgered）

## 用户轮（3 user turns，逐字）

- **U#0/#1**（合并输入，第一段被截断后续补全）：「我有一个时钟信号CLK，我用他去采样一笔data，采完得到的dataout。同时这个CLK经过了一段延时得到了CLK_Delay,我还想用CLK_Delay在dataout刚出来的时候就将它采到，那么我用什么方式可以让dataout和CLK_Delay的上升沿对齐呢」
  → 概念性 how-to（时钟延迟对齐/重采样），**非 produce-task**，assistant 给了 PLL/DLL、Replica Delay Path、数字延迟线+校准 等方案讲解。
- **U#5**（**本轮选料轮 · produce-task**）：「帮我看一下IN和OUT之间的delay在不同PVT下有多大\n`/proj/m2701/V0_DDR4/workdir/curryxu/simulation/delay_test.sp`\n`/proj/m2701/V0_DDR4/workdir/curryxu/simulation/delay_test/hspiceD/schematic/netlist/netlist`」
  → **CLEAN produce-task** ✓：提需求（测 IN→OUT delay 在不同 PVT 下），给了网表/参考 deck 路径，**未给根因/修复方案**。A-faithful 合规（仅 key/token/密码掩码，无敏感字段）。

## assistant 工具链（msg #6–#28）

1. msg#6 尝试 `run_commands`（被禁）+ `read_files` 读 `delay_test.sp` 与 `.../netlist/netlist`
2. msg#9 read_files 返回空（policy 拦截 raw shell），assistant **凭返回的电路结构分析**：
   - `delay_test.sp` 驱动 **25 级 `invFx1_sub_Fifo` 反相器链**（XI_0~XI_24），IN→OUT 奇数级反相
   - HL22 22ULL 工艺，NMOS W=130n/L=30n，PMOS W=230n/L=30n
   - **当前问题**：无 `.meas` 语句 → 仿真跑完无 delay 数值；激励 VClk 仅单脉冲，边沿太少无法多次测量取平均
   - 计划：① 改激励为连续方波（多边沿）② 加 `.meas tran` 测 IN 上升/下降沿到 OUT 对应跳变沿的 delay（每 corner 测 4 边沿 + 平均）③ 提交仿真 ④ 读结果分析 PVT 差异
3. msg#9/13/17 多次尝试 `run_approved_command`/`list_allowed_files`/`get_agent_policy_status`：policy engine 强制 enforcing，`dynamicFileRoots` 限 `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/curryxu/simulation`，`writableRoots` 排除 `delay_test.sp`
4. msg#23 assistant 准备 editor 改 `delay_test.sp` 激励：`VClk IN 0 pulse(0 pvcc 'tRst_delay+4*tck+1.5*tck' tr tf '3*tck-tr' '6*tCK')` → `VClk IN 0 pulse(0 pvcc 0 tr tf 'tCK-tr' '2*tCK')`（单脉冲→连续方波）
5. msg#24/26 editor 写入被 `writableRoots` 拒（`/proj/...` 与 `/rundata/...` 均不可写）
6. msg#27/28 `list_allowed_files /home/curryxu` 探查可写目录 → **session 在此结束，未产出最终 deck/结果**

## 金标准判定

- trace 末尾**无用户实际接受的产物**（assistant 被 policy 阻塞，未写出最终 deck，未跑仿真）→ 不能取 A-faithful 金标准
- 按 trace **文档化需求 + 电路结构** 做 **B-synthesized L1 复刻**：
  - 电路：25 级反相器链 IN→OUT（奇数级反相），HL22 22ULL，NMOS W=130n/L=30n PMOS W=230n/L=30n
  - 需求：测 IN→OUT 在不同 PVT 下的传播延迟
  - assistant 的修复方案（连续方波激励 + `.meas tran` 4 边沿 + 平均 + PVT corner sweep）作为金标准结构
- 真实 `delay_test.sp` 在 `/proj/m2701/...`（curryxu 所有，e0031982 无权限读，已验证 NOACCESS）→ 合成代表性 base netlist（25 级 invFx1_sub_Fifo，单脉冲 VClk，.param pvcc/tCK/tr/tf）

## case 设计

**EDA-Eval-DesignFlow-PvtInvDelayMeas-001**（spice_sim / synthesized / L1，k=14）

- **deliverable**: `pvt_inv_delay_meas_gen.py`，CLI `python3 pvt_inv_delay_meas_gen.py <base_netlist.sp> <spec.json> <out_deck.sp> <out_report.json>`
- 读 base_netlist.sp（反相器链 subckt + XI_ 实例 + .param pvcc/tCK/tr/tf + 单脉冲 VClk）→ 解析 n_stages（XI_ 计数）/ in_node / out_node / params
- 读 spec.json（corners[] {name,temp,vdd,process} / stimulus{tCK,tr,tf,n_edges} / measure{rise,fall,n_samples} / model_lib / in_node / out_node）
- 生成 out_deck.sp：
  - `.lib "<model_lib>" <base process>`
  - `.param pvcc=<base vdd> tCK=... tr=... tf=...`
  - 连续方波激励 `VClk IN 0 pulse(0 pvcc 0 tr tf 'tCK-tr' '2*tCK')`（**反单脉冲**）
  - 反相器链 subckt + XI_ 实例（从 base 提取，verbatim）
  - `.tran <tstep> <n_edges*tCK>`（tstep=tr/10）
  - `.meas tran td_rise_k`（k=1..n_samples）：trig v(IN) val=pvcc/2 rise=k targ v(OUT) val=pvcc/2 rise=k + `.meas td_rise_avg param=avg`
  - 若 measure.fall：`.meas tran td_fall_k` fall=k + `.meas td_fall_avg`
  - 每 corner（除 base）一个 `.alter` 块：`.temp <temp>` + `.param pvcc=<vdd>` + `.lib "<model_lib>" <process>`
  - `.end`
- 生成 out_report.json：case_id / spec 镜像 / extracted{n_stages, in_node, out_node, original_stimulus_type} / deck_lines / has_tran / has_alter / n_alter_blocks / n_corners / n_measure_stmts / measure_names[] / has_rise_meas / has_fall_meas / square_wave_stimulus / n_edges / tran_tstop

## 资产

- A: base_netlist.sp（25 级，单脉冲）+ spec.json（3 corners TT25/1.0·FF-40/1.1·SS125/0.9，n_edges=8，n_samples=4，rise+fall）
- 隐藏 B1: hidden_b1_netlist.sp（15 级）+ hidden_b1_spec.json（4 corners，n_edges=10，n_samples=6，rise+fall）
- 隐藏 B2（反硬编码）: hidden_b2_netlist.sp（31 级）+ hidden_b2_spec.json（2 corners，n_edges=6，n_samples=3，rise only / fall=false）
- check 只跑 B1+B2，subprocess 真跑候选，断言 deck 结构 + report JSON 字段

## 14 断言 (a-n)

a zip 含 pvt_inv_delay_meas_gen.py ｜ b py_compile ｜ c B1 exit0 出 out_deck.sp+out_report.json ｜ d B1 deck 含连续方波激励（pulse ... 'tCK-tr' '2*tCK'，反单脉冲 tRst_delay）｜ e B1 deck 含 ≥2 条 .meas tran ｜ f B1 deck 含上升沿 delay 量测（trig v(IN) rise + targ v(OUT) rise）｜ g B1 deck .alter 块数 == n_corners-1 ｜ h B1 deck 含所有 corner 的 .temp（base+各 alter）｜ i B1 deck 含 VDD 变化（pvcc 多个不同值）｜ j B1 deck .tran tstop ≥ n_edges*tCK ｜ k B1 report 合法且 n_stages==XI_计数 / n_corners==spec / has_rise_meas==spec.rise / has_fall_meas==spec.fall / square_wave_stimulus==true ｜ l 反硬编码 B2 deck != B1 且 report.n_stages==B2 XI_计数 / n_corners==B2 spec / .alter 数==B2 corners-1 ｜ m 确定性 B1 连跑 2 次字节一致 ｜ n B1 deck 含下降沿 delay 量测（spec.fall=true ⇒ trig v(IN) fall + targ v(OUT) fall）
