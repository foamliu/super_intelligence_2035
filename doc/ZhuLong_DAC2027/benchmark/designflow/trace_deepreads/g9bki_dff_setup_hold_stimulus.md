# 深读笔记 · g9bki · DFF 建立/保持时间激励构造

- session: `1795052008686_g9bki` · user `e0029308` @ `hfeg0pkn001` (10.129.2.10) · mc=353
- domain: spice_sim · keywords: hspice:1649;virtuoso:1343;netlist:336;rtl:90;verilog:27;pex:11
- 467 msgs (messages.json 1.3MB + archive 27MB)；agent = deepseek-v4-flash，lead

## 用户真实意图（trace verbatim）

用户在 35H 数字库（VDD=0.75V，HSPICE `.LIB tt_mos_varactor_dbc`）上搭一个 GUI 化的 Hspice 自动验证工具（`Auto_Check.py`），核心 spice 诉求集中在 DFF 时序测量激励的构造：

- U[88]：「有个问题，我想仿真一个D触发器的建立时间和保持时间，那我应该如何搭建放置环境呢」
- U[109]：「我说错了没事仿真环境，就是我放置的激励如何建立呢」
- U[117]：在 `4_CLC_Truth_table_sim.sp` 添加第二行 `.LIB ".../35H_DBCFS_Model_PF_v0d1_Rev03.lib" tt_diode_bjt_dbc`，要求 GUI Corner 下拉再加一个，**同时保证 DFF 的 sp 文件也做相同的修改**。
- U[444]：「DFF的sp生产脚本，并没有把Corner2的路径与Corner1统一，我希望gui输入的那个路径能用到全部的Corner上」

agent 在 MSG 116 给出参数化激励模板（trace verbatim，核心交付物）：

```spice
.param CDLY = 0.8n          ; 扫描变量: D 跳变相对时钟沿的时间
.param TCP  = 1.0n          ; CP 上升沿时刻
.param EDT  = 1.0n          ; 沿后采样 Q 的时刻
VDD vdd 0 DC=0.75
VPP vpp 0 DC=0.75
VSS vss 0 DC=0
VBB vbb 0 DC=0
VCP CP 0 PULSE(0 0.75 {TCP} 50p 50p 0.9n 4n)
VD  D 0 PWL(0 0  {TCP-CDLY} 0  {TCP-CDLY+50p} 0.75)
XDFF D CP Q 1 vdd vss vbb vpp <DFF型号>
.MEASURE TRAN Q_CAP MAX v(Q) FROM={EDT} TO={EDT+0.1n}
```

并给出 setup/hold 扫描判据：CDLY 大 → D 提前 → 锁到 Q=1；CDLY 小/负 → D 晚于沿 → 锁不到 Q=0；临界点即 setup/hold。

MSG 126 agent 把四个 DFF deck（`4_DFF_Hold_sim.sp` / `4_DFF_Trigger_sim.sp` / `4_DFF_Reset_sim.sp` / `4_DFF_Scan_sim.sp`）各补第二行 `.LIB`（同模型库、`tt_mos_varactor_dbc` + `tt_diode_bjt_dbc` 两 corner）。

## 环境与不可便携点

- 真实 PDK：`/apps/imctf/models/35H/model_local/35H_DBCFS_Model_PF_v0d1_Rev03/hspice/35H_DBCFS_Model_PF_v0d1_Rev03.lib`（在用户机 10.129.2.10 上，SUT 沙盒无此 PDK）→ 不可便携。
- HSPICE：`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`（.75 沙盒可用，已验证 exit=0 + `.lis` 产出 + `.MEASURE` 解析）。
- DFF cell 在 35H PDK 内（`mydff`/`DFF_Hspice_inputs.txt` 运行期生成），沙盒无 → check 侧提供简化 TG-DFF（level-1 MOS）作 DUT。

## reframe 方案（portability-reframe + harness-for-teeth）

- 交付物 = 参数化 `dff_setup_hold_gen.py`：读 spec.json（VDD/TCP/EDT/CDLY/tr/tf/PWM/period/DFF cell+pin/两 corner 名+lib 路径/measure/tran）→ 生成 `setup_hold.sp`，含 `.param CDLY/TCP/EDT/VDDV` + VDD/VPP/VSS/VBB 电源 + `VCP PULSE` + `VD PWL(0 0 'TCP-CDLY' 0 'TCP-CDLY+tr' VDDV)` + `XDFF <pins> <cell>` + 两行 `.LIB` corner + `.tran` + `.MEASURE TRAN Q_CAP MAX v(Q) FROM=EDT TO='EDT+0.1n'`。
- check 在 hidden B 上：① 结构断言（B 参数忠实：VDD/TCP/EDT/CDLY/corner 名/DFF pin 全用 B 值，PWL 数据沿 = TCP-CDLY 数学正确，measure 窗口 = EDT..EDT+0.1n）② 真跑 HSPICE：check 侧写 `dut.inc`（TG-DFF + level-1 model），把生成 deck 的 `.LIB` 行替换为 `.inc 'dut.inc'`，跑 HSPICE，断言 job concluded + `q_cap=` 数值 measure 行存在 ③ early/late 两 CDLY 各跑一次，数据沿时间不同（反硬编码）④ 五假提交全 FAIL。
- 不要求 DFF 锁存方向（setup/hold 临界值）——那是 DUT 属性，非激励生成器职责；level-1 TG-DFF 锁存边界不锐，故 tooth 取「HSPICE 真跑 + q_cap 数值存在 + 结构 B 参数」组合，足以判真假交付。

## 验证（.75 沙盒实证）

- `metaencrypt` / `hspice` V-2023.12-SP1-1 在 .75 可用（`/apps/synopsys/SRB/...` + `/proj/shdc/cad/script/bin/`）。
- `/tmp/dff_test`：TG-DFF（互补栅 `tg d g gb s`）+ level-1 MOS + 上述激励 deck，`hspice -i tb.sp -o out` exit=0，`out.lis` 含 `q_cap= 381.2271m at= 2.5078n`（CDLY=0.8）/ `379.8789m`（0.2）/ `372.1079m`（-0.2）。job concluded + measure 解析 ✓。
- HSPICE 参数语法：`DC=VDDV`（裸参数，不可用 `{VDDV}`）、`PULSE(0 VDDV TCP 50p 50p 0.9n 4n)`、`PWL(0 0 'TCP-CDLY' 0 'TCP-CDLY+50p' VDDV)`（单引号表达式）、`.MEASURE ... FROM=EDT TO='EDT+0.1n'`。

## 判分牙来源

1. 结构：deck 含全部 trace 模板要素 + B 参数忠实（VDD/TCP/EDT/CDLY/corner/pin）。
2. 数学：PWL 数据沿时刻 = TCP-CDLY（解析后数值复算，stub 写死 A 值即不匹配 B）。
3. 真跑：HSPICE job concluded + `q_cap=` 浮点 measure 存在（subprocess on B）。
4. 反硬编码：early/late 两 CDLY 的数据沿时刻不同 + B≠A 全参数。
5. 反 stub：空/print-A/core-deleted/always-pass/hardcode-A 五假全 FAIL。
