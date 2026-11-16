# Deepread: reo1p — DDR6 ddr6_test.sv 期望值根因分析 (DEBT, r659 deepread, 待 r660 合成)

> **状态**: DEBT 1 (r660 合成). r659 deepread 闭合, 根因假说已定位至精确代码行, 待 r660 验证 read-expected 路径后合成 case.

## trace 溯源
- session: `1791191409174_reo1p` (dandans / hfhds201=10.129.32.75 / mc=113 / 64 msgs / 1.46MB / agent=lead)
- trace_avail: EXISTS on .75 本机 `/home/dandans/.cline/data/sessions/1791191409174_reo1p/1791191409174_reo1p.messages.json`
- domain: **verification / digital** (SystemVerilog testbench code-comprehension)
- **旧判定**: 未进 parked_reaudit (scan 命中但被 r651/r654 的"A-domain genuine 耗尽"结论漏掉 — 该结论基于 mc≥5 A-score≥20 子集, 未覆盖 dandans 的 verilog:549/sv:38 强 A-domain 信号). **r659 修正: .75 本机 A-domain 未枯竭, reo1p 等 8+ 条 fresh unledgered 候选存在.**

## 用户真实意图 (U#0 逐字)
> `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen 帮我解析下ddr6_test.sv文件，告诉我为啥在CRC没开的时候+MD_8b+1P6时，PSD0的dq5的D16-D23位期望值是0？`

= **analysis-Q&A / code-comprehension**: 解释为何在 CRC-off + MD_8b + X1P6 模式下, PSD0 的 dq5 D16-D23 位期望值是 0.
(按 11-15 任务初衷, analysis-Q&A 是合法真实用户意图, 可造.)

## trace agent 行为
- agent (lead) 用 read_files 分段读了 ddr6_test.sv (10950 行) + specdef/package/tasks/genvector/interface/pevave_tasks, 共 72 个 read_files query.
- run_commands 全程 disabled (env 限制), search_codebase 三次超时.
- **trace agent 未给出最终答案** (64 msgs, 最后仍在读文件, 无结论). → 正确根因须由我自行从代码定位.

## 资产可及性
- `/proj/dscqa/V0/...` 在 .75 上 **不可读** (t0002997 无权限 / 未挂载).
- **资产 = trace-embedded**: 72 个 read_files 结果含完整带行号 SV 代码, 已抽取存 `.75:/tmp/reo1p_all_sv.txt`. 合成时 A_FILES 从 trace 抽取 (同 r637/r646 模式).

## 关键代码定位 (从 trace 抽取, 行号 = ddr6_test.sv / ddr6_tasks.sv 原行号)

### 1. wr_reorganize_dq / rd_reorganize_dq (ddr6_tasks.sv:1922-1940)
```sv
function reg[MAX_DQ_BITS-1:0] wr_reorganize_dq (input[MAX_DQ_BITS-1:0] dq, int bl);
    begin:wr_reorganize_dq_func
        for(int i=0;i<MAX_DQ_BITS;i++)
            wr_reorganize_dq[i/DQ_BITS + MAX_DQ_BITS-bl*(DQ_BITS-i%DQ_BITS)] = dq[i];
    end
endfunction
// MAX_DQ_BITS=144, DQ_BITS=6, MAX_BURST_LEN=24
function reg[MAX_DQ_BITS-1:0] rd_reorganize_dq (input[MAX_DQ_BITS-1:0] dq, int bl);
    begin:rd_reorganize_dq_func
        for(int i=0;i<MAX_DQ_BITS;i++)
            rd_reorganize_dq[DQ_BITS*(i%bl) + i/bl] = dq[i];
    end
endfunction
```
144 = 24(burst) × 6(pin). reorganize 是 burst×pin 维度重排.

### 2. CRC zero-pad block (ddr6_test.sv:1068-1107) — **核心**
```sv
//Cal CRC value, for MD_off or MD_8b not support MD_16b
if(`mr_da.MR1_wr_crc_en) begin
  ...
  else if((dutconfig.dqmode==X1P6)&(`mr_da.MR0_sys_md_mode==MD_OFF|`mr_da.MR0_sys_md_mode==MD_8b_B))begin//zero pad change from DQ2-->DQ5
  `ifndef SC1
  `ifndef DQSEL_LH
  randcase
    ALL_ZERO:begin
        for(int i=0;i<8;i++) begin
            dq_org[143-i] = 'b0;   // ★ 置零 dq_org[143:136]
        end
        for(int i=0;i<8;i++) begin
            dq[143-6*i] = 'b0;
        end
    end
    RANDOM_VALUE:begin
        if(dq_org[143:136]) begin ... MRSetting crc error ... end
    end
  endcase
```
**关键事实**:
- 此块在 `if(MR1_wr_crc_en)` 内, 即 **CRC-ON** 时, 对 X1P6 + MD_OFF/MD_8b_B **显式 zero-pad `dq_org[143:136]`**.
- `dq_org[143:136]` = 144-bit 的最高 8 位. pin k 占 bits [k*24+23 : k*24] (因 ECC 块用 `dq_org[(5*24+16)+:8]` = pin5 D16-D23). 故 **bit 143 = pin5 bit23, bit 136 = pin5 bit16** → `dq_org[143:136]` = **dq5 的 D16-D23**.
- 注释 **"zero pad change from DQ2-->DQ5"** 直接证实: zero-pad 位置从 DQ2 改到 DQ5 (即 dq5 D16-D23 是 CRC pad 槽).

### 3. write_mem_arr md_mask (ddr6_tasks.sv:1684-1774) — write 侧 memory model mask
X1P6 + MD_8b (DqSelect==0, no SC1):
- MD_8b_A: `md_mask=144'h000000_000000_000000_FF0000_000000_000000` (dq3 D16-D23 masked)
- MD_8b_B: `md_mask=144'hFF0000_000000_000000_000000_000000_000000` (dq0 D16-D23 masked)
mask bit=1 → 不写入 mem_arr. 6 组 24-bit = {dq0,dq1,dq2,dq3,dq4,dq5} (MSB first).
(注: 此处 mask 命中 dq0/dq3, 不是 dq5 — write 侧 memory model 与 read 侧 expected 是不同路径.)

