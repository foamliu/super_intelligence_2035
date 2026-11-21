# Deepread: r966 — session 1794969685019_elb1i (rose3wang @ hfeg0pkn003, mc144)

## Trace Overview
- **Session**: 1794969685019_elb1i.messages.json
- **User**: rose3wang
- **Host**: hfeg0pkn003 (10.129.2.12)
- **mc**: 144, keywords: verilog:244;rtl:127;spectre:68;analog:26;netlist:18;synthesis:18;systemverilog:13;floorplan:13;synopsys:7;virtuoso:6;primetime:6;tempus:5;hspice:5;cadence:4;genus:3;.spi:3;innovus:2;bandgap:1
- **Domain**: A-pure digital (verilog+rtl+synthesis+systemverilog+synopsys+primetime+tempus+genus+innovus 主导; spectre/hspice/cadence/virtuoso 次要)
- **Messages**: 201
- **File size**: 778KB
- **Scan source**: ssh_eda_search_20261121_151844 (fresh A-domain candidate, top500, mc144)
- **Dup-keyword siblings**: bltup/lq85o/xzcak (同 rose3wang, 同 keywords, ~10min 间隔, 均未 ledgered; elb1i 取最早时间戳)

## 真实用户意图 (逐字, clean questions)

7 大主题, 29 clean user questions:

### Phase 1 (U#1-U#2, m#0-m#35): Efuse.v → EFUSE.v 同步 + Verilog 壳子
- U#1: "把model /proj/lacaa/V0/workdir/rose3wang/rtl/efuse/Efuse.v 的修改同步到/proj/lacaa/V0/workdir/rose3wang/DK/release/verilog里面的EFUSE.v文件"
- U#2: 同上 (重复) + "写一个verilog壳子" (附 pin table: VDDA/VSSA/VMEAS/VREF/VD_EN/CHIP_EN/CONV_EN/CLK_IN/TEST_EN/TR<37:0>/RSV<5:0>/DO<10:0>/RDY/TPOD<3:0>/TPOA/TPIA<1:0>/TPID<1:0>)
- assistant: cp Efuse.v → EFUSE.v; 创建 EFUSE_TOP.v wrapper (port table → module 壳子, 内部例化 Efuse)
- 注意: shell-runner 只能写 /home/rose3wang, 经 cp 脚本中转

