# trace_deepread — 1792746530652_5erm4 (shanliny@hfeg0pkn001, mc=80)

- session: `/home/shanliny/.cline/data/sessions/1792746530652_5erm4/1792746530652_5erm4.messages.json`
- 149 msgs, 4.1MB. provider cxmt-deepseek-flash / deepseek-v4-flash. cwd /home/shanliny.
- keyword profile: systemverilog:569; verilog:115; rtl:28; synopsys:26; aether:10; analog:9; synthesis:1.
- domain: **verification**（形似 UVM 的 SRAM 验证 SV 环境）。

## 用户意图流（user 轮摘要）
- U[0] 「告诉我如果我需要将top.sv连接上sp_sram.v，应当怎样改？」+ 附件 top.sv / sp_sram.v → **提出需求轮（A-档合格）**：把 testbench top_tb 接上真实 SRAM DUT。
- U[1] 继续之前的问题。
- U[33] 「为什么我用 make all 启动程序时本来应该启动的 monitor 并没有在 log 文件里显示检验结果？」→ 转入 monitor 调试。
- U[35] redundancy_all_states/rand 策略下 monitor 对比结果异常挪位。
- U[37] top.sv 是参考、dut 是被检验；monitor 在有冗余时对比周期挪一位。
- U[39] monitor 只采样到 addr=0x00。
- U[45] redundancy all states 时 strategy_ext 地址在变，但 top.sv 采样 A_IN 一直 0x00。
- U[53] 冗余/bypass 当前周期强制置 x；read 下个周期显示——纠正 assistant 把 rdata 放下周期的错误。
- U[55] read 后紧接 repair 希望跳过 read 对比，直接对比 repair 输出强制 x。
- U[57] VCS Error-[XMRE] Cross-module reference resolution error transaction_ext.sv token 'drv_cb'。
- U[59] 「cr 后面不一定接 write/idle，给个干净彻底的办法」。
- U[62] 改后错更多（XMRE token 'rdata_expected'）。
- U[64] execute 和 next execute 同时修改 expected/valid 会报错。
- U[66] 贴 interface sram_if 片段。
- U[68] 「去做吧，monitor.sv 和 interface.sv 的 mon_cb 加 crs0e/crs1e/crs0a/crs1a/byp input，让 Monitor 自己判断 CR/Bypass 场景并正确比对」。
- U[86] 在操作数组内取消冗余/bypass 之前一个操作的 valid 来修 bug。
- U[115] 「三个派生类加标记+next execute 查标记怎么不写完整」。
- U[119] 改后某种操作顺序下 monitor 超前一个周期。
- U[125] 把预先编排好的操作执行前通过文件输出（识别操作+显示 q/bitw/d/a/rdata_valid）。
- U[139] 报错。
- U[145] random 跑下来 monitor 仍有挪位问题。

## 附件清单
- U[0]: top.sv (4389B), sp_sram.v (200472B, sram_sp 单口 SRAM 行为模型 v14.3l)
- U[33]: driver.sv env.sv interface.sv makefile monitor.sv package.sv ref_model.sv strategy_base.sv strategy_ext.sv transaction_base.sv transaction_ext.sv
- U[121]/U[145]: log（1.4MB / 641KB）、strategy.seq (182KB)

## sram_sp 端口表（sp_sram.v line 770-950，逐字）
```
module sram_sp #(.ADDR_WIDTH,.DATA_WIDTH,.DEPTH,...,.CR_ADDR_WIDTH_L,.CR_ADDR_WIDTH_R,...)
( input [ADDR_WIDTH-1:0] A, input [DATA_WIDTH-1:0] D, input CLK, input CEB, input WEB,
  input [DATA_WIDTH-1:0] BWEB, output [DATA_WIDTH-1:0] Q,
  input [3:0] WT, input [4:0] RT, input TEST, input BYP, input WA,
  input [1:0] WAT, input [1:0] WAV, input [1:0] RA,
  inout VSS, inout VDD,
  input CRSLE, input [CR_ADDR_WIDTH_L-1:0] CRSLA, input CRSRE, input [CR_ADDR_WIDTH_R-1:0] CRSRA );
```

## top_tb 现有线网（与 sram_sp 端口的对应）
- dut_addr[ADDR_WIDTH-1:0]→A, dut_wdata[DATA_WIDTH-1:0]→D, clk→CLK, dut_ce_n→CEB, dut_we_n→WEB, dut_bwen[DATA_WIDTH-1:0]→BWEB, dut_q[DATA_WIDTH-1:0]→Q
- TEST→TEST, BYP→BYP, WA_E→WA, WAT_VAL[1:0]→WAT, WAV_VAL[1:0]→WAV, RA_E[1:0]→RA
- **WT_VAL[1:0] → WT[3:0]**（恒定 2→4 失配，必须补齐 {2'b00,WT_VAL}）
- **RT_VAL[1:0] → RT[4:0]**（恒定 2→5 失配，必须补齐 {3'b000,RT_VAL}）
- VSS/VDD → 1'b0/1'b1（inout supply，常量驱动）
- CRS0E→CRSLE, CRS0A[CRA_WIDTH-1:0]→CRSLA[CR_ADDR_WIDTH_L-1:0], CRS1E→CRSRE, CRS1A→CRSRA
  （CD=0 时 CR_ADDR_WIDTH_L/R == CR_ADDR_WIDTH == clog2(DATA_WIDTH) == CRA_WIDTH，位宽天然对齐）

## 取用决定
- 本 case 只取 **U[0] 首轮「布线」子任务**（A-档 trace-faithful produce）。
- 后续 U[33]+ 的 monitor 挪位/冗余/bypass 调试 = L3 多轮 debug，trace 末尾用户未明确接受一个单一最终产物（仍在迭代），不适合做 A-档金标准；可作为另一条 B-档/L3 case 的素材，本轮不开。
- 难度：L1-static（纯 SV 结构解析判分，无仿真）。判分 14 断言，关键区分点 = WT/RT 位宽补齐 + 参数化布线（反硬编码 16/128）。