### 4. ECC_READ X1P6 分支 (ddr6_test.sv:1046-1058)
```sv
`else//1p6 2p6 1p12
case(rdecc_rdccr_mdecc_mdccr)
  4'b1000: begin dq_org[(2*24+16)+:8]=8'hC7; dq_org[(5*24+16)+:8]=8'h00; end  // pin5 D16-D23 = 0
  ...
```
ECC_READ 时 pin5 D16-D23 (= (5*24+16)+:8 = bits 136-143) 在多个 case 被设 8'h00 / 8'hFF / 8'h80. 印证 pin5 D16-D23 是 metadata/pad 槽.

### 5. read 侧 expected (dq_exp) DSDM 段 (ddr6_test.sv:7000-8000)
- 7056+ `if(!skip_mrupd)` MRUPD DSDM entry; `dq_exp <= #(dsdm_valid_time_perdq) 'd0;` 初始清零.
- 7073+ `if(opt_mapping && dutconfig.dqmode==X2P6)` 分支 per-pin dq_exp 设置.
- **X1P6 的 dq_exp 设置分支尚未抽取** — 这是 r660 必须补的关键代码 (确认 CRC-off 时 dq5 D16-D23 expected=0 的直接机制).

## 根因假说 (待 r660 验证)
**主假说**: 在 X1P6 + MD_8b 模式下, dq5 的 D16-D23 (即 144-bit 的 bits[143:136]) 是 **metadata/pad 保留槽**, 不是有效数据位. 
- CRC-ON 时: 上面 §2 显式 zero-pad 该槽 (ALL_ZERO) 或注入 CRC (RANDOM_VALUE 走 error 路径).
- CRC-OFF 时: 该槽仍为 0, 因为 (a) wr_reorganize_dq 的有效数据只填到 D0-D15 区域 (MD_8b 限制有效数据宽度), (b) dq_exp 初值清零且 read-expected 路径不为该槽填数据 → 期望值保持 0.
**用户问题本质**: dq5 D16-D23 在 X1P6+MD_8b 下是 CRC pad 槽 (注释 "zero pad change from DQ2-->DQ5"), CRC 开与否该槽都不携带有效数据, 故期望值=0; CRC-ON 时显式 zero-pad, CRC-OFF 时该槽从未被填有效数据 (reorganize/expected 路径跳过).

## r660 合成计划 (Ddr6Dq5ExpZeroDiagnose-001)
- **case_id**: `EDA-Eval-DesignFlow-Ddr6Dq5ExpZero-001` (待 r660 确认根因后定名)
- **形态**: C-A analysis-Q&A / code-comprehension (debug-Q&A 变体)
- **A_FILES (trace-embedded, SUT 可见)**: 从 trace 抽取的关键 SV 片段:
  - ddr6_test.sv:1012-1110 (reorganize 调用 + CRC zero-pad 块) ← 核心
  - ddr6_tasks.sv:1684-1774 (write_mem_arr md_mask)
  - ddr6_tasks.sv:1922-1940 (wr/rd_reorganize_dq 定义)
  - ddr6_test.sv:1046-1058 (ECC_READ X1P6 分支)
  - ddr6_specdef.sv: MD_OFF/MD_8b_A/MD_8b_B/X1P6 定义片段
  - ddr6_package.sv: PSD0/PSD1/DqSelect 定义片段
  - 用户原话 U#0 (逐字)
- **B (hidden, 不进 SUT)**: 变体 — 改 mode 为 X2P6 + MD_OFF + CRC-on (或改 DqSelect/SC1), 使 zero-pad 槽变为 dq0 或 dq2 (旧位置), 答案变为不同的 pin/bit-range. 须 r660 从代码确认 X2P6/SC1/DQSEL_LH 分支的对应 mask/pad 位置以构造 faithful B.
- **check() (k≥14, 双参, B 上 subprocess 解析 report JSON)**: 验 report 正确指出
  ① zero-pad 槽 = dq5 D16-D23 (bits[143:136]) ② 该槽在 X1P6+MD_8b 是 metadata/pad 保留位 ③ CRC-on 显式 zero-pad (dq_org[143-i]=0) ④ CRC-off 该槽未被填有效数据 → 期望 0 ⑤ 注释 "zero pad change from DQ2-->DQ5" ⑥ wr_reorganize_dq 不向 D16-D23 写数据 ⑦ B 变体的对应槽位/答案正确 等.
- **3 neg + §4.9 三假提交全 FAIL**.

## r659 结论
- reo1p 确认为 **fresh genuine A-domain** (verification/digital analysis-Q&A), **.75 本机可读**, 旧"枯竭"结论漏报.
- deepread 闭合, 根因定位至 ddr6_test.sv:1089 + dq_org[143:136]=dq5 D16-D23, 主假说明确.
- **DEBT 1**: r660 补 read-expected (dq_exp) X1P6 分支代码 + 确认 CRC-off 机制 + 合成 case.
- ledger: reo1p 须 claim (r659 落).
