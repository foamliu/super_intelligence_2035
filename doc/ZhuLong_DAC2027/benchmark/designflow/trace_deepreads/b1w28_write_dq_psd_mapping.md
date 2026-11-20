# deepread: b1w28 — Write-task dq → PSD0DQ/PSD1DQ mapping table

**trace**: `1791796775106_b1w28` (tongfanl @ hfhds201, dir-based, 222 msgs, 2.49 MB)
**session path**: `/home/tongfanl/.cline/data/sessions/1791796775106_b1w28/1791796775106_b1w28.messages.json`
**domain**: spice_sim (DDR6 DSCQA vecgen stimulus vector generation)
**A-faithful选轮**: U#0 — 提出需求（整理表格），无根因/修复方向 ✓

## U#0 任务说明（逐字作 prompt）
> /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local，帮我整理一个表格，当没有定义DQSEL_LH时，write task中的传入参数和PSD0DQ[5:0]、PSD1DQ[5:0]的mapping关系，分成1P12、1P6、2P6、2P3.分别说明。

## 对话流要点
- U#0–U#3: 同一任务重复4次（cline 重试机制）
- A#4–A#88: assistant 大量 read_files/search_codebase 读 ddr6_tasks.sv / ddr6_genvector.sv / ddr6_test.sv / ddr6_interface.sv / top.sv，理解 Write task dq 参数流、drive_dq pin 映射、genvector $fmonitor 向量列序
- A#90: assistant 开始输出分析总结（Write task 定义在 ddr6_test.sv:839, MAX_DQ_BITS=144/288, DQ_BITS=12/6, 数据流 wr_reorganize_dq→CRC→load_fifo→drive_dq→A_pin_if.DQ[n]→genvector 向量列）
- U#91: 用户追加要求——把 !DQSEL_LH 且定义 DQSELH 的情况也一起总结
- A#102: **金标准**——完整 mapping 对比表（!DQSEL_LH 的 !DQSELH / DQSELH 两子场景，4 模式）
- U#103/U#127/U#129: 后续追问（MRSetting psd_mr 固定映射、2P3 DUALSC 详梳、DUALSC sc 作用）——不入 prompt
- U#194+: 用户改代码后复查（mrdf[n+4]→mrdf[n] error bit 修复等）——不入 prompt

## 金标准（A#102 + A#128 补充）

### 关键代码结构
- **specdef**: `DQ_BITS = 12 (X1P12) | 6 (其他)`；`MAX_DQ_BITS = 288 (X1P12) | 144`
- **interface** (ddr6_interface.sv:229-233): `DqSelect = DQSEL_LH ? 1 : 0`
- **test** Write task (ddr6_test.sv:839): `task Write(..., reg[MAX_DQ_BITS-1:0] dq='0, ...)`
  - load_fifo: `dq_fifo[i] = dq[i*DQ_BITS +: DQ_BITS]`（每 burst 取 DQ_BITS 位）
  - drive_dq: `dq_out[n]` → `A_pin_if.DQ[n]`（SC0→PSD0）或 `B_pin_if.DQ[n]`（SC1→PSD1）
- **genvector** (ddr6_genvector.sv:439): $fmonitor 列序 = PSD0 DQ[5:0] (DQ5_0..DQ0_0) 然后 PSD1 DQ[5:0] (DQ5_1..DQ0_1)

### mapping 表（!DQSEL_LH, DqSelect=0）

| 模式 | DQ_BITS | SC0 PSD0 | SC0 PSD1 | SC1 PSD0 | SC1 PSD1 |
|:--|:--:|:--|:--|:--|:--|
| X1P12 | 12 | dq[0..5]→DQ0_0..DQ5_0 | dq[6..11]→DQ0_1..DQ5_1 | dq[6..11]→DQ0_0..DQ5_0 (swap) | dq[0..5]→DQ0_1..DQ5_1 (swap) |
| X1P6 | 6 | dq[0..5]→DQ0_0..DQ5_0 | (空) | (空) | dq[0..5]→DQ0_1..DQ5_1 |
| X2P6 | 6 | 同 X1P6 | (空) | (空) | 同 X1P6 |
| X2P3 | 6 | dq[0..2]→DQ0_0..DQ2_0 (仅DQ[2:0] bonded) | (空) | (空) | dq[0..2]→DQ0_1..DQ2_1 |

**关键洞察**：
- X1P12 (DQ_BITS=12): 12 位拆 6+6 分别进 PSD0/PSD1，SC 决定哪 6 位进哪个 PSD
- X1P6/X2P6 (DQ_BITS=6): 6 位全进一个 PSD（由 SC 决定 PSD0 还是 PSD1）
- X2P3 (DQ_BITS=6 但仅 DQ[2:0] bonded): 只有低 3 位驱动到 chip pin
- DQSEL_LH 控制 interface DqSelect（驱动行为）；DQSELH 仅控制向量输出列摆放，不影响物理连接

## 合成（case: EDA-Eval-DesignFlow-WriteDqPsdMappingExtract-001）

### A 资产（真实 trace-time 代码结构节选）
- `A_ddr6_specdef.sv`: 4 模式 ifdef 块 + DQ_BITS/MAX_DQ_BITS 参数
- `A_ddr6_interface.sv`: DqSelect ifdef
- `A_ddr6_test.sv`: Write task + load_fifo + drive_dq（X1P12 拆 6+6 / X2P3 仅 n<=2 / else 全 6 位单 PSD）
- `A_ddr6_genvector.sv`: $fmonitor 列序（PSD0 DQ[5:0] → PSD1 DQ[5:0]）

### 通用化脚本 `extract_dq_psd_mapping.py`
泛型解析器：parse_specdef 提取任意模式名+DQ_BITS；extract_drive_block 按模式名定位 test.sv ifdef 块；parse_drive_assignments 解析 n<K 拆分 + sc==0/else 双分支 + n-K 偏移；parse_genvector_columns 建 (iface,pin)→vec_col 映射。输出 JSON: {modes:[{name,dq_bits,sc0:{psd0,psd1},sc1:{psd0,psd1}}]}。

### hidden B（结构不同挡硬编码）
- 模式名: M1P8/M1P4/M2P4/M2P2（≠ A 的 X1P12/X1P6/X2P6/X2P3）
- DQ_BITS: 8/4（≠ A 的 12/6）
- 拆分点: M1P8 拆 4+4（≠ A 的 6+6）
- bonded pins: M2P2 仅 DQ[1:0]（≠ A 的 X2P3 仅 DQ[2:0]）

### 判分 15 断言 (a-o)
zip含.py(a) + py_compile(b) + B运行exit0(c) + 4模式(d) + M1P8 dq_bits=8(e) + M1P8 sc0 psd0 4条DQ0_0-DQ3_0(f) + sc0 psd1 4条DQ0_1-DQ3_1(g) + sc1 psd0 4条证明SC1翻转(h) + sc1 psd1 4条(i) + M2P2 sc0 psd0仅2条(j) + M2P2 sc0 psd1空(k) + M1P4 sc0 psd0 4条psd1空(l) + 无A模式名泄漏(m) + M1P8 dq_bits≠12(n) + 3次幂等sha256(o)

### 自验
- ref PASS 15/15 ✓
- 5 negative 全 FAIL distinct（naive_hardcode_a→e / fake_empty→c / fake_print_expected→e / fake_core_deleted→f / naive_no_split→f）✓
- NEG_RC=0 ✓
- §4.9 三假（空壳→c / 打印期望→e / 删核心→f）全 FAIL ✓
- 断言闸门 k=15==15≥8 ✓
- jsonl test==disk check.py roundtrip ✓