### Phase 2 (U#4, m#36-m#49): vsensor.v testbench
- U#4: "/proj/lacaa/V0/workdir/rose3wang/rtl/vsensor/tv1/vsensor.v 写一个tb,只给个clk和例化端口，激励我自己写就行"
- assistant: 读 vsensor.v, 发现 line 69 bug (DOUT 应为 DO), 创建 tb_vsensor.v (25MHz clk #20 toggle, 40ns 周期, 全端口例化, VDDA=1/VSSA=0/VMEAS=0.78 初值, 激励留空)

### Phase 3 (U#5-U#14, m#50-m#69): $recovery/$setup/$hold 时序检查语义 Q&A ★ 本 case 提炼源
- U#5: "模拟模块有上电下电顺序的检查 能写成$setup的格式吗？lib必须要一一对应吗？"
  - assistant: $setup 数学上可(参数交换)但语义不建议; 电源时序用 $recovery/$removal (异步控制信号); SDF 反标 RECOVERY 不会反标到 $setup; STA 工具只找 recovery/removal; Liberty 对应 recovery(); 不必逐条对应($period 仿真专属)
- U#6: "上电后到使能 这些是输入，lib中不一定有体现"
  - assistant 修正: 纯 input→input $recovery 在 lib 中通常不需要也没有 (lib pin 只管 pin-to-pin 可传播路径); 电源顺序由 UPF + PG 约束 + Verilog 仿真 $recovery + SPICE 验证分工
- U#7: "VDD CHEN CVEN TR依次上电（从输入到输入），功能结束后再依次退出，怎么写时序检查 都是input" ★
  - assistant: 全部用 $recovery 统一写, 上电 posedge/下电 negedge, ref(先)→test(后); specparam Tvdd2chen=5000/Tchen2cven=50000/Tcven2tr=100/Ttr2cven=100/Tcven2chen=100/Tchen2vdd=5000; 放 specify 块便于 SDF 反标
- U#8: "输出RDY拉低后，input CVEN才能拉低 能写吗" ★
  - assistant: $recovery(negedge RDY, negedge CVEN, Trdy2cven=10, ); IEEE 1800-2017 §31.3 事件表达式可以是任何端口信号不限 input/output; 推荐 $recovery 不用 $hold (参数反着易搞反)
- U#9: "$recovery(posedge CHEN, posedge CVEN, Tchen2cven, ); 不是power信号，是input;要在EN为1的时候检查怎么写；用$recovery还是$setup写好一点"
  - assistant: &&& 条件事件筛选符: $recovery(posedge CHEN &&& EN, posedge CVEN &&& EN, T); $recovery vs $setup 数学等价但语义/违例报告/SDF反标/Liberty对应/业界习惯全偏向 $recovery
- U#10: "$hold用途也是关于时钟？" → 是, $setup/$hold 经典对 (D→CLK); $hold(posedge CLK, D, Thold)
- U#11: "后端的STA flow" → floorplan→placement→CTS→routing→signoff 各阶段 SPEF 反标 + SDC
- U#12: "$period(posedge CLK_IN &&& enable, 36);能检查不能 36<t<44的范围吗？" → 不能, $period 只有下限无上限 (IEEE 1800-2017 §31.3.3.1)
- U#13: "$recovery(posedge CHIP_EN, posedge CONV_EN, 100); 改成VDDA=1条件下检查" → $recovery(posedge CHIP_EN &&& VDDA, posedge CONV_EN &&& VDDA, 100, ); 可链式 !VSSA
- U#14: "Error-[SE] Syntax error ... token is ',' ... $recovery(posedge CHIP_EN &&& VDDA &&& !VSSA,posedge CONV_EN..." → 根因: &&& 是 SystemVerilog 语法, .v 文件默认 Verilog 模式不识别; 方案A: -sverilog 或改 .sv; 方案B: always 块手动检查 ($rose/$realtime/$error)

### Phase 4 (U#15-U#24, m#70-m#85): efuse Liberty timing arc + char.tcl + SPICE model 作用
- U#15-U#23 (重复9次): "efuse 的lib需要出哪些timing arc;char.tcl怎么配"
  - assistant: CLK_IN(posedge)→DO[63:0] 寄存器输出弧; char.tcl 配置; Liberty recovery()/removal() for 异步控制
- U#24: "/proj/lacaa/TV1_FS_Virtuoso/model/current/spectre/35H_DBCFS_Model_PF_v0d1_Rev05.lib model在仿真时的作用"
  - assistant: SPICE model library = 晶体管字典 (MOS/电阻/电容/二极管/三极管 电压温度电气特性); characterization 时用

### Phase 5 (U#25-U#26, m#86-m#185): ECO Dummy 生成 (从 mapped netlist)
- U#25: "rtl 设计中加些dummy,便于后期ECO. 一般怎么加dummy呢 举个例子"
  - assistant: Spare Gate Array (spare cells 预放, 综合保留, ECO 时接线索); (* dont_touch *)
- U#26: "/proj/lacaa/V0/workdir/rose3wang/synflow/psensor/flow_top_psensor/results/top_psensor.mapped.v 用里面用到的cell ,写一个ECO Dummy"
  - assistant: grep 提取 cell types (DBCP51H180L6W25T5SVT 库); 经多次 python/heredoc 脚本迭代 (转义问题); 最终 eco_dummy_psensor.v 134行: SDFRPQD1×8/DFRPQD1×4/SDFSNQD1×2/INV×16/BUF×8 + NAND/NOR 变种; portless all-tied (输入 1'b0, CD 1'b1, 输出悬空)
  - 注: 此 sub-task 与 r965 (9ofdu tsensor eco_dummy) 同 user 同项目同类型 — intent-dup, 故本 case 不取此 sub-task

### Phase 6 (U#27-U#28, m#186-m#200): top_psensor wrapper + ECO dummy cell 选择
- U#27: "这4个rtl (cnt_window/gen_process/osc_cnt/top_psensor) 应该怎么加 eco_dummy_psensor.v 不要修改上面4个原文件"
  - assistant: 新增 top_psensor_wrapper.v, 例化 top_psensor + eco_dummy_psensor, eco 浮空端口 tie-off
- U#28: "根据这4个rtl dummy加哪些cell好一点？" → 分析 4 RTL 逻辑特点 (cnt_window 分频/FSM, osc_cnt counter, gen_process, top_psensor 顶层) 针对性配 ECO cell
- U#29: "要" → 确认

## Case 合成决策

**选取 sub-task**: Phase 3 电源时序 $recovery 时序检查生成 (U#7 + U#8 + U#9 + U#13)
- **原因**: (1) A-pure digital (Verilog 时序检查语义) (2) trace-faithful (assistant 产出完整 specify 块) (3) 牙口足: $recovery 方向(上电posedge/下电negedge) + ref→test 顺序 + RDY↓→CVEN↓ output控制input + &&& 条件门控 + specparam (4) 与 r965 EcoSpareGenProduce-001 (同 user eco_dummy) 无 intent-dup (不同 sub-task) (5) 可泛化: spec JSON 驱动, hidden B 不同信号名+gate 字段测通用性

**Case 类型**: produce-task (脚本生成器), A=pwrseq_spec_A.json (psensor, gate=null), hidden B=pwrseq_spec_B.json (vsensor: VDDA/VDD2/CHEN/CVEN, gate={VDDA on CHEN/CVEN})

**k = 16**: A-side ①-⑧ (specify/$recovery/3上电方向/RDY→CVEN/下电逆序/specparam) + B-side ⑨-⑭ (specify/VDDA→VDD2/&&&门控/CHEN/CVEN&&&VDDA/negedge/反泄漏B≠A) + meta ⑮-⑯ (确定性/module+endmodule)

## trace gold (可提炼的判定知识)

1. **$recovery 语义**: $recovery(reference_event, data_event, limit, notifier) — data_event 须在 reference_event 之后 ≥ limit 发生; ref→test 顺序永远是先发生→后发生
2. **电源时序用 $recovery 不用 $setup**: $setup 是 data→clock 同步时序; $recovery 是异步控制信号时序; SDF 反标 RECOVERY 不会反标到 $setup; STA 工具只找 recovery/removal
3. **上电 posedge / 下电 negedge**: $recovery(posedge VDD, posedge CHEN, T) 上电; $recovery(negedge CVEN, negedge CHEN, T) 下电; 上电下电都用 $recovery (不用 $removal, 参数顺序一致不易搞反)
4. **output 控制下电合法**: $recovery(negedge RDY, negedge CVEN, T) — IEEE 1800-2017 §31.3 事件表达式可是任何端口信号不限 input/output
5. **&&& 条件门控**: $recovery(posedge CHEN &&& EN, posedge CVEN &&& EN, T) — &&& 是 SystemVerilog 语法, .v 文件需 -sverilog 编译否则 syntax error
6. **$period 只有下限无上限**: IEEE 1800-2017 §31.3.3.1
7. **纯 input→input $recovery 不需要 lib 对应**: lib pin 只管 pin-to-pin 可传播路径; 电源顺序由 UPF + PG + Verilog 仿真 $recovery + SPICE 分工
8. **specparam 放 specify 块**: 便于 SDF 反标覆盖, 不需改 RTL
