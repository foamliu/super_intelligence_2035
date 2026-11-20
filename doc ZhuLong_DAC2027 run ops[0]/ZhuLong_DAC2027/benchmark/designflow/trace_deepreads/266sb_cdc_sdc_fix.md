# Deepread: 266sb (1792738846439_266sb) — CDC/SDC fix (B档候选)

- sid: 1792738846439_266sb
- user: xing1z @ hfeg0plg07 (172.16.8.14)
- mc: 8, keywords: verilog:233;analog:49;rtl:27;synopsys:14;cadence:4;synthesis:3;primetime:3;netlist:3
- domain: pnr_signoff (CDC / SDC / synthesis)
- scan: ssh_eda_search_20261115_081559 (mc5-9 band fresh, mc≥5 recompute)
- ledger: claimed r555 (mc5-recompute), B档 DEBT (synthesis pending)

## Session structure (10 msgs, agent=lead)
- MSG0 (user, 114188 chars): 粘贴 `module rx_top #(...)` (FPGA RX top, 6 banks × 30 lanes, FIFO per lane) + SDC 约束片段 + CDC 错误 + 设计意图。
  - **ASK**: "上述代码只是部分module 的代码，核心关注 fifo 相关的信号，对上述的进行cdc检查，报错如下：Error - CDC_UNSYNC_CTRL ... 请帮我分析这个是什么原因。...如果sdc约束文件和设计意图不同，以设计意图为正确，**修改sdc文件**。"
  - 设计意图: fifo 写时钟 rxfifo_wclk 各自独立异步 0.625GHz；读时钟 tc_clk 1.25GHz；csr_clk 1.25GHz 与 tc_clk 同源（无需 CDC）。
  - 原始 SDC 片段 (在 MSG0 text 内): set_input_delay rstn/csr_rstn; create_reset softreset/csr_rstn_sync_tc_clk; create_clock -period 1.6 {rxfifo_wclk[9]}; foreach i 0-5 create_reset rst_path_softreset + foreach j 0-29 create_reset rst_path_tc_clk。
- MSG1-6 (assistant): list_allowed_files Desktop(空) / read_files(空，无附件，代码在 text 内)。
- MSG7 (assistant, 8461 chars text): **CDC 错误分析**（无文件产出）。解释 CDC_UNSYNC_CTRL = 控制信号跨异步域无完整同步方案；路径 waddr[6:0](rxfifo_wclk) → csr_clk；根因 SDC 未声明 wclk 与 tc_clk/csr_clk 异步。
- MSG8-9 (user, 补充): 只有 fifo **full** 信号报错（empty 不报，因 empty 在 tc_clk 读域产生）；full 在写时钟域产生跨到 tc_clk/csr_clk。提供更完整错误: SrcObject u_rxfifo/u0_sig_sync/signal_delay/Q[6:0] → DestObject rxfifo_full_ff/Q[0][18], crossing rxfifo_wclk[18] → tc_clk。

## 关键判定
- **PRODUCE-TASK**: 用户明确要求"修改sdc文件" → 交付物 = 修正后的 SDC 文件。
- **A档不可行**: session 内 agent 只做了分析(MSG7)，**未产出修正 SDC 文件**；read_files 返回空（无实际 SDC 文件附件，SDC 在 text 内）；session 在 MSG9(user 补充) 后结束，无最终 assistant 产出。
- **B档可行**: 需构造 reference SDC。设计意图清晰，可构造正确约束。

## B档 reference 方案（待合成）
设计意图 → 正确 SDC 应包含：
1. `create_clock -period 1.6` 对每个 rxfifo_wclk[i] (i=0..5, per-lane 0..29) — 0.625GHz
2. `create_clock -period 0.8` tc_clk / csr_clk — 1.25GHz（同源）
3. `set_clock_groups -asynchronous` 声明所有 rxfifo_wclk 互相异步 + 与 tc_clk/csr_clk 组异步
4. **禁止** tc_clk ↔ csr_clk 之间 false_path/set_clock_groups（同源无需 CDC）
5. full 信号路径 (rxfifo_wclk → tc_clk/csr_clk) 经 synchronizer，需 set_false_path 或在 clock_groups 中已覆盖
6. 原 SDC 的 create_reset 保留（softreset / csr_rstn_sync_tc_clk）

check.py 断言方向 (≥8): ① SDC 含 create_clock rxfifo_wclk -period 1.6 ② 含 tc_clk/csr_clk -period 0.8 ③ 含 set_clock_groups -asynchronous ④ wclk 们互相异步分组 ⑤ tc_clk 与 csr_clk 同组(非异步) ⑥ 无 tc_clk↔csr_clk false_path ⑦ 含 full 信号 false_path/async 声明 ⑧ create_reset 保留 ⑨ 无 set_input_delay 删除 ⑩ 注释/结构完整

## 状态
- DEBT: 1 deepread (266sb) 未合成。下一轮第一件事：合成 B档 SdcCdcFix-001 case。
- 时间原因本轮未合成（mc≥5 recompute 为本轮最高优先）。
