# 深读笔记 · 1792746530652_5erm4 · shanliny @ hfeg0pkn001 (10.129.2.10) · verification A-档候选

## trace 元信息
- session: 1792746530652_5erm4 (149 msgs, 4MB — 含 sp_sram.v 200KB + top.sv/interface.sv 内嵌附件)
- user: shanliny (pkn001, 10.129.2.10)
- mc=80, systemverilog tools: 569
- trace_source: {user: shanliny, host: hfeg0pkn001, session_file: 1792746530652_5erm4.messages.json, match_count: 569}
- 工具调用: run_approved_command 多次 (vcs/vlogan 编译验证), editor 多次 (改 top.sv/interface.sv)

## 用户原话（A-档任务说明 = USER#0 逐字原文）
> 告诉我如果我需要将top.sv连接上sp_sram.v，应当怎样改？
> --- Attached files ---
> [sp_sram.v → .../uploads/sp_sram.v]
> [top.sv → .../uploads/top.sv]

后续用户轮（27 个 user turns 中抽样）：
- 多轮为催促/确认（「继续」「嗯」），无新独立需求
- 部分轮为编译报错后追问，属根因/修复轮（rule2 违反，不取）

**A-档合规判定 (规则 #2)**：USER#0 用户只给目标（如何把 top.sv 连上 sp_sram.v）+ 附件，未指出根因、未给修复方案 ⇒ CLEAN ✓

## 附件（真实原文）
1. **sp_sram.v** (200KB) — 单口 SRAM 行为模型 `sram_sp`，21 端口：
   - `CLK, CEB, WEB, A[ADDR_WIDTH-1:0], D[DATA_WIDTH-1:0], Q[DATA_WIDTH-1:0], BWEB[DATA_WIDTH-1:0]`
   - `TEST, BYP, WA, WAT[1:0], WAV[1:0], RA[1:0], WT[1:0], RT[1:0]`
   - `VSS, VDD (inout), CRSLE, CRSLA[CRA_WIDTH-1:0], CRSRE, CRSRA[CRA_WIDTH-1:0]`
   - 参数: ADDR_WIDTH=7, DATA_WIDTH=16, DEPTH=128, CRA_WIDTH, LAT, CENTER_DECODE, TIMING_DEBUG
   - 含 task sram_op_exec / timing_check / mem_init；specify 块；column redundancy 直连 pin
2. **top.sv** (4.8KB) — SV 验证测试台 `top_tb`：
   - `include package.sv + interface.sv + transaction_*/ref_model/strategy_*/driver/monitor/env.sv`
   - 时钟生成 `logic clk; initial clk=0; forever #(current_clk_half_period) clk=~clk;`
   - DUT 线网: `dut_ce_n, dut_we_n, dut_addr[ADDR_WIDTH-1:0], dut_wdata, dut_q, dut_bwen`
   - VCD 观测线网: `CLK, CEB, WEB, A_IN, D_IN, BWEB_IN, CRS0E/CRS1E, CRS0A/CRS1A, Q_REF, Q_EN, TEST, WA_E, RA_E, WAT/WAV/WT/RT_VAL, TRKWT, BYP, ERROR_FLAG`
   - 接口例化: `sram_if #(ADDR_WIDTH, DATA_WIDTH) sram_vif (.clk(clk), .fp(fp), .dut_rdata(dut_q))`
   - `assign` 把接口信号接到模块级线网
   - **注释掉的 DUT 例化占位**（`// your_sram_design #(...) dut_inst (...)`）← 用户要填的就是这块
3. **interface.sv** — `sram_if` 接口（sram_vif），含 ce_n/we_n/addr/wdata/bwen/test/crs0e/crs0a/crs1e/crs1a/ra_e/wa_e/wat/wav/wt/rt/trkt/byp/rdata_expected/rdata_valid/error_flag

## gold（用户接受的助手分析）
ASSISTANT#32 (msg32): 对 top.sv 连接 sram_sp 的 SV 集成分析 ——
- 端口别名映射: `CLK→clk, CEB→dut_ce_n, WEB→dut_we_n, A→dut_addr, D→dut_wdata, Q→dut_q, BWEB→dut_bwen`
- 缺失信号需声明（TEST/BYP/WA/WAT/WAV/RA/WT/RT/CRSLE/CRSLA/CRSRE/CRSRA 等 dut_ 线网 top.sv 未声明）
- parameter 覆盖: `.ADDR_WIDTH(ADDR_WIDTH), .DATA_WIDTH(DATA_WIDTH)`
- 例化模板: `sram_sp #(.ADDR_WIDTH(ADDR_WIDTH), .DATA_WIDTH(DATA_WIDTH)) dut_inst (.CLK(clk), .CEB(dut_ce_n), ...)`

## 合成 B（A-档 faithful，B 档合成隐藏输入）
真实 SUT 远程路径不可达 → B 档合成对偶验证场景：
- **b_sram.v**: `sram_dp_2p` 双口 SRAM，10 端口（`clk/cke/csb/web/oe/addr/din/bwen/q/test`），命名异于 A（小写 + cke/csb/web/oe 而非 CEB/WEB），行为模型自包含（无 tech lib）
- **b_top.sv**: `b_top_tb`，dut_* net（`dut_cs_n/dut_we_n/dut_cke/dut_oe/dut_addr/dut_din/dut_bwen/dut_q/dut_test` + 模块级 `clk`），含 `sram_dp_if` 接口例化 + assign，注释掉的 DUT 例化占位
- **b_if.sv**: `sram_dp_if` 接口（cke_s/cs_n/we_n/oe_s/a_in/d_in/bw_n/test_s/...）
- 别名表 PORT_ALIAS 覆盖: CLK→clk, CSB→dut_cs_n, WEB→dut_we_n, CKE→dut_cke, OE→dut_oe, A→dut_addr, D→dut_din, BWEB→dut_bwen, Q→dut_q, TEST→dut_test

## 交付物形式
`gen_sv_dut_inst.py`（通用 SV 模块 DUT 例化生成器）—— 而非静态分析文本，以支持 B 档隐藏输入的泛化判定。
- parse_module: 正则解析 module 名/参数/端口（方向/类型/位宽）
- parse_testbench_nets: 抓 TB 全部 logic/wire/reg 声明
- find_or_create_net: 按端口别名表匹配 dut_ net，缺失则声明
- 输出: 缺失 net 声明 + `dut_inst` 例化 + parameter override

## 判分（15 条 a-o，L2-static）
- a/b: zip 含 gen_sv_dut_inst.py + py_compile
- c-g: [B] 非空 SV / 含 sram_dp_2p dut_inst / 10 端口全连 / 缺失 net 已声明 / 位宽 AW·DW
- h/i: [B] vlogan 0 错 + vcs elaborate 产 simv（L2 静态编译验证，.75 VCS R-2020.12）
- j/k: [B] .q(dut_q) / 无 A 专有 token
- l: [A] 候选在真实 sp_sram.v 运行产非空（泛化守卫）
- m: 源码无 A/B 模块名字面量（反硬编码）
- n: [B'] 端口随机重排结构一致
- o: 合法 SV 含 dut_inst

## 自验（.75 GREEN）
- REF: check() → PASS（vlogan 0 错，vcs 产 simv 827KB）
- 5 negatives 全 FAIL，4 distinct conds {c, d, e, m}：
  - naive_empty → c（不产输出文件）
  - core_deleted → e（只连 5 端口，缺 .addr(）
  - naive_only_summary → d（输出无 sram_dp_2p）
  - fake_print_expected → m（源码含 'sram_dp_2p' 字面量）
  - naive_hardcode_b → m（源码含 'sram_dp_2p' 字面量）
- §4.9 三次 false 提交: naive_empty→c, fake_print_expected→m, core_deleted→e 全 FAIL ✓
- 本地（无 VCS）复验: REF 过 a-g 止于 h（vlogan not found），negatives c/d/e 复现一致 ✓

## 难度定位
- L2-static（vlogan+vcs 静态编译门），新 case 不上 L3
- rolling-20: 本 case 无 cline 实跑，rolling pass rate 不变（5/20=25%，在 20-30% 目标区间）
