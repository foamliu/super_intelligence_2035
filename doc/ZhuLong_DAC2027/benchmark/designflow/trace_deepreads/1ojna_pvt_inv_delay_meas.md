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

## case 设计（实际交付，与 on-disk check.py/ref 一致）

**EDA-Eval-DesignFlow-PvtInvChainDelayMeas-001**（spice_sim / synthesized / L1，k=12）

- **deliverable**: `pvt_delay_meas_gen.py`，CLI `python3 pvt_delay_meas_gen.py <testbench.sp> <meas_config.json> <measure_output.mt0> <out_deck.sp> <out_report.json>`
- 读 testbench.sp：提取 PVT corner 链（base .lib + 各 .alter）与各 corner pvcc；定位 `VClk IN 0 pulse(...)` 单脉冲激励行；定位空 .measure 段
- 读 meas_config.json：in_node/out_node/vdd_param/vth_fraction/n_edges/inverting/corner_meta{temp,vcc}
- 生成 out_deck.sp：单脉冲→连续方波 `pulse(0 pvcc <tRst_delay> tr tf 'tCK-tr' '2*tCK')`（**保留符号 2*tCK 周期，不数值代入**）；.measure 段插 2*n_edges 条 `.measure tran td_rise_<i>`/`td_fall_<i>`（inverting=true：trig v(IN) rise=<i> → targ v(OUT) fall=<i>；trig v(IN) fall=<i> → targ v(OUT) rise=<i>，阈值 pvcc*vth_fraction）；保留 .alter 链 + .end
- 解析 measure_output.mt0（CSV: measname,corner,value）：按 corner 聚合 → td_rise_avg/td_fall_avg
- 写 out_report.json：{corners:[{name,temp,vcc,td_rise_avg,td_fall_avg,edges:[...]}], summary:{min_rise,max_rise,spread_rise,min_fall,max_fall,spread_fall}, n_edges}

## 资产（实际）

- A: delay_test.sp（25 级，单脉冲，5 corner TT/FF/SS×-40/25/125℃）+ netlist.sp（invFx1_sub_Fifo subckt + 25 XI_ 实例）+ meas_config.json（n_edges=4/inverting=true/5 corner_meta）+ measure_output.mt0（measform=3 CSV）+ output_format_spec.txt + task_brief.md
- 隐藏 B1: testbench.sp + meas_config.json(3 corner/3 edges) + measure_output.mt0 + netlist.sp
- 隐藏 B2（反硬编码）: 4 corner(tt_85_pre/ff_m40_pre/ss_85_pre/fs_125_pre)/5 edges，值≠B1
- check 只跑 B1+B2，subprocess 真跑候选，check 内 _expected_report() 独立重算期望（1% tol）

## 12 断言 (a-l)

a zip 含 pvt_delay_meas_gen.py ｜ b py_compile ｜ c B1 exit0 出 out_deck.sp+out_report.json ｜ d deck .measure trig v(IN)/targ v(OUT) ｜ e deck 同时含 rise=/fall= ｜ f B1 连续方波(2*tCK 周期)+td_* 量测数≥2*n_edges ｜ g B1 deck 覆盖 3 corner(tt_25/ff_85/ss_m40)+.alter≥2 ｜ h B1 report 每 corner td_rise_avg+td_fall_avg ｜ i B1 report 延迟值与 mt0 真值 1% 一致 ｜ j B1 report summary 含 min/max/spread(rise+fall) ｜ k 反硬编码 B2 4 corner+10 measures+值≠B1 ｜ l B2 report 延迟值与 B2 mt0 真值一致(交叉输入)

## 自验
ref PASS 12/12 + 6neg(naive_empty/only_print/empty_shell/no_measure/hardcoded_b1/ref_core_deleted)全 FAIL + §4.9 三假(empty_shell→c/only_print→c/ref_core_deleted→d)全 FAIL + 确定性 B1 连跑 3 次 k=12 一致 + byte-sync sha256=d7346cfd(14137B) + jsonl B 237→238, ledger covered 238→239(spice_sim 191→192)
